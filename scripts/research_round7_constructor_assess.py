"""Validate preserved I11 evidence and write a compact aggregate assessment."""

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

import hashlib,json,pathlib
root=project_root(__file__)
rows=json.loads((project_path('research_round7_constructor_split_v1_summary.json', base=root)).read_text())
manifest=json.loads((project_path('research_round7_constructor_split_v1_manifest.json', base=root)).read_text())
assert manifest['status']=='COMPLETE' and [r['slice'] for r in rows]==list('abcd')
assert manifest['source_sha256']==hashlib.sha256((project_path('research_round7_constructor_split.py', base=root)).read_bytes()).hexdigest()
for r in rows:
    assert r==json.loads((project_path('research_round7_constructor_split_v1_'+r['slice']+'.json', base=root)).read_text())
    assert r['cost_sha256']==hashlib.sha256((project_path('research_round7_lex_'+r['slice']+'_2m_cost.f32', base=root)).read_bytes()).hexdigest()
    assert r['input_sha256']==hashlib.sha256((project_path('research_round7_'+r['slice']+'2m.bin', base=root)).read_bytes()).hexdigest()
    assert all(v['roundtrip']=='PASS' and v['bytes_saved_before_incremental_decoder']<0 for v in r['screen_rows'])
    assert all(r[k]==0 for k in ['paid_rental_usd']) and not r['deletions'] and not r['neural_training']
total_bits=sum(r['all_native_bits'] for r in rows);constructor_bits=sum(r['constructor_native_span_bits'] for r in rows)
aggregate=[]
for mode in ('direct','ordered_templates','multiset_plus_order'):
    for codec in ('zlib9','lzma6'):
        subset=[next(v for v in r['screen_rows'] if v['representation']==mode and v['codec']==codec) for r in rows]
        baseline=sum(v['matched_original_archive_bytes'] for v in subset);candidate=sum(v['candidate_archive_bytes'] for v in subset)
        aggregate.append({'representation':mode,'codec':codec,'original_archive_bytes':baseline,'candidate_archive_bytes':candidate,
                          'increase_bytes_before_incremental_decoder':candidate-baseline,'increase_percent':100*(candidate/baseline-1)})
gaps=sum(r['constructor_gap_count'] for r in rows);multi=sum(r['gaps_with_two_or_more_constructors'] for r in rows)
a={'status':'COMPLETE_NEGATIVE_SCREEN','total_input_bytes':sum(r['input_bytes'] for r in rows),
   'ASCII_word_events':sum(r['ASCII_words_after_first_page_marker'] for r in rows),
   'constructor_occurrences':sum(r['constructor_occurrences'] for r in rows),'fixed_lexicon_count':176,
   'constructor_native_span_share':constructor_bits/total_bits,'constructor_native_span_bits':constructor_bits,
   'all_native_bits':total_bits,'constructor_gaps':gaps,'gaps_with_two_or_more_constructors':multi,
   'gap_share_length_zero_or_one':1-multi/gaps,
   'within_slice_distinct_template_reduction_percent':[100*r['distinct_template_count_reduction_fraction'] for r in rows],
   'casefold_empirical_conditional_order_bits_in_sample_only':sum(r['casefold_empirical_conditional_order_bits_in_sample_only'] for r in rows),
   'cpu_seconds_prototype':sum(r['cpu_seconds'] for r in rows),'wall_seconds_prototype':sum(r['wall_seconds'] for r in rows),
   'prototype_max_RSS_KiB_reported':max(r['prototype_peak_RSS_KiB_process_to_date'] for r in rows),
   'matched_codec_aggregate':aggregate,'all_24_raw_roundtrips':'PASS',
   'source_and_preserved_result_cost_hashes':'PASS','neural_training':False,'paid_rental_usd':0,'deletions':[],
   'interpretation':'Negative exact two-stream representation screen against matched zlib/LZMA; not a cmix result and not a proof against all conditional syntax models. Constructor budget is sampled fixed-lexicon raw spans, not a global corpus bound. Additional decoder/model cost only worsens current negative packets.'}
(project_path('research_round7_constructor_assessment.json', base=root)).write_text(json.dumps(a,indent=2),encoding='utf-8')
print(json.dumps(a,indent=2))
