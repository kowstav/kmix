# Current continuation checkpoint — round 14

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
   Corrected native exact-law/UPX parity is RUNNING under
   hp_round14/guard_storage_parity_v2/manifest.json, worker PID 668 in this session.
   Four 64 KiB guard variants plus 16 KiB packed neutral; four CPU lanes; 25-min cap.
   Do not transfer quality claims until terminal PASS and Q16/archive identity.
   Parity v1 actually used 16 KiB despite its original 64 KiB label: preflight=True
   truncates inputs. The actual 16 KiB PASS is valid; label corrected and original
   manifest backed up. V2 uses preflight=False, explicit expected_bytes and returned
   byte-count assertions; source_scope_gate_v7 SHA is in the handoff.
   V1 failed before compilation on CRLF-vs-LF SHA mismatch; v2 canonical bytes
   fixed it. Keep both failures and fixes. No original artifact was overwritten.

3. Guard×match implementation and frozen job are now ready. Gated pipeline started
   12:03 UTC, PID 587: hp_round14/guard_match_pipeline_v1.json. Parent was SIGSTOP-held
   at 12:06 after the scope error above, before any long submission. Its children
   finish normally; v2 parity worker releases only this verified parent on genuine
   64 KiB PASS, recording guard_match_scope_gate_release_v2.json. Do not manually
   resume it on the old v1 result. The normal pipeline waits for storage
   PASS, builds the combined binary, tests two regions × two modes on four lanes,
   then creates a private asset and submits one fifth-slot notebook. Until a verified
   push exists, do not call that long notebook running. Source SHA
   68ec99890423ef99a9f991e65d5f54e1ff8fa4c2b3a4634a3da752fb106fae7e.
   Lexical structural experts and paid grammar templates remain implementation
   work, with finite protocols in the handoff. Full global-state qualification and GPU pilot
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
