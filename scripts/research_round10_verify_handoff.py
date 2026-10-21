"""Verify saved provenance and the prepared CPU batch without network access."""

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
import ast
import datetime
import hashlib
import json
import re
import zipfile

P = project_root(__file__)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def read(name):
    return json.loads((project_path(name, base=P)).read_text(encoding="utf-8-sig"))


def main():
    checks = {}
    audit = read("research_round10_audit_fixes.json")
    assert sha(project_path("CLAUDE_AUDIT_01_FLAWS_REPORT.md", base=P)) == audit["audit_sha256"]
    assert sha(project_path("CLAUDE_AUDIT_02_NEXT_EXPERIMENTS_AND_THEORY.md", base=P)) == audit["companion_sha256"]
    source = (project_path("CLAUDE_AUDIT_01_FLAWS_REPORT.md", base=P)).read_text(encoding="utf-8-sig")
    ids = set(re.findall(r"^### ([SMDLER]\d+)\.", source, re.M))
    ids.update(re.findall(r"^\| (P\d+) \|", source, re.M))
    assert len(ids) == 53 and ids == {row["id"] for row in audit["findings"]}
    assert audit["all_experimental_fixes_complete"] is False
    checks["original_audits_and_all_53_findings"] = True
    scope = read("research_round10_96_scope.json")
    assert len(scope["entries"]) == len({row["id"] for row in scope["entries"]}) == 96
    assert scope["all96_thoroughly_tested"] is False
    checks["96_distinct_protocols_without_false_completion"] = True
    local = read("research_round10_local_checks_results.json")
    assert local["status"] == "COMPLETE_LOCAL_CORRECTNESS_CHECKS_PASS"
    assert all(row["return_code"] == 0 for row in local["commands"])
    assert "Ran 23 tests" in local["commands"][0]["output"]
    for name, expected in local["source_hashes"].items():
        assert sha(project_path(name, base=P)) == expected, name
    checks["23_checks_match_current_source_hashes"] = True
    reader = read("research_round10_native_reader_results.json")
    assert sha(project_path("hutter_research/weights_dump.exe", base=P)) == reader["reader_binary_sha256"]
    for row in reader["cases"]:
        prefix = project_path("research_round10_bf16_repaired_models", base=P) / row["name"]
        assert sha(prefix.with_suffix(".tfwc3")) == row["model_sha256"]
        assert prefix.with_suffix(".tfwc3").stat().st_size == row["model_bytes"]
        assert sha(prefix.with_suffix(".native.tfw")) == row["native_decoded_sha256"]
        assert row["tensor_count"] == len(row["tensors"]) == 435
        assert row["all_tensor_dtype_shape_bytes_equal"] is True
    assert len(reader["cases"]) == 4
    checks["four_models_and_native_reader_dumps_preserved"] = True
    batch = read("research_round10_private_cpu_batch_manifest.json")
    payload = project_path("kaggle_cpu_round10/local_code_models.zip", base=P)
    assert payload.stat().st_size == batch["payload_bytes"] and sha(payload) == batch["payload_sha256"]
    assert len(batch["jobs"]) == 6 and batch["status"] == "PREPARED_NOT_SUBMITTED"
    with zipfile.ZipFile(payload) as archive:
        assert archive.testzip() is None
        embedded = json.loads(archive.read("local_manifest.json"))
        assert embedded["files"] == batch["files"] and embedded["jobs"] == batch["jobs"]
        for name, expected in batch["files"].items():
            raw = archive.read(name)
            assert len(raw) == expected["bytes"]
            assert hashlib.sha256(raw).hexdigest() == expected["sha256"], name
        for row in batch["jobs"]:
            folder = project_path(row["folder"], base=P)
            raw = (folder / "main.py").read_bytes()
            assert hashlib.sha256(raw).hexdigest() == row["source_sha256"]
            assert raw == archive.read("kernels/" + row["job"] + "/main.py")
            ast.parse(raw)
            metadata = read(row["folder"] + "/kernel-metadata.json")
            assert metadata["is_private"] is True
            assert all(metadata[key] is False for key in ["enable_gpu", "enable_tpu", "enable_internet"])
            assert metadata["dataset_sources"] == [batch["dataset"]]
    checks["six_private_CPU_payloads_CRC_entry_and_physical_source_hashes"] = True
    for path in project_glob("research_round10_*.py", base=P):
        ast.parse(path.read_bytes())
    checks["all_round10_python_sources_parse"] = True
    migration = read("research_round10_reporting_migration_manifest.json")
    for row in migration["records"]:
        assert sha(project_path(row["preserved"], base=P)) == row["original_sha256"]
    assert migration["deletions"] == []
    checks["historical_status_sources_preserved_exactly"] = True
    registry = [json.loads(line) for line in (project_path("results/registry.jsonl", base=P)).read_text().splitlines()]
    for row in registry:
        evidence = row["evidence"]
        assert sha(project_path(evidence["path"], base=P)) == evidence["sha256"], row["id"]
    checks["registry_all_evidence_hashes_match"] = True
    for document in ["README.md", "research_round10_report.md", "research_round10_pre_experiment_report.md",
                     "research_round10_training_and_5090_plan.md", "research_round10_audit_response.md"]:
        document_path = project_path(document, base=P)
        text = document_path.read_text(encoding="utf-8-sig")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" not in target and not target.startswith("#"):
                assert (document_path.parent / target.split("#")[0]).exists(), (document, target)
    checks["current_report_local_links_exist"] = True
    result = {"status": "PASS_LOCAL_HANDOFF_PROVENANCE", "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "checks": checks, "private_jobs_submitted": 0, "paid_usd": 0, "deletions": [],
              "limits": "No remote terminal status, rounded-model native archive quality or whole-package improvement is established."}
    (project_path("research_round10_handoff_verification.json", base=P)).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
