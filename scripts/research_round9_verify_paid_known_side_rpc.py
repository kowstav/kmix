"""Independently reconstruct every decoder hint from the counted side container.

Never consult the original input or frequency census to construct mask/values.
Byte identity with the files used in the completed independent native decodes
is a compositional verification, without repeating the same expensive decodes.
"""
import pathlib,json,zlib,struct,hashlib,time,os
R=pathlib.Path('/kaggle/working/hp_round9');D=R/'known_literals_side_verify_v2';D.mkdir(exist_ok=False);S=pathlib.Path('/root/hp_round9/known_literals_v1');rows=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def varint(b,p):
 v=shift=0
 while True:
  assert p<len(b),'truncated side varint';c=b[p];p+=1;v|=(c&127)<<shift
  if c<128:return v,p
  shift+=7;assert shift<=63
manifest=json.loads((R/'known_literals_v1/manifest.json').read_text());assert manifest['status'].startswith('COMPLETE')
for row in manifest['candidates']:
 name=row['name'];packed=(S/(name+'.hpknown')).read_bytes();assert packed[:8]==b'HPKNOWN1';mode=packed[8];assert mode in [0,1];slen=struct.unpack_from('<I',packed,9)[0];side=zlib.decompress(packed[13:13+slen]);assert side[:8]==b'HPMSK1\x00\x00';length=struct.unpack_from('<I',side,8)[0];mask=bytearray(length);values=bytearray(length);literal=bytearray(length);count,p=varint(side,12);previous=0
 for _ in range(count):
  gap,p=varint(side,p);n,p=varint(side,p);lo=previous+gap;hi=lo+n;assert n>0 and hi<=length and p+n<=len(side);mask[lo:hi]=b'\x01'*n;values[lo:hi]=side[p:p+n] if mode==0 else b' '*n;literal[lo:hi]=side[p:p+n];p+=n;previous=hi
 assert p==len(side);C=S/name;assert bytes(mask)==(C/'mask.u8').read_bytes() and bytes(values)==(C/'values.u8').read_bytes();assert packed[13+slen:]==(C/'out.cmx').read_bytes()
 decoded=S/(name+'_decode')/'decoded.bin';restored=bytearray(decoded.read_bytes());assert len(restored)==length
 if mode==1:
  for i,flag in enumerate(mask):
   if flag:assert restored[i]==32;restored[i]=literal[i]
 assert sha(restored)==manifest['baseline']['input_sha256']
 rows.append({'name':name,'all_hints_constructed_from_paid_container_only':True,'known_mask_sha256':sha(mask),'known_values_sha256':sha(values),'exact_files_used_by_independent_native_decoder':True,'original_input_restored_sha256':sha(restored),'full_container_bytes':len(packed),'side_bytes':slen,'spans':count})
out={'status':'COMPLETE_INDEPENDENT_PAID_SIDE_HINT_RECONSTRUCTION_IDENTITY','pid':os.getpid(),'finished':time.time(),'scope':'independent side parser, mask/value identity with executed native decodes and original encoded-input reconstruction; production native side loader and full package still pending','rows':rows,'deletions':[],'spending_usd':0};(D/'manifest.json').write_text(json.dumps(out,indent=2));print(json.dumps({'status':out['status'],'candidates':len(rows)}))
