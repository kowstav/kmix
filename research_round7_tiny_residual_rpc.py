import datetime,hashlib,json,os,pathlib,subprocess,time
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'tiny_residual_v1';assert not d.exists();d.mkdir();b=d/'train_replay';links=d/'inputs';links.mkdir()
m={'status':'RUNNING','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preregistered':'A/B fitting, ridge64/4096, +/-0.25logit bound,128biases, exact integer odds; C/D frozen','deletions':[],'paid_rental_usd':0}
(d/'manifest.json').write_text(json.dumps(m,indent=2));subprocess.run(['g++','-O3','-std=c++17',str(r/'research_round7_tiny_residual.cpp'),'-o',str(b)],check=True)
for n in 'abcd':
 raw=r/'preserved/slices'/(n+'2m.bin') if n in 'ab' else r/(n+'2m.bin');(links/(n+'2m.bin')).symlink_to(raw);(links/(n+'_p.u16')).symlink_to(r/'lex_finalbit_2m_v1'/n/'final_p.u16')
log=(d/'fit.log').open('x');p=subprocess.Popen([str(b),str(links/'a2m.bin'),str(links/'a_p.u16'),str(links/'b2m.bin'),str(links/'b_p.u16'),str(links),str(d)],stdout=log,stderr=subprocess.STDOUT)
_,status,u=os.wait4(p.pid,0);log.close();assert os.waitstatus_to_exitcode(status)==0
m.update(status='COMPLETE',user_seconds=u.ru_utime,max_rss_kbytes=u.ru_maxrss,binary_bytes=b.stat().st_size,binary_sha256=hashlib.sha256(b.read_bytes()).hexdigest());(d/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({'manifest':m,'results':json.loads((d/'results.json').read_text())}))
