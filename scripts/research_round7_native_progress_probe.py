import pathlib,subprocess,json
root=pathlib.Path('/root/hp/lex_native_2m_recovered');out=pathlib.Path('/kaggle/working/hp_round7')
print(subprocess.check_output(['ps','-p','212,213,207,225','-o','pid,etime,time,pcpu,stat,args'],text=True))
for n in 'ab':
    p=root/(n+'_decode')
    if not p.exists():p=root/(n+'decode')
    print(n,[(str(x),x.stat().st_size) for x in root.glob('**/decoded.bin') if n in str(x.parent.name)])
for name in ['cpu.max','cpu.stat']:
    p=pathlib.Path('/sys/fs/cgroup')/name
    print(name,p.read_text() if p.exists() else 'UNAVAILABLE')
print('recovery_tail',(out/'lex_native_2m_recovery_controller.log').read_text()[-2200:])
print('pilot_tail',(out/'frozen_logits_pilot_controller.log').read_text()[-2200:])
