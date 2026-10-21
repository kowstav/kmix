
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

import ast,hashlib,json,pathlib
import numpy as np
root=project_root(__file__)
tree=ast.parse((project_path('research_round7_constructor_split.py', base=root)).read_text())
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LEXICON' for t in n.targets))
raw=next(n.value for n in ast.walk(assignment) if isinstance(n,ast.Constant) and isinstance(n.value,bytes))
(project_path('research_round7_remaining_constructors.txt', base=root)).write_text('\n'.join(x.decode() for x in sorted(set(raw.split())))+'\n')
z=np.load(project_path('research_round7_idea_arch_integer_graph_v1.npz', base=root));np.savetxt(project_path('research_round7_remaining_graph.txt', base=root),z['ids'],fmt='%d')
manifest={'version':'remaining_experts_v1','session':355529591,'fixed_before_results':{
 'slices':'ABCD cold2M, A/B screens; C/D confirmation only, not pristine validation',
 'strengths':[-.125,.125,.5,1.],'mixture':'half prior neutral, half equally over60 models; posterior uses only previous bits',
 'normalization':'word expert subtree conditional log odds minus matched adaptive-global subtree conditional log odds',
 'integer':'p/65536, round nearest to[1,65535]; neutral returns original integer',
 'article_bank':'1024 completed pages; up to4 donors by observed title overlap; top32 bounded word counters; cold baseline and cold candidate',
 'features':'ASCII word completion after delimiter, including literal I; no future length, spelling or POS gate',
 'limits':'4096 causal rows/32 edges, recent128, article bank1024, static8 geometry neighbors',
 'selection':'do not select best full-ABCD arm as free oracle; byte gain not qualifying archive',
 'new_EF':'required after source fidelity/full-stream regeneration for any optimized positive',
 'I09_scope':'TTL/survival recency screen; full counterfactual hazard fitting contingent on screen',
 'I10_scope':'original-transformer training remains blocked by numerical parity; tiny final-bit residual can be tested separately',
 'paid_rental_usd':0,'deletions':[]},
 'sources':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [project_path('research_round7_remaining_experts.cpp', base=root),project_path('research_round7_remaining_constructors.txt', base=root),project_path('research_round7_remaining_graph.txt', base=root)]}}
(project_path('research_round7_remaining_preregistration.json', base=root)).write_text(json.dumps(manifest,indent=2))
print(json.dumps({'prepared':manifest['version'],'sources':manifest['sources']}))
