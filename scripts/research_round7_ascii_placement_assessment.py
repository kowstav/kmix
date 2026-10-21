
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

import collections,json,pathlib
p=project_root(__file__)
rows=json.loads((project_path('research_round7_ascii_placement_audit_v1_summary.json', base=p)).read_text())
counts=collections.Counter();pairs=collections.Counter();n=0
for r in rows:
    n+=r['ascii_word_events']
    for w,v in r['word_stats'].items():counts[w]+=v['count']
    for v in r['example_pairs']:pairs[v['scope'],v['source'],v['target'],v['lag_ASCII_words']]+=v['pair_count']
r={'ascii_word_events':n,'word_counts':dict(counts),
   'now_know_selected_lags':[{'scope':s,'source':u,'target':v,'lag_ASCII_words':d,'count':pairs[s,u,v,d]}
                             for s in ['article','raw_punctuation_segment'] for u,v in [('now','know'),('know','now')]
                             for d in [1,2,3,4]],
   'interpretation':'Full ASCII words including literal I/i and markup; previously inspected cold8M; descriptive, not codec gain or whole corpus'}
(project_path('research_round7_ascii_placement_assessment.json', base=p)).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
