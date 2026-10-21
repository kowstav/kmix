"""Verify one collector bundle locally against its downloaded collection receipt.

Usage: python research_round14_verify_collected_bundle_v2.py <tag>
Pattern of research_round14_verify_new_bundles.py, plus a cross-check that the
bundle's entries.json equals every per-file (path, bytes, sha256) row recorded in
the receipt. Extracts into research_round14_confirmation_compact_<tag>_evidence/.
Never overwrites a differing existing file.
"""

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
import hashlib, json, sys, zipfile

R = project_root(__file__)
tag = sys.argv[1]
record = json.loads((project_path('research_round14_confirmation_collection_' + tag + '.json', base=R)).read_text())
assert record['status'] == 'TERMINAL_WAVE_SNAPSHOT', record['status']
expected = record['compact']['sha256']
p = project_path('research_round14_confirmation_compact_' + tag + '.zip', base=R)
assert p.stat().st_size == record['compact']['bytes']
assert hashlib.sha256(p.read_bytes()).hexdigest() == expected
receipt_rows = sorted((e['path'], e['bytes'], e['sha256']) for row in record['jobs'] for e in row['files'])
dest = project_path('research_round14_confirmation_compact_' + tag + '_evidence', base=R)
dest.mkdir(exist_ok=True)
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    entries = json.loads(z.read('entries.json'))
    assert sorted((e['path'], e['bytes'], e['sha256']) for e in entries) == receipt_rows
    assert set(z.namelist()) == {e['path'] for e in entries} | {'entries.json'}
    for e in entries:
        b = z.read(e['path'])
        assert len(b) == e['bytes'] and hashlib.sha256(b).hexdigest() == e['sha256']
        out = (dest / e['path']).resolve()
        assert out.is_relative_to(dest.resolve())
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            assert out.read_bytes() == b
        else:
            out.write_bytes(b)
print(json.dumps({'bundle': p.name, 'verified_entries': len(entries), 'sha256': expected,
                  'receipt_rows_matched': len(receipt_rows), 'zip_crc': 'ok'}))
