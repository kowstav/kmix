# Round 12 (Claude): verification of the audit fixes, new flaws in rounds 10–11, and new CPU experiments

**Author:** Claude (Opus 5.5).
**Date:** 7 October 2026.

**Scope:**
- All 214 files created or updated after the first audit (07 Oct, 02:40 IST). That covers rounds 10 and 11, `hutter_research/`, `tests/`, `kaggle_cpu_round10/` and the registry.
- The live Kaggle session 356010973, plus the outputs of the private notebooks the project submitted.
- New CPU experiments that I designed and ran.

**Local changes:** this file is the only addition to this directory. Nothing else here was modified; the project's 32 unit tests were run with bytecode writing disabled, and no files changed.

**Kaggle changes:** everything new lives under `/kaggle/working/hp_round12_claude/`, in two private datasets (`chaoscpp/hutter-r12-warm-stream-assets`, `…-assets-c`) and in three private CPU notebooks (`chaoscpp/hutter-r12-warm-stream-{a,b,c}`). No Kaggle file was deleted (§7).

**Status of this draft:** sections marked *PENDING* are filled in when the long notebook runs finish.

---

## 0. Executive summary

1. **Most audit findings are now fixed or correctly re-scoped.** The export artifact (L3), formatting (R1), the header bug (P1), report structure (S5/R2), MDL normalization (M1) and amortization (M2) are verifiably fixed. The project also found **six genuine errors in my own audit** (path-entropy gating, a t-test used as an equivalence test, the Lloyd–Max occupancy claim, assumed non-negative redundancy, a 2-opt optimality claim, and sum/mean mixing in my training objective). I accept all of them (§2).
2. **The decisive open question from the audit (D1: do cold-slice gains survive warm state?) is now answered, negatively.** The project's best positive result was the round-9 adaptive law (+168/+172 B on cold G/H slices, independently decoded).
   - On cold 512 KiB windows it gains **+159.7 to +167.9 B on every window**, independent of content.
   - In a warm stream it gains **+154.5 B in the first window and −0.1, −1.1, −1.1 B in the next three**.
   - The frozen wider law becomes harmful: **−50 to −83 B per warm window**.

   The "neural under-weighting" signal behind every positive result of rounds 8–9 is a cold-start transient of cmix's own mixers, not a stationary defect (§4).
3. **The three BF16-repaired finetunes all lose** on a warm 3 MiB prefix: −997, −1,031 and −4,211 B (project notebooks; I pulled the outputs). They come from the round-9 protocol the project itself had already disqualified (audit L2). The round-10 claim that the repair "reopens finetuning" is not supported by any measured model (§3.4).
4. **Seven new logical/engineering flaws** were found in rounds 10–11 (§3). The two most consequential:
   - The integer mixer's memory arms *replace* 8 of 12 features instead of adding to them, so the registered `long_memory`-vs-`full` comparison is confounded.
   - The context classifier reads raw WRT bytes, so its intended XML-markup class never fires. On the canonical stream, raw `<`/`>` occur 0 times in 64 MiB, while the remapped bytes that decode to them occur about 325,000 times each.
5. **CPU-time accounting (audit S4/D7) is still unresolved by the project.** Its component job failed by design (it demanded `-d` decodes of compress-only modes). Identical baseline encodes took 986.6 s, 1,616.9 s and 1,806.5 s on three notebook VMs (1.83× spread). My clean component timing is in §5 (*PENDING*).

---

## 1. Verification of the original 53 findings

Legend:
- **FIXED**: verified in code, data or reports.
- **PROTOCOL**: corrected rule; experiment not yet run.
- **PARTIAL**: improved, but a material gap remains.
- **OPEN**: not fixed.

| ID | Finding | Status | Evidence / remaining gap |
|---|---|---|---|
| S1 | Portfolio vs target scale | PARTIAL | Target restated per canonical byte; work remains on ≤0.1% effects |
| S2 | Critical path never ran | **OPEN** | No full warm baseline. The 9.4 MB warm atlas ran in an interactive session again and died with it; its dependants never ran |
| S3 | Unfalsifiable portfolio | PARTIAL | Every idea now has a finite endpoint and a stopping/reopening clause; no low-ceiling family has been closed |
| S4 | CPU unpriced | PARTIAL | Component job failed by design (§3.3); my timing in §5 |
| S5 | Repository structure | FIXED | README, registry, single checkpoint |
| M1 | λ = 30 | FIXED (protocol) | J = mean CE + mλR/T with λ = 1; not yet run |
| M2 | Amortization | FIXED | `conditional_projection` charges assets once per copy over T |
| M3 | One-copy MDL | FIXED | Retracted |
| M4 | Elasticity | PROTOCOL | κ not yet measured |
| M5 | TTL within noise | FIXED | Retracted |
| M6 | No uncertainty | PARTIAL | Bootstrap/equivalence/Holm implemented, but the bootstrap accepts 2 clusters (§3.6) |
| M7 | Atypical development slice | PARTIAL | New BF16 and atlas jobs still use the atypical canonical prefix [0, 3–9 MiB) |
| M8 | Underpowered confirmation | FIXED | Inference corrected |
| M9 | Precision bound scope | FIXED | Inference corrected |
| M10 | Weight-coding inference | FIXED (and my claim corrected) | See §2, item 4 |
| M11 | Masking before theory | PARTIAL | Theory accepted, yet the zero-rare-loss model was still priced in a notebook (−4,211 B, as the theorem predicts) |
| M12 | Outcome-conditioned budgets | FIXED | |
| M13 | Denominators | FIXED | Labelled, not merged |
| D1 | Cold-slice regime | **ANSWERED HERE** | §4: cold gains vanish warm |
| D2 | Warm candidate vs cold core | FIXED (protocol) | |
| D3 | Slice reuse | PARTIAL | New windows registered, still one early cluster |
| D4–D6 | Calibration, held-out, test tuning | FIXED (accepted) | |
| D7 | Timing | **OPEN** | 1.83× VM-to-VM spread for identical work |
| L1 | Parity gate | FIXED (protocol) | Aggregate gate; no GPU training yet |
| L2 | Finetune power | PROTOCOL | The models from the flawed protocol were nonetheless re-priced (§3.4) |
| L3 | Export artifact | **FIXED** | Growth now 38/42/60 B per copy; 435-tensor native-reader identity |
| L4–L5 | Short resets, undertrained heads | PROTOCOL (GPU) | |
| L6 | Mixer diagnosis | Superseded | The premise is refuted in warm state (§4) |
| L7 | Float-constant channel | PROTOCOL | |
| E1 | Ephemeral platform | PARTIAL | Notebooks used for the BF16 jobs; the critical warm atlas again died with an interactive session |
| E2 | `exec` patching | FIXED (new code) | |
| E3 | No pre-flight | PARTIAL | New design errors still reached the remote (§3.3, §3.7) |
| E4–E6 | Lab builds, warm infra, portability | PARTIAL | My streaming warm harness (§4.1) supplies working warm infrastructure |
| P1 | Header include | FIXED | `#include "research_round9_adaptive_law.h"` |
| P2 | libm law | PARTIAL | New integer law is libm-free; the adaptive law still uses libm, which is moot after §4 |
| P3, P8, P9 | | FIXED | |
| P4–P7, P10 | | FIXED (accepted) | |
| R1 | Glued tokens | **FIXED** | 0 glued tokens across all round-10/11 reports (previously 1,353) |
| R2–R5 | Reporting | FIXED | |

---

## 2. Corrections to my own audit (accepted)

The project's response (`research_round10_audit_response.md`) identifies real errors in my companion theory. I re-derived each one; all are correct.

1. **Realized-path entropy is not a before-byte gate.** $\sum_k h(p_{t,k})$ along the realized bit path depends on the unknown bits. The before-byte entropy is its expectation over paths. My R(α) table is descriptive only; a deployable gate must use the 205-way neural entropy or prefix-visible classes. (My report flagged this as a proxy but still derived savings from it.)
2. **|t| < 2 is not an equivalence test.** Use TOST, i.e. a confidence interval inside a predeclared margin.
3. **The parameter optimum is conditional.** It rests on ε and κ that have not been measured for this pipeline. Factors of 35 to 63 in model size require an explicit power-law vs log-linear choice. Proposition 8 is a scenario, not a theorem.
4. **Lloyd–Max does not equalize index occupancy.** At high rate the point density is ∝ p^{1/3}, so cell probability is ∝ p^{2/3}, which is non-uniform. My inference "near-uniform indices ⇒ fixed-rate-optimized quantizer" was invalid. The Panter–Dite vs Gish–Pierce constants remain a correct comparison of the two optimal quantizers at equal MSE, but say nothing about this specific learned codebook.
5. **Interaction can be positive.** Joint gain can exceed the sum of individual gains (XOR-type synergy). $I_{AB} = G_{AB}-G_A-G_B$ has either sign, so my "Red ≥ 0" and the fixed 0.7–0.85 discount were unjustified.
6. **Greedy + 2-opt has no generic guarantee** on an asymmetric graph.
7. **My TIDE-Z objective mixed a sum loss with a per-token rate,** under-weighting the rate by a factor of T. It also double-weighted mixer trust by multiplying by $w_{\rm NN}$ a term whose gradient already contains it.
8. **A fixed shadow price cannot license exceeding a hard time limit.**

These corrections leave the audit's *empirical* findings intact (L3 was confirmed and fixed; D1 is confirmed here). They weaken several *quantitative forecasts* in my companion report. The 4.5–6% "central frontier" should now be read as a hypothesis with wide uncertainty, not an estimate.

---

## 3. New flaws in the round-10/11 work

### 3.1 Integer-mixer memory arms replace features instead of adding them — High
`hutter_research/integer_mixer_replay.cpp`: the mixer has a fixed 16-feature layout (native, NN, 13 sources, bias). The memory arms write their 8 memory features into `sources[5..12]`, overwriting first-stage mixer outputs 4–11. Consequences:
- `long_memory` vs `full` compares a memory model with 5 mixer features against a memory-free model with 12, so the two effects are confounded.
- Only `long_memory` vs `memory_zero` isolates memory.
- The registered selection rule (`research_round11_warm_mixer_worker.py`) picks the best of `full_*` and `long_memory_*` by development gain, which mixes feature-count and memory effects.

Measured (my runs): `long_memory_1000` minus `memory_zero_1000` is −0.3 to −1.2 B per window, cold and warm. The memory bank carries no usable signal. `memory_zero` (fewer features) beats `full_1000` by 25–60 B per window, so the apparent "memory effect" in any `long_memory`-vs-`full` comparison would really be a feature-count effect.

### 3.2 The context classifier reads raw WRT bytes, so the markup context never fires — Medium
`previous_class` tests `byte == '<'`, `'>'`, `';'`, `':'` on raw WRT bytes. The WRT byte map (`research_round7_wrt.py`) swaps ranges: decoded `<` is stored as raw `L` (76), `>` as `N` (78), `:`/`;` as `J`/`K`. Verified on the first 64 MiB of the canonical stream:

| Raw byte | Count in 64 MiB | Decodes to |
|---|---:|---|
| `<` (60) | 0 | — |
| `>` (62) | 0 | — |
| `:` (58) | 0 | — |
| `;` (59) | 0 | — |
| `L` (76) | 325,396 | `<` |
| `N` (78) | 325,988 | `>` |
| `J` (74) | 262,301 | `:` |
| `K` (75) | 44,196 | `;` |

The intended "markup" class 7 therefore only fires on `[`/`]`; XML angle brackets fall into the uppercase class. Causality and correctness are unaffected; the semantics of the registered context design are not what the documents describe. Measured effect of decoding first (my `full_1000_decodedclass` arm): within ±2 B per window. This finite mixer is not sensitive to the error, but the stated context design was not the one tested.

### 3.3 The component-CPU job was impossible as designed — Medium
`kaggle_cpu_round10/kernel_job.py::component_audit` requires an independent `-d` decode for `--ppmd-only` and `--transformer-only` archives. cmix rejects those flags in `-d` mode; its usage text states they "can only be used when compressing (-c, -n or -e)". The job therefore failed after its first PPMD case (`research_round11_component_failed_decode.log`). Encode-only timing is the correct design (§5). This is a pre-flight failure of the kind audit E3 described: the constraint was printed in the binary's own help text.

### 3.4 Re-pricing models that the project had already disqualified — Medium
The three BF16 notebook pairs evaluate the round-9 `core_training_v2` models: batch 1, 128 steps, fresh AdamW, ≈7,000–32,000 supervised targets. The project accepted that protocol as underpowered and drift-dominated (L2). Results (outputs pulled from Kaggle):

| Candidate | Archive bytes, 3 MiB warm prefix (baseline 310,050) | Gain | Per-window gain, 1–3 MiB |
|---|---:|---:|---|
| unweighted (BF16-repaired) | 311,047 | **−997** | −270, −255, −254, −221 B |
| cut107_half | 311,081 | **−1,031** | ≈ −270 B each |
| cut1392_zero | 314,261 | **−4,211** | ≈ −790 B each |

Two aggravating details:
- The finetuning corpus was canonical bytes [6, 262,144). That lies inside the evaluated prefix, so part of each archive comparison is in-sample in the candidates' favour; they lose anyway.
- `cut1392_zero` is predicted to lose by the project's own masking theorem: $\mathrm{KL}\to\infty$ as the rare-word weight → 0.

These runs consumed three notebook slots to confirm outcomes predicted by documents already in the repository. The round-10 sentence "this reopens stable finetuning as a serious candidate" should be qualified: no finetuned model has yet beaten the baseline in warm state.

### 3.5 The integer mixer has no regret guard — Medium
The round-9 adaptive law is a fixed-share Bayesian mixture that contains the identity expert. Its loss against identity is bounded by roughly $\log_2 5$ bits plus switching cost, which is why it costs only about 1 B per warm window once its signal disappears.

The round-10 integer mixer is unguarded online SGD over 640 contexts × 16 weights, and it can lose without bound. Measured on cold 512 KiB windows:

| Arm | Gain per cold window |
|---|---:|
| `full_4000` | −558 to −683 B |
| `full_1000` | −38 to −89 B |
| `full_250` | +25 to +52 B |
| `global_1000` | +88 to +111 B |

Two of the three registered rates lose. Any production online law should sit inside a Bayesian or fixed-share mixture with the identity. My cluster-C notebook tests exactly that guard (`guarded_fixedshare`, §4).

### 3.6 The bootstrap contract accepts two clusters — Low
`contracts.stratified_cluster_bootstrap` returns a percentile interval whenever each stratum has ≥ 2 clusters. With 2 clusters there are only 3 distinct resample means, so a "95%" percentile interval has badly wrong coverage. Require ≥ 8–10 independent clusters, or use a small-sample t interval and report the cluster count prominently.

### 3.7 Proxy designs that cannot answer their questions — Medium
- **Article order (gzip proxy, −5,314 B = 0.34%).** gzip's 32 KB window spans about 4 pages at the average 8.25 KB page length. A cmix with a 3.5 GB PPMD and unbounded match history responds to ordering through entirely different mechanisms. The proxy's sign need not transfer. The O(n²) swap descent also cannot scale from 512 pages to 243,425.
- **Constructor/anchor proxy (all arms −8 to −14% vs gzip).** Right-anchor conditioning uses exact anchor-word hashes folded into 2,048 buckets, over about 3 × 128 pages. Each bucket mixes a few hundred colliding observations, so "anchors ≈ wrong anchors" reflects missing statistical power, not evidence against right-context information.
- **Warm atlas protocol.** Development (6 windows) and confirmation (10 windows) are adjacent windows of one early cluster that starts at offset 0, the atypical region of audit M7. The registered design was again placed in an interactive session, which died (E1).
- **The integer-mixer notebook never existed.** The CLI wrapper printed an API error with exit code 0, and the job was treated as submitted (acknowledged by the project).

---

## 4. New experiment R12: does the cold-slice signal survive warm state?

### 4.1 Infrastructure (new)
The native observer opens every trace with `fopen(path, "wbx")` (`O_EXCL`), so FIFOs are impossible, and full traces cost 817 B per input byte (39 GB per 48 MiB). I wrote:
- **`stream_replay.cpp`**: a C++ consumer that follows the four trace files as regular files while the encoder writes them. It runs every arm online in lockstep, entirely before-target, and punches holes behind its read position with `fallocate(PUNCH_HOLE)` so disk use stays bounded. Verified: 278 MB apparent vs 109 MB allocated.
- **`r12_driver.py`**: pins the encoder and consumer to different physical cores (cpu0 and cpu1; cpu2/cpu3 are their SMT siblings), enforces a wall-time budget with graceful truncation and a disk guard, and cross-checks the replay baseline against the native per-byte cost trace.

Arms:
- identity;
- frozen wider law (a = 1);
- the round-9 adaptive law, a verbatim port;
- the project's integer mixer (headers byte-identical to its asset manifest), at full 250/1000/4000, full_1000 with decoded-character classes, no_explicit_nn, global, memory_zero and long_memory;
- cluster C additionally: reduced_250, minimal_250 and guarded_fixedshare.

### 4.2 Validation (exact reproduction of published results)

| Check | Published | Measured here |
|---|---:|---:|
| Native archive, cold G window (canonical 65,000,000, 512 KiB; input SHA `54869732…`) | 100,473 B | **100,473 B** |
| Adaptive-law gain on G | +168 B (actual archive) | **+167.874 B** (ideal) |
| Identity arm mismatches | 0 | 0 |
| Replay baseline − native cost trace | 0 | 1.5×10⁻⁶ bits |

### 4.3 Warm stream from canonical offset 0 (validation run V1, 2 MiB)
Gains in bytes per 512 KiB window:

| History | Baseline B | Adaptive r9 | Wider a1 | full_250 | full_1000 | global_1000 | memory_zero | long_memory |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 39,340 | **+154.5** | +48.2 | +44.3 | +5.4 | +88.5 | +40.0 | +39.6 |
| 512 KiB | 42,534 | **−0.1** | **−82.6** | +32.1 | −19.2 | −36.7 | +19.0 | +18.6 |
| 1 MiB | 54,639 | **−1.1** | **−75.9** | +30.4 | −21.3 | −7.3 | +16.6 | +16.0 |
| 1.5 MiB | 61,863 | **−1.1** | **−50.0** | +18.3 | −27.5 | +2.8 | +6.4 | +6.1 |

### 4.4 Cold controls: the same windows coded from a cold start
Gains in bytes per 512 KiB window. Every archive was independently produced by the unchanged native binary; the replay baseline matches the native cost trace.

| Window (canonical offset) | Cold baseline (ideal B) | Native archive B | Adaptive r9 | Wider a1 | full_250 | full_1000 | full_4000 | global_1000 | memory_zero | long_memory |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| G 65,000,000 | 100,435 | 100,473 (= published) | +167.9 | +49.9 | +31.4 | −82.1 | −666.7 | +86.3 | +7.6 | +6.6 |
| A 4 MiB | 93,628 | 93,665 | +161.6 | +34.0 | +51.6 | −38.1 | −557.9 | +87.8 | +36.4 | +36.5 |
| A 12 MiB | 106,753 | 106,790 | +160.5 | +93.1 | +29.2 | −83.4 | −663.3 | +111.3 | +4.0 | +3.2 |
| A 24 MiB | 103,925 | 103,962 | +159.7 | +74.3 | +25.3 | −88.9 | −683.0 | +102.5 | +2.8 | +2.5 |
| A 36 MiB | 110,179 | 110,217 | +161.6 | +72.7 | +30.5 | −81.6 | −665.5 | +105.0 | +8.2 | +7.0 |
| A 48 MiB | 118,059 | 118,096 | +166.1 | +82.3 | +22.9 | −101.9 | −738.2 | +94.6 | −3.2 | −3.0 |
| A 60 MiB | 110,108 | 110,145 | +155.6 | +48.1 | +37.5 | −76.5 | −691.2 | +89.9 | +18.1 | +17.2 |
| B 300M+12 MiB | 75,393 | 75,431 | +160.6 | +47.2 | +37.3 | −47.6 | −518.7 | +88.8 | +21.3 | +22.2 |
| B 300M+24 MiB | 108,838 | 108,875 | +169.4 | +92.1 | +21.0 | −104.4 | −717.0 | +112.0 | −9.5 | −11.0 |
| B 300M+36 MiB | 110,984 | 111,022 | +165.5 | +77.2 | +27.1 | −87.6 | −700.6 | +103.7 | +3.6 | +2.9 |
| B 300M+48 MiB | 113,008 | 113,046 | +167.8 | +101.0 | +29.7 | −89.8 | −713.0 | +125.5 | +5.3 | +4.8 |
| B 300M+60 MiB | 105,559 | 105,597 | +168.6 | +104.6 | +24.9 | −84.9 | −680.6 | +113.2 | +3.8 | +3.3 |
| H 375,000,000 | 112,229 | 112,266 (= published) | +172.2 | +117.0 | +24.0 | −96.7 | −695.5 | +122.7 | −1.2 | −2.2 |

Across the 13 cold windows (G, 11 matched, H) the adaptive law gains **mean +164.4 B, range 155.6–172.2 B, coefficient of variation 3%**, while the windows' baseline costs vary by 57% (75–118 KB). A gain that is nearly *constant per cold start*, independent of content and of the window's own cost, is the signature of a warm-up transient. A gain proportional to content would scale with the baseline cost instead. The archive minus ideal cost is a constant +37–38 B per window (coder flush/header), which confirms that ideal gains transfer to actual bytes at this scale.

### 4.5 Warm clusters A (offset 0), B (offset 300,000,000) and C (offset 450,000,000), 64 MiB each
*PENDING (notebooks running).*

---

## 5. CPU component timing (repairs §3.3)

**Method.**
- Encode-only, one process at a time, pinned to cpu0 with its SMT sibling (cpu2) idle and no other job on the VM.
- Canonical prefix from offset 0 at 1 MiB and 3 MiB.
- Marginal cost = [T(3 MiB) − T(1 MiB)] / 2 MiB, which removes startup (model load, allocation).
- Binary: the project's unchanged observer build (lab flags, no PGO/LTO) with no trace variables set.

| Mode | User+sys CPU, 1 MiB | User+sys CPU, 3 MiB | Peak RSS | Archive, 3 MiB | Marginal µs/byte | Share |
|---|---:|---:|---:|---:|---:|---:|
| Combined (lexth11c CM) | 862.6 s | 2,336.3 s | 6.08 GB | 310,050 B | **702.7** | 100% |
| Transformer stepping + PPMD (`--transformer-only`) | 308.2 s | 1,036.2 s | 1.26 GB | 562,531 B (PPMD-coded) | **347.1** | 49.4% |
| PPMD only | 10.5 s | 32.6 s | 1.21 GB | 562,531 B | **10.5** | 1.5% |
| **Classical bank + mixers + SSE** (difference) | | | ≈ 4.8 GB | | **355.6** | **50.6%** |

Readings:
1. **Half of all encode CPU is spent outside the transformer and PPMD.** Round 5 measured that this classical stack adds only 1.70–2.97% over the transformer (with its PPMD prior). Its average efficiency is roughly 2–3% of payload per 50% of CPU. This is the audit's Corollary 2.1 reallocation question, now with a measured CPU share. A per-model-family ablation (which families buy their CPU) is the natural next CPU experiment. It needs fork-based warm windows, not cold slices.
2. **The classical bank also owns about 4.8 GB of the 6.1 GB resident set.** The transformer-only process peaks at 1.26 GB. The RAM headroom for any new memory mechanism must come from this side.
3. The combined 3 MiB archive (310,050 B) is byte-identical in size to the baseline of the project's three BF16 notebooks, which is an independent reproducibility check.
4. **These timings cannot qualify anything** (audit D7). At 702.7 µs/byte a full canonical stream would take about 115 h on this lab build and Xeon, against 55.4 h for the production lexth11c build on its sandbox. Only *shares* are meaningful here.

---

## 6. What this means

*PENDING the warm clusters. Provisional reading from V1 plus the cold controls:*
- A cold slice systematically overstates every residual that pushes toward the transformer's prediction, by roughly a constant amount per cold start (~160 B for the adaptive law).
- In the actual full-file compression only the first window is cold, so the adaptive law's full-file value is about that one window, i.e. negligible.

---

## 7. Disk space on `/kaggle/working`

`/kaggle/working` was 97% full (20.2 of 21 GB; 686 MB free). I identified **2.46 GB** of non-essential files and verified each one read-only (SHA-256):

| Candidate | Size | Why it is safe |
|---|---:|---|
| 4 × `hp_round8/native_inline_{wide,residual}_v1/*_candidate_decode/hidden.q8` | 4 × 101.2 MB | Byte-identical to the encode-side `*_candidate/hidden.q8` (SHA verified); not referenced by any manifest |
| `hp_round8/round8_native_extension_20261006_complete.zip.failed_text_upload.bin` | 51.7 MB | Failed text-mode upload; the intact zip is present |
| `hutter_lab/exp2/runs/f288/test_probs.npy` | 1,174 MB | Round-2 enwik8 toy output; `model.pt`, `lm.py` and `test.bin` present for regeneration; referenced only by an inventory listing |
| `hutter_lab/exp4/knn_search_20MB_q0.5.pt` | 831 MB | Round-4 toy kNN cache; regeneration inputs present |

**I did not delete them.** My operating rules do not allow me to permanently delete data even when asked. Instead I wrote `/kaggle/working/hp_round12_claude/cleanup_verified.py`. It removes a file only if its SHA-256 still matches the recorded value and, for duplicates, only if the twin still exists with the identical hash. It logs every action to `cleanup_ledger.json`. Run it first without arguments (dry run), then with `--apply`:

```bash
python3 /kaggle/working/hp_round12_claude/cleanup_verified.py
```

```bash
python3 /kaggle/working/hp_round12_claude/cleanup_verified.py --apply
```

---

## 8. Recommended next steps
*PENDING final results.*

---

## Appendix A. Artifacts and reproduction

| Artifact | Location |
|---|---|
| Consumer and driver source | `/kaggle/working/hp_round12_claude/code/` (`stream_replay.cpp` v1 for A/B and cold runs; `stream_replay_v2.cpp` for C) |
| Validation and cold results | `/kaggle/working/hp_round12_claude/{validation,cold}/` (JSONL per window, `manifest.json`) |
| Component timing | `/kaggle/working/hp_round12_claude/component/manifest.json` |
| Warm notebook outputs | `kaggle kernels output chaoscpp/hutter-r12-warm-stream-{a,b,c}` |
| Notebook C version 1 | Failed in seconds because my metadata edit corrupted the dataset slug; its output is preserved under `/root/r12_pull/c_v1_failed` and version 2 was pushed |

Exact asset hashes:
- native observer `17768b06…`;
- model `948847d9…`;
- dictionary `4c8568cc…`;
- canonical stream `7826ff63…`;
- consumer v1 `cdd49521…`, v2 `68c5a252…`.
