import pathlib,json,hashlib
R=pathlib.Path('/kaggle/working/hp_round8');stream=R/'lexical_full_prepare_v1/lexical_full_ready.wrt';offsets=dict(a=0,b=102635191,c=310000000,d=520000000,e=190000000,f=430000000);out=[]
with stream.open('rb') as f:
 for s,off in offsets.items():
  p=R/'atom_cache_v1'/(s+'512k.bin') if s in 'abcd' else R/'source_wide_confirmation_v1'/(s+'512k')/'input.bin';f.seek(off);canonical=f.read(524288);raw=p.read_bytes();out.append({'slice':s,'canonical_matches_native_trace_input':canonical==raw,'canonical_SHA256':hashlib.sha256(canonical).hexdigest(),'native_input_SHA256':hashlib.sha256(raw).hexdigest()})
print(json.dumps(out));(pathlib.Path('/kaggle/working/hp_round9/word_input_gate.json')).write_text(json.dumps(out,indent=2))
