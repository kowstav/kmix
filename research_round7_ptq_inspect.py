import pathlib,struct,json,numpy as np,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
path=out/'candidate_bf16.old.cpp_raw.bin'
data=path.read_bytes();p=12;rows=[]
count=struct.unpack_from('<I',data,8)[0]
for _ in range(count):
    n=struct.unpack_from('<I',data,p)[0];p+=4;name=data[p:p+n].decode();p+=n
    dtype=data[p];p+=1;ndim=struct.unpack_from('<I',data,p)[0];p+=4
    shape=struct.unpack_from('<'+'I'*ndim,data,p);p+=4*ndim;size=int(np.prod(shape))*(1 if dtype==0 else 2 if dtype==1 else 4)
    if dtype==0:
        a=np.frombuffer(data,dtype=np.int8,count=size,offset=p);rows.append({'name':name,'shape':shape,'values':size,'unit_magnitude':int(np.count_nonzero(np.abs(a)==1)),'zero':int(np.count_nonzero(a==0))})
    p+=size
if p!=len(data):raise RuntimeError('Malformed raw weight file')
print(json.dumps({'q4_tensors':len(rows),'q4_values':sum(r['values'] for r in rows),'total_unit_magnitude':sum(r['unit_magnitude'] for r in rows),'q4_rows':rows[:30],'raw_model_bytes':len(data),'binary_present':(out/'cmix_round7_baseline').exists(),'vocab_present':(out/'preserved/data/vocab.bm').exists()}))
