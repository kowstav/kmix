import pathlib,json,subprocess
out=pathlib.Path('/kaggle/working/hp_round7');hp=pathlib.Path('/root/hp')
print('CODEC',(out/'v5_codec.log').read_text()[-1800:])
if (out/'v5_codec_results.json').exists():
    print('RESULTS',[{k:v for k,v in r.items() if k!='q4_encodings'} for r in json.loads((out/'v5_codec_results.json').read_text())])
print('ROOT_SCRIPTS',[(p.name,p.stat().st_size) for p in hp.glob('*') if p.is_file()])
print('SX',(out/'sx_topology_controls.json').read_text())
print('PROCESSES','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix ' in x or 'v5_worker' in x))
