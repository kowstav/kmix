from pathlib import Path
import gzip,json,hashlib,time,zipfile
W=Path('/kaggle/working/hp_round14');d=W/'word_costs_v2';m=json.loads((d/'manifest.json').read_text());assert m['status']=='COMPLETE_16_WARM_WORD_COST_REGIONS'
out={'scope':m['scope'],'regions':16,'categories':{},'thresholds':{},'words':{},'total_native_bits':0.}
for p in sorted(d.glob('region_*.json')):
    r=json.loads(p.read_text());out['total_native_bits']+=r['native_bits']
    for dest,src in [('categories','categories'),('thresholds','rarity_thresholds')]:
        for name,counts in r[src].items():
            o=out[dest].setdefault(name,{'events':0,'coded_bytes':0,'native_bits':0.})
            for k,v in counts.items():o[k]+=v
    f=d/f"region_{r['index']:02}_words.tsv.gz";assert hashlib.sha256(f.read_bytes()).hexdigest()==r['words_file_sha256']
    with gzip.open(f,'rt') as h:
        next(h)
        for line in h:
            word,n,b,bits,freq=line.rstrip().split('\t');s=out['words'].setdefault(word,{'word':word,'events':0,'coded_bytes':0,'native_bits':0.,'corpus_count':int(freq)})
            s['events']+=int(n);s['coded_bytes']+=int(b);s['native_bits']+=float(bits)
assert abs(sum(v['native_bits'] for v in out['categories'].values())-out['total_native_bits'])<1e-3
words=out.pop('words');out['word_types']=len(words);out['top_total']=sorted(words.values(),key=lambda r:-r['native_bits'])[:30]
out['top_mean_min32']=sorted([r for r in words.values() if r['events']>=32],key=lambda r:-r['native_bits']/r['events'])[:30]
out['CPU_seconds']=sum(s['worker_CPU_seconds']+s['parser_CPU_seconds'] for s in m['shards']);out['wall_seconds']=m['finished']-m['started']
(W/'word_cost_summary_v2.json').write_text(json.dumps(out,indent=2))
zpath=W/'word_costs_v2_compact.zip';entries=[]
assert not zpath.exists()
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
    for p in sorted(d.iterdir()):
        if p.is_file():
            n=p.name;z.write(p,n);entries.append({'path':n,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    z.writestr('entries.json',json.dumps(entries,indent=2))
out['compact']={'path':str(zpath),'bytes':zpath.stat().st_size,'sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'entries':len(entries)}
(W/'word_cost_summary_v2.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
