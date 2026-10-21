"""Independent native2M decodes, queued behind the running compression controls."""
import pathlib,subprocess,os,json,time,hashlib,shutil
out=pathlib.Path('/kaggle/working/hp_round7');pre=out/'preserved';dest=out/'lex_native_2m_decode';dest.mkdir(exist_ok=False);work=pathlib.Path('/root/hp/lex_native_2m_decode');work.mkdir(exist_ok=False)
for _ in range(4320):
    log=(out/'lex_native_2m_controller.log').read_text()
    if 'LEX_NATIVE_2M_CONTROLS_COMPLETE' in log:break
    if 'Traceback' in log:raise RuntimeError('Stop: larger compression controls failed; preserve their logs')
    time.sleep(5)
else:raise RuntimeError('Six-hour wait limit reached')
records={r['slice']:r for r in json.loads((out/'lex_native_2m/results.json').read_text())};rows=[]
binary=out/'cmix_round7_lex_codebook';weights=out/'lex_audit/lex_h1_run11.tfwc2'
for pair in ['cd','ab']:
    jobs=[]
    for n in pair:
        run=work/n;run.mkdir();(run/'.dict').symlink_to(pre/'gen/.dict');archive=pathlib.Path('/root/hp/lex_native_2m')/n/'out.cmx'
        shutil.copy2(archive,out/'lex_native_2m'/(n+'_out.cmx'))
        env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(pre/'data/vocab.bm'),'LAB_DICT':str(pre/'gen/.dict'),'LAB_KEEP_TEMP':'1'}
        for k in ['LAB_COST','LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(k,None)
        log=(dest/(n+'.log')).open('w');started=time.monotonic()
        p=subprocess.Popen(['/usr/bin/time','-v','-o',str(dest/(n+'.time')),str(binary),'-d','--transformer',str(weights),str(archive),'decoded.bin'],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT)
        jobs.append((n,p,log,run,started));print('LEX_2M_DECODE_STARTED',n,p.pid,flush=True)
    for n,p,log,run,started in jobs:
        rc=p.wait();log.close();assert rc==0,('larger native decode failed',n)
        decoded=(run/'decoded.bin').read_bytes();digest=hashlib.sha256(decoded).hexdigest();assert len(decoded)==2000000 and digest==records[n]['input_sha256'],('full slice round trip differs',n)
        row={'slice':n,'input_bytes':len(decoded),'byte_exact_sha256':digest,'native_full_slice_roundtrip':True,'native_archive_bytes':records[n]['native_archive_bytes'],'decode_wall_seconds':time.monotonic()-started,'scope':'2M cold slice with correct model and independent process; not full enwik9 or final package'}
        for line in (dest/(n+'.time')).read_text().splitlines():
            if 'Maximum resident set size (kbytes)' in line:row['decode_max_rss_kbytes']=int(line.rsplit(':',1)[1])
            if 'User time (seconds)' in line:row['decode_user_seconds']=float(line.rsplit(':',1)[1])
            if 'System time (seconds)' in line:row['decode_system_seconds']=float(line.rsplit(':',1)[1])
        rows.append(row);(dest/'results.json').write_text(json.dumps(rows,indent=2));print(json.dumps(row),flush=True)
print('LEX_NATIVE_2M_DECODES_COMPLETE',flush=True)
