# Independent audit of the Hutter-Prize research program (rounds 2–9): flaws, errors and their consequences

**Auditor:** Claude (Opus 5.5), independent review requested by the project owner.
**Date:** 7 October 2026.
**Scope:** every narrative report in this directory (76 Markdown files, ~164,000 words) and the idea files. Also representative source code (≈550 Python scripts, 36 C/C++ files, the preserved native build tree) and the locally preserved evidence (result JSONs, native final-bit traces, cost traces, checkpoints).
**Rule followed:** nothing in this directory was modified. Only this file and its companion (`CLAUDE_AUDIT_02_NEXT_EXPERIMENTS_AND_THEORY.md`) were added. Every new number below was recomputed from local files; Appendix B lists the scripts.

---

## 0. How to read this report

Each finding has an identifier, a category, a severity, evidence (file and line, or the computation I ran), an explanation and a concrete fix.

| Severity | Meaning |
|---|---|
| **Critical** | Changes a headline conclusion, or blocked progress on the critical path |
| **High** | Materially biases a class of results or wastes a large share of effort |
| **Medium** | Real defect with bounded impact |
| **Low** | Hygiene, clarity or robustness issue |

| Provenance tag | Meaning |
|---|---|
| **[NEW]** | Not identified anywhere in the project's own reports |
| **[PARTIAL]** | The project noticed a symptom but drew no correct consequence, or kept using the flawed result |
| **[SELF]** | Already identified by the project. Listed for completeness and credited; not counted as a new finding |

Throughout, *S* is the prize total (compressor plus self-extracting archive). *T* = 587,138,826 is the canonical lexical WRT length (586,459,020 on the old FX2 stream). "Payload" is the arithmetic-coded stream.

---

## 1. Executive summary

The project produced a large amount of careful, hash-verified *instrumentation*. Examples: exact native round trips, integer probability replay, independent decoders, prefix-causality tests and convex certificates. Those are real strengths and are credited in §9.

The *research conclusions*, however, rest on a measurement regime, an accounting convention and a set of acceptance gates that are each flawed. Together they explain why nine rounds produced no qualifying improvement. The twelve most consequential findings:

| # | Finding | Severity | Tag |
|---|---|---|---|
| 1 | **The GPU/native "parity gate" that blocked all core training for three rounds cannot be met by design.** The native engine's own report documents per-row "quantization-knife-edge chaos", with aggregate loss agreement of −0.0052%. The gate demanded per-row agreement (KL ≤ 1e-5 bits, max probability error ≤ 1e-3). (§5, L1) | Critical | NEW |
| 2 | **The finetuned-model "growth" that killed core training is an export artifact.** After 128 steps, 28,226 of the 28,281 non-quantized float parameters lost BF16-exactness. That is 28,226 × 2 = 56,452 new incompressible bytes, matching the measured +56,548 B/copy within 0.2%. A gates-only arm independently predicts 13,878 B against 13,767 B measured. The remaining +30,032 B/copy is tensor-order repacking. The "0.0023 bits/byte break-even" rests on this artifact. (§5, L3) | Critical | NEW |
| 3 | **Every residual and expert screen is measured in a cold-start regime that is not representative of the full file.** Cold 2M slices B/C/D cost 1.75 bits/WRT byte, against a full-file average of 1.26 (+39%). Round 8 then warmed the *candidate's* memory on genuine history while leaving the *baseline core* cold, which violates the project's own round-7 rule. (§4, D1–D2) | Critical | PARTIAL / NEW |
| 4 | **Fixed asset costs are charged against 1 MiB development gains instead of full-file gains** (~560× too large a weight). Every "priced" verdict is therefore biased negative for stationary effects. Separately, cold-slice gains may be startup-dominated, so the raw numbers are biased positive. Two opposite biases make the gates uninterpretable. (§3, M2) | High | PARTIAL |
| 5 | **The round-6 rate-aware QAT used λ = 30, a 30× over-weighting of the exact two-copy MDL rate.** At the first-order optimum the trade-off ratio is λ, so "≈9× (later 10.8×) worse than break-even" is implied by the setting itself. The run carries almost no information about rate-aware training, yet its conclusion ("needs a full retrain") was carried forward. (§3, M1) | High | PARTIAL |
| 6 | **CPU time, the binding constraint, was never priced.** The preserved baseline compresses in 55.4 h wall (196,733 s user) and decodes in 59.4 h, at 9.77 GB peak RSS (`research_round7_sources/lex_README.md:3,19`). No experiment reports incremental production CPU or bytes saved per CPU-hour. All timings come from contended, SMT-shared Kaggle vCPUs. (§2 S4; §6 E4) | High | NEW |
| 7 | **The core-finetuning protocol could not detect any effect.** It used batch 1, 128 steps, a fresh AdamW at lr 1e-5 (first steps ≈ lr·sign(g) on all 5.9M parameters), and loss on the last 256 of up to 4,096 positions, for 32,768 supervised targets in total. "Development" articles were part of the model's original 592-epoch training set. (§5, L2) | High | PARTIAL |
| 8 | **Architectures meant to test long memory were trained with 64-byte (sequence screen) and 128-byte (hidden/TTL screen) resets.** Retention beyond the block cannot be learned or measured, so the negative TTL/sequence verdicts are true by construction. (§5, L4) | High | PARTIAL |
| 9 | **The "fresh confirmation" that rejected the only learned calibration was statistically powerless.** The expected effect on a 64 KiB slice was ≈ +1.2 B, below integer-archive granularity and sampling noise. (§3, M8) | Medium | NEW |
| 10 | **Round 4's headline "−2.3% contest total" flips sign under the prize's two-copy rule:** 21.51 MB (byte model) versus 22.09 MB (dictionary model). | High | SELF |
| 11 | **The 96-family portfolio has no stopping rule.** Every family stays OPEN forever, so effort is spread over low-ceiling ideas (OCR, glyphs, Wordle) while the critical path never ran: one full warm baseline plus candidate run on qualifying hardware. $0 of $70 was spent. (§2 S1–S3) | High | NEW |
| 12 | **Reporting quality degrades usability.** There are 1,353 glued number–word tokens ("118completed", "budget70/spent0") across 88 files. Generated status blocks are prepended above superseded text. Boilerplate repeats: "20%" 141×, "deletion" 111×, "OPEN" 222×. False precision runs to 9–12 significant digits with no uncertainty. (§8) | Medium | NEW |

**Net assessment.** The infrastructure is trustworthy at the level of a single cold slice. The inferential layer (what generalizes to the full file, what pays after assets and CPU, what is statistically real) is not. The good news: fixing findings 1–3 and 6 is cheap (days and tens of dollars, not GPU-weeks). It would turn the existing tooling into a sound research platform. The companion report lays out that program.

---

## 2. Strategic and structural flaws

### S1. The test portfolio does not match the target's scale — High [NEW]
A strict >20% reduction requires payload savings of 0.27398 bits per WRT symbol (research_round7_report.md:98–101). Round 7–9 screens target effects of 10⁻⁵ to 10⁻³ of the sample cost. A few examples, as a percentage of the slice's native cost:

| Screen | Best measured gain |
|---|---|
| 15 shared causal experts (8 MB) | +1.73 B ≈ 0.0001% |
| Corrected root/new-mention | +41.9 B ≈ 0.003% |
| Semantic last-content head (8 MB) | +191.9 B = 0.0127% |
| Wider neural-difference law (E/F, 1 MiB) | +154 B ≈ 0.08% |
| Adaptive law (G/H, 1 MiB) | +340 B ≈ 0.16% |

More than 150 fitted heads were run. Even the best result is roughly **1/130 of the needed rate**. A portfolio whose *ceiling* (not just its outcome) is three orders of magnitude below the goal cannot reach the goal by accumulation, especially since gains are not additive (round 8 itself showed relation arms lose their value after generic calibration). The 20% target needed an explicit scaling argument from the start (companion report, Proposition 8). That argument shows parameter scaling is excluded and leaves only a few zero-byte levers.

### S2. The critical-path experiment never ran — High [PARTIAL]
Every report ends with "full warm production run required". In nine rounds no full-stream warm baseline was ever run, neither with nor without a candidate, on any machine. A single run needs about 55–60 single-core hours and about 10 GB RAM. On a dedicated 2-vCPU/16 GB cloud instance that is on the order of $5–15. Live prices vary; verify before renting. Meanwhile $0 of the $70 budget was spent, and "spent $0" appears about 40 times in the reports as if it were a merit. Without that run:
- the time headroom is unknown;
- warm traces for residual research do not exist (see D1);
- no candidate can be qualified.

### S3. An unfalsifiable research program — High [NEW]
Rounds 8–9 convert all ideas into "96 families", each permanently **OPEN**. Every negative result is described as "rejects this finite arm, not the family" (e.g., research_round9_report.md:25,27,111). Taken one at a time this is logically true. As portfolio management it is fatal: no family can ever be closed, priorities are never updated by evidence, and effort is diluted. The ledger (`research_round9_all96_execution_ledger.md`, 211 KB) assigns follow-up work even to OCR, low-resolution glyph codewords and CNNs over rendered text. Rounds 1–3 had already measured these as worse than zlib or ≈0.0004 bits/byte. A value-of-information rule is needed: expected saving × probability ÷ cost, with explicit kill criteria. The companion report proposes one.

### S4. The binding constraint is time, but experiments ignore it — High [NEW]
The preserved lexth11c run already sits at **55.4 h compress and 59.4 h decode wall on a 2-vCPU sandbox, with 9.77 GB peak RSS**. The rule allows 70,000/T hours per program (≈47–49 h on a Geekbench-5 ≈1,430–1,500 reference). Unless the judge's machine is substantially faster than that sandbox, *the baseline itself may be over budget*. Consequences:
1. Every added module must be paid for by removing CPU elsewhere. No experiment measured the production CPU increment, or ranked components by bytes saved per CPU-hour.
2. The project's own data imply the classical cmix bank delivers a small share of the payload for a large share of CPU. Round 5 found the classical bank adds only 1.70–2.97% over the transformer (whose input already includes the PPMD prior). Meanwhile the transformer alone is about 25 h of the run: 154.7 µs/token × 587M tokens on a 3.34 GHz Zen 2 core (cpp_infer/REPORT.md:12). This reallocation question, probably the largest systematic lever, was never posed.
3. The 615,424 B RAM margin was used, correctly, to reject large tables. No equivalent time margin exists, because none was measured.

### S5. Repository structure blocks verification — Medium [NEW]
The directory has ≈1,240 top-level entries with no index, including 549 `.py` and 486 `.json` files, and 201 one-off `*launch*`/`*status*` RPC scripts. Results, code, evidence bundles and status heartbeats sit side by side. Several reports begin with machine-generated HTML-comment blocks that *prepend* newer status above older narrative. For example, `research_round7_report.md:1–42` opens with round-8 and round-9 status, and the round-7 text follows. A reader must reconcile "historical" paragraphs against the latest checkpoint by hand. Duplicate evidence also exists: a 2.13 GB zip *and* its 18 split parts are both stored. Fix: one `README.md` index; a `results/registry.jsonl` with a single row per experiment (id, hypothesis, data, gate, outcome, status); reports generated *from* the registry, never edited in place by status scripts.

---

## 3. Mathematical and statistical flaws

### M1. λ = 30 in the round-6 MDL objective makes the "9× worse" verdict circular — High [PARTIAL]
**Evidence.** hutter_round6_report.md:130 defines $J = \mathrm{CE}_\text{bits} + \lambda \cdot 2 L_W / T$. Lines 141–148 compare λ = 0 with λ = 30 and conclude "roughly 9× worse than break-even". research_round7_training.md:36 later re-derives "10.8 times the break-even rate".

**Why it is wrong.** With CE in bits per token and $L_W$ in total weight bits, the exact prize objective (both weight copies, payload over $T$ tokens) is $J$ with **λ = 1**. At any stationary point of $J_\lambda$:
$$\frac{\partial\,\mathrm{CE}}{\partial L_W} = -\frac{2\lambda}{T}.$$
So the run trades payload for weight bits at an exchange rate λ times the break-even rate, *by construction*. Measuring a trade-off ratio of 9–11× after 100–200 steps at λ = 30 says nothing about whether rate-aware training pays at λ = 1. A ratio below 30 is expected away from convergence. On top of this, the λ = 0 control itself degraded by +2.4% (fresh optimizer on a converged, memorizing model; see L2), so the run was dominated by optimizer drift. Round 7 notes "λ = 30 is an experiment". The round-6 conclusion that compression-aware training "needs a full retrain", and the 10.8× extrapolation, nevertheless persisted.

**Fix.** Sweep λ ∈ {0.5, 1, 2} with a stable continuation (L2). Report the Pareto slope $d\,\text{payload}/d\,\text{weight bytes}$ and compare it with −2.

### M2. Amortization error in every priced gate — High [PARTIAL]
**Evidence.** research_round8_report.md:878–892 (canonical atom heads), 764–779 (native cache), 940–966 (native stage fit), and protocols with a "64-byte advancement gate". Example: the generic head gains 5.653 B on the 1 MiB A/B development sample. It is reported as "−26.85 B after two coefficient copies + 4-bit selector".

**Why it is wrong.** Coefficients are stored once per package copy and apply to all $T$ symbols. For a *stationary* effect with gain rate $g$ per MiB, the full-file saving is ≈ 560 $g$ (587M/1.05M), against a fixed cost $2c$. The correct criterion is $560g - 2c > 0$, not $g - 2c > 64$. For the generic head that is ≈ +3.2 KB against 32 B of cost, positive by two orders of magnitude.

**Two-sided bias.** Cold slices can also overstate $g$ when the effect is a startup transient. Round 8 observed this itself: "A32K pilot saved about 79 bytes and full A2M about 78: much of the opportunity is startup" (research_round8_report.md:195–196). The gate therefore mixes an anti-conservative measurement regime (D1) with an over-conservative amortization. Its verdicts are not interpretable in either direction. Note that this flaw did not hide a *large* effect (all heads are ≤ 0.1%), but it would systematically misrank scalable versus transient effects.

**Fix.** Estimate the *rate* $g$ on warm windows (D1, Experiment E0 in the companion report) with a block-bootstrap CI. Amortize over $T$. Subtract assets × copies and the CPU shadow price (S4).

### M3. One-copy MDL in round 4 reverses the sign of the "contest" result — High [SELF]
hutter_context_miner_report.md:42–51 reports 18.54 MB versus 18.98 MB. Under $S$ = compressor + archive, both containing the model: byte model 16.45 + 2×2.53 = **21.51 MB**; dictionary + cache 14.99 + 2×3.55 = **22.09 MB**, i.e. +2.7% worse. The project's own audit (research_round1_to_round7_idea_audit.md, finding 4) identified this. Credited.

### M4. Assumed 1:1 elasticity from transformer loss to payload — Medium [PARTIAL]
hutter_round6_report.md:147–148 converts "+1.7% transformer loss" into "+1.6 MB of payload". That assumes $\partial\,\text{payload}/\partial\,\text{CE}_\text{NN} = $ payload/CE. The project's own measurement contradicts this for improvements: head adaptation −0.63% NN loss → −0.02% final (hutter_round5_report.md:113), an elasticity of about 0.03. The final-coder elasticity κ is the central unknown in every NN-side decision, and it is likely asymmetric (degradations pass through more than adaptive improvements). It was never measured. **Fix:** measure κ directly with the preserved 6M/8M/10M checkpoints on warm windows (companion E3).

### M5. Round 3's TTL claim lies inside its stated noise band — Medium [PARTIAL]
hutter_ideas_report.md:13 claims −1.3% for "128 empty + 128 keep-alive" against "256 empty". Line 152 of the same file states that "differences up to about 1.5% are within run-to-run noise". Line 137 shows **128 empty slots alone (1.6981) beat the claimed winner (1.7012)**. The "noise-free within-model" ablation (blanking memory: 1.7012 → 1.7289) measures train/test distribution shift of a model trained with that memory, not the information content of the memory. The project's audit later softened this. The original verdict "Works; worth scaling up" (line 161) was never retracted.

### M6. No uncertainty quantification anywhere; false precision everywhere — Medium [NEW]
No report gives a confidence interval, standard error or bootstrap distribution for any compression gain. Meanwhile, values are printed to 9–12 significant digits ("27.923620853 bytes", "1.09744214e-08 byte certificate gap"). Optimization certificates (numerical gap ≈ 10⁻⁹ B) sit next to generalization uncertainty of order ±50%. For example, frozen wider-law gains differ by 2.5× between two fresh slices (E: 110 B, F: 44 B, research_round8_native_inline_wide_results.json), and adaptive-law replay gains range 59.8–119.5 B across C/D/E/F. With 2–4 slices per estimate (cross-slice CV ≈ 0.37), the corpus-mean gain has a relative standard error of roughly 20–30%. **Fix:** report per-window gains, a block bootstrap over ≥ 16 warm windows, and three significant figures.

### M7. Development fits use an atypical slice — Medium [NEW]
Slice A (stream offset 0) costs **0.75 bits/WRT byte**; B/C/D cost **1.75–1.79** (my computation from `research_round7_lex_{a..d}_2m_cost.f32`). Within A, the 128 K-window costs range from 0.51 to 1.00 bits/byte and trend upward. Nearly every residual head was *fitted on A/B* (A/B develop, C/D or E/F confirm). Pooling one 2.3×-cheaper, non-stationary slice with one typical slice yields coefficients that are a compromise between regimes. **Fix:** stratify development windows by cost regime and position. Never fit on fewer than ~8 windows.

### M8. Confirmation slices too small to detect the effect being confirmed — Medium [NEW]
The A/B-fitted 512 B integer calibration gained +36 B per 2M slice on C/D (out of sample). It was then "confirmed" on fresh 64 KiB E/F slices, where the expected gain is 36 × 65,536 / 2,000,000 ≈ **+1.2 B**. That is comparable to arithmetic-coder termination granularity (whole bytes) and far inside sampling noise. Observed: −1 B and −3 B actual (−0.61/−3.24 B ideal) (research_round7_report.md:997–1004). The test had essentially zero power, and the rejection is uninformative. Note: my own analysis (§4, D4) independently shows calibration headroom is ≤ ~0.03%, so the decision was right for a different reason.

### M9. "Precision-only upper bound" covers only the last quantization step — Low [NEW]
research_round7_precision_bound.py bounds the gain of replacing the final `unsigned(1+65534p)` discretization by the most favourable probability inside each bin. That is a valid bound for *that* step only. cmix's internal 12-bit stretch/squash domain, APM interpolation and mixer clamps impose earlier precision limits. The label "bound on probability precision" overstates the scope. Relatedly, my per-bin reliability analysis (§4 D4) finds ~63–72 B per 2M slice of *underconfidence* in the 0.999–0.9999 confidence bin (accuracy 0.99988 vs confidence 0.99973). A last-step bound cannot see that. Whether it comes from internal clamps or precision limits, or from model behaviour, is untested.

### M10. Post-hoc i.i.d. weight statistics were read as "weight description is exhausted" — Medium [NEW]
Round 5 (hutter_round5_report.md:92,119) and cpp_infer/COMPRESSION.md establish that the int4 indices are i.i.d. at 3.786 bits, close to the 3.907-bit maximum, and that context models do not help. The project concluded that further weight-coding gains are negligible. That inference is invalid. Near-uniform index usage is exactly what a *fixed-rate-optimized* quantizer produces (Lloyd–Max equalizes level occupancy). The container *entropy-codes* the indices, so the relevant optimum is an entropy-constrained quantizer trained under a rate penalty with λ = 1. High-rate theory puts the equal-distortion gap at 0.47 (Gaussian) to 0.93 (Laplacian) bits/weight, i.e. 0.7–1.4 MB across both copies (companion report, Proposition 2). Post-hoc coding of a fixed quantizer cannot reveal a lever that sits in training. (Note: round 2's ternary "entropy-coded = nominal" column is consistent with theory: absmean ternary indices of Gaussian or Laplacian weights have entropy ≈ 1.57–1.58 bits ≈ log₂3.)

### M11. Masking experiments were run before the theory that predicts them — Low [NEW]
research_round8_5090_hours_and_rarity_plan.md:144–158 derives that zeroing rare-word loss gives $\mathrm{KL}(P\|q_\lambda) = \log Z - r\log\lambda \to \infty$ as λ → 0. That is correct, and it predicts the measured round-9 result (total 0.644 vs 0.592 bits/symbol for "1392zero"). The experiments (two seeds × several cut-offs × 1,152 steps) were run first, and the thresholds 107/1,392/8,372 have no stated rationale.

### M12. Outcome-conditioned cost "budgets" are not recoverable budgets — Medium [PARTIAL]
Categories like "previously seen word, first mention in article" (37–43% of bits) are defined by the *realized* outcome. They are useful descriptively, but they are not the cost of a decoder-visible event class. A predictor can only act on prefix-visible features, and the conditional entropy given those features is a different quantity. I demonstrate the trap in §4 D4: per-class "realized minus expected" gaps of −44% (spaces) and +20% (markup) are pure selection artifacts of conditioning on the outcome. The project's attachment assessment (research_round8_attachment_assessment.md:13–17) states the principle. The planning documents still use the 37–43% category as a "budget" (e.g., research_round7_lex_residual_findings.md "would require recovering 49.5–58.1% of its current bits").

### M13. Denominator inconsistency — Low [NEW]
Reports use 100,424,672 (official record). The preserved lexth11c README lists the same entry as "fx2-cmix-transformer (pending) 100,420,830" (research_round7_sources/lex_README.md:26). The 3,842 B difference is never reconciled, despite the project's repeated insistence on not switching denominators.

---

## 4. Data-science and experimental-design flaws

### D1. The cold-slice regime is unrepresentative, and the bias was never quantified — Critical [PARTIAL]
**Evidence (my computation).**

| Native cold 2M slice | Bits per WRT byte | Ratio to full-file mean |
|---|---:|---:|
| A (offset 0) | 0.750 | 0.59 |
| B (102.6M) | 1.748 | 1.39 |
| C (100M) | 1.788 | 1.42 |
| D (180M) | 1.757 | 1.39 |
| Full file, lexth11c | 92,559,456 × 8 / 587,138,826 = **1.261** | 1.00 |

Excluding the cheap metadata tail (~0.77 bits/byte measured in round 6), main text averages about 1.33 bits/byte. So the cold main-text slices cost about **30–35% more** than warm main text. Part of this is content, but cold PPMD/cmix tables, untrained mixer weights and empty match histories plausibly dominate.

**Why it matters.** A residual that helps a *cold* coder (calibration, re-weighting toward the pretrained transformer, short-range memory) can be worth much less on a warm one. The frozen "wider" law pushes final log-odds about 20% toward the neural log-odds:
$$\theta_2/12 \approx 0.198 \quad\text{(research\_round9\_report.md:13)}.$$
That is precisely the kind of correction expected while cmix's mixers have not yet learned to trust the transformer. It may shrink in the warm regime. It may not, but it has never been tested. The project repeatedly labels results "cold" and never measures the size of the effect.

**Fix.** One instrumented full warm run (companion E0) that stores final p, NN p, pre-SSE p and the first-layer mixer outputs. Alternatively, fork-based warm snapshots at window boundaries. Evaluate all residual laws on warm windows.

### D2. Asymmetric warmth: warm candidate versus cold baseline — High [NEW]
research_round7_pre_experiment_report.md:604–609 states the correct rule: a warm-retrieval comparison is illegitimate "if only the candidate receives earlier history". research_round8_report.md:278–281 and 415–418 then do exactly that: "the statistical source is reconstructed incrementally from the real earlier full old-FX2 stream… the core probabilities are still cold slice probabilities"; "State is warmed on genuine earlier full-source bytes, while native core traces remain cold". The directed-memory, title and warm-source results are biased in favour of the candidate. A cold core lacks exactly the knowledge the warm memory supplies.

### D3. Repeated reuse of the same few slices for fitting, selection and confirmation — Medium [SELF/PARTIAL]
A/B (fit), C/D (develop, later re-used as "exploratory confirmation"), E/F (fresh in round 7, then re-used repeatedly in rounds 8–9) all fed decisions. Only G/H were registered in advance (round 9). The project acknowledges "C/D have now informed the research decisions". The result is a garden of forking paths over 150+ heads, which inflates any apparent positive finding. Fix: a single untouched, pre-registered confirmation pool of ≥ 16 warm windows, opened once per candidate family.

### D4. Calibration headroom is essentially exhausted; the realized-versus-expected gap is misleading — Medium [NEW, verifies the project's nulls]
I computed the native final coder's reliability on all 64M coded bits of A–D (Appendix B.3):
- Per-confidence-bin accuracy matches confidence within ≈0.3% everywhere. There is slight overconfidence at 0.8–0.98 and slight underconfidence at 0.999–0.9999 (accuracy 0.99988 vs confidence 0.99973).
- The **in-sample upper bound** for an 11-parameter per-bin temperature recalibration is **112–122 B per 2M slice (≈0.03%)**.
- A strictly causal online logistic recalibrator (16 bins × 8 bit positions) *loses* 78–93 B per 2M on B/C/D (Appendix B.2).
- The realized minus expected-entropy gap is 0.80–0.87% on B/C/D. That gap is *first order* in the miscalibration, while recoverable KL is *second order*. A large gap therefore coexists with negligible recoverable gain.
- Splitting the same gap by the *realized* byte class gives −44% for spaces, −3% for code-first bytes, +20% for punctuation/markup and +41% for escapes. These numbers are selection artifacts of conditioning on the outcome, not miscalibration. That is the M12 trap made concrete.

Conclusion: no further work on final-probability calibration is justified. Gains must come from new information sources.

### D5. Held-out protocol in rounds 2–4 versus the contest regime — Medium [PARTIAL]
Rounds 2–4 evaluate on held-out articles. The prize trains on the very file it compresses (592 epochs). Generalization-oriented mechanisms (kNN over training states, online adaptation, ensembles of snapshots) behave very differently when the test text was memorized. kNN over the model's own training-set states retrieves memorized continuations. Their toy gains (−3% to −8%) were nonetheless used as motivation for the real pipeline, where round 6 measured neural-cache gains of only 0.045–0.084%. The transfer was never justified.

### D6. Test-set selection of hyperparameters (rounds 2–4) — Low [SELF]
Acknowledged in hutter_context_miner_report.md:149: learning rates, mixer variants and ensemble composition were selected on the test set, a 0.1–0.3% effect against a 0.3% margin.

### D7. Timing measurements cannot qualify anything — High [NEW]
All CPU figures come from Kaggle 4-vCPU (2-core SMT) VMs, often with two cmix processes running concurrently (research_round7_pre_experiment_report.md:115–118). The upstream engine's own measurement shows an SMT sibling costs **−55 to −57% throughput** (cpp_infer/REPORT.md, §5 table). Lab builds also lack PGO/LTO. Example: the H-slice candidate encode used 461.8 s CPU against the teacher's 404.8 s for the same 512 KiB (research_round9_adaptive_native_v2_results.json). A 14% "difference" for a module that costs about five transcendental operations per bit is noise. Fix: dedicated, pinned, Geekbench-scored machine; production PGO build; median of ≥ 3 runs; report incremental µs/bit.

---

## 5. Machine-learning flaws

### L1. A mis-specified parity gate blocked core training for three rounds — Critical [NEW]
**Evidence.** The gate (research_round7_pre_experiment_report.md:311–317) requires mean |ΔNLL| ≤ 0.005 bits, max ≤ 0.1, mean KL ≤ 1e-5 bits and max |Δp| ≤ 1e-3, *per row*. Measured: mean |ΔNLL| = 0.026, max 2.01, KL 0.0022 (research_round7_frozen_logits_parity_diagnostic.json). Rounds 8–9 then ran four "GPU layer differential" versions trying to close the gap (research_round9_report.md:39).

**Why it was hopeless.** The model uses dynamic per-token int8 activation quantization (`TF_ACTQ_DYN`, research_round9_native_build_dependencies_v1/cpp_infer/src/opt/tf_arch.h:11–17), int8 KV rings and recurrent KDA state. Any 1-ulp difference in a pre-quantization value flips a rounding decision ("knife edge"). That perturbation then propagates through recurrence. The engine authors document exactly this: "132 flips of ±1 in 11.1M ints (rounding knife-edges)… Chained drift proven inherent via an independent exact-fp32 numpy chain… per-row diffs are symmetric quantization-knife-edge chaos seeded at ~4e-6… loss-neutral" (cpp_infer/REPORT.md:36–48), with full-set loss agreeing to **−0.0052%**. The diagnostic's own offset profile (error growing from 0.004 to 0.043 bits with context length, mean signed difference ≈ +0.0003 bits) is the signature of symmetric chaotic divergence, not of a bug. The evidence sat in a file the project had preserved locally.

**Consequence.** Core training was gated on an unachievable per-row criterion. Effort went into bit-exact kernel emulation instead of the actual question: does the GPU training path produce weights whose *native aggregate* loss improves?

**Fix (companion E2).** A distribution-level gate:
1. Aggregate native vs GPU CE on ≥ 4M warm tokens agrees within 0.02%.
2. Paired per-article CE differences have mean zero (|t| < 2).
3. Trained-checkpoint *rankings* agree between GPU and native evaluation.

Then train on GPU and *select* on native.

### L2. The finetuning protocol had no statistical power — High [PARTIAL]
**Evidence.** research_round9_core_training_worker_v2.py:83–85: `AdamW(lr=1e-5, weight_decay=0)`, freshly constructed; 128 steps; one sampled window per step; loss on the last 256 targets of a ≤ 4,096-token prefix. That is 32,768 supervised targets in total. Development articles are every fifth article of the same 262 KiB corpus (line 73), and *all of them were in the original 592-epoch training set*.

**Why it is wrong.**
1. A fresh Adam's first update is ≈ lr·sign(g) for every coordinate (m̂/√v̂ = ±1). That is an isotropic 1e-5 perturbation of all 5.9M shadow weights per step, applied to a model sitting in a sharp, memorizing minimum. The matched λ = 0 control degrading by +2.4% in round 6 is the same phenomenon.
2. With 32K targets (5.6×10⁻⁵ of one epoch) no masking or weighting policy can produce a detectable *improvement*. Only drift is measurable.
3. Loss on 256 of 4,096 positions wastes ≈94% of each forward pass.
4. A "development" split of memorized articles measures forgetting, not generalization, and the relevant objective is full-file loss anyway.

**Fix.** Warmup from lr ≈ 0 over ≥ 500 steps (or restore optimizer state). Use ≥ 64 full pieces per step with loss on all positions, token-weighted sampling over the whole canonical stream, ≥ 2,000 steps, and full-stream (or stratified-window) evaluation. A λ = 0 control must hold full-file loss within +0.02% before any arm is interpreted.

### L3. The export artifact that inflated every trained model by ~56 KB per copy — Critical [NEW, verified]
**Evidence (my computation, Appendix B.5).** I parsed the preserved checkpoints without PyTorch:

| Parameter class | Elements | Changed after 128 steps | Non-BF16-exact, zero-update | Non-BF16-exact, trained |
|---|---:|---:|---:|---:|
| Quantized weights (snapped to codebook on export) | 5,868,864 | 5,862,924 (shadow) | 3,071,998 | 5,865,311 |
| Row scales | 25,973 | 0 | 0 | 0 |
| Codebooks | 2,385 | 0 | 0 | 0 |
| **Other floats** (dt_bias, convolutions, β-projection, norm gates, coefficients) | **28,281** | **28,226** | **0** | **28,226** |

The FX2TFWC3 container codes raw float tensors with per-byte-plane adaptive models (cpp_infer/COMPRESSION.md, "v2" table). BF16-exact float32 values have two zero low bytes and cost almost nothing. After training, those two bytes are noise: 28,226 × 2 B = **56,452 B**. Measured growth of the order-preserving export: 3,034,587 − 2,978,039 = **56,548 B/copy** (research_round9_native_promotion_v1_results.json, `model_delta_per_copy`). The two agree to within 0.2%.

A second, independent confirmation comes from the "recurrent_gates_high" selective arm. It trains only `beta_projection`, `log_baseline_decay_rate`, `dt_bias` (free floats) and the forget/output gate projections, which are quantized and re-snapped (research_round9_core_selective_worker.py:59). Its free floats number 9 KDA layers × (576 + 3 + 192) = 6,939. That predicts 13,878 B of growth; the measured value is **13,767 B** (−0.8%).

The earlier +85,922 B figure additionally contained +30,032 B of tensor-reordering overhead (zero-update repack: 3,008,071 B, research_round9_core_export_v2_results.json).

**Consequence.** research_round9_training_and_5090_plan.md:78–83 derives a break-even of 0.0023416 bits/byte "for a model adding 85,927 B". About 99.8% of that cost is avoidable:
- round the 28K free floats to BF16 (or train them with a BF16 straight-through estimator, or freeze them);
- export in the original tensor order.

The true cost of a finetune is only the entropy change of the int4 code indices, likely a few KB. A "core_bf16_qat" job appears in the latest snapshot, but no report states the cause or retracts the break-even analysis.

### L4. Long-memory architectures trained with short resets — High [PARTIAL]
- Sequence screen: "fixed 64-byte resets" (research_round9_report.md:25).
- Hidden/TTL screen: "Decay targets 1/8/64/512 completed bytes, but block resets bound effective retention to 128 bytes" (line 27).

Decay constants of 64–512 events are unlearnable and untestable when the state is wiped every 64–128 bytes. These models compete against a final coder with unlimited history. The project stated the bound and still recorded "model bytes do not pay" as a verdict on the family (TTL). Fix: truncated BPTT with state carry-over across blocks (detach, but do not reset), and episodes of ≥ 16 K bytes.

### L5. Word-level heads were undertrained by orders of magnitude, then priced at slice scale — Medium [NEW]
word_softmax v1/v2 and word_warmstart trained 44,515-way output layers and spelling composers for 128–1,152 steps on ~1 MiB of A/B. They were evaluated on 1 MiB E/F *as incremental residuals behind an adaptive law that already absorbs the easy signal*, and priced against model sizes of tens of KB per copy. A 44,515-class softmax sees each class a handful of times in that budget. The negatives (−3 to −25 B) are uninformative about word-level modelling. Note that the competitor cmix-neif obtained part of its −3.4% over lexth11c from an online word-level model (research_round8_neif_architecture_audit.md:17–19).

### L6. The strongest positive signal was mis-diagnosed as a tiny head rather than a mixer defect — Medium [NEW]
Every positive result in rounds 8–9 is driven by the neural channel: neural_difference 89.3 B, neural_valid 91.1 B, wider law, adaptive law (research_round8_report.md:956–966). The fitted law moves final log-odds about 20% toward the neural log-odds. That is a *diagnosis*: cmix's final mixer plus SSE/APM chain under-uses the transformer, at least in cold state. The principled response is an architectural one (a learned, contextual post-SSE mixer with the NN as a direct input, plus warm-state verification). A frozen 3-coefficient law with a 5-expert fixed-share wrapper is not. Companion E4.

### L7. Mixed-precision and finetuning experiments ignore the float-constant channel — Low [NEW]
Related to L3: the post-training sparsification study (research_round7_ptq_native_results.json) and the selective-training arms change float constants without BF16 re-snapping. Storage deltas are therefore confounded by mantissa noise.

---

## 6. Engineering flaws

### E1. Ephemeral Kaggle sessions as the primary research platform — High [NEW]
Sessions last at most 12 h. /root scratch is wiped. RPC calls are bounded at 50 s through a WebSocket proxy that repeatedly failed ("Kernel WebSocket connection failed", HTTP 404, at least six distinct session IDs across rounds 7–9). A large share of the artifacts are recovery, preservation, heartbeat and status scripts (201 `*launch*`/`*status*` files). A full warm run (55–60 h) is *impossible* on this platform. That single fact explains S2 and D1. A $5–15 dedicated CPU instance removes the whole class of problems.

### E2. Experiments generated by string-patching and `exec` — Medium [NEW]
Example: research_round7_frozen_logits_pilot_v2_worker.py reads an earlier worker's source, applies `replace_once` text substitutions, writes an "effective" file and runs it with `exec(compile(source, …), globals())`. Several failures stem from this style. One is the round-9 `core_distributed_v1` failure, where importing the core overwrote a manifest variable in the shared global namespace (research_round9_report.md:117). Fix: importable modules, explicit parameters, no global-namespace `exec`.

### E3. Remote launches without local static checks — Medium [PARTIAL]
Each of these failed only after a remote launch, costing a session cycle:
- syntax error in `continuous_v1` (research_round8_report.md:365);
- missing `/usr/bin/time`, lost executable bit, omitted `-d` decoder flag (line 848);
- NumPy-2 float32 weak-scalar promotion bugs, twice (round 6 cache evaluator; round 9 adaptive validation, research_round9_report.md:31);
- slice-EOF handling defects, look-ahead in the root scorer, title-tag contamination, context-key namespace collisions.

A minimal pre-flight (`python -m py_compile`, `ruff`, a 4 KB synthetic end-to-end run, explicit dtype assertions) would have caught most of them.

### E4. Lab builds are not production builds — Medium [PARTIAL]
Research binaries use no PGO/LTO, x86-64-v3 and extra instrumentation. The production lexth11c uses PGO+LTO with runtime-dispatched AVX-512 VNNI. Archive bytes match, but CPU, RSS and executable-size deltas do not transfer (the project notes "lab binary delta 768/784/1,904 B"). Production-flag A/B builds are needed for any CPU or size claim.

### E5. No warm-state infrastructure — High [NEW]
cmix has no state serialization, but Linux `fork()` gives copy-on-write snapshots for free. Run the baseline once, fork at window boundaries, and evaluate candidates in the forked children from identical warm states. This, or an instrumented full trace, is the missing piece behind D1 and D2.

### E6. Portability and reproducibility hygiene — Low [NEW]
Absolute Kaggle paths are hard-coded in nearly every script (`/kaggle/working/hp_round7/…`). There is no package layout, no lockfile for the Python stack (Python 3.12/Torch 2.10 on Kaggle versus the declared 3.11/2.12), no tests directory, and the local Windows environment cannot run the Linux-specific `resource`/`wait4` accounting.

---

## 7. Programming flaws (code level)

| ID | Location | Defect | Severity |
|---|---|---|---|
| P1 | research_round9_adaptive_law.cpp:1 | `#include "hp_adaptive_law.h"`, but the preserved header is `research_round9_adaptive_law.h`. The preserved source does not build as stored. | Low |
| P2 | research_round9_adaptive_law.cpp:6–30 | Production probability law uses `std::log`/`std::exp` (platform libm) with double rounding into Q16. Encoder and decoder must use bit-identical libm. Safe on one machine, but a cross-machine or cross-libc decode (the lexth11c README tests an AMD leg) can desynchronize. Use integer stretch/squash tables, as paq/cmix do. | Medium |
| P3 | research_round7_frozen_logits_pilot_v2_worker.py:43–79 | Source patching by literal string replacement, then `exec(..., globals())`. See E2. | Medium |
| P4 | research_round7_frozen_parity_diagnostic.py:6–7 | Parity compared on float16-stored probabilities (`'<f2'`). Adequate for the observed failure size, but sub-6e-5 probabilities are subnormal and lose relative precision. A KL ≤ 1e-5 gate was specified against data whose storage noise floor is never stated. | Low |
| P5 | hutter_exp4_code/full_tok.py:163–190 | kNN datastore of fp16 keys for 25.8M states = 14.86 GB, beyond the 10 GB RAM bound (credited to the project's audit). | Medium [SELF] |
| P6 | hutter_exp4_code/tcm.c:90 | Context hash tables without check bytes: collisions silently merge contexts. Acceptable for a stand-in, but the stand-in's weakness (1.82–1.89 bpb) drove "blend" conclusions in rounds 2–4. | Low |
| P7 | hutter_exp4_code/dyn_cache.py, knn_cache.py | `best_single_lambda_bpb` (an in-sample oracle) is computed and saved next to online results. The reports were careful, but the artifact invites misuse. | Low |
| P8 | research_round9_core_training_worker_v2.py:85 | The per-window ratio `(CE*w).sum()/w.sum()` is a biased estimator of the stated corpus objective Σw·CE/Σw (expectation of a ratio ≠ ratio of expectations). With batch 1 and 256-target windows, windows dense in rare words are silently up-weighted relative to the declared objective. | Low |
| P9 | status/report generators (e.g., research_round8_refresh_current_handoff.py) | Generators prepend blocks into human reports and strip whitespace around numbers (§8, R1). | Medium |
| P10 | research_round8_hidden_cache_executed_worker.py | Field named `…3bit_selector_bytes` actually charges a 4-bit selector (acknowledged, not fixed, "to avoid editing a queued worker"). Naming drift in evidence files. | Low |

---

## 8. Reporting and formatting flaws

### R1. Systematic whitespace corruption — Medium [NEW]
A regex scan (Appendix B.6) finds **1,353 glued number–word tokens in 88 report files**. Fifteen files have ≥ 20, led by the round-9 ledger (129), the round-7 pre-experiment report (124) and the round-7 report (120). Examples: "118completed finite native fitted heads,27online role policies", "budget70/spent0", "1.731295ideal bytes/8M", "5897145total scalars". A generator evidently removed spaces adjacent to numbers. In a numbers-heavy research record this makes values ambiguous and unsearchable.

### R2. Append-only logs presented as reports — Medium [NEW]
research_round7_report.md is a chronological log: running statuses, heartbeats ("Read-only heartbeat 5 October 14:27 UTC confirmed…"), credential and Goal-status chatter, and superseded results, all above and below the current state. Readers are told to read "the checkpoint" to know which paragraphs are true. A report should state the current state first and keep the history in a changelog.

### R3. Boilerplate overwhelms content — Low [NEW]
Across the 76 Markdown files the phrase "20%" appears 141 times, "deletion" 111, "OPEN" 222, "qualifying" 73, "Goal" 83, "absolute optimum" 26. Disclaimers are repeated in nearly every paragraph. The signal-to-noise ratio of the record is low.

### R4. Internal contradictions — Low [PARTIAL]
Examples:
- "No project deletion" versus eleven redundant paths removed (corrected in research_round9_report.md:96).
- "95 families" versus "96 families" in adjacent documents.
- research_round7_report.md:1–42 (round-8/9 status) contradicts its own body (round-7 status).
- Round-6 "S1 candidate 3,369,451 B" is used as a component of projected totals that mix FX2 and lexical baselines.

### R5. Mixed baselines and units in adjacent tables — Low [NEW]
Within single sections, numbers switch between FX2 old-stream and lexical canonical baselines (193,366 vs 187,363 B for "slice A baseline"), ideal versus actual archive bytes, per-slice versus per-8 MB totals, and one versus two package copies. Each table needs an explicit baseline id and unit column.

---

## 9. What the project did well (credit where due)

1. **Exactness discipline.** Native archives, independent decodes, SHA-pinned inputs, integer replay of every Q16 probability, and neutral-mode identity checks are excellent and should be kept.
2. **Causality hygiene.** Prefix-measurability (the $\mathcal F_t$ contract), "insert after decode" memory semantics, and future-mutation non-interference tests are correct and important.
3. **Real wins.** The round-5/6 structural tail experts (−274,829 B over two fully scored regions, unchanged CPU) and the bf16/float container work are genuine, mechanistically understood gains.
4. **Self-correction.** The rounds 1–7 audit correctly retracted the round-4 package claim, the kNN memory feasibility and the FX2→lexical packing transfer.
5. **Correct mathematics in the small.** I re-derived and confirmed:
   - KT marginals;
   - the CTW-style stop/split posterior σ(ℓ − s) in natural-log units (research_round8_conditional.cpp:32);
   - supporting-plane certificates;
   - fixed-share identities;
   - the strongly convex contextual-intercept bracket [−1/λ, 1/λ];
   - the gradient-projection inequality $g_C \cdot d^* = \max(g_C\cdot d, 0) \ge 0$;
   - the masking KL identity;
   - all the arithmetic in the prize-threshold ledgers (80,339,737; 79,449,939; 76,731,240; 0.27398 bits/symbol; 0.019432 bits/symbol for a 712,240 B table; 95.4 T MACs; 11.67 GB of logits).

   The errors are in *what was measured and how it was priced*, not in algebra.

---

## 10. Prioritized fixes (one-line each)

1. Replace the per-row parity gate with a distribution-level gate (L1).
2. BF16-snap free floats and preserve tensor order on export; re-price all trained candidates (L3).
3. Rent one dedicated CPU instance; run the full warm baseline once with trace export and per-component CPU instrumentation (S2, D1, D7, E1, E5).
4. Re-derive every gate as *full-file rate × T − copies × assets − μ × ΔCPU*, with bootstrap CIs (M2, M6, S4).
5. Fix the continuation protocol (warmup, batch, full-piece loss, full-stream evaluation) before any rate or masking study (L2, M1).
6. Retrain long-memory heads with state carry-over (L4).
7. Close low-value families explicitly; adopt a value-of-information portfolio (S3).
8. Restructure the repository and regenerate reports from a results registry (S5, R1–R5).

---

## Appendix A. Evidence index for headline numbers

| Number | Source |
|---|---|
| lexth11c S = 99,313,750; payload 92,559,456; weights 2,978,039 ×2 | research_round7_sources/lex_README.md:10–16 |
| Compress 55:24:11 wall, 196,733 s user, 9,765,024 kB; decode 59:26:45 | lex_README.md:3,19 |
| Transformer 6,464 tok/s, 154.7 µs/token (Zen 2 3.337 GHz) | research_round9_native_build_dependencies_v1/cpp_infer/REPORT.md:12 |
| Knife-edge chaos, −0.0052% aggregate loss | cpp_infer/REPORT.md:30–48 |
| Parity gate and failure | research_round7_pre_experiment_report.md:311–317; research_round7_frozen_logits_parity_diagnostic.json |
| Model growth 85,922 B; break-even 0.0023416 | research_round9_training_and_5090_plan.md:78–83 |
| Ordered export growth 56,548 B; selective 13,767 B | research_round9_native_promotion_v1_results.json |
| Zero-update repack +30,032 B | research_round9_core_export_v2_results.json |
| λ = 30 QAT | hutter_round6_report.md:130–148 |
| Classical bank adds 1.70–2.97% | hutter_round5_report.md:94 |
| Wider law θ | research_round9_report.md:13 |
| Startup-dominated paid policy | research_round8_report.md:195–196 |
| E/F 64 KiB calibration −1/−3 B | research_round7_report.md:997–1004 |
| 64/128-byte resets | research_round9_report.md:25,27 |

## Appendix B. Reproducible diagnostics run for this audit

All inputs are the project's preserved local files. All scripts ran with local Python 3.13 / NumPy 2.4 and MSYS2 gcc. Scripts live in the session scratchpad; their logic is reproduced here.

**B.1 Cold-slice cost.** Sum `research_round7_lex_{s}_2m_cost.f32` (float32 bits per WRT byte) and divide by 2,000,000. Report per-128 K-window means.

**B.2 Causal online recalibration** (`coldstart.c`). For each bit:
1. $p = n/65536$, $\ell = \operatorname{logit}p$;
2. context = bit position × min(15, ⌊2|ℓ|⌋);
3. $q = \sigma(a\ell + b)$, rounded to Q16;
4. after observing the bit, SGD with lr = 0.002 on $(a, b)$.

Result (bytes gained per 2M slice): A +47.1, B −93.4, C −80.3, D −78.0.

**B.3 Reliability and per-bin temperature bound** (`rel.py`). Bin bits by confidence max(p, 1−p) into 11 bins and compare accuracy with mean confidence. Inside each bin, grid-search a log-odds multiplier t ∈ [0.5, 1.5] (101 points) and take the in-sample minimum CE. Bound: A 111.6 B, B 117.7 B, C 121.6 B, D 115.5 B per 2M slice.

**B.4 Bit anatomy** (`anatomy.py`, `gate.py`). Classify every WRT byte with the project's own inverse map (`research_round7_wrt.py`): dictionary code first byte, code continuation, case control, escape, literal letter, space, newline, digit, punctuation/markup. Attribute native per-byte cost. The resulting pooled table is used in the companion report, §1.

**B.5 Checkpoint float audit.** Custom `pickle.Unpickler` with stubs for `torch._utils._rebuild_tensor_v2`, reading raw storages from the `.pt` zip (no PyTorch needed). Compare `research_round9_native_evidence/core_models/selected_core_zero_update.pt` with `unweighted_step128.pt`. Classify tensors: quantized weight (has `.quantize_weight.scale`), scale, codebook, other float. Count changed elements and elements whose low 16 mantissa bits are non-zero.

**B.6 Glued-token scan.** Regexes `(?<![\w./-])\d[\d,.]*[a-z]{3,}(?!\w)` and `(?<![\w/-])[a-z]{3,}\d[\d,.]*`, minus an allow-list of legitimate identifiers (fx2, enwik9, sha256, float32, log2, zlib9, …). Run over all `*.md`/`*.txt` in the directory: 1,353 hits in 88 files.
