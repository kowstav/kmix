"""Versioned asset preparation after completing the notebook delivery repair."""
from pathlib import Path
import hashlib
import json
import struct
import time
import traceback
import zipfile

W = Path('/kaggle/working/hp_round11')
S = Path('/root/hp_round11_private_assets_v2')
S.mkdir(exist_ok=False)
M = {'status':'PREPARING','started':time.time(),'deletions':[],'files':{}}

def save():
    (W/'private_cpu_assets_manifest.json').write_text(json.dumps(M,indent=2))

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(1<<20):
            h.update(block)
    return h.hexdigest()

try:
    incoming=W/'local_code_models.zip'
    with zipfile.ZipFile(incoming) as archive:
        local=json.loads(archive.read('local_manifest.json'))
        M['local_payload_sha256']=sha(incoming)
        for name,row in local['files'].items():
            raw=archive.read(name)
            assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
            path=S/name
            assert path.resolve().is_relative_to(S.resolve())
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(raw)
    original=Path('/root/hp_round10_private_assets_v1')
    old=json.loads((Path('/kaggle/working/hp_round10')/'private_cpu_assets_manifest.json').read_text())
    assert old['status']=='COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED'
    for name,row in old['files'].items():
        if not (name.startswith(('native/','data/')) or name=='models/original.tfwc3'):
            continue
        source=original/name
        assert source.stat().st_size==row['bytes'] and sha(source)==row['sha256']
        path=S/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(source.read_bytes())
    upload=S/'upload'
    upload.mkdir()
    with zipfile.ZipFile(upload/'round10_cpu_assets.zip','w',zipfile.ZIP_DEFLATED) as archive:
        def put(name,raw):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,raw)
        for top in ['code','native','models','data']:
            for path in sorted((S/top).rglob('*')):
                if path.is_file():
                    name=path.relative_to(S).as_posix()
                    raw=path.read_bytes()
                    M['files'][name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
                    put(name,raw)
        immutable={'files':M['files'],'protocol_version':2,
                   'canonical_sha256':'7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce',
                   'original_raw_sha256':'159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc',
                   'selection':'canonical first 3 MiB; first 512 complete raw page elements for separate gzip proxy'}
        put('asset_manifest.json',json.dumps(immutable,indent=2,sort_keys=True).encode())
    (upload/'dataset-metadata.json').write_bytes((original/'upload/dataset-metadata.json').read_bytes())
    M.update(status='COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED',upload_dir=str(upload),
             asset_zip_bytes=(upload/'round10_cpu_assets.zip').stat().st_size,
             asset_zip_sha256=sha(upload/'round10_cpu_assets.zip'),kernels_dir=str(S/'kernels'),finished=time.time(),
             superseded_unsent_asset_dir=str(original))
    save()
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc())
    save()
    raise
