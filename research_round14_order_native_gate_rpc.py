from pathlib import Path
import json,hashlib,zipfile,sys,unittest,time
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_order_native_gate');assert not R.exists();R.mkdir()
prepared=json.loads((W/'prepared_order_native_v4.json').read_text());raw=(W/'sources_order_native_v4.zip.dat').read_bytes();assert hashlib.sha256(raw).hexdigest()==prepared['source_sha256']
with zipfile.ZipFile(W/'sources_order_native_v4.zip.dat') as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(R/e['path']).resolve();assert p.is_relative_to(R);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(R))
suite=unittest.defaultTestLoader.discover(str(R/'tests'),pattern='test_article_order_native.py');result=unittest.TextTestRunner().run(suite)
assert result.wasSuccessful() and result.testsRun==2 and not result.skipped
from hutter_research import article_order_native as order
rows=[]
for name,level in [('region_0_8_False.raw',8),('region_2_16_True.raw',16),('region_3_8_False.raw',8)]:
    raw=(Path('/root/r14_backend_probe')/name).read_bytes();pages=[raw[:8192],raw[8192:]];blob=order.compress(pages,[1,0],level);assert order.decompress(blob)==pages
    rows.append({'input':name,'order':level,'bytes':len(raw),'archive_bytes':len(blob),'exact':True})
m={'status':'PASS_NATIVE_ORDER_CONTAINER_AND_REAL_CASES','time':time.time(),'source_sha256':prepared['source_sha256'],'tests':result.testsRun,'real_cases':rows,'backend':order.backend_identity(),'temporary_scratch_created_and_removed':order.SCRATCH,'deletions':[]}
(W/'order_native_gate_v4.json').write_text(json.dumps(m,indent=2));print(json.dumps(m))
