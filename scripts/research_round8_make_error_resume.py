
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

# New experiment directory and source: never overwrite an interrupted worker.
old = project_path('research_round8_error_memory_worker.py').read_text()
start = old[:old.index(" m['status']='FITTING_DEVELOPMENT_ONLY'")]
start = start.replace("D=R/'error_memory_v1'", "D=R/'error_memory_resume_v1'")
start = start.replace("'session':355655943", "'session':355735431")
start = start.replace("p=N/'manifest.json';nm=json.loads(p.read_text()) if p.exists() else {}", "p=R/'atom_fit_resume_v1/manifest.json';parent=json.loads(p.read_text()) if p.exists() else {};nm=json.loads((N/'manifest.json').read_text())")
start = start.replace("if nm.get('status','').startswith('COMPLETE') or nm.get('status')=='FAIL':break", "if parent.get('status','').startswith('COMPLETE') or parent.get('status')=='FAIL':break")
start = start.replace(" m['reused_native_manifest_sha256']", " m['parent_fit_status']=parent['status'];m['parent_fit_manifest_sha256']=sha(p)\n m['reused_native_manifest_sha256']")
start = start.replace("records=np.fromfile(out,dtype=dtype);", "records=np.memmap(out,dtype=dtype,mode='r');")
needle = " m['reused_native_manifest_sha256']=sha(N/'manifest.json')"
assert needle in start
start = start.replace(needle, "\n for v in nm['native_exports']:\n  s=v['slice'];assert sha(N/(s+'512k.bin'))==v['input_sha256'] and sha(N/(s+'_native/final_p.u16'))==v['final_p_sha256'] and sha(N/(s+'_native/hidden.q8'))==v['hidden_sha256']\n" + needle)

resume = project_path('research_round8_resume_atom_fit_worker.py').read_text()
helpers = resume[resume.index('def columns('):resume.index('\ntry:')]
helpers = helpers.replace('arm==10', 'arm==23').replace('[0,2,4,6,7]', '[1,7,13,18,19,20]').replace('dim=7 if arm==23', 'dim=8 if arm==23')
prefix = start[:start.index('\ntry:')]
body = start[start.index('\ntry:'):]
finish = '''
 m['status']='FITTING_DEVELOPMENT_ONLY';save('streamed bounded A/B fitting; conditional C/D untouched')
 sources=[f'{geom}_{control}_lambda{lam}' for geom in ['raw','centered','white'] for control in ['actual','paired_permutation'] for lam in ['025','1','4']]+['prefix_hashed_control','recency_control','raw_actual_one_Newton','raw_permuted_one_Newton'];names=['generic']+sources+['joint']
 rng=np.random.default_rng(18547);X=rng.normal(size=(71,8));yy=rng.integers(0,2,size=71);l=rng.normal(size=71);t=rng.uniform(-.4,.4,size=8);z=l+X@t;q=expit(z);g=X.T@(q-yy);H=X.T@((q*(1-q))[:,None]*X);eps=1e-5
 def toy(x):z=l+X@x;return np.sum(np.logaddexp(0,z)-yy*z)
 fd=np.array([(toy(t+np.eye(8)[j]*eps)-toy(t-np.eye(8)[j]*eps))/(2*eps) for j in range(8)]);err=float(np.max(np.abs(fd-g)));mineig=float(np.linalg.eigvalsh(H).min());assert err<1e-7 and mineig>=0;m['independent_math_test']={'gradient_error':err,'Hessian_min_eigenvalue':mineig}
 for arm,name in enumerate(names):
  begin=time.monotonic();t,hist,solver=solve([data['a'],data['b']],arm);_,g,_=summation([data['a'],data['b']],arm,t);cert=gap(t,g);evals=[dict(slice=s,**evaluate(data[s],arm,t)) for s in 'ab'];gain=sum(v['q16_saving_bytes'] for v in evals);row={'name':name,'arm':arm,'coefficients':t.tolist(),'coefficient_bytes_per_copy':8*len(t),'supporting_plane_gap_bytes':cert,'ideal_box_optimum_certified':cert<=.05,'solver':solver,'iteration_history':hist,'fit_evaluate_wall_seconds':time.monotonic()-begin,'evaluations':evals,'development_q16_saving_bytes':gain,'development_after_two_coefficient_copies_and_5bit_selector_bytes':gain-16*len(t)-.625};m['results'].append(row);save('fit '+name);assert cert<=.05
 fixed={name:sum(v[name] for v in m['feature_exports']) for name in ['bayes_global_saving_bytes','bayes_context_saving_bytes']};m['fixed_online_AB']=fixed;m['advance_gate_bytes']=64.;best=max(m['results'],key=lambda v:v['development_after_two_coefficient_copies_and_5bit_selector_bytes']);m['selected_development_head']=best['name'];m['best_priced_AB_bytes']=best['development_after_two_coefficient_copies_and_5bit_selector_bytes'];advance=max(m['best_priced_AB_bytes'],max(fixed.values()))>=64;m['advance_gate_pass']=advance;save('locked A/B advancement gate')
 if advance:
  for s in 'cd':export(s)
  for v in m['results']:v['evaluations'].extend(dict(slice=s,**evaluate(data[s],v['arm'],np.array(v['coefficients']))) for s in 'cd');v['confirmation_q16_saving_bytes']=sum(a['q16_saving_bytes'] for a in v['evaluations'] if a['slice'] in 'cd')
  m['confirmation_candidates_evaluated']=True;m['fixed_online_CD']={name:sum(v[name] for v in m['feature_exports'] if v['slice'] in 'cd') for name in fixed}
 m.update(status='COMPLETE_CANONICAL_ERROR_MEMORY_DIAGNOSTIC',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('finite paired-error branch complete; full warm/native package remains open')
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save('failure preserved; no duplicate restart');raise
'''
project_path('research_round8_resume_error_memory_worker.py').write_text(prefix+'\n'+helpers+body+finish)
project_path('research_round8_resume_error_memory_launch.py').write_text('''import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'error_memory_resume_v1').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_resume_error_memory_worker.py')],stdout=(R/'error_memory_resume_v1_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'error_memory_resume_v1','parent':'atom_fit_resume_v1','preserved_native_exports_reused':True,'spending_usd':0,'deletions':[]}))
''')
