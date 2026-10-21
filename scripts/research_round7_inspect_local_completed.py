
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

import json,pathlib,hashlib
r=project_path('research_round7_completed_20261005T1912');out={}
for x in json.loads((r/'index.json').read_text()):
 b=(r/x['path']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
out['evidence_files_verified']=len(json.loads((r/'index.json').read_text()))
names=['a','b','c','d'];ex=[json.loads((r/'remaining_experts_v1'/(n+'_2m.json')).read_text()) for n in names];out['expert_savings']=[x['mixture_saving_bytes'] for x in ex];out['expert_total']=sum(out['expert_savings']);out['expert_cpu']=sum(x['user_seconds'] for x in ex);out['expert_RSS']=max(x['max_rss_kbytes'] for x in ex)
out['expert_fixed_best']=[max((m for m in x['models'] if m['family']!='empty'),key=lambda m:m['saving_bytes']) for x in ex]
roots=[json.loads((r/'root_eof_v3'/(n+'.json')).read_text()) for n in names];out['root_savings']=[x['score']['prequential_saving_bytes'] for x in roots];out['root_total']=sum(out['root_savings']);out['root_fixed_best']=[max(x['score']['fixed_models'],key=lambda m:m['saving_bytes']) for x in roots]
out['root_keys']=[list(x.keys()) for x in roots]
groups={}
for x in json.loads((r/'exact_prior_transforms_v1/manifest.json').read_text())['rows']:
 k=x['transform']+'/'+x['codec'];g=groups.setdefault(k,{'packed':0,'raw':0,'decode_s':0,'compress_s':0});g['packed']+=x['compressed_bytes'];g['raw']+=x['raw_bytes'];g['decode_s']+=x['decode_and_inverse_seconds'];g['compress_s']+=x['compress_seconds']
for g in groups.values():g.update(ratio=g['packed']/g['raw'],projected_full_bytes=g['packed']/g['raw']*240448198200,decode_MB_s=g['raw']/g['decode_s']/1e6)
out['prior_groups']=groups
print(json.dumps(out,indent=2))
