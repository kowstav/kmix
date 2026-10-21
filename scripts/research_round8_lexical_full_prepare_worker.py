import datetime,hashlib,json,os,pathlib,shutil,subprocess,time,traceback,zipfile
P=pathlib.Path('/kaggle/working/hp_round7');R=pathlib.Path('/kaggle/working/hp_round8');D=R/'lexical_full_prepare_v1';D.mkdir(exist_ok=False)
S=pathlib.Path('/root/hp/round8_lexical_full_prepare_v1');assert not S.exists();S.mkdir(parents=True);T=S/'tree'
m={'status':'RUNNING','pid':os.getpid(),'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'production lexical preparation and full inverse only; no entropy archive or gain','scratch':str(S),'core_retraining':False,'paid_rental_usd':0,'deletions':[],'scratch_replacements':['Native R1 inverse mutates only a separately copied encoded scratch stream; original and models remain preserved'],'results':[]}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while chunk:=f.read(1<<20):h.update(chunk)
 return h.hexdigest()
def save(stage):m['stage']=stage;(D/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({'status':m['status'],'stage':stage}),flush=True)
def run(cmd,cwd,env,label):
 t=time.monotonic()
 with (D/(label+'.log')).open('x') as f:p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);_,status,u=os.wait4(p.pid,0);p.returncode=os.waitstatus_to_exitcode(status)
 a={'wall_seconds':time.monotonic()-t,'user_seconds':u.ru_utime,'system_seconds':u.ru_stime,'max_rss_kbytes':u.ru_maxrss,'returncode':p.returncode}
 m['results'].append({'stage':label,'accounting':a});save(label)
 if p.returncode:raise RuntimeError((label,p.returncode))
 return a
try:
 assert shutil.disk_usage(S).free>30_000_000_000 and shutil.disk_usage(R).free>1_200_000_000
 save('isolated native preparation source');shutil.copytree(R/'native_hidden_trace_v1/tree',T,symlinks=True)
 runner=T/'src/runner.cpp';s=runner.read_text();anchor='    if (selfextract_comp() != 0) {';assert s.count(anchor)==1;s=s.replace(anchor,'    if (!std::getenv("HP_LEX_PREP_ONLY") && selfextract_comp() != 0) {')
 anchor='int main(int argc, char** argv) {';assert s.count(anchor)==1
 inverse=r'''int main(int argc, char** argv) {
  // Isolated preprocessing utility: restores a copied stream, never entropy-decodes.
  if (std::getenv("HP_LEX_INVERSE_ONLY")) {
    if (argc != 2) return 41;
    if (!r1_reorder::ExtractSideFromFile(argv[1], ".r1_inverse_side") ||
        !r1_reorder::RestoreEncodedTailFile(argv[1], ".r1_inverse_side")) return 42;
    FILE* in = std::fopen(argv[1], "rb");
    FILE* out = std::fopen(".input_decomp", "wb");
    FILE* dict = std::fopen(".dict", "rb");
    if (!in || !out || !dict) return 43;
    preprocessor::Decode(in, out, dict);
    std::fclose(in); std::fclose(out); std::fclose(dict);
    split4Decomp(); phda9_resto(); sort();
    cat(".intro_decomp", ".main_decomp_restored_sorted", "un1_d");
    cat("un1_d", ".coda_decomp", "enwik9_uncompressed");
    return 0;
  }
'''
 s=s.replace(anchor,inverse);runner.write_text(s);m['utility_runner_sha256']=sha(runner)
 flags='-DSEED=923 -DUPDATE_LIMIT=3000 -DPPMD_MEM_MB=3500 -DCMIX_L0_LR_SCALE=0.6 -DCMIX_L1_LR_SCALE=0.25 -DCMIX_L0_MIXER_MASK=0x42e72du -DFXCM_CM_DIV=2';tf='-DQMAT_CODEBOOK=1 -DQMAT_WMAX=21 -DQMAT_SMALL_W8=1 -DTF_ACTQ_DYN=1 -DTF_AVX512=1';env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','HP_LEX_','FX_PREPARE'))};env['PATH']=str(T/'task_bin')+os.pathsep+env['PATH']
 run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+flags,'CFLAGS_TF_DEFINES='+tf],T,env,'build');binary=T/'cmix';m['utility_binary_sha256']=sha(binary)
 save('verified source corpus extraction');zip_path=P/'preserved/data/enwik9.zip'
 with zipfile.ZipFile(zip_path) as z:
  member=z.getinfo('enwik9');assert member.file_size==1_000_000_000
  with z.open(member) as src,(S/'enwik9').open('xb') as dst:shutil.copyfileobj(src,dst,1<<20)
 original_sha=sha(S/'enwik9');assert original_sha=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc';m['original_sha256']=original_sha
 shutil.copy2(T/'dictionary/english.dic',S/'.dict');shutil.copy2(T/'src/readalike_prepr/data/new_article_order',S/'.new_article_order');m['order_sha256']=sha(S/'.new_article_order');assert m['order_sha256']=='eecd462c29319bab185b48229c4d09ab52f16ca9c582e8e32eff9a7c2a7de39e';m['dictionary_sha256']=sha(S/'.dict')
 save('full production lexical preparation');prep_env={**env,'HP_LEX_PREP_ONLY':'1','FX_PREPARE_ONLY':'1','LAB_KEEP_TEMP':'1'};run([str(binary),'-e',str(S/'enwik9'),'lex_prepared','--bytes-only','--save-ppmd-bytes','unused_tokens.bin'],S,prep_env,'prepare')
 prepared=S/'lex_prepared.cmix.temp';assert prepared.is_file() and prepared.stat().st_size>586459321;side=S/'.r1_payload_lex_side';assert side.is_file();m['prepared']={'bytes':prepared.stat().st_size,'sha256':sha(prepared)};m['side']={'bytes':side.stat().st_size,'sha256':sha(side)}
 save('full inverse of copied lexical prepared stream');inverse_copy=S/'inverse_lexical.wrt';shutil.copy2(prepared,inverse_copy);run([str(binary),str(inverse_copy)],S,{**env,'HP_LEX_INVERSE_ONLY':'1'},'inverse');restored=S/'enwik9_uncompressed';assert restored.stat().st_size==1_000_000_000 and sha(restored)==original_sha;m['full_inverse_exact']=True
 assert shutil.disk_usage(R).free>prepared.stat().st_size+100_000_000;shutil.copy2(prepared,D/'lexical_full_ready.wrt');shutil.copy2(side,D/'lexical_side.bin');m['preserved_full_stream_sha256']=sha(D/'lexical_full_ready.wrt');assert m['preserved_full_stream_sha256']==m['prepared']['sha256'];m['scratch_apparent_bytes']=sum(p.stat().st_size for p in S.rglob('*') if p.is_file());assert m['scratch_apparent_bytes']<100_000_000_000
 m.update(status='COMPLETE_LEXICAL_PREPARATION_FULL_INVERSE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('production stream preserved; native/full entropy coding still unexecuted')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no automatic relaunch');raise
