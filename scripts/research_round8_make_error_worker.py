
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
R=project_root(__file__)
base=(project_path('research_round8_atom_cache_worker.py', base=R)).read_text(encoding='utf-8')
start=base.index('try:\n lex=');end=base.index(" replay=D/'replay';",start)
prefix='''try:
 N=R/'atom_cache_v1';deadline=time.monotonic()+7200;save('waiting for existing canonical job; no duplicate native inference')
 while True:
  p=N/'manifest.json';nm=json.loads(p.read_text()) if p.exists() else {}
  if nm.get('status','').startswith('COMPLETE') or nm.get('status')=='FAIL':break
  if time.monotonic()>deadline:raise RuntimeError('Existing canonical job still active after two-hour dependent wait; preserve and inspect, no duplicate')
  time.sleep(30)
 assert len(nm.get('controls',[]))==2 and all(v['archive_identity'] and v['final_Q16_identity'] and v['decoded_raw_exact'] and v['hidden_encode_decode_identity'] for v in nm['controls'])
 assert len(nm.get('native_exports',[]))==4
 m['reused_native_manifest_sha256']=sha(N/'manifest.json');m['reused_native_status']=nm['status'];m['production_stream']=nm['production_stream'];m['controls']=nm['controls'];m['native_exports']=nm['native_exports'];m['native_inference_reused_without_duplicate']=True
 dictionary=R/'native_hidden_trace_v1/tree/dictionary/english.dic';assert sha(dictionary)==nm['dictionary_sha256']
 env={k:v for k,v in os.environ.items() if not k.startswith(('LAB_','HP_LEX_','FX_PREPARE'))}
 for s in 'abcd':
  (D/(s+'512k.bin')).symlink_to(N/(s+'512k.bin'));(D/(s+'_native')).symlink_to(N/(s+'_native'))
 assert shutil.disk_usage(R).free>1_600_000_000
 save('reused canonical native controls PASS; independent error-memory replay')
'''
s=base[:start]+prefix+base[end:]
s=s.replace("D=R/'atom_cache_v1'","D=R/'error_memory_v1'")
s=s.replace("canonical lexical cold-core dictionary-atom memory; registered conditional confirmation","canonical lexical paired-error memory; native exports reused; registered conditional confirmation")
s=s.replace("str(R/'research_round8_atom_cache.cpp')","str(R/'research_round8_error_memory.cpp')")
s=s.replace("['research_round8_atom_cache.cpp','research_round8_atom_cache_protocol.md',pathlib.Path(__file__).name]","['research_round8_error_memory.cpp','research_round8_atom_cache.cpp','research_round8_residual_memory_math.md',pathlib.Path(__file__).name]")
s=s.replace("[str(replay),'selftest',str(dictionary)]","[str(replay),'selftest']")
s=s.replace("('signals','<f4',(9,))","('signals','<f4',(22,))").replace('dtype.itemsize==39','dtype.itemsize==91').replace('*8*39','*8*91')
s=s.replace("sources=['raw_word','permuted_raw_word','centered_word','permuted_centered_word','white_word','permuted_white_word','word_recency','centered_hard_word','permuted_centered_hard_word'];names=['generic']+sources+['joint']","sources=[f'{geom}_{control}_lambda{lam}' for geom in ['raw','centered','white'] for control in ['actual','paired_permutation'] for lam in ['025','1','4']]+['prefix_hashed_control','recency_control','raw_actual_one_Newton','raw_permuted_one_Newton'];names=['generic']+sources+['joint']")
s=s.replace('if arm==10:','if arm==23:').replace('for j in [0,2,4,6,7]','for j in [1,7,13,18,19,20]')
s=s.replace('4bit_selector','5bit_selector').replace('gain-16*len(opt.x)-.5','gain-16*len(opt.x)-.625')
s=s.replace('COMPLETE_CANONICAL_ATOM_CACHE_DIAGNOSTIC','COMPLETE_CANONICAL_ERROR_MEMORY_DIAGNOSTIC').replace('word-aligned features','paired-error features').replace('finite word-aligned branch complete','finite paired-error branch complete')
(project_path('research_round8_error_memory_worker.py', base=R)).write_text(s,encoding='utf-8')
print({'worker_bytes':len(s.encode()),'sources':22,'heads':24,'native_inference':'reuse only'})
