import hashlib, json, os, shutil
from pathlib import Path
W = Path('/kaggle/working'); A = Path('/root/r12_assets'); A.mkdir(exist_ok=False)
CANON = W / 'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt'
NA = NB = 64 * 1048576
slices = {'A': {'file': 'stream_A.bin', 'abs_offset': 0, 'bytes': NA},
          'B': {'file': 'stream_B.bin', 'abs_offset': 300000000, 'bytes': NB}}
with open(CANON, 'rb') as f:
    for k, s in slices.items():
        f.seek(s['abs_offset']); data = f.read(s['bytes']); assert len(data) == s['bytes']
        (A / s['file']).write_bytes(data)
shutil.copy2(W / 'hp_round8/native_stage_trace_v1/tree/cmix', A / 'native_cmix')
shutil.copy2(W / 'hp_round7/lex_audit/lex_h1_run11.tfwc2', A / 'lex_h1_run11.tfwc2')
shutil.copy2(W / 'hp_round8/native_stage_trace_v1/tree/dictionary/english.dic', A / 'english.dic')
shutil.copy2(W / 'hp_round7/preserved/data/vocab.bm', A / 'vocab.bm')
for f in ['stream_replay.cpp', 'integer_mixer.h', 'long_memory.h', 'probability_tables.inc', 'r12_driver.py']:
    shutil.copy2(W / 'hp_round12_claude/code' / f, A / f)
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        while b := fh.read(1 << 22): h.update(b)
    return h.hexdigest()
files = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(A.iterdir())}
meta = {'purpose': 'R12 warm-stream replay assets (Claude audit round)', 'canonical_stream_sha256': sha(CANON),
        'canonical_stream_bytes': CANON.stat().st_size, 'slices': slices, 'files': files}
(A / 'r12_manifest.json').write_text(json.dumps(meta, indent=1))
(A / 'dataset-metadata.json').write_text(json.dumps({'title': 'hutter-r12-warm-stream-assets',
    'id': 'chaoscpp/hutter-r12-warm-stream-assets', 'licenses': [{'name': 'other'}]}))
for n, i in files.items(): print(n, i['bytes'], i['sha256'][:16])
print('canonical', meta['canonical_stream_sha256'][:16])
