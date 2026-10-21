
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
r=project_root(__file__)
s=(project_path('research_round8_hidden_cache_executed_worker.py', base=r)).read_text(encoding='utf-8')
s=s.replace("D=R/'hidden_cache_v2'", "D=R/'metric_cache_v1'").replace('research_round8_hidden_cache_replay_v3.cpp','research_round8_metric_cache.cpp').replace('research_round8_hidden_cache_protocol.md','research_round8_metric_cache_protocol.md')
s=s.replace("'research_round8_hidden_cache_math.md',", '')
s=s.replace("('signals','<f4',(9,))", "('signals','<f4',(17,))").replace('dtype.itemsize==39','dtype.itemsize==71').replace('4096*8*39','4096*8*71')
names=['raw_soft','raw_sharp_k1','raw_sharp_k8','raw_tau100','centered_k1','centered_k8','whitened_k1','whitened_k8','shuffled_raw_k1','shuffled_centered_k1','shuffled_whitened_k1','hard_centered_k1','hard_centered_k8','shuffled_hard_centered_k1','hard_whitened_k1','hard_whitened_k8','shuffled_hard_whitened_k1']
start=s.index(' names=[');end=s.index('\n rng=',start);s=s[:start]+' names='+repr(['generic']+[n+'_signed' for n in names]+[n+'_positive' for n in names]+['joint_signed','joint_positive'])+s[end:]
start=s.index('  if arm==8:');end=s.index('\n  return np.column_stack(cols)',start)
s=s[:start]+'''  if arm in [35,36]:cols.extend(records['signals'][:,j].astype(np.float64) for j in [1,4,6,11,14])
  elif 1<=arm<=17:cols.append(records['signals'][:,arm-1].astype(np.float64))
  elif 18<=arm<=34:cols.append(records['signals'][:,arm-18].astype(np.float64))'''+s[end:]
s=s.replace("bounds=[(-1,1)]*X.shape[1]", "bounds=bounds")
s=s.replace('  best=minimize(', "  bounds=[(-1,1)]*X.shape[1]\n  if 18<=arm<=34 or arm==36:bounds[2:]=[(0,1)]*(X.shape[1]-2)\n  best=minimize(")
s=s.replace('vertex=np.where(grad>=0,-1.,1.)', 'vertex=np.array([lo if g>=0 else hi for g,(lo,hi) in zip(grad,bounds)])')
s=s.replace('development_after_two_coefficient_copies_and_3bit_selector_bytes', 'development_after_two_coefficient_copies_and_6bit_selector_bytes').replace('-0.5', '-0.75').replace('-.5', '-.75')
s=s.replace("m.update(status='COMPLETE_NATIVE_HIDDEN_CACHE_DIAGNOSTIC'", "bestrow=max(m['results'],key=lambda v:v['development_after_two_coefficient_copies_and_6bit_selector_bytes']);m['AB_selected_name']=bestrow['name'];m['AB_selected_after_parameters_and_selector_bytes']=bestrow['development_after_two_coefficient_copies_and_6bit_selector_bytes'];m['fresh_advance_gate_passed']=bool(m['AB_selected_after_parameters_and_selector_bytes']>=64);m['fresh_GH_evaluated']=False\n m.update(status='COMPLETE_METRIC_CACHE_DIAGNOSTIC'")
(project_path('research_round8_metric_cache_worker.py', base=r)).write_text(s,encoding='utf-8');print('Generated 37 frozen heads and A/B-only priced advancement gate')
