"""Relocate preserved checkpoint files; no model/data deletion.

Run only after all11 files are downloaded and their10 trained hashes verified.
"""
import pathlib,json,hashlib,shutil,time
R=pathlib.Path('/kaggle/working/hp_round9');src=R/'core_training_v2';dst=pathlib.Path('/root/hp_round9/preserved_core_training_v2');dst.mkdir(exist_ok=False);m={'started':time.time(),'reason':'working disk has220MB free; longer checkpoints use scratch; all old models downloaded locally before relocation','operation':'verified copy followed by unlink original checkpoint file; model content remains in root scratch and local workspace','deletions_of_model_content':[],'moves':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((src/'manifest.json').read_text());expected={v['arm']+'_step'+str(v['step'])+'.pt':v['checkpoint_sha256'] for v in manifest['rungs']};files=sorted(src.glob('*.pt'));assert len(files)==11
for p in files:
 digest=sha(p)
 if p.name in expected:assert digest==expected[p.name]
 target=dst/p.name;shutil.copy2(p,target);assert sha(target)==digest and target.stat().st_size==p.stat().st_size
 row={'source':str(p),'destination':str(target),'bytes':p.stat().st_size,'sha256':digest,'local_copy_verified_before_rpc':True};p.unlink();m['moves'].append(row)
m.update(status='COMPLETE_VERIFIED_CORE_CHECKPOINT_RELOCATION',free_working_after=shutil.disk_usage(R).free);(R/'core_checkpoint_relocation_manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({'status':m['status'],'moved':len(m['moves']),'free_working_after':m['free_working_after']}))
