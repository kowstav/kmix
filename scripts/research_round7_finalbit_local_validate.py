"""Independent local checks of the preserved final integer probability traces."""

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

import hashlib,json,pathlib,time
import numpy as np
root=project_root(__file__);rows=json.loads((project_path('research_round7_lex_finalbit_2m_v1_results.json', base=root)).read_text())
manifest=json.loads((project_path('research_round7_lex_finalbit_2m_v1_manifest.json', base=root)).read_text());assert manifest['status']=='PASS'
assert {r['slice'] for r in rows}==set('abcd');start=time.monotonic();checks=[]
for name in 'abcd':
    row=next(r for r in rows if r['slice']==name);ip=project_path('research_round7_'+name+'2m.bin', base=root)
    pp=project_path('research_round7_lex_finalbit_'+name+'2m_p.u16', base=root);cp=project_path('research_round7_lex_'+name+'_2m_cost.f32', base=root)
    ap=project_path('research_round7_lex_'+name+'_2m.cmx', base=root);raw=ip.read_bytes();assert len(raw)==2000000
    assert hashlib.sha256(raw).hexdigest()==row['input_sha256']
    assert pp.stat().st_size==32000000 and hashlib.sha256(pp.read_bytes()).hexdigest()==row['bit_trace_sha256']
    assert hashlib.sha256(ap.read_bytes()).hexdigest()==manifest['archive_control_sha256'][name]
    probs=np.memmap(pp,dtype='<u2',mode='r');cost=np.memmap(cp,dtype='<f4',mode='r');assert len(probs)==8*len(raw)==16000000
    assert len(cost)==len(raw) and row['archive_bit_exact_preserved'] and row['costs_bit_exact_preserved']
    worst=0.;sumbits=0.
    for lo in range(0,len(raw),65536):
        hi=min(len(raw),lo+65536);p=probs[8*lo:8*hi].astype(np.float64);assert np.all((p>=1)&(p<=65535))
        actual=np.unpackbits(np.frombuffer(raw[lo:hi],np.uint8),bitorder='big')
        bits=(-np.log2(np.where(actual,p,65536.-p)/65536.)).reshape(-1,8).sum(axis=1)
        worst=max(worst,float(np.max(np.abs(bits-cost[lo:hi]))));sumbits+=float(bits.sum())
    assert worst<=1e-4
    checks.append({'slice':name,'status':'PASS','input_sha256':row['input_sha256'],'trace_sha256':row['bit_trace_sha256'],
                   'native_archive_control_sha256':manifest['archive_control_sha256'][name],
                   'max_reconstructed_byte_bits_diff':worst,'native_integer_trace_bits':sumbits,
                   'trace_bytes':pp.stat().st_size,'native_user_CPU_seconds':row['user_seconds'],
                   'native_peak_RSS_KiB':row['max_rss_kbytes']})
result={'status':'PASS','scope':'4x2M original WRT and64M actual final integer bit probabilities; local trace reconstruction/hash controls, no new compression gain',
        'checks':checks,'local_validation_wall_seconds':time.monotonic()-start,'neural_training':False,'paid_rental_usd':0,'deletions':[]}
(project_path('research_round7_finalbit_local_validation.json', base=root)).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
