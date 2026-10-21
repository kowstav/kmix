import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
for n in 'abcd':
    p=out/(n+'_word_newmention_v1_screen.json');log=out/(n+'_word_newmention_v1.log')
    if p.exists():
        d=json.loads(p.read_text());s=d['score'];print('NEWMENTION',n,{'saving_bytes':s['prequential_saving_bytes'],'classes':d['by_occurrence_class'],'wall_seconds':d['wall_seconds'],'best_fixed':sorted(s['fixed_models'],key=lambda x:-x['saving_bytes'])[:3]})
    elif log.exists():print('NEWMENTION_PROGRESS',n,log.read_text()[-400:])
for name in ['ptq_codec.log','ptq_native_controller.log']:
    p=out/name
    if p.exists():print(name,p.read_text()[-2000:])
for name in ['codec_results.json','native_results.json']:
    p=out/'ptq_round7'/name
    if p.exists():print(name,[{k:v for k,v in r.items() if k!='tensors_changed'} for r in json.loads(p.read_text())])
print('JOBS','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix_round7_v5 ' in x or 'word_newmention_screen.py' in x or 'ptq_codec_worker.py' in x))
