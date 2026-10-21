
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

import pathlib,numpy as np,hashlib,json
P=project_root(__file__);D=project_path('hutter_research', base=P)
q=np.arange(1,65536,dtype=np.float64);s=np.zeros(65536,dtype='<i2');s[1:]=np.rint(256*np.log(q/(65536-q))).astype('<i2')
z=np.arange(-4096,4097,dtype=np.float64)/256
f=np.clip(np.floor(65536/(1+np.exp(-z))+.5),1,65535).astype('<u2')
odds_z=np.arange(-2048,2049,dtype=np.float64)/256
odds=np.floor((1<<20)*np.exp(odds_z)+.5).astype('<u4')
assert odds[2048]==1<<20 and int(odds[-1])*65535*65536+((1<<48)//2)<(1<<64)
assert np.all(np.diff(s[1:].astype(np.int32))>=0) and np.all(np.diff(f.astype(np.int32))>=0)
out='#pragma once\n#include <cstdint>\nnamespace hp {\n'
for name,ctype,array in [('kStretch','int16_t',s),('kSquash','uint16_t',f),('kOdds','uint32_t',odds)]:
 out+='inline constexpr '+ctype+' '+name+'['+str(len(array))+']={\n'
 out+='\n'.join(','.join(map(str,array[i:i+32].tolist()))+',' for i in range(0,len(array),32))+'\n};\n'
out+='}\n';(D/'probability_tables.inc').write_text(out,encoding='utf-8')
binary=s.tobytes()+f.tobytes()+odds.tobytes();(D/'probability_tables.bin').write_bytes(binary)
m={'fixed_asset_bytes':len(binary),'sha256':hashlib.sha256(binary).hexdigest(),'source_sha256':hashlib.sha256(out.encode()).hexdigest(),
 'tables_are_assets_not_free':True,'rounding':'frozen offline RNE stretch Q8, nearest Q16 squash, nearest Q20 exp on [-8,8]; runtime integer odds update preserves native Q16 exactly at zero correction',
 'runtime_model_state_bytes_measured':46160,'long_memory_state_bytes_measured':72,
 'deployment_status':'C++ replay and native/cross-platform qualification required'}
(project_path('research_round10_probability_tables_manifest.json', base=P)).write_text(json.dumps(m,indent=2),encoding='utf-8');print(json.dumps(m))
