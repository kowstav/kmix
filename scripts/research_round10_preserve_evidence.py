"""Preserve compact local round-10 evidence; never delete any source artifact."""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import datetime
import hashlib
import json
import re
import zipfile

P = project_root(__file__)
DEST = project_path("research_round10_evidence_v1.zip", base=P)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def main():
    assert not DEST.exists(), "preserve the current bundle; use a new evidence version"
    verified = json.loads((project_path("research_round10_handoff_verification.json", base=P)).read_text())
    assert verified["status"] == "PASS_LOCAL_HANDOFF_PROVENANCE"
    paths = set(path for path in project_glob("research_round10_*", base=P) if path.is_file()
                and path.suffix in [".py", ".json", ".md"]
                and not path.name.endswith("_response.json")
                and not path.name.startswith("research_round10_evidence_"))
    paths.update(project_path(name, base=P) for name in ["README.md", "research_round7_checkpoint.md",
        "CLAUDE_AUDIT_01_FLAWS_REPORT.md", "CLAUDE_AUDIT_02_NEXT_EXPERIMENTS_AND_THEORY.md",
        "research_round10_old_native_models.zip", "research_round9_native_build_dependencies_v1.zip",
        "research_round9_weights_dump.cpp", "research_round9_adaptive_law.cpp", "research_round9_adaptive_law.h",
        "research_round9_adaptive_strict_worker.py", "research_round9_adaptive_numeric_detail_rpc.py",
        "research_round9_native_promotion_v1_results.json", "research_round9_native_bf16_promotion_v1_results.json",
        "research_round9_core_bf16_qat_v1_results.json", "research_round9_core_checkpoint_relocation_manifest.json",
        "research_round9_extended_evidence_v2_validation.json", "kaggle_research_client.mjs",
        "research_round7_sources/lex_README.md"])
    for top in ["hutter_research", "tests", "kaggle_cpu_round10", "historical_code", "historical_reports", "results"]:
        paths.update(path for path in (project_path(top, base=P)).rglob("*") if path.is_file()
                     and path.suffix in [".py", ".h", ".cpp", ".inc", ".bin", ".exe", ".json", ".jsonl", ".md", ".zip"]
                     and "__pycache__" not in path.parts)
    paths.update((project_path("research_round10_bf16_repaired_models", base=P)).glob("*.tfwc3"))
    rows = []
    with zipfile.ZipFile(DEST, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(paths):
            assert path.exists(), str(path)
            name = path.relative_to(P).as_posix()
            raw = path.read_bytes()
            # Signed proxy URLs and credential responses are never bundle inputs.
            if path.suffix in [".py", ".json", ".md", ".mjs"]:
                assert not re.search(rb"https://kkb-production[.]jupyter-proxy[.]kaggle[.]net/k/[0-9]+/eyJ", raw), name
            digest = hashlib.sha256(raw).hexdigest()
            rows.append({"file": name, "bytes": len(raw), "sha256": digest})
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, raw)
        manifest = {"entries": rows, "scope": "Compact local code/models/metadata, not the canonical full corpus or remote terminal results.",
                    "unpreserved_latest_R9_artifacts": "Latest prior-session QAT /root models/archives were lost; only their terminal metadata is included.",
                    "current_remote_jobs": "Two launched workers terminal UNKNOWN; six private CPU kernels PREPARED_NOT_SUBMITTED.",
                    "deletions": [], "paid_usd": 0}
        archive.writestr("bundle_entry_manifest.json", json.dumps(manifest, indent=2))
    with zipfile.ZipFile(DEST) as archive:
        assert archive.testzip() is None
        for row in rows:
            raw = archive.read(row["file"])
            assert len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"]
    result = {"status": "COMPLETE_LOCAL_COMPACT_EVIDENCE_CRC_AND_ALL_ENTRY_SHA_VERIFIED",
              "date": datetime.datetime.now(datetime.timezone.utc).isoformat(), "archive": DEST.name,
              "archive_bytes": DEST.stat().st_size, "archive_sha256": sha(DEST), "entries": len(rows),
              "deletions": [], "paid_usd": 0, "scope": manifest["scope"]}
    (project_path("research_round10_evidence_v1_validation.json", base=P)).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
