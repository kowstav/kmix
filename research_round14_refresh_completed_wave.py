from pathlib import Path
import datetime,hashlib,json,shutil
R=Path(__file__).resolve().parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(name,data):(R/name).write_text(data,encoding='utf-8')
old=R/'historical_reports/research_round7_checkpoint_20261009_early.md'
if not old.exists():shutil.copyfile(R/'research_round7_checkpoint.md',old)
text('research_round7_checkpoint.md','''# Current continuation checkpoint — round 14

Updated 9 October 2026 after the completed component/order wave and new confirmation submissions.
Read **PENDING_EXPERIMENTS_HANDOFF.md first**: six-row queue followed by detailed
procedures, exact source/input identities, equations, commands and failure rules.
Current session **356740330**, kernel **284fe56b-f03b-4011-8af5-7a68e651ec5e**.
Always check for a newer user URL; keep signed credentials out of reports.

The managed Goal remains usageLimited. Never resume, replace or bypass it.
The 8 October auto-review rejection was respected. Current manual work follows
renewed user instructions and normal reviewed access. $0 spent, no GPU/rental.
Research week ends 11 October; no automatic extension.

## Completed and locally preserved — do not relaunch

Four development CPU notebooks (word/match/indirect pruning, output FP32) all
completed four matched pairs, 32 actual native archives, every inverse exact.
Neutral archives AND Q16 probabilities agree across hosts. Signed whole/warm gains:
word −153/−73.649 B; match −2/−5.737 B; indirect +19/+7.416 B; FP32 +7/+3.438 B.
Match reduces measured encode/decode CPU 4.63%/4.88% and regional RSS about 24 MiB;
word saves 9.49%/1.82% CPU and about 42 MiB. These are finite resource trades,
not qualified global speed or compression gains. Effective cores 3.75–3.94.

Repaired native article-order sweep: all 160 paid archives invert. Frozen graph
loses 1594/1577 B on confirmation at PPMd order 8/16. Python-backend corruption
evidence is preserved. Native backend fixes the operational blocker without
claiming its upstream root cause was diagnosed. Different live/commit 7z versions
are recorded and never mixed in a size comparison.

Local analysis: research_round14_native_wave_analysis_v1.json.
Local bundle: research_round14_native_wave_compact_v1.zip, 45,063,335 B,
SHA dbff4696be32970c23d5bb24c0c027999c17e3f51de88cc3b5362dda55ce4365;
all 310 entries CRC/SHA verified and extracted in research_round14_native_wave_evidence.
All native/order archives are local; 32 large Q16 traces remain in private outputs.
15-entry real-failure bundle and 10-entry native CPU binary/source bundle also verified.

Earlier verified evidence: guard +2587 actual B across eight regional pairs,
+415.558 warm-only ideal B; 608 complete constructor cases; four exact full 1 GB
raw-proxy reconstructions; grouped weight storage loses 21233 B/model copy;
16 exactly aligned native word-cost windows. See integrated report for scope.
No complete-package record win, 20% result, global optimum or all-96 completion.

## Active and ready-to-run

1. FOUR confirmation-A commits were verified at 11:49 UTC:
   chaoscpp/hutter-r14-{prune-word,prune-match,prune-indirect,output-fp32}-confirm-a-v1.
   Each has four pinned workers, IDs 8,10,12,14, paired 3 MiB histories/2 MiB warmup.
   Source SHA 4b17b53dc08664d64007fdd5768d4fd3ffd567f0928fc2ad54d4b7c937358ac8.
   Receipt hp_round14/confirm_a_dispatch_v5.json; inspect status, do not duplicate.
   B-wave IDs 9,11,13,15 are PREPARED, NOT SUBMITTED. After A finishes normally:
   python3 /kaggle/working/research_round14_dispatch_confirmation_worker.py --role b
   Inspect partial receipts and actual five-CPU-commit quota before launching.

2. Exact guard storage builds COMPLETE in the live session:
   hp_round14/guard_storage_build_v2.json and guard_storage_binaries_v2/.
   UPX bytes: neutral 209568; guard raw 232008; packed 218752; packed16 218608.
   Raw neutral and raw guard hashes match earlier compiled binaries exactly.
   The new tables match all 77826 frozen values in Python and local C++.
   Native exact-law/UPX parity is RUNNING under
   hp_round14/guard_storage_parity_v1/manifest.json, worker PID 562 in this session.
   Four 64 KiB guard variants plus 16 KiB packed neutral; four CPU lanes; 25-min cap.
   Do not transfer quality claims until terminal PASS and Q16/archive identity.
   V1 failed before compilation on CRLF-vs-LF SHA mismatch; v2 canonical bytes
   fixed it. Keep both failures and fixes. No original artifact was overwritten.

3. Guard×match combination, lexical structural experts and paid grammar templates
   remain implementation work, with precise finite protocols in the handoff.
   Do not report them as launched. Full global-state qualification and GPU pilot
   remain separate. Source/model hashes and $70 pilot rules are in the handoff.

## Preservation, cleanup and reporting

Preserve new packed binaries/source ZIPs and parity output locally when terminal.
Current working space is tight; put bulky scratch in /root. If the session dies,
working files/private committed outputs survive; root PIDs/paths do not.
Collectors must exhaust next_page_token and verify every output count/member hash.
Existing collector names the development jobs; adapt its fixed ref list and
versioned paths for confirmation before running it. Never repeat its old dispatch.

Old asset cleanup: only 480078284 B of verified duplicates, exact ledger in
research_round14_detail_preservation.json and research_round14_pull_manifest.json.
Article-order run cleaned 12608 newly generated temporary files (61324909 B),
preflight 70 (1288112 B); final archives retained. No original model/data deleted.

Update research_round14_report.md, research_round14_shortlist.md, the 96 coverage
delta, results/registry.jsonl and this checkpoint after material outcomes.
Do not rerun old report generators blindly: their historical text predates this wave.
''')
p=R/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('| [Current CPU execution]', '| [Pending experiments — read first](PENDING_EXPERIMENTS_HANDOFF.md) | Six-work-package queue, exact procedures, commands, mathematical gates and implementation status |\n| [Current CPU execution]') if 'Pending experiments — read first' not in s else s;p.write_text(s,encoding='utf-8')
p=R/'research_round14_96_coverage.json';m=json.loads(p.read_text(encoding='utf-8'))
updates={
'A31':('COMPLETE_DEVELOPMENT_CONFIRMATION_SUBMITTED','All three pruning arms independently invert on four paired development regions; match loses 2 B for measured CPU/RAM savings. Confirmation A submitted, B frozen/prepared.',['R14-native-component-wave-v1','R14-confirmation-a-dispatch-v5']),
'A43':('COMPLETE_OUTPUT_ROUNDING_DEVELOPMENT','FP32 output saves 7 actual B/3.438 warm-only ideal B on four pairs, all exact; confirmation A submitted. Weight QAT remains separate.',['R14-native-component-wave-v1','R14-confirmation-a-dispatch-v5']),
'A44':('COMPLETE_FINITE_PAID_NATIVE_ORDER_SWEEP','Replacement native PPMd-H completed all 160 inverses. Frozen graph loses 1594/1577 B at two confirmation orders; upstream Python failure preserved. Not all ordering descendants rejected.',['R14-native-article-order-v2']),
'A42':('REGIONAL_GUARD_CONFIRMED_STORAGE_ENGINEERING_ACTIVE','Existing guard +2587 actual regional B; exact table-storage builds cut packed executable by 13400 B/copy. Native storage parity pending; no full package win.',['R14-native-guard-confirmation','R14-guard-storage-build-v2']),
'A93':('NATIVE_PARITY_AND_INVERSE_GATES_PASSED_NEW_GATE_ACTIVE','32 component/precision development archives invert; neutral Q16/archive match across hosts. Packed-guard native gate running; all-435 training parity remains separate.',['R14-native-component-wave-v1','R14-guard-storage-build-v2'])}
for e in m['entries']:
 if e['id'] in updates:e['round14_state'],e['round14_actual_work'],e['round14_evidence_ids']=updates[e['id']]
m['updated']=now;text(p.name,json.dumps(m,ensure_ascii=False,indent=2)+'\n')
lines=['# All 96 ideas: round-14 evidence delta','','All original per-idea rigor/protocol/dependency fields remain in the JSON and [detailed prior ledger](research_round13_96_coverage.md). Read [pending work](PENDING_EXPERIMENTS_HANDOFF.md) for executable next steps. A finite negative screen is not a universal impossibility proof.','','| ID | Idea | Round-14 direct work | Evidence IDs |','|---|---|---|---|']
for e in m['entries']:lines.append('| '+e['id']+' | '+e['title'].replace('|','/')+' | '+e['round14_actual_work']+' | '+(', '.join(e['round14_evidence_ids']) or '—')+' |')
text('research_round14_96_coverage.md','\n'.join(lines)+'\n')
reg=R/'results/registry.jsonl';have={json.loads(x)['id'] for x in reg.read_text(encoding='utf-8').splitlines() if x.strip()}
rows=[
('R14-native-component-wave-v1','COMPLETE_32_NATIVE_ARCHIVES','research_round14_native_wave_analysis_v1.json','Finite development quality/resource trades; every inverse exact; no population or global-history claim.'),
('R14-native-article-order-v2','COMPLETE_160_PAID_INVERSES','research_round14_native_wave_analysis_v1.json','Native backend completes full frozen split; selected graph loses 1594/1577 B on confirmation.'),
('R14-group-storage-evidence-correction','EVIDENCE_POINTER_CORRECTION_ONLY','research_round14_batch_evidence/hutter-r14-group-weight-storage-v1/group-storage/manifest.json','Corrects earlier registry pointer to the exact grouped manifest; same experiment, not additional evidence. Best 2999272 B, loses 21233 B/copy.'),
('R14-confirmation-a-dispatch-v5','PREPARED_AND_REMOTE_SUBMISSION_VERIFIED','kaggle_cpu_round14/prepared_confirm_v5.json','Four A commits verified; four B prepared but not submitted. Preparation manifest is source identity, remote receipt is separate.'),
('R14-guard-storage-build-v2','BUILDS_MEASURED_NATIVE_PARITY_PENDING','research_round14_packed_tables_v2.json','Exact table integer data reconstructed; packed native build measured remotely; final native parity is a distinct pending gate.')]
with reg.open('a',encoding='utf-8') as f:
 for id,status,name,outcome in rows:
  if id in have:continue
  p=R/name;assert p.exists();f.write(json.dumps({'id':id,'status':status,'recorded':now,'outcome':outcome,'evidence':{'path':name,'sha256':sha(p)},'GPU':False,'paid_usd':0})+'\n')
print(json.dumps({'updated':now,'coverage':len(m['entries']),'handoff':'PENDING_EXPERIMENTS_HANDOFF.md'}))
