import hashlib,json,pathlib,zipfile
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'calibration_native_v4';m=json.loads((d/'manifest.json').read_text());assert m['status']=='COMPLETE_64K_NATIVE';out=r/'native_calibration_20261005.zip';assert not out.exists();index=[]
with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 def put(p,name):
  b=p.read_bytes();z.writestr(name,b);index.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 for name in ['manifest.json','results.json','e64k.bin','f64k.bin']:put(d/name,name)
 for n in 'ef':
  for mode in ['reference','neutral','candidate']:
   q=d/(n+'_'+mode)
   for file in ['out.cmx','cost.f32','final_p.u16']:put(q/file,n+'_'+mode+'/'+file)
  put(d/(n+'_decode')/'decoded.bin',n+'_decode/decoded.bin')
  p=d/(n+'_decode.log');z.writestr(n+'_decode/log_tail.txt',p.read_text()[-800:])
 put(r/'tiny_residual_v1/odds_0.u32','odds_0.u32');put(r/'calibration_native_v1/cmix_calibrated','cmix_calibrated')
 put(r/'calibration_native_v1/build_command.json','build_command.json');put(r/'research_round7_calibration_native_v4_worker.py','worker.py')
 for file in ['hp_calibration_odds.h','encoder.cpp','decoder.cpp']:
  put(pathlib.Path('/root/hp/calibration_native_v1/src/coder')/file,'source/'+file)
 z.writestr('index.json',json.dumps(index,indent=2))
print(json.dumps({'file':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(index)}))
