import json, pathlib, subprocess
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'conditional_gate_v1'
if not (D/'manifest.json').exists(): print(json.dumps({'status':'NOT_LAUNCHED'}))
else:
    m=json.loads((D/'manifest.json').read_text());out={k:v for k,v in m.items() if k!='results'}
    out['results']=[{'slice':row['slice'],'arms':[{k:a[k] for k in ['name','saving_bytes','q16_tax_bytes','tree_nodes']} for a in row['arms']],'accounting':row['accounting']} for row in m['results']]
    for log in [R/'conditional_gate_v1_controller.log',*sorted(D.glob('*.log'))[-2:]]:
        out[str(log)]=log.read_text(errors='replace')[-1800:]
    print(json.dumps(out))
