"""I05: collect actual lex FINAL integer probabilities on matched2M slices.

Wait for both new32K identity/decode gates. At most two native processes;
reuse old native archives and costs as exact controls, not recompress them.
All outputs persist, including failures. No neural retraining or residual yet.
"""
import datetime,json,os,pathlib,subprocess,time,traceback
import numpy as np
import research_round7_lex_finalbit_trace_worker as W
from research_round7_directed_lag_screen import INPUT_SHA256,COST_SHA256

OUT=W.OUT;DEST=OUT/'lex_finalbit_2m_v1'


def main():
    assert not DEST.exists(),'Preserve results; no duplicate trace collection'
    gate=OUT/'lex_finalbit_trace_v2/results.json'
    assert gate.is_file(),'32K identity gate must have started'
    DEST.mkdir();rows=[]
    meta={'status':'WAITING_FOR32K_GATES','utc_started':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'maximum_native_processes':2,'neural_training':False,'paid_rental_usd':0,'deletions':[],
          'scope':'Original FX2-ordered WRT slices with actual lexth11c model/config; final integer probability traces, not qualifying archive or published ordered full stream'}
    def save():
        (DEST/'manifest.json').write_text(json.dumps(meta,indent=2))
        (DEST/'results.json').write_text(json.dumps(rows,indent=2))
    save()
    try:
        begun=time.monotonic()
        while True:
            g=json.loads(gate.read_text())
            if g['status']=='PASS':break
            if g['status']=='FAIL':raise RuntimeError('32K fidelity gate failed; no2M launch')
            if time.monotonic()-begun>1200:raise RuntimeError('32K gate wait expired; no2M launch')
            time.sleep(30)
        assert len(g['controls'])==2 and all(r['archive_bit_exact_reference'] and r['costs_bit_exact_older2M_prefix'] and r['independent_raw_decode_exact'] for r in g['controls'])
        binary=OUT/'lex_finalbit_trace_v1/cmix_trace';weights=OUT/'lex_audit/lex_h1_run11.tfwc2'
        assert W.sha(binary)=='d906d0f2e98c1f5d0d3c1f3ca893b2190750b4bd708b9e001382c7330381c76e' and W.sha(weights)==W.WEIGHT_SHA
        inputs={n:OUT/'preserved/slices'/(n+'2m.bin') if n in 'ab' else OUT/(n+'2m.bin') for n in 'abcd'}
        costs={n:OUT/'lex_native_2m'/(n+'_cost.f32') for n in 'abcd'}
        archives={n:OUT/('lex_native_2m_recovered' if n in 'ab' else 'lex_native_2m')/(n+'_out.cmx') for n in 'abcd'}
        for n in 'abcd':
            assert inputs[n].stat().st_size==2000000 and W.sha(inputs[n])==INPUT_SHA256[n],('Input drift',n)
            assert costs[n].stat().st_size==8000000 and W.sha(costs[n])==COST_SHA256[n],('Cost drift',n)
            assert archives[n].is_file(),('Preserved native archive missing',n)
        meta.update(status='RUNNING',binary_sha256=W.sha(binary),weights_sha256=W.sha(weights),
                    identity_gate=g['controls'],archive_control_sha256={n:W.sha(p) for n,p in archives.items()})
        save()
        base_env={k:v for k,v in os.environ.items() if not k.startswith('LAB_')}
        base_env.update(LAB_RAW='1',LAB_VOCAB=str(OUT/'preserved/data/vocab.bm'),LAB_DICT=str(OUT/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
        for pair in ['cd','ab']:
            jobs={}
            for n in pair:
                d=DEST/n;d.mkdir();(d/'.dict').symlink_to(OUT/'preserved/gen/.dict')
                env={**base_env,'LAB_COST':str(d/'cost.f32'),'LAB_BITTRACE':str(d/'final_p.u16')}
                log=(d/'compress.log').open('x');start=time.monotonic()
                p=subprocess.Popen([str(binary),'-n','--transformer',str(weights),str(inputs[n]),'out.cmx'],cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
                jobs[p.pid]=(n,p,d,log,start)
                print(json.dumps({'started_slice':n,'pid':p.pid,'new_measurement':'final-bit trace; preserved archive is reference'}),flush=True)
            while jobs:
                for pid,(n,p,d,log,start) in list(jobs.items()):
                    got,status,usage=os.wait4(pid,os.WNOHANG)
                    if not got:continue
                    p.returncode=os.waitstatus_to_exitcode(status);log.close();del jobs[pid]
                    row={'slice':n,'returncode':p.returncode,'wall_seconds_completion_poll':time.monotonic()-start,
                         'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'max_rss_kbytes':usage.ru_maxrss,
                         'measurement':'Linux wait4 per native child; completion observed within controller poll/validation delay'}
                    rows.append(row);save()
                    assert p.returncode==0,('Native trace failed',n)
                    assert (d/'out.cmx').read_bytes()==archives[n].read_bytes(),('Archive identity failed',n)
                    cost=np.fromfile(d/'cost.f32','<f4');old=np.fromfile(costs[n],'<f4')
                    assert len(cost)==2000000 and np.array_equal(cost,old),('Cost identity failed',n)
                    raw=inputs[n].read_bytes();pbits=np.fromfile(d/'final_p.u16','<u2')
                    assert len(pbits)==16000000 and np.all((pbits>=1)&(pbits<=65535)),('Trace alignment/range failed',n)
                    # Blocked reconstruction bounds transient RAM; records every actual bit.
                    worst=0.
                    for lo in range(0,len(raw),65536):
                        hi=min(len(raw),lo+65536);actual=np.unpackbits(np.frombuffer(raw[lo:hi],np.uint8),bitorder='big')
                        probabilities=pbits[8*lo:8*hi].astype(np.float64)
                        bits=-np.log2(np.where(actual,probabilities,65536.-probabilities)/65536.)
                        worst=max(worst,float(np.max(np.abs(bits.reshape(-1,8).sum(axis=1)-cost[lo:hi]))))
                    assert worst<=1e-4,('Bit reconstruction mismatch',n,worst)
                    row.update(input_sha256=W.sha(inputs[n]),archive_bit_exact_preserved=True,
                               costs_bit_exact_preserved=True,bit_trace_sha256=W.sha(d/'final_p.u16'),
                               trace_bytes=(d/'final_p.u16').stat().st_size,actual_bit_count=len(pbits),
                               native_archive_bytes=(d/'out.cmx').stat().st_size,max_reconstructed_byte_bits_diff=worst,
                               ready_for_residual_screen=True)
                    save();print(json.dumps(row),flush=True)
                if jobs:time.sleep(1)
        meta['status']='PASS';save();print('LEX_FINALBIT_2M_TRACES_COMPLETE',flush=True)
    except Exception:
        meta['status'],meta['error']='FAIL',traceback.format_exc();save();raise


if __name__=='__main__':main()
