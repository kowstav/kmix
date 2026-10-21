
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

import hashlib,json,pathlib,sys
root=project_root(__file__);version=sys.argv[1];assert version in ('v1','v2')
prefix='research_round7_constructor_skeleton_'+version+'_'
rows=json.loads((project_path(prefix+'summary.json', base=root)).read_text());meta=json.loads((project_path(prefix+'manifest.json', base=root)).read_text())
source='research_round7_constructor_skeleton.py' if version=='v1' else 'research_round7_constructor_skeleton_v2.py'
assert meta['status']=='COMPLETE' and [r['slice'] for r in rows]==list('abcd')
assert meta['source_sha256']==hashlib.sha256((project_path(source, base=root)).read_bytes()).hexdigest()
assert meta['split_dependency_sha256']==hashlib.sha256((project_path('research_round7_constructor_split.py', base=root)).read_bytes()).hexdigest()
for r in rows:
    assert r==json.loads((project_path(prefix+r['slice']+'.json', base=root)).read_text())
    assert r['input_sha256']==hashlib.sha256((project_path('research_round7_'+r['slice']+'2m.bin', base=root)).read_bytes()).hexdigest()
    assert r['cost_sha256']==hashlib.sha256((project_path('research_round7_lex_'+r['slice']+'_2m_cost.f32', base=root)).read_bytes()).hexdigest()
    assert all(v['roundtrip']=='PASS' for v in r['screen_rows'])
aggregate=[]
for mode in ('direct','constructor_word_table'):
    for codec in ('zlib9','lzma6'):
        subset=[next(v for v in r['screen_rows'] if v['representation']==mode and v['codec']==codec) for r in rows]
        baseline=sum(v['matched_original_archive_bytes'] for v in subset);candidate=sum(v['candidate_archive_bytes'] for v in subset)
        aggregate.append({'representation':mode,'codec':codec,'original_archive_bytes':baseline,'candidate_archive_bytes':candidate,
                          'increase_bytes_before_incremental_decoder':candidate-baseline,'increase_percent':100*(candidate/baseline-1),
                          'all_slice_deltas_bytes_saved':[v['bytes_saved_before_incremental_decoder'] for v in subset]})
result={'status':'COMPLETE','version':version,'matched_codec_aggregate':aggregate,'total_input_bytes':8000000,
        'all_16_raw_roundtrips':'PASS','source_dependency_input_cost_hashes':'PASS',
        'wall_seconds_prototype':sum(r['wall_seconds'] for r in rows),'CPU_seconds_prototype':sum(r['cpu_seconds'] for r in rows),
        'peak_RSS_KiB_reported':max(r['prototype_peak_RSS_KiB_process_to_date'] for r in rows),
        'interpretation':'Exact raw WRT matched-codec exploratory screen; overhead is included in packets, additional decoder cost excluded; no qualifying cmix claim.',
        'neural_training':False,'paid_rental_usd':0,'deletions':[]}
(project_path('research_round7_constructor_skeleton_'+version+'_assessment.json', base=root)).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
