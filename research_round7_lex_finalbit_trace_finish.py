"""Repair missing timing utility and explicit -d; reuse the completed trace build.

V1 failure and log remain unchanged. New V2 runs use Linux wait4 per-process
CPU/RSS. No recompilation, relaxed parity threshold or model substitution.
"""
import datetime,hashlib,json,os,pathlib,signal,subprocess,time,traceback
import numpy as np
import research_round7_lex_finalbit_trace_worker as W

OUT=W.OUT;DEST=OUT/'lex_finalbit_trace_v2';N=32768


def timed(cmd,cwd,env,label):
    begun=time.monotonic()
    with (DEST/(label+'.log')).open('x') as log:
        p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while True:
            pid,status,usage=os.wait4(p.pid,os.WNOHANG)
            if pid:break
            if time.monotonic()-begun>500:
                os.killpg(p.pid,signal.SIGTERM);pid,status,usage=os.wait4(p.pid,0)
                raise RuntimeError('Native32K control timeout; partial files preserved')
            time.sleep(1)
        p.returncode=os.waitstatus_to_exitcode(status)
        row={'wall_seconds':time.monotonic()-begun,'user_seconds':usage.ru_utime,
             'system_seconds':usage.ru_stime,'max_rss_kbytes':usage.ru_maxrss,
             'measurement':'Linux wait4, individual child, sequential controls',
             'returncode':p.returncode}
        (DEST/(label+'.time.json')).write_text(json.dumps(row,indent=2))
        if p.returncode:raise RuntimeError(('Native control failed',label,p.returncode))
        return row


def main():
    assert not DEST.exists(),'Preserve V2; no duplicate'
    assert not any('research_round7_lex_finalbit_trace_worker.py' in s for s in subprocess.check_output(['ps','-eo','args'],text=True).splitlines()),'V1 still active'
    v1=json.loads((W.DEST/'results.json').read_text())
    assert v1['status']=='FAIL' and "No such file or directory: '/usr/bin/time'" in v1['error'],'Repair only documented timer failure'
    binary=W.DEST/'cmix_trace';baseline=OUT/'cmix_round7_lex_codebook';weights=OUT/'lex_audit/lex_h1_run11.tfwc2'
    assert W.sha(binary)==v1['binary_sha256']=='d906d0f2e98c1f5d0d3c1f3ca893b2190750b4bd708b9e001382c7330381c76e'
    assert W.sha(baseline)==W.BASE_BINARY_SHA and W.sha(weights)==W.WEIGHT_SHA
    DEST.mkdir()
    result={'status':'RUNNING','utc_started':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'v1_failure_preserved':True,'repair':'Linux wait4 replaces missing /usr/bin/time; explicit -d before decode',
            'reused_build':v1,'controls':[],'neural_training':False,'paid_rental_usd':0,'deletions':[]}
    def save(stage):
        result['stage']=stage;(DEST/'results.json').write_text(json.dumps(result,indent=2))
        print(json.dumps({'stage':stage,'status':result['status']}),flush=True)
    save('matched32K controls using existing compiled binary')
    try:
        base_env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')}
        base_env.update(LAB_RAW='1',LAB_VOCAB=str(OUT/'preserved/data/vocab.bm'),LAB_DICT=str(OUT/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
        for n in 'ab':
            raw=(OUT/'preserved/slices'/(n+'2m.bin')).read_bytes()[:N];inp=DEST/(n+'32k.bin');inp.write_bytes(raw);runs={}
            for mode,program in [('reference',baseline),('trace',binary)]:
                d=DEST/(n+'_'+mode);d.mkdir();(d/'.dict').symlink_to(OUT/'preserved/gen/.dict')
                env={**base_env,'LAB_COST':str(d/'cost.f32')}
                if mode=='trace':env['LAB_BITTRACE']=str(d/'final_p.u16')
                runs[mode]=timed([str(program),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,env,n+'_'+mode)
            a,b=DEST/(n+'_reference'),DEST/(n+'_trace')
            assert (a/'out.cmx').read_bytes()==(b/'out.cmx').read_bytes(),('Archive identity',n)
            ref,got=np.fromfile(a/'cost.f32','<f4'),np.fromfile(b/'cost.f32','<f4')
            old=np.fromfile(OUT/'lex_native_2m'/(n+'_cost.f32'),'<f4')[:N]
            assert len(ref)==len(got)==N and np.array_equal(ref,got) and np.array_equal(ref,old),('Cost identity',n)
            p=np.fromfile(b/'final_p.u16','<u2');assert len(p)==8*N and np.all((p>=1)&(p<=65535)),('Trace size/range',n)
            actual=np.unpackbits(np.frombuffer(raw,np.uint8),bitorder='big')
            reconstructed=(-np.log2(np.where(actual,p.astype(np.float64),65536.-p.astype(np.float64))/65536.)).reshape(-1,8).sum(axis=1)
            err=float(np.max(np.abs(reconstructed-ref)));assert err<=1e-4,('Trace cost reconstruction',n,err)
            d=DEST/(n+'_decode');d.mkdir();(d/'.dict').symlink_to(OUT/'preserved/gen/.dict')
            runs['decode']=timed([str(binary),'-d','--transformer',str(weights),str(b/'out.cmx'),'decoded.bin'],d,base_env,n+'_decode')
            assert (d/'decoded.bin').read_bytes()==raw,('Independent decode',n)
            result['controls'].append({'slice':n,'input_bytes':N,'input_sha256':W.sha(inp),
                'archive_bytes':(b/'out.cmx').stat().st_size,'archive_sha256':W.sha(b/'out.cmx'),
                'bit_trace_sha256':W.sha(b/'final_p.u16'),'bit_count':len(p),
                'max_bit_reconstruction_vs_float32_byte_cost_diff':err,
                'archive_bit_exact_reference':True,'costs_bit_exact_older2M_prefix':True,
                'independent_raw_decode_exact':True,'runtime':runs})
            save('matched32K '+n+' PASS')
        result['status']='PASS';save('all identity trace and decode gates PASS; residual screen pending')
        print('LEX_FINALBIT_TRACE_V2_COMPLETE',flush=True)
    except Exception:
        result['status'],result['error']='FAIL',traceback.format_exc();save('failed; all evidence preserved');raise


if __name__=='__main__':main()
