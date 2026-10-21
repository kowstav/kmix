# Pending experiments: short queue and executable handoff

Updated **9 October 2026, 17:36 UTC**. Read this first when continuing the project.
The latest session is **356823832**; its current kernel is
`be23f85f-e859-4264-94e8-a7ed65762c66`. Read the newest user message in case either
has changed. Never put the signed session URL or Kaggle token in a report/notebook.

## Small pending list

| Order | Experiment | Current state | What the next agent should do |
|---|---|---|---|
| P1 | Confirm component pruning and output precision | A-wave complete and verified locally; four **B-wave commits submitted** | Collect B without relaunching; compare all eight matched regions and repeat uncertain timing |
| P2 | Make the guarded final predictor cheap enough to package | Four builds and actual 64 KiB native parity complete | Preserve the verified parity; qualify full-run RAM/startup and complete package price |
| P3 | Combine the guard with match-model pruning | Development complete; fixed confirmation A submitted, B prepared | Collect A; submit the unchanged joint B after A completes; assess payload/code/RAM together |
| P4 | Port structural copy/field experts to the lexical coder | Older pipeline has evidence; lexical port **not implemented** | Build a causal parser and small exact-copy experts, first proving token/state alignment and neutral fallback |
| P5 | Paid grammar-template/backoff descendant | Conditional bag sweep finished; new template branch **not implemented** | Implement a complete reversible codec with charged templates, edits, selectors and layout; run matched controls |
| P6 | Global native qualification, then GPU pilots | Full native global run and stable retraining **not done** | Qualify the selected complete package on a persistent eligible CPU host; request GPU session for the parity-gated pilot |

This is six work packages, not a claim that six tests exhaust all 96 ideas. The
complete per-idea dependencies, actual historical testing, stronger descendants
and reopening conditions remain in [the 96-idea ledger](research_round14_96_coverage.md)
and its JSON. Do not silently mark unimplemented architectures complete.

## Latest continuation: 9 October, 17:36 UTC

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

At 17:36 UTC all five current CPU jobs were verified RUNNING: the four component
B jobs and joint A. Each is configured for four pinned compute workers. Current
working disk free space is 73,785,344 B. The collector deliberately stops if its
conservative uncompressed-size-plus-20-MiB ZIP reserve does not fit; preserve the
scratch outputs and free only verified duplicate evidence with a deletion ledger.
Do not remove models, source, input corpus or sole copies to make room.

## Completed work: reuse it

The previous five notebooks are **COMPLETE**, with terminal experiment manifests,
not merely successful submissions. The local archive
`research_round14_native_wave_compact_v1.zip` is 45,063,335 B, SHA-256
`dbff4696be32970c23d5bb24c0c027999c17e3f51de88cc3b5362dda55ce4365`.
All **310 entries** were CRC/SHA checked and extracted into
`research_round14_native_wave_evidence/`. It contains all 32 native candidate/control
archives and all 160 paid article-order archives. Eight probability traces per
native notebook remain in its private committed output; compact collection did
not download those traces. Do not call the compact bundle a full trace backup.

Development results, four matched 3 MiB regions, with the final 1 MiB scored warm:

| Arm | Whole-archive saving, B | Warm-only saving, ideal B | Encode CPU reduction | Decode CPU reduction |
|---|---:|---:|---:|---:|
| Remove word group | −153 | −73.649 | 9.49% | 1.82% |
| Remove match group | −2 | −5.737 | 4.63% | 4.88% |
| Remove double-indirect group | +19 | +7.416 | 3.32% | −0.012% |
| Keep final transformer output in FP32 | +7 | +3.438 | 0.96% | 1.62% |

Every inverse is exact; every neutral archive and Q16 trajectory agrees across
the four notebooks. Aggregate CPU reductions are finite matched-host measurements,
not precision estimates or proof of production speed. Match pruning saves roughly
24 MiB per regional run; word pruning roughly 42 MiB. **Do not sum RSS over regions
and call it one run's memory reduction.** Effective CPU use was 3.75–3.94 cores.

The original Python PPMd backend failed real-data inverses. Its failures remain
preserved. A separately implemented native PPMd-H container passed the failed
inputs and then all 160 planned cases. Frozen rare-word graph loses 1,594 B
(order 8) and 1,577 B (order 16) on eight confirmation regions. Do not rerun
this same negative screen or select its successful subset. A different order
search needs a new causal mechanism and protocol; no universal rejection follows.
The committed image used 7-Zip 23.01; the live preflight used p7zip 16.02. Both
identities are recorded. All committed archives independently inverted; sizes
from the two versions are not mixed into one comparison.

Earlier: guarded native predictor saves 2,587 actual regional bytes and 415.558
warm-only ideal B on eight confirmation regions. Paid coarse-right grammar earns
a narrow conditional signal but loses to full gzip/zstd. Exact grouped weights
lose 21,233 B per copy. Full literal/OOV masking and mature learned TTL remain
untested, not disproved. See [integrated results](research_round14_report.md).

## Common execution and mathematical contract

Work locally in `C:/Users/91707/Downloads/compression_cmix`. On Kaggle use `/root`
for scratch, `/kaggle/working/hp_round14` for compact durable evidence, and private
datasets/committed outputs for durable large inputs. The new session had about
186 MB free in working before the latest 45 MB evidence bundle. Do not copy full
probability traces there. Models and original corpus must remain preserved.

Five concurrent committed CPU slots plus the live session were observed. Do not
assume six or seven batch slots or bypass a rejection. Each compute notebook uses
four independent `ProcessPoolExecutor` processes, `fork`, one pinned CPU ID each,
and `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=NUMEXPR_NUM_THREADS=1`.
Use `hutter_research/cpu_round13_jobs.py::initialize_lane`. Four independent
regions/configurations may run concurrently; a single causal adaptive stream must
retain its bit order. `make -j4` is appropriate for a live native build. Record
worker user+system CPU divided by wall time; four configured workers alone is
not evidence of four-core use. Include subprocess CPU for native codec probes.

Optimize actual package bytes

    S = B_payload + Σ_a m_a B_a,
    G = S_baseline − S_candidate.

Count encoded selectors, templates, rare/literal residuals, permutations, framing,
models, dictionaries and the actual executable copies. Positive G is better.
For a warm region use the actual coded Q16 probability of each realized bit:

    L = −Σ_t log2(y_t q_t + (1−y_t)(1−q_t)),
    G_warm_bytes = (L_baseline − L_candidate)/8.

This ideal cost is not the serialized archive byte count. A 3 MiB archive includes
the first 2 MiB reset/warmup; its last 1 MiB cost does not. None of these regional
resets is a full-file global-state snapshot. Prefix-visible features update only
after their target has been coded; future-aware encoder choices require paid
side information or an exactly reproduced decoder-side search.

Keep CPU, RAM and bytes as a measured Pareto vector. A CPU saving does not create
an assumed bit saving. Eight clusters are below the ten-cluster bootstrap gate;
report descriptive per-region effects instead of invented confidence intervals.
Do not treat adjacent warm windows as independent articles. Use new untouched
mechanism-specific confirmation after development selection and preserve its freeze.

The managed Goal is **usageLimited**; never resume or replace it automatically.
Respect actual account, tool approval, runtime, spending and research-week limits.
Paid spending is $0; no rental has been launched. Existing week ends 11 October.

## P1 — confirmation and reliable CPU/RAM trades

Code: `hutter_research/cpu_round14_native_ablation.py`,
`hutter_research/cpu_round13_native.py`, and
`research_round14_dispatch_confirmation_worker.py`.
Registered rationale/gates: `research_round14_confirmation_freeze_v1.md`.

Frozen source bundle `kaggle_cpu_round14/sources_confirm_v5.zip` has SHA
`4b17b53dc08664d64007fdd5768d4fd3ffd567f0928fc2ad54d4b7c937358ac8`.
`prepared_confirm_v5.json` stores each main.py hash and exact input references;
`kernels_confirm_v5.zip` contains all eight prepared private CPU notebooks.
Remote copies have `.zip.dat` suffixes to prevent notebook interpretation.

The four A references are `chaoscpp/hutter-r14-<arm>-confirm-a-v1`, where `<arm>`
is `prune-word`, `prune-match`, `prune-indirect`, or `output-fp32`. All four push
receipts were verified at 11:49 UTC. **Do not submit A again.** Read
`hp_round14/confirm_a_dispatch_v5.json` and CLI status. A uses IDs 8,10,12,14;
B uses 9,11,13,15. B was submitted at 17:31 UTC. No settings change is allowed between A and B.

Historical launch command below: B has now been submitted; **do not rerun it**:

```bash
python3 /kaggle/working/research_round14_dispatch_confirmation_worker.py --role b
```

It verifies the immutable source, native preflight, existing references and A
completion. A failed/partial dispatch must be inspected; do not rerun it wholesale.
If the live session replaced `/root`, restore from the working ZIPs. Do not needlessly
rebuild models. Input datasets:

- `chaoscpp/hutter-r13-four-lane-cpu-assets-v1` (regions and original assets).
- `chaoscpp/hutter-r14-native-cpu-assets-v1` (five native binaries and source/parity evidence).

Each arm performs four baseline/candidate pairs, two separate encoder/decoder
processes per archive. Pair order rotates by region. A 10.3-hour deadline stops
an overlong job; failure must remain visible. Prior pair notebooks took about
4.46–5.62 hours, a planning observation rather than a runtime guarantee.

Ready collector: `research_round14_collect_confirmation_worker.py`. Exact uploaded
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

Timing follow-up: if a proposed speed gain is comparable with paired variability,
run A/B/B/A on the same two registered regions, separate encode/decode, same core
affinity and process initialization. Four lanes can be two regions × two repeats.
Keep every run, include startup, and report per-pair CPU differences. Never use
the faster VM's absolute baseline against another VM's candidate. Confirm full
production RSS separately; regional peak memory cannot qualify the full stream.

## P2 — exact table storage and packed executable cost

Code: `hutter_research/pack_probability_tables.py`, frozen original
`probability_tables.bin/.inc`, new `probability_tables_packed.inc`, and
`tests/probability_table_storage_exact.cpp`.
Build worker: `research_round14_build_packed_guard_v2_worker.py`.
Current remote manifest: `hp_round14/guard_storage_build_v2.json`.
Completed UPX sizes: neutral 209,568 B; raw-table guard 232,008 B; packed-table
guard 218,752 B; packed 16-feature guard 218,608 B. The smallest guard is 13,400 B
per copy smaller than the raw-table guard, but 9,040 B larger than matched lab
neutral and 20,372 B larger than the historical production executable. This is
why raw-table bytes saved must not be confused with full-package improvement.
Native parity worker `research_round14_guard_storage_parity_v2_worker.py` completed successfully;
read `hp_round14/guard_storage_parity_v2/manifest.json` before starting anything.
It compares raw/packed/slim/UPX guard on 64 KiB and packed neutral on 16 KiB against
the already preserved pinned result. Its declared deadline was 25 minutes. Four guard cases actually coded 65,536 B and the neutral case 16,384 B; all five independently inverted.

**Scope correction:** v1 incorrectly labelled its result 64 KiB because
`archive_case(..., preflight=True)` always truncates to 16 KiB. Its actual 16 KiB
parity passed. The original manifest was backed up; the current v1 status now
explicitly says 16 KiB only. V2 calls `preflight=False`, passes an explicit
`expected_bytes` contract, and asserts every returned row's byte count. The two
regression tests are in `tests/test_native_input_contract.py`; run them on Linux
(Windows lacks the harness's `resource` module). Do not promote a label over its
actual trace/input length. Source bundle for this fix is `sources_scope_gate_v7.zip`,
SHA `4a417983c3f161098492057f2ea3829bed6fd09722a17fd1bc0c4dd6bc808e43`.

The finite search compares RLE of first and second integer differences with
ZigZag/base-128 varints. No approximate log, exp or sigmoid is evaluated while
coding. All **77,826** values must match the frozen arrays exactly. Selected
stored streams are 11,063 B (stretch), 4,227 B (squash), 8,455 B (odds), versus
163,846 B of raw tables. Decoder code, runtime arrays and startup cost also count.
These asset bytes alone are not executable or package savings.

The generated header must be uploaded as exact bytes. Its LF-byte SHA is
`6eb41d6bd3c78ffdaa83854e374eb7ef4167e97f27b305c4debbd8308114e059`.
Version 1 caught a Windows text-newline mismatch before building; that failure
is retained. Version 2 uses `write_bytes` and binary transfer. Do not weaken SHA
validation by accepting arbitrary newline or content differences.

Four builds: neutral/raw; guard/raw; guard/packed; guard/packed with 16 features
instead of 24. The last arm removes only eight permanently zero memory features
from this particular native guard. It is invalid for a learned-memory arm. All
remaining update loops, counts, rates, contexts and Q16 rounding remain identical.
Use the pinned Clang/LLD 17 flags from the build manifest, not GCC or fast-math.
UPX 3.96 with `--lzma -9` is applied to independent copies. Every raw and packed
binary and full source archive is preserved; never overwrite the pinned baseline.

Required native gate before accepting size savings:

1. Rebuild neutral and match the pinned 16 KiB archive AND every Q16 probability.
2. Guard/packed and guard/packed16 must match guard/raw at every Q16 probability
   and archive byte on 16 KiB, then one registered ≥64 KiB region. Independent
   decoders for raw and UPX variants must reconstruct exactly.
3. Record UPX-compressed executable sizes for **both** baseline and candidate,
   not raw ELF differences as production cost. The historical package used
   UPX-packed executables counted twice (198,236 B each in its ledger).
4. Measure startup/RSS and verify the packed-table arrays fit the full-run limit.
   Current regional data do not prove this. Preserve the original frozen table
   hash and exhaustive C++ comparison output along with native probability hashes.

Only after this gate is the measured guard probability law transferable to the
smaller implementation. Any Q16 difference makes it a new candidate requiring
quality evaluation; do not call it an exact implementation optimization.

## P3 — guard × match-pruning interaction

Runnable implementation: `hutter_research/cpu_round14_guard_match.py` and
`research_round14_guard_match_pipeline_worker.py`. The development pipeline and
its notebook are **complete; do not rerun them**. Its frozen source SHA is
`68ec99890423ef99a9f991e65d5f54e1ff8fa4c2b3a4634a3da752fb106fae7e`.
Prepared historical files remain in `kaggle_cpu_round14/*guard_match_v6*`.
At 12:06 UTC in the previous session, its parent was held before submission
because the first storage test had a false input-length label. The corrected
64 KiB gate passed at 12:19 and released that parent; the original build,
four 16 KiB preflights, private asset creation and verified submission completed.
Receipt: `hp_round14/guard_match_scope_gate_release_v2.json`. Old process IDs
are not valid restart targets in this new session. The unchanged binaries are
now undergoing the confirmation described at the top of this document.

This requires a new binary, not a sum of the two previous savings. It restores the
140-entry source archive from P2, use `HP_R13_HEAD=2`, `HP_R14_ABLATION=2`,
`HP_R14_OUTPUT_FP32=0`, with all other flags unchanged. First confirm that the
native final-head capture still receives its registered 14 mixer inputs; failure
requires a new explicit feature mapping rather than bypassing the assertion.

The four conceptual cells are native neutral N, guard G, match-pruned M, and combined GM.
On identical development IDs 0,2,4,6, define gains relative to N and interaction

    I = (B_N−B_GM) − (B_N−B_G) − (B_N−B_M)
      = B_G + B_M − B_N − B_GM.

Its sign is unrestricted. Use whole-archive AND warm-only values separately.
The useful marginal for adding the guard after pruning is `B_M−B_GM`. The new
job directly measures **G−GM**, i.e. pruning conditional on the guard; its JSON
keys `guard_marginal_actual_bytes` and `guard_marginal_warm_ideal_bytes` store that
explicit G−GM quantity. Combine these with the completed matching N/M archive
rows only after validating identical input/region/binary identities. Do not
misread those keys as M−GM or as a new four-cell same-host timing experiment. Charge
the combined binary, not two alternative complete executables. Do not sum noisy
cross-host CPU estimates; run G/GM and N/M as matched pairs on each host, or all
four cells where the 10.3-hour limit permits. Two notebooks can run the two pairs
in parallel. Keep original state trajectories and both independent inverses.

New binary must pass the short native reconstruction gate before any long commit.
Use the existing `archive_case` harness with distinct versioned asset manifest,
source hashes and names. If development is promising, freeze the exact combined
binary and validate on the eight confirmation regions. A changed learning rate,
feature map or table value is a new model, not a continuation of the same trial.

## P4 — lexical structural experts

Start with the actual lexical `src/preprocess/preprocessor.cpp`,
`src/preprocess/dictionary.cpp`, `src/readalike_prepr/phda9_preprocess.h` and predictor source in
the preserved native tree, plus `research_round14_word_cost_worker.py` for the
diagnostic full WRT parser and its byte/event cursor checks. The diagnostic
parser uses future/offline labels and **must not become a free runtime feature**.
`hutter_research/wrt_classes.h` is only a byte classifier, not a full structural
parser. The original round-6 expert implementation must be located and hashed
in the preserved round-6/7 assets before porting; its 274,829 B gain belongs to
the older pipeline and cold structural regions, not to this lexical coder.

Implement a decoder-synchronous finite state machine for the transformed stream,
including dictionary escape/case state, page/field boundaries and all literal
fallbacks. Parse only already decoded bytes. Candidate stores: recent contributor
IDs, usernames keyed by earlier IDs, a bounded timestamp predictor, and exact
title copies only when the title has already been reconstructed. No raw XML `<`
test may be assumed valid on remapped WRT bytes. Reject/neutral-fallback on
unrecognized state; require parser re-serialization or cursor alignment checks.

For any byte-copy expert, specify a complete distribution, e.g.

    q_E(b) = (1−epsilon) 1[b=predicted] + epsilon/256,
    q = (1−alpha) q_native + alpha q_E.

The finite positive epsilon, prefix-visible alpha, exact byte-to-bit conversion,
integer CDF rounding and post-observation update order must be registered. A
copy miss still pays its residual. Bounded lookup capacity and eviction are
measured RAM, not an unlimited corpus index. If adding a native mixer input,
use a topology-matched neutral expert to isolate its benefit from the new mixer.

Test neutral alignment on arbitrary byte/escape tails; then full structural
regions with matched preceding history, exact archive inverse, and all-target
cost. Compare direct field predictor, wrong-key control, neutral expert and
joint predictor. Partition earlier/later **record blocks** for development and
confirmation, not overlapping token windows. Do not select only high-gain fields
after opening confirmation. First port the four mechanism-backed experts;
infobox/schema extensions are a later separately priced design.

## P5 — paid templates with right-context backoff

Existing primitives: `hutter_research/constructor_codec.py`,
`cpu_round14_constructor.py`, `article_order_native.py` framing examples and the
608 complete archives. New template codec and job **must be written**; do not
present an unimplemented filename as runnable.

Build an ordered constructor-run trie, preserving exact order and multiplicity.
Store templates derived from development or pay a full corpus-derived table.
Choose a direct branch or a template-plus-edit branch. The stream must encode
the branch, template ID, exact insert/delete/substitute operations, run length,
all literal/OOV bytes, case, punctuation and layout. The content-first stream
pays right anchors before using them. Decoder must reconstruct the original
bytes, not just grammatical text. Encoding may search all candidate templates
using future text **only because the chosen branch/ID/edit stream is paid**.

Proposed finite CPU grid: template caps 0/64/256, edit cap 0/1/2, and direct versus
paid-right context; add a matched wrong-right-anchor control. Pre-register the
cost of every selector and any table. Derive branch choice from the exact total
encoded length including headers, not an oracle minimum of uncharged losses.
Use a sequential prefix-built template dictionary as a separate descendant; its
encoder/decoder insertion and eviction must be identical and future-free.

For the four-cell direct/template × left/right comparison compute interaction
as in P3. Use spread original-text slices and independent article/region blocks,
equal baselines and four process lanes. Tiny dictionaries can be screened on
16 development MiB; freeze configuration, then 16 separate confirmation MiB.
Run a complete 1 GB serialized inverse only after a meaningful full-code gain
over zstd or a documented reason to test native transfer. A tiny conditional
grammar gain by itself does not justify another expensive full proxy run.

## P6 — full global history and GPU transition

The unchanged full native pipeline historically needs roughly 55–60 hours per
encode/decode and approaches the 10 GB RAM ceiling. A 12-hour Kaggle commit cannot
complete that by pretending independent slices share state. Options are a
persistent eligible CPU host or a new, exact whole-state checkpoint facility.
The latter must serialize transformer caches, all adaptive CM/PPMd/SSE state,
random/bit/arithmetic-coder state, pointers as stable indices, and parser/expert
state; prove resume equals uninterrupted Q16 and archive bytes before use.
This facility is not currently implemented. Do not promise that snapshots exist.

Freeze code/model/dictionary/permutation and measure the complete package,
independent full inverse/hash, CPU and peak RAM. Respect actual prize rules and
verify current official baseline/rules before claiming a record; the repository
contains historical and pending numbers that are not interchangeable.

After the finite CPU shortlist is frozen, request a GPU session. Follow
`research_round10_training_and_5090_plan.md`: zero-step CPU/GPU probability and
all-435-tensor export parity; then stable original-core continuation with equal
useful-target exposure and paired seeds. The correct rate objective is

    J = mean_token_CE + (m * lambda * R_model_bits)/T,

with actual model multiplicity m (historically two), not an unnormalized rate
penalty. A mixture-aware objective must not multiply by mixer trust twice.
Rarity diagnostics use floors 1/0.5/0.1, frozen thresholds 107/1392 and KL controls;
retain rare words' context and score every target. Measure gradient interaction
under the optimizer's actual preconditioning. Masking is not permission to omit
rare/literal residual bits. Word/TTL models require adequate sequence horizon
and target exposure; 128 tiny reset steps cannot settle the architecture.

Budget remains $70 maximum, no paid machine launched. Benchmark useful targets/s
on the actual rented hardware before quoting required 5090 hours. Existing
throughput scenarios are not measurements. Stop a rung for failed parity,
nonfinite loss, spend/time limit or clearly dominated paid rate/quality; retain
the failed evidence. Do not promise an after-training percentage or 20% gain.

## Preservation checklist for every continuation

Before launch, inspect live process/manifest and existing committed references.
After completion, save status, source/input/binary hashes, actual archive bytes,
independent inverse SHA, warm cost, all-target cost, CPU/RSS, selection timestamp,
per-region rows, errors and cleanup ledger. Verify ZIP CRC and every member SHA
locally; never expose temporary authenticated download URLs. Append a new result
ID rather than rewriting a failed record into a success.

The earlier cleanup removed only 480,078,284 B of hash-verified duplicates, logged
in `research_round14_detail_preservation.json` and `research_round14_pull_manifest.json`.
The native article-order worker also automatically removed 12,608 **newly created
temporary** codec files, totaling 61,324,909 B; all final 160 archives were kept.
Its preflight removed 70 new scratch files (1,288,112 B). These are distinct from
deleting existing research assets. No new-session original model/data was deleted.
