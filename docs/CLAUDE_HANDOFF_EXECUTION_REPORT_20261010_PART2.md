# Handoff execution report, part 2: continuation on 10 October 2026

Prepared by Claude (Anthropic), continuing `PENDING_EXPERIMENTS_HANDOFF.md` in live session
**356938144** (kernel `395d7f96…`). All times are UTC. Every artefact is a new file, and no
existing project file was modified. The signed session URL and the Kaggle token appear in
no file. Paid spend is **$0**; no GPU was used and no rental was launched. The usageLimited
Goal was not touched. Part 1 is `CLAUDE_HANDOFF_EXECUTION_REPORT_20261010.md`.

**Short version.**
- Collected and verified joint confirmation B and all four timing repeats (§1).
- Launched four new handoff experiments, each behind a live gate:
  - the prescribed G-vs-GM A/B/B/A timing repeat (P3 freeze);
  - the P5 template development screen (new codec, 39 arms × 16 MiB);
  - two P4 structural-expert development notebooks (new lexical port).
- P4's first pushes failed on an execution-permission bug that the gate missed. They are
  preserved; the fix was re-gated and pushed as `-v2`.
- Not done: P6 (GPU or persistent host). Confirmation stages for P4/P5 wait for their
  development results.

## 1. Results collected this session

### 1.1 Joint confirmation B (P3): eight-region joint totals

Collector v2, tag `joint-b-20261010-0446`: `TERMINAL_WAVE_SNAPSHOT`, 33 entries,
5,971,114 B, SHA `a61e7bea…`. Every member SHA and the ZIP CRC were verified locally.
Analysis: `research_round14_analyze_joint_confirmation_v3.py` →
`research_round14_joint_confirmation_analysis_v3.json`.

| Region | Wave | G−GM actual B | G−GM warm B | N−GM actual B | N−G actual B | Interaction actual B | Interaction warm B | Encode CPU G / GM s | RSS saved G−GM |
|---:|:-:|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | A | -15 | -6.094 | +313 | +328 | -1 | -0.061 | 4217 / 5022 | 23.9 MiB |
| 9 | B | -17 | -6.316 | +301 | +318 | -1 | +0.005 | 4185 / 4076 | 24.0 MiB |
| 10 | A | -26 | -12.940 | +291 | +317 | +1 | -0.098 | 5064 / 4257 | 24.0 MiB |
| 11 | B | -15 | -4.680 | +336 | +351 | -1 | -0.554 | 4221 / 3952 | 23.8 MiB |
| 12 | A | -11 | +1.200 | +289 | +300 | +0 | -0.171 | 4323 / 5050 | 23.8 MiB |
| 13 | B | -9 | -1.057 | +328 | +337 | -1 | -0.364 | 4044 / 4054 | 24.0 MiB |
| 14 | A | +1 | -0.901 | +311 | +310 | -1 | -0.271 | 5050 / 4171 | 24.0 MiB |
| 15 | B | -5 | -9.564 | +321 | +326 | -1 | +0.184 | 3943 / 3687 | 24.0 MiB |
| **Sum** | | **-97** | **-40.352** | **+2490** | **+2587** | **-5** | **-1.331** | 35047 / 34268 | 23.9 MiB mean |

* **Exact storage parity on 24 MiB.** On all eight regions the packed16 guard (`5f6e0c7b…`)
  reproduces the historical raw-table guard: archive, every Q16 probability and warm bits.
  N−G therefore reproduces the historical guard result exactly, 2,587 actual B and
  415.558 warm B.
* **Guard + match pruning vs guard:** −97 actual B (7/8 regions worse) and −40.35 warm B,
  for 23.9 MiB less regional RSS. Against neutral it still saves 2,490 actual B (8/8
  regions) and 375.2 warm B.
* **Interaction** I = B_G + B_M − B_N − B_GM = **−5 actual B** (range −1…+1 per region) and
  −1.33 warm B. The two effects are additive within noise.
* **Timing stays unresolved** across the two notebooks:
  - encode G−GM per region 97 ± 618 s, with 5 regions faster and 3 slower;
  - decode 93 ± 538 s, with 4 faster and 4 slower;
  - position effects up to +805 s (joint A).

  The joint freeze's rule ("if timing remains inconsistent … A/B/B/A repeats") therefore
  triggered the joint timing repeat in §2.


### 1.2 Component timing repeats (P1): counterbalanced A/B/B/A

Collector v3 (`--wave timing`), tag `timing-20261010-0504`: `TERMINAL_WAVE_SNAPSHOT`,
132 entries, 27,217,057 B, SHA `dc5e044b…`. All four notebooks finished
`COMPLETE_FOUR_LANE_ABBA_TIMING`, and every archive and Q16 hash equals its confirmation
reference. The collector's disk reserve was met by a temporary, verified, fully restored
relocation of two locally duplicated ZIPs (ledger
`research_round14_relocation_ledger_timing-20261010-0504.json`,
`RESTORED_VERIFIED_NO_NET_DELETION`). Analysis: `research_round14_analyze_timing_abba_v1.py`
→ `research_round14_timing_abba_analysis_v1.json`.

| Arm | Encode: per-pair CPU saved s (8AB, 8BA, 9AB, 9BA) | Encode order-balanced | Decode: per-pair CPU saved s | Decode order-balanced | Position effect enc / dec s | Effective cores |
|---|---|---:|---|---:|---:|---:|
| Word pruning | -69, +645, +6, +586 | +292 s (+6.32%) | -580, +139, -490, +302 | -157 s (-3.51%) | +323 / +378 | 3.906 |
| Match pruning | -6, +105, +119, +260 | +120 s (+2.97%) | -13, +274, +20, +314 | +149 s (+3.66%) | +63 / +145 | 3.937 |
| Indirect pruning | +19, +108, +10, +46 | +46 s (+2.27%) | -125, +296, -184, +177 | +41 s (+2.01%) | +31 / +196 | 3.950 |
| FP32 output | +254, -184, +159, +13 | +60 s (+1.47%) | -478, +694, -364, +524 | +94 s (+2.26%) | -146 / +515 | 3.937 |

Positive values mean the arm uses less CPU than neutral, on the same host and core. Each
lane's two runs are back to back, and the AB/BA pairing cancels the large time-position
effects, which were again comparable to the arm effects.

Reading the counterbalanced repeats:
* Match pruning: +3.0 % encode / +3.7 % decode, both regions positive in both phases.
* Indirect pruning: +2.3 % encode, with all four pairs positive.
* FP32 output: +1.5 % / +2.3 %.
* Word pruning: +6.3 % encode but −3.5 % decode (slower).

These are four pairs per arm on two regions, so the result is descriptive. It is cleaner
than the confirmation waves, whose regional signs were dominated by the position effect,
but not a deployment speed claim. Full production timing and RSS still need the
full-stream run (P6).


## 2. New experiments launched (all per the handoff)

| Pushed (UTC) | Reference | Handoff item | Gate |
|---|---|---|---|
| 05:02 | `chaoscpp/hutter-r14-guard-match-timing-abba-v1` | P3 joint timing (freeze rule triggered) | 16 KiB parity on 4 lanes, both binaries |
| 05:14 | `chaoscpp/hutter-r14-template-development-v1` | P5 development screen | real-data inverses + baseline byte identity |
| 05:57 | `…-structx-development-{a,b}-v1` | P4 development | **failed (PermissionError), preserved** |
| 06:07 | `chaoscpp/hutter-r14-structx-development-a-v2` (modes 1, 2) and `-b-v2` (modes 3, 0) | P4 development | P4 gate + read-only re-gate (identical hashes) |

All are private CPU notebooks with four pinned workers, a 10.3 h deadline, no GPU and no
internet. Each push was verified by its dispatcher, which refuses duplicates and never retries.

## 3. P5 implementation: paid constructor-run templates

**Codec** (`hutter_research/template_codec.py`, new; `constructor_codec.py` unchanged).

The paid channels are the same as the constructor codec's: lexicon, layout, constructor/literal
flags, literal/OOV words and case. All the coding happens in one range-coded run stream. For each
maximal constructor run (its length is known from the flags), a paid branch flag selects either:

- the unchanged direct model, or
- a template plus up to E edits: a template id keyed by (min(n,4), anchor class); an edit count;
  and per edit a type, a uniform position, and a symbol where the edit needs one.

After every run the direct model is updated with the run's ids, so its statistics do not depend
on which branch was taken. The branch is chosen by minimum exact ideal code length under the
current integer frequencies, including the flag cost. Search pruning is exact: a slot is skipped
only when its unavoidable cost already reaches the best total.

Dictionaries:
- **Static:** top-K runs of length ≥ 2 from an ordered run trie, ranked by count × (length − 1).
  The table is paid inside **every** archive. Development builds it leave-one-out; confirmation
  builds it from all development regions.
- **Prefix:** sequential, future-free insertion with least-recently-used eviction, and no table.

Correctness checks:
- With no dictionary, the run stream is **byte-identical** to `constructor_codec` coarse_<ctx>:4.
  The job asserts this on every such case; the archive is +8 B, all header.
- Every case independently decodes to its exact input.

**Protocol** (`research_round14_template_freeze_v1.md`, SHA `28bc5683…`, written before any
result). The regions are the same 32 spread 1 MiB slices as the 608 completed constructor
archives (16 development + 16 confirmation). The grid has 39 arms:
- none × {left, right, wrong};
- static × {64, 256} × E {0, 1, 2} × {left, right, wrong};
- prefix × the same.

Analysis includes the four-cell interaction as in P3, with a matched wrong-anchor control. The
selection rule is fixed: the minimum total among right-context template arms, advancing only if
it beats none-right.

**Live real-data gate** (region 0): all inverses exact, with byte identity for the three
baselines. Early, single-region signal: static templates save 64–195 B of run stream, but their
paid table (188–604 B) makes them net worse. The prefix dictionary is worse outright. The
16-region screen decides, under the pre-registered rule.


## 4. P4 implementation: lexical structural experts

**Provenance.** round 6's implementation was located and hashed before porting:
`structx.h` (`3470b9e7…`) and `sxpatch.py` (`6b67e97d…`) in `research_round7_sources/`.

**Port.** `hutter_research/structx_lex.h` is a decoder-synchronous parser of the lexical
transformed stream. It tracks:
- dictionary escape/code grammar (0x0C; 1-, 2- and 3-byte codes; case markers), with a neutral
  fallback for the line on any violation;
- page/title boundaries;
- PHDA9 tail records;
- interlanguage blocks.

The four mechanism-backed experts are timestamp from revision id, contributor id by username,
username from time neighbour, and interlanguage title copied from the already-reconstructed owner
title. Stores are bounded (262,144 entries, FIFO eviction). `structx_lex_patch.py` integrates them
as round 6 did: one extra layer-0 input and one extra layer-0 mixer keyed by kind × confidence ×
bit position, all under `#if HP_R14_STRUCTX`. The modes:
- mode 0 is the pinned neutral;
- mode 1 is the topology-matched neutral expert;
- mode 2 is the joint predictor;
- mode 3 is the wrong-key control.

**Build** (pinned Clang/LLD 17.0.6, restored from the signed official repository with the
project's own fingerprint check):
- The untouched bundle rebuilds the R14 neutral **byte-identically** (`30b539b3…`).
- Mode 0 of the patched tree is also byte-identical to it.

**Gate** (`hp_round14/p4_gate_v2.json`, `PASS_P4_GATE_ALIGNMENT_FUZZ_AND_NATIVE_INVERSES`):
1. **Exact cursor alignment.** An independent Python re-serialization of the whole PHDA9 tail
   rebuilds the dictionary codes from `english.dic` exactly as `dictionary.cpp` does. It agrees
   with the parser on **all 1,582,867 records at identical byte offsets**: 243,425 timestamps,
   205,397 usernames, 448,822 ids and 685,223 interlanguage lines. There were zero mismatches
   and zero decode or grammar errors.
2. **Independent agreement with round 6.** The parser finds exactly **93,707 owners and 93,700
   interlanguage blocks**, round 6's Python reference counts. The contributor-id expert is active
   on exactly **1,121,627 bytes at 139 B** standalone, also round 6's numbers.
3. **FSM fuzz.** 4 MiB of arbitrary byte/escape tails run crash-free and deterministic; experts
   stay inactive (60 active bytes).
4. **Native inverses.** Modes 1–3 invert exactly on 16 KiB of a revision region, an
   interlanguage region (with owners) and a synthetic escape tail.

**Regions** are fixed-rule 3 MiB windows (2 MiB warmup) in the revision tail
(554.87–570.59 MB) and the interlanguage tail (570.59–586.45 MB). k = 0, 1 are development
(ids 0, 1, 4, 5); k = 2, 3 are confirmation (ids 2, 3, 6, 7). Interlanguage regions receive the
causal parser's owner list through lab-only variables. Encoder and decoder read the same file;
this emulates matched preceding history. Assets are in the private dataset
`chaoscpp/hutter-r14-structx-assets-v1` (manifest `0ec19431…`).

**Preserved failure and fix.** The first two development notebooks (`…-development-{a,b}-v1`)
failed within seconds, before coding anything. The harness executed the binaries directly from
the read-only, non-executable dataset mount. The live gate missed this because its assets had
execute permission. v13 only copies the binaries to scratch, sets execute and re-verifies their
SHA (addendum `research_round14_structx_freeze_v1_addendum_v13.md`). A re-gate on a read-only,
non-executable asset copy had to reproduce the v12 gate's hashes exactly before the `-v2`
references were pushed. The v1 failures stay recorded as failures.


## 5. Kaggle queue

At 06:07 UTC four of our notebooks were `RUNNING`: joint timing, P5 development, and P4
D-A and D-B (`-v2`). Expected completions: joint timing about 10:00; P5 development about
07:30; P4 development about 11:30. These are planning estimates, not guarantees.

## 6. Disk, preservation and integrity

No deletion of any kind. Both collections that exceeded the frozen collectors' reserve used
verified, fully restored temporary relocations (ledgers above). Working space was about
9 MB free after the timing bundle, so future collections need the same procedure. All
bundles were verified locally (CRC + every member SHA). The P4 assets live in the private
dataset; large scratch stays in non-durable `/root`.

## 7. Next actions

1. **P5:** when development completes, collect it (it writes only JSON), run
   `research_round14_analyze_template_development_v1.py`, and only if the pre-registered
   selection advances, freeze with `research_round14_build_template_confirmation.py` and push.
2. **P4:** collect D-A/D-B. They need a collector selector for `structx` refs, which is not yet
   written; freeze it as a new collector version. Then compare modes 1/2/3/0 per the freeze and
   run confirmation (regions 2, 3, 6, 7) with the frozen binaries.
3. **Joint timing:** collect with a selector for `hutter-r14-guard-match-timing-abba-v1`, which
   also needs a new collector version. Its manifest uses `pairs[]`, which collector v3 already
   validates.
4. **P6:** your decision (persistent CPU host or GPU session); nothing paid will be launched.
