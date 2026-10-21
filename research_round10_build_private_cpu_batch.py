"""Build concrete private CPU kernel sources and the local source/model payload.

No credentials, network writes or notebook submissions occur here. The live
runtime supplies the pinned native observer and canonical data after reconnect.
"""
from pathlib import Path
import hashlib
import json
import zipfile

P = Path(__file__).resolve().parent
D = P / "kaggle_cpu_round10"
JOBS = ["bf16-unweighted", "bf16-cut107_half", "bf16-cut1392_zero", "integer-mixer",
        "component-ppmd", "article-order-proxy"]


def main():
    code = (D / "kernel_job.py").read_text(encoding="utf-8")
    manifest = {"status": "PREPARED_NOT_SUBMITTED", "account": "chaoscpp", "GPU": False,
                "dataset": "chaoscpp/hutter-round10-private-cpu-assets-v1", "jobs": [], "files": {}}
    for job in JOBS:
        slug = "hutter-r10-" + job.replace("_", "-") + "-v1"
        folder = D / job
        folder.mkdir(exist_ok=True)
        source = "import os\nos.environ['HP_CPU_JOB'] = " + repr(job) + "\n" + code
        compile(source, str(folder / "main.py"), "exec")
        (folder / "main.py").write_text(source, encoding="utf-8", newline="\n")
        metadata = {"id": "chaoscpp/" + slug, "title": "Hutter R10 CPU " + job,
            "code_file": "main.py", "language": "python", "kernel_type": "script",
            "is_private": True, "enable_gpu": False, "enable_tpu": False,
            "enable_internet": False, "dataset_sources": [manifest["dataset"]],
            "competition_sources": [], "kernel_sources": []}
        (folder / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8", newline="\n")
        manifest["jobs"].append({"job": job, "id": metadata["id"], "source_sha256": hashlib.sha256((folder / "main.py").read_bytes()).hexdigest(),
                                 "folder": str(folder.relative_to(P)).replace("\\", "/"), "status": "PREPARED_NOT_SUBMITTED"})
    payload = D / "local_code_models.zip"
    with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as z:
        entries = {"models/" + name + ".tfwc3": P / "research_round10_bf16_repaired_models" / (name + ".tfwc3")
                   for name in ["unweighted", "cut107_half", "cut1392_zero"]}
        for path in (P / "hutter_research").iterdir():
            if path.is_file() and path.suffix in [".py", ".h", ".cpp", ".inc", ".bin"]:
                entries["code/hutter_research/" + path.name] = path
        entries["code/kernel_job.py"] = D / "kernel_job.py"
        for job in manifest["jobs"]:
            folder = P / job["folder"]
            for name in ["main.py", "kernel-metadata.json"]:
                entries["kernels/" + job["job"] + "/" + name] = folder / name
        def put(name, raw):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, raw)
        for name, path in sorted(entries.items()):
            raw = path.read_bytes()
            manifest["files"][name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            put(name, raw)
        put("local_manifest.json", json.dumps(manifest, indent=2).encode())
    manifest["payload_bytes"] = payload.stat().st_size
    manifest["payload_sha256"] = hashlib.sha256(payload.read_bytes()).hexdigest()
    (P / "research_round10_private_cpu_batch_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "jobs": len(JOBS), "payload_bytes": manifest["payload_bytes"],
                      "payload_sha256": manifest["payload_sha256"]}))


if __name__ == "__main__":
    main()
