from pathlib import Path
import json
import subprocess

W = Path('/kaggle/working')
out = {}
for name in ['hp_round11/preflight_v4/manifest.json', 'hp_round11/private_cpu_assets_manifest.json',
             'hp_round11/private_cpu_submission_v4_manifest.json', 'hp_round11/warm_atlas_v2/manifest.json',
             'hp_round11/weight_codec_v1/manifest.json','hp_round11/constructor_proxy_v1/manifest.json',
             'hp_round11/word_coverage_v1/manifest.json','hp_round11/word_cost_v1/manifest.json']:
    path = W / name
    if path.exists():
        row = json.loads(path.read_text())
        out[name] = {k:row.get(k) for k in ['status','pid','child_pid','stage','error','archive_bytes','independent_decode_exact',
                                           'asset_zip_bytes','asset_zip_sha256','jobs','dataset_action','finished','failed_gate','delivered_assets_all_entry_SHA_verified',
                                           'total_tokens','distinct_types','pages','tokenizer_difference_pages']}
        out[name]['cases_completed']=len(row.get('cases',[]))
        if row.get('status') == 'FAIL':
            out[name]['traceback'] = row.get('traceback')
out['processes'] = subprocess.check_output(['ps','-eo','pid,ppid,etime,time,%cpu,%mem,comm','--sort=-%cpu'],text=True).splitlines()[:9]
print(json.dumps(out))
