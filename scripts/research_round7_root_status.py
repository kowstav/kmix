import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
for n in 'abcd':
    p=out/(n+'_word_association_root_v1_screen.json');log=out/(n+'_word_association_root_v1.log')
    if p.exists():
        d=json.loads(p.read_text());s=d['score'];print(n,{'saving_bytes':s['prequential_saving_bytes'],'covered_bits':s['baseline_suffix_bits'],'fraction_total_bits':s['baseline_suffix_bits']/(d['baseline_ideal_bytes']*8),'classes':d['by_occurrence_class'],'best_fixed':sorted(s['fixed_models'],key=lambda x:-x['saving_bytes'])[:4],'wall_seconds':d['wall_seconds']})
    elif log.exists():print(n,log.read_text()[-650:])
print('CONTROLLER',(out/'word_root_controller.log').read_text()[-500:])
print('JOBS','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'word_association_root_screen.py' in x))
