from pathlib import Path
import json,subprocess,time
W=Path('/kaggle/working/hp_round14');out={'time':time.time(),'live':{},'confirmation':[]}
for name in ('guard_storage_parity_v2/manifest.json','guard_match_pipeline_v1.json','guard_match_scope_gate_release_v2.json'):
    p=W/name
    if p.exists():
        m=json.loads(p.read_text());out['live'][name]={k:v for k,v in m.items() if k not in ('cases','traceback','command')};out['live'][name]['cases']=len(m.get('cases',[]))
for arm in ('prune-word','prune-match','prune-indirect','output-fp32'):
    ref='chaoscpp/hutter-r14-'+arm+'-confirm-a-v1';p=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=20)
    state=next((s for s in ('COMPLETE','ERROR','RUNNING','QUEUED') if 'KernelWorkerStatus.'+s in p.stdout),'UNKNOWN');out['confirmation'].append({'ref':ref,'status':state,'exit':p.returncode})
(W/'handoff_status_v1.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
