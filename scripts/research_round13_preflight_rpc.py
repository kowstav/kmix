from pathlib import Path
import hashlib,json,os,subprocess,sys,zipfile
import numpy as np

S=Path('/root/hp_round13_preflight');S.mkdir(exist_ok=False)
with zipfile.ZipFile('/kaggle/working/hp_round13/source_v1.zip') as z:
    rows=json.loads(z.read('source_manifest.json'))
    for row in rows:
        data=z.read(row['path']);assert hashlib.sha256(data).hexdigest()==row['sha256']
        p=S/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
code=S/'hutter_research'
sys.path.insert(0,str(S))
r=subprocess.run(['g++','-O2','-std=c++17','-fno-fast-math','-ffp-contract=off',str(code/'stream_mixer_v3.cpp'),'-o',str(S/'consumer')],capture_output=True,text=True)
assert r.returncode==0,r.stderr
c=code/'native_reader'
r=subprocess.run(['g++','-O2','-std=c++17','-ffp-contract=off','-I',str(c),str(c/'dump.cpp'),str(c/'weights_io.cpp'),str(c/'weights_io_compressed.cpp'),'-o',str(S/'dump')],capture_output=True,text=True)
assert r.returncode==0,r.stderr
model=Path('/kaggle/working/hp_round7/lex_audit/lex_h1_run11.tfwc2')
r=subprocess.run([str(S/'dump'),str(model),str(S/'original.tfw')],capture_output=True,text=True)
assert r.returncode==0,r.stderr
assert hashlib.sha256((S/'original.tfw').read_bytes()).hexdigest()=='0e3ee73140eadd68fa5e28758be06c5d68204d057b5d138f413a79223bbc7f44'
# Complete synthetic frozen traces exercise the streaming protocol and guards.
n=512;raw=bytes((i*37+13)%256 for i in range(n));(S/'input').write_bytes(raw)
np.full((n,8),24000,dtype='<u2').tofile(S/'q')
stage=np.full((n,8,19),.61,dtype='<f4');stage[:,:,:14]=.7;stage[:,:,17]=.82
(S/'stage').write_bytes(b'HPSTG001'+np.array([19],dtype='<u4').tobytes()+stage.tobytes())
h=np.zeros((n,193),dtype='u1');h[:,0]=1;h[:,1:]=np.arange(192,dtype='u1');h.tofile(S/'hidden');(S/'done').write_text('done')
cmd=[str(S/'consumer'),str(S/'input'),str(S/'q'),str(S/'stage'),str(S/'hidden'),str(S/'done'),str(S/'result.jsonl'),'128','0']
r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
result=[json.loads(l) for l in (S/'result.jsonl').read_text().splitlines()];last=result[-1]
assert last['bytes']==n and last['identity_mismatch_bits']==last['memory_zero_mismatch_bits']==0
# Future mutation must leave the shared prefix and next bit's prediction law
# unchanged. Window costs before the mutation are a coarse protocol check.
(S/'input').write_bytes(raw[:256]+bytes(b^255 for b in raw[256:]));cmd[-3]=str(S/'mutated.jsonl')
r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
mutated=[json.loads(l) for l in (S/'mutated.jsonl').read_text().splitlines()];assert result[:2]==mutated[:2]
out={'status':'PASS_LINUX_SOURCE_AND_STREAM_PREFLIGHT','source_entries':len(rows),
     'native_435_tensor_reference_SHA_identity':True,'stream_identity_and_memory_zero_identity':True,
     'shared_prefix_windows_unchanged_after_future_mutation':True,'consumer_sha256':hashlib.sha256((S/'consumer').read_bytes()).hexdigest()}
Path('/kaggle/working/hp_round13/preflight_v1.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
