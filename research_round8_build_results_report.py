from pathlib import Path
import collections,datetime,hashlib,json
import numpy as np
R=Path(__file__).resolve().parent
def read(name):return json.loads((R/name).read_text(encoding='utf-8'))
conditional=read('research_round8_conditional_manifest.json');paid=read('research_round8_paid_schedule_manifest.json');fixed=read('research_round8_fixed_semantic_manifest.json');directed=read('research_round8_directed_memory_manifest.json');continuous=read('research_round8_continuous_manifest.json');warm=read('research_round8_warm_source_manifest.json');weight=read('research_round8_weight_partition_manifest.json')
def full(m):return [r for r in m['results'] if r.get('raw_bytes',r.get('input_bytes'))==2000000]
cs=full(conditional);ps=full(paid);fs=[r for r in fixed['results'] if r['slice'].endswith('_2m')];assert len(cs)==len(ps)==len(fs)==4
def sums(rows,key,value):
 out=collections.defaultdict(float)
 for r in rows:
  for a in r[key]:out[a['name']]+=a[value]
 return dict(out)
cn=sums(cs,'arms','saving_bytes');pn=sums(ps,'programs','saving_bytes_including_mode');fn=sums(fs,'arms','saving_bytes')
baseline=0
for s in 'abcd':baseline+=float(np.fromfile(R/f'research_round7_lex_{s}_2m_cost.f32',dtype='<f4').astype(np.float64).sum())/8
assert baseline>0
summary={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'session':355655943,'status':'REGISTERED_ROUND8_BATCH_COMPLETE_OVERALL_RESEARCH_OPEN','qualifying_package_result':False,'twenty_percent_achieved':False,'all_ideas_fully_explored':False,'core_transformer_retrained':False,'statistical_coefficients_fitted':True,'paid_rental_usd':0,'deletions':[],'conditional_8m_byte_equivalents':cn,'paid_program_8m_bytes_after_policy_duration_mode_only':pn,'fixed_continuous_8m_byte_equivalents':fn,'approx_native_8m_payload_byte_equivalents_from_f32_cost':baseline,'semantic_fixed_sample_payload_improvement_percent':100*fn['semantic_last_content']/baseline,'sparse_graph':fixed['sparse_graph'],'directed_warm_source_cold_core_512k':[{k:r[k] for k in ['name','development_q16_saving_bytes','confirmation_q16_saving_bytes','supporting_plane_gap_bytes','development_after_two_coefficient_copies_and_3bit_selector_bytes']} for r in directed['results']],'weight_partition_gain_same_overhead_bytes_per_copy':weight['summary']['partition_gain_over_homogeneous_bits']/8,'full_published_peak_bytes':9765024*1024,'conservative_10gb_headroom_bytes':10_000_000_000-9765024*1024,'manifest_hashes':[]}
files=['research_round8_conditional_manifest.json','research_round8_paid_schedule_manifest.json','research_round8_weight_partition_manifest.json','research_round8_clean_title_v4_manifest.json','research_round8_warm_source_manifest.json','research_round8_semantic_graph_manifest.json','research_round8_semantic_replay_manifest.json','research_round8_continuous_manifest.json','research_round8_fixed_semantic_manifest.json','research_round8_directed_memory_manifest.json']
for name in files:summary['manifest_hashes'].append({'file':name,'sha256':hashlib.sha256((R/name).read_bytes()).hexdigest()})
(R/'research_round8_final_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
parts=['\n## 14. Final measured batch ledger\n\n',f"Generated {summary['updated_utc']}. All registered jobs in this batch completed; the overall research and all 95 families remain open. No qualifying archive or 20% gain. Figures below are likelihood-derived integer-prediction byte equivalents except where an explicit finite side-code or diagnostic description is stated.\n\n"]
parts+=['| Joint gate, ABCD2M (8M) | Gain before module/assets/framing, bytes |\n|---|---:|\n']
for name,gain in cn.items():parts.append(f'| {name} | {gain:.9f} |\n')
parts+=['\n| Paid policy programs, ABCD2M | Gain after policy/duration/mode only, bytes |\n|---|---:|\n']
for name,gain in pn.items():parts.append(f'| {name} | {gain:.9f} |\n')
parts+=['\n| Frozen AB128K continuous head, full ABCD2M | Integer prediction gain before assets, bytes |\n|---|---:|\n']
for name,gain in fn.items():parts.append(f'| {name} | {gain:.9f} |\n')
parts.append(f"\nThe semantic last-content head is positive on all four full slices. The approximate native cold-sample likelihood cost from the existing float32 cost arrays is {baseline:,.3f} byte equivalents. Its {fn['semantic_last_content']:.6f}-byte gain is approximately **{summary['semantic_fixed_sample_payload_improvement_percent']:.6f}%** of that sample cost. This is neither an archive measurement nor a full production extrapolation. The full graph is 613,724 LZMA bytes per copy before framing, requiring 1,227,448 bytes for two copies; the measured signal does not justify it.\n\n")
sp=fixed['sparse_graph'];parts.append(f"The exact finite source-row subset selects {sp['combined_selected_source_count']} rows on combined ABCD. Its best priced result is {sp['combined_ABCD_best_bytes']:.9f} bytes before loader, so ordinary native mode wins. Maximum combined marginal for any source is {sp['maximum_combined_marginal_bytes']:.9f} byte versus 36 bytes charged per selected row. The independent subset enumeration passes. This rejects that specific row format/frozen head at this scale; it does not bound compressed factors or all retention mechanisms.\n\n")
parts+=['| Directed source warm, native core cold; AB fit, CD frozen test | AB128K+128K gain | CD128K+128K gain | AB after two coefficient copies and selector | Certificate gap (bytes) |\n|---|---:|---:|---:|---:|\n']
for row in directed['results']:parts.append(f"| {row['name']} | {row['development_q16_saving_bytes']:.6f} | {row['confirmation_q16_saving_bytes']:.6f} | {row['development_after_two_coefficient_copies_and_3bit_selector_bytes']:.6f} | {row['supporting_plane_gap_bytes']:.9f} |\n")
parts.append("\nNext-content associations have a small positive controlled signal; widening to eight-content co-occurrence does not improve it here. These parameters are fitted statistical models with a frozen original transformer. Full warmed-core and actual code costs remain required. The independent source tests pass; instrumented association arrays occupy 106,496 bytes, while 69,632 bytes is a packed-layout design estimate. No graph or current-word target is supplied to the predictor.\n\n")
parts+=['| Research execution phase | CPU user seconds | Peak RSS KiB |\n|---|---:|---:|\n']
for name,rows in [('conditional all4arms',cs),('paid all5programs',ps),('fixed all6heads',fs)]:
 for row in rows:
  ac=row['accounting'];parts.append(f"| {name} {row['slice']} | {ac['user_seconds']:.6f} | {ac['max_rss_kbytes']} |\n")
for name,ac in [('title/retrieval warm-source',warm['runtime']),('directed warm-source/export',directed['warm_export_runtime'])]:parts.append(f"| {name} | {ac['user_seconds']:.6f} | {ac['max_rss_kbytes']} |\n")
parts.append(f"\nContinuous fit/evaluate wall time: {continuous['fit_evaluate_wall_seconds']:.6f}s. Directed fit/evaluate wall time: {directed['fit_evaluate_wall_seconds']:.6f}s. Those in-process fitting phases do not have separate wait4 user/RSS accounting; do not reuse exporter-only RSS as their measurement. Research binaries include instrumentation, duplicate source structures and traces; their size/peak is not the compact native incremental cost. Actual native package, Geekbench-normalized time and full peak gates are unexecuted.\n\n")
parts.append("Authoritative compact machine-readable results: [research_round8_final_summary.json](research_round8_final_summary.json). Sources, individual controls, coefficients, prediction hashes and failure traces remain in their corresponding manifests and evidence bundle. No dataset/model deletion or paid expense. The $70 training plan remains staged and unexecuted.\n")
p=R/'research_round8_report.md';s=p.read_text(encoding='utf-8').split('<!-- generated-round8-results -->')[0];p.write_text(s+'<!-- generated-round8-results -->\n'+''.join(parts),encoding='utf-8')
print(json.dumps({'conditional':cn,'paid':pn,'fixed':fn,'sample_percent':summary['semantic_fixed_sample_payload_improvement_percent'],'sparse_bytes':sp['combined_ABCD_best_bytes'],'status':summary['status']}))
