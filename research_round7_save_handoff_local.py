import hashlib,json,pathlib
r=pathlib.Path('.');names=['research_round7_checkpoint.md','research_round7_pre_experiment_report.md','research_round7_report.md','research_round7_remaining_experiments_report.md','research_round7_finetuning_execution_plan.md','research_round7_training_contract.json','research_round7_final_batch_summary.json','research_round7_native_calibration_local_validation.json']
data={'session':355529591,'status':'COMPLETED_BOUNDED_BATCH','files':[]}
for name in names:
 b=(r/name).read_bytes();data['files'].append({'path':name,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'text':b.decode('utf8')})
(r/'research_round7_handoff_20261005.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
print(json.dumps({'files':len(names),'bytes':(r/'research_round7_handoff_20261005.json').stat().st_size}))
