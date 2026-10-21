
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
import hashlib,json,zipfile
R=project_root(__file__)
bundle=project_path('research_round8_evidence.zip', base=R);meta=json.loads((project_path('research_round8_evidence_bundle_manifest.json', base=R)).read_text(encoding='utf-8'));assert hashlib.sha256(bundle.read_bytes()).hexdigest()==meta['zip_sha256'];assert bundle.stat().st_size==meta['zip_bytes']
with zipfile.ZipFile(bundle) as z:
 assert z.testzip() is None;ledger=json.loads(z.read('EVIDENCE_MANIFEST.json'));checks=[]
 for row in ledger['files']:
  data=z.read(row['file']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];checks.append(row['file'])
 assert len(checks)==len(set(checks))==meta['files']
program=json.loads((project_path('research_round8_idea_program.json', base=R)).read_text(encoding='utf-8'));assert len(program['entries'])==95 and len({r['id'] for r in program['entries']})==95;assert all(not r['fully_explored'] for r in program['entries']);assert all(r['stronger_descendant'] and r['discriminating_test'] and r['combination_partners'] for r in program['entries'])
summary=json.loads((project_path('research_round8_final_summary.json', base=R)).read_text(encoding='utf-8'));assert not summary['qualifying_package_result'] and not summary['twenty_percent_achieved'];assert summary['paid_rental_usd']==0 and summary['deletions']==[]
for row in summary['manifest_hashes']:assert hashlib.sha256((project_path(row['file'], base=R)).read_bytes()).hexdigest()==row['sha256']
fixed=json.loads((project_path('research_round8_fixed_semantic_manifest.json', base=R)).read_text(encoding='utf-8'));assert fixed['all_24_independent_integer_sha256_checks']=='PASS';assert fixed['sparse_graph']['independent_subset_enumeration']=='PASS';assert fixed['sparse_graph']['combined_selected_source_count']==0
for name in ['research_round8_continuous_manifest.json','research_round8_directed_memory_manifest.json']:
 m=json.loads((project_path(name, base=R)).read_text(encoding='utf-8'));assert m['status'].startswith('COMPLETE');assert all(r['certified_ideal_development_optimum'] and r['supporting_plane_gap_bytes']<=.05 for r in m['results'])
report=(project_path('research_round8_report.md', base=R)).read_text(encoding='utf-8');assert report.count('<!-- generated-round8-results -->')==1 and '191.944362' in report
result={'status':'PASS','bundle_files_verified':len(checks),'zip_sha256':meta['zip_sha256'],'all_95_families_have_descendant_test_and_partners':True,'no_false_qualification_or_completion_claims_in_summary':True,'all_result_manifest_hashes_equal':True,'24_independent_Q16_hashes_equal':True,'all_12_continuous_head_certificates_within_threshold':True,'scope':'evidence integrity and finite-method certificates, NOT native/full package qualification'}
(project_path('research_round8_validation.json', base=R)).write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
