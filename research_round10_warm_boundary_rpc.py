import pathlib,json,hashlib
W=pathlib.Path('/kaggle/working');S=W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
with S.open('rb') as f:head=f.read(128)
out={'canonical_head_hex':head.hex(),'raw_inputs':{},'trace_source':{}}
for p in [W/'hp_round8/atom_cache_v1/a512k.bin',W/'hp_round8/native_stage_trace_v1/a512k/input.bin',W/'hp_round7/lex_a2m.bin']:
 if p.is_file():
  with p.open('rb') as f:h=f.read(64)
  out['raw_inputs'][str(p)]={'head_hex':h.hex(),'match_offset':head.find(h),'size':p.stat().st_size}
for p in [W/'hp_round8/native_stage_trace_v1/tree/src/coder/encoder.cpp',W/'hp_round8/native_stage_trace_v1/tree/src/runner.cpp']:
 text=p.read_text();lines=text.splitlines();out['trace_source'][str(p)]=[{'line':i+1,'text':'\n'.join(lines[max(0,i-4):i+8])} for i,l in enumerate(lines) if 'LAB_' in l or 'WriteHeader' in l]
print(json.dumps(out))
