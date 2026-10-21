from pathlib import Path
import py_compile
R=Path(__file__).resolve().parent
s=(R/'research_round8_continuous_worker.py').read_text(encoding='utf-8')
old="records['signals'][:,5].astype(np.float64));z=ell+features@best.x"
new="records['signals'][:,5].astype(np.float64)));z=ell+features@best.x"
assert s.count(old)==1
s=s.replace(old,new).replace("'continuous_strength_v1'","'continuous_strength_v2'")
(R/'research_round8_continuous_v2_worker.py').write_text(s,encoding='utf-8')
l=(R/'research_round8_continuous_launch.py').read_text(encoding='utf-8').replace('continuous_strength_v1','continuous_strength_v2').replace('research_round8_continuous_worker.py','research_round8_continuous_v2_worker.py')
(R/'research_round8_continuous_v2_launch.py').write_text(l,encoding='utf-8')
py_compile.compile(str(R/'research_round8_continuous_v2_worker.py'),doraise=True)
py_compile.compile(str(R/'research_round8_continuous_v2_launch.py'),doraise=True)
print('PASS: repaired worker and launcher parse; v1 source and failure evidence retained')
