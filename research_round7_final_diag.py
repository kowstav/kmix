import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');out={}
for p in ['calibration_native_v3/e_decode.log','calibration_native_v3/e_reference.log','calibration_native_v3/e_candidate.log','research_round7_calibration_native_v3_worker.py','full_inverse_v2/generated_scratch_deletions.txt']:
 q=r/p;out[p]=q.read_text()[-20000:] if q.is_file() else 'ABSENT'
p=r/'exact_prior_transforms_v1/manifest.json'
if p.is_file():
 m=json.loads(p.read_text());rows=m.pop('rows',[]);groups={}
 for x in rows:
  key=x['transform']+'/'+x['codec'];g=groups.setdefault(key,{'compressed_bytes':0,'decode_seconds':0,'raw_bytes':0,'all_exact':True})
  g['compressed_bytes']+=x['compressed_bytes'];g['raw_bytes']+=x['raw_bytes'];g['decode_seconds']+=x['decode_and_inverse_seconds'];g['all_exact'] &= x['exact_roundtrip']
 out['prior_transforms']={'manifest':m,'groups':groups}
out['active']=[x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if any(k in x for k in ('calibration_native','full_inverse','prior_transforms'))]
print(json.dumps(out,indent=2))
