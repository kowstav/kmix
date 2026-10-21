"""Finite A/B cost/cluster audit; never selects from C/D or modifies core files."""
import datetime, hashlib, json, math, pathlib, re, time
import numpy as np

R=pathlib.Path('/kaggle/working/hp_round8');N=R/'atom_cache_v1';D=R/'canonical_cost_atlas_v4';D.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def inv(c):
 if 123<=c<127:c+=80-123
 elif 80<=c<84:c-=80-123
 elif 58<=c<=63 or 74<=c<=79:c^=0x70
 if c in (88,96):c^=88^96
 return c
def code(j):
 if j<80:v=[128+j]
 elif j<3920:j-=80;v=[208+j//80,128+j%80]
 else:j-=3920;v=[240+(j//80)//32,208+(j//80)%32,128+j%80]
 return bytes(map(inv,v))
dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic';words=re.findall('[a-z]+',dictionary.read_text());assert len(words)==44515
mapping={code(j):w for j,w in enumerate(words)};assert len(mapping)==44515
def encode_marker(t):
 out=bytearray()
 for s in re.findall('[a-z]+|[^a-z]',t):out.extend(code(words.index(s)) if s.isalpha() else bytes([inv(ord(s))]))
 return bytes(out)
marker=encode_marker('  <page>\n    <title>')
constructors=set('the a an is are was were be been being and or but if then as at by for from in of on to with that which who whom whose this these those it its he she they we you i not no now there here when where how what why do does did have has had can could shall should will would may might must than so all any some such also into over under between through after before during'.split())
nm=json.loads((N/'manifest.json').read_text());assert nm['dictionary_sha256']==sha(dictionary)
manifest={'status':'RUNNING','session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':__import__('os').getpid(),'scope':'canonical cold A/B dictionary-code cost attribution and fixed causal cluster KT diagnostic; no linguistic/POS claim','confirmation_used':False,'core_retraining':False,'paid_rental_usd':0,'deletions':[],'production_stream':nm['production_stream'],'dictionary_sha256':sha(dictionary),'source_sha256':sha(pathlib.Path(__file__)),'slices':[],'cluster_definition':'(previous_completed_atom_class in 0..4, atom_depth in 0..2, byte_bit_position in 0..7, native p1 bucket in 0..31); all assigned before current bit target','cluster_prior':'.5/.5 Krichevsky-Trofimov per cluster; global half-prior mixture of identity and this complete cluster expert'}
(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
try:
 for s in 'ab':
  started=time.monotonic();raw=(N/(s+'512k.bin')).read_bytes();v=next(v for v in nm['native_exports'] if v['slice']==s);assert hashlib.sha256(raw).hexdigest()==v['input_sha256'];pp=N/(s+'_native/final_p.u16');assert sha(pp)==v['final_p_sha256'];p=np.fromfile(pp,dtype='<u2').astype(np.int32).reshape(-1,8);assert len(p)==len(raw) and p.min()>0
  y=((np.frombuffer(raw,dtype=np.uint8)[:,None]>>(7-np.arange(8)))&1);cost=-np.log2(np.where(y,p,65536-p)/65536.);bytecost=cost.sum(axis=1);start=raw.find(marker)+len(marker);assert start>=len(marker)
  aggregate={};classbits={};classcount={};literal={};depth=0;atom=bytearray();atomcost=0.;escape=False;prev=0;counts=np.zeros((3840,2),np.int64);stats={};kt_bits=0.;mix_bits=0.;log_odds=0.;ideal_mix_bits=0.;p_hash=hashlib.sha256();pending=[]
  for i,byte in enumerate(raw):
   for b in range(8):
    cluster=(((prev*3+min(depth,2))*8+b)*32+min(31,int(p[i,b])//2048));c=counts[cluster];q=(c[1]+.5)/(int(c.sum())+1);base=float(p[i,b])/65536.;e=math.exp(-abs(log_odds));post=1/(1+e) if log_odds>=0 else e/(1+e);pred=post*base+(1-post)*q;pq=min(65535,max(1,int(math.floor(pred*65536+.5))));target=int(y[i,b]);lik_base=base if target else 1-base;lik_kt=q if target else 1-q;lik_mix=pred if target else 1-pred;ktc=-math.log2(lik_kt);qc=-math.log2((pq if target else 65536-pq)/65536.);ic=-math.log2(lik_mix);bc=float(cost[i,b]);kt_bits+=ktc;mix_bits+=qc;ideal_mix_bits+=ic;log_odds+=math.log(lik_base)-math.log(lik_kt);c[target]+=1
    row=stats.setdefault(cluster,[0,0.,0.,0.]);row[0]+=1;row[1]+=bc;row[2]+=ktc;row[3]+=qc;pending.append(pq)
   if len(pending)>=65536:p_hash.update(np.asarray(pending,dtype='<u2').tobytes());pending=[]
   if i<start:classbits['sync_prefix']=classbits.get('sync_prefix',0.)+float(bytecost[i]);continue
   if escape:kind='escaped_payload';key=str(byte);escape=False;prev=4;value=float(bytecost[i])
   else:
    atom.append(byte);atomcost+=float(bytecost[i]);original=inv(byte);depth+=1
    if not (original<208 or depth==3):continue
    encoded=bytes(atom);word=mapping.get(encoded)
    if word is not None:kind='constructor_dictionary' if word in constructors else 'other_dictionary';key=word;prev=1 if word in constructors else 2
    else:assert len(atom)==1 and original<128;kind='literal_or_control';key=str(original);prev=3;escape=original==12;literal[original]=literal.get(original,0)+1
    value=atomcost;atom=bytearray();atomcost=0.;depth=0
   classbits[kind]=classbits.get(kind,0.)+value;classcount[kind]=classcount.get(kind,0)+1
   a=aggregate.setdefault((kind,key),[0,0.,0.]);a[0]+=1;a[1]+=value;a[2]=max(a[2],value)
  if atom:classbits['partial_eof_atom']=atomcost
  if pending:p_hash.update(np.asarray(pending,dtype='<u2').tobytes())
  total=float(cost.sum());closed_form_mixture_bits=float((-np.logaddexp(-total*math.log(2),-kt_bits*math.log(2))+math.log(2))/math.log(2));assert abs(ideal_mix_bits-closed_form_mixture_bits)<1e-5;assert abs(sum(classbits.values())-total)<1e-5;assert total-closed_form_mixture_bits>=-1.00000001
  ranked=sorted([{'kind':k,'label':w,'occurrences':v[0],'native_bits':v[1],'mean_bits_per_atom':v[1]/v[0],'max_bits_per_atom':v[2]} for (k,w),v in aggregate.items()],key=lambda r:r['native_bits'],reverse=True)
  cs=[{'cluster':k,'count':r[0],'native_bits':r[1],'KT_prequential_bits':r[2],'KT_increment_bits':r[1]-r[2],'global_mixture_bits':r[3]} for k,r in stats.items()]
  row={'slice':s,'input_sha256':v['input_sha256'],'native_p_sha256':v['final_p_sha256'],'bytes':len(raw),'sync_prefix_bytes':start,'total_native_likelihood_bytes':total/8,'class_cost_bytes':{k:v/8 for k,v in classbits.items()},'class_occurrences':classcount,'distinct_dictionary_words_seen_in_slice':sum(k[0].endswith('_dictionary') for k in aggregate),'cost_reconciliation_bits_error':sum(classbits.values())-total,'dictionary_words_top100': [r for r in ranked if r['kind'].endswith('_dictionary')][:100],'all_atoms_top100':ranked[:100],'cluster_count':len(stats),'KT_total_saving_bytes':(total-kt_bits)/8,'identity_plus_KT_ideal_saving_bytes':(total-ideal_mix_bits)/8,'batch_exact_mixture_ideal_saving_bytes':(total-closed_form_mixture_bits)/8,'identity_plus_KT_Q16_saving_bytes':(total-mix_bits)/8,'Q16_tax_bytes':(mix_bits-ideal_mix_bits)/8,'mixture_prediction_sha256':p_hash.hexdigest(),'all_cluster_rows':cs,'wall_seconds':time.monotonic()-started,'log_posterior_odds_used':True,'independent_batch_mixture_bits_error':ideal_mix_bits-closed_form_mixture_bits,'not_recoverable_savings_bound':True,'word_cost_excludes_separate_case_controls':True,'header_literal_escape_and_partial_eof_cost_included':True}
  (D/(s+'.json')).write_text(json.dumps(row,indent=2));manifest['slices'].append({k:v for k,v in row.items() if k not in ('all_cluster_rows','all_atoms_top100','dictionary_words_top100')});(D/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({'slice':s,'native_bytes':total/8,'mixture_saving_bytes':row['identity_plus_KT_Q16_saving_bytes']}),flush=True)
 manifest.update(status='COMPLETE_CANONICAL_COST_ATLAS',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
except BaseException as e:
 manifest.update(status='FAIL',error=repr(e));(D/'manifest.json').write_text(json.dumps(manifest,indent=2));raise

