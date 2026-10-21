"""Exact word-to-coded-span cost census on the sequential warm native prefix."""
from pathlib import Path
from collections import defaultdict
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
import numpy as np
from hutter_research.constructor_codec import WORDS

W=Path('/kaggle/working/hp_round11/word_cost_v1')
S=Path('/root/hp_round11_word_cost_v1')
assert not W.exists() and not S.exists(), 'Inspect existing word-cost job rather than duplicate'
W.mkdir(parents=True); S.mkdir()
T=Path('/kaggle/working/hp_round8/native_stage_trace_v1/tree')
ATLAS=Path('/kaggle/working/hp_round11/warm_atlas_v2/manifest.json')
TRACES=Path('/root/hp_round11/warm_atlas_v2')
N=9437184; K=524288
M={'status':'EXTRACTING_EXACT_WORD_EVENTS','started':time.time(),'pid':os.getpid(),
   'deletions':[],'paid_usd':0,'GPU':False,'production_package_qualified':False,
   'scope':'one sequential early canonical cluster, 9 MiB; descriptive word labels are never inference gates',
   'word_definition':'ASCII letters with internal apostrophes; completed delimiters, only whole coded spans',
   'excluded_prefix_bytes':16}

def save(): (W/'manifest.json').write_text(json.dumps(M,indent=2))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1<<20): h.update(b)
    return h.hexdigest()

try:
    save(); source=Path('/kaggle/working/hp_round11/word_events.cpp')
    M['word_event_source_sha256']=sha(source)
    compile_result=subprocess.run(['g++','-O2','-std=c++17','-march=x86-64-v3','-mrecip=none',
       '-I'+str(T/'src/preprocess'),str(source),str(T/'src/preprocess/dictionary.cpp'),'-o',str(S/'word_events')],
       capture_output=True,text=True)
    assert compile_result.returncode==0,compile_result.stderr[-2000:]
    (S/'windows.txt').write_text(f'0 {N}\n')
    result=subprocess.run([str(S/'word_events'),'/kaggle/working/hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt',
       str(T/'dictionary/english.dic'),str(S/'events.tsv'),str(S/'sample.txt'),str(N),str(S/'windows.txt')],
       capture_output=True,text=True)
    assert result.returncode==0,('word decoder mismatch',result.returncode,result.stdout[-500:])
    # Dictionary construction emits a short line before the final JSON record.
    lines=[line for line in result.stdout.splitlines() if line.startswith('{')]
    assert len(lines)==1
    M['independent_WRT_native_character_comparison']=json.loads(lines[0]); M['events_sha256']=sha(S/'events.tsv')
    with (S/'events.tsv').open('rb') as f, gzip.open(W/'events.tsv.gz','wb') as out:
        while b:=f.read(1<<20): out.write(b)
    M['status']='WAITING_FOR_COMPLETE_NATIVE_COST_TRACE'; save()
    while True:
        a=json.loads(ATLAS.read_text())
        if a['status']=='FAIL': raise RuntimeError('Native atlas failed; evidence preserved')
        if a['status'] in ['RUNNING_INDEPENDENT_NATIVE_DECODE','COMPLETE_SEQUENTIAL_EARLY_WARM_ATLAS_AND_INDEPENDENT_DECODE']: break
        time.sleep(45)
    assert (TRACES/'cost.f32').stat().st_size==4*N
    cost=np.asarray(np.memmap(TRACES/'cost.f32',dtype='<f4',mode='r',shape=(N,)),dtype=np.float64)
    assert np.isfinite(cost).all() and (cost>=0).all()
    cum=np.r_[0.,np.cumsum(cost)]; owner=np.full(N,-1,dtype=np.int32)
    words={}; ctors=set(WORDS)
    dictionary=set(re.findall('[a-z]+',(T/'dictionary/english.dic').read_text()))
    frequency=Path('/kaggle/working/hp_round11/word_coverage_v1/strict_ascii_first_appearance.tsv.gz')
    frequency_manifest=json.loads((frequency.parent/'manifest.json').read_text())
    assert frequency_manifest['status']=='COMPLETE_WORD_APPEARANCE_CONSTRUCTOR_CENSUS'
    assert frequency.exists(), 'Strict corpus labels must be preserved before analysis'
    with gzip.open(frequency,'rt') as f:
        next(f)
        freq={parts[0]:int(parts[1]) for line in f if (parts:=line.rstrip('\n').split('\t'))}
    categories=['body_constructor','body_dictionary_other','body_literal_or_oov','metadata_word']
    groups={name:{'events':0,'coded_bytes':0,'native_bits':0.} for name in categories}
    thresholds={str(c):{'events':0,'coded_bytes':0,'native_bits':0.} for c in [2,16,64,128,107,1024,1392,8372]}
    first={}; rows=[]
    with (S/'events.tsv').open() as f:
        for line in f:
            idx,lo,hi,completion,body,word=line.rstrip('\n').split('\t')
            lo,hi,completion,body=map(int,[lo,hi,completion,body])
            assert 16<=lo<hi<=completion<=N
            assert (owner[lo:hi]<0).all(), 'Overlapping word spans would double-count cost'
            category=categories[0 if word in ctors else 1 if word in dictionary else 2] if body else categories[3]
            owner[lo:hi]=categories.index(category)
            bits=float(cum[hi]-cum[lo]); size=hi-lo; row=groups[category]
            row['events']+=1; row['coded_bytes']+=size; row['native_bits']+=bits
            first.setdefault(word,completion)
            if body:
                aggregate=words.setdefault(word,{'word':word,'events':0,'coded_bytes':0,'native_bits':0.,'corpus_count':freq.get(word,0)})
                aggregate['events']+=1; aggregate['coded_bytes']+=size; aggregate['native_bits']+=bits
                for cut,row in thresholds.items():
                    if freq.get(word,0)<int(cut): row['events']+=1; row['coded_bytes']+=size; row['native_bits']+=bits
            rows.append((lo,hi,category,bits))
    total=float(cost.sum()); lexical=sum(r['native_bits'] for r in groups.values())
    groups['nonword_or_unlabelled']={'coded_bytes':int((owner<0).sum()),'native_bits':float(cost[owner<0].sum())}
    assert abs(sum(r['native_bits'] for r in groups.values())-total)<1e-4
    for row in groups.values(): row['share_of_all_native_bits']=row['native_bits']/total
    for row in thresholds.values(): row['share_of_all_native_bits']=row['native_bits']/total
    coverage=[{'canonical_prefix_bytes':cut,'observed_completed_word_types':sum(pos<=cut for pos in first.values()),
               'fraction_of_prefix_final_observed_types':sum(pos<=cut for pos in first.values())/len(first)}
              for cut in [K,2*K,4*K,8*K,12*K,16*K,N]]
    windows=[]
    for o in range(2*K,N,K):
        window={'offset':o,'bytes':K,'native_bits':float(cost[o:o+K].sum()),'categories':{}}
        for ci,name in enumerate(categories): window['categories'][name]=float(cost[o:o+K][owner[o:o+K]==ci].sum())
        window['categories']['nonword_or_unlabelled']=float(cost[o:o+K][owner[o:o+K]<0].sum())
        windows.append(window)
    rankings=sorted(words.values(),key=lambda row:row['native_bits'],reverse=True)
    with gzip.open(W/'all_body_word_costs.tsv.gz','wt') as f:
        f.write('word\tevents\tcoded_bytes\tnative_bits\tcorpus_count\n')
        for r in rankings: f.write(f"{r['word']}\t{r['events']}\t{r['coded_bytes']}\t{r['native_bits']:.12g}\t{r['corpus_count']}\n")
    M.update(status='COMPLETE_EXACT_WARM_WORD_COST_DIAGNOSTIC_DECODE_PENDING',finished=time.time(),
             total_native_bits=total,categories=groups,corpus_rarity_thresholds=thresholds,windows=windows,
             coded_prefix_first_appearance=coverage,observed_word_types=len(first),
             top_aggregate_bit_words=rankings[:60],top_mean_bits_words=sorted([r for r in rankings if r['events']>=8],key=lambda r:r['native_bits']/r['events'],reverse=True)[:60],
             atlas_independent_decode_exact=a.get('independent_decode_exact',False),
             frequency_table_sha256=sha(frequency),original_model_sha256='948847d9649251796f100d5353bd42859767ed5614e5e316e2c3a1c35a62ef71')
    if M['atlas_independent_decode_exact']: M['status']='COMPLETE_EXACT_WARM_WORD_COST_DIAGNOSTIC'
    save()
    while not M['atlas_independent_decode_exact']:
        time.sleep(45); a=json.loads(ATLAS.read_text())
        if a['status']=='FAIL': raise RuntimeError('Independent native atlas decode failed')
        if a['status']=='COMPLETE_SEQUENTIAL_EARLY_WARM_ATLAS_AND_INDEPENDENT_DECODE':
            assert a['independent_decode_exact']
            M.update(status='COMPLETE_EXACT_WARM_WORD_COST_DIAGNOSTIC',atlas_independent_decode_exact=True,
                     verified_atlas_manifest_sha256=sha(ATLAS),qualification_finished=time.time()); save()
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc(),finished=time.time()); save(); raise
