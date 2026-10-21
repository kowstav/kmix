"""Prepare one immutable private CPU asset, preserving all models and inputs."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,traceback,zipfile

W=Path('/kaggle/working/hp_round13');W.mkdir(exist_ok=True)
OUT=W/'asset_prepare_manifest.json'
S=Path('/root/hp_round13_asset_v1')
M={'status':'PREPARING','started':time.time(),'pid':os.getpid(),'deletions':[],
   'paid_usd':0,'GPU':False,'dataset':'chaoscpp/hutter-r13-four-lane-cpu-assets-v1'}
def save(): OUT.write_text(json.dumps(M,indent=2))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1<<22):h.update(b)
    return h.hexdigest()
try:
    assert not S.exists() and not OUT.exists(),'inspect existing preparation instead of duplicate'
    S.mkdir();save()
    base=Path('/kaggle/working')
    files={
      'native_cmix':base/'hp_round8/native_stage_trace_v1/tree/cmix',
      'original.tfwc3':base/'hp_round7/lex_audit/lex_h1_run11.tfwc2',
      'english.dic':base/'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic',
      'vocab.bm':base/'hp_round7/preserved/data/vocab.bm',
      'original_enwik9.zip.dat':base/'hp_round7/preserved/data/enwik9.zip'}
    for name,p in files.items():shutil.copyfile(p,S/name)
    expected={'native_cmix':'17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa',
      'original.tfwc3':'948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71',
      'english.dic':'4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a',
      'vocab.bm':'3e7f8c043939ccba8675b3a260f65a665bc34acac883a7316cc50fecfd7d36b5'}
    for name,want in expected.items():assert sha(S/name)==want,name
    canonical=base/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
    assert sha(canonical)=='7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce'
    # Fixed before new outputs. First eight develop; last eight confirmation.
    offsets=[32000000,96000000,160000000,224000000,288000000,352000000,416000000,480000000,
             64000000,128000000,192000000,256000000,320000000,384000000,448000000,544000000]
    regions=[]
    with canonical.open('rb') as f:
        for i,offset in enumerate(offsets):
            f.seek(offset);raw=f.read(3*1048576);assert len(raw)==3*1048576
            name=f'region_{i:02}.bin';(S/name).write_bytes(raw)
            regions.append({'id':i,'file':name,'offset':offset,'bytes':len(raw),
              'role':'development' if i<8 else 'confirmation','warmup_bytes':2*1048576,
              'state_regime':'native and candidate reset at regional start, both then advance through 2 MiB; not exact full-file state'})
    # Store compressed source as .dat so dataset ZIP expansion cannot alter it.
    entries={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in S.iterdir() if p.is_file()}
    meta={'files':entries,'regions':regions,'source_original_sha256':'159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc',
          'source_original_bytes':1000000000,'canonical_source_bytes':587138826,
          'canonical_source_sha256':'7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce'}
    (S/'r13_assets.json').write_text(json.dumps(meta,indent=2))
    (S/'dataset-metadata.json').write_text(json.dumps({'title':'Hutter r13 four lane cpu assets v1',
      'id':M['dataset'],'licenses':[{'name':'other'}]}))
    M.update(status='UPLOADING_PRIVATE_DATASET',asset_dir=str(S),asset_bytes=sum(x['bytes'] for x in entries.values()),
             files=entries,regions=regions);save()
    r=subprocess.run(['kaggle','datasets','create','-p',str(S)],capture_output=True,text=True,timeout=1200)
    # CLI can return zero after API rejection. Persist only scoped verified URL.
    wanted='https://www.kaggle.com/datasets/'+M['dataset']
    assert r.returncode==0 and wanted in r.stdout and 'error' not in r.stdout.lower(),'private dataset creation was not verified; no automatic retry'
    M.update(status='COMPLETE_PRIVATE_CPU_ASSETS_CREATED',dataset_url=wanted,finished=time.time());save()
except BaseException as e:
    M.update(status='FAIL_NO_AUTOMATIC_RETRY',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
