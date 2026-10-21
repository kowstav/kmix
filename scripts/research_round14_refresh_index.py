"""Append verified evidence and retain every original per-idea audit field."""

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
import copy, datetime, hashlib, json, shutil

R=project_root(__file__)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(name):return json.loads((project_path(name, base=R)).read_text(encoding='utf-8'))
def sha(name):return hashlib.sha256((project_path(name, base=R)).read_bytes()).hexdigest()
def write(name,text):(project_path(name, base=R)).write_text(text,encoding='utf-8')

old=project_path('historical_reports/research_round7_checkpoint_20261008_before_completed_wave.md', base=R)
if not old.exists():shutil.copyfile(project_path('research_round7_checkpoint.md', base=R),old)
write('research_round7_checkpoint.md','''# Current continuation checkpoint — round 14

Updated 9 October 2026 after verified submission of four new CPU notebooks.
Use the latest human-provided session **356640492**, kernel
**c2200b55-9f0e-47ea-9747-8c46c592bfeb**. The signed URL is a credential and
must stay out of reports. Root scratch of the old session is gone; working
files and the native binaries survived. Inspect manifests before any launch.

The managed Goal remains usageLimited: never resume, replace or bypass it.
An 8 October escalation was rejected for a usage limit; it was not executed.
The user renewed the task on 9 October and ordinary approval review accepted
the new session calls. Respect any subsequent block. Paid spending $0; no GPU
or rental launched. Research week ends 11 October; do not extend automatically.

## Current authority and verified outcome

Read research_round14_report.md, research_round14_shortlist.md,
research_round14_theory.md, research_round14_audit_delta.md and
research_round14_pre_experiment_report.md. All-96 detailed historical audit fields
are preserved in research_round14_96_coverage.json with a new direct-evidence delta.

- Native guard: eight 3 MiB confirmation archives save 2,587 actual bytes
  against 4,491,669 B; every inverse exact. Warm last-1-MiB aggregate saving is
  415.558 ideal bytes. These are regional resets, not full global history.
  Extra executable bytes are not yet paid; no complete-package win established.
- Four full 1 GB raw proxy archives independently decode exactly. Actual totals:
  gzip 323,066,249; zstd 278,574,861; Markov 350,344,017; right-context 349,939,776 B.
- 608 paid constructor cases all invert exactly. Frozen coarse-right saves
  9,441 B against matched Markov on confirmation, but loses 1,037,000 B to zstd.
  Frozen conditional bag loses 11,143 B to uniform bag. Learned infilling remains open.
- Grouped exact weight coding: best 2,999,272 B, loses 21,233 B per model copy.
  All 435 native tensors exact. This does not test lossy retrained quantization.
- Sixteen warm word-cost windows now have exact WRT event attribution. Constructors
  account for 15.55% of measured bits; other dictionary words 50.27%; literal/OOV
  13.43%. Offline corpus frequency is diagnostic, not a free decoder feature.
- No absolute optimum, 20% reduction, record win, universal rejection of any idea,
  or thorough completion of all 96 ideas is established.

## Running four-core native CPU jobs

Six 16 KiB preflight cases PASSED: pinned, neutral, prune_word, prune_match,
prune_indirect, output_fp32. All independently decoded. Neutral archive AND every
Q16 probability match pinned. hp_round14/native_cpu_preflight_v1/manifest.json.

All four private version-1 submissions were verified at 05:40:53 UTC on 9 October:

- chaoscpp/hutter-r14-native-prune-word-v1
- chaoscpp/hutter-r14-native-prune-match-v1
- chaoscpp/hutter-r14-native-prune-indirect-v1
- chaoscpp/hutter-r14-native-output-fp32-v1

Each uses four pinned processes and four matched 3 MiB pairs on development IDs
0,2,4,6, 2 MiB warmup, alternating baseline/candidate order. They measure actual
archives, independent inverse, warm loss, encode/decode CPU and RSS. Ten-hour
deadline. No quality claim follows merely from preflight. Inspect CLI status;
reuse existing commits and collect every output page, not just the first 500.

Dispatcher hp_round14/native_dispatch_v3.json is COMPLETE_FOUR_VERIFIED_PRIVATE_CPU_PUSHES.
Private input chaoscpp/hutter-r14-native-cpu-assets-v1 includes source/build/parity
manifests. Source hash e110931611c3c55ab004cb92207715d22002f37b63337e6da1ba4bc8b9c6b58a
in kaggle_cpu_round14/sources_native_v3.zip. Full native source archive is separately
hashed a21f035652bf756db9e0bc43c34835ed85412540dc5dd9329d62fd1cd4183840.

## Open PPMd article-order failure

The 160-case order sweep did NOT finish. Partial successes are not a valid
aggregate. pyppmd 1.3.1 variant I directly fails on three real page inputs even
without our container. Padding and explicit decoder lengths do not fix it.
Variant H with the required explicit output length also corrupts region 0
at byte 104,808, although two other cases invert. Do not switch backends without
passing every real failure and preflight stress case. Preserve failure evidence.

New-session diagnostic files: hp_round14/ppmd_backend_probe_v2.json and
hp_round14/ppmd_h_probe_v1.json. Exact raw failures and payloads are under
/root/r14_backend_probe; preserve them compactly before session loss. Follow
up with the actual library implementation or another verified implementation.
No result from a failed inverse may be counted as compression.

## Preservation and cleanup

All completed compact bundles were locally CRC/SHA verified: 1,298 batch/tail/word
entries and 156 earlier completed entries, plus both detailed warm-cost ZIPs,
native sources/binaries and regenerated model. Manifests:
research_round14_preserved_verification.json and research_round14_local_detail_verification.json.
Some full probability traces and partial .hporder files remain in private committed
outputs; do not claim every artifact is local.

New native preservation ZIP: hp_round14/native_cpu_preservation_v2.zip,
1,738,710 B, SHA e259132fb7f50c160f527d6a77f974766965b1457583e14f4ebcea682c08aa90.
Download and verify if not already present locally.

Deleted in this round only 480,078,284 B of verified duplicate data: one aggregate
ZIP and four decoder hidden traces with identical retained encoder twins. Exact
paths/hashes/reasons in research_round14_pull_manifest.json and
research_round14_detail_preservation.json. No original data, trained models or
unique source was deleted. No new-session deletion has occurred.

## Next decisions

Finish article-order backend repair; collect four native pairs per arm; shortlist
on complete paid archive cost AND CPU/RAM. Register a new finite hypothesis before
confirmatory tuning. A full global native run and eligible CPU/RAM measurement
remain open. Ask for a GPU session after the declared finite CPU work is complete,
not after falsely declaring unrestricted 96-idea families exhausted. Use the
existing $70 training plan and measured throughput pilot before any rental.
''')

base=read('research_round13_96_coverage.json');new=copy.deepcopy(base)
new.update(updated=now,source_round13_sha256=sha('research_round13_96_coverage.json'),entry_count=96)
updates={
 'A15':('COMPLETE_DIAGNOSTIC_NOT_MASK_TRAINING','Sixteen warm native word-cost regions parsed exactly; frequency thresholds are offline diagnostics. Full literal/OOV masking and stable original-core training remain untested.',['R14-word-costs-v2']),
 'A17':('COMPLETE_FINITE_EXACT_STORAGE_SWEEP','Four fixed groupings and 18 codecs per group; best loses 21,233 B per copy, all 435 tensors exact. No lossy/retraining descendant rejected.',['R14-group-weight-storage-v1']),
 'A31':('NATIVE_FOUR_LANE_COMMITS_SUBMITTED','Three separate genuine component-removal arms passed native inverse; long matched CPU/quality pairs submitted. No long-run result yet.',['R14-native-cpu-preflight-v1','R14-native-dispatch-v3']),
 'A42':('COMPLETE_REGIONAL_NATIVE_GUARD_CONFIRMATION','Eight exact native archives save 2,587 B; warm-only ideal gain 415.558 B. Global history, code size and complete package remain unqualified.',['R14-native-guard-confirmation']),
 'A43':('OUTPUT_ROUNDING_INTERVENTION_SUBMITTED','Only final softmax-output FP16 roundtrip removed, preserving core state. Native inverse passed; long matched pairs pending. This is not retrained low-bit weights.',['R14-native-cpu-preflight-v1','R14-native-dispatch-v3']),
 'A44':('PPMD_BACKEND_FAILURE_PRESERVED','Paid article ordering sweep stopped on real inverse failures in pyppmd. Partial successful cases are not used for selection; repair ongoing.',['R14-ppmd-real-failure']),
 'A67':('COMPLETE_EVENT_COST_DIAGNOSTIC','Exact WRT word events attributed to final-coder bits on sixteen warm regions. No trained word auxiliary head result implied.',['R14-word-costs-v2']),
 'A84':('COMPLETE_ONE_INTEGER_RESIDUAL_DESCENDANT','Native final-coder integer guard confirmed regionally; this does not implement the family of learned nonlinear residual architectures.',['R14-native-guard-confirmation']),
 'A85':('COMPLETE_FINITE_PAID_FACTORISATION','608 paid constructor regional codecs and four whole-file raw proxy inverses complete; split loses against stronger raw codecs. Learned skeleton/native transfer remains open.',['R14-constructors-608','R14-full-serialized-inverse']),
 'A86':('COMPLETE_FINITE_CONDITIONAL_BAG_SWEEP','Conditional-count bag posterior, beta 0/1 and alpha 1/4 with left/right/wrong/Markov controls. Frozen bag loses 11,143 B to uniform bag on confirmation. Not a universal bag impossibility.',['R14-constructors-608']),
 'A88':('COMPLETE_COARSE_PAID_RIGHT_CONTEXT_PROXY','Frozen coarse-right saves 9,441 B versus matched Markov but loses to gzip and zstd. Learned bidirectional infill and final-coder transfer remain open.',['R14-constructors-608','R14-full-serialized-inverse']),
 'A93':('NATIVE_PARITY_AND_INVERSE_GATES_PASSED','Neutral rebuild matches pinned archive and Q16 trajectory; six short CPU-intervention inverses exact. Full training probability parity remains required.',['R14-native-cpu-preflight-v1']),
 'A95':('COMPLETE_RAW_FULL_FILE_INVERSE_ONLY','Four framed 1 GB raw proxies independently invert; representative native guard archives exact. Full native global state and complete package/resources remain open.',['R14-full-serialized-inverse','R14-native-guard-confirmation']),
 'A96':('COMPLETE_RARITY_COST_DIAGNOSTIC','Native word costs by full-corpus frequency measured; future-informed rarity remains a diagnostic unless paid or causally derived. No zero-cost omission and no full masking training result.',['R14-word-costs-v2']),
}
assert len(new['entries'])==96 and len({e['id'] for e in new['entries']})==96
lines=['# All 96 ideas: round-14 evidence delta','',
 'This preserves every idea-specific mathematical protocol, historical audit answer, stronger descendant and dependency from the [round-13 detailed ledger](research_round13_96_coverage.md). The JSON retains all those fields verbatim and adds the entries below. A preflight or diagnostic is not a mature architecture test. No family is declared impossible or fully optimized.','',
 '| ID | Idea | Round-14 direct work | Evidence IDs |','|---|---|---|---|']
for e in new['entries']:
    s,t,ids=updates.get(e['id'],('NO_NEW_ROUND14_DIRECT_TEST','No direct new round-14 experiment; prior evidence and the registered descendant protocol remain in the detailed ledger.',[]))
    e.update(round14_state=s,round14_actual_work=t,round14_evidence_ids=ids)
    e['thorough_testing_complete']=False;e['absolute_best_descendant_established']=False
    lines.append('| '+e['id']+' | '+e['title'].replace('|','/')+' | '+t+' | '+(', '.join(ids) or '—')+' |')
write('research_round14_96_coverage.json',json.dumps(new,ensure_ascii=False,indent=2)+'\n')
write('research_round14_96_coverage.md','\n'.join(lines)+'\n')

p=project_path('README.md', base=R);text=p.read_text(encoding='utf-8')
text=text.replace('Current authority: [round 13 execution report](research_round13_report.md)','Current authority: [round 14 integrated report](research_round14_report.md)')
for old,newfile in [('research_round13_report.md','research_round14_report.md'),('research_round13_pre_experiment_report.md','research_round14_pre_experiment_report.md'),('research_round13_theory.md','research_round14_theory.md'),('research_round13_96_coverage.md','research_round14_96_coverage.md')]:text=text.replace(old,newfile)
text=text.replace('| [Audit repair ledger](research_round13_audit_fixes.md)', '| [Audit repair ledger](research_round14_audit_delta.md)')
text=text.replace('| [Training and 5090 budget]', '| [Measured shortlist](research_round14_shortlist.md) | Native guard, paid right-context mechanism and open CPU resource frontier |\n| [Training and 5090 budget]')
text=text.replace('`kaggle_cpu_round13/` contains the new frozen','`kaggle_cpu_round13/` and `kaggle_cpu_round14/` contain the frozen').replace('recorded in round 13.','recorded in the current checkpoint.')
write('README.md',text)

rows=[
 ('R13-completed-wave','COMPLETE_FINITE_EXPERIMENTS','research_round13_completed_summary_v1.json','Earlier finite CPU wave: preserve individual scope; superseded process status only.'),
 ('R14-native-guard-confirmation','COMPLETE_REGIONAL_NATIVE_INVERSES','research_round14_verified_facts.json','Eight regional archive pairs save 2587 B; warm-only 415.558 ideal B; no complete-package win.'),
 ('R14-constructors-608','COMPLETE_ALL_PAID_INVERSES','research_round14_constructor_analysis_v1.json','608 paid cases; frozen right-context saves 9441 B vs Markov on confirmation but loses 1037000 B to zstd.'),
 ('R14-full-serialized-inverse','COMPLETE_FOUR_EXACT_1GB_FILES','research_round14_full_serialized_verification_v1.json','Independent parse/decode of all four serialized full raw proxy archives; not full native package.'),
 ('R14-group-weight-storage-v1','COMPLETE_FINITE_435_TENSOR_EXACT_SWEEP','research_round14_summary_v1.json','Grouped best 2999272 B versus original 2978039 B; actual detailed result in batch evidence.'),
 ('R14-word-costs-v2','COMPLETE_16_WARM_REGION_DIAGNOSTIC','research_round14_word_cost_summary_v2.json','Exact word-event cost and offline frequency diagnostics; not trained masking.'),
 ('R14-native-cpu-preflight-v1','PASS_NEUTRAL_PARITY_AND_SIX_EXACT_INVERSES','research_round14_oct9_progress_response.json','Native encode/decode preflight passed; neutral archive and Q16 equal pinned.'),
 ('R14-native-dispatch-v3','COMPLETE_FOUR_VERIFIED_PRIVATE_CPU_PUSHES','research_round14_oct9_progress_response.json','Four four-worker private CPU commits submitted; no long-run quality or resource result yet.'),
 ('R14-ppmd-real-failure','FAILURE_REPRODUCED_NO_QUALITY_AGGREGATE','research_round14_oct9_progress_response.json','Three direct real-input pyppmd-I failures; H also corrupts one input; repair remains open.'),
]
reg=project_path('results/registry.jsonl', base=R);have={json.loads(x)['id'] for x in reg.read_text(encoding='utf-8').splitlines() if x.strip()}
with reg.open('a',encoding='utf-8') as f:
    for id,status,file,outcome in rows:
        if id in have:continue
        assert (project_path(file, base=R)).exists()
        f.write(json.dumps({'id':id,'status':status,'recorded':now,'outcome':outcome,'gate':'No family-wide impossibility; full package, global state and eligible CPU/RAM require separate evidence.','evidence':{'path':file,'sha256':sha(file)},'GPU':False,'paid_usd':0})+'\n')
print(json.dumps({'updated':now,'coverage_entries':96,'round14_direct_or_pending_mappings':len(updates),'registry_entries':len(have)+sum(r[0] not in have for r in rows)}))
