import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
for name in 'abcd':
    p=out/(name+'_word_association_v2_screen.json');log=out/(name+'_word_association_v2.log')
    if p.exists():
        d=json.loads(p.read_text());s=d['score'];print(name,{'saving_bytes':s['prequential_saving_bytes'],'eligible_suffix_bits':s['baseline_suffix_bits'],'fraction_total_bits':s['baseline_suffix_bits']/(d['baseline_ideal_bytes']*8),'wall_seconds':d['wall_seconds'],'occurrence_classes':d['by_occurrence_class'],'best_fixed':sorted(s['fixed_models'],key=lambda x:-x['saving_bytes'])[:3]})
    elif log.exists():print(name,log.read_text()[-700:])
print('JOBS','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'word_association_screen.py' in x))
