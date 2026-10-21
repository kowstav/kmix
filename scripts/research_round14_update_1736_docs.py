
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
import json
R=project_root(__file__)
p=project_path('PENDING_EXPERIMENTS_HANDOFF.md', base=R);s=p.read_text(encoding='utf-8')
s=s.replace('Updated **9 October 2026, 12:08 UTC**','Updated **9 October 2026, 17:36 UTC**').replace('**356740330**','**356823832**').replace('284fe56b-f03b-4011-8af5-7a68e651ec5e','be23f85f-e859-4264-94e8-a7ed65762c66')
s=s.replace('Four **A-wave commits submitted**; four B-wave notebooks frozen and prepared','A-wave complete and verified locally; four **B-wave commits submitted**').replace('Collect A; submit B into released slots; compare all eight matched regions and repeat uncertain timing','Collect B without relaunching; compare all eight matched regions and repeat uncertain timing')
s=s.replace('Four builds complete; native parity running on four live CPU lanes','Four builds and actual 64 KiB native parity complete').replace('Require exact native probability/archive parity, preserve source and binaries, then price the complete package','Preserve the verified parity; qualify full-run RAM/startup and complete package price')
s=s.replace('Combined build/preflight implemented; parent explicitly held for corrected P2 scope gate','Development complete; fixed confirmation A submitted, B prepared').replace('Do not resume manually: corrected P2 worker releases it only after actual 64 KiB parity, then it submits once','Collect A; submit the unchanged joint B after A completes; assess payload/code/RAM together')
anchor='## Completed work: reuse it'
new='''## Latest continuation: 9 October, 17:36 UTC

All four component A notebooks completed; 132 compact entries and all 32 native
archives were downloaded and hash/CRC verified locally. Their neutral Q16 and
archive hashes match the historical pinned confirmation exactly. Signed actual /
warm ideal gains: word **−89 / −51.495 B**, match **−50 / −18.133 B**, indirect
**−24 / −0.760 B**, FP32 **+4 / +2.371 B**. This is only half the registered
confirmation set. Effective CPU use was 3.855–3.920 cores. Timing reversals require
counterbalanced follow-up; do not repeat earlier development speed claims as settled.

Joint development completed four G/GM pairs, every inverse exact: **−10 actual B**
versus G, **−6.746 warm ideal B** versus G, **+1,247 actual B** versus N. Interaction
is **−8 actual B**. Joint saves roughly 24 MiB RSS and 1,068 packed executable B
per copy versus G. This is a package/RAM hypothesis, not compression synergy.
Analysis: `research_round14_confirm_a_joint_analysis_v1.json` and reproducible
`research_round14_analyze_confirm_a_and_joint.py`.

P2 actual 64 KiB gate passed at 12:19 UTC and released the old parent normally.
The old session PID/hold instructions below are historical, **not current actions**.
No original model/data was deleted. Seven gate/hold/correction receipts are verified
under `research_round14_live_gate_receipts_356823832_v1_evidence/`.

Four component **B** submissions have verified receipts in
`research_round14_confirm_b_dispatch_v5.json`; do not run their dispatcher again.
Joint confirmation protocol is `research_round14_guard_match_confirmation_freeze.md`.
Frozen source `sources_guard_match_confirm_v8.zip` SHA:
`df8d5b7aaf8d9667a85ffe97f7671aca09e661bfe8df5402ef3f03fc607f4817`.
Its A job is `chaoscpp/hutter-r14-guard-match-confirm-a-v1`. Check the receipt
`hp_round14/guard_match_confirm_a_dispatch_v8.json` before any launch. After A
completes normally, B is ready with:

```bash
python3 /kaggle/working/hp_round14/dispatch_guard_match_confirmation.py.dat --role b
```

The source and both notebook ZIPs, prepared manifest and dispatcher are preserved
under `hp_round14/` with `.dat` suffixes. The dispatcher verifies frozen source,
64 KiB gate, predecessor completion, private CPU metadata and actual push URL.
It stops on duplicate, ambiguous result or failure; do not automatically retry.

## Completed work: reuse it'''
s=s.replace(anchor,new)
s=s.replace('B uses 9,11,13,15. No settings change is allowed between A and B.','B uses 9,11,13,15. B was submitted at 17:31 UTC. No settings change is allowed between A and B.')
s=s.replace('When all A jobs have completed and normal slots are free, the prepared B launch is:','Historical launch command below: B has now been submitted; **do not rerun it**:')
start=s.index('Collect with the paginated API pattern in');end=s.index('\nTiming follow-up:',start)
s=s[:start]+'''Ready collector: `research_round14_collect_confirmation_worker.py`. Exact uploaded
copy is `hp_round14/confirmation_collector_v1.py.dat`, SHA
`ec1adc3c3c1d14cb4d5d04ddfee38fa22eb511380051db653040ab00472e1272`.
It was tested against all 32 prior development archives and successfully collected
the actual A and joint development outputs. It never launches a notebook.

```bash
python3 /kaggle/working/hp_round14/confirmation_collector_v1.py.dat --wave b --tag b-YYYYMMDD-HHMM
```

Use a unique lowercase tag. `a` and `b` select the four component references;
`combo` selects **joint development**, not joint confirmation. For joint
confirmation, first extend the explicit reference selector and freeze a new
collector version; do not accidentally recollect development and label it new.
The collector follows every pagination token, checks path containment, preserves
failed terminal outputs, checks native archive hashes and recorded independent
inverse claims, and verifies ZIP CRC. Large probability traces remain in private
outputs, with omitted counts. It checks free disk before writing a durable ZIP.
Download its bundle and receipt locally, verify every member SHA using the pattern
in `research_round14_verify_new_bundles.py`, then analyze. A nonterminal snapshot
does not wait or restart work. Do not rerun the old development collector unchanged.
''' + s[end:]
s=s.replace('Native parity worker `research_round14_guard_storage_parity_v2_worker.py` is running;','Native parity worker `research_round14_guard_storage_parity_v2_worker.py` completed successfully;')
s=s.replace('Its declared deadline is 25 minutes.','Its declared deadline was 25 minutes. Four guard cases actually coded 65,536 B and the neutral case 16,384 B; all five independently inverted.')
s=s.replace('Prepared job is `chaoscpp/hutter-r14-guard-match-development-v1`; it is **not','Historical prepared job was `chaoscpp/hutter-r14-guard-match-development-v1`; at the earlier checkpoint it was **not')
p.write_text(s,encoding='utf-8')
append='''

## 9 October 17:36 UTC: confirmed A-wave and joint development

Four component A notebooks completed on IDs 8,10,12,14; their 32 native archives
invert exactly, and baseline Q16/archive hashes match the earlier pinned native
confirmation. Whole-archive / warm ideal signed savings:

| Arm | Actual saving B | Warm ideal saving B |
|---|---:|---:|
| Word pruning | -89 | -51.495 |
| Match pruning | -50 | -18.133 |
| Indirect pruning | -24 | -0.760 |
| Output FP32 | +4 | +2.371 |

Effective CPU use was 3.855–3.920 cores. CPU timing varies and some signs reverse;
development speed estimates are not established deployment gains. All four B
confirmation notebooks were successfully submitted; eight-region totals are pending.

Joint guard-plus-match development has eight exact archives over four pairs.
Against guard alone it adds 10 actual B and 6.745555 warm ideal B. Against native
neutral it saves 1,247 actual B and 233.362611 warm ideal B. The interaction is
-8 actual B and -1.009007 warm ideal B; individual savings are not additive.
Mean RSS reduction versus guard is approximately 24 MiB. Joint UPX executable
is 217,540 B, 1,068 B smaller than the exact packed guard. Confirmation advances
this fixed package/RAM tradeoff, not a synergy claim. Paired decode CPU fell 3.03%
but encoding was essentially unchanged; noisy regional signs require repeats.

The corrected actual 64 KiB guard storage gate passed (four guard variants plus
16 KiB neutral), with identical probability/archive hashes and exact independent
inverses. The false 64 KiB label from the earlier truncated test remains explicitly
corrected and preserved. Exact implementation size savings are now transferable
on the tested trajectory; full-stream CPU/RAM and full-package gain are unqualified.

Evidence: `research_round14_confirm_a_joint_analysis_v1.json`, 132-entry A bundle,
33-entry joint bundle, seven-entry gate receipt bundle; all locally SHA/CRC verified.
Current pending procedures: `PENDING_EXPERIMENTS_HANDOFF.md`. $0 spent, no GPU.
'''
for name in ['research_round14_report.md','research_round14_shortlist.md','research_round14_audit_delta.md']:
    p=project_path(name, base=R);p.write_text(p.read_text(encoding='utf-8')+append,encoding='utf-8')
p=project_path('research_round7_checkpoint.md', base=R);old=p.read_text(encoding='utf-8')
(project_path('historical_reports/research_round7_checkpoint_20261009_1210.md', base=R)).write_text(old,encoding='utf-8')
p.write_text('''# Current checkpoint — 9 October 2026, 17:36 UTC

Read PENDING_EXPERIMENTS_HANDOFF.md first. Current session 356823832, kernel
be23f85f-e859-4264-94e8-a7ed65762c66. Never save the signed URL/token in reports.
The Goal remains usageLimited: do not resume/replace it automatically. Manual
continuation follows renewed user authorization and normally reviewed tools.
Week ends 11 October. Paid spend $0; no GPU/rental or original model/data deletion.

Four component A commits COMPLETE and locally verified; four frozen component
B commits submitted successfully at 17:31 UTC. Do not relaunch. Receipt:
research_round14_confirm_b_dispatch_v5.json. B uses IDs 9,11,13,15 with four lanes.

Guard storage v2 actual 64 KiB gate PASSED and released its historical held parent.
Joint guard+match development COMPLETE; 33 compact entries/eight archives local.
Joint A confirmation dispatcher launched; check hp_round14/guard_match_confirm_a_dispatch_v8.json
for verified push/current job. Joint B is prepared, not submitted; run the .dat
dispatcher --role b only after A completes normally. No duplicate jobs.

New verified analysis: research_round14_confirm_a_joint_analysis_v1.json.
Detailed results and limitations appended to report, shortlist and audit delta.
All pending code/procedure/hash/byte-accounting details are in the handoff.
P4 lexical structural expert port and P5 paid template branch remain unimplemented.
No all-96 completion, record, 20% gain, global optimum or full-package win claimed.

Do not run old report generators blindly: they contain earlier-state snapshots.
Use the new confirmation collector, not the old development-only collector.
Preserve failed evidence and every deletion record. Previous detailed checkpoint:
historical_reports/research_round7_checkpoint_20261009_1210.md.
''',encoding='utf-8')
print('Updated handoff, checkpoint, integrated report, shortlist and audit delta.')
