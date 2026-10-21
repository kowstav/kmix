import datetime,gzip,hashlib,json,os,pathlib,re,resource,time,traceback,zipfile
from collections import Counter
import xml.etree.ElementTree as ET
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'rarity_census_v1';D.mkdir(exist_ok=False)
Z=pathlib.Path('/kaggle/working/hp_round7/preserved/data/enwik9.zip')
rx=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")
m={'status':'RUNNING','pid':os.getpid(),'session':355735431,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_spending_usd':0,'deletions':[],'scope':'complete XML text pages, ASCII casefold lexical diagnostic; not all coded outcomes'}
t0=time.monotonic()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def save(stage):
 m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(stage,flush=True)
def pages(audit=None):
 h=hashlib.sha256();read=0;buf=b'';count=0
 with zipfile.ZipFile(Z) as z:
  candidates=[v for v in z.infolist() if v.file_size==1000000000];assert len(candidates)==1
  if audit is not None:audit['member']=candidates[0].filename
  with z.open(candidates[0]) as f:
   while chunk:=f.read(1<<20):
    h.update(chunk);read+=len(chunk);buf+=chunk
    while True:
     start=buf.find(b'<page>')
     if start<0:
      buf=buf[-16:];break
     end=buf.find(b'</page>',start)
     if end<0:buf=buf[start:];break
     data=buf[start:end+7];buf=buf[end+7:];count+=1
     page=ET.fromstring(data);text=page.find('./revision/text');yield count,Counter(rx.findall((text.text or '').lower())) if text is not None else Counter()
    assert len(buf)<128*1024*1024,'unexpected enormous XML page or missing framing'
 if audit is not None:audit.update(original_bytes=read,original_sha256=h.hexdigest(),complete_pages=count,incomplete_terminal_page_bytes=len(buf) if b'<page>' in buf else 0)
 assert read==1000000000 and h.hexdigest()=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
try:
 save('streaming original XML pages; no extraction or deletion')
 counts=Counter();df=Counter();psum=Counter();pmax={};n=0;nonempty=0;local_count_cuts=[2,4,8];local_frac_cuts=[.001,.005,.01,.02];local={str(c):{'removed_occurrences':0,'removed_word_article_pairs':0,'empty_retained_articles':0} for c in local_count_cuts+local_frac_cuts}
 audit={}
 for i,c in pages(audit):
  size=sum(c.values());n+=size;counts.update(c);df.update(c.keys())
  if size:
   nonempty+=1
   for w,f in c.items():v=f/size;psum[w]+=v;pmax[w]=max(pmax.get(w,0.),v)
   for cut in local_count_cuts+local_frac_cuts:
    selected=[(w,f) for w,f in c.items() if (f<cut if isinstance(cut,int) else f/size<cut)];row=local[str(cut)];removed=sum(f for _,f in selected);row['removed_occurrences']+=removed;row['removed_word_article_pairs']+=len(selected);row['empty_retained_articles']+=int(removed==size)
  if i%20000==0:m['complete_pages_so_far']=i;m['tokens_so_far']=n;save('census progress '+str(i))
 histogram=Counter(counts.values());corpus={}
 for cut in [2,4,8,16,32,64,128,256,1024]:
  selected=[(f,k) for f,k in histogram.items() if f<cut];removed=sum(f*k for f,k in selected);corpus[str(cut)]={'rule':'count < cutoff','removed_types':sum(k for _,k in selected),'removed_occurrences':removed,'removed_occurrence_fraction':removed/n}
 for cut in [1e-6,1e-5,1e-4]:
  selected=[(f,k) for f,k in histogram.items() if f/n<cut];removed=sum(f*k for f,k in selected);corpus[str(cut)]={'rule':'corpus fraction < cutoff','removed_types':sum(k for _,k in selected),'removed_occurrences':removed,'removed_occurrence_fraction':removed/n}
 for cut,row in local.items():row['removed_occurrence_fraction']=row['removed_occurrences']/n;row['rule']='article count < cutoff' if cut in ['2','4','8'] else 'article fraction < cutoff'
 mass=[];remaining=n
 for f,k in sorted(histogram.items()):
  mass.append({'count':f,'types':k,'occurrences':f*k,'retained_fraction_if_mask_count_below_this':remaining/n});remaining-=f*k
 choices=[]
 for target in [.70,.85,.95]:
  candidates=[v for v in mass if v['retained_fraction_if_mask_count_below_this']>=target];row=min(candidates,key=lambda v:v['retained_fraction_if_mask_count_below_this']-target);choices.append({'requested_retained_fraction':target,**row})
 out=D/'word_article_frequencies.tsv.gz'
 with gzip.open(out,'wt',encoding='utf-8',newline='') as f:
  f.write('word\tcorpus_count\tcorpus_fraction\tcontaining_articles\tmax_article_fraction\tmean_fraction_in_containing_articles\n')
  for w,c in sorted(counts.items()):f.write(f'{w}\t{c}\t{c/n:.12g}\t{df[w]}\t{pmax[w]:.12g}\t{psum[w]/df[w]:.12g}\n')
 m.update(status='COMPLETE_RARITY_CENSUS_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),original=audit,total_tokens=n,unique_types=len(counts),nonempty_pages=nonempty,word_article_pairs=sum(df.values()),corpus_thresholds=corpus,article_thresholds=local,proposed_retention_cutoffs=choices,top_words=[{'word':w,'count':c,'fraction':c/n} for w,c in counts.most_common(30)],frequency_file={'remote':str(out),'bytes':out.stat().st_size,'sha256':sha(out)},source_hashes=[{'file':v,'sha256':sha(R/v)} for v in ['research_round8_rarity_census_worker.py','research_round8_rarity_mask_protocol.md']],accounting={'wall_seconds':time.monotonic()-t0,'user_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime,'system_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_stime,'max_rss_kbytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},training_evaluated=False,coded_bits_evaluated=False)
 save('complete frequency census; no inference gate or training claim')
except BaseException as e:
 m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved');raise
