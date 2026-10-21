# Handoff execution report: round 14 continuation (9–10 October 2026)

Prepared by Claude (Anthropic), working from `PENDING_EXPERIMENTS_HANDOFF.md`
(updated 9 Oct 17:36 UTC) in the new live session **356878808** (kernel
`968af08e…`). All times are UTC. No existing project file was modified; every
artefact below is a new file. The signed session URL and the Kaggle token appear
in no file. Paid spend remains **$0**; no GPU, no rental, the usageLimited Goal
was not touched.

**Short version.** I collected and verified everything the five finished notebooks produced, finished
the eight-region P1 comparison, submitted joint B exactly as frozen, and filled the remaining four slots with the
counterbalanced A/B/B/A timing repeats that P1 requires (after a live parity gate). I extended the P2 evidence
(parity, RAM, startup, package ledger). P4 and P5 remain unimplemented and P6 is blocked; neither was faked.

| Handoff item | Status now |
|---|---|
| P1 component pruning / precision | Wave B collected and verified; **all eight regions analysed** (§3); four timing repeats **running** |
| P2 guard packaging | Exact storage parity now verified on 12 MiB of confirmation trajectories; RAM-limit risk quantified; startup/RSS probe run; package ledger written (§6). Full-stream RAM still unqualified |
| P3 guard × match | Joint A collected and verified (interaction −1 B); **joint B running** |
| P4 structural experts | Not implemented (§7) |
| P5 paid templates | Not implemented (§7) |
| P6 global / GPU | Not executable here; needs your decision (§8) |
| Kaggle slots | **5 / 5 occupied** (§9) |

## 1. State found at pickup (23:20 UTC, 9 Oct)

* New session: fresh `/root`, persisted `/kaggle/working` (73,805,824 B free),
  no `/kaggle/input` datasets, nothing of ours running. Secret `kaggle_api_token`
  present (used only in-process).
* All five committed jobs listed in the handoff had finished normally (CLI status
  `COMPLETE`): the four component confirmation-B notebooks
  (`hutter-r14-{prune-word,prune-match,prune-indirect,output-fp32}-confirm-b-v1`)
  and joint confirmation A (`hutter-r14-guard-match-confirm-a-v1`). Joint B did
  not exist yet (correct: it may only be submitted after A completes).
* Receipts checked before any launch: `confirm_b_dispatch_v5.json`
  (four verified pushes, not rerun) and `guard_match_confirm_a_dispatch_v8.json`
  (verified push of joint A).

## 2. What I ran, in order

| Time | Handoff item | Action | Result |
|---|---|---|---|
| 23:25 | P3 | Froze **collector v2** (adds only `--wave joint-a/joint-b`; `combo` still means development) — `research_round14_collect_confirmation_worker_v2.py`, SHA `b993c7c4…` | Uploaded as `hp_round14/confirmation_collector_v2.py.dat` |
| 23:25 | P3 | Collected joint A, tag `joint-a-20261009-2325` | `TERMINAL_WAVE_SNAPSHOT`, 33 entries, 6,102,896 B, SHA `1f831834…`; 8/8 archives hash- and inverse-claim verified |
| 23:27 | P3 | Checked joint A completed **normally** (experiment `COMPLETE_FOUR_NATIVE_GUARD_MATCH_PAIRS`, guard baseline = historical guard on 4/4 regions), then ran the frozen dispatcher once: `dispatch_guard_match_confirmation.py.dat --role b` (SHA `73c55a2e…` verified first) | `COMPLETE_VERIFIED_PRIVATE_CPU_PUSH`, `chaoscpp/hutter-r14-guard-match-confirm-b-v1` v1, regions 9/11/13/15, main SHA `568dbf9a…` = prepared |
| 23:28 | P1 | Collected component wave B with the frozen **collector v1** (SHA `ec1adc3c…`), tag `b-20261009-2328` | `TERMINAL_WAVE_SNAPSHOT`, 132 entries, 23,862,317 B, SHA `868aa9e8…`; 32/32 archives verified |
| 23:30 | P1/P3 | Downloaded both bundles and receipts; verified ZIP CRC, bundle SHA and every member SHA against the receipt (`research_round14_verify_collected_bundle_v2.py`) | 33/33 and 132/132 entries verified; extracted to `research_round14_confirmation_compact_{joint-a-20261009-2325,b-20261009-2328}_evidence/` |
| 23:33 | P1/P3 | Analysis `research_round14_analyze_confirm_ab_joint_a_v2.py` → `research_round14_confirm_ab_joint_a_analysis_v2.json` | §3 and §4 below |
| 23:34–00:22 | P1 | Built, froze and gated the **A/B/B/A timing repeat** (§5) | Four private CPU notebooks pushed and verified: word 23:50, match 00:00, indirect 00:11, FP32 00:21 (each right after its own live gate passed); all RUNNING at 00:22 |
| 00:22–00:42 | P2 | Live parity/startup/RSS probe of neutral, raw-table guard, packed16 guard (raw and UPX) and GM UPX, A/B/B/A per pinned lane, 16 KiB; plus RAM-headroom analysis and package-price ledger | `COMPLETE_EXACT_PARITY_STARTUP_RSS_PROBE`: 16/16 hashes exact; packed16 adds +0.10–0.25 MiB RSS vs lab neutral; GM −23.7 MiB (§6) |

### Disk handling (no deletion)

The frozen collector reserves uncompressed size + 20 MiB before writing its ZIP.
Wave B needed about 88.8 MB while 67.7 MB was free. Rather than deleting anything,
one durable file whose identical copy is already SHA-verified locally
(`native_wave_compact_v1.zip`, 45,063,335 B, SHA `dbff4696…`) was copied to `/root`,
verified, unlinked from working, the frozen collector was run, and the file was
copied back and re-verified before the temporary copy was removed. Ledger:
`research_round14_relocation_ledger_b-20261009-2328.json`, final status
`RESTORED_VERIFIED_NO_NET_DELETION`. Working free space afterwards: 43,749,376 B.
**No model, source, corpus, evidence or sole copy was deleted.**

## 3. P1 results: all eight component confirmation regions (IDs 8–15)

Every archive independently inverts. In all 32 neutral runs the archive **and every
Q16 probability** equal the historical pinned native confirmation for that region,
and neutral is identical across all four arm notebooks (so attribution is valid).
Candidate binary hashes are identical between waves A and B. Signed effect =
baseline − candidate; positive is better (for CPU: positive = less CPU). Eight clusters are below the ten-cluster
bootstrap gate, so values are descriptive only (no interval).

**Totals over regions 8–15** (baseline archives total 4,491,669 B per arm):

| Arm | Actual saving B (8 regions) | Sign +/−/0 | Warm ideal B | All-target ideal B | Encode CPU reduction % (A / B / all) | Decode CPU reduction % (A / B / all) | Peak RSS saved, mean |
|---|---:|:-:|---:|---:|---:|---:|---:|
| Word pruning | -356 | 0/8/0 | -192.074 | -355.174 | -0.49 / +2.42 / +0.93 | +2.41 / +2.65 / +2.53 | +41.7 MiB |
| Match pruning | -92 | 1/7/0 | -39.021 | -90.822 | +3.32 / +0.38 / +2.05 | -2.93 / -2.64 / -2.80 | +23.7 MiB |
| Indirect pruning | -44 | 4/4/0 | -5.659 | -44.249 | -2.74 / +2.93 / -0.46 | -4.81 / +0.22 / -2.81 | +0.8 MiB |
| FP32 output | +14 | 6/0/2 | +4.894 | +13.958 | +2.44 / -2.38 / +0.03 | -0.06 / +3.34 / +1.57 | -0.1 MiB |

**Per region, actual B / warm ideal B:**

| Region | Word pruning actual / warm B | Match pruning actual / warm B | Indirect pruning actual / warm B | FP32 output actual / warm B |
|---:|---:|---:|---:|---:|
| 8 | -26 / -15.262 | -14 / -6.033 | +1 / -0.194 | +0 / +0.727 |
| 9 | -21 / -12.073 | -16 / -6.321 | +8 / +2.794 | +2 / +0.611 |
| 10 | -25 / -18.608 | -27 / -12.841 | -31 / -3.942 | +2 / +0.757 |
| 11 | -105 / -52.002 | -14 / -4.126 | +9 / +7.556 | +1 / +0.739 |
| 12 | -15 / -11.632 | -11 / +1.372 | +7 / +2.315 | +2 / +0.695 |
| 13 | -61 / -20.362 | -8 / -0.692 | -4 / -1.468 | +2 / +0.681 |
| 14 | -23 / -5.992 | +2 / -0.630 | -1 / +1.060 | +0 / +0.193 |
| 15 | -80 / -56.144 | -4 / -9.748 | -33 / -13.781 | +5 / +0.490 |

**Within-notebook timing decomposition.** Each notebook alternates which archive runs first. With d = baseline − candidate CPU, the order-balanced arm effect is mean(d), and the position effect (second run minus first run) is half the difference between candidate-first and baseline-first regions:

| Arm | Notebook | Wall h | Effective cores | Order-balanced encode effect s/region | Position effect (2nd−1st) encode s | Order-balanced decode s/region | Position decode s |
|---|:-:|---:|---:|---:|---:|---:|---:|
| Word pruning | A | 5.21 | 3.904 | -22 | -470 | +111 | -158 |
| Word pruning | B | 5.10 | 3.821 | +106 | -31 | +119 | +50 |
| Match pruning | A | 5.51 | 3.902 | +166 | -1067 | -137 | -38 |
| Match pruning | B | 4.52 | 3.771 | +15 | +283 | -100 | +168 |
| Indirect pruning | A | 5.32 | 3.855 | -124 | -301 | -217 | +65 |
| Indirect pruning | B | 3.49 | 3.826 | +90 | -17 | +7 | -29 |
| FP32 output | A | 5.13 | 3.920 | +108 | +34 | -3 | -124 |
| FP32 output | B | 5.14 | 3.769 | -105 | +222 | +144 | -429 |

Reading these results:

* **Word pruning** costs bytes in **8/8** regions (−356 actual B, −192.1 warm ideal B
  over the eight confirmation regions; total baseline 4,491,669 B). It saves about
  41.7 MiB of regional peak RSS. Its CPU reduction is +0.9 % encode / +2.5 % decode, with
  regional signs disagreeing (6 faster / 2 slower in each phase); the 9.49 % development encode saving did **not**
  replicate. It is a resource trade with a definite byte penalty, not a gain.
* **Match pruning** costs bytes in 7/8 regions (−92 / −39.0 B) and saves about
  23.7 MiB RSS. Encode CPU reduction +2.0 % (4 regions faster, 4 slower); decode **−2.8 %**
  (7/8 regions slower).
  The development decode saving (4.88 %) reversed on confirmation.
* **Indirect pruning** is byte-neutral within noise (4/4 signs, −44 / −5.7 B), saves
  only 0.8 MiB, and is slower on aggregate (−0.5 % encode, −2.8 % decode).
* **FP32 output** is the only arm that never loses: +14 actual B (6 positive, 2 zero)
  and +4.894 warm ideal B with **8/8** positive warm effects. The bit gain is tiny
  (≈0.0003 % of baseline) and its timing is noise (+0.03 % / +1.6 %).
* **Large time-position effects** explain the timing contradictions. Within a
  notebook each lane runs two archives back to back; the second run differs from
  the first by up to ±1,067 CPU s per encode (≈20 %), with a sign that changes from
  host to host. The registered alternating order cancels this only on average over
  regions; the per-region signs are dominated by it. Hence the counterbalanced
  repeat in §5. No speed claim is supported by the confirmation waves.

## 4. P3 results: joint confirmation A (IDs 8, 10, 12, 14)

The joint job's guard baseline is the **packed16 exact-storage guard**
(`5f6e0c7b…`). On all four regions its 3 MiB archive, every Q16 probability and the
warm bits are byte-identical to the historical raw-table guard (`752a774c…`).
G = guard, GM = guard + match pruning, N/M from component wave A on the same inputs
(binary identities checked). Byte interaction only; CPU is never compared across hosts.

| Region | G−GM actual B | G−GM warm B | N−GM actual B | N−GM warm B | Interaction actual B | Interaction warm B | Guard = historical | Encode CPU G/GM s | RSS saved G−GM |
|---:|---:|---:|---:|---:|---:|---:|:-:|---:|---:|
| 8 | -15 | -6.094 | +313 | +45.573 | -1 | -0.061 | yes | 4217 / 5022 | 23.9 MiB |
| 10 | -26 | -12.940 | +291 | +25.529 | +1 | -0.098 | yes | 5064 / 4257 | 24.0 MiB |
| 12 | -11 | +1.200 | +289 | +46.739 | +0 | -0.171 | yes | 4323 / 5050 | 23.8 MiB |
| 14 | +1 | -0.901 | +311 | +54.625 | -1 | -0.271 | yes | 5050 / 4171 | 24.0 MiB |
| **Sum** | -51 | -18.735 | +1204 | +172.467 | -1 | -0.602 | 4/4 | 18654 / 18500 | 23.9 MiB mean |

* Adding match pruning to the guard costs 51 actual B / 18.7 warm B over four regions
  (development: 10 / 6.7 B over four other regions) and saves 23.9 MiB RSS.
* Joint versus native neutral still saves 1,204 actual B and 172.5 warm ideal B.
* Interaction I = B_G + B_M − B_N − B_GM = **−1 actual B, −0.60 warm B**: the two
  effects are additive within noise. This is a package/RAM trade, not synergy.
* Timing: order-balanced GM is 39 CPU s/region faster to encode (0.8 %) and 148 s
  faster to decode (3.2 %), but the position effect in this notebook is **+805 s**
  (second run slower) — twenty times larger. Joint timing stays unresolved; the
  freeze prescribes A/B/B/A repeats if it remains inconsistent after B.
* Joint B (9, 11, 13, 15) is running; eight-region joint totals are pending.

## 5. P1 timing follow-up: counterbalanced A/B/B/A repeat

Rule (fixed before any B-wave value was read): repeat an arm/phase when development
proposed a CPU gain and the eight confirmation pairs disagree in sign or have |mean|
below one paired SD. All four arms qualify (indirect in encode only; its development
decode change was −0.012 %).

Design (`research_round14_timing_abba_freeze_v1.md`, SHA `8102775d…`): one private CPU
notebook per arm; four pinned fork workers via `initialize_lane`, thread variables 1;
lane tasks (8,AB), (8,BA), (9,AB), (9,BA), with A = neutral and B = arm. Each lane runs its two
archives on its own CPU through the unchanged `cpu_round13_native.archive_case`, so
per region the four runs form A/B/B/A in time. Host-time, lane and region effects
cancel in the order-balanced contrast when additive. Encoder and decoder are separate
processes, CPU includes process startup, every run is kept, archive/Q16 hashes are
compared with the confirmation references (a mismatch stops attribution), and per-pair
CPU differences are reported. Regions 8 and 9 were chosen by a fixed rule, the lowest
region of each confirmation half. 10.3 h deadline, no GPU, no internet.

Files: `hutter_research/cpu_round14_timing_abba.py` (new module),
`research_round14_build_timing_abba_batch.py`, `kaggle_cpu_round14/{sources_timing_abba_v9.zip
(c792a9fb…), kernels_timing_abba_v9.zip (dae6a077…), prepared_timing_abba_v9.json,
timing_abba_references_v9.json (e980e29c…), hutter-r14-<arm>-timing-abba-v1/}`,
dispatcher `research_round14_dispatch_timing_abba.py` (SHA `54245250…`), collector
v3 for the outputs (SHA `0c207312…`, adds `--wave timing`).

Live gate before any commit: the identical code path must reproduce the stored
16 KiB region-0 native preflight archive **and** Q16 hashes for neutral and the arm.
Attempt 1 (`hp_round14/timing_abba_preflight_v9/summary.json`) failed before running anything: the live runner did not create its `/root` scratch parents (`FileNotFoundError`). The committed notebooks default to `/root` and `/kaggle/working`, so they are unaffected. The failure is preserved, and attempt 2 is a new record (`v9b`). Attempt 2 ran each arm through the identical frozen code path (four pinned lanes, 2 × 16 KiB archives per lane). On every lane neutral and arm reproduced the stored archive **and** Q16 hashes. The summary is `PASS_ALL_FOUR_16KIB_PREFLIGHT_REFERENCE_PARITY` (23:38–00:21), with 3.81–3.88 effective cores. The gate also shows the design working: for word pruning the per-pair encode differences were +28.5/−7.7/+27.2/−9.4 s on AB/BA/AB/BA lanes. That is a −18.2 s time-position effect cancelling to an order-balanced +9.6 s. The dispatcher checks each arm's own gate manifest, the frozen hashes, both terminal confirmation collections, private CPU metadata and the push URL, and it refuses duplicates. All four receipts read `COMPLETE_VERIFIED_PRIVATE_CPU_PUSH` (version 1).

## 6. P2: guard packaging cost, storage parity, RAM and package price

**Parity is now much stronger than the 64 KiB gate.** The 9 Oct corrected gate
(guard raw/packed/packed16/UPX at 64 KiB, neutral UPX at 16 KiB) is preserved
unchanged. New evidence: the joint job's guard baseline *is* the packed16 build, and
on four 3 MiB confirmation regions it reproduces the historical raw-table guard's
archives and all 100,663,296 coded Q16 probabilities exactly (§4). Joint B will add
four more regions. The exact-storage implementation is therefore verified on long
trajectories, not only on a 64 KiB prefix. It is still a regional, reset-at-start
trajectory, not the full stream.

**RAM: the limit question is real and not settled.** Historical full lexth11c run:
compress peak **9,765,024 KiB** (9,999,384,576 B), decode 9,597,984 KiB. Under a
literal decimal 10 GB limit the compress headroom is only **601 KiB**; decode has
163.7 MiB. Under 10 GiB the compress headroom is 703.8 MiB. Regional peak-RSS
increments on the confirmation regions:

| Comparison (3 MiB regions) | Host relation | Encode increment, KiB | Decode increment, KiB |
|---|---|---:|---:|
| guard raw-table − pinned production neutral, regions 8–15 | same notebook | +432 … +844 (mean +576.5) | +380 … +888 (mean +637) |
| packed16 guard − pinned, regions 8/10/12/14 | different notebooks | +216 … +508 | +184 … +464 |
| guard+match (GM) − pinned, regions 8/10/12/14 | different notebooks | −24,204 … −24,004 | −24,224 … −23,828 |

The raw-table guard's regional increment exceeds the 601 KiB decimal headroom on
2 of 8 regions. The packed16 increment is below it but of the same order. A
regional increment is not the full-stream increment, so **whether G alone fits under
a literal decimal 10 GB limit is not established**. GM's ≈24 MiB reduction would
give ample margin if it carries over to the full stream, which is a concrete reason
to treat P3 as a package/RAM trade. The exact wording of the official RAM limit
(decimal GB or GiB) must be verified (P6 already requires checking current rules).
Only a full-stream run (P6) can qualify the peak.

**Startup / RSS probe (live session, no batch slot).** `research_round14_p2_startup_rss_probe.py`
(SHA `8f698ea5…`) ran 00:22–00:42 with 3.881 effective cores; the live session was idle afterwards. It used four pinned lanes, each an A/B/B/A
sequence on its own CPU, through the unchanged `archive_case` harness (separate encoder and independent
decoder, whole-process rusage including startup) on the first 16 KiB of canonical region 0. Status:
`COMPLETE_EXACT_PARITY_STARTUP_RSS_PROBE`. All 16 runs reproduced the stored 16 KiB archive and Q16 hashes:
neutral raw/UPX `1c2c2188…`; guard raw / packed16 / packed16-UPX all `ed0adaa8…`; joint UPX `d5001d57…`.
This is also a same-core re-check that the UPX executables decode identically.

| Lane (same CPU, A/B/B/A) | Encode CPU A−B, per repeat (s) | Decode CPU A−B (s) | Encode peak RSS B−A (KiB) | Decode peak RSS B−A (KiB) |
|---|---|---|---:|---:|
| A = neutral raw, B = guard packed16 | −1.80, +2.28 | −1.96, +0.63 | +256 | +172 |
| A = guard raw-table, B = guard packed16 | −4.22, −5.86 | −5.27, −2.18 | −1,524 | −1,160 |
| A = neutral UPX, B = guard packed16 UPX | −1.13, +3.55 | +0.63, −0.53 | +106 | +234 |
| A = guard packed16 UPX, B = GM UPX | +1.88, +5.84 | +7.52, +10.66 | −24,296 | −24,248 |

How to read this: each process costs about 150 CPU s at 16 KiB, almost all of it startup.

* The packed16 guard adds only +0.10 to +0.25 MiB of peak RSS over the matched lab neutral (raw and UPX).
  That is below the 601 KiB decimal headroom at this size.
* Packed16 uses 1.1–1.5 MiB less RSS than the raw-table guard.
* GM uses 23.7 MiB less than packed16.
* Neutral vs packed16 CPU differences are within ±2–4 s noise.
* The raw-table guard was 4–6 s (≈3–4 %) cheaper than packed16 in both repeats. Earlier 16 KiB parity runs
  showed the same direction (130 vs 136 s). This probe cannot tell whether that is a fixed startup or layout
  cost or scales with input. Cross-host 3 MiB ratios (0.86–1.27) exclude a large per-byte slowdown but
  cannot resolve a few percent.
* GM was 2–6 s cheaper to encode and 7.5–10.7 s cheaper to decode than packed16.

None of this measures the full-stream peak.

**Complete package price (ledger; S = B_payload + Σ m_a·B_a, executables m = 2).**

| Build (UPX) | Bytes | Δ executables vs historical production 198,236 B (×2) | Δ vs matched lab neutral 209,568 B (×2) |
|---|---:|---:|---:|
| lab neutral | 209,568 | +22,664 | 0 |
| guard packed16 | 218,608 | +40,744 | +18,080 |
| guard + match (GM) | 217,540 | +38,608 | +15,944 |

The model and dictionary are unchanged. Payload has been measured only regionally.
For the guard, confirmation gives 415.558 warm ideal B over 8 warm MiB, i.e.
51.9 B/MiB. For GM vs N, joint A gives 172.467 B over 4 warm MiB, i.e. 43.1 B/MiB.
A stationary scaling to T = 587,138,826 B is **illustrative only**: about 29.1 KB for
G and about 24.1 KB for GM. Against the matched lab increments that gives roughly
+11.0 KB (G) and +8.2 KB (GM). Against the historical production executable, which
also lacks the lab instrumentation, it gives −11.7 KB and −14.5 KB. The sign of the
complete package effect is therefore **not established**. It depends on:

1. a guard build of the production configuration, to price the guard code
   without lab instrumentation;
2. whether the warm rate holds globally;
3. the RAM limit above.

None of this is a measured complete-package win.

## 7. P4 and P5: not implemented (honest status)

Both remain **unimplemented**, exactly as the handoff states; nothing was submitted
for them and no filename is presented as runnable.

* **P4 (lexical structural experts).** Requires a decoder-synchronous parser of the
  transformed WRT stream (dictionary escape/case state, page/field boundaries,
  literal fallbacks, neutral fallback on unknown state), cursor/re-serialization
  checks, four bounded exact-copy experts (contributor IDs, usernames keyed by earlier
  IDs, bounded timestamp predictor, already-reconstructed titles) with a registered
  complete distribution q = (1−α)q_native + α q_E and q_E = (1−ε)·1[b = predicted] + ε/256,
  a topology-matched neutral expert, wrong-key controls and record-block
  development/confirmation partitions. The original round-6 expert implementation
  must first be located and hashed. This is a native C++ change to the predictor plus
  a new parser and harness: multi-day engineering, not a parameter change.
* **P5 (paid templates with right-context backoff).** Requires a new complete
  reversible codec (ordered constructor-run trie, template-plus-edit branch with paid
  branch/ID/edit/literal/case/layout streams, paid right anchors, exact-length branch
  choice, wrong-right-anchor control, sequential prefix-built dictionary descendant)
  and the finite grid 0/64/256 × edit 0/1/2 × direct/paid-right on 16 development MiB,
  then 16 confirmation MiB.

With all five commit slots now occupied (joint B plus four timing repeats, §9), neither
could run before the first slots free up, roughly 03:00–05:30 UTC. They are the next engineering items.

## 8. P6: not executable in this environment

Full global qualification needs 55–60 h per encode/decode near the 10 GB ceiling: a
persistent eligible CPU host or an exact whole-state checkpoint facility, which does
**not** exist (no snapshot is claimed). The GPU pilot comes only after the CPU
shortlist is frozen (joint B and the timing repeats are still running) and requires
you to provide a GPU session within the $70 budget. Nothing was launched.

## 9. Kaggle queue now

All five observed concurrent CPU commit slots are occupied (all `RUNNING` at 00:22 and again at 00:45 UTC).
No push was rejected, no quota was bypassed, and nothing was duplicated.

| Slot | Reference (private, CPU, no internet) | Handoff item | Pushed (UTC) | Regions / design |
|---|---|---|---|---|
| 1 | `chaoscpp/hutter-r14-guard-match-confirm-b-v1` v1 | P3 joint confirmation B | 23:27 | 9, 11, 13, 15; G vs GM pairs, frozen v8 |
| 2 | `chaoscpp/hutter-r14-prune-word-timing-abba-v1` v1 | P1 timing repeat | 23:50 | 8/9 × AB/BA (A/B/B/A) |
| 3 | `chaoscpp/hutter-r14-prune-match-timing-abba-v1` v1 | P1 timing repeat | 00:00 | 8/9 × AB/BA |
| 4 | `chaoscpp/hutter-r14-prune-indirect-timing-abba-v1` v1 | P1 timing repeat | 00:11 | 8/9 × AB/BA |
| 5 | `chaoscpp/hutter-r14-output-fp32-timing-abba-v1` v1 | P1 timing repeat | 00:21 | 8/9 × AB/BA |

Kaggle has no queue beyond these slots; a sixth push was rejected in an earlier round.
Each job has a 10.3 h deadline and four pinned workers. From prior timings they should
finish by roughly 03:00–05:30 UTC on 10 October, inside the research week that ends
11 October (a planning estimate, not a guarantee). The live session is idle; nothing
of mine is left running there.

## 10. Where the project stands

* **The only measured native compression signal is still the integer final-coder
  guard (G).** Eight confirmation regions save 2,587 actual B and 415.558 warm ideal B.
  Its exact-storage implementation (packed16, 218,608 UPX B) is now verified on
  12 MiB of confirmation trajectories. Full-stream payload, RAM fit and the complete
  package sign remain open (§6). Even optimistically this is tens of KB on a package
  of about 99.3 MB (≈0.03 %), not 20 %.
* **Component pruning is fully confirmed on eight regions and none of the arms is a
  compression gain.** Word and match pruning are byte-negative RAM trades (−356 B and
  −92 B per 24 MiB of regional input, for about 41.7 MiB and 23.7 MiB of regional
  RSS). Indirect pruning gives neither bytes nor speed. FP32 output is a tiny but
  sign-consistent bit gain (+14 B, 8/8 warm-positive). No development speed claim
  survived confirmation; the counterbalanced timing repeats are running.
* **Guard + match pruning is additive (interaction −1 B), and choosing it over G alone
  is a RAM decision.** Over four regions GM costs 51 B (18.7 warm B) against G. Two
  executable copies are 2,136 B smaller. Illustratively the bytes roughly cancel at
  full scale (−2.6 KB payload vs +2.1 KB code), while GM buys about 24 MiB of RSS.
  That matters if the limit is read as decimal 10 GB.
* **Grammar/constructor (paid right context):** a narrow conditional signal that still
  loses to gzip and zstd as a complete codec. The template descendant (P5) is
  unimplemented.
* **Structural experts on the lexical coder (P4):** unimplemented. Their 274,829 B
  gain belongs to the older pipeline.
* **Global qualification and GPU (P6):** blocked on infrastructure (a persistent host
  or a whole-state checkpoint facility) and on your GPU session. $0 has been spent.
* **Statistics:** every comparison above has at most eight regional clusters, so it
  is descriptive. Any stronger claim needs more genuinely independent regions or a
  justified finite-population design.

## 11. Next actions (exact commands)

Run these on Kaggle with `KAGGLE_API_TOKEN` taken in-process from the
`kaggle_api_token` secret. Never rerun an accepted dispatcher; each dispatcher
refuses duplicates.

1. **Joint B** (submitted 23:27; comparable notebooks took 3.5–5.5 h, so expect
   roughly 03:00–05:00 UTC; that is a planning observation, not a guarantee). When `kaggle kernels status` shows `COMPLETE`, collect:

   ```bash
   python3 /kaggle/working/hp_round14/confirmation_collector_v2.py.dat --wave joint-b --tag joint-b-YYYYMMDD-HHMM
   ```

   It needs about 17 MB + 20 MiB of reserve; 42,790,912 B was free at 00:45. Then download
   the bundle and receipt and run
   `python research_round14_verify_collected_bundle_v2.py joint-b-YYYYMMDD-HHMM`
   locally. Extend the analysis in a **new** version that adds IDs 9/11/13/15, uses
   component-B N/M for the byte interaction, and checks the guard baseline against
   historical mode 2 on all eight regions.
2. **Four timing repeats** (submitted 23:50, 00:00, 00:11, 00:21;
   about 5 h each). When all are terminal, collect them with the frozen
   collector v3 (`0c207312…`):

   ```bash
   python3 /kaggle/working/hp_round14/confirmation_collector_v3.py.dat --wave timing --tag timing-YYYYMMDD-HHMM
   ```

   Its conservative reserve is about 4 × 17 MB + 20 MiB ≈ 89 MB, more than will be
   free. Use the same verified temporary relocation as in §2 (ledger, no deletion),
   or have a person free hash-verified duplicates with a deletion ledger. Analyze per
   the freeze: every per-pair difference, the per-region means over AB/BA, the
   order-balanced mean, the position effect, and the reference-hash status.
3. **Joint timing:** if joint B's G/GM timing is still dominated by the position
   effect, register and run the same A/B/B/A design for G vs GM. The freeze requires
   this before any deployment speed claim.
4. **P2:** build the guard (and GM) in the production configuration (no lab
   instrumentation) to price the code exactly. Settle the RAM-limit wording.
   Full-stream RSS needs P6.
5. **P4 / P5:** implement as specified in the handoff (§7 here). The first slots free up
   roughly 03:00–05:30 UTC.
6. **P6:** decide on a persistent CPU host or GPU session yourself; nothing will be
   launched or paid for without that decision.

## Appendix: new files

Local, in this directory (all new; no existing file changed):

| File | SHA-256 (prefix) | Purpose |
|---|---|---|
| `research_round14_collect_confirmation_worker_v2.py` | `b993c7c4…` | Frozen collector v2: explicit joint-confirmation selectors |
| `research_round14_collect_confirmation_worker_v3.py` | `0c207312…` | Frozen collector v3: adds `--wave timing`, validates `pairs[].cases` |
| `research_round14_verify_collected_bundle_v2.py` | `4659836e…` | Local CRC + bundle SHA + every member SHA, cross-checked with the receipt |
| `research_round14_confirmation_compact_joint-a-20261009-2325.zip` (+ `_evidence/`, collection JSON `71ab8c4b…`) | `1f831834…` | Joint A outputs, 33 entries |
| `research_round14_confirmation_compact_b-20261009-2328.zip` (+ `_evidence/`, collection JSON `abc2acdb…`) | `868aa9e8…` | Component wave B outputs, 132 entries |
| `research_round14_relocation_ledger_b-20261009-2328.json` | `7e72756c…` | Temporary-relocation ledger (no deletion) |
| `research_round14_guard_match_confirm_b_dispatch_v8.json` | `eafd45cc…` | Joint B push receipt |
| `research_round14_analyze_confirm_ab_joint_a_v2.py` → `research_round14_confirm_ab_joint_a_analysis_v2.json` | `72916e5c…` → `e2a58d70…` | Eight-region component analysis + joint A analysis |
| `research_round14_timing_abba_freeze_v1.md` | `8102775d…` | Registered timing-repeat protocol |
| `hutter_research/cpu_round14_timing_abba.py` | `5685ab6a…` | Timing harness (wraps the unchanged `archive_case`) |
| `research_round14_build_timing_abba_batch.py` | `7b9c0b27…` | Builds the frozen timing batch |
| `kaggle_cpu_round14/sources_timing_abba_v9.zip`, `kernels_timing_abba_v9.zip`, `prepared_timing_abba_v9.json`, `timing_abba_references_v9.json`, `hutter-r14-<arm>-timing-abba-v1/` | `c792a9fb…`, `dae6a077…`, `634211cd…`, `e980e29c…` | Frozen timing batch (main.py: word `78037d61…`, match `8109df7a…`, indirect `d0f153bf…`, FP32 `e3fdbec6…`) |
| `research_round14_dispatch_timing_abba.py` | `54245250…` | Timing dispatcher (one receipt per arm, no retry) |
| `research_round14_p2_startup_rss_probe.py` | `8f698ea5…` | P2 live parity/startup/RSS probe |
| `research_round14_handoff_execution_20261010_receipts/` | see `SHA256SUMS.txt` there | Local copies of every new Kaggle receipt, gate manifest and log |
| `CLAUDE_HANDOFF_EXECUTION_REPORT_20261010.md` | — | This report |

On Kaggle under `/kaggle/working/hp_round14/` (all new): `confirmation_collector_v2.py.dat`,
`confirmation_collector_v3.py.dat`, the two collection records/bundles/logs, the relocation ledger,
`guard_match_confirm_b_dispatch_v8.{json,log}`, the timing `.dat` files (sources, kernels, prepared,
references, freeze, dispatcher), `timing_abba_preflight_v9/` (failed attempt 1, kept),
`timing_abba_preflight_v9b/` (passing gate), four `timing_abba_<arm>_dispatch_v9.json` plus logs,
`research_round14_p2_startup_rss_probe.py.dat` and `p2_startup_rss_probe_v1/manifest.json`.
Large scratch (datasets, codec work dirs, Q16 traces of the probes) lives only in non-durable `/root`.
