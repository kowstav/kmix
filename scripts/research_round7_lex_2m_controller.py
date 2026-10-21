"""Larger true native lexical controls: four2M slices, at most two cmix jobs."""
import pathlib,subprocess,os,json,time,hashlib
import numpy as np
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved';dest=out/'lex_native_2m';dest.mkdir(exist_ok=False);work=pathlib.Path('/root/hp/lex_native_2m');work.mkdir(exist_ok=False)
small=json.loads((out/'lex_native_v3/results.json').read_text());assert len(small)==4 and all(r['roundtrip_byte_exact'] for r in small)
binary=out/'cmix_round7_lex_codebook';weights=out/'lex_audit/lex_h1_run11.tfwc2';rows=[]
for pair in ['cd','ab']:
    jobs=[]
    for n in pair:
        inp=pre/'slices'/f'{n}2m.bin' if n in 'ab' else out/f'{n}2m.bin'
        run=work/n;run.mkdir();(run/'.dict').symlink_to(pre/'gen/.dict')
        env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(pre/'data/vocab.bm'),'LAB_DICT':str(pre/'gen/.dict'),'LAB_KEEP_TEMP':'1','LAB_COST':str(run/'cost.f32')}
        for k in ['LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(k,None)
        started=time.monotonic();log=(dest/(n+'.log')).open('w')
        p=subprocess.Popen(['/usr/bin/time','-v','-o',str(dest/(n+'.time')),str(binary),'-n','--transformer',str(weights),str(inp),'out.cmx'],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
        jobs.append((n,p,log,run,inp,started));print('LEX_NATIVE_2M_STARTED',n,p.pid,flush=True)
    for n,p,log,run,inp,started in jobs:
        rc=p.wait();log.close();assert rc==0,('larger lexical compression failed',n)
        cost=np.fromfile(run/'cost.f32','<f4');assert len(cost)==2000000
        # Prefix parity tests catch configuration/reset drift in the larger run.
        prior=pathlib.Path('/root/hp/lex_native_v3')/(n+'_compress')/'cost.f32'
        assert np.array_equal(cost[:32768],np.fromfile(prior,'<f4')),('32K prefix parity differs',n)
        (dest/(n+'_cost.f32')).write_bytes((run/'cost.f32').read_bytes())
        row={'slice':n,'input_bytes':len(cost),'native_archive_bytes':(run/'out.cmx').stat().st_size,'ideal_bytes':float(cost.astype(np.float64).sum()/8),'cold_classical_and_neural_start':True,'same_32k_prefix_costs_exact':True,'native_neural_inference':True,'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'wall_seconds':time.monotonic()-started,'weights_bytes':weights.stat().st_size,'scope':'Original FX2-ordered WRT slices with actual lexth11c checkpoint/config; cannot equate to lexth11c full ordered stream, package or judge run','full_slice_roundtrip':'not yet; only32K prefixes independently decoded'}
        for line in (dest/(n+'.time')).read_text().splitlines():
            if 'Maximum resident set size (kbytes)' in line:row['max_rss_kbytes']=int(line.rsplit(':',1)[1])
            if 'User time (seconds)' in line:row['user_seconds']=float(line.rsplit(':',1)[1])
            if 'System time (seconds)' in line:row['system_seconds']=float(line.rsplit(':',1)[1])
        rows.append(row);(dest/'results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
print('LEX_NATIVE_2M_CONTROLS_COMPLETE',flush=True)
