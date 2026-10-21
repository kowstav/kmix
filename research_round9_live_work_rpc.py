import pathlib,json,subprocess,os
R=pathlib.Path('/kaggle/working/hp_round9');out={}
for name in ['core_extension_v1','core_export_v1','core_export_v2','core_native_codec_v3','word_events_v1','word_features_v1','literal_split_v1','known_literals_v1','word_softmax_queue_v1','word_softmax_v1','word_softmax_v2','word_warmstart_v1','title_memory_v1','distributed_core_data_v1','core_distributed_v1','core_distributed_v2','core_pipeline_profile_v1','compact_preservation_v2','compact_download_parts_v2','adaptive_native_v2']:
 p=R/name/'manifest.json'
 if p.exists():
  j=json.loads(p.read_text());out[name]={k:j.get(k) for k in ['status','pid','stage','error','child_pid']};out[name]['rungs']=len(j.get('rungs',[]));out[name]['native_candidates']=len(j.get('native_candidates',j.get('candidates',[])))
print(json.dumps(out));print(subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,memory.used','--format=csv,noheader'],text=True))
if (R/'word_events_v1/manifest.json').exists():
 j=json.loads((R/'word_events_v1/manifest.json').read_text());parent=str(j['pid'])
 for line in subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True).splitlines():
  bits=line.strip().split(None,2)
  if len(bits)==3 and bits[1]==parent and '/word_events' in bits[2]:
   for fd in pathlib.Path('/proc/'+bits[0]+'/fd').iterdir():
    try:
     if os.readlink(fd).endswith('lexical_full_ready.wrt'):print(json.dumps({'word_decoder_pid':int(bits[0]),'fd_info':pathlib.Path('/proc/'+bits[0]+'/fdinfo/'+fd.name).read_text()}))
    except OSError:pass
print(subprocess.check_output(['ps','-eo','pid,ppid,stat,etime,time,%cpu,%mem,args','--sort=-%cpu'],text=True).splitlines()[:9])
