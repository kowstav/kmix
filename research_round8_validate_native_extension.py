import gzip,hashlib,json,math
from collections import Counter
from pathlib import Path
R=Path(__file__).parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def read(n):return json.loads((R/n).read_text())
census=read('research_round8_rarity_census_results.json');stage=read('research_round8_native_stage_trace_results.json');fit=read('research_round8_native_stage_fit_results.json');atom=read('research_round8_canonical_atom_fit_results.json');error=read('research_round8_canonical_error_memory_results.json');role=read('research_round8_canonical_role_residual_results.json');program=read('research_round8_idea_program.json')
wide=read('research_round8_source_wide_box_results.json');ef=read('research_round8_source_wide_confirmation_results.json');inline=read('research_round8_native_inline_residual_results.json');mask=read('research_round8_rarity_residual_pilot_results.json');wp=R/'research_round8_native_inline_wide_results.json';wi=read(wp.name) if wp.exists() else None
assert census['status'].startswith('COMPLETE') and stage['status'].startswith('COMPLETE') and fit['status']=='COMPLETE_NATIVE_STAGE_FINITE_FIT'
assert len(program['entries'])==96 and len({v['id'] for v in program['entries']})==96 and all(v['fully_explored'] is False for v in program['entries'])
assert len(atom['results'])==11 and len(error['results'])==24 and len(fit['results'])==31 and len(role['development_policy_gains_bytes'])==27
assert all(v['ideal_box_optimum_certified'] and v['supporting_plane_gap_bytes']<=.05 for m in [atom,error,fit] for v in m['results'])
checked=[]
for m in [census,stage,fit,wide,ef,inline,mask]+([wi] if wi else []):
 for row in m['source_hashes']:
  p=R/row['file'];assert p.is_file() and sha(p)==row['sha256'],str(p);checked.append(row)
assert sha(R/'research_round8_word_article_frequencies.tsv.gz')==census['frequency_file']['sha256']
assert sha(R/'research_round8_native_evidence/cmix_stage_trace')==stage['binary_sha256']
assert sha(R/'research_round8_native_evidence/staged_predictor.cpp')==stage['patched_predictor_sha256']
assert wide['certificate_bytes']<=.05 and wide['advance_gate_pass'];assert ef['wider_both_slices_improve'] and ef['wider_both_slices_beat_generic']
assert inline['status']=='COMPLETE_NATIVE_INLINE_RESIDUAL_COLD_CODING_DECODE' and inline['actual_CD_archive_saving_bytes']==127
for manifest,prefix,binary,archive_slices in [(inline,'inline','cmix_inline_residual','cd')]+([(wi,'wide_inline','cmix_inline_wide','ef')] if wi else []):
 assert sha(R/'research_round8_native_evidence'/binary)==manifest['binary']['sha256']
 for source,digest in manifest['patched_interfaces_sha256'].items():
  suffix=source.split('/')[-1];assert sha(R/'research_round8_native_evidence'/f'{prefix}_{suffix}')==digest
 assert all(row['native_archive_identity'] and row['native_Q16_identity'] and row['independent_decode_exact'] for row in manifest['controls'])
 for row in manifest['candidates']:
  assert row['slice'] in archive_slices and row['exact_frozen_replay_Q16_identity'] and row['core_hidden_state_identity'] and row['independent_decode_exact'] and row['encode_decode_integer_trace_identical'] and row['encode_decode_hidden_trace_identical'];assert sha(R/f"research_round8_native_evidence/{row['slice']}512k_{'inline' if prefix=='inline' else 'wide_inline'}.cmx")==row['archive_sha256']
assert mask['status']=='COMPLETE_PARTIAL_DICTIONARY_MASK_RESIDUAL_TRAINING' and len(mask['rungs'])==36 and mask['core_retraining'] is False and mask['all_word_mask_training_completed'] is False
for row in mask['rungs']:
 for name,hashname in [('parameter_file','parameter_sha256'),('optimizer_resume_file','optimizer_resume_sha256')]:assert sha(R/'research_round8_native_evidence/rarity_residual_models'/row[name])==row[hashname]
assert sha(R/'research_round7_sources/lex_h1_run11.tfwc2')=='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
assert sha(R/'research_round8_native_evidence/english.dic')=='4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a'
source_dir=R/'research_round8_native_evidence/stage_observer_source';source_inventory=json.loads((source_dir/'source_evidence_manifest.json').read_text())
for row in source_inventory['entries']:
 p=source_dir/row['file'];assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert sha(source_dir/'src/predictor.cpp')==stage['patched_predictor_sha256']
if wi:
 for row in ef['exports']:
  s=row['slice'];assert sha(R/f'research_round8_native_evidence/{s}512k.bin')==row['input_sha256'];assert sha(R/f'research_round8_native_evidence/{s}512k_native.cmx')==row['native_archive_sha256']
for row in stage['controls']:
 s=row['slice'];assert sha(R/f'research_round8_native_evidence/{s}32k.cmx')==row['archive_sha256'];assert sha(R/f'research_round8_native_evidence/{s}32k_final_p.u16')==row['final_p_sha256'];assert row['archive_identity'] and row['Q16_identity'] and row['independent_decode_exact']
rows=total=articles=0;hist=Counter();previous='';known={}
with gzip.open(R/'research_round8_word_article_frequencies.tsv.gz','rt',encoding='utf-8') as f:
 assert next(f).startswith('word\tcorpus_count\tcorpus_fraction\tcontaining_articles\t')
 for line in f:
  w,c,frac,df,maximum,mean=line.rstrip('\n').split('\t');c=int(c);df=int(df);frac=float(frac);maximum=float(maximum);mean=float(mean);assert w>previous and c>=df>=1 and df<=census['original']['complete_pages'];assert 0<mean<=maximum+2e-12<=1.000000000002;assert abs(frac-c/census['total_tokens'])<max(1e-15,1e-11*frac);previous=w;rows+=1;total+=c;articles+=df;hist[c]+=1
  if w in ['the','a','is','camel','know','now','diamond']:known[w]={'count':c,'corpus_fraction':frac,'containing_articles':df,'maximum_article_fraction':maximum,'mean_fraction_in_containing_articles':mean}
assert rows==census['unique_types'] and total==census['total_tokens'] and articles==census['word_article_pairs']
for cutoff in [2,4,8,16,32,64,128,256,1024]:
 row=census['corpus_thresholds'][str(cutoff)];assert sum(k for c,k in hist.items() if c<cutoff)==row['removed_types'];assert sum(c*k for c,k in hist.items() if c<cutoff)==row['removed_occurrences']
result={'status':'PASS','validated_sources':checked,'all_96_open':True,'finite_new_fit_heads':67,'prior_fitted_heads':51,'total_fitted_heads':118,'role_online_policies':27,'max_new_finite_box_gap_bytes':max([wide['certificate_bytes']]+[v['supporting_plane_gap_bytes'] for m in [atom,error,fit] for v in m['results']]),'frequency_rows':rows,'frequency_token_total':total,'frequency_word_article_pairs':articles,'known_word_examples':known,'observer_binary_and_patched_predictor_hashes':'PASS','weights_and_dictionary_hashes':'PASS','exact_32K_archive_integer_trace_controls':'PASS','full_AB_observer_identity':'PASS','actual_CD_narrow_archive_and_independent_decode':'PASS','actual_EF_wider_archive_and_independent_decode':'PASS' if wi else 'PENDING','partial_dictionary_mask_residual_rungs':36,'all_mask_model_optimizer_hashes':'PASS','qualifying_archive_or_twenty_percent':False,'full_word_or_original_transformer_mask_evaluated':False,'paid_spending_usd':0,'deletions':[]}
(R/'research_round8_native_extension_validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
