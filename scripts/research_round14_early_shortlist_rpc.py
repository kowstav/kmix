from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
R=Path('/root/r14_batch_outputs');W=Path('/kaggle/working/hp_round14');out={}
for slug,kind in [('hutter-r14-group-weight-storage-v1','group-storage'),('hutter-r14-native-confirmation-b-v1','native-confirmation')]:
    p=R/slug/kind/'manifest.json'
    if p.exists():
        m=json.loads(p.read_text());out[kind]={k:v for k,v in m.items() if k!='groups'}
        if 'groups' in m:out[kind]['groups_tested']=len(m['groups'])
def pull(role):
    ref='chaoscpp/hutter-r14-constructor-'+role+'-v1';target=Path('/root/r14_manifest_reads')/role;target.mkdir(parents=True,exist_ok=True)
    p=subprocess.run(['kaggle','kernels','output',ref,'-p',str(target),'--file-pattern',r'(^|/)manifest\.json$'],capture_output=True,text=True,timeout=35)
    paths=list(target.rglob('manifest.json'));assert p.returncode==0 and len(paths)==1
    return {'role':role,'path':str(paths[0])}
with ThreadPoolExecutor(max_workers=2) as pool:out['constructor_manifest_paths']=list(pool.map(pull,['development','confirmation']))
(W/'early_results_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
