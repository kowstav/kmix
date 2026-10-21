"""Stream full entry SHA/CRC verification without extracting or deleting content."""
import pathlib,json,hashlib,zipfile,datetime
P=pathlib.Path(__file__).resolve().parent
def sha(file):
 h=hashlib.sha256()
 with file.open('rb') as f:
  while chunk:=f.read(1<<20):h.update(chunk)
 return h.hexdigest()
meta=json.loads((P/'research_round9_compact_download_parts_v2_results.json').read_text(encoding='utf-8-sig'))
p=P/'research_round9_extended_evidence_v2.zip';assert p.stat().st_size==meta['source_bytes'];assert sha(p)==meta['source_sha256']
with zipfile.ZipFile(p) as z:
 rows=json.loads(z.read('bundle_entry_manifest.json'));assert len(z.namelist())==len(rows)+1
 for row in rows:
  h=hashlib.sha256();n=0
  with z.open(row['file']) as f:
   while chunk:=f.read(1<<20):h.update(chunk);n+=len(chunk)
  assert n==row['bytes'] and h.hexdigest()==row['sha256'],row['file']
result={'status':'LOCAL_FULL_ZIP_CRC_AND_EVERY_ENTRY_SHA_PASS','bytes':p.stat().st_size,'sha256':meta['source_sha256'],'entries':len(rows)+1,'source_entries':len(rows),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[]}
(P/'research_round9_extended_evidence_v2_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
