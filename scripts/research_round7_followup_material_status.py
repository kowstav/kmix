import pathlib,subprocess,json
out=pathlib.Path('/kaggle/working/hp_round7')
for name in ['lex_native_2m_recovery_controller.log','causal_latent_v2_controller.log','causal_latent_v3_controller.log','frozen_logits_pilot_controller.log']:
    p=out/name;print(name,p.read_text()[-1600:] if p.exists() else 'MISSING')
for folder in ['lex_native_2m_recovered','causal_latent_words_v2','causal_latent_words_v3','frozen_logits_pilot']:
    p=out/folder;print('JSON',folder,[(f.name,f.stat().st_size) for f in p.glob('*.json')])
print('ACTIVE','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix_round7_' in x or 'causal_latent_word_v2_screen.py' in x or 'causal_latent_v3_screen.py' in x))
