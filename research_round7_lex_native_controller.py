import pathlib,subprocess,os,time,json,hashlib
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved';dest=out/'lex_native';dest.mkdir(exist_ok=False);work=pathlib.Path('/root/hp/lex_native');work.mkdir(exist_ok=False)
subprocess.run(['python','-u',str(out/'research_round7_lex_roundtrip_prepare.py')],check=True)
binary=out/'cmix_round7_lex_roundtrip';weights=out/'lex_audit/lex_h1_run11.tfwc2';rows=[]
for pair in ['ab','cd']:
    jobs=[]
    for n in pair:
        src=pre/'slices'/f'{n}2m.bin' if n in 'ab' else out/f'{n}2m.bin';raw=src.read_bytes()[:32768]
        inp=work/(n+'_input.bin');inp.write_bytes(raw);run=work/(n+'_compress');run.mkdir();(run/'.dict').symlink_to(pre/'gen/.dict')
        env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(pre/'data/vocab.bm'),'LAB_DICT':str(pre/'gen/.dict'),'LAB_KEEP_TEMP':'1','LAB_COST':str(run/'cost.f32')}
        for key in ['LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(key,None)
        log=(dest/(n+'_compress.log')).open('w');started=time.monotonic()
        cmd=['/usr/bin/time','-v','-o',str(dest/(n+'_compress.time')),str(binary),'-n','--transformer',str(weights),str(inp),'out.cmx']
        p=subprocess.Popen(cmd,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT);jobs.append((n,p,log,run,env,started,raw));print('LEX_NATIVE_STARTED',n,p.pid,flush=True)
    for n,p,log,run,env,started,raw in jobs:
        rc=p.wait();log.close();assert rc==0,('native compress failed',n)
        cost=np.fromfile(run/'cost.f32','<f4');assert len(cost)==len(raw)
        row={'slice':n,'input_bytes':len(raw),'native_archive_bytes':(run/'out.cmx').stat().st_size,'ideal_bytes':float(cost.astype(np.float64).sum()/8.),'input_sha256':hashlib.sha256(raw).hexdigest(),'compress_wall_seconds':time.monotonic()-started,'weights_bytes':weights.stat().st_size,'native_probabilities':True,'scope':'cold native32K matched lexical baseline; not original record PGO/full-file result'}
        # Decompression follows compression for the pair; never exceeds two cmix jobs.
        row['_run']=str(run);row['_env']=env;row['_raw']=raw;rows.append(row)
    decjobs=[]
    for row in rows[-2:]:
        n=row['slice'];run=work/(n+'_decode');run.mkdir();(run/'.dict').symlink_to(pre/'gen/.dict');env=row['_env'].copy();env.pop('LAB_COST',None)
        log=(dest/(n+'_decode.log')).open('w');started=time.monotonic()
        p=subprocess.Popen(['/usr/bin/time','-v','-o',str(dest/(n+'_decode.time')),str(binary),'-d','--transformer',str(weights),str(pathlib.Path(row['_run'])/'out.cmx'),'decoded.bin'],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
        decjobs.append((row,p,log,run,started));print('LEX_DECODE_STARTED',n,p.pid,flush=True)
    for row,p,log,run,started in decjobs:
        rc=p.wait();log.close();assert rc==0,('native decode failed',row['slice']);decoded=(run/'decoded.bin').read_bytes();assert decoded==row['_raw'],('round trip differs',row['slice'])
        row.update({'decoded_sha256':hashlib.sha256(decoded).hexdigest(),'roundtrip_byte_exact':True,'decode_wall_seconds':time.monotonic()-started})
        for key in ['_run','_env','_raw']:row.pop(key)
        for mode in ['compress','decode']:
            text=(dest/(row['slice']+'_'+mode+'.time')).read_text()
            for line in text.splitlines():
                if 'Maximum resident set size (kbytes)' in line:row[mode+'_max_rss_kbytes']=int(line.rsplit(':',1)[1])
                if 'User time (seconds)' in line:row[mode+'_user_seconds']=float(line.rsplit(':',1)[1])
                if 'System time (seconds)' in line:row[mode+'_system_seconds']=float(line.rsplit(':',1)[1])
        (dest/'results.json').write_text(json.dumps([r for r in rows if '_raw' not in r],indent=2));print(json.dumps(row),flush=True)
print('LEX_NATIVE_ROUNDTRIPS_COMPLETE',flush=True)
