import hashlib,json,pathlib
import numpy as np
r=pathlib.Path('research_round7_native_calibration_20261005');idx=json.loads((r/'index.json').read_text())
for x in idx:
 b=(r/x['path']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
F=np.fromfile(r/'odds_0.u32','<u4').astype(np.uint64);results=[]
for row in json.loads((r/'results.json').read_text()):
 n=row['slice'];raw=(r/(n+'64k.bin')).read_bytes();assert raw==(r/(n+'_decode/decoded.bin')).read_bytes()
 p=np.fromfile(r/(n+'_reference/final_p.u16'),'<u2').astype(np.uint64);neutral=np.fromfile(r/(n+'_neutral/final_p.u16'),'<u2');q=np.fromfile(r/(n+'_candidate/final_p.u16'),'<u2').astype(np.uint64)
 assert len(p)==len(raw)*8 and np.array_equal(p,neutral)
 assert (r/(n+'_reference/out.cmx')).read_bytes()==(r/(n+'_neutral/out.cmx')).read_bytes()
 a=p*F[np.tile(np.arange(8),len(raw))*16+(p>>12).astype(np.int64)];d=a+(65536-p)*(1<<20);expected=np.clip((a*65536+d//2)//d,1,65535);assert np.array_equal(q,expected)
 y=np.unpackbits(np.frombuffer(raw,np.uint8),bitorder='big');cost=lambda v:-np.log2(np.where(y,v,65536-v)/65536.0)
 c0=cost(p).reshape(-1,8).sum(axis=1);c1=cost(q).reshape(-1,8).sum(axis=1);stored0=np.fromfile(r/(n+'_reference/cost.f32'),'<f4');stored1=np.fromfile(r/(n+'_candidate/cost.f32'),'<f4');error=max(float(np.max(np.abs(c0-stored0))),float(np.max(np.abs(c1-stored1))));assert error<1e-5
 saving=float((c0-c1).sum()/8);assert abs(saving-row['ideal_saving_bytes'])<1e-4
 delta=(r/(n+'_reference/out.cmx')).stat().st_size-(r/(n+'_candidate/out.cmx')).stat().st_size;assert delta==row['native_archive_saving_bytes']
 results.append({'slice':n,'raw_sha256':hashlib.sha256(raw).hexdigest(),'actual_saving_bytes':delta,'integer_cost_saving_bytes':saving,'f32_cost_saving_bytes':row['ideal_saving_bytes'],'max_f32_reconstruction_error_bits_per_byte':error,'all_integer_replay_exact':True,'neutral_archive_exact':True,'raw_decode_exact':True})
out={'native_evidence_files_verified':len(idx),'status':'PASS_LOCAL_INDEPENDENT_REPLAY_NO_COMPRESSION_PROMOTION','results':results,'native_zip_sha256':hashlib.sha256(pathlib.Path('research_round7_native_calibration_20261005.zip').read_bytes()).hexdigest()}
pathlib.Path('research_round7_native_calibration_local_validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
