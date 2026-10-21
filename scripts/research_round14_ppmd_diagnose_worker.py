
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import sys,subprocess,json,traceback,struct,gzip,time
W=Path('/kaggle/working/hp_round14');R=Path('/root/r14_ppmd_diagnostic');R.mkdir();M={'status':'INSTALLING','started':time.time(),'cases':[]}
def save():(W/'ppmd_diagnostic_v1.json').write_text(json.dumps(M,indent=2))
try:
    save()
    with (W/'ppmd_diagnostic_install.log').open('wb') as f:subprocess.run([sys.executable,'-m','pip','install','--target',str(R/'lib'),'pyppmd==1.3.1'],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
    sys.path.insert(0,str(R/'lib'));sys.path.insert(0,'/root/r14_code_v2')
    import pyppmd
    from hutter_research.article_order_ppmd import compress,decompress
    # Independent real-data stress test; no compression selection from these runs.
    source=Path('/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt')
    raw=source.read_bytes()[:2<<20]
    for n in (65536,1048576,2097152):
        for order in (8,16):
            x=raw[:n];p=pyppmd.compress(x,max_order=order,mem_size=64<<20,variant='I');row={'bytes':n,'order':order,'compressed':len(p)}
            for label,fn in [('simple',lambda:pyppmd.decompress(p,max_order=order,mem_size=64<<20,variant='I')),('bounded',lambda:pyppmd.Ppmd8Decoder(order,64<<20).decode(p,len(x)))]:
                try:row[label]={'exact':fn()==x}
                except Exception as e:row[label]={'error':repr(e)}
            M['cases'].append(row);save()
    M.update(status='COMPLETE_DIAGNOSTIC',finished=time.time());save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
