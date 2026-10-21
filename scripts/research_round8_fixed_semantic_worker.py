import os
os.environ['OPENBLAS_NUM_THREADS']='2'
import datetime,hashlib,itertools,json,pathlib,subprocess,time,traceback
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'fixed_semantic_v1';D.mkdir(exist_ok=False)
m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_rental_usd':0,'deletions':[],'results':[]}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
def run(cmd,log):
 with log.open('x') as f:
  start=time.monotonic();p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 account={'wall_seconds':time.monotonic()-start,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 if p.returncode:m['failed_runtime']=account;save();raise RuntimeError((cmd,p.returncode,str(log)))
 return account
save()
try:
 fitted=json.loads((R/'continuous_strength_v2/manifest.json').read_text());assert fitted['status']=='COMPLETE_FINITE_CONTINUOUS_DIAGNOSTIC';rows=fitted['results'];coefficient_file=D/'coefficients.txt';coefficient_file.write_text('\n'.join(str(len(a['coefficients']))+' '+' '.join(format(v,'.17g') for v in a['coefficients']) for a in rows));m['frozen_coefficients_sha256']=hashlib.sha256(coefficient_file.read_bytes()).hexdigest();m['coefficient_source_manifest_sha256']=hashlib.sha256((R/'continuous_strength_v2/manifest.json').read_bytes()).hexdigest();save()
 binary=D/'replay';m['compile']=run(['g++','-O3','-std=c++17',str(R/'research_round8_fixed_semantic.cpp'),'-o',str(binary)],D/'compile.log');m['binary']={'bytes':binary.stat().st_size,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()};m['source_sha256']=hashlib.sha256((R/'research_round8_fixed_semantic.cpp').read_bytes()).hexdigest();save()
 args=[str(P/'preserved/gen/.dict'),str(P/'research_round7_remaining_graph.txt'),str(P/'research_round7_remaining_constructors.txt'),str(R/'semantic_graph_v1/semantic_k8.u16')]
 def evaluate(s,limit):
  tag=s+('_128k' if limit else '_2m');raw=P/'preserved/slices'/(s+'2m.bin') if s in 'ab' else P/(s+'2m.bin');output=D/(tag+'.json');account=run([str(binary),str(raw),str(P/'lex_finalbit_2m_v1'/s/'final_p.u16'),*args,str(limit),str(output),str(coefficient_file)],D/(tag+'.log'));row=json.loads(output.read_text());row.update(slice=tag,accounting=account)
  if limit:
   row['python_integer_parity']=[]
   for i,a in enumerate(row['arms']):
    expected=rows[i]['evaluations']['abcd'.index(s)];sha=hashlib.sha256(pathlib.Path(str(output)+'.q'+str(i)).read_bytes()).hexdigest();error=abs(a['saving_bytes']-expected['q16_saving_bytes']);assert sha==expected['prediction_sha256'],(tag,i,'q16 parity');assert error<1e-7;row['python_integer_parity'].append({'name':a['name'],'sha256_equal':True,'saving_error_bytes':error})
  mg=np.fromfile(str(output)+'.marginals',dtype='<f8');assert len(mg)==44515 and np.isfinite(mg).all();semantic=row['arms'][1]['saving_bytes'];assert abs(mg.sum()+row['off_head_saving_bytes']-semantic)<1e-7
  row['marginal_sha256']=hashlib.sha256(pathlib.Path(str(output)+'.marginals').read_bytes()).hexdigest();row['optimal_sparse_before_loader_bytes']=row['off_head_saving_bytes']+float(np.maximum(mg-36,0).sum())-4-64-.125;row['selected_source_count']=int((mg>36).sum());row['maximum_source_marginal_bytes']=float(mg.max());output.write_text(json.dumps(row,indent=2));m['results'].append(row);save();print(json.dumps({'completed':tag,'arms':row['arms'],'best_sparse_bytes':row['optimal_sparse_before_loader_bytes']}),flush=True);return mg,row
 for s in 'abcd':evaluate(s,131072)
 m['all_24_independent_integer_sha256_checks']='PASS';m['status']='FULL_2M_CONFIRMATION_RUNNING';save();marginals=[];full=[]
 for s in 'abcd':mg,row=evaluate(s,0);marginals.append(mg);full.append(row)
 # Independent exhaustive subset reference; formula uses separable per-row charge.
 tiny=np.array([20.,45.,-2.,80.,35.9]);brute=max(sum(tiny[i]-36 for i,b in enumerate(mask) if b) for mask in itertools.product([0,1],repeat=len(tiny)));assert abs(brute-np.maximum(tiny-36,0).sum())<1e-12
 combined=np.sum(marginals,axis=0);dev=marginals[0]+marginals[1];selected=dev>36;allselected=combined>36
 def sparse(gains,off):return float(off+np.maximum(gains-36,0).sum()-4-64-.125)
 m['sparse_graph']={'scope':'exact finite selection with independent row charges; no loader or actual archive','row_bytes_per_copy':18,'copies':2,'count_bytes_per_copy':2,'coefficient_bytes_per_copy':32,'mode_bits':1,'independent_subset_enumeration':'PASS','combined_ABCD_best_bytes':sparse(combined,sum(r['off_head_saving_bytes'] for r in full)),'combined_selected_source_count':int(allselected.sum()),'AB_selected_source_ids':np.flatnonzero(selected).tolist(),'AB_best_bytes':sparse(dev,full[0]['off_head_saving_bytes']+full[1]['off_head_saving_bytes']),'CD_frozen_AB_selector_bytes_before_already_paid_assets':float(full[2]['off_head_saving_bytes']+full[3]['off_head_saving_bytes']+np.sum((marginals[2]+marginals[3])[selected])),'maximum_combined_marginal_bytes':float(combined.max())}
 m.update(status='COMPLETE_FIXED_CONFIRMATION_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
