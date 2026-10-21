import datetime,hashlib,json,re
from pathlib import Path
R=Path(__file__).parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
atom=json.loads((R/'research_round8_canonical_atom_fit_results.json').read_text())
assert atom['status']=='COMPLETE_CANONICAL_ATOM_CACHE_DIAGNOSTIC' and len(atom['results'])==11
assert all(v['ideal_box_optimum_certified'] and v['supporting_plane_gap_bytes']<=.05 for v in atom['results'])
atlas_path=R/'research_round8_canonical_cost_atlas_complete_manifest.json'
atlas=json.loads(atlas_path.read_text()) if atlas_path.exists() else None
error_path=R/'research_round8_canonical_error_memory_results.json'
error=json.loads(error_path.read_text()) if error_path.exists() else None
error_complete=bool(error and error['status'].startswith('COMPLETE'))
atlas_complete=bool(atlas and atlas['status']=='COMPLETE_CANONICAL_COST_ATLAS')
count=62+(len(error['results']) if error_complete else 0)
summary={'updated':now,'session':355735431,'status':'PARTIAL_RESEARCH_CONTINUATION_ALL_FAMILIES_OPEN','native_heads_completed':count,'canonical_atom_fit':{'status':atom['status'],'result_file':'research_round8_canonical_atom_fit_results.json','heads':11,'best_priced_AB_bytes':atom['best_priced_AB_bytes'],'advance_gate_pass':atom['advance_gate_pass'],'confirmation_candidates_evaluated':False,'joint_development_raw_bytes':atom['results'][-1]['development_q16_saving_bytes']},'contextual_error_memory':{'directory':'error_memory_resume_v2','historical_pid':136,'status':error['status'] if error else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS','result_file':error_path.name if error else None},'canonical_cost_atlas':{'directory':'canonical_cost_atlas_v4','historical_pid':172,'status':atlas['status'] if atlas else 'LAUNCHED_VERIFY_CURRENT_MANIFEST_AND_PROCESS','result_file':atlas_path.name if atlas else None},'attachment_read_in_full_bytes':9969,'attachment_assessment':'research_round8_attachment_assessment.md','training_addendum':'research_round8_attachment_training_addendum.md','new_competitor_source_audit':'research_round8_neif_architecture_audit.md','full_native_qualifying_candidate':False,'twenty_percent_achieved':False,'absolute_optimum_claimed':False,'all_95_fully_explored':False,'paid_spending_usd':0,'deletions':[],'managed_goal_status':'usageLimited_DO_NOT_RESUME_OR_REPLACE','week_end':'2026-10-11','source_state':'old_session355655943_unreachable; preserved native exports and A/B atom features reused'}
(R/'research_round8_session355735431_extension_status.json').write_text(json.dumps(summary,indent=2))
err_text=(f"COMPLETE with {len(error['results'])} heads; read research_round8_canonical_error_memory_results.json before any further decision" if error_complete else "launched in error_memory_resume_v2, PID136 at launch; verify current manifest and actual child process, do not duplicate")
atl_text=("COMPLETE; canonical A/B attribution and stable causal-mixture diagnostic preserved locally" if atlas_complete else "launched in canonical_cost_atlas_v4, PID172 at launch; earlier failed versions remain evidence, verify actual status")
note=f'''<!-- canonical-status-start -->
## Current authoritative continuation — {now}

Newest Kaggle session355735431. Old355655943 is unreachable; copied historical
PIDs1491/1514 are not live. Never reuse a copied PID as proof of a running job.
Completed resumed atom_fit_resume_v2:11canonical heads, all ideal convex box
certificates<=0.05B. Best priced A/B=-26.846967465B; joint raw gain28.249721346B
on1MiB, coefficients+selector112.5B. Registered64B advancement failed; C/D
candidate checks remain untouched. This rejects the registered finite screen,
not every amortized/full-warm variant. No duplicate native inference was run.

Contextual paired-error memory: {err_text}.
Canonical cost/cluster audit: {atl_text}.
Read research_round8_session355735431_handoff.md and its extension_status.json.
Preserve any new compact output locally before another session refresh.

Attachment fully read:9,969B. Its six mapped proposals remain OPEN.
Assessment: research_round8_attachment_assessment.md. Controlled$70training
addendum: research_round8_attachment_training_addendum.md. No training/rental.
Weighted curriculum can bias probabilities; current surprise cannot be an
inference gate; altered synthetic prefixes require consistent states/priors.

Correct lexical preparation/full inverse COMPLETE:587138826B prepared,
SHA7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce;
original1B SHA159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.
Remote hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt preserved.
Full native entropy archive and full resource-qualified improvement remain
unexecuted. Baseline peak leaves615424B below decimal10GB; KVI8alreadyused.
Parser experts must fall back on arbitrary side/tail bytes with legal framing.

Pending cmix-neif1.0 reports95914051B; official awarded100424672B. Strict>20%
of pending target needs<=76731240B. This is a target, not a forecast/result.
Read research_round8_neif_architecture_audit.md for compatible causal-reminder,
word-model and recurrent-error lessons; no competitor code/model adopted.

{count} native/metric/atom heads now complete. All95historical families OPEN;
no claim of LLM-development-equivalent effort, absolute optimum or20%gain.
Models/data preserved; project deletions NONE; budget$70/spent$0.
Managed Goal remainsusageLimited. Do not resume/replace/mutate/bypass it on
heartbeats. Ordinary work in this explicit human turn is separate. Week ends
11October2026. Core GPU parity stillfails; native-feature residual route remains.
Older entries below are historical and superseded.
<!-- canonical-status-end -->

'''
p=R/'research_round7_checkpoint.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- canonical-status-start -->.*?<!-- canonical-status-end -->\s*','',s,flags=re.S);p.write_text(note+s,encoding='utf-8')
handoff=f'''# Session355735431 continuation handoff

Updated {now}. This file supersedes historical launch/PID instructions. Signed URLs are never saved in artifacts. Obtain the newest user-authorized URL from the conversation and use the existing Jupyter client. Kernel at launch: f1943494-319d-462a-b309-cfd2136fc338. Verify its status if the session changes.

## Current finite jobs and exact continuation

* atom_fit_resume_v2 COMPLETE. Sources research_round8_resume_atom_fit_worker_v2.py; output hp_round8/atom_fit_resume_v2/manifest.json, locally research_round8_canonical_atom_fit_results.json.11heads, no advancement. Do not rerun or regenerate native inference.
* Contextual error-memory: {err_text}. Source research_round8_resume_error_memory_worker_v2.py. Remote manifest hp_round8/error_memory_resume_v2/manifest.json.22signals/24fitted heads; FIFO512/K8, raw/center/diagonal, paired-value controls, lambda .25/1/4. Strong convex local roots, exact Q16 replay, bounded A/B fits and fixed causal policies. Only64priced development bytes permit conditional C/D features under this protocol.
* Canonical difficulty/cluster atlas: {atl_text}. Source research_round8_canonical_cost_atlas_v4.py. Remote manifest plus a.json/b.json under hp_round8/canonical_cost_atlas_v4. All native bits reconciled. Dictionary atoms are not all linguistic words; constructor list is not POS.3840fixed causal contexts, KT estimation and global half-identity mixture use log posterior odds. Independent batch-normalizer test detects numerical posterior loss.

The error-memory source includes research_round8_error_memory.cpp, which includes research_round8_atom_cache.cpp. Preserve these exact executed files, compiler flags, binary SHA and selftests. Original native inputs remain under hp_round8/atom_cache_v1: a512k.bin..d512k.bin and a_native..d_native/final_p.u16,hidden.q8. The original interrupted atom manifest is historical but its input/features hashes are verified by resumed workers. A/B512K atom features reused without regeneration. Preserve the four full native exports remotely; compact evidence records their hashes and exact32K reference/decode controls.

## Required next actions

1. Read current manifests and actual worker/child processes once. Copied manifest PIDs are historical. Reuse live jobs; no duplicate launch. Wait/back off while unchanged, working on independent math/report tasks.
2. On completion download manifests, controller/replay/selftest logs and compact per-slice results using kaggle_research_client.mjs download. Verify exact source/hash/Q16 certificates, future-target/hidden noninterference and finite advancement. Preserve FAIL outputs before any separately named repair.
3. If a head advances, freeze its A/B coefficients and choices; inspect only registered C/D confirmation. Price coefficients, variant selector, loader/code, state, search time and whole peak RAM. Tiny cold gain is not full-file gain; shipping costs amortize over a full candidate. A new weak-signal experiment needs a declared protocol and fresh checks or exploratory labeling.
4. Update this handoff, checkpoint, integrated reports, training plan and machine-readable95family evidence. Keep every fully_explored flag false until its own full tests actually finish. Six attachment proposals are separately mapped to existing families.
5. Preserve a separate compact native extension ZIP and its SHA/source ledger. Initial189file research_round8_evidence.zip is immutable. Do not overwrite it or delete original model/data. Large traces/features may be excluded from a compact bundle only with explicit remote/hash/reproduction accounting, not called deleted.
6. The native full encoder and exact1B entropy decode remain required. Cold512K tests use reset core state. The existing full preprocessing inverse is a different completed gate. Fix core GPU parity before core finetuning; a small independent residual may train from native-produced real features without it.

## Failure ledger and repairs

The old session ended during original A/B fitting and before error replay. In the new session atom_fit_resume_v1 completed its first solve but exited on a NumPy boolean JSON conversion; its error handler also could not serialize that boolean, leaving a stale RUNNING manifest. The preserved log proves exit. Error_memory_resume_v1 waited on that dead parent and was stopped only after exact argv/PID verification; it had generated no data. New v2 directories repaired serialization and reused each head's design matrix. Atlasv1 failed on NumPy uint16 subtraction;v2 exposed irreversible direct posterior saturation;v3 passed the independent batch identity but a too-tight streaming-regret tolerance failed. V4 checks the exact batch bound and explicitly records accumulated floating roundoff. Earlier failed directories/logs remain unchanged.

No project files/models/data have been deleted. Only the verified waiting controller was stopped; no training or native export was killed. Spending$0. No paid instance has been launched. Managed Goal remainsusageLimited and may not be automatically resumed or replaced. All95families remain OPEN. User's week ends11October2026.
'''
(R/'research_round8_session355735431_handoff.md').write_text(handoff,encoding='utf-8')

table='\n'.join(f"| {v['name']} | {v['development_q16_saving_bytes']:.9f} | {v['development_after_two_coefficient_copies_and_4bit_selector_bytes']:.9f} | {v['supporting_plane_gap_bytes']:.9g} |" for v in atom['results'])
block=f'''<!-- session355735431-integration-start -->
## 19. Attached curriculum and resumed canonical experiments — {now}

The9,969B attachment was read in full. Its useful additions are cost-weighted opportunity mining, paired error replay, acceptance/rejection, causal synthetic relation tasks and an unweighted finish. Weighted objectives, plug-in cluster entropy and altered-prefix priors need the corrections in [research_round8_attachment_assessment.md](research_round8_attachment_assessment.md). The detailed controlled training ladder is in [research_round8_attachment_training_addendum.md](research_round8_attachment_training_addendum.md), within the unchanged$70cap and$0spending. All six new mapped proposals remain open.

Session355735431 preserved four canonical native512K exports and A/B atom features. Old355655943 became unreachable during fitting. The corrected resumed worker completes11bounded heads without repeating core inference. Future-target/hidden noninterference and32K independent native decode/reference identity are reused and hash-checked. All ideal support-plane certificates are below0.05byte. These certify a continuous finite box objective only; Q16, package and warmed-history optima are separate.

| Canonical atom head | A/B Q16 gain bytes | After two coefficient copies + 4-bit selector | Ideal supporting-plane gap bytes |
|---|---:|---:|---:|
{table}

Fixed causal global/context policies save-0.255883569/-1.465964140bytes on A/B. The best priced fit is generic at-26.846967465bytes. The joint head's28.249721346raw bytes versus generic5.653032535 suggests a small finite interaction; its112.5byte assets dominate this1MiB screen. Most ordinary recall coefficients are negative; the hard-word coefficient is positive. The registered64B advancement gate fails and C/D candidate evaluation is not performed.

This is a finite screening decision, not a proof that full-file amortization or trained retention fails. Those coefficients would be stored once per package copy over the full file; cold reset samples do not establish the warmed rate. A new weak-signal branch needs a predeclared full-rate/code-size test and independent or honestly exploratory checks. Do not scale28bytes to587M and call it an achieved archive saving.

The stronger paired contextual-error memory is {err_text}. It preserves probability/outcome pairs, estimates a strongly convex local signed correction, matches prefix events and compares actual/permuted keys, recency and prefix-only controls. The canonical cost atlas is {atl_text}. Its global Bayesian mixture required log posterior odds; a batch likelihood-normalizer identity independently checks its streamed result. All failures/repairs and exact executable sources are preserved in the handoff.

The new competitor source audit is [research_round8_neif_architecture_audit.md](research_round8_neif_architecture_audit.md). Causal reminders, online word models and recurrent final-bit corrections support stronger descendants of the user's ideas. Their alphabet/training/state/resource contracts differ from this core; no competitor code or model has been adopted. The pending95,914,051B target still requires<=76,731,240B for>20%; no such result is demonstrated.

Current count:{count}native/metric/atom fitted heads complete. All95families remain OPEN. No absolute optimum, LLM-development-equivalent effort, qualifying full archive or20%gain is claimed. Exact full preprocessing inverse is complete; full entropy archive/CPU/RAM qualification is open. No project deletion; spending$0. See research_round8_session355735431_extension_status.json for machine-readable handoff.
<!-- session355735431-integration-end -->
'''
p=R/'research_round8_report.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- session355735431-integration-start -->.*?<!-- session355735431-integration-end -->\s*','',s,flags=re.S);p.write_text(s+'\n'+block,encoding='utf-8')
for name,title in [('research_round7_report.md','Latest integrated research'),('research_round7_finetuning_execution_plan.md','Latest training/attachment correction')]:
 p=R/name;s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- session355735431-summary-start -->.*?<!-- session355735431-summary-end -->\s*','',s,flags=re.S);p.write_text(f'''<!-- session355735431-summary-start -->
> {title}, {now}: newest session355735431; {count}native/cache heads complete;
> canonical11head atom screen fails its registered gate. Strong paired-error
> branch:{'complete' if error_complete else 'running; verify actual manifest/process'}. Attachment fully read;
> see research_round8_attachment_assessment.md and
> research_round8_attachment_training_addendum.md for cost mining,
> objective-safe replay, curriculum controls, causal synthetic tasks and export
> gates. Full correct lexical inverse PASS; full native entropy qualification
> stillOPEN. All95families OPEN; no20%result; budget$70/spent$0; deletionsNONE.
> Current handoff: research_round8_session355735431_handoff.md. Historical stream,
> PID and incomplete-preparation claims below are superseded by the checkpoint.
<!-- session355735431-summary-end -->

'''+s,encoding='utf-8')

p=R/'research_round8_idea_program.json';program=json.loads(p.read_text(encoding='utf-8'));program['date']=now;program['session']=355735431;program['latest_extension']='research_round8_session355735431_extension_status.json'
targets={'A15','A18','A19','A20','A21','A22','A25','A64','A66','A67','A68','A70','A71','A79','A80','A81','A82','A83','A84','A85','A88','A91','A92'}
for e in program['entries']:
 assert e['fully_explored'] is False
 if e['id'] in targets:
  evidence=e.setdefault('round8_evidence',[])
  for line in ['canonical atom_fit_resume_v2:11bounded ideal-certified heads; registered gate fails; full amortization/warm family still open','contextual error-memory descendant: paired native probability/outcome; exact prefix matching and strongly convex root; inspect latest extension status','complete attached curriculum assessment and controlled$70training addendum; training unexecuted']:
   if line not in evidence:evidence.append(line)
program['attachment_proposals']=[{'id':'S%02d'%i,'status':'OPEN','assessment':'research_round8_attachment_assessment.md','training':'research_round8_attachment_training_addendum.md'} for i in range(1,7)]
p.write_text(json.dumps(program,indent=2),encoding='utf-8')
p=R/'research_round8_idea_program.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- session355735431-program-start -->.*?<!-- session355735431-program-end -->\s*','',s,flags=re.S);p.write_text(f'''<!-- session355735431-program-start -->
Updated {now}, session355735431. All95historical families remain OPEN. Six
attachment proposals S01–S06 are separately mapped in the machine-readable
program and assessment. Canonical11-head box-certified screen now complete;
{count}native/cache heads total. Paired-error memory and cost atlas status are
in research_round8_session355735431_extension_status.json. Stronger conditional
residuals, trained retention/rejection and paid content-first grammar remain
unfinished. The complete attachment's bias/causality corrections and controlled
$70training ladder are in the assessment/addendum. No comparable historical
LLM research-effort or global optimum claim is made. Do not rerun the original
program generator without preserving these appended evidence entries.
<!-- session355735431-program-end -->

'''+s,encoding='utf-8')
print(json.dumps(summary,indent=2))
