import pathlib,json,subprocess
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'lexical_full_prepare_v1';m=json.loads((D/'manifest.json').read_text())
o={k:m.get(k) for k in ['status','stage','pid','error','prepared','side','full_inverse_exact','results']};o['controller_tail']=(R/'lexical_full_prepare_v1_controller.log').read_text(errors='replace')[-700:];o['build_tail']=(D/'build.log').read_text(errors='replace')[-500:] if (D/'build.log').exists() else None;o['prepare_tail']=(D/'prepare.log').read_text(errors='replace')[-500:] if (D/'prepare.log').exists() else None;print(json.dumps(o))
