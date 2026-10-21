"""Finite paid constructor/variable/anchor CPU proxy with matched controls."""

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
from hutter_research.constructor_codec import encode,decode,inspect_sizes
from hutter_research.article_order import read_pages
import gzip
import hashlib
import json
import os
import resource
import time
import traceback

W=Path('/kaggle/working/hp_round11/constructor_proxy_v1')
assert not W.exists(), 'Inspect existing version rather than duplicate'
W.mkdir(parents=True)
SOURCE=Path('/root/hp_round11_private_assets_v2/data/pages.bin')
ARMS=[('unigram',0),('markov',1),('markov',4),('anchors',1),('anchors',4),('wrong_anchors',4),('bag',0)]
M={'status':'RUNNING_PAID_CONSTRUCTOR_PROXY','started':time.time(),'pid':os.getpid(),
   'arms':ARMS,'deletions':[],'paid_usd':0,'GPU':False,'cases':[],
   'scope':'Three disjoint consecutive sets of 128 complete early raw pages; gzip proxy, not canonical native compression.',
   'selection':'All variants registered before their sizes; exploratory proxy selection has no held-out corpus claim.',
   'production_package_qualified':False}

def sha(raw): return hashlib.sha256(raw).hexdigest()
def save(): (W/'manifest.json').write_text(json.dumps(M,indent=2))

try:
    save(); assert sha(SOURCE.read_bytes())=='f21282dac8f18561f16050ca9c6945fe95e09ce782e541bf449d1ab688d471a1'
    pages=read_pages(SOURCE); assert len(pages)==512
    for group in range(3):
        raw=b''.join(pages[group*128:(group+1)*128]); raw_sha=sha(raw)
        baseline=gzip.compress(raw,compresslevel=9,mtime=0)
        (W/f'group{group}_gzip.gz').write_bytes(baseline)
        for mode,alpha in ARMS:
            before=resource.getrusage(resource.RUSAGE_SELF); begin=time.monotonic()
            archive=encode(raw,mode,alpha)
            encode_wall=time.monotonic()-begin; middle=resource.getrusage(resource.RUSAGE_SELF)
            begin=time.monotonic(); reconstructed=decode(archive)
            after=resource.getrusage(resource.RUSAGE_SELF)
            assert reconstructed==raw
            name=f'group{group}_{mode}_alpha{alpha}'
            (W/(name+'.hpctor')).write_bytes(archive)
            row={'name':name,'mode':mode,'alpha_numerator_over_eight':alpha,'group':group,
                 'source_raw_bytes':len(raw),'source_sha256':raw_sha,'gzip_baseline_bytes':len(baseline),
                 'archive_bytes':len(archive),'archive_sha256':sha(archive),
                 'actual_proxy_saving_vs_gzip_bytes':len(baseline)-len(archive),
                 'channel_bytes':inspect_sizes(archive),'container_header_bytes':50,'independent_reconstruction_exact':True,
                 'encode_wall_seconds':encode_wall,'decode_wall_seconds':time.monotonic()-begin,
                 'encode_CPU_seconds':middle.ru_utime+middle.ru_stime-before.ru_utime-before.ru_stime,
                 'decode_CPU_seconds':after.ru_utime+after.ru_stime-middle.ru_utime-middle.ru_stime,
                 'process_peak_RSS_KiB':after.ru_maxrss}
            M['cases'].append(row); save()
    M.update(status='COMPLETE_THREE_GROUP_PAID_CONSTRUCTOR_PROXY',finished=time.time())
    save()
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc(),finished=time.time()); save(); raise
