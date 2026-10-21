import pathlib,zipfile,json,hashlib
P=pathlib.Path(__file__).resolve().parent;source=P/'research_round9_extended_evidence_v2.zip';dest=P/'research_round10_old_native_models.zip'
with zipfile.ZipFile(source) as z:
 manifest={v['file']:v for v in json.loads(z.read('bundle_entry_manifest.json'))}
 files=[v for v in z.namelist() if v.startswith('native_models/') and v.endswith('.tfwc2')]
 assert len(files)==4,files
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as o:
  rows=[]
  for name in files:
   data=z.read(name);s=hashlib.sha256(data).hexdigest();assert s==manifest[name]['sha256']
   o.writestr(name,data);rows.append({'file':name,'bytes':len(data),'sha256':s})
  o.writestr('manifest.json',json.dumps(rows,indent=2))
result={'archive_bytes':dest.stat().st_size,'archive_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'entries':rows,'source_bundle_sha256':'5467487020dd54a192bafe6fb5c76e3386d8ddadbc2423ba49d924d15f7c7656'}
(P/'research_round10_old_native_models_zip_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
