
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
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip,hashlib,json,multiprocessing as mp,os,resource,struct,time,traceback
from hutter_research.cpu_round13_jobs import atomic_json,initialize_lane,sha
from hutter_research import cpu_round13_jobs as lanes
from hutter_research.constructor_codec import decode
ROOT=Path('/root/hp_round14_full_verify');W=Path('/kaggle/working/hp_round14')
FILES=Path('/root/hp_round14_pulls/hutter-r13-full-corpus-factorization-v1/full-corpus-factorization')
def one(t):
    policy,index,offset,n,size,expected=t;start=time.monotonic();u=resource.getrusage(resource.RUSAGE_SELF)
    with (FILES/(policy+'.hpfull')).open('rb') as f:f.seek(offset);blob=f.read(size)
    if blob.startswith(b'HPCTOR11'):raw=decode(blob)
    elif blob.startswith(b'\x1f\x8b'):raw=gzip.decompress(blob)
    elif blob.startswith(b'\x28\xb5\x2f\xfd'):
        import zstandard
        raw=zstandard.ZstdDecompressor().decompress(blob,max_output_size=n)
    else:raise ValueError('unknown serialized codec')
    assert len(raw)==n and hashlib.sha256(raw).hexdigest()==expected
    (ROOT/f'{policy}_{index:03}.bin').write_bytes(raw);a=resource.getrusage(resource.RUSAGE_SELF)
    return {'policy':policy,'chunk':index,'bytes':n,'sha256':expected,'CPU_lane':lanes.LANE_CPU,
        'CPU_seconds':a.ru_utime+a.ru_stime-u.ru_utime-u.ru_stime,'wall_seconds':time.monotonic()-start}
def main():
    ROOT.mkdir(exist_ok=False);M={'status':'VALIDATING_SERIALIZED_FRAMES','started':time.time(),'cases':[],'results':[],'workers':4,'deletions':[]}
    out=W/'full_serialized_verification_v1.json'
    try:
        atomic_json(out,M);source=json.loads((FILES/'manifest.json').read_text());tasks=[]
        for row in source['full_archives']:
            policy=row['policy'];p=FILES/(policy+'.hpfull');assert sha(p)==row['archive_sha256']
            rows={r['chunk']:r for r in source['cases'] if r['policy']==policy}
            with p.open('rb') as f:
                assert f.read(8)==b'HPFULL13';n,k=struct.unpack('<QI',f.read(12));assert n==1000000000 and k==239
                total=0
                for i in range(k):
                    rawlen,size=struct.unpack('<II',f.read(8));assert 0<rawlen<=4194304 and size>0
                    offset=f.tell();blob=f.read(size);assert len(blob)==size and hashlib.sha256(blob).hexdigest()==rows[i]['archive_sha256']
                    tasks.append((policy,i,offset,rawlen,size,rows[i]['input_sha256']));total+=rawlen
                assert total==n and not f.read(1)
        tasks.sort(key=lambda t:(t[0] in ('gzip','zstd'),t[1],t[0]))
        cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);M['status']='INDEPENDENT_FOUR_LANE_FULL_DECODE';atomic_json(out,M)
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(one,t) for t in tasks]):M['cases'].append(f.result());atomic_json(out,M)
        for policy in ('gzip','zstd','markov','coarse_right'):
            h=hashlib.sha256();n=0
            for i in range(239):
                raw=(ROOT/f'{policy}_{i:03}.bin').read_bytes();h.update(raw);n+=len(raw)
            assert n==1000000000 and h.hexdigest()=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
            M['results'].append({'policy':policy,'decoded_bytes':n,'exact_original_sha256':h.hexdigest(),'independent_serialized_inverse':True})
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        M.update(status='COMPLETE_ALL_FOUR_SERIALIZED_ARCHIVES_EXACT',finished=time.time(),worker_CPU_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime);atomic_json(out,M)
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());atomic_json(out,M);raise
if __name__=='__main__':main()
