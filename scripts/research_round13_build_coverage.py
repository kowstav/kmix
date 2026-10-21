
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
import datetime,hashlib,json
ROOT=project_root(__file__)
old=json.loads((project_path('research_round10_96_scope.json', base=ROOT)).read_text(encoding='utf-8'))
links={
 'A17':('FINITE_CODEC_RESULTS_AND_STRONGER_DESCENDANT_RUNNING','Eighteen exact materialized layouts completed; eighteen original-storage/regeneration-preserving layouts running. Earlier twelve adaptive V4 arms also completed. Native loader/code/CPU qualification remains open.',['R13-weight-storage','R13-weight-storage-regeneration']),
 'A25':('TINY_MEMORY_PRIMITIVE_RUNNING','Four fixed EW horizons and two hidden projections are being evaluated with append-only/zero/short controls. Learned survival, optimal eviction and TTL architecture are not implemented.',['R13-warm-development','R13-warm-confirmation']),
 'A31':('FINAL_MIXER_SUBCLASS_RUNNING','Global versus partitioned contexts and reduced source laws are running. This does not implement a new token-level CM or prune the original model bank.',['R13-warm-development','R13-native-final-head-v2']),
 'A32':('SUMMARY_PRIMITIVE_RUNNING_CACHE_PENDING','A tiny carried hidden summary is running; an actual associative hidden-state cache and retrieval controls remain pending.',['R13-warm-development','R13-warm-confirmation']),
 'A35':('FOUR_EXPERT_MIXTURE_RUNNING','A deterministic fixed-share mixture of identity/full/global/reduced laws is running. No snapshot ensemble or best expert portfolio is established.',['R13-warm-development','R13-native-final-head-v2']),
 'A42':('POST_SSE_DESCENDANT_RUNNING','Integer online residuals and guarded final-bit routing are running in matched regional states; actual native archive integration is submitted after a delivery repair. Full package/resources remain open.',['R13-warm-development','R13-native-final-head-v2']),
 'A63':('FINITE_INTEGER_CALIBRATION_RUNNING','Three learning rates, contexts and Q16 odds corrections are running. The full learned 128-factor controller and every precision alternative are not exhausted.',['R13-warm-development','R13-native-final-head-v2']),
 'A82':('FINITE_ADDITIVE_AND_GUARDED_COMBINATIONS_RUNNING','Original-source/neutral/add-memory/short-memory combinations and two fixed-share mixtures are running. This is a finite control grid, not the best multi-channel architecture.',['R13-warm-development','R13-warm-confirmation']),
 'A84':('SMALL_LINEAR_NATIVE_RESIDUAL_RUNNING','A causal online integer linear residual is implemented, prefix/neutral tested, and submitted for native archives. A trained residual transformer or optimal descendant is unimplemented.',['R13-warm-development','R13-native-final-head-v2']),
 'A85':('FINITE_PAID_LEXICAL_SPLIT_COMPLETE','144 exact paid lexical constructor/literal proxy cases completed. Full-corpus fixed arms running. True typed rare/OOV and POS or neural constructor classification remain pending.',['R13-constructor-descendants','R13-full-corpus-factorization']),
 'A86':('UNIFORM_BAG_ARM_COMPLETE_STRONGER_ORDER_PENDING','Sixteen paid bag cases completed. Conditional multiset order, learned templates, subset dictionaries and full code/state economics remain pending.',['R13-constructor-descendants']),
 'A87':('FINITE_ORDERED_MARKOV_DESCENDANT_COMPLETE','An ordered Markov constructor law and pooled-anchor descendants were tested; reusable template dictionaries/subset grammar and trained joint models remain unimplemented.',['R13-constructor-descendants','R13-full-corpus-factorization']),
 'A88':('PAID_RIGHT_ANCHOR_PROXY_COMPLETE_NEURAL_PENDING','Pooled paid right anchors have completed representative exact proxy tests. The complete selected confirmation still loses to gzip. Neural infilling and optimized common/rare typed factorization remain untested.',['R13-constructor-descendants','R13-full-corpus-factorization']),
 'A93':('CPU_IDENTITY_REPAIRED_GPU_PARITY_PENDING','435-tensor native identity is verified; actual neutral archive/trajectory checks are required in the native job. GPU production batching/parity and all reset configurations remain open.',['R13-weight-storage','R13-native-final-head-v2']),
 'A95':('REGIONAL_NATIVE_AND_FULL_RAW_PROXY_RUNNING','Sixteen matched regional native resets and complete original-corpus proxies are running. Neither supplies full-file native global state or eligible full-package CPU/RAM qualification.',['R13-warm-development','R13-warm-confirmation','R13-full-corpus-factorization']),
 'A96':('THEORY_CORRECTED_GPU_IMPLEMENTATION_PENDING','Shared WRT-byte loss masking is distinguished from exclusive word-alphabet masking. Old disqualified finetunes lose; full literal/OOV masking and stable core continuations are still untested.',['R12-preserved-bf16-results']),
}
entries=[]
for item in old['entries']:
    row=dict(item);identifier=row['id'];state,note,evidence=links.get(identifier,('NO_NEW_ROUND13_DIRECT_TEST',
       'Read the historical evidence below. This round does not implement or complete this idea. Its specific stronger descendant, matched controls and dependencies remain the registered work.',[]))
    row.update(round13_state=state,round13_actual_work=note,round13_evidence_ids=evidence,
       thorough_testing_complete=False,absolute_best_descendant_established=False,
       universal_impossibility_claim=False,
       researcher_level_mature_architecture_claim=False,
       combination_status='Only the explicitly named combinations are implemented/tested; all listed partner combinations remain proposals unless an actual result ID is provided.',
       idea_specific_thinking_hours='No separately measured thinking-hour ledger; do not invent hours or decades-equivalent maturity.')
    entries.append(row)
report={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entry_count':len(entries),
    'all96_thoroughly_tested':False,'absolute_best_descendants_established':False,
    'no_finite_result_is_universal_impossibility':True,'coverage_definition':'Each actual job is mapped only to the mechanism it implements; a fixed linear primitive is not evidence for its full learned architecture.',
    'source_scope_sha256':hashlib.sha256((project_path('research_round10_96_scope.json', base=ROOT)).read_bytes()).hexdigest(),'entries':entries}
assert len(entries)==96 and len({e['id'] for e in entries})==96
(project_path('research_round13_96_coverage.json', base=ROOT)).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
lines=['# All 96 ideas: actual evidence and remaining rigorous tests','',
    '7 October 2026. None is labelled universally exhausted or optimally implemented.',
    'The requested researcher-level maturity is not claimed. Thinking hours per idea',
    'were not separately measured; breadth of a ledger is not depth of experiments.','',
    'Each entry preserves the three historical audit questions, then gives the actual',
    'round-13 work, stronger descendant, specific protocol, engineering and combination',
    'dependencies. “No new direct test” does not erase historical experiments.','']
for r in entries:
    h=r['historical_evidence'];lines += [f"## {r['id']}: {r['title']}",'',
      f"Current finite status: **{r['round13_state']}**. Thorough testing complete: **No**.",'',
      '**1. Was mature researcher-level rigor/architecture/engineering established?**',
      h.get('rigor_applied','A later addition to the historical inventory: '+h.get('origin','no separate historical maturity evidence')),
      'No claim of that level or an optimal architecture is supported by the recorded work.','',
      '**2. What was actually tested, and what is the fair stronger test?**',
      h.get('actual_testing_and_needed_testing','Full typed literal/OOV recovery and stable original-core continuation remain untested; old loss-masked finetunes are finite disqualified-protocol observations.'),r['round13_actual_work'],'',
      'Stronger descendant: '+r['stronger_descendant'],
      'Idea-specific test: '+r['idea_specific_test'],
      'Exact protocol: '+r['protocol'],
      'Mathematical contract: '+r['math'],
      'Engineering requirements: '+r['engineering'],'',
      '**3. Were the best combinations developed and tested for hours?**',
      h.get('combination_work','No mature rare/common/mixer-aware combined architecture or separately recorded optimization hours.'),r['combination_status'],r['idea_specific_thinking_hours'],
      'Registered partners: '+', '.join(r['combination_partners'])+'.','',
      'Dependencies: '+r['dependencies'],
      'Finite endpoint: '+r['finite_endpoint'],
      'Stopping rule: '+r['stop_current_arm'],
      'Reopening rule: '+r['reopen'],
      'Direct round-13 evidence: '+(', '.join(r['round13_evidence_ids']) or 'None; not upgraded by association.')+'.','']
(project_path('research_round13_96_coverage.md', base=ROOT)).write_text('\n'.join(lines),encoding='utf-8')

audit=json.loads((project_path('research_round10_audit_fixes.json', base=ROOT)).read_text())
updates={
 'S2':('REGIONAL_NATIVE_RUNNING_FULL_STATE_OPEN','The R11 atlas was interrupted; sixteen regional native jobs run as matched regional histories. Full global-state baseline remains open.'),
 'S4':('COARSE_TIMING_MEASURED_PRODUCTION_OPEN','Preserved R12 encode-only timings; new jobs use actual user/system CPU and RSS. Four-core constructor utilization is measured. Eligible production timing remains open.'),
 'M6':('STATISTICAL_IMPLEMENTATION_REPAIRED','Bootstrap rejects fewer than ten clusters per stratum; R13 confirmation has eight and remains descriptive, with no unjustified population CI.'),
 'D1':('OLD_PREFIX_TRANSIENT_OBSERVED_BROADER_TEST_RUNNING','The old law loses its gain after startup in R12 early warm windows. Broader regional controls run; no whole-family stationarity theorem is inferred.'),
 'D7':('LAB_TIMING_MEASURED_QUALIFICATION_OPEN','Do not compare only wall time across VMs. Component timing and new within-region paired jobs price actual CPU; shared notebook lanes are not production qualification.'),
 'L6':('WARM_CAUSAL_CONTROLS_RUNNING','Old neural-underweighting startup signal is not assumed stationary. New online residual/neutral/global/source controls run; no premise is inferred from a cold gain.'),
 'E1':('COMMITTED_JOBS_RUNNING_PRESERVATION_PARTIAL','Main new jobs are durable private commits. Full warm stage/hidden traces still live only in root scratch; actual baseline archives and compact records are notebook outputs.'),
 'E3':('PREFLIGHT_ADDED_DELIVERY_FAILURE_REPAIRED','Linux and codec preflights pass; a native ZIP-delivery failure was caught before compression, preserved and repaired using .zip.dat. Production checks remain open.'),
 'E4':('LAB_NATIVE_INTEGRATION_RUNNING_PRODUCTION_OPEN','Pinned Clang/LLD17 and portable flags restored; actual coder laws are built, with neutral archive/trajectory and independent inverse gates. Original PGO and eligible resources remain open.'),
 'E5':('REGIONAL_WARM_INFRASTRUCTURE_RUNNING','Carried state within each registered 3 MiB region, with 2 MiB warmup. Exact full-file snapshots remain unimplemented.'),
 'E6':('INTEGER_LAW_IMPLEMENTED_PORTABILITY_OPEN','Fixed integer tables/posterior and native direct-Q16 boundary are implemented. Cross-vendor whole production trajectory still needs evidence.'),
}
for row in audit['findings']:
    row['round13_status'],row['round13_correction']=updates.get(row['id'],(row['status'],'Existing correction/protocol remains; no automatic claim that its experimental requirement is complete.'))
new=[
 ('R12-N1','Memory overwrote original predictors','FIXED_AND_PROPERTY_VERIFIED','Eight features appended; full and neutral-memory trajectories must match. Quality tests run.'),
 ('R12-N2','Raw WRT markup class never fired','FIXED_AND_PROPERTY_VERIFIED','Invert exact byte map before classification; distinguish mapped bytes from full dictionary/escape-state decoding.'),
 ('R12-N3','Compression-only modes demanded independent decode','INVALID_JOB_STOPPED_REPLACEMENT_PRESERVED','Old job refuses invalid use; R12 encode-only evidence is preserved and honestly labelled.'),
 ('R12-N4','Old disqualified finetunes re-priced','NEGATIVE_RESULTS_PRESERVED_PROTOCOL_NOT_REHABILITATED','Old models lose on 3 MiB native prefix; do not interpret this as a stable-continuation test or reject all future training.'),
 ('R12-N5','Unguarded SGD can lose','GUARDED_DESCENDANT_IMPLEMENTED','Fixed-share law added; no ideal finite-precision regret theorem asserted. Actual native quality/resources pending.'),
 ('R12-N6','Two-cluster bootstrap was unreliable','FIXED_AND_PROPERTY_VERIFIED','Minimum ten clusters; deterministic spacing and shared windows do not create population independence.'),
 ('R12-N7','Sixth commit unresolved; gzip transfer and sparse anchors','SOURCE_AND_EXECUTION_RESCOPED','Actual URLs verified; pooled coarse anchor descendants run. Gzip gains remain proxies; vanished live atlas recorded interrupted.'),
]
audit.update(updated=report['updated'],all_experimental_fixes_complete=False,
    third_audit_sha256=hashlib.sha256((project_path('CLAUDE_AUDIT_03_ROUND12_VERIFICATION_AND_CPU_RESULTS.md', base=ROOT)).read_bytes()).hexdigest(),
    new_findings=[{'id':i,'finding':f,'status':s,'correction':c} for i,f,s,c in new])
(project_path('research_round13_audit_fixes.json', base=ROOT)).write_text(json.dumps(audit,indent=2),encoding='utf-8')
lines=['# Round 13 audit repair ledger','',
 'All three original Claude reports remain unchanged. This ledger carries every',
 'original finding and the seven new finding groups; an addressed protocol is not',
 'silently upgraded to a completed experiment. Full experimental closure: **No**.','',
 '| ID | Finding | Round-13 status | Correction / remaining work |','|---|---|---|---|']
for r in audit['findings']:lines.append('| '+r['id']+' | '+r['finding'].replace('|','/')+' | '+r['round13_status']+' | '+r['round13_correction'].replace('|','/')+' Original requirement: '+r['remaining_requirement'].replace('|','/')+' |')
for r in audit['new_findings']:lines.append('| '+r['id']+' | '+r['finding']+' | '+r['status']+' | '+r['correction']+' |')
lines += ['','Theory corrections and masking-alphabet distinctions: research_round13_theory.md.',
    'Execution/versioned failures and proof of actual four-core utilization: research_round13_report.md.','']
(project_path('research_round13_audit_fixes.md', base=ROOT)).write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'ideas':len(entries),'original_audit_findings':len(audit['findings']),'new_groups':len(new),'all_thoroughly_complete':False}))
