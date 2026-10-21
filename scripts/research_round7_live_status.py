import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
print(subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).split('COMMAND')[-1] if False else '\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix' in x or 'controller' in x or 'confirmation_screens_worker' in x))
for name in ['sx_topology_controls.json','sx_topology_controls.log','sx_controller.log','corrected_confirmation_screens.log']:
    p=out/name
    if p.exists():print(name,p.read_text()[-6000:])
for p in sorted(out.glob('*_corrected_*_screen.json')):
    d=json.loads(p.read_text());print(p.name,{k:round(v['prequential_saving_bytes'],6) for k,v in d['scores'].items()})
for p in sorted(out.glob('[cd]_line_*.json')):
    d=json.loads(p.read_text());print(p.name,{k:v for k,v in d['score'].items() if k in ['prequential_saving_bytes','oracle_best_per_event_saving_bytes_UNPAID','events']})
print('DISK',subprocess.check_output(['df','-h','/kaggle/working'],text=True))
