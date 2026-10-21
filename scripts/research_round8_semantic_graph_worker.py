import datetime,hashlib,json,lzma,os,pathlib,re,subprocess,time,traceback,urllib.request,zipfile,zlib
import numpy as np
R=pathlib.Path('/kaggle/working/hp_round8');P=pathlib.Path('/kaggle/working/hp_round7');D=R/'semantic_graph_v1';D.mkdir(exist_ok=False)
URL='https://nlp.stanford.edu/data/wordvecs/glove.2024.wikigiga.50d.zip'
m={'status':'RUNNING','pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'session':355655943,'sources_url':URL,'vector_license':'PDDL 1.0','deletions':[],'paid_rental_usd':0,'core_retraining':False}
def save(): (D/'manifest.json').write_text(json.dumps(m,indent=2))
def hashed(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'bytes':p.stat().st_size,'sha256':h.hexdigest()}
save()
try:
 start=time.monotonic();dst=D/'glove.2024.wikigiga.50d.zip';request=urllib.request.Request(URL,headers={'User-Agent':'Hutter-compression-research/1.0'})
 with urllib.request.urlopen(request,timeout=45) as source,dst.open('xb') as target:
  m['download_headers']={k:source.headers.get(k) for k in ['Content-Length','ETag','Last-Modified']};save()
  while True:
   chunk=source.read(1024*1024)
   if not chunk:break
   target.write(chunk)
 m['download_seconds']=time.monotonic()-start;m['download']=hashed(dst);m['status']='SELECTING_VECTORS';save()
 words=re.findall(rb'[a-z]+',(P/'preserved/gen/.dict').read_bytes());assert len(words)==44515
 ids={w:i for i,w in enumerate(words)};vectors=np.zeros((len(words),50),dtype=np.float32);found=np.zeros(len(words),dtype=np.bool_);lines=0
 with zipfile.ZipFile(dst) as archive:
  names=[i.filename for i in archive.infolist() if not i.is_dir() and i.filename.endswith('.txt')];assert len(names)==1,names
  m['zip_members']=[{'name':i.filename,'bytes':i.file_size} for i in archive.infolist()];save()
  with archive.open(names[0]) as source:
   for line in source:
    lines+=1;word,sep,rest=line.partition(b' ')
    if word in ids:
     row=np.fromstring(rest.decode('ascii'),sep=' ',dtype=np.float32);assert row.shape==(50,) and np.isfinite(row).all();i=ids[word];assert not found[i];vectors[i]=row;found[i]=True
 np.save(D/'selected_vectors.npy',vectors,allow_pickle=False);m['vectors']=hashed(D/'selected_vectors.npy');m['matched_words']=int(found.sum());m['dictionary_words']=len(words);m['vector_lines']=lines;m['status']='BUILDING_GRAPH';save()
 import torch
 torch.set_num_threads(2);device='cuda:0' if torch.cuda.is_available() else 'cpu'
 constructors=set((P/'research_round7_remaining_constructors.txt').read_bytes().split());allowed=np.array([i for i,w in enumerate(words) if found[i] and len(w)>=3 and w not in constructors],dtype=np.int64)
 vv=torch.from_numpy(vectors).to(device);vv=torch.nn.functional.normalize(vv,dim=1);candidates=vv[torch.from_numpy(allowed).to(device)];graph=np.empty((len(words),8),dtype='<u2');graph_start=time.monotonic()
 with torch.no_grad():
  for i in range(0,len(words),1024):
   hi=min(i+1024,len(words));scores=vv[i:hi]@candidates.T;local=np.searchsorted(allowed,np.arange(i,hi));valid=(local<len(allowed));valid[valid]&=allowed[local[valid]]==np.arange(i,hi)[valid]
   rr=np.flatnonzero(valid);scores[torch.tensor(rr,device=device),torch.tensor(local[valid],device=device)]=-float('inf')
   neighbors=allowed[torch.topk(scores,8,dim=1).indices.cpu().numpy()];graph[i:hi]=neighbors
   for j in range(i,hi):
    if not found[j]:graph[j]=j
 graph.tofile(D/'semantic_k8.u16');np.savetxt(D/'semantic_k8.txt',graph,fmt='%d')
 blob=(D/'semantic_k8.u16').read_bytes();m['graph']={**hashed(D/'semantic_k8.u16'),'shape':list(graph.shape),'zlib9_bytes':len(zlib.compress(blob,9)),'lzma6_bytes':len(lzma.compress(blob,preset=6)),'construction_seconds':time.monotonic()-graph_start,'device':device,'allowed_neighbors':len(allowed),'missing_vector_self_fallback':int((~found).sum()),'torch_version':torch.__version__}
 assert ((graph>=0)&(graph<len(words))).all();m['selftests']={'shape_bounds':'PASS','self_exclusion_for_present_vectors':bool(all(i not in graph[i] for i in np.flatnonzero(found))),'source_sha_recorded':True};assert m['selftests']['self_exclusion_for_present_vectors']
 m.update(status='COMPLETE_GRAPH_NOT_COMPRESSION_RESULT',wall_seconds=time.monotonic()-start,finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
