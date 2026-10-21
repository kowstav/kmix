
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
s=project_path('research_round8_canonical_cost_atlas_v2.py').read_text().replace("D=R/'canonical_cost_atlas_v2'","D=R/'canonical_cost_atlas_v3'")
s=s.replace('post=.5;ideal_mix_bits', 'log_odds=0.;ideal_mix_bits')
s=s.replace("base=float(p[i,b])/65536.;pred=post*base+(1-post)*q;", "base=float(p[i,b])/65536.;e=math.exp(-abs(log_odds));post=1/(1+e) if log_odds>=0 else e/(1+e);pred=post*base+(1-post)*q;")
s=s.replace('post=post*lik_base/lik_mix;c[target]+=1', 'log_odds+=math.log(lik_base)-math.log(lik_kt);c[target]+=1')
s=s.replace('total=float(cost.sum());assert', 'total=float(cost.sum());closed_form_mixture_bits=float((-np.logaddexp(-total*math.log(2),-kt_bits*math.log(2))+math.log(2))/math.log(2));assert abs(ideal_mix_bits-closed_form_mixture_bits)<1e-5;assert')
s=s.replace("'not_recoverable_savings_bound':True", "'log_posterior_odds_used':True,'independent_batch_mixture_bits_error':ideal_mix_bits-closed_form_mixture_bits,'not_recoverable_savings_bound':True")
assert 'post=post*' not in s
project_path('research_round8_canonical_cost_atlas_v3.py').write_text(s)
project_path('research_round8_canonical_cost_atlas_v3_launch.py').write_text('''import pathlib,subprocess,json
R=pathlib.Path('/kaggle/working/hp_round8');assert not (R/'canonical_cost_atlas_v3').exists()
p=subprocess.Popen(['python','-u',str(R/'research_round8_canonical_cost_atlas_v3.py')],stdout=(R/'canonical_cost_atlas_v3_controller.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'pid':p.pid,'experiment':'canonical_cost_atlas_v3','reason':'numerical posterior saturation repair; same predeclared probability law, independent batch-normalizer identity test added','spending_usd':0,'deletions':[]}))
''')
