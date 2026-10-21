"""Post-training CPU export repair; independent native acceptance is separate.

Reads the original container's storage types and order. Rounds only fields that
were actually BF16 in that model, using IEEE round-to-nearest, ties-to-even.
Frozen quantized code indices, config and FP32 RoPE retain their original types.
"""
import pathlib,json,hashlib,time,zipfile
import numpy as np
from hutter_research import native_weights as v3,legacy_weights as v2

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bf16_bits(a):
 a=np.asarray(a,dtype='<f4');assert np.isfinite(a).all()
 u=a.view('<u4');return ((u+np.uint32(0x7fff)+((u>>16)&np.uint32(1)))>>16).astype('<u2')
def promoted_bf16(a):return (np.asarray(a,dtype='<u2').astype('<u4')<<16).view('<f4')

def repair(original_file,old_file,dest):
 original=v3.read_tensor_file_v3(str(original_file));trained=v2.read_tensor_file_v2(str(old_file));assert set(original)==set(trained)
 entries=[];rounded_fields=[]
 for name,(original_type,old_value) in original.items():
  dt,a=trained[name];assert a.shape==old_value.shape
  if original_type==1 and dt==2:
   rounded=bf16_bits(a);entries.append((name,1,rounded));rounded_fields.append({'name':name,'elements':a.size,'changed_from_original':int((rounded!=old_value).sum())})
  elif original_type==1 and dt==1:entries.append((name,dt,a))
  else:
   assert dt==original_type,(name,dt,original_type);entries.append((name,dt,a))
 v3.write_tensor_file_v3(str(dest),entries);decoded=v3.read_tensor_file_v3(str(dest));v3._verify_equal({n:(dt,a) for n,dt,a in entries},decoded)
 return {'old_model_bytes':old_file.stat().st_size,'new_model_bytes':dest.stat().st_size,'growth_per_copy':dest.stat().st_size-original_file.stat().st_size,
         'new_sha256':sha(dest),'original_sha256':sha(original_file),'rounded_fields':rounded_fields,
         'native_reader_and_archive_gate':'PENDING; Python codec roundtrip does not substitute for native reader/independent decode'}

if __name__=='__main__':
 P=pathlib.Path(__file__).resolve().parent;S=P/'research_round10_bf16_repaired_models';S.mkdir(exist_ok=True)
 original=P/'research_round7_sources/lex_h1_run11.tfwc2';assert sha(original)=='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
 m={'status':'RUNNING_CPU_POST_TRAINING_BF16_REPAIR','started':time.time(),'models':[]}
 def save():(P/'research_round10_bf16_repair_results.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
 save();orig=v3.read_tensor_file_v3(str(original));neutral=S/'neutral.tfwc3';v3.write_tensor_file_v3(str(neutral),[(n,dt,a) for n,(dt,a) in orig.items()]);assert sha(neutral)==sha(original)
 m['zero_update_byte_identity']=True;save()
 with zipfile.ZipFile(P/'research_round10_old_native_models.zip') as z:
  for name in ['unweighted','cut107_half','cut1392_zero']:
   source=S/(name+'.old.tfwc2');source.write_bytes(z.read('native_models/'+name+'.tfwc2'))
   row=repair(original,source,S/(name+'.tfwc3'));row['name']=name;m['models'].append(row);save();print(json.dumps({k:v for k,v in row.items() if k!='rounded_fields'}),flush=True)
 m.update(status='COMPLETE_CPU_BF16_REPAIR_PYTHON_PRICE_AND_NEUTRAL_IDENTITY',finished=time.time());save()
