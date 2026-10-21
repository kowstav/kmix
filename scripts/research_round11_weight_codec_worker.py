"""Finite exact lossless weight-codec sweep. No probability-model retraining."""

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

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
import hashlib
import json
import os
import resource
import struct
import subprocess
import sys
import time
import traceback
import numpy as np

S=Path('/root/hp_round11_codec_v1')
W=Path('/kaggle/working/hp_round11/weight_codec_v1')
assert not W.exists(), 'Inspect existing version; never duplicate this sweep'
W.mkdir(parents=True)
sys.path.insert(0,str(S/'code'))
from hutter_research import native_weights as codec, tensor_io
SOURCE=Path('/root/hp_round11_private_assets_v2/models/original.tfwc3')
BINARY=S/'weights_dump_v4'
EXPECTED='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
M={'status':'PREPARING_EXACT_WEIGHT_SWEEP','pid':os.getpid(),'started':time.time(),
   'deletions':[],'paid_usd':0,'GPU':False,'cases':[],'format_header_growth':8,
   'arms':[(s,l) for s in [64,240,960,3840] for l in [16384,65536,262144]],
   'production_package_qualified':False,
   'limits':'Tensor-preserving model storage; new native production integration, executable size and resource qualification remain required.'}

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1<<20): h.update(b)
    return h.hexdigest()

def save(): (W/'manifest.json').write_text(json.dumps(M,indent=2))

def arm(parameters):
    seed,limit=parameters
    name=f'seed{seed}_limit{limit}'
    dest=W/(name+'.tfwc4')
    begin=time.monotonic(); before=resource.getrusage(resource.RUSAGE_SELF)
    codec.write_tensor_file_v3(dest,ENTRIES,seed_total=seed,halve_limit=limit,format_version=4)
    after=resource.getrusage(resource.RUSAGE_SELF)
    encode={'wall_seconds':time.monotonic()-begin,'CPU_user_seconds':after.ru_utime-before.ru_utime,
            'CPU_system_seconds':after.ru_stime-before.ru_stime,'peak_RSS_KiB':after.ru_maxrss}
    decoded=S/(name+'.native.tfw')
    before=resource.getrusage(resource.RUSAGE_CHILDREN); begin=time.monotonic()
    result=subprocess.run([str(BINARY),str(dest),str(decoded)],capture_output=True,text=True)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    assert result.returncode==0, 'independent C++ decoding failed'
    assert sha(decoded)==REFERENCE_SHA, 'exact native tensor bytes differ'
    row={'seed_total':seed,'halve_limit':limit,'model_bytes':dest.stat().st_size,'model_sha256':sha(dest),
         'saving_bytes_per_copy':SOURCE.stat().st_size-dest.stat().st_size,
         'two_model_copy_saving_before_executable_price':2*(SOURCE.stat().st_size-dest.stat().st_size),
         'native_decoded_sha256':REFERENCE_SHA,'all_435_native_tensors_equal':True,'encode':encode,
         'decode':{'wall_seconds':time.monotonic()-begin,'CPU_user_seconds':after.ru_utime-before.ru_utime,
                   'CPU_system_seconds':after.ru_stime-before.ru_stime,'peak_RSS_KiB':after.ru_maxrss}}
    (W/(name+'.json')).write_text(json.dumps(row,indent=2))
    return row

try:
    save(); assert sha(SOURCE)==EXPECTED
    source_dir=S/'native'
    cmd=['g++','-O2','-std=c++17','-ffp-contract=off','-I',str(source_dir),
         str(S/'weights_dump.cpp'),str(source_dir/'weights_io.cpp'),
         str(S/'weights_io_compressed_v4.cpp'),'-o',str(BINARY)]
    result=subprocess.run(cmd,capture_output=True,text=True)
    assert result.returncode==0, result.stderr[-2000:]
    M['reader_binary_sha256']=sha(BINARY); M['reader_binary_bytes']=BINARY.stat().st_size
    tensors=codec.read_tensor_file_v3(SOURCE)
    ENTRIES=[(name,dt,array) for name,(dt,array) in tensors.items()]
    assert len(ENTRIES)==435
    ref=S/'original.native.tfw'
    result=subprocess.run([str(BINARY),str(SOURCE),str(ref)],capture_output=True,text=True)
    assert result.returncode==0
    native=tensor_io.read_tensor_file(ref); assert set(native)==set(tensors)
    for name,(dt,array) in tensors.items():
        if dt==1 and not name.endswith('.scale'):
            array=(array.astype('<u4')<<16).view('<f4'); dt=2
        actual_dt,actual_array=native[name]
        assert actual_dt==dt and actual_array.shape==array.shape and actual_array.tobytes()==array.tobytes(),name
    REFERENCE_SHA=sha(ref)
    neutral=W/'neutral.tfwc3'
    codec.write_tensor_file_v3(neutral,ENTRIES)
    assert sha(neutral)==EXPECTED, 'Default V3 export must reproduce the original bytes'
    M.update(status='RUNNING_TWELVE_EXACT_CODEC_ARMS',native_reference_sha256=REFERENCE_SHA,
             neutral_original_byte_identity=True,source_model_bytes=SOURCE.stat().st_size)
    save()
    with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('fork')) as pool:
        futures=[pool.submit(arm,tuple(p)) for p in M['arms']]
        for future in as_completed(futures):
            M['cases'].append(future.result()); save()
    M['cases'].sort(key=lambda r:(r['model_bytes'],r['seed_total'],r['halve_limit']))
    M.update(status='COMPLETE_TWELVE_EXACT_CODEC_ARMS',finished=time.time(),best=M['cases'][0])
    save()
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc(),finished=time.time()); save(); raise
