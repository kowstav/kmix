"""Preserve old status writers and retire their ability to overwrite authority."""

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
import hashlib
import json

P = project_root(__file__)
H = project_path("historical_code", base=P)
H.mkdir(exist_ok=True)
R = project_path("historical_reports", base=P)
R.mkdir(exist_ok=True)
records = []
for name in ["research_round8_refresh_current_handoff.py", "research_round8_update_handoff.py",
             "research_round8_update_canonical_handoff.py", "research_round8_update_session355735431_handoff.py",
             "research_round9_build_report.py"]:
    source = project_path(name, base=P)
    if source.read_text(encoding="utf-8-sig").startswith('"""Retired historical status writer.'):
        continue
    original = source.read_bytes()
    destination = H / name
    assert not destination.exists(), destination
    destination.write_bytes(original)
    assert destination.read_bytes() == original
    source.write_text('"""Retired historical status writer. Original source is preserved in historical_code/."""\n'
        'raise SystemExit("This historical generator is retired. Read research_round10_report.md; '
        'use research_round10_build_results_registry.py and the current ledger builders.")\n', encoding="utf-8")
    records.append({"original": name, "preserved": str(destination.relative_to(P)),
                    "original_sha256": hashlib.sha256(original).hexdigest(), "action": "preserve_and_retire_status_writer"})
for name in ["research_round7_checkpoint.md", "research_round9_training_and_5090_plan.md", "research_round9_latest_measurements.md"]:
    destination = R / (Path(name).stem + "_through_20261007.md")
    if not destination.exists():
        original = (project_path(name, base=P)).read_bytes()
        destination.write_bytes(original)
        assert destination.read_bytes() == original
        records.append({"original": name, "preserved": str(destination.relative_to(P)),
                        "original_sha256": hashlib.sha256(original).hexdigest(), "action": "preserve_before_current_replacement"})
(project_path("research_round10_reporting_migration_manifest.json", base=P)).write_text(json.dumps({"records": records, "deletions": []}, indent=2), encoding="utf-8")
print(json.dumps({"preserved_records": len(records), "deletions": 0}))
