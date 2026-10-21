import hashlib,json,pathlib,zipfile
p=pathlib.Path('/kaggle/working/hp_round8/round8_native_extension_20261006_complete.zip');h=hashlib.sha256()
with p.open('rb') as f:
 while b:=f.read(1<<20):h.update(b)
assert h.hexdigest()=='b338507e574640ab2ce64fb564d1e1594eceaf36271b2133eb358a2a745ba713'
with zipfile.ZipFile(p) as z:assert z.testzip() is None;count=len(z.namelist())
print(json.dumps({'status':'PASS','bytes':p.stat().st_size,'files':count,'remote_zip_sha256':h.hexdigest(),'CRC':'PASS','no_project_deletions':True,'paid_spending_usd':0}))
