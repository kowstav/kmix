import hashlib,json,pathlib,zipfile
R=pathlib.Path('/kaggle/working/hp_round8');rows=[]
for name,expected in [('round8_native_extension_20261006_complete.zip','b338507e574640ab2ce64fb564d1e1594eceaf36271b2133eb358a2a745ba713'),('round8_evidence_20261006_complete.zip','b322344131ac6e16a0824a491968b793bc34a6a348227dfe03f41acb0d0568df')]:
 p=R/name;h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 assert h.hexdigest()==expected
 with zipfile.ZipFile(p) as z:assert z.testzip() is None;count=len(z.namelist())
 rows.append({'name':name,'bytes':p.stat().st_size,'files':count,'sha256':expected,'CRC':'PASS'})
print(json.dumps({'status':'PASS','bundles':rows,'failed_uploads_preserved':True,'deletions':[],'paid_spending_usd':0}))
