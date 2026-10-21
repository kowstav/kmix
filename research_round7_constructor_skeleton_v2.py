"""I11c fixed one-byte-marker skeleton layout: avoid per-content-word/per-separator framing.

Raw zero is escaped as 00 00 and raw08 as00 08; removed constructors become08.
Paid constructor stream uses direct framed raw words or a paid raw-word table.
All channels, flags, IDs, tables, case/control/EOF bytes are included.
This is a matched zlib/LZMA screen, not a final cmix probability claim.
"""
import collections,hashlib,json,pathlib,resource,time,zlib,lzma
import numpy as np
from research_round7_constructor_split import ROOT,split_raw,vu,blob,Reader,load_dictionary,LEXICON

DEST=ROOT/'constructor_skeleton_v2'

def transform(raw,spans,mode):
    skeleton=bytearray();words=[];pos=0
    for a,b in spans:
        assert pos<=a<b<=len(raw)
        skeleton.extend(raw[pos:a].replace(b'\x00',b'\x00\x00').replace(b'\x08',b'\x00\x08'));skeleton.append(8)
        words.append(raw[a:b]);pos=b
    skeleton.extend(raw[pos:].replace(b'\x00',b'\x00\x00').replace(b'\x08',b'\x00\x08'))
    g=bytearray(b'CS1'+bytes([mode]));g.extend(vu(len(words)))
    table=[]
    if mode:
        # Order table by observed frequency; its explicit raw definition is paid.
        count=collections.Counter(words);table=sorted(count,key=lambda w:(-count[w],w));ids={w:i for i,w in enumerate(table)}
        g.extend(vu(len(table)));g.extend(b''.join(blob(w) for w in table));g.extend(b''.join(vu(ids[w]) for w in words))
    else:g.extend(b''.join(blob(w) for w in words))
    return bytes(skeleton),bytes(g),{'raw_constructor_type_count':len(table),
                                   'raw_table_bytes':len(vu(len(table)))+sum(len(blob(w)) for w in table) if mode else 0}

def inverse(skeleton,grammar):
    assert grammar[:3]==b'CS1' and grammar[3] in (0,1)
    r=Reader(grammar);r.i=4;n=r.integer();table=[]
    if grammar[3]:table=[r.blob() for _ in range(r.integer())];words=[table[r.integer()] for _ in range(n)]
    else:words=[r.blob() for _ in range(n)]
    r.done();out=bytearray();i=0;j=0
    while i<len(skeleton):
        c=skeleton[i];i+=1
        if c==0:
            assert i<len(skeleton);literal=skeleton[i];i+=1
            assert literal in (0,8);out.append(literal)
        elif c==8:
            assert j<len(words);out.extend(words[j]);j+=1
        else:out.append(c)
    assert j==len(words);return bytes(out)

def pack(c,g,codec):
    f=(lambda b:zlib.compress(b,9)) if codec=='zlib9' else (lambda b:lzma.compress(b,preset=6))
    return b'CSP2'+bytes([codec=='lzma6'])+blob(f(c))+blob(f(g))

def unpack(p):
    assert p[:4]==b'CSP2' and p[4] in (0,1);r=Reader(p);r.i=5
    f=zlib.decompress if p[4]==0 else lzma.decompress
    c=f(r.blob());g=f(r.blob());r.done();return inverse(c,g)

def selftest():
    for x in range(256):
        raw=bytes([x])+b'aa'+bytes([x])+b'aa'+bytes([x])
        for mode in (0,1):
            c,g,_=transform(raw,[(1,3),(4,6)],mode);assert inverse(c,g)==raw
    for raw,spans in [(b'\x00a\x00b\x00',[(1,2),(3,4)]),(b'\x00',[]),(b'\x00\xffab\x00ab',[(2,4),(5,7)]),(b'abc',[(0,3)])]:
        for mode in (0,1):
            c,g,_=transform(raw,spans,mode);assert inverse(c,g)==raw
            for codec in ('zlib9','lzma6'):assert unpack(pack(c,g,codec))==raw
    print(json.dumps({'I11c_one_byte_marker_256_literal_boundaries_roundtrip':'PASS'}),flush=True)

if __name__=='__main__':
    selftest();DEST.mkdir(exist_ok=False);d=load_dictionary(ROOT/'preserved/gen/.dict');rows=[]
    manifest={'status':'RUNNING','experiment':'I11c one-byte constructor marker layout',
              'fixed_before_run':['same176-word lexicon','fixed08 one-byte marker with00 escape of raw00/08','direct/paid categorical constructor dictionary','zlib9/lzma6','ABCD2M'],
              'source_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
              'split_dependency_sha256':hashlib.sha256((ROOT/'research_round7_constructor_split.py').read_bytes()).hexdigest(),
              'neural_training':False,'paid_rental_usd':0,'deletions':[]}
    (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2))
    try:
        for name in 'abcd':
            ip=ROOT/'preserved/slices'/(name+'2m.bin') if name in 'ab' else ROOT/(name+'2m.bin')
            raw=ip.read_bytes();cost=np.fromfile(ROOT/'lex_native_2m'/(name+'_cost.f32'),'<f4');assert len(raw)==len(cost)==2000000
            start=time.monotonic();cpu=time.process_time();_,_,spans,_,_=split_raw(raw,d)
            baselines={'zlib9':len(zlib.compress(raw,9)),'lzma6':len(lzma.compress(raw,preset=6))};screens=[]
            for mode,label in enumerate(('direct','constructor_word_table')):
                c,g,meta=transform(raw,spans,mode);assert inverse(c,g)==raw
                for codec in ('zlib9','lzma6'):
                    packet=pack(c,g,codec);assert unpack(packet)==raw
                    screens.append({'representation':label,'codec':codec,'candidate_archive_bytes':len(packet),
                                    'matched_original_archive_bytes':baselines[codec],
                                    'bytes_saved_before_incremental_decoder':baselines[codec]-len(packet),
                                    'skeleton_raw_bytes':len(c),'constructor_channel_raw_bytes':len(g),**meta,
                                    'packet_sha256':hashlib.sha256(packet).hexdigest(),'roundtrip':'PASS'})
            r={'slice':name,'input_bytes':len(raw),'constructor_spans':len(spans),'screen_rows':screens,
               'input_sha256':hashlib.sha256(raw).hexdigest(),'cost_sha256':hashlib.sha256(cost.astype('<f4',copy=False).tobytes()).hexdigest(),
               'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,
               'prototype_peak_RSS_KiB_process_to_date':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'interpretation':'Matched-codec exact raw skeleton screen; no cmix or qualifying package improvement implied.',
               'neural_training':False,'paid_rental_usd':0,'deletions':[]}
            rows.append(r);(DEST/(name+'.json')).write_text(json.dumps(r,indent=2));(DEST/'summary.json').write_text(json.dumps(rows,indent=2))
            print(json.dumps({'slice':name,'saved_bytes':[v['bytes_saved_before_incremental_decoder'] for v in screens],
                              'wall_seconds':r['wall_seconds']}),flush=True)
        manifest['status']='COMPLETE'
    except BaseException as exc:manifest['status']='FAILED';manifest['error']=repr(exc);raise
    finally:(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('CONSTRUCTOR_SKELETON_SCREEN_COMPLETE',flush=True)
