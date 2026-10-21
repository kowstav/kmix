import pathlib,os,json,subprocess,hashlib
W=pathlib.Path('/kaggle/working');S=pathlib.Path('/root/hp_round10/preflight_v2');S.mkdir(parents=True,exist_ok=False)
T=W/'hp_round8/native_stage_trace_v1/tree';B=T/'cmix';weights=W/'hp_round7/lex_audit/lex_h1_run11.tfwc2'
B.chmod(B.stat().st_mode | 0o100)
assert hashlib.sha256(B.read_bytes()).hexdigest()=='17768b0673e5a1ad6fb39ca86af25d6d40db3b1790fc17e365341456819fd3fa'
with (W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt').open('rb') as f:raw=f.read(4096)
(S/'input.bin').write_bytes(raw);(S/'.dict').symlink_to(T/'dictionary/english.dic')
env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')};env.update(LAB_RAW='1',LAB_DICT=str(T/'dictionary/english.dic'),LAB_VOCAB=str(W/'hp_round7/preserved/data/vocab.bm'),LAB_KEEP_TEMP='1')
out={'bytes':len(raw),'cases':[]}
for name,args in [('encode',[str(B),'-n','--transformer',str(weights),'input.bin','out.cmx']),('decode',[str(B),'-d','--transformer',str(weights),'out.cmx','decoded.bin'])]:
 p=subprocess.run(args,cwd=S,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=35)
 out['cases'].append({'name':name,'exit_code':p.returncode});assert p.returncode==0,(name,p.returncode)
assert (S/'decoded.bin').read_bytes()==raw
out.update(status='PASS_4096_BYTE_NATIVE_ENCODE_INDEPENDENT_DECODE',input_sha256=hashlib.sha256(raw).hexdigest())
print(json.dumps(out))
