import pathlib,tarfile,json,shutil,subprocess
out=pathlib.Path('/kaggle/working/hp_round7');rows=[]
with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
    for m in tar:
        if m.isfile() and (any(x in m.name for x in ['pysrc/','checkpoint','train_lex','lab/exp','tools/']) or m.name.endswith(('.pt','.pth','.tch','.ckpt'))):
            rows.append({'name':m.name,'bytes':m.size})
(out/'training_asset_inventory.json').write_text(json.dumps(rows,indent=2))
print('CHECKPOINTS',[r for r in rows if r['name'].endswith(('.pt','.pth','.tch','.ckpt'))])
print('TRAINING_SOURCES',[r for r in rows if any(x in r['name'] for x in ['train','model.py','export_weights','dataset'])][:50])
print('NATIVE_STATUS',(out/'lex_native_v3_controller.log').read_text()[-1600:])
print('GPU',subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.used,utilization.gpu','--format=csv,noheader'],text=True))
