"""Restore isolated T4 runtime and repair the preserved native/GPU pilot.

No neural SGD, paid rental, deletions or changes to original model/source.
V1 failure evidence stays intact. Each source replacement checks one anchor.
"""
import pathlib,subprocess,sys,hashlib,json,tarfile,traceback,time
out=pathlib.Path('/kaggle/working/hp_round7')
audit=out/'frozen_logits_pilot_v2_setup.json'
state={'job':'F01','scope':'Native/GPU frozen-model control, no SGD','paid_rental_usd':0,'deletions':[]}
def save_setup():audit.write_text(json.dumps(state,indent=2))
try:
    packages=pathlib.Path('/root/hp/round7_runtime_packages');packages.mkdir(parents=True,exist_ok=False)
    rc=subprocess.run(['python3','-m','pip','download','--no-deps','--only-binary=:all:','--dest',str(packages),
                       'fla-core==0.5.1','jaxtyping==0.3.11','wadler-lindig==0.1.3'],timeout=180).returncode
    assert rc==0,'Pinned isolated runtime download failed'
    expected={'fla_core-0.5.1-py3-none-any.whl':'02150d34aa1e37f6b8ed9b2feec5d29af93680573e5077ed981238179c11fb06',
              'jaxtyping-0.3.11-py3-none-any.whl':'8a4bedc4e3f963fa82df41bd13c7ebc2bad925601eb48614c65798f21329d4e3',
              'wadler_lindig-0.1.3-py3-none-any.whl':'3018e4e6b115a7ef21c77414a41cbe7e03e83f6b5e25004958e33432a17f3c94'}
    for n,h in expected.items():assert hashlib.sha256((packages/n).read_bytes()).hexdigest()==h,n+' wheel hash differs'
    site=pathlib.Path('/root/hp/round7_runtime_site');site.mkdir(exist_ok=False)
    rc=subprocess.run(['python3','-m','pip','install','--no-deps','--no-index','--target',str(site),
                       *[str(packages/n) for n in expected]],timeout=120).returncode
    assert rc==0,'Isolated runtime installation failed'
    repo=pathlib.Path('/root/hp/src/fx2-cmix-transformer-v1');repo.mkdir(parents=True,exist_ok=False)
    tools_dir=pathlib.Path('/root/hp/tools');tools_dir.mkdir(exist_ok=False)
    names=['6m-q4-fp32.tch','8m.tch','10m.tch'];prefix='src/fx2-cmix-transformer-v1/'
    with tarfile.open(out/'preserved/research_sources_and_candidates.tar.gz','r:gz') as tar:
        for m in tar.getmembers():
            if not m.isfile() or not m.name.startswith(prefix):continue
            suffix=m.name[len(prefix):]
            if not (suffix.startswith('pysrc/') and suffix.endswith('.py') or suffix in ['models/'+n for n in names]):continue
            p=repo/suffix;assert p.resolve().is_relative_to(repo.resolve());p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(tar.extractfile(m).read())
        (tools_dir/'tfh.py').write_bytes(tar.extractfile('tools/tfh.py').read())
    hashes={'6m-q4-fp32.tch':'2ca3428f729799a93927822c14c67ef99493ceeabf6e82895b7f07646b4024fd',
            '8m.tch':'a88aad29b44fc58bb5e1a9d0f4123d34e58a1d2945e7067566030158965cdbbb',
            '10m.tch':'c84a6d4cfcb9915d38b9447d95290815007cb85c5fdc28cd4d39c642155fb7a7'}
    for n,h in hashes.items():assert hashlib.sha256((repo/'models'/n).read_bytes()).hexdigest()==h,n+' weight hash differs'
    source=(out/'research_round7_frozen_logits_pilot_worker.py').read_text()
    state['original_worker_sha256']=hashlib.sha256(source.encode()).hexdigest()
    source=source.replace("'frozen_logits_pilot'","'frozen_logits_pilot_v2'")
    source=source.replace("'/root/hp/frozen_logits_pilot'","'/root/hp/frozen_logits_pilot_v2'")
    def replace_once(old,new):
        global source
        assert source.count(old)==1,'Unexpected source anchor: '+old[:90]
        source=source.replace(old,new)
    replace_once(",str(work/'tokens.u8'),'--save-article-boundaries',str(work/'bounds.i32'),str(inp)",
                 ",str(work/'tokens.u8'),str(inp)")
    old="bounds=np.fromfile(work/'bounds.i32','<i4').astype(np.int64);assert bounds[0]==0 and bounds[-1]==N and np.all(np.diff(bounds)>0)"
    new="""from research_round7_field_screen import literal_wrt,SEP
    from research_round7_wrt import load_dictionary
    import re
    observed_map={}
    for byte,token in zip(raw,tokens):
        if byte in observed_map:assert observed_map[byte]==int(token),'Token map changed within stream'
        else:observed_map[byte]=int(token)
    assert len(set(observed_map.values()))==len(observed_map),'Token map not injective'
    ordered=[observed_map[b] for b in sorted(observed_map)]
    assert all(a<b for a,b in zip(ordered,ordered[1:])),'Vocabulary mapping not ordered'
    marker=literal_wrt(SEP,load_dictionary(pre/'gen/.dict'))
    expected_sep=bytes([0x08,0x08,0x25,0xac,0x65,0x27,0x05,0x08,0x08,0x08,0x08,0x25,0xac,0x68,0x27])
    assert bytes(observed_map[b] for b in marker)==expected_sep,'Dictionary marker does not match native separator'
    ends=[m.end() for m in re.finditer(re.escape(expected_sep),tokens.astype('u1').tobytes())]
    assert ends,'No complete native article marker'
    bounds=np.asarray(sorted(set([0,*ends,N])),np.int64)
    assert bounds[0]==0 and bounds[-1]==N and np.all(np.diff(bounds)>0)
    bounds.astype('<i4').tofile(work/'bounds.i32')
    result['repair']={'CLI':'Removed -e-only article-boundary extraction from raw -n sample',
                     'boundaries':'Derived from complete native token markers, validated against dictionary encoding',
                     'parity_rows':'Only N-1 rows with real next targets; uncoded EOF row excluded',
                     'thresholds':'Original numerical thresholds unchanged'}"""
    replace_once(old,new)
    replace_once('native_clamped=np.maximum(native.astype(np.float64),1e-6)',
                 'native_clamped=np.maximum(native[:-1].astype(np.float64),1e-6)')
    replace_once('q=np.maximum(gpu_rows.astype(np.float64),1e-6)',
                 'q=np.maximum(gpu_rows[:-1].astype(np.float64),1e-6)')
    state.update(runtime_restored=True,global_torch_unchanged=True,weights_verified=True,
                 patched_worker_sha256=hashlib.sha256(source.encode()).hexdigest())
    (out/'frozen_logits_pilot_v2_effective.py').write_text(source);save_setup()
    exec(compile(source,str(out/'frozen_logits_pilot_v2_effective.py'),'exec'),globals())
except Exception as e:
    state.update(failed=True,error=str(e),traceback=traceback.format_exc());save_setup();print(state['traceback'],flush=True);raise
