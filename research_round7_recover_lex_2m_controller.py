"""Recover interrupted native controls; reuse C/D archives, regenerate only lost A/B.

Maximum two native processes. Per-process CPU/RSS uses wait4 without GNU time.
Original results, checkpoints, costs and failure logs are preserved.
"""
import pathlib, subprocess, os, json, time, hashlib, numpy as np, shutil
out=pathlib.Path('/kaggle/working/hp_round7'); pre=out/'preserved'
dest=out/'lex_native_2m_recovered'; dest.mkdir(exist_ok=False)
work=pathlib.Path('/root/hp/lex_native_2m_recovered'); work.mkdir(parents=True,exist_ok=False)
old=out/'lex_native_2m'; records={r['slice']:r for r in json.loads((old/'results.json').read_text())}
assert len(records)==4 and all(r['same_32k_prefix_costs_exact'] for r in records.values())
binary=out/'cmix_round7_lex_codebook'; weights=out/'lex_audit/lex_h1_run11.tfwc2'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(binary)=='bedd480e36fc3a2ff3bf2150f0eded74f6d4eb4014fb3e35c6be3b5aeeda20c1'
assert digest(weights)=='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71'
binary.chmod(binary.stat().st_mode|0o111)
rows=[]; archives={n:old/(n+'_out.cmx') for n in 'cd'}
for n in 'cd':assert archives[n].stat().st_size==records[n]['native_archive_bytes']
assert not any((old/(n+'_out.cmx')).exists() for n in 'ab'),'A/B archive recovered elsewhere: inspect before recompression'
cpu_info=[s for s in pathlib.Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name') or s.startswith('flags')][:2]
meta={'scope':'Previously completed cold2M controls recovered after session restart; no neural retraining, no qualifying full package',
      'binary_sha256':digest(binary),'weights_sha256':digest(weights),'maximum_native_processes':2,
      'reuse':['C archive','D archive','all four input/cost files'],
      'regenerate_reason':'A/B archives were in lost ephemeral /root/hp; persistent compression results and costs survived',
      'cpu_info':cpu_info,'deletions':[]}
(dest/'manifest.json').write_text(json.dumps(meta,indent=2))
def start(n,kind,archive=None):
    run=work/(n+'_'+kind);run.mkdir();(run/'.dict').symlink_to(pre/'gen/.dict')
    inp=pre/'slices'/(n+'2m.bin') if n in 'ab' else out/(n+'2m.bin')
    assert digest(inp)==records[n]['input_sha256']
    env={**os.environ,'LAB_RAW':'1','LAB_VOCAB':str(pre/'data/vocab.bm'),'LAB_DICT':str(pre/'gen/.dict'),'LAB_KEEP_TEMP':'1'}
    for k in ['LAB_COST','LAB_FINAL_P','LAB_FINALMIX','LAB_UNIFORM_NN','LAB_SX']:env.pop(k,None)
    if kind=='compress':
        env['LAB_COST']=str(run/'cost.f32');args=['-n','--transformer',str(weights),str(inp),'out.cmx']
    else:args=['-d','--transformer',str(weights),str(archive),'decoded.bin']
    f=(dest/(n+'_'+kind+'.log')).open('w');t=time.monotonic()
    p=subprocess.Popen([str(binary),*args],cwd=run,env=env,stdout=f,stderr=subprocess.STDOUT)
    print('RECOVERY_STARTED',n,kind,p.pid,flush=True)
    return n,kind,p,f,run,inp,t
def finish(job):
    n,kind,p,f,run,inp,t=job
    pid,status,usage=os.wait4(p.pid,0);assert pid==p.pid
    p.returncode=os.waitstatus_to_exitcode(status);f.close()
    row={'slice':n,'operation':kind,'returncode':p.returncode,'wall_seconds_wait_observed':time.monotonic()-t,
         'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'max_rss_kbytes':usage.ru_maxrss,
         'measurement':'Linux wait4 per-process CPU/RSS; overlapping-job observed wall times are not exact completion durations'}
    assert p.returncode==0,('native recovery failed',row)
    if kind=='compress':
        cost=np.fromfile(run/'cost.f32','<f4'); prior=np.fromfile(old/(n+'_cost.f32'),'<f4'); assert cost.size==prior.size==2000000
        row.update(native_archive_bytes=(run/'out.cmx').stat().st_size,ideal_bytes=float(cost.astype(np.float64).sum()/8),
                   previous_archive_bytes=records[n]['native_archive_bytes'],all_costs_bit_exact=np.array_equal(cost,prior),
                   changed_cost_symbols=int(np.count_nonzero(cost!=prior)),max_abs_cost_difference_bits=float(np.max(np.abs(cost-prior))),
                   ideal_cost_difference_bytes=float((cost.astype(np.float64)-prior).sum()/8))
        archives[n]=dest/(n+'_out.cmx');shutil.copy2(run/'out.cmx',archives[n])
        row['archive_sha256']=digest(archives[n])
    else:
        recovered=run/'decoded.bin';got=digest(recovered)
        assert recovered.stat().st_size==2000000 and got==records[n]['input_sha256'],('decoded bytes differ',n,got)
        row.update(native_full_slice_roundtrip=True,input_bytes=2000000,decoded_sha256=got,
                   archive_sha256=digest(archives[n]),native_archive_bytes=archives[n].stat().st_size)
    rows.append(row);tmp=dest/'results.json.tmp';tmp.write_text(json.dumps(rows,indent=2));tmp.replace(dest/'results.json')
    print(json.dumps(row),flush=True)
for pair,kind in [('cd','decode'),('ab','compress'),('ab','decode')]:
    jobs=[start(n,kind,archives.get(n)) for n in pair]
    for job in jobs:finish(job)
print('LEX_NATIVE_2M_RECOVERY_COMPLETE',flush=True)
