"""Preserve old status writers and retire their ability to overwrite authority."""
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent
H = P / "historical_code"
H.mkdir(exist_ok=True)
R = P / "historical_reports"
R.mkdir(exist_ok=True)
records = []
for name in ["research_round8_refresh_current_handoff.py", "research_round8_update_handoff.py",
             "research_round8_update_canonical_handoff.py", "research_round8_update_session355735431_handoff.py",
             "research_round9_build_report.py"]:
    source = P / name
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
        original = (P / name).read_bytes()
        destination.write_bytes(original)
        assert destination.read_bytes() == original
        records.append({"original": name, "preserved": str(destination.relative_to(P)),
                        "original_sha256": hashlib.sha256(original).hexdigest(), "action": "preserve_before_current_replacement"})
(P / "research_round10_reporting_migration_manifest.json").write_text(json.dumps({"records": records, "deletions": []}, indent=2), encoding="utf-8")
print(json.dumps({"preserved_records": len(records), "deletions": 0}))
