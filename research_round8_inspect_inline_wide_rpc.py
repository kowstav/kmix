import json,pathlib,shutil
R=pathlib.Path('/kaggle/working/hp_round8');D=R/'native_inline_wide_v1'
print(json.dumps({'manifest':json.loads((D/'manifest.json').read_text()) if (D/'manifest.json').exists() else None,'working_disk_free_bytes':shutil.disk_usage(R).free,'controller_tail':(R/'native_inline_wide_v1_controller.log').read_text()[-3500:] if (R/'native_inline_wide_v1_controller.log').exists() else None}))
