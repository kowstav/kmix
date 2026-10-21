"""Versioned paid permutation with native 7z PPMd-H and exact framed inverse.

All bytes of the embedded 7z container are counted. This is a raw proxy, not a
qualifying native lexical archive. Temporary codec files contain only newly
generated data; their automatic cleanup is counted in SCRATCH for the run ledger.
"""
import gzip, hashlib, json, shutil, struct, subprocess, tempfile
from pathlib import Path
import numpy as np
from .article_order_ppmd import graph_orders as _graph_orders
MAGIC=b'HPOR14H0'
SCRATCH={'files_created_and_removed':0,'bytes_created_and_removed':0}

def _settings(max_order,mem_size):
    if not 2<=max_order<=64 or mem_size not in (8<<20,64<<20):raise ValueError('unregistered PPMd settings')

def backend_identity():
    exe=shutil.which('7z')
    if exe is None:raise RuntimeError('native 7z absent; no silent fallback')
    p=Path(exe).resolve()
    # Debian's /usr/bin/7z can be a wrapper. Hash the actual codec binary too.
    files=[p]
    q=Path('/usr/lib/p7zip/7z')
    if q.exists() and q!=p:files.append(q)
    return {'command':'7z','version':subprocess.run([exe],capture_output=True,text=True,timeout=10).stdout.split('Usage:')[0].strip(),
            'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}

def compress_payload(raw,max_order=8,mem_size=64<<20):
    _settings(max_order,mem_size)
    with tempfile.TemporaryDirectory(prefix='hp14_ppmd_') as tmp:
        p=Path(tmp)/'payload.7z'
        args=['7z','a','-t7z',f'-m0=PPMd:mem={mem_size>>20}m:o={max_order}','-mmt=1','-mtm=off','-mtc=off','-mta=off','-bd','-bb0','-y','-sistored.bin',str(p)]
        r=subprocess.run(args,input=raw,capture_output=True,timeout=180)
        if r.returncode:raise RuntimeError('native PPMd encode failed: '+r.stderr.decode(errors='replace')[-400:])
        data=p.read_bytes();SCRATCH['files_created_and_removed']+=1;SCRATCH['bytes_created_and_removed']+=len(data)
        return data

def decompress_payload(data,expected_bytes):
    with tempfile.TemporaryDirectory(prefix='hp14_ppmd_') as tmp:
        p=Path(tmp)/'payload.7z';p.write_bytes(data)
        SCRATCH['files_created_and_removed']+=1;SCRATCH['bytes_created_and_removed']+=len(data)
        # Read stdout: the embedded name can never choose an extraction path.
        r=subprocess.run(['7z','x','-so','-bd',str(p)],capture_output=True,timeout=180)
        if r.returncode or len(r.stdout)!=expected_bytes:raise ValueError('native PPMd inverse or length failed')
        return r.stdout

def compress(pages,order,max_order=8,mem_size=64<<20):
    _settings(max_order,mem_size);n=len(pages);order=list(map(int,order))
    if sorted(order)!=list(range(n)):raise ValueError('invalid permutation')
    ordering=b'' if order==list(range(n)) else gzip.compress(np.asarray(order,dtype='<u4').tobytes(),mtime=0)
    lengths=gzip.compress(np.asarray([len(pages[i]) for i in order],dtype='<u4').tobytes(),mtime=0)
    raw=b''.join(pages[i] for i in order);payload=compress_payload(raw,max_order,mem_size)
    return MAGIC+struct.pack('<6I',n,max_order,mem_size,len(ordering),len(lengths),len(payload))+ordering+lengths+payload

def decompress(blob):
    if len(blob)<32 or blob[:8]!=MAGIC:raise ValueError('invalid order container')
    n,o,m,a,b,c=struct.unpack_from('<6I',blob,8);_settings(o,m)
    if 32+a+b+c!=len(blob):raise ValueError('invalid order framing')
    seq=np.frombuffer(gzip.decompress(blob[32:32+a]),dtype='<u4').tolist() if a else list(range(n))
    if sorted(seq)!=list(range(n)):raise ValueError('invalid paid permutation')
    lengths=np.frombuffer(gzip.decompress(blob[32+a:32+a+b]),dtype='<u4').tolist()
    if len(lengths)!=n:raise ValueError('invalid lengths')
    raw=decompress_payload(blob[32+a+b:],sum(lengths));pages=[None]*n;offset=0
    for i,k in zip(seq,lengths):pages[i]=raw[offset:offset+k];offset+=k
    if offset!=len(raw):raise ValueError('invalid restored lengths')
    return pages

def graph_orders(pages):return _graph_orders(pages,compress_payload=compress_payload)
