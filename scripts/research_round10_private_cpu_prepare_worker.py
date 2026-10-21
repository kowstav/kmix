"""Assemble immutable private dataset assets in root scratch after reconnect.

Upload local_code_models.zip once to hp_round10 first. This does not launch
research jobs; it creates the exact asset ZIP and private metadata for review.
"""
from pathlib import Path
import hashlib
import json
import struct
import time
import traceback
import zipfile

W = Path("/kaggle/working/hp_round10")
S = Path("/root/hp_round10_private_assets_v1")
S.mkdir(exist_ok=False)
M = {"status": "PREPARING", "started": time.time(), "deletions": [], "files": {}}


def save():
    (W / "private_cpu_assets_manifest.json").write_text(json.dumps(M, indent=2))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


try:
    incoming = W / "local_code_models.zip"
    with zipfile.ZipFile(incoming) as archive:
        local = json.loads(archive.read("local_manifest.json"))
        M["local_payload_sha256"] = sha(incoming)
        for name, metadata in local["files"].items():
            raw = archive.read(name)
            assert hashlib.sha256(raw).hexdigest() == metadata["sha256"]
            assert len(raw) == metadata["bytes"]
            path = S / name
            assert path.resolve().is_relative_to(S.resolve())
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    pinned = {
        "native/cmix": (Path("/kaggle/working/hp_round8/native_stage_trace_v1/tree/cmix"), "17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa"),
        "native/english.dic": (Path("/kaggle/working/hp_round8/native_stage_trace_v1/tree/dictionary/english.dic"), "4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a"),
        "models/original.tfwc3": (Path("/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2"), "948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71"),
    }
    for name, (source, expected) in pinned.items():
        assert sha(source) == expected, name
        path = S / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source.read_bytes())
    data = S / "data"
    data.mkdir(exist_ok=True)
    stream = Path("/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt")
    assert stream.stat().st_size == 587138826
    assert sha(stream) == "7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce"
    with stream.open("rb") as f:
        prefix = f.read(3145728)
    assert len(prefix) == 3145728
    (data / "canonical_prefix.bin").write_bytes(prefix)
    vocab = Path("/kaggle/working/hp_round7/preserved/data/vocab.bm")
    assert vocab.stat().st_size == 32
    (data / "vocab.bm").write_bytes(vocab.read_bytes())
    source_zip = Path("/kaggle/working/hp_round7/preserved/data/enwik9.zip")
    pages = []
    buffer = b""
    with zipfile.ZipFile(source_zip) as archive:
        names = [name for name in archive.namelist() if name.endswith("enwik9")]
        assert len(names) == 1
        source_hash = hashlib.sha256()
        with archive.open(names[0]) as f:
            while True:
                block = f.read(1 << 20)
                if not block:
                    break
                source_hash.update(block)
                if len(pages) >= 512:
                    continue
                buffer += block
                while len(pages) < 512:
                    first = buffer.find(b"<page>")
                    last = buffer.find(b"</page>", first)
                    if first < 0 or last < 0:
                        break
                    last += len(b"</page>")
                    pages.append(buffer[first:last])
                    buffer = buffer[last:]
        assert source_hash.hexdigest() == "159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc"
        assert len(pages) == 512
    raw = struct.pack("<I", len(pages)) + b"".join(struct.pack("<I", len(page)) + page for page in pages)
    (data / "pages.bin").write_bytes(raw)
    M["raw_pages_provenance"] = {"source": str(source_zip), "source_zip_sha256": sha(source_zip),
        "selection": "first 512 complete page elements; early raw-page proxy only", "canonical_transform": False}
    upload = S / "upload"
    upload.mkdir()
    with zipfile.ZipFile(upload / "round10_cpu_assets.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        def put(name, raw):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
        for top in ["code", "native", "models", "data"]:
            for path in sorted((S / top).rglob("*")):
                if path.is_file():
                    name = path.relative_to(S).as_posix()
                    raw = path.read_bytes()
                    M["files"][name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                    put(name, raw)
        immutable = {"files": M["files"], "protocol_version": 1,
            "canonical_sha256": "7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce",
            "original_raw_sha256": source_hash.hexdigest(),
            "selection": "canonical first 3 MiB; first 512 complete raw page elements for a separate gzip proxy"}
        put("asset_manifest.json", json.dumps(immutable, indent=2, sort_keys=True).encode())
    metadata = {"title": "Hutter round 10 private CPU assets",
        "id": "chaoscpp/hutter-round10-private-cpu-assets-v1", "licenses": [{"name": "other"}],
        "description": "Private research bundle. Native sources retain their upstream GPL-3.0 license; Wikipedia content retains its original attribution/share-alike terms. Model/dictionary provenance and hashes are recorded in asset_manifest.json. This metadata does not relicense third-party assets."}
    (upload / "dataset-metadata.json").write_text(json.dumps(metadata, indent=2))
    M.update(status="COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED", upload_dir=str(upload),
             asset_zip_bytes=(upload / "round10_cpu_assets.zip").stat().st_size,
             asset_zip_sha256=sha(upload / "round10_cpu_assets.zip"), kernels_dir=str(S / "kernels"), finished=time.time())
    save()
except BaseException as error:
    M.update(status="FAIL", error=repr(error), traceback=traceback.format_exc())
    save()
    raise
