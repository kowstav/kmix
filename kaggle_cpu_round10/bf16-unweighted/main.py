import os
os.environ['HP_CPU_JOB'] = 'bf16-unweighted'
"""Six finite private CPU experiments; no GPU and no paid infrastructure.

Each run verifies immutable input assets before native execution. A replay or
article-order proxy is labelled as such. None establishes a production record.
"""
from pathlib import Path
import hashlib
import json
import os
import resource
import shutil
import struct
import subprocess
import sys
import time
import traceback
import zipfile
import numpy as np

JOB = os.environ.get("HP_CPU_JOB", "integer-mixer")
W = Path("/kaggle/working") / JOB
W.mkdir(parents=True, exist_ok=False)
S = Path("/root/hp_round10_committed") / JOB
S.mkdir(parents=True, exist_ok=False)
M = {"id": "R10-CPU-" + JOB, "status": "PREPARING", "started": time.time(),
     "regime": "predeclared early sequential prefix or article-order proxy",
     "paid_usd": 0, "GPU": False, "deletions": [], "cases": [],
     "production_package_qualified": False, "accounting": {}}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def save(stage):
    M["stage"] = stage
    (W / "manifest.json").write_text(json.dumps(M, indent=2))
    print(stage, flush=True)


def run(args, label, cwd, env):
    start = time.monotonic()
    with (W / (label + ".log")).open("x") as log:
        process = subprocess.Popen(args, cwd=cwd, env=env, stdout=log,
                                   stderr=subprocess.STDOUT)
        _, status, usage = os.wait4(process.pid, 0)
    code = os.waitstatus_to_exitcode(status)
    M["accounting"][label] = {"wall_seconds": time.monotonic() - start,
        "CPU_user_seconds": usage.ru_utime, "CPU_system_seconds": usage.ru_stime,
        "peak_RSS_KiB": usage.ru_maxrss, "return_code": code}
    save(label + " finished")
    assert code == 0, (label, code)


def load_assets():
    candidates = list(Path("/kaggle/input").rglob("round10_cpu_assets.zip"))
    def install(metadata, read):
        for name, expected in metadata['files'].items():
            path = S / name
            assert path.resolve().is_relative_to(S.resolve())
            data = read(name)
            assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
            assert len(data) == expected['bytes'], name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    if candidates:
        assert len(candidates) == 1, [str(x) for x in candidates]
        with zipfile.ZipFile(candidates[0]) as archive:
            metadata = json.loads(archive.read('asset_manifest.json'))
            install(metadata, archive.read)
        M['asset_zip_sha256'] = sha(candidates[0])
        M['asset_delivery'] = 'original ZIP'
    else:
        manifests = list(Path('/kaggle/input').rglob('asset_manifest.json'))
        assert len(manifests) == 1, [str(x) for x in manifests]
        manifest = manifests[0]
        metadata = json.loads(manifest.read_text())
        def read(name):
            path = (manifest.parent / name).resolve()
            assert path.is_relative_to(manifest.parent.resolve())
            return path.read_bytes()
        install(metadata, read)
        M['asset_manifest_sha256'] = sha(manifest)
        M['asset_delivery'] = 'platform-extracted files; every entry hash verified'
    M["assets"] = metadata
    M["affinity"] = sorted(os.sched_getaffinity(0))
    M["CPU_count"] = os.cpu_count()
    M["python_version"] = sys.version
    M["numpy_version"] = np.__version__
    sys.path.insert(0, str(S / "code"))
    (S / "native/cmix").chmod(0o700)
    return metadata


def native_case(label, weights, flags=(), size=3 * 1048576, stage=False):
    folder = S / label
    folder.mkdir()
    (folder / "input.bin").write_bytes((S / "data/canonical_prefix.bin").read_bytes()[:size])
    (folder / ".dict").symlink_to(S / "native/english.dic")
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("LAB_", "FX_PREPARE", "HP_LEX_"))}
    env.update(LAB_RAW="1", LAB_DICT=str(S / "native/english.dic"),
               LAB_VOCAB=str(S / "data/vocab.bm"), LAB_KEEP_TEMP="1", OMP_NUM_THREADS="1")
    binary = str(S / "native/cmix")
    options = list(flags)
    if weights is not None:
        options += ["--transformer", str(S / "models" / (weights + ".tfwc3"))]
    q = folder / "final_p.u16"
    hidden = folder / "hidden.q8"
    cost = folder / "cost.f32"
    extra = {"LAB_COST": str(cost), "LAB_BITTRACE": str(q), "LAB_HIDDENTRACE": str(hidden)}
    if stage:
        extra["LAB_STAGETRACE"] = str(folder / "stage.f32")
    save(label + " encode starting")
    run([binary, "-n", *options, "input.bin", "out.cmx"], label + "_encode", folder,
        {**env, **extra})
    if weights is not None:
        assert q.exists() and q.stat().st_size == 16 * size
        assert hidden.exists() and hidden.stat().st_size == 193 * size
        assert cost.exists() and cost.stat().st_size == 4 * size
    if stage:
        assert (folder / "stage.f32").stat().st_size == 12 + 608 * size
    dq = folder / "decode_p.u16"
    dh = folder / "decode_hidden.q8"
    save(label + " separate decode starting")
    run([binary, "-d", *options, "out.cmx", "decoded.bin"], label + "_decode", folder,
        {**env, "LAB_DECODE_BITTRACE": str(dq), "LAB_HIDDENTRACE": str(dh)})
    assert sha(folder / "input.bin") == sha(folder / "decoded.bin"), label
    # Some diagnostic modes bypass the final CM observer and do not emit these
    # optional streams. Test identity when emitted; never claim an absent trace.
    trace_check = {"Q16": q.exists() and dq.exists(), "hidden": hidden.exists() and dh.exists()}
    if trace_check["Q16"]:
        assert q.stat().st_size == 16 * size and sha(q) == sha(dq)
    if trace_check["hidden"]:
        assert hidden.stat().st_size == 193 * size and sha(hidden) == sha(dh)
    shutil.copyfile(folder / "out.cmx", W / (label + ".cmx"))
    result = {"label": label, "input_bytes": size, "input_sha256": sha(folder / "input.bin"),
              "archive_bytes": (folder / "out.cmx").stat().st_size,
              "archive_sha256": sha(folder / "out.cmx"), "independent_decode_exact": True,
              "trace_identity_checked": trace_check,
              "Q16_decoder_trace_limit": "Unavailable when retained observer lacks LAB_DECODE_BITTRACE; do not claim measured Q16 trajectory identity in that case."}
    if cost.exists() and cost.stat().st_size == 4 * size:
        costs = np.memmap(cost, dtype="<f4", mode="r", shape=(size,))
        result["windows"] = [{"offset": o, "bytes": 524288,
            "native_bits": float(np.asarray(costs[o:o + 524288], dtype="float64").sum())}
            for o in range(1048576, size, 524288) if o + 524288 <= size]
    M["cases"].append(result)
    save(label + " independent decode PASS")
    return folder, result


def bf16_pair(name):
    M["protocol"] = {"canonical_start": 0, "bytes": 3145728, "warmup_bytes": 1048576,
                     "warm_windows": 4, "selection": "arm fixed before observation",
                     "limits": "one early-region cluster; no whole-file extrapolation"}
    _, baseline = native_case("baseline", "original")
    _, candidate = native_case("candidate", name)
    model = S / "models" / (name + ".tfwc3")
    growth = model.stat().st_size - (S / "models/original.tfwc3").stat().st_size
    M["comparison"] = {"actual_prefix_archive_gain_bytes": baseline["archive_bytes"] - candidate["archive_bytes"],
                       "model_growth_bytes_per_copy": growth, "counted_weight_copies": 2,
                       "conditional_full_file_projection": None}
    M["status"] = "COMPLETE_EARLY_WARM_NATIVE_MODEL_PAIR"


def mixer():
    M["protocol"] = {"canonical_start": 0, "bytes": 3145728, "warmup_bytes": 1048576,
        "arms": ["identity", "full", "global", "no_explicit_nn", "relabel", "long_memory", "short_memory", "memory_zero"],
        "memory_horizons_completed_bytes": [1, 1024, 32768, 131072],
        "memory_episode_bytes": 3145728,
        "full_learning_rates": [250, 1000, 4000], "selection": "first two warm windows",
        "confirmation": "last two warm windows; adjacent exploratory confirmation",
        "limits": "unchanged native-state replay; new native coder feedback not tested"}
    folder, _ = native_case("native_baseline", "original", stage=True)
    code = S / "code/hutter_research"
    exe = S / "integer_replay"
    run(["g++", "-O2", "-std=c++17", "-fno-fast-math", str(code / "integer_mixer_replay.cpp"),
         "-o", str(exe)], "compile_integer", S, os.environ.copy())
    M["replays"] = []
    reference = np.memmap(folder / "final_p.u16", dtype="<u2", mode="r", shape=(3145728, 8))
    raw = np.frombuffer((folder / "input.bin").read_bytes(), dtype="u1")
    targets = ((raw[:, None] >> (7 - np.arange(8))) & 1).astype(bool)
    base_likelihood = np.where(targets, reference, 65536 - reference.astype("uint32")) / 65536
    base_bits = -np.log2(base_likelihood)
    outputs = {}
    for arm, rate in [("identity", 1000), ("full", 250), ("full", 1000), ("full", 4000),
                      ("global", 1000), ("no_explicit_nn", 1000), ("relabel", 1000),
                      ("long_memory", 250), ("long_memory", 1000), ("long_memory", 4000),
                      ("short_memory", 1000), ("memory_zero", 1000)]:
        label = arm + "_" + str(rate)
        out = S / (label + ".u16")
        run([str(exe), *map(str, [folder / "input.bin", folder / "final_p.u16", folder / "hidden.q8",
            folder / "stage.f32", out]), arm, str(rate)], "replay_" + label, S, os.environ.copy())
        q = np.memmap(out, dtype="<u2", mode="r", shape=(3145728, 8))
        probability = np.where(targets, q, 65536 - q.astype("uint32")) / 65536
        gains = (base_bits + np.log2(probability)).sum(axis=1) / 8
        row = {"arm": arm, "rate": rate, "Q16_sha256": sha(out), "unit": "byte equivalents",
            "windows": [{"offset": o, "bytes": 524288, "gain": float(gains[o:o + 524288].sum())}
                        for o in range(1048576, 3145728, 524288)]}
        M["replays"].append(row)
        outputs[label] = sha(out)
        if arm == "identity":
            assert sha(out) == sha(folder / "final_p.u16")
        save(label + " replay complete")
    assert outputs["full_1000"] == outputs["relabel_1000"]
    M["status"] = "COMPLETE_INTEGER_MIXER_EARLY_WARM_REPLAY_ONLY"


def component_audit():
    M["protocol"] = {"sizes": [262144, 1048576], "modes": ["combined", "ppmd", "ppmd_with_NN_stepped"],
        "limits": "coarse mode timing; NN-stepped mode returns PPMD, not NN probabilities; no PGO or judge benchmark"}
    for size in [262144, 1048576]:
        native_case("combined_" + str(size), "original", size=size)
        native_case("ppmd_" + str(size), None, ("--ppmd-only",), size=size)
        native_case("ppmd_with_NN_stepped_" + str(size), "original", ("--transformer-only",), size=size)
    M["status"] = "COMPLETE_COARSE_CPU_COMPONENT_DIAGNOSTIC"


def article_order():
    from hutter_research.article_order import experiment
    M.update(experiment(S / "data/pages.bin", W))


try:
    load_assets()
    save("all source/model/data hashes verified")
    if JOB.startswith("bf16-"):
        bf16_pair(JOB[5:])
    elif JOB == "integer-mixer":
        mixer()
    elif JOB == "component-ppmd":
        component_audit()
    elif JOB == "article-order-proxy":
        article_order()
    else:
        raise ValueError(JOB)
    M["finished"] = time.time()
    save("finite CPU experiment complete; qualification scope recorded")
except BaseException as error:
    M.update(status="FAIL", error=repr(error), traceback=traceback.format_exc(), finished=time.time())
    save("failure evidence preserved")
    raise
