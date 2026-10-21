"""Reuse completed regional costs; independently decode real WRT to label words.

Runs only after the live four-core serialized verification releases its CPUs.
No label enters a coding model. Region histories remain local, not full-stream.
"""

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
import gzip,hashlib,json,multiprocessing as mp,os,re,resource,subprocess,sys,time,traceback
import numpy as np
sys.path.insert(0,'/root/r14_code_v2')
from hutter_research.cpu_round13_jobs import atomic_json,initialize_lane,sha
from hutter_research import cpu_round13_jobs as lanes
from hutter_research.constructor_codec import WORDS
W=Path('/kaggle/working');OUT=W/'hp_round14/word_costs_v2';ROOT=Path('/root/r14_word_costs_v2');P=Path('/root/hp_round14_pulls')
SOURCE=W/'hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt';TREE=W/'hp_round8/native_stage_trace_v1/tree'
REGIONS=FREQ=DICT=None;CTOR=set(WORDS)
CATEGORIES=('body_constructor','body_dictionary_other','body_literal_or_oov','metadata_word','nonword_or_unlabelled')
CUTS=(2,16,64,107,128,1024,1392,8372)
def shard(task):
    ids=task;label='_'.join(map(str,ids));start=time.monotonic();cpu0=resource.getrusage(resource.RUSAGE_SELF)
    windows=[(REGIONS[i]['offset']+2097152,REGIONS[i]['offset']+3145728) for i in ids]
    wp=ROOT/('windows_'+label+'.txt');wp.write_text(''.join(f'{a} {b}\n' for a,b in windows))
    events=ROOT/('events_'+label+'.tsv');log=OUT/('parser_'+label+'.log')
    with log.open('wb') as f:r=subprocess.run([str(ROOT/'word_events'),str(SOURCE),str(TREE/'dictionary/english.dic'),str(events),str(ROOT/('sample_'+label+'.txt')),str(max(b for a,b in windows)),str(wp)],stdout=f,stderr=subprocess.STDOUT)
    assert r.returncode==0,('independent WRT scanner failed',r.returncode,str(log))
    rows=[];states=[]
    for index,(lo,hi) in zip(ids,windows):
        role='development' if index<8 else 'confirmation'
        p=P/f'hutter-r13-warm-{role}-v1'/('warm-'+role)/f'region_{index:02}.cost.f32.gz'
        cost=np.frombuffer(gzip.decompress(p.read_bytes()),dtype='<f4').astype('float64');assert cost.shape==(3145728,) and np.isfinite(cost).all() and (cost>=0).all()
        cost=cost[2097152:];states.append({'index':index,'lo':lo,'hi':hi,'cost':cost,'cum':np.r_[0.,np.cumsum(cost)],'owner':np.full(len(cost),-1,dtype='i1'),
            'groups':{k:{'events':0,'coded_bytes':0,'native_bits':0.} for k in CATEGORIES},
            'thresholds':{str(c):{'events':0,'coded_bytes':0,'native_bits':0.} for c in CUTS},'words':{}})
    with events.open() as f:
        for line in f:
            region,lo,hi,complete,body,word=line.rstrip('\n').split('\t');s=states[int(region)]
            lo,hi,complete,body=map(int,(lo,hi,complete,body));assert s['lo']+16<=lo<hi<=complete<=s['hi']
            a,b=lo-s['lo'],hi-s['lo'];assert (s['owner'][a:b]<0).all()
            ci=0 if word in CTOR else 1 if word in DICT else 2;ci=ci if body else 3;s['owner'][a:b]=ci
            bits=float(s['cum'][b]-s['cum'][a]);n=b-a;g=s['groups'][CATEGORIES[ci]];g['events']+=1;g['coded_bytes']+=n;g['native_bits']+=bits
            if body:
                w=s['words'].setdefault(word,{'word':word,'events':0,'coded_bytes':0,'native_bits':0.,'corpus_count':FREQ.get(word,0)})
                w['events']+=1;w['coded_bytes']+=n;w['native_bits']+=bits
                for cut,g in s['thresholds'].items():
                    if FREQ.get(word,0)<int(cut):g['events']+=1;g['coded_bytes']+=n;g['native_bits']+=bits
    for s in states:
        total=float(s['cost'].sum());unlabelled=s['owner']<0;s['groups'][CATEGORIES[4]].update(coded_bytes=int(unlabelled.sum()),native_bits=float(s['cost'][unlabelled].sum()))
        assert abs(sum(g['native_bits'] for g in s['groups'].values())-total)<1e-4
        words=sorted(s['words'].values(),key=lambda w:(-w['native_bits'],w['word']))
        p=OUT/f"region_{s['index']:02}_words.tsv.gz"
        with gzip.open(p,'wt') as f:
            f.write('word\tevents\tcoded_bytes\tnative_bits\tcorpus_count\n')
            for w in words:f.write(f"{w['word']}\t{w['events']}\t{w['coded_bytes']}\t{w['native_bits']:.12g}\t{w['corpus_count']}\n")
        row={'index':s['index'],'scored_interval':[s['lo'],s['hi']],'native_bits':total,'categories':s['groups'],'rarity_thresholds':s['thresholds'],
          'top_aggregate_bit_words':words[:60],'top_mean_bit_words_min8':[w for w in sorted(words,key=lambda w:(-w['native_bits']/w['events'],w['word'])) if w['events']>=8][:60],
          'words_file_sha256':sha(p),'CPU_lane':lanes.LANE_CPU,'exact_WRT_character_crosscheck':True}
        atomic_json(OUT/f"region_{s['index']:02}.json",row);rows.append(row)
    u=resource.getrusage(resource.RUSAGE_SELF);v=resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'indices':ids,'regions':rows,'CPU_lane':lanes.LANE_CPU,'wall_seconds':time.monotonic()-start,
       'worker_CPU_seconds':u.ru_utime+u.ru_stime-cpu0.ru_utime-cpu0.ru_stime,'parser_CPU_seconds':v.ru_utime+v.ru_stime}
def main():
    global REGIONS,FREQ,DICT
    assert not ROOT.exists() and not OUT.exists();ROOT.mkdir();OUT.mkdir()
    M={'status':'WAITING_FOR_FOUR_LIVE_CPUS','started':time.time(),'shards':[],'deletions':[],'GPU':False,'paid_usd':0,
      'scope':'16 completed 1 MiB regional-warm cost windows; exact globally parsed word labels; labels not available to decoder gates'}
    def save():atomic_json(OUT/'manifest.json',M)
    try:
        save()
        while True:
            v=json.loads((W/'hp_round14/full_serialized_verification_v1.json').read_text())
            if v['status'].startswith('FAIL'):raise RuntimeError('prior live verification failed; inspect before scheduling')
            if v['status']=='COMPLETE_ALL_FOUR_SERIALIZED_ARCHIVES_EXACT':break
            time.sleep(60)
        M['status']='VALIDATING_WORD_PARSER';save()
        assert sha(SOURCE)=='7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce'
        r=subprocess.run(['g++','-O2','-std=c++17','-I'+str(TREE/'src/preprocess'),'/root/research_round14_word_events.cpp',str(TREE/'src/preprocess/dictionary.cpp'),'-o',str(ROOT/'word_events')],capture_output=True,text=True)
        assert r.returncode==0,r.stderr[-3000:]
        REGIONS={}
        for role in ('development','confirmation'):
            manifest=json.loads((P/f'hutter-r13-warm-{role}-v1'/('warm-'+role)/'manifest.json').read_text())
            for row in manifest['cases']:
                r=row['region'];assert set(('id','offset','bytes','warmup_bytes'))<=r.keys()
                assert r['bytes']==3145728 and r['warmup_bytes']==2097152 and r['id'] not in REGIONS
                REGIONS[r['id']]=r
        assert set(REGIONS)==set(range(16)), 'published region manifest contract differs'
        DICT=set(re.findall('[a-z]+',(TREE/'dictionary/english.dic').read_text()))
        freq=W/'hp_round11/word_coverage_v1/strict_ascii_first_appearance.tsv.gz'
        assert sha(freq)=='a0e8824a13b84d0a911f68fd44284680b0c53aace3310134ec3175f4ea2c4c3d'
        with gzip.open(freq,'rt') as f:
            next(f);FREQ={p[0]:int(p[1]) for line in f if (p:=line.rstrip('\n').split('\t'))}
        ids=sorted(REGIONS,key=lambda i:REGIONS[i]['offset']);tasks=[ids[i:i+4] for i in range(0,16,4)]
        cpus=sorted(os.sched_getaffinity(0))[:4];assert len(cpus)==4;ctx=mp.get_context('fork');q=ctx.Queue()
        for c in cpus:q.put(c)
        M['status']='FOUR_LANE_NATIVE_WORD_ALIGNMENT';save()
        with ProcessPoolExecutor(4,mp_context=ctx,initializer=initialize_lane,initargs=(q,)) as pool:
            for f in as_completed([pool.submit(shard,t) for t in tasks]):M['shards'].append(f.result());save()
        M.update(status='COMPLETE_16_WARM_WORD_COST_REGIONS',finished=time.time());save()
    except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
if __name__=='__main__':main()
