import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'calibration_native_v4';p=d/'manifest.json';q=d/'results.json'
out={'manifest':json.loads(p.read_text()) if p.is_file() else None,'results':json.loads(q.read_text()) if q.is_file() else [],'tail':(r/'calibration_native_v4_controller.log').read_text()[-1500:]}
out['logs']={p.name:p.read_text()[-350:] for p in sorted(d.glob('*.log'))}
out['active']=[x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if any(s in x for s in ['calibration_native_v4','cmix_calibrated','cmix_reference'])]
print(json.dumps(out,indent=2))
