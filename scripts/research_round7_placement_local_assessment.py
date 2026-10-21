"""Compact preserved evidence from completed placement and native trace tests."""

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

import collections,datetime,json,pathlib
ROOT=project_root(__file__)
def read(n):return json.loads((project_path(n, base=ROOT)).read_text())
g=read('research_round7_lex_finalbit_trace_v2_results.json')
qs=[read('research_round7_placement_pair_audit_v1_'+n+'.json') for n in 'abcd']
groups=[read('research_round7_idea_arch_directed_lag_v1_'+n+'.json') for n in 'abcd']
budget=collections.defaultdict(lambda:[0,0.]);pairs=collections.Counter()
for q in qs:
    for w,v in q['word_stats'].items():budget[w][0]+=v['count'];budget[w][1]+=v['native_complete_code_bits']
    for v in q['records']:
        if v['source'] in ['no','now','know'] and v['target'] in ['no','now','know']:
            pairs[v['scope'],v['source'],v['target'],v['lag_DICT_events']]+=v['pair_count']
base=sum(q['baseline_ideal_bytes'] for q in groups)
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_identity_gate_status':g['status'],
   'native_controls':g['controls'],'collector_status_at_download':read('research_round7_lex_finalbit_2m_v1_manifest.json')['status'],
   'directed_ideal_saving_bytes':sum(q['score']['prequential_saving_bytes'] for q in groups),
   'matched_full_native_ideal_bytes':base,'complete_dictionary_atoms':sum(q['complete_DICT_atoms'] for q in qs),
   'word_budgets':{w:{'count':n,'native_complete_code_bits':b,'mean_native_code_bits':b/n if n else None,
                      'restricted_oracle_budget_percent_of_full_native_bits':100*b/(8*base)} for w,(n,b) in budget.items()},
   'example_pairs':[{'scope':k[0],'source':k[1],'target':k[2],'lag_DICT_events':k[3],'pair_count':v}
                    for k,v in sorted(pairs.items()) if k[1]!=k[2] and k[3]<=4],
   'directed_resources':[{'slice':n,'peak_rss_kbytes':q['prototype_peak_rss_kbytes_linux_only'],
                         'wall_seconds':q['wall_seconds'],'memory':q['memory']} for n,q in zip('abcd',groups)],
   'interpretation':'Cold previously examined slices, complete dictionary-code bits only; descriptive pair frequencies/oracle budgets are not achieved compression or a global upper bound',
   'neural_training':False,'paid_rental_usd':0,'deletions':[]}
(project_path('research_round7_placement_assessment.json', base=ROOT)).write_text(json.dumps(r,indent=2))
print(json.dumps({k:v for k,v in r.items() if k not in ['directed_resources','native_controls']},indent=2))
print(json.dumps({'trace_native_time_RSS':[(v['slice'],v['runtime']['trace']) for v in g['controls']],
                  'I04_resource_summary':[(n,q['prototype_peak_rss_kbytes_linux_only'],q['memory']['active_edges']) for n,q in zip('abcd',groups)]}))
