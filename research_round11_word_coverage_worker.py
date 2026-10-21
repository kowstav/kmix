"""Full-source first-appearance and constructor-run census with exact framing.

All frequency/appearance results are offline diagnostics, never free model inputs.
Reports strict ASCII casefold versus the previous Unicode-lower-before-regex
tokenizer explicitly. Future frequency tables are research assets only.
"""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import json
import math
import os
import re
import resource
import time
import traceback
import zipfile
import xml.etree.ElementTree as ET
from hutter_research.constructor_codec import WORDS

W=Path('/kaggle/working/hp_round11/word_coverage_v1')
assert not W.exists(), 'Inspect existing census rather than duplicate'
W.mkdir(parents=True)
Z=Path('/kaggle/working/hp_round7/preserved/data/enwik9.zip')
RX=re.compile(rb"[A-Za-z]+(?:'[A-Za-z]+)*")
OLD_RX=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*")
CTOR={word.encode():i for i,word in enumerate(WORDS)}
CHECKS=[int(f*1000000000) for f in [.001,.0025,.005,.01,.02,.05,.10,.20,.30,.40,.50,.60,.70,.80,.90,.95,.99,1.]]
M={'status':'RUNNING_WORD_APPEARANCE_CONSTRUCTOR_CENSUS','started':time.time(),'pid':os.getpid(),
   'deletions':[],'paid_usd':0,'GPU':False,'scope':'complete XML revision/text pages; strict ASCII byte regex, then ASCII casefold',
   'limits':'Raw physical-order corpus diagnostics; not canonical WRT coding order, bit shares or inference savings.',
   'lexicon':list(WORDS),'coverage':[],'tokenizer_difference_pages':0,'previous_tokenizer_total_tokens':0}

def save(): (W/'manifest.json').write_text(json.dumps(M,indent=2))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1<<20): h.update(b)
    return h.hexdigest()

try:
    save(); counts=Counter(); df=Counter(); first={}; sequences=Counter(); bags=Counter(); sets=Counter()
    ctor_occurrences=0; tokens=0; pagecount=0; nonempty=0; check=0; permutation_bits=0.
    member_hash=hashlib.sha256(); read=0; buf=b''; base=0; max_run=0
    with zipfile.ZipFile(Z) as archive:
        infos=[v for v in archive.infolist() if v.file_size==1000000000]; assert len(infos)==1
        with archive.open(infos[0]) as stream:
            while chunk:=stream.read(1<<20):
                member_hash.update(chunk); read+=len(chunk); buf+=chunk
                while True:
                    start=buf.find(b'<page>')
                    if start<0:
                        drop=max(0,len(buf)-16); base+=drop; buf=buf[drop:]; break
                    end=buf.find(b'</page>',start)
                    if end<0:
                        base+=start; buf=buf[start:]; break
                    abs_start,abs_end=base+start,base+end+7
                    data=buf[start:end+7]; consume=end+7; buf=buf[consume:]; base+=consume
                    page=ET.fromstring(data); element=page.find('./revision/text')
                    text=element.text or '' if element is not None else ''
                    word_list=[w.lower() for w in RX.findall(text.encode('utf-8'))]
                    current=Counter(word_list); old=Counter(w.encode() for w in OLD_RX.findall(text.lower()))
                    M['previous_tokenizer_total_tokens']+=sum(old.values())
                    M['tokenizer_difference_pages']+=int(current!=old)
                    before=len(counts); prior_tokens=tokens
                    for word in current:
                        if word not in first: first[word]=(abs_start,abs_end)
                    counts.update(current); df.update(current.keys()); tokens+=len(word_list)
                    pagecount+=1; nonempty+=bool(word_list)
                    while check<len(CHECKS) and CHECKS[check]<=abs_end:
                        cut=CHECKS[check]; exact_end=cut==abs_end; before_page=cut<=abs_start
                        M['coverage'].append({'raw_byte_cutoff':cut,'types_definitely_completed':len(counts) if exact_end else before,
                           'types_including_boundary_page':before if before_page else len(counts),'tokens_definitely_completed':tokens if exact_end else prior_tokens,
                           'boundary_page_start':abs_start,'boundary_page_end':abs_end})
                        check+=1
                    run=[]
                    def finish_run():
                        global permutation_bits,max_run
                        if not run: return
                        tup=tuple(run); counter=Counter(run); bag=tuple(sorted(counter.items()))
                        sequences[tup]+=1; bags[bag]+=1; sets[tuple(sorted(counter))]+=1
                        max_run=max(max_run,len(run))
                        permutation_bits+=(math.lgamma(len(run)+1)-sum(math.lgamma(c+1) for c in counter.values()))/math.log(2)
                        run.clear()
                    for word in word_list:
                        idx=CTOR.get(word)
                        if idx is not None: run.append(idx); ctor_occurrences+=1
                        else: finish_run()
                    finish_run()
                    if pagecount%20000==0:
                        M.update(pages=pagecount,tokens=tokens,distinct_types=len(counts),raw_bytes_read=read); save()
                assert len(buf)<128*1024*1024
    assert read==1000000000 and member_hash.hexdigest()=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
    while check<len(CHECKS):
        M['coverage'].append({'raw_byte_cutoff':CHECKS[check],'types_definitely_completed':len(counts),
                             'types_including_boundary_page':len(counts),'tokens_definitely_completed':tokens,
                             'incomplete_terminal_page_excluded':True}); check+=1
    for row in M['coverage']:
        row['type_coverage_lower']=row['types_definitely_completed']/len(counts)
        row['type_coverage_upper']=row['types_including_boundary_page']/len(counts)
    freq=W/'strict_ascii_first_appearance.tsv.gz'
    with gzip.open(freq,'wt',encoding='ascii',newline='') as f:
        f.write('word\tcorpus_count\tcontaining_articles\tfirst_page_start\tfirst_page_end\n')
        for word,count in sorted(counts.items()):
            lo,hi=first[word]; f.write(f'{word.decode()}\t{count}\t{df[word]}\t{lo}\t{hi}\n')
    def describe(hist):
        occurrences=sum(hist.values())
        entropy=-sum(n*math.log2(n/occurrences) for n in hist.values()) if occurrences else 0.
        return {'distinct_patterns':len(hist),'run_occurrences':occurrences,'empirical_code_bits_before_dictionary_price':entropy,
                'qualification':'same-data plug-in descriptive entropy; no achieved compressed size or free pattern dictionary'}
    M.update(status='COMPLETE_WORD_APPEARANCE_CONSTRUCTOR_CENSUS',finished=time.time(),
             original_sha256=member_hash.hexdigest(),original_bytes=read,complete_pages=pagecount,nonempty_pages=nonempty,
             incomplete_terminal_page_bytes=len(buf) if b'<page>' in buf else 0,total_tokens=tokens,distinct_types=len(counts),
             constructor_occurrences=ctor_occurrences,constructor_occurrence_fraction=ctor_occurrences/tokens,
             constructor_ordered_runs=describe(sequences),constructor_bags=describe(bags),constructor_sets=describe(sets),
             constructor_max_run=max_run,paid_bag_uniform_order_ideal_bits=permutation_bits,
             frequency_table={'bytes':freq.stat().st_size,'sha256':sha(freq),'remote':str(freq),'deployment_asset':False},
             process_CPU_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,
             process_peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    save()
except BaseException as error:
    M.update(status='FAIL',error=repr(error),traceback=traceback.format_exc(),finished=time.time()); save(); raise
