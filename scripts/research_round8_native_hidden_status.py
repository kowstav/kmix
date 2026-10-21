import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_hidden_trace_v1';p=D/'manifest.json';m=json.loads(p.read_text()) if p.exists() else {}
out={k:m.get(k) for k in ['status','stage','pid','started','compiler','error','exports','controls']}
out['controller_tail']=(R/'native_hidden_trace_v1_controller.log').read_text(errors='replace')[-1700:]
out['build_tail']=(D/'build.log').read_text(errors='replace')[-600:] if (D/'build.log').exists() else None
out['active']=[s for s in subprocess.run(['ps','-eo','pid,etime,args'],capture_output=True,text=True).stdout.splitlines() if ('native_hidden' in s or 'apt-get' in s or 'clang-17' in s) and 'jupyter' not in s]
print(json.dumps(out))
