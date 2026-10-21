import datetime,hashlib,json,pathlib
R=pathlib.Path('.');E=R/'research_round7_completed_20261005T1912';N=R/'research_round7_native_calibration_20261005'
load=lambda p:json.loads(p.read_text())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
names='abcd';ex=[load(E/'remaining_experts_v1'/(n+'_2m.json')) for n in names];root=[load(E/'root_eof_v3'/(n+'.json')) for n in names]
numeric=load(E/'numeric_programs_v2/results.json');tiny=load(E/'tiny_residual_v1/results.json');macro=load(E/'macro_packets_v1/results.json')
manifest=load(N/'manifest.json');native=load(N/'results.json');assert manifest['status']=='COMPLETE_64K_NATIVE' and len(native)==2
for x in load(E/'index.json'):
 b=(E/x['path']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],x['path']
groups={}
for x in load(E/'exact_prior_transforms_v1/manifest.json')['rows']:
 assert x['exact_roundtrip'];k=x['transform']+'/'+x['codec'];g=groups.setdefault(k,{'packed_bytes':0,'raw_bytes':0,'decode_seconds':0})
 g['packed_bytes']+=x['compressed_bytes'];g['raw_bytes']+=x['raw_bytes'];g['decode_seconds']+=x['decode_and_inverse_seconds']
for g in groups.values():g.update(ratio=g['packed_bytes']/g['raw_bytes'],decode_MB_s=g['raw_bytes']/g['decode_seconds']/1e6,projected_full_bytes_not_guaranteed=g['packed_bytes']/g['raw_bytes']*240448198200)
numrows=numeric if isinstance(numeric,list) else numeric.get('results',numeric.get('rows',[]))
record={'utc':now,'session':355529591,'status':'FINITE_REGISTERED_BATCH_COMPLETE_NO_QUALIFYING_BREAKTHROUGH','expert_ABCD_saving_bytes':[x['mixture_saving_bytes'] for x in ex],
 'expert_total_saving_bytes':sum(x['mixture_saving_bytes'] for x in ex),'root_ABCD_saving_bytes':[x['score']['prequential_saving_bytes'] for x in root],
 'root_total_saving_bytes':sum(x['score']['prequential_saving_bytes'] for x in root),'tiny_residual_screen':tiny,'native_confirmation':native,
 'prior_codec_groups':groups,'full_inverse':load(E/'full_inverse_v2/manifest.json'),'paid_usd':0,'manual_project_deletions':[],
 'full_original_transformer_training':'NOT_EXECUTED','production_lexical_full_stream':'NOT_REGENERATED','full_exact_training_priors':'NOT_REGENERATED',
 'full_qualifying_package':'NOT_BUILT_OR_MEASURED','absolute_optimum_proved':False,'over_20_percent_improvement':False,'goal':'usageLimited; not resumed or mutated'}
(R/'research_round7_final_batch_summary.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
lines=['## Completed measured batch','',f'Finalized {now}; Kaggle session355529591. Positive values mean savings. All quantities below are bytes, not percentages of enwik9 unless explicitly stated.','',
'| Final-coder screen | A (2M) | B (2M) | C (2M) | D (2M) | Total |',
'|---|---:|---:|---:|---:|---:|']
for title,vals in [('Shared causal experts (actual uint16)',record['expert_ABCD_saving_bytes']),('Corrected root/new-mention (ideal event likelihood)',record['root_ABCD_saving_bytes']),('A/B-fitted 512B integer calibration (ridge64)',[x['saving_bytes'] for x in tiny['arms'][0]['slices']])]:
 lines.append('| '+title+' | '+' | '.join(f'{v:+.6f}' for v in vals+[sum(vals)])+' |')
lines+=['','Shared experts:3393.031207CPU user seconds for four2M screens, peak96,700KiB. Their best fixed non-identity arm is the mildly negative anagram correction in every slice, and it still loses2.219/5.580/6.499/8.560B. Positive online mixture results do not establish a profitable packaged expert. Root/new-mention fixed non-neutral arms also all lose. Root wall time is'+f"{sum(x['wall_seconds'] for x in root):.3f}"+'s; independent process CPU and peak RSS were not captured for that screen and are not invented. Its bounded graph capacities are4096rows/262144edges per graph. Neither prototype is promoted.',
'','Finite numeric programs lose0.498887388ideal bytes in aggregate over8M; every fixed numeric arm loses. The four frozen template packets reconstruct raw bytes exactly but are larger than matched generic-codec baselines: zlib9 +4.10/+5.54/+5.30/+4.88%; LZMA6 +5.75/+4.69/+4.48/+4.05%. Even the relaxed native covered-cost minus two pool copies is negative on all four. No native macro result is claimed.',
'','### Native confirmation on fresh E/F',
'','| Slice | Input bytes | Actual archive saving | Ideal saving | Candidate CPU s | Decode CPU s | Decode peak RSS KiB |',
'|---|---:|---:|---:|---:|---:|---:|']
for x in native:
 t=x['runtime'];c=t['candidate'].get('user_seconds');d=t['decode'];lines.append(f"| {x['slice'].upper()} | {x['input_bytes']} | {x['native_archive_saving_bytes']:+d} | {x['ideal_saving_bytes']:+.6f} | {c if c is not None else 'not captured; reused E'} | {d['user_seconds']:.6f} | {d['max_rss_kbytes']} |")
lines+=['','Neutral candidate/reference archive and every final probability match exactly; all candidate integers match independent rational replay; both independent raw decodes reconstruct the exact inputs. The A/B table was frozen before E/F. Fresh confirmation does not justify promotion: small old-region likelihood gains are not a significant archive improvement. Model cost is512B per stored copy, two copies in the current package; the laboratory wrapper adds1016executable bytes before final packing and option overhead. No full-package net saving is measured. The original transformer weights were never changed. E compression timings were lost when v3 failed before persisting its row; v4 reused these completed outputs and reports the timing as unavailable rather than repeating them.',
'','### Training-data storage and provenance',
'','Old-FX2 preparation and inverse are complete:586,459,020transformed bytes invert to all1,000,000,000original bytes with SHA256159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc. This is a preprocessing roundtrip; there is no full entropy-coded qualifying candidate. Preparation CPU568.392895s/RSS7,120,448KiB; inverse CPU245.599285s/RSS1,515,868KiB.',
'','The262144-row native-prior probe takes4.043254CPU seconds/RSS1,136,116KiB and yields107,479,040B of genuine float16 priors. Raw Zstandard9 stores50,901,611B (47.35957% of raw), with four-block in-memory decode0.285259s. All48 tested representation/codec cases round-trip exactly. LZMA3 is smaller but slower. Full Zstandard9 storage extrapolates113.875GB if the early-sample ratio holds; this is not a capacity guarantee. No full priors or production lexical-order data have been prepared. Training-data storage reductions are excluded from submitted archive improvements.',
'','### Concrete continuation and remaining work',
'','Read `research_round7_finetuning_execution_plan.md` and `research_round7_training_contract.json`. The plan contains exact data shifts, legal-piece sampling, loader read-amplification controls, native/GPU layer parity, F0 load/export identity, conservative32-update F1 screens, two-copy MDL units, conditional F2–F5arms, optimizer/checkpoint schedules, token-throughput pricing, strict CPU/RAM/disk accounting and the$4/$12/$36/$8/$10budget caps. No GPU rental, neural training or expense has occurred.',
'','The finite registered bounded batch is complete. P01 full production package/reference validation remains gated; P03 larger suffix/word-head/native improvements are unimplemented beyond the measured calibration arm; P05 production lexical full stream and complete exact priors remain pending. Full learned hazard/counterfactual TTL, link-key retrieval, pair-HMM/geometry architectures and bidirectional two-pass neural training are hypotheses, not completed experiments. Their narrower screens are described explicitly. The numerical neural parity gate still fails, so the first recommended work is fidelity repair and F0/F1, not a long paid run.',
'','Evidence: `research_round7_completed_20261005T1912.zip` (SHA256d4c2ade0be91480c3620049dc4cfea905b8259a6a1cdeebd7db39ea46e1ef3cf), its hash-checked40-file index, `research_round7_native_calibration_20261005` and `research_round7_final_batch_summary.json`. Exclusive launch directories and failed attempts are preserved. No manual project deletion or managed Goal mutation. Signed session credentials remain outside reports.']
section='\n'.join(lines)+'\n'
p=R/'research_round7_remaining_experiments_report.md';s=p.read_text(encoding='utf8');a=s.index('<!-- GENERATED_RESULTS_START -->');b=s.index('<!-- GENERATED_RESULTS_END -->',a)+len('<!-- GENERATED_RESULTS_END -->');s=s[:a]+'<!-- GENERATED_RESULTS_START -->\n'+section+'<!-- GENERATED_RESULTS_END -->'+s[b:];s=s.replace("This report accompanies the user's explicit5October continuation. Updated result tables and final statuses are inserted below when preserved outputs complete.","This report accompanies the user's explicit5October continuation. The finite registered bounded batch is complete; final result tables and scope limits are below.");p.write_text(s,encoding='utf8')
banner=f"""<!-- round7-final-20261005-start -->
# Current handoff — 6 October 2026 IST

Updated {now}. Session355529591, kernel a5c194c1-af88-49ea-8809-a66b8fb074d7.
FINITE REGISTERED BOUNDED BATCH COMPLETE. No experiment from this batch remains
running. No qualifying package, absolute optimum or20% improvement. No paid
rental, original-transformer training, manual project deletion or Goal mutation.

Shared title retrieval, syntax/source-surprise, exact/random/geometry/phonetic
memory, TTL and constructor-run experts: +1.731295ideal bytes/8M total.
Corrected root/new-mention/EOF: +41.891326ideal bytes/8M. Numeric programs:
-0.498887B/8M. Frozen numeric-template packets: all four larger despite exact
roundtrips. A/B-fitted512B calibration: +148.167866ideal bytes/8M, but fresh
native E/F give {native[0]['native_archive_saving_bytes']:+d}/{native[1]['native_archive_saving_bytes']:+d}actual archive bytes; no promotion. Neutral archives,
all integer replay and both independent raw decodes pass. Full old-FX2 transform
inverse reconstructs all1B bytes/hash exactly. This is not full entropy coding.

Current authoritative reports: research_round7_remaining_experiments_report.md,
research_round7_finetuning_execution_plan.md, research_round7_training_contract.json
and research_round7_final_batch_summary.json. Compact outputs/hashes are under
research_round7_completed_20261005T1912 and research_round7_native_calibration_20261005.
Inspect manifests before any continuation; never relaunch completed directories.
Credentials stay in conversation/runtime only.

Still gated/unexecuted: full production lexical preprocessing/priors; native/GPU
neural parity repair (existing gate FAILED); F0/F1training controls; trained
lexical head or full learned hazard; production package and qualifying CPU/RAM
validation. Full learned proposals are not represented as completed by their
bounded screens. The$70plan is staged4/12/36/8/10USD; spent0USD.

Managed Goal remains usageLimited and has not been resumed. This batch follows
the latest explicit human continuation; heartbeats must not bypass that limit.
The week research objective remains unachieved. Earlier entries below are
historical and superseded by this current handoff.
<!-- round7-final-20261005-end -->

"""
for name in ['research_round7_checkpoint.md','research_round7_pre_experiment_report.md']:
 p=R/name;s=p.read_text(encoding='utf8');a=s.find('<!-- round7-final-20261005-start -->')
 if a>=0:
  b=s.index('<!-- round7-final-20261005-end -->',a)+len('<!-- round7-final-20261005-end -->');s=s[:a]+s[b:].lstrip('\n')
 p.write_text(banner+s,encoding='utf8')
p=R/'research_round7_report.md';s=p.read_text(encoding='utf8');tag='<!-- final-batch-20261005-start -->';a=s.find(tag)
if a>=0:s=s[:a]
p.write_text(s.rstrip()+'\n\n'+tag+'\n'+section+'<!-- final-batch-20261005-end -->\n',encoding='utf8')
p=R/'research_round7_training.md';s=p.read_text(encoding='utf8');note='<!-- training-plan-current-20261005 -->\nCurrent detailed execution plan: `research_round7_finetuning_execution_plan.md`;\nmachine-readable contract: `research_round7_training_contract.json`. The bounded\nno-retraining batch has completed, with no qualifying gain. Old-FX2 inverse and\nlossless prior-storage probes pass; full lexical data/priors and neural parity\nstill gate training. Spent$0; staged total$70. Earlier plan material below is\nhistorical where it conflicts with the current contract.\n\n'
if not s.startswith('<!-- training-plan-current-20261005 -->'):p.write_text(note+s,encoding='utf8')
p=R/'research_round7_training_contract.json';j=load(p);j['data_contract']['older_fx2_inverse']='PASS_FULL_1B_SHA256';j['data_contract']['exact_prior_probe']={'rows':262144,'raw_bytes':107479040,'raw_zstd9_bytes':50901611,'all_48_exact_roundtrips':True,'whole_stream_ratio_not_guaranteed':True};j['completed_no_retraining_batch']='research_round7_final_batch_summary.json';j['native_calibration_confirmation']='NO_PROMOTION';j['control_training']['winner_schedule']='N=floor(3600*affordable_hours*measured_useful_targets_per_second/2^20); screened LR first80%, cosine to0.1LR final20%; checkpoint<=32updates/30min';p.write_text(json.dumps(j,indent=2)+'\n',encoding='utf8')
print(json.dumps({'updated':now,'status':record['status'],'native':[(x['slice'],x['native_archive_saving_bytes']) for x in native],'evidence_files_verified':40}))
