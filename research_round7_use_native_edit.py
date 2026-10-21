def _hp_use_native_edit():
    import pathlib,subprocess,os,json,signal,time,ctypes,sys
    import numpy as np
    out=pathlib.Path('/kaggle/working/hp_round7')
    library=out/'hp_edit_kernel.so'
    subprocess.run(['clang++-17','-O3','-std=c++17','-shared','-fPIC',str(out/'research_round7_edit_kernel.cpp'),'-o',str(library)],check=True)
    sys.path.insert(0,str(out))
    import research_round7_edit_screen as E
    kernel=ctypes.CDLL(str(library)).hp_edit_logratio
    kernel.argtypes=[ctypes.c_char_p,ctypes.c_uint64,ctypes.c_char_p,ctypes.c_uint64,ctypes.POINTER(ctypes.c_double),ctypes.c_double,ctypes.c_double,ctypes.c_double]
    kernel.restype=ctypes.c_double
    rng=np.random.default_rng(923); error=0.; cases=0
    for j in range(30):
        donor=rng.integers(65,70,size=10+j%8,dtype=np.uint8).tobytes()
        observed=bytearray(donor)
        if j%3==0:observed[j%len(observed)]=88
        if j%3==1:observed.insert(j%len(observed),89)
        if j%3==2:del observed[j%len(observed)]
        costs=rng.uniform(.05,12,size=len(observed)).astype(np.float64)
        for rates in E.CHANNELS:
            E._native=None; slow=E.edit_logratio(bytes(observed),donor,costs,rates)
            E._native=kernel; fast=E.edit_logratio(bytes(observed),donor,costs,rates)
            if np.isfinite(slow):error=max(error,abs(slow-fast))
            elif slow!=fast:raise RuntimeError('Native infinite-path mismatch')
            cases+=1
    if error>1e-9:raise RuntimeError('Native edit likelihood disagrees')
    E.self_test()
    print(json.dumps({'parity_cases':cases,'max_error_bits':error}),flush=True)
    (out/'edit_kernel_parity.json').write_text(json.dumps({'cases':cases,'maximum_absolute_error_bits':error},indent=2))
    # Replace only this experiment's slow Python scorers after proving parity.
    stopped=[]
    for proc in pathlib.Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:args=(proc/'cmdline').read_bytes().split(b'\0')
        except OSError:continue
        if str(out/'research_round7_edit_screen.py').encode() in args and b'edit' in args and b'--mode' in args:
            pid=int(proc.name);os.kill(pid,signal.SIGTERM);stopped.append(pid)
    jobs=[]
    for name in ['a','b']:
        env={**os.environ,'HP_EDIT_KERNEL':str(library),'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
        with (out/(name+'_native_edit.log')).open('w') as log:
            p=subprocess.Popen(['python','-u',str(out/'research_round7_edit_screen.py'),'--slice',f'/root/hp/slices/{name}2m.bin','--cost',f'/root/hp/runs/lex_{name}/cost.f32','--dictionary','/root/hp/gen/.dict','--mode','edit','--json',str(out/(name+'_native_edit_screen.json'))],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        (out/(name+'_native_edit.pid')).write_text(str(p.pid));jobs.append({'slice':name,'pid':p.pid})
    print(json.dumps({'equivalent_scorers_replaced':stopped,'jobs':jobs}))
_hp_use_native_edit()
del _hp_use_native_edit
