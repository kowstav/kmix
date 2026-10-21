import datetime,json,re
from pathlib import Path
R=Path(__file__).parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(name):
 p=R/name;return json.loads(p.read_text()) if p.exists() else None
atom=read('research_round8_canonical_atom_fit_results.json');error=read('research_round8_canonical_error_memory_results.json');role=read('research_round8_canonical_role_residual_results.json');atlas=read('research_round8_canonical_cost_atlas_summary.json');stage=read('research_round8_native_stage_trace_results.json');fit=read('research_round8_native_stage_fit_results.json') or read('research_round8_native_stage_fit_v2_progress.json');census=read('research_round8_rarity_census_results.json') or read('research_round8_rarity_census_progress.json')
weak=read('research_round8_native_stage_weak_confirmation_results.json') or read('research_round8_native_stage_weak_confirmation_progress.json')
inline=read('research_round8_native_inline_residual_results.json') or read('research_round8_native_inline_residual_progress.json')
wide=read('research_round8_source_wide_box_results.json') or read('research_round8_source_wide_box_progress.json')
ef=read('research_round8_source_wide_confirmation_results.json') or read('research_round8_source_wide_confirmation_progress.json')
wi=read('research_round8_native_inline_wide_results.json') or read('research_round8_native_inline_wide_progress.json')
mask=read('research_round8_rarity_residual_pilot_results.json') or read('research_round8_rarity_residual_pilot_progress.json')
timing=read('research_round8_residual_throughput_results.json')
assert atom and error and role and stage
assert len(atom['results'])==11 and len(error['results'])==24 and len(role['development_policy_gains_bytes'])==27
assert all(v['ideal_box_optimum_certified'] for m in [atom,error] for v in m['results'])
fit_complete=bool(fit and fit['status']=='COMPLETE_NATIVE_STAGE_FINITE_FIT');fit_n=len(fit['results']) if fit else 0
count=86+(fit_n if fit_complete else 0)+(1 if wide and wide['status']=='COMPLETE_WIDER_SOURCE_FINITE_BOX' else 0)
summary={'updated':now,'session':355735431,'status':'ONGOING_ALL_96_CURRENT_FAMILIES_OPEN','historical_families':95,'new_explicit_family':'A96 rarity masking/gradient allocation','current_families':96,'attachment_proposals_mapped_to_families':6,'certified_native_fitted_heads_completed':count,'role_online_policies_completed':27,'stage_source_fit':{'status':fit['status'] if fit else 'UNKNOWN','directory':'native_stage_fit_v2','historical_launch_pid':1185,'fitted_heads_so_far':fit_n,'all_expected_heads':31,'complete':fit_complete,'best_priced_AB_bytes':fit.get('best_priced_AB_bytes') if fit else None,'advance_gate_pass':fit.get('advance_gate_pass') if fit else None,'result_file':'research_round8_native_stage_fit_results.json' if fit_complete else 'research_round8_native_stage_fit_v2_progress.json'},'stage_observer':{'status':stage['status'],'controls':2,'exports':2,'full_AB_archive_and_Q16_identity':all(v['archive_identity'] and v['Q16_identity'] for v in stage['exports']),'independent_32K_decodes':all(v['independent_decode_exact'] for v in stage['controls'])},'rarity_census':{'status':census['status'] if census else 'UNKNOWN','historical_launch_pid':1192,'directory':'rarity_census_v1','training_evaluated':False},'canonical_atom_screen':{'heads':11,'best_priced_AB_bytes':atom['best_priced_AB_bytes'],'advance_gate_pass':False},'paired_error_memory_screen':{'heads':24,'best_priced_AB_bytes':error['best_priced_AB_bytes'],'advance_gate_pass':False},'role_online_screen':{'policies':27,'best_raw_AB_bytes':max(role['development_policy_gains_bytes']),'best_priced_AB_bytes':role['best_development_after_5bit_selector_bytes'],'advance_gate_pass':False},'atlas_complete':True,'full_native_qualifying_candidate':False,'twenty_percent_achieved':False,'absolute_optimum_claimed':False,'all_96_fully_explored':False,'paid_spending_usd':0,'budget_usd':70,'deletions':[],'managed_goal_status':'usageLimited_DO_NOT_RESUME_OR_REPLACE','week_end':'2026-10-11','new_user_answers_and_training_plan':'research_round8_5090_hours_and_rarity_plan.md','rarity_protocol':'research_round8_rarity_mask_protocol.md'}
(R/'research_round8_session355735431_extension_status.json').write_text(json.dumps(summary,indent=2))
summary['weak_source_confirmation']={'directory':'native_stage_weak_confirmation_v1','historical_launch_pid':1208,'status':weak['status'] if weak else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS','result_file':'research_round8_native_stage_weak_confirmation_results.json' if weak and weak['status'].startswith('COMPLETE') else 'research_round8_native_stage_weak_confirmation_progress.json','candidate_frozen':'neural_valid','original_64B_screen_passed':False,'actual_candidate_archive_evaluated':False}
summary['native_inline_residual']={'directory':'native_inline_residual_v1','historical_launch_pid':1235,'status':inline['status'] if inline else 'UNKNOWN','actual_CD_archive_saving_bytes':inline.get('actual_CD_archive_saving_bytes') if inline else None,'matched_lab_binary_delta_bytes':inline.get('binary',{}).get('lab_binary_delta_bytes') if inline else None,'full_qualifying_package':False}
summary['wider_source_fit']={'directory':'source_wide_box_v1','historical_launch_pid':1306,'status':wide['status'] if wide else 'UNKNOWN','development_priced_gain_bytes':wide.get('development_after_two_coefficient_copies_and_6bit_selector_bytes') if wide else None,'coefficients':wide.get('coefficients') if wide else None,'original_source_upper_bound_was_active':True}
summary['fresh_wider_source_confirmation']={'directory':'source_wide_confirmation_v1','historical_launch_pid':1316,'status':ef['status'] if ef else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS','offsets':[190000000,430000000],'refit_allowed':False}
summary['fresh_wider_source_confirmation'].update(Q16_gain_bytes=ef.get('wider_confirmation_Q16_gain_bytes') if ef else None,both_slices_improve=ef.get('wider_both_slices_improve') if ef else None,both_slices_beat_generic=ef.get('wider_both_slices_beat_generic') if ef else None)
summary['native_inline_wider']={'directory':'native_inline_wide_v1','historical_launch_pid':1329,'status':wi['status'] if wi else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS','stage':wi.get('stage') if wi else None,'actual_EF_archive_saving_bytes':wi.get('actual_EF_archive_saving_bytes') if wi else None,'matched_lab_binary_delta_bytes':wi.get('binary',{}).get('lab_binary_delta_bytes') if wi else None,'full_qualifying_package':False,'result_file':'research_round8_native_inline_wide_results.json' if wi and wi['status'].startswith('COMPLETE') else 'research_round8_native_inline_wide_progress.json'}
summary['free_T4_timing']={'status':timing['status'] if timing else 'UNKNOWN','model_parameters_changed':False,'small_residual_pilots_need_paid_5090_hours_now':0}
summary['partial_A96_dictionary_mask_residual_training']={'directory':'rarity_residual_pilot_v1','historical_launch_pid':1400,'status':mask['status'] if mask else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS','stage':mask.get('stage') if mask else None,'core_retraining':False,'original_transformer_gradient_interference_measured':False,'all_word_mask_training_completed':False,'native_candidate_archive_evaluated':False,'result_file':'research_round8_rarity_residual_pilot_results.json' if mask and mask['status'].startswith('COMPLETE') else 'research_round8_rarity_residual_pilot_progress.json'}
(R/'research_round8_session355735431_extension_status.json').write_text(json.dumps(summary,indent=2))
old=R/'research_round8_native_extension_summary.json';historical=R/'research_round8_native_extension_summary_historical_51_heads.json'
if old.exists() and not historical.exists():historical.write_bytes(old.read_bytes())
old.write_text(json.dumps({'status':'SUPERSEDED_BY_CURRENT_AUTHORITATIVE_EXTENSION_STATUS','current_status_file':'research_round8_session355735431_extension_status.json','preserved_historical_51_head_summary':historical.name,**summary},indent=2))
fit_line=(f"COMPLETE31heads; best priced A/B{fit['best_priced_AB_bytes']:.9f}B; advancement{fit['advance_gate_pass']}." if fit_complete else f"{fit['status'] if fit else 'UNKNOWN'}, {fit_n}/31heads completed at last snapshot; actual launchPID1185, verify current process before any continuation.")
census_line=f"{census['status'] if census else 'UNKNOWN'}; launchPID1192; read its manifest, no masking training yet."
weak_line=f"{weak['status'] if weak else 'LAUNCHED'}, launchPID1208; separate preregistered weak-signal branch, original64B gate still fails."
inline_line=f"{inline['status'] if inline else 'UNKNOWN'}; launchPID1235; C/Dactual archive gain{inline.get('actual_CD_archive_saving_bytes') if inline else None}B, lab binary delta768B; full/package qualification open."
wide_line=f"{wide['status'] if wide else 'UNKNOWN'}; launchPID1306; development priced gain{wide.get('development_after_two_coefficient_copies_and_6bit_selector_bytes') if wide else None}B; E/Fstatus{ef['status'] if ef else 'LAUNCHED'}, launchPID1316."
ef_line=f"Fresh E/F frozen wider Q16 gain{ef.get('wider_confirmation_Q16_gain_bytes') if ef else None}B; both improve and beat generic:{bool(ef and ef.get('wider_both_slices_improve') and ef.get('wider_both_slices_beat_generic'))}."
wi_line=f"{wi['status'] if wi else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS'}; launchPID1329; actual E/Farchive gain{wi.get('actual_EF_archive_saving_bytes') if wi else None}B; matched lab binary delta{wi.get('binary',{}).get('lab_binary_delta_bytes') if wi else None}B; full/package qualification open."
mask_line=f"{mask['status'] if mask else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS'}; launchPID1400; partial dictionary-target training of a161parameter residual; original transformer/OOV masking/native qualification open."
note=f'''<!-- canonical-status-start -->
## Current authoritative continuation — {now}

Newest session355735431. Full native stage observation COMPLETE: two32K
independent decode/reference controls, A/B512K archives and all native Q16
probabilities identical. The19source channels are fresh observation-only data;
no original core training was changed. Source-conditioned fitv2: {fit_line}
V1failed before fitting on overlapping2/3byte WRT prefixes; its executed
worker/log/manifest remain preserved. V2tests every dictionary code/proper
prefix, exact earlier integer predictions, and raw-prefix role causality.
Independent weak-source C/D confirmation:{weak_line}
Actual native inline residual:{inline_line}
Wider nested coefficient family:{wide_line}
{ef_line}
Actual wider native coding/decode:{wi_line}

Completed native/cache fitted heads:{count}, plus27constant-time online role
policies. Atom11head screen and paired-error24head screen fail their priced
64B gates. Role policies save at most4.623679192raw bytes on A/B and do not
beat the equal-capacity null/generic controls. No full archive gain follows.
Canonical native cost atlas COMPLETE: constructors12.8477%, other dictionary
53.0499%, literals/control33.4788% of observed A/B ideal native bit cost.
These are heuristic atom classes on cold slices, not an all-grammar bound.

New explicitA96rarity masking/gradient allocation: {census_line}
Partial A96 free-T4 residual experiment:{mask_line}
The recovered historical audit has95families; current ledger96includes this
new proposal. All remainOPEN. Six attachment proposals are mapped, not claimed
as six more completed ideas. The5090hours, short-pilot design and common/rare
interference answer are in research_round8_5090_hours_and_rarity_plan.md.
Two freeT4s are available; many remaining prototypes can run on Kaggle.
Core GPU parity is still unresolved. No paid rental/training has started.

Correct full lexical preparation/inverse PASS:587138826B, SHA
7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce.
Full native entropy archive/resource qualification remainOPEN. Old C3 peak
leaves615424B under decimal10GB. Do not double-count existing KVI8savings.
Parser experts need legal framing/fallback on arbitrary side/tail bytes.
Pending competitor95914051B; strict20%target<=76731240B, not a forecast.
No absolute optimum, best-possible descendants, equivalent LLM research effort
or20%gain is claimed. Budget70/spent0; project/model/data deletionsNONE.
Managed Goal remainsusageLimited; never automatically resume or replace it.
Week ends11October2026. Older status/PID/count entries below are historical.
<!-- canonical-status-end -->

'''
p=R/'research_round7_checkpoint.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- canonical-status-start -->.*?<!-- canonical-status-end -->\s*','',s,flags=re.S);p.write_text(note+s,encoding='utf-8')
handoff=f'''# Current session355735431 handoff

Updated{now}. Current kernel at dispatch:f1943494-319d-462a-b309-cfd2136fc338.
Get the newest authorized signed session link from the conversation; never
persist its credential. Copied historical PIDs are not proof of a live job.

## Completed and running experiments

| Experiment | Current evidence | Next action |
|---|---|---|
| Native51prior finite heads | Initial immutable evidence ZIP and round8report | Reuse; no duplicate launch |
| Canonical atom11heads | research_round8_canonical_atom_fit_results.json | Gate failed; full-warm descendants still open |
| Paired-error24heads | research_round8_canonical_error_memory_results.json | Gate failed; trained/nonlinear family open |
| Constant-time role27policies | research_round8_canonical_role_residual_results.json | Gate failed; actual roles do not win controls |
| Canonical cost atlas | research_round8_canonical_cost_atlas_report.md | Use class costs, not a whole-corpus POS bound |
| Native source observer | research_round8_native_stage_trace_results.json | COMPLETE; reuse staged A/B traces |
| Native source/role31head fit | {fit_line} | Reuse native_stage_fit_v2; do not relaunch |
| Full-corpus rarity censusA96 | {census_line} | Preserve manifest/gzipcounts on completion |
| Frozen weak-source independent C/D | {weak_line} | Reuse live job; preserve C/D manifest; no candidate archive yet |
| Actual native inline narrow head | {inline_line} | Preserve exact C/D512K coding/decode; no full result |
| Widened source coefficient | {wide_line} {ef_line} | Frozen E/Fconfirmation complete; no refit |
| Actual native inline wider head | {wi_line} | Reuse native_inline_wide_v1; inspect manifest/process before launching |
| Partial dictionary-mask residual trainingA96 | {mask_line} | Reuse rarity_residual_pilot_v1; full transformer/OOV/specialist tests still open |
| Shared/separate-head original-transformer trainingA96 | Registered only | Native/GPU parity, all-word span alignment, full-loss evaluation |

Read research_round8_native_stage_fit_protocol.md and itsv2repair addendum.
Exact executed fit worker:research_round8_native_stage_fit_worker_v2.py.
Manifest:hp_round8/native_stage_fit_v2/manifest.json. The21st and later heads
may cost longer than the single-source fits; work independently and back off
when progress is unchanged. Preserve new FAIL outputs before a named repair.
Read research_round8_rarity_mask_protocol.md and executed census worker.
Manifest:hp_round8/rarity_census_v1/manifest.json. Gzipcounts remain remote
until downloaded and hash-checked. Census is neither a training result nor an
archive improvement. Global/article future counts cannot freely gate decode.

Weak confirmation sources:research_round8_native_stage_weak_confirmation_worker.py
and research_round8_native_stage_weak_confirmation_protocol.md, registered before
C/D source generation. Manifest:hp_round8/native_stage_weak_confirmation_v1/manifest.json.
It freezes one positive priced head because full-file amortization differs from
the1MiB screen. Both C/D must improve and beat generic before a newly registered
actual inline-coder test; do not reselect using C/D. Its status:{weak_line}

The narrow inline result is in research_round8_native_inline_residual_results.json:
two zero-mode native32Kidentities and C/D512Kactual coding/independent decoding,
every candidateQ16value equals replay; core hidden traces unchanged. Actual
payload gains64/63B, summed127B; matched lab executable+768B. This is not a
net production package gain and cannot be scaled to the full file.

The old selected coefficient hit its upper bound. The registered wider box
contains that family and yields2.3818512619982752for its source coefficient,
130.478350711Braw A/B,81.728350711Bafter coefficient copies/6bit selector,
certificate.000169690B. It passes its development gate. Fresh E/Fsource and
exactQ16confirmation is complete:worker
research_round8_source_wide_confirmation_worker.py; protocol same base name.
Directory source_wide_confirmation_v1, launchPID1316. It stores only teacher
archives, not a wider candidate archive. Read manifest before any relaunch.
Both fresh pieces pass; Q16 gains109.926712771/43.910941532B sum153.837654303B.
Actual inline-wide candidate coding/decode was registered and launched with
unchanged coefficients:research_round8_native_inline_wide_worker.py/protocol.md,
native_inline_wide_v1,launchPID1329. Status:{wi_line}
Then production/warmed/full package/resource gates remain necessary.

If the registered source fit passes64priced A/B bytes, freeze its coefficients
and head before producing/evaluating conditional C/D source exports. Require
independent Q16 and native coding/decode, actual package and whole CPU/RAM.
If it fails, keep the failure decision; a new amortized weak-signal branch
needs a declared protocol and fresh independent checks. Do not extrapolate
tiny cold gains to a full archive. Original C/D native outputs are preserved,
and their frozen source/candidate outcomes have already been inspected. Do not
claim those same C/D outcomes as fresh validation of a newly selected model.

Training plan:research_round8_attachment_training_addendum.md plus
research_round8_5090_hours_and_rarity_plan.md. Short128/384/1152step ladder,
equal useful-target/compute controls, curve-crossing allowance, independent
all-target score. Native/GPU core parity and zero-update export precede core
finetuning. A small native-feature residual is a separate usable route.
Do not rent before live total-price/throughput/export readiness and dollar caps.

The newly executed partial mask pilot is registered in
research_round8_rarity_residual_pilot_protocol.md; worker same base name.
Status:{mask_line} It preserves every input and masks complete native dictionary
code spans after known page boundaries. Literal/OOV/case/layout targets stay in
the loss. Ten arms/two seeds,128/384/1152steps with locked development selections;
all-bit C/D confirmation follows frozen finalists. Both raw inference parameters
and optimizer resume checkpoints are preserved. This is a frozen-core residual
test, not original transformer finetuning or proof of its gradient interference.
The completed result/limitations are in research_round8_rarity_residual_pilot_report.md.
Direct coverage/compute/current-result answers:research_round8_current_answers_20261006.md.
The next source-adaptation mathematics and implementation protocol is
research_round8_source_adaptive_descendant_protocol.md; it is NOT executed.

## Preservation and failures

Initial research_round8_evidence.zip is immutable. Build a separate native
extension bundle with exact executed sources, compact controls/model/dictionary,
failed logs/manifests, current report/checkpoint and SHA/CRC validation. Large
remote traces are excluded with path/size/SHA/reproduction records, not deleted.
Old atomv1serialization and atlasv1–v3numerics failures are in their preserved
logs. The stage-fitv1parser failure happened before any fitted head; v2repairs
the overlapping two/three-byte prefix contract without repeating core exports.

No project data/models/files deleted; only a verified dead-parent waiting
controller was previously stopped. Spending0; budget70. Managed Goal stays
usageLimited and must not be resumed/replaced/bypassed by heartbeats. All96
current families remainOPEN; no20%result or absolute optimum. End11October2026.
'''
(R/'research_round8_session355735431_handoff.md').write_text(handoff,encoding='utf-8')
program=read('research_round8_idea_program.json');program.update(date=now,session=355735431,entry_count=96,historical_entry_count=95,latest_extension='research_round8_session355735431_extension_status.json')
if not any(e['id']=='A96' for e in program['entries']):program['entries'].append({'id':'A96','title':'Rarity thresholds, masked losses, gradient allocation and common/rare specialists','route':'T','priority':0,'combination_partners':['A15','A83','A85'],'formal_contracts':['R','C','N','S'],'stronger_descendant':'Keep exact rare context, separate common/rare training gradients and use a normalized expert law with native fallback; charge any decoder frequency lookup.','discriminating_test':'Corpus/article threshold census, masked/soft-weight/unweighted controls, shared-gradient versus frozen-backbone/separate-head controls, all-word native bit cost.','historical_evidence':{'origin':'New human proposal6October2026, not recovered round1–7 item','thinking_hours':'NOT_RECORDED_OR_VERIFIABLE'},'status':'FREQUENCY_CENSUS_LAUNCHED_TRAINING_NOT_EXECUTED','fully_explored':False,'thinking_hours':'NOT_A_COMPLETION_METRIC','round8_evidence':[],'prerequisites':['exact word/span mask alignment','matched useful-target exposure','all-target native evaluation','paid normalized class/mixing law']})
assert len(program['entries'])==96 and all(e['fully_explored'] is False for e in program['entries'])
for e in program['entries']:
 if e['id'] in ['A15','A83','A85','A96']:
  evidence=e.setdefault('round8_evidence',[])
  line='A96registered frequency census and common/rare masking/gradient controls; training unexecuted; see5090hours_and_rarity_plan'
  if line not in evidence:evidence.append(line)
 if e['id']=='A96':
  e['status']='PARTIAL_DICTIONARY_MASK_RESIDUAL_PILOT_'+(mask['status'] if mask else 'LAUNCHED')+'_CORE_OOV_FULL_CODEC_OPEN'
  line='Free-T4 dictionary-span masked residual pilot: research_round8_rarity_residual_pilot_protocol.md; original transformer gradients, OOV masks and native qualification remain open'
  if line not in e['round8_evidence']:e['round8_evidence'].append(line)
(R/'research_round8_idea_program.json').write_text(json.dumps(program,indent=2),encoding='utf-8')
small=f'''<!-- current-native-and-rarity-start -->
Updated{now}: {count}completed finite native fitted heads,27online role policies;
source-conditioned31head fit:{fit_line} Rarity census:{census_line}
Current ledger96 =95historical families +newA96; every family remainsOPEN.
Read research_round8_5090_hours_and_rarity_plan.md for the direct coverage,
GPU-hour and masking answers. No qualifying archive/20%gain; budget70/spent0.
<!-- current-native-and-rarity-end -->

'''
for name in ['research_round8_idea_program.md','research_round7_report.md','research_round7_finetuning_execution_plan.md']:
 p=R/name;s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- current-native-and-rarity-start -->.*?<!-- current-native-and-rarity-end -->\s*','',s,flags=re.S);p.write_text(small+s,encoding='utf-8')
table='\n'.join(f"|{r['name']}|{r['development_q16_saving_bytes']:.9f}|{r['development_after_two_coefficient_copies_and_5bit_selector_bytes']:.9f}|{r['supporting_plane_gap_bytes']:.6g}|" for r in fit['results']) if fit else ''
block=f'''<!-- current-native-rarity-integration-start -->
## 20. Native source observation, stronger residuals and rarity allocation —{now}

The completed24paired-error heads certify their ideal boxes to<=.05byte but
fail the registered priced gate; best priced result{error['best_priced_AB_bytes']:.9f}B.
The27constant-time role policies are considerably cheaper to replay, about8CPU
seconds/slice for the full research sweep, yet actual roles save4.468373421B
versus generic4.576862926B and permuted roles4.623679192B. Their best selector-
priced gain3.998679192B fails64B. This does not settle nonlinear learned roles.
The complete native cost atlas attributes constructor atoms12.8477% of A/B
ideal bit cost; the remaining dictionary53.0499%, literal/control33.4788%.
Common frequency is not equivalent to recoverable native entropy.

The observer exports19actual core channels before consuming each target,
preserving both full A/B512K archives and every native integer probability,
plus independent32K decodes. Its observation files are not decoder assets.
V1fit failed before fitting due to overlapping2/3byte WRT initial codes;
V2preserves the failure and checks all44515codes/proper prefixes. It supplies
stronger source disagreement/role interactions and a128bit-delay control.
Its exact earlier integer laws pass future target/source/role noninterference.
Source fit status:{fit_line}
Independent weak-source confirmation:{weak_line}
Actual inline result:{inline_line}
Nested wider coefficient family:{wide_line}
{ef_line}
Actual wider native result:{wi_line}
The first source bound had derivative-329.141nats toward a larger coefficient;
an extended-box fit removes this artificial limitation without changing features.
Fresh E/Fconfirmation passed; the old C/Dresults cannot be relabeled fresh.

|Registered head|A/B Q16 gain bytes|After2coefficient copies +5bit selector|Ideal box gap bytes|
|---|---:|---:|---:|
{table}

These figures are development outcomes. Only a predeclared advancement and
frozen independent/native/full-package qualification can establish a candidate.
The historical95family audit remains unchanged; A96now formalizes the user's
frequency-threshold mask/gradient/specialist proposal. Its corpus census is
{census_line} Partial dictionary-target residual experiment:{mask_line}
No full-word/original-transformer mask training is claimed. Detailed equations, controls,
step/throughput GPU-hour arithmetic and70dollar gates are in
research_round8_5090_hours_and_rarity_plan.md and rarity_mask_protocol.md.
No best-possible descendant or LLM-equivalent research effort is established.
All96current families remainOPEN; no absolute optimum/20%archive result.
<!-- current-native-rarity-integration-end -->
'''
p=R/'research_round8_report.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- current-native-rarity-integration-start -->.*?<!-- current-native-rarity-integration-end -->\s*','',s,flags=re.S);p.write_text(s+'\n'+block,encoding='utf-8')
print(json.dumps(summary,indent=2))
