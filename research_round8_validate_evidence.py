from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent
bundle=R/'research_round8_evidence.zip';meta=json.loads((R/'research_round8_evidence_bundle_manifest.json').read_text(encoding='utf-8'));assert hashlib.sha256(bundle.read_bytes()).hexdigest()==meta['zip_sha256'];assert bundle.stat().st_size==meta['zip_bytes']
with zipfile.ZipFile(bundle) as z:
 assert z.testzip() is None;ledger=json.loads(z.read('EVIDENCE_MANIFEST.json'));checks=[]
 for row in ledger['files']:
  data=z.read(row['file']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];checks.append(row['file'])
 assert len(checks)==len(set(checks))==meta['files']
program=json.loads((R/'research_round8_idea_program.json').read_text(encoding='utf-8'));assert len(program['entries'])==95 and len({r['id'] for r in program['entries']})==95;assert all(not r['fully_explored'] for r in program['entries']);assert all(r['stronger_descendant'] and r['discriminating_test'] and r['combination_partners'] for r in program['entries'])
summary=json.loads((R/'research_round8_final_summary.json').read_text(encoding='utf-8'));assert not summary['qualifying_package_result'] and not summary['twenty_percent_achieved'];assert summary['paid_rental_usd']==0 and summary['deletions']==[]
for row in summary['manifest_hashes']:assert hashlib.sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256']
fixed=json.loads((R/'research_round8_fixed_semantic_manifest.json').read_text(encoding='utf-8'));assert fixed['all_24_independent_integer_sha256_checks']=='PASS';assert fixed['sparse_graph']['independent_subset_enumeration']=='PASS';assert fixed['sparse_graph']['combined_selected_source_count']==0
for name in ['research_round8_continuous_manifest.json','research_round8_directed_memory_manifest.json']:
 m=json.loads((R/name).read_text(encoding='utf-8'));assert m['status'].startswith('COMPLETE');assert all(r['certified_ideal_development_optimum'] and r['supporting_plane_gap_bytes']<=.05 for r in m['results'])
report=(R/'research_round8_report.md').read_text(encoding='utf-8');assert report.count('<!-- generated-round8-results -->')==1 and '191.944362' in report
result={'status':'PASS','bundle_files_verified':len(checks),'zip_sha256':meta['zip_sha256'],'all_95_families_have_descendant_test_and_partners':True,'no_false_qualification_or_completion_claims_in_summary':True,'all_result_manifest_hashes_equal':True,'24_independent_Q16_hashes_equal':True,'all_12_continuous_head_certificates_within_threshold':True,'scope':'evidence integrity and finite-method certificates, NOT native/full package qualification'}
(R/'research_round8_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
