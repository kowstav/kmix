# What to do next: a measured synthesis, a theory of where compression can still come from, and a ranked experimental program

**Author:** Claude (Opus 5.5), independent review.
**Date:** 7 October 2026.
**Companion:** `CLAUDE_AUDIT_01_FLAWS_REPORT.md` (flaws). This document is constructive: it synthesizes the reports' data and my own recomputations on the preserved traces, then builds a theory and an experimental program on that basis.
**Baseline used throughout:** lexth11c, S = 99,313,750 B (payload 92,559,456; weights 2,978,039 per copy; T = 587,138,826 canonical WRT bytes). Reference targets: official record 100,424,672; reported pending cmix-neif 95,914,051.

---

## 0. Executive summary

**Three findings drive everything below.**

1. **The record is already at the two-copy-MDL optimum in parameter count** (Proposition 1). Calibrate a log-linear payload model with the project's only clean scaling measurement (round 2: 2.37× parameters gave −6.1% bits, elasticity ε ≈ 0.073). The marginal payload gain from more parameters, ≈ 6.3 MB per log-unit, equals the two-copy weight cost of 5.96 MB per log-unit to within the uncertainty. **Adding parameters cannot help.** Every remaining first-order lever is one that costs *no parameter bytes*:
   - fewer bits per parameter;
   - compute that does not add parameters;
   - decoder-side information (memory, structure, order);
   - better objectives.
2. **Bits are concentrated, compute is not** (Proposition 4, my measurement on 64M native coded bits).
   - Dictionary code bytes are 38.9% of WRT bytes and carry 68.7% of the bits.
   - Positions right after a space or case control are 29% of bytes and carry 52% of the bits.
   - 35% of positions have decoder-visible expected entropy below 0.1 bit and carry 0.12% of the bits.

   The transformer spends identical compute on all of them. Ideal entropy-proportional reallocation at fixed total compute is worth ε·(1−R(α))/α ≈ **3.8–5.0% of the neural-attributable payload**, with R(α) measured. That is equivalent to ~1.7× compute for free.
3. **The record's weight quantizer is optimized for the wrong rate model** (Proposition 2). Index usage is near-uniform (3.78 of a maximum 3.91 bits), the signature of a *fixed-rate*-optimal quantizer. The container, however, entropy-codes the indices. High-rate quantization theory gives up to ≈0.47 bits/weight (Gaussian) or ≈0.93 bits/weight (Laplacian) saving at equal distortion from entropy-constrained scalar quantization (ECSQ). That is **0.7–1.4 MB** across both copies, before Fisher-optimal per-tensor allocation adds an estimated 0.2–0.8 MB.

**Verdict on the 20% target.** Proposition 8 shows that reaching ≤ 79.45 MB by model scaling would require ~35× the parameters (≈100 MB of weights per copy) and ~35× the CPU. That is infeasible by two orders of magnitude. All levers that are not scaling are estimated in §2.11:

| Scenario | Estimated total saving vs lexth11c | Resulting S |
|---|---|---|
| Pessimistic | ≈ 2% | ≈ 97.3 MB |
| Central | ≈ **4.5–6%** | ≈ 93.4–94.8 MB |
| Optimistic, all levers succeed | ≈ 9–12% | ≈ 87–90 MB |

The central range beats the 1% prize threshold and the reported pending entries (including cmix-neif at 95.9 MB). It does not reach 20%. A 20% result would need several breakthroughs each the size of the LSTM → transformer transition (7.5%); no evidence in this directory supports one.

**The program I recommend** (§4) is ordered by value of information per dollar:

- **Tier 0 (≤ $20, days).** These unblock everything.
  - E0: one full warm instrumented baseline run on a dedicated CPU instance.
  - E1: export repair (BF16 snap plus tensor order).
  - E2: a distribution-level parity gate.
  - E3: elasticity calibration with the preserved 6M/8M checkpoints.
- **Tier 1 (CPU only, weeks).**
  - E4: a post-SSE NN-aware mixer.
  - E5: a per-component CPU-efficiency audit and pruning.
  - E10: article-order optimization.
  - E11/E12: structural experts and precision.
- **Tier 2 (GPU, $50–150).**
  - E6: stable continuation with ECSQ and Fisher allocation.
  - E7: complementarity training.
- **Tier 3 (architecture, beyond $70).** E8/E9: the two-timescale, zero-byte-memory architecture "TIDE-Z" (§3).

---

## 1. What the evidence actually says

### 1.1 The package ledger (lexth11c)

| Component | Bytes | Copies | Contribution to S | Share |
|---|---:|---:|---:|---:|
| Payload | 92,559,456 | 1 | 92,559,456 | 93.20% |
| Transformer weights (FX2TFWC3) | 2,978,039 | 2 | 5,956,078 | 6.00% |
| Stub (UPX/LZMA) | 198,236 | 2 | 396,472 | 0.40% |
| Dictionary | 100,866 | 2 | 201,732 | 0.20% |
| Article order (compressor only) | 199,980 | 1 | 199,980 | 0.20% |
| Headers | 16 | 2 | 32 | ~0 |
| **Total** | | | **99,313,750** | 100% |

Measured constraints (research_round7_sources/lex_README.md):
- compress 55.4 h wall, 196,733 s user;
- decode 59.4 h wall;
- peak RSS 9,765,024 kB (615,424 B below decimal 10 GB);
- the transformer alone takes 154.7 µs/token on a 3.34 GHz Zen 2 core, ≈ 25 h for T tokens (cpp_infer/REPORT.md:12).

**Time and memory are both saturated.**

### 1.2 Where the bits are: a new measurement

I classified all 8,000,000 WRT bytes of the four preserved 2M slices with the project's exact inverse WRT map and attributed the native final-coder cost (`research_round7_lex_{a..d}_2m_cost.f32`; method in audit Appendix B.4).

| WRT byte class | Share of bytes | Share of bits | Bits/byte |
|---|---:|---:|---:|
| Dictionary code, first byte | 21.65% | **44.73%** | 3.121 |
| Dictionary code, continuation byte | 17.20% | **24.00%** | 2.108 |
| Literal letters (OOV spelling) | 8.41% | 10.77% | 1.933 |
| Punctuation / markup | 17.17% | 9.65% | 0.849 |
| Digits | 4.09% | 3.49% | 1.288 |
| Case control | 5.57% | 3.12% | 0.847 |
| Spaces | 23.36% | 3.03% | 0.196 |
| Newlines | 2.21% | 0.96% | 0.658 |
| Escapes | 0.33% | 0.25% | 1.179 |

Concentration (pooled):
- the top 10% of bytes carry 46.4% of bits, the top 25% carry 82.6%, the top 50% carry 99.3%;
- 47.0% of bytes cost < 0.1 bit and together carry 0.44% of bits.

**Gates.** The previous-byte classes are known before the byte. $H_t$ is the sum of per-bit entropies along the realized bit path. It is a close proxy for the byte-level predictive entropy, which the transformer's 205-way softmax supplies exactly before the byte.

| Gate | Share of bytes | Share of realized bits |
|---|---:|---:|
| Expected entropy H_t < 0.1 bit | 34.9% | 0.12% |
| Expected entropy H_t < 0.2 bit | 40.6% | 0.34% |
| Previous byte is a space | 23.4% | **41.4%** (2.68 bits/byte) |
| Previous byte is a case control | 5.6% | 10.4% (2.81 bits/byte) |

Calibration (64M coded bits): per-confidence-bin accuracy matches confidence within ≈0.3%. The in-sample upper bound for *any* per-bin temperature correction is 112–122 B per 2M slice (≈0.03%). **Final-probability calibration is exhausted.**

### 1.3 The magnitude map of everything tried

| Family (rounds) | Best measured effect | Regime | Interpretation |
|---|---|---|---|
| Structural tail experts: timestamp, contributor, username, interwiki title (5–6) | **−274,829 B (−0.28% of S)** | full regions, cold | Real, mechanistic, CPU-free. Port to the lexical pipeline |
| fxcm_v26 classical model (5) | −0.25 to −0.40% | 2M slices | Already in lexth11c |
| bf16 floats, FX4 C5 codec, UPX-LZMA (5–7) | −55 to −110 KB | component exact | FX2-only; C3 already better |
| Adaptive / wider neural-emphasis law (8–9) | −0.06% to −0.17% | cold 512K | Signal = NN under-weighted by final mixer (E4) |
| Neural cache / hidden-state kNN (6, 8) | −0.045 to −0.084% | cold | Absorbed by match models |
| Final-probability calibration (7, this audit) | ≤ 0.03% (in-sample) | cold | Exhausted |
| Exact field/line copy, edit automata, numeric programs (7) | ≈ 0 (±10 B/2M) | cold | Exhausted at this donor design |
| Spelling/letter-moment echoes, anagram, glyph (3, 7, 8) | ≈ 0 | cold | Exhausted (no information beyond letters) |
| Topic unigram / paid topic profiles (7) | negative | cold | Exhausted |
| Semantic graph (GloVe, 614 KB) (8) | −0.0127% (saving); graph unaffordable | cold | Signal real, mechanism too expensive |
| Word-softmax / sequence / TTL heads (9) | worse than reference | 1 MiB, ≤ 1,152 steps, 64–128 B resets | Uninformative (audit L4, L5) |
| Core finetune (9) | −14 to −105 B per 64 KiB (saving); model +56 KB/copy | cold | Model cost is an export artifact (audit L3) |
| Loss masking (9) | negative, as theory predicts | cold | Close |
| Any-order / Wordle / skeleton (1, 3) | +2% to +130% worse | toy | Close |

**The pattern is unambiguous.** Mechanisms that re-use information the coder already has (copies, spellings, calibration, recency) are exhausted. Mechanisms that add *new conditional information* (exact relations in metadata, the transformer's own signal that the mixer discards) or *new modelling capacity* (training) are where measurable effects live.

### 1.4 What the competitor tells us

cmix-neif (95,914,051 B, −3.4% vs lexth11c) combines:
- causal *reminders* (titles, headings, links, redirects fed as prompts);
- an online word-level log-bilinear model;
- a small online LSTM;
- a recurrent bit-level correction head;
- a modified article order;
- ~1,000 bf16 epochs (≈ 400 GPU-h) (research_round8_neif_architecture_audit.md).

Every one of those ingredients maps onto a lever in §2: zero-byte memory, word-onset modelling, complementary heads, order, training. Nothing in that list adds parameter bytes at scale.

---

## 2. Theory: compute- and copy-constrained minimum description length (C²-MDL)

### 2.1 The exact optimization problem

Let a design $\pi$ fix preprocessing, model architecture, parameters, training and packaging. The prize objective is
$$
S(\pi) \;=\; \Big\lceil \tfrac{1}{8}\textstyle\sum_{t=1}^{T} -\log_2 q_\pi(x_t\mid x_{<t}) + \epsilon_{\rm AC}\Big\rceil \;+\; \sum_{a\in\mathcal A} m_a\,B_a(\pi),
$$
subject to $T^{\rm enc}(\pi)\le\tau$, $T^{\rm dec}(\pi)\le\tau$ ($\tau = 70{,}000/T_{\rm GB5}$ hours) and $M(\pi)\le M^\*$. Here $B_a$ is the stored size of asset $a$ and $m_a$ its multiplicity: 2 for weights, stub and dictionary; 1 for order. $\epsilon_{\rm AC}$ is arithmetic-coder overhead, measured at a few bytes.

Relax design choices to continuous resource allocations. The KKT conditions with multipliers $\mu_T,\mu_M\ge 0$ read
$$
\nabla S + \mu_T\nabla T + \mu_M \nabla M = 0 .
$$

**Definition (component efficiency).** For a component $c$ (a cmix model group, PPMD order or heap, transformer layer, SSE stage, expert), let $\eta_c = -\partial S/\partial T_c$ be the bytes saved per CPU-second it consumes, and $\nu_c = -\partial S/\partial M_c$ the bytes saved per byte of RAM.

**Corollary 2.1.** At an optimum, every active component satisfies $\eta_c = \mu_T$ and $\nu_c=\mu_M$. Any component with $\eta_c<\mu_T$ should shrink, and its CPU should move to a component with $\eta_c>\mu_T$.

*Proof:* direct from KKT stationarity and complementary slackness. ∎

**Data.** The classical cmix bank (excluding the PPMD prior, which the transformer consumes) adds 1.70–2.97% over the transformer (hutter_round5_report.md:94). Its CPU share is plausibly ~50%: total 196,733 s user, minus transformer ≈ 91,000 s. Its average efficiency is therefore of order $\bar\eta_{\rm cls}\approx 50$–$90$ KB/CPU-h. The marginal fxcm_v26 addition (−234 to −375 KB for +11–15% runtime) gives ≈ 30–60 KB/CPU-h. No transformer-side or expert-side efficiency was ever measured. **Experiment E5 measures $\eta_c$ for every component.** That is the single most decision-relevant missing number.

### 2.2 Proposition 1 — the parameter count is at the two-copy MDL optimum

Model the payload locally as log-linear in the number of quantized parameters $N$ at fixed training regime:
$$
P(N) = P_0 - \kappa\,\varepsilon\,P_0 \ln\frac{N}{N_0}, \qquad S(N) = P(N) + 2bN + \text{const}\quad(\text{bits}),
$$
where:
- $\varepsilon = -d\ln \mathrm{CE}_{\rm NN}/d\ln N$ is the neural parameter elasticity;
- $\kappa = d\ln P/d\ln \mathrm{CE}_{\rm NN}$ is the final-coder pass-through;
- $b$ is the coded bits per parameter.

Setting $dS/dN=0$:
$$
N^\* = \frac{\kappa\,\varepsilon\,P_0}{2b}.
$$

**Calibration.**
- $P_0 = 92{,}559{,}456\times 8 = 7.405\times10^8$ bits.
- $b = 3.786$ (measured).
- $\varepsilon = 0.0727$: round 2, $\ln(1.393/1.483)/\ln(14.9/6.3)$.
- $\kappa\in[0.8,1]$.

Hence $N^\*\in[5.7, 7.1]$ M, against the actual $N_0 = 5.87$ M int4 parameters. Equivalently, the marginal payload gain per log-unit of parameters ($\kappa\varepsilon P_0/8 \approx 5.4$–$6.7$ MB) equals the two-copy weight cost per log-unit ($2bN_0/8 = 5.56$ MB for the int4 part; 5.96 MB for the whole container).

**Interpretation.** The record holders tuned model size, implicitly or explicitly, to the MDL frontier. With $x = N^\*/N_0$, the net saving from moving to the optimum is exactly
$$
\Delta S^\* = \kappa\varepsilon P_0\big(\ln x - 1 + 1/x\big)\ \ge 0 .
$$
For $\varepsilon\in[0.06,0.09]$ (±25% around the measured value) and $\kappa\in[0.8,1]$ this is **≤ 0.6% of the payload**. Only at an extreme $\varepsilon = 0.12$ would it reach ≈ 2%, and then only with ~2× the CPU. **More parameters are not the lever.**

*Caveat:* ε is a held-out, 2-pass estimate; in the 592-epoch prize regime it may differ. Experiment E3 measures ε and κ directly with the preserved 6M and 8M (16 × 192) checkpoints on warm windows.

### 2.3 Proposition 2 — bits per parameter: the record's quantizer optimizes the wrong rate

The weight term's gradient is $\partial S/\partial b = 2N$ bits, i.e. **1.467 MB per bit/parameter**.

Two quantization regimes:
- A *fixed-rate*-optimal quantizer (Lloyd–Max / companding) equalizes level usage. Its index entropy approaches $\log_2 K$.
- An *entropy-coded* quantizer should instead be a uniform quantizer with entropy coding (ECSQ).

The record's learned 15-level codebook has index entropy 3.786 against a maximum of $\log_2 15 = 3.907$, i.e. 97% of maximum. The project's own analysis found the indices i.i.d. (cpp_infer/COMPRESSION.md). That is the fixed-rate signature, yet the FX2TFWC3 container entropy-codes the indices.

High-resolution theory (Panter–Dite for fixed rate, Gish–Pierce for ECSQ) gives distortion $D \approx c\,\sigma^2 2^{-2R}$ with:

| Weight distribution | $c$, fixed-rate optimal | $c$, ECSQ | Rate saving at equal MSE: $\tfrac12\log_2(c_{\rm FR}/c_{\rm EC})$ |
|---|---:|---:|---:|
| Gaussian | $\tfrac{\sqrt3\pi}{2}\approx 2.72$ | $\tfrac{\pi e}{6}\approx 1.42$ | **0.47 bits/weight** |
| Laplacian | $\tfrac{54}{12}=4.5$ (since $(\int p^{1/3})^3 = 54\sigma^2$) | $\tfrac{2e^2}{12}\approx 1.23$ | **0.93 bits/weight** |

At R ≈ 3.8 bits the high-rate approximations are reasonable, not exact. A saving of 0.47–0.93 bits/weight at unchanged reconstruction MSE is worth **0.69–1.36 MB** across both copies. QAT under an entropy penalty with **λ = 1** (not 30; audit M1) is the training-side realization.

**Re-optimizing N after lowering b.** From Proposition 1, $N^\*\propto 1/b$. Moving from $b_0 = 3.78$ to $b_1 = 3.0$ raises $N^\*$ by 26%. The net additional saving is
$$
\Delta S = -\kappa\varepsilon P_0\ln\tfrac{b_0}{b_1} + 2b_1\Delta N \approx -1.45\text{ MB} + 1.14\text{ MB} = -0.31\text{ MB},
$$
on top of the direct $2N_0(b_0-b_1)/8 = 1.15$ MB. This needs +26% transformer compute, which must be found elsewhere (Corollary 2.1, Proposition 4).

### 2.4 Proposition 3 — Fisher reverse water-filling for per-tensor step sizes

Let tensor $k$ have $N_k$ weights, uniform step $\Delta_k$, and per-token mean diagonal Fisher $F_k$ (natural-log units). To second order, the payload increase from quantization noise is $\frac{T}{2\ln 2}\sum_k F_k N_k \Delta_k^2/12$ bits. The rate is $\sum_k N_k(h_k-\log_2\Delta_k)$.

*Result:* minimizing rate at fixed payload increase gives
$$
\Delta_k = c/\sqrt{F_k}.
$$
Relative to a common step at equal distortion, the rate saving is
$$
\Delta R = \frac{N}{2}\log_2\frac{A}{G},\qquad A = \frac{\sum_k N_kF_k}{N},\quad G = \exp\Big(\frac{\sum_k N_k\ln F_k}{N}\Big).
$$

*Proof:* Lagrangian stationarity in $\Delta_k$ gives $F_k\Delta_k^2$ constant. Substitute, equate distortions ($c^2=\Delta^2A$), and difference the rates. ∎

For a log-normal Fisher spread with $\sigma_{\ln F}=1$, $A/G = e^{1/2}$ and $\Delta R\approx 0.36$ bits/weight, i.e. **≈0.5 MB** across both copies. Per-row BF16 scales already capture part of the within-tensor component, so expect **0.2–0.8 MB**. The diagonal Fisher costs one GPU pass.

### 2.5 Proposition 4 — information-weighted compute allocation

Model the per-position reducible loss as $\ell_t(c_t) = \ell_t^\infty + a_t c_t^{-\alpha}$, with $a_t\propto$ the decoder-visible expected entropy $H_t$ and total compute $\sum_t c_t = C$ fixed.

*Result:* the optimal allocation is $c_t\propto a_t^{1/(1+\alpha)}$, and the reducible loss shrinks by the factor
$$
R(\alpha) = \frac{M_{1/(1+\alpha)}(a)}{M_1(a)}\le 1,
$$
where $M_p$ is the power mean. *Proof:* Lagrangian stationarity, substitution, and the identity $1-\alpha/(1+\alpha) = 1/(1+\alpha)$. The inequality is the power-mean inequality. ∎

**Measured on the native traces (64M coded bits):**

| α | 0.1 | 0.2 | 0.3 | 0.5 | 1.0 |
|---|---:|---:|---:|---:|---:|
| R(α) | 0.932 | 0.874 | 0.822 | 0.738 | 0.596 |

Let $\rho$ be the compute-reducible fraction of the loss. Under the scaling model $L = L_\infty + A C^{-\alpha}$ we have $\varepsilon = \alpha\rho$, so the relative gain at fixed compute is
$$
G_{\rm alloc} = \rho\,(1-R(\alpha)) = \varepsilon\,\frac{1-R(\alpha)}{\alpha} \in \{4.96\%, 4.64\%, 4.33\%, 3.83\%\}\ \text{for}\ \alpha\in\{0.1,0.2,0.3,0.5\}.
$$
The estimate is **robust to the unknown α** (3.8–5.0%) because $1-R(\alpha)$ is close to proportional to α. It corresponds to the gain of ≈ 1.7× uniform compute ($e^{0.04/0.073}$).

Two discounts apply:
- recurrence (weight sharing) is less efficient per FLOP than distinct parameters; take an efficiency $\phi\in[0.3,0.7]$;
- a causal gate realizes only part of the ideal allocation.

**Realistic estimate: 1.2–3.5% of payload, at zero added parameter bytes and equal CPU.** This is the theoretical case for the two-timescale architecture of §3. Recurrent (KDA) layers cannot simply skip tokens, because their state must ingest every token. The allocation must therefore be implemented *architecturally*: a light per-token stream plus a deep stream that runs at decision points.

### 2.6 Proposition 5 — the mixture-optimal training gradient (complementarity)

Let the final logit be $z=\sum_i w_i(c)\,s_i$, with stretched inputs $s_i$. This is cmix's gated linear mixing; SSE is ignored here and can be added as a monotone map. For the final loss $\ell = -\log\sigma(\pm z)$,
$$
\frac{\partial \ell}{\partial s_{\rm NN}} = w_{\rm NN}(c)\,\big(q_{\rm final}-y\big),
\qquad\text{whereas standalone training uses}\quad (p_{\rm NN}-y).
$$

So the CE-optimal transformer is not the ensemble-optimal one. The ensemble-optimal gradient is (i) *weighted by the mixer's trust* in context $c$, and (ii) *evaluated at the ensemble's error*. Where the classical bank is already right, it vanishes. That is boosting.

**Evidence that the current system is far from ensemble-optimal.** The frozen wider law moves the final log-odds by $\approx 0.198\,(\ell_{\rm NN}-\ell_{\rm final})$ and saves 0.06–0.17% on cold slices. The final mixer and SSE chain discard part of the transformer's evidence.

Two complementary actions:
1. *Inference side:* a post-SSE NN-aware mixer (E4).
2. *Training side:* train the transformer through a frozen, per-context replica of the mixer on recorded classical logits (E7).

**Estimate: 0.3–1.5%.**

### 2.7 Proposition 6 — the value of zero-byte (decoder-side) information

Let $M_t = f(x_{<t})$ be any decoder-computable memory and $Z_t$ the baseline's finite internal state.

*Result:* the improvement in expected log-loss of the best $(Z_t,M_t)$-measurable predictor over the best $Z_t$-measurable predictor is exactly
$$
\Delta L^\* = H(X_t\mid Z_t) - H(X_t\mid Z_t,M_t) = I\big(X_t; M_t \mid Z_t\big) \;\ge 0,
$$
with no archive cost. Since $M_t$ is a function of $x_{<t}$, $I(X_t;M_t\mid x_{<t}) = 0$. A gain exists only because $Z_t$ is a lossy summary of $x_{<t}$. The realized gain is at most $\Delta L^\*$ minus the approximation error of the learned read-out.

*Proof:* chain rule for mutual information and the data-processing inequality. ∎

**Where $\Delta L^\*$ can be large.** Positions whose predictive information lies in *other articles* that the 1,024-token window and the KDA state have long forgotten.

- 37–43% of bits are first-in-article mentions of words seen earlier (outcome-conditioned, so an upper envelope, not a budget).
- In the toy setting, cross-article kNN added −1.8% on top of a cache (round 4: 1.2493 → 1.2265).
- The competitor's reminder prompts (titles, links, headings) are a working instance.

**The link graph is the key structure.** `[[B]]` inside article A is a decoder-visible pointer to an already-decoded article B in the sorted order, available at zero bytes. B's summary is exactly the kind of $M_t$ that $Z_t$ lacks.

**Estimate: 1–3%** with a trained read-out. It costs RAM: 243,425 summaries × 64 B ≈ 15.6 MB, more than the 615 KB margin, so it must be traded against the PPMD heap via measured $\nu_c$ (E5).

### 2.8 Proposition 7 — article order as an asymmetric TSP on conditional description length

The decompressor restores page-id order, so *any* permutation costs only the fixed ≈ 200 KB order file already paid in S1. The exact objective is
$$
\min_\pi \sum_i L\big(a_{\pi(i)}\mid a_{\pi(1)},\dots,a_{\pi(i-1)}\big).
$$
This is intractable. Its first-order surrogate, under the assumption of a bounded effective memory of the adaptive models, is
$$
\max_\pi \sum_i \mathrm{sim}\big(a_{\pi(i)}, a_{\pi(i-1)}\big)
$$
with sim = estimated conditional saving (shared rare-word mass, link adjacency, template identity). That is a maximum-weight Hamiltonian path; greedy plus 2-opt reaches within a few percent of optimal on such graphs.

Evidence: both cmix-lex and cmix-neif gained from reordering. Slice A's window costs (0.51–1.00 bits/byte, trending upward) show the current order has strongly non-stationary difficulty. **Estimate: 0.2–1%**, CPU-only to evaluate.

### 2.9 Proposition 8 — 20% is infeasible by scaling

A 21.42% payload reduction requires $\ln(N'/N) = -\ln(0.7858)/(\kappa\varepsilon) = 0.241/0.068 \approx 3.5$, i.e. $N' \approx 35N$: ~205 M parameters, ≈ 100 MB of weights *per copy*, and ~35× the CPU. Beating cmix-neif by 20% needs a 24.4% payload reduction (payload ≤ 69,976,946 B; research_round8_competitor_update.md), and the factor becomes $e^{0.280/0.068}\approx 63\times$. Both are infeasible by one to two orders of magnitude.

*Consequence:* any credible 20% plan must obtain ≳ 15% from zero-byte levers (Propositions 4–7) and architectural efficiency. Historical precedent: LSTM → transformer was 7.5% (cmix-obias 108.5 → fx2-cmix-T 100.4 MB). That requires two to three generational architecture gains. ∎

### 2.10 Combination calculus

Individually measured gains are not additive. For components $j$ with standalone gains $G_j$, the joint gain is
$$
G(A) = \sum_{j\in A}G_j - \sum_{j<k}\mathrm{Red}_{jk} + \cdots,
$$
where the redundancy $\mathrm{Red}_{jk}\ge 0$ is the information two components share. Round 8 measured it: relation arms lost their value after generic calibration, and round 5 measured −0.63% NN loss → −0.02% final.

Use a $2^{k-p}$ fractional factorial over warm windows to estimate main effects and pairwise redundancy, and report Shapley-value attributions. Mechanisms that act on *different information* combine near-additively:
- weights (bytes),
- allocation (compute),
- memory (cross-article information),
- order (data arrangement),
- tail experts (metadata).

Mechanisms that all re-weight the same transformer evidence combine sub-additively: post-SSE mixer, complementarity training, calibration.

### 2.11 The frontier estimate

| Lever | Mechanism | Evidence | Low | Central | High | Main cost |
|---|---|---|---:|---:|---:|---|
| ECSQ weights + λ = 1 QAT | Prop. 2 | i.i.d. near-uniform indices; high-rate theory | 0.5% | 0.9% | 1.4% | 20–60 GPU-h |
| Fisher mixed precision | Prop. 3 | heterogeneity (to measure) | 0.1% | 0.4% | 0.8% | 2 GPU-h + QAT |
| N re-optimization after ECSQ | Props. 1–2 | MDL optimum shift | 0 | 0.3% | 0.6% | +26% NN compute |
| Two-timescale compute allocation | Prop. 4 | measured R(α) | 0.8% | 2.0% | 3.5% | new architecture, ≥ 200 GPU-h |
| Zero-byte cross-article memory | Prop. 6 | competitor; round-4 kNN | 0.5% | 1.5% | 3.0% | training + RAM trade |
| Complementarity + post-SSE mixer | Prop. 5 | wider/adaptive law | 0.2% | 0.6% | 1.5% | traces + GPU |
| Article order | Prop. 7 | lex/neif reorders | 0.1% | 0.4% | 1.0% | CPU |
| Structural experts on lexical pipeline | measured | −274,829 B (FX2, cold) | 0.1% | 0.25% | 0.4% | CPU, small code |
| **Undiscounted sum of the rows above** | | | 2.3% | 6.35% | 12.2% | |
| **Combined** (sub-additivity discount 0.7–0.85, §2.10) | | | **≈ 2%** | **≈ 4.5–6%** | **≈ 9–12%** | |

Two items are *enablers*, not savings against lexth11c, and are excluded from the sum:
- *classical-bank pruning* (Corollary 2.1) frees the CPU that the allocation and N re-optimization levers consume;
- *export/BF16/order hygiene* (audit L3) avoids a 113–172 KB two-copy loss on any retrained model.

Resulting S: central ≈ 93.4–94.8 MB, optimistic ≈ 87–90 MB. Both lie below the 1% threshold (99.42 MB) and the reported cmix-neif total (95.9 MB). Both are far from the 20% line (79.45 MB).

---

## 3. Architecture blueprint: TIDE-Z (Two-timescale Information-Directed Encoder with Zero-byte memory)

### 3.1 Design principles derived from the theory

1. **Same parameter bytes** (Proposition 1): stay near $N^\*$, but make each byte cheaper (Propositions 2–3).
2. **Same CPU, re-allocated** (Proposition 4 and Corollary 2.1): spend depth where entropy is, i.e. at word onsets.
3. **New information at zero bytes** (Proposition 6): link and title memory, structural relations.
4. **Ensemble-consistent objective** (Proposition 5).

### 3.2 Components

```
                          WRT token stream (205-symbol alphabet) + PPMD order-25 prior (kept)
                                                   |
            +--------------------------------------+---------------------------------------+
            |  LOCAL STREAM (every token)                                                   |
            |  6 x KDA/SWA blocks, d=192, int8 activations, ECSQ weights                    |
            |  output: per-token state u_t, local logits                                    |
            +--------------------------------------+---------------------------------------+
                                                   | decision points D: prev byte in {space, case-ctrl}
                                                   | = 29% of tokens, 52% of bits (measured); optional
                                                   v extension: newline, '[', '|', '(' (raises cost)
            +------------------------------------------------------------------------------+
            |  GLOBAL WORD-ONSET STREAM (only at t in D)                                    |
            |  3 unique blocks, d=256, looped 2x (6 effective), weight-tied                  |
            |  input: pooled u over the last segment + segment embedding                    |
            |  cross-attention -> MEMORY (k <= 8 entries)                                   |
            |  output: onset logits over code_first/literal/case; state broadcast to local  |
            +-----------------------------+------------------------------------------------+
                                          |
     +------------------------------------+-------------------------------------+
     | ZERO-BYTE MEMORY (decoder-built)                                          |
     |  (a) article summary bank: for each completed article, 64-B int8 vector  |
     |      = mean-pooled global states over its first 512 tokens + title hash  |
     |  (b) keys: completed [[link]] targets, title words, current heading      |
     |  (c) current-article entity cache: last 64 completed content words       |
     |  insertion strictly after the article/word completes                     |
     +-------------------------------------------------------------------------+
                                          |
     final: cmix bank (pruned by measured eta_c) -> SSE -> POST-SSE NN-AWARE MIXER
            inputs {l_final, l_NN, l_preSSE, 12 first-stage outputs}; contexts:
            bitpos x NN-confidence x prev-byte class; identity-initialised
```

### 3.3 Budgets (first-order)

Per-layer parameters are ≈ 0.45 M at d = 192 (QKV/O 4d² plus MLP 2·d·4d plus gates) and ≈ 0.79 M at d = 256.

| Quantity | Current (12 × 192) | TIDE-Z |
|---|---:|---:|
| Quantized parameters | ≈ 5.4 M (+ tables) | local 6 × 0.45 = 2.7 M + global 3 × 0.79 = 2.4 M ⇒ **5.1 M** |
| Weight bytes per copy at 3.78 / 3.0 bits | 2.98 MB / — | 2.6 MB / **2.1 MB** |
| MACs per token, average | 12 × 0.45 M = 5.4 M | 2.7 M + 0.29 × 6 × 0.79 M = **4.07 M (75%)** |
| Effective depth at decision points | 12 | **12** (6 local + 6 global; global layers 1.33× wider, 1.78× the MACs) |
| Effective depth elsewhere | 12 | 6 |
| Extra RAM | — | summary bank ≈ 15.6 MB + caches ≈ 1 MB (trade against PPMD heap) |

The 25% compute saving funds the memory read-outs and part of the N re-optimization. The training cost to reach parity with the 592-epoch recipe is large (≈ 200–400 GPU-h). It is therefore Tier 3, gated on the small-scale pilot E8.

### 3.4 Training recipe (when funded)

1. Data: canonical lexical stream, whole 2¹⁷ pieces, PPMD priors generated in true coding order (as the project specifies), and decision-point masks computed causally.
2. Objective:
   $$\mathcal L = \sum_t \mathrm{CE}_t \;+\; \beta\sum_t w_{\rm NN}(c_t)\,\mathrm{BCE}\big(\sigma(z^{\rm mix}_t),y_t\big) \;+\; \tfrac{2\lambda}{T}R_{\rm ECSQ}(\theta),$$
   with λ = 1, β ramped from 0 to ≈ 0.3 after 50% of training, and $R_{\rm ECSQ}$ the differentiable entropy of the uniform-quantizer indices (soft histogram, stop-gradient probabilities).
3. Quantization: uniform step per tensor or row with $\Delta_k\propto F_k^{-1/2}$ (Proposition 3); free floats trained on a BF16 grid with a straight-through estimator (audit L3).
4. Memory: train with the summary bank built causally from earlier pieces in coding order; empty-memory and shuffled-memory arms as controls.
5. Export: original tensor order; zero-update identity test; native aggregate-CE gate (E2).

---

## 4. The experimental program (ranked by value of information per dollar)

### 4.0 Common statistical and economic protocol (applies to every experiment)

- **Warm windows.** Evaluate on ≥ 16 windows of ≥ 512 KiB taken from a *warm* full-stream run, stratified by position (early/mid/late) and region (main text, tables, metadata).
  - The project's own cross-slice variation (wider-law replay gains 59.8–119.5 B per 512 KiB) gives CV ≈ 0.37, so 16 windows yield a relative standard error of ≈ 9% on the full-file extrapolation.
  - Use a block bootstrap (window = block) for 95% CIs.
- **Pre-registration and one-shot confirmation.** Freeze each family's configuration on 8 development windows. Confirm once on 8 untouched windows. Apply Holm correction across families.
- **Decision rule** (replaces the 64-byte gate; audit M2):
  $$\text{promote} \iff \mathrm{LCB}_{95}\big(\hat g\big)\cdot\tfrac{T}{W} \;-\; \sum_a m_a\Delta B_a \;-\; \hat\mu_T\,\Delta T \;>\; 0,$$
  where $\hat g$ is the per-window saving rate, $W$ the window length, and $\hat\mu_T$ the measured shadow price of time (E5; provisional 50 KB/CPU-h).
- **Production measurement.** CPU deltas come from production-flag builds (PGO/LTO, the deployed ISA), pinned to an isolated core, as the median of 3 runs, reported as ns/bit.

### Tier 0 — enablers (do first; ≤ $20 total; ≈ 1 week)

**E0. Warm instrumented full baseline on a dedicated CPU instance.**
- *Why:* fixes audit findings D1, D2, D7, S2 and §6-E1 (platform). Without it no full-file claim is possible.
- *Method:*
  1. Rent one 2-vCPU, ≥ 16 GB, ≥ 150 GB disk Linux instance and record its Geekbench 5 single-core score.
  2. Build lexth11c exactly (PGO+LTO recipe in research_round7_sources).
  3. Run `comp9` once. Log per-byte cost and final Q16 p and NN bit-p for all $8T$ bits (4 B/bit ≈ 18.8 GB raw, ≈ 8 GB zstd). For 32 pre-registered windows of 2 MB also log pre-SSE p, the 12 first-stage mixer outputs and the 192-dim hidden q5 state.
  4. Instrument rdtsc per component group: PPMD, each cmix model family, mixers, SSE, transformer.
  5. Optionally `fork()` the process at each window start and keep children paused, giving warm snapshots for A/B tests.
- *Outputs:* full-file warm cost atlas; per-component CPU shares; time headroom $\tau - T^{\rm enc}$ on a known-score machine; reusable warm traces.
- *Cost:* ≈ 60–70 h of one instance, of order $5–15 (verify live prices). Then decode once for qualification.

**E1. Export repair and re-pricing of trained cores.**
1. Round the 28,281 free floats to BF16 (or freeze them).
2. Export in the original tensor order.
3. Re-run the existing native 64 KiB codec checks for the round-9 candidates.

*Prediction:* the per-copy delta falls from 56,548 B to ≲ 5 KB with unchanged probabilities up to BF16 rounding. *Decision:* if confirmed, retract the "0.0023 bits/byte break-even" and reopen continuation training. *Cost:* < 1 h.

**E2. Distribution-level parity gate.**
Replace per-row thresholds with:
1. aggregate native vs GPU CE on ≥ 4M warm tokens within ±0.02%;
2. paired per-article CE differences with |t| < 2;
3. identical ranking of ≥ 3 trained checkpoints under GPU and native evaluation.

Run it on the existing T4 harness. *Decision:* if the gate passes, the GPU path is certified for *training*; native evaluation remains the *selection* criterion. *Cost:* hours.

**E3. Elasticity calibration (ε, κ) with preserved checkpoints.**
- Export 6M (12 × 192) and 8M (16 × 192; native build `TF_NL=16`) FX2-era checkpoints. Run the FX2 reference pipeline on the 16 E0 warm windows.
- Measure $\Delta\ln\mathrm{CE}_{\rm NN}$ and $\Delta\ln P_{\rm final}$, which gives ε and κ (Proposition 1). Also measure transformer CPU.
- *Decision:* if $\kappa\varepsilon P_0/(2bN_0)>1.3$, the model is below the MDL optimum and N re-optimization moves up the priority list; if < 0.8, consider a smaller N with ECSQ.
- *Cost:* CPU-hours.

### Tier 1 — CPU-only, high expected value per dollar

**E4. Post-SSE NN-aware online mixer** (generalizes the round-9 adaptive law).
- *Model:* $z = \sum_i w_{i,c}\,s_i$ with $s\in\{\ell_{\rm final},\ell_{\rm NN},\ell_{\rm preSSE},\ell^{(1..12)}_{\rm mix}, 1\}$. Weight sets indexed by $c$ = bit position × NN-confidence bucket (8) × previous-byte class (10). Online gradient with lr schedule $\eta_n = \eta_0/\sqrt{n_c}$. Initialized to the identity on $\ell_{\rm final}$. Output Q16 via integer stretch/squash tables (audit P2).
- *Controls:* identity; the frozen adaptive law; the same mixer with $\ell_{\rm NN}$ removed (to isolate the NN contribution); the same mixer with shuffled contexts.
- *Evaluation:* warm-window replay from E0 traces. Native integration and decode only if the decision rule passes.
- *Expected:* 0.1–0.3% (90–280 KB) if the cold-slice signal survives warm. Decisive either way about the "NN under-weighted" diagnosis. CPU ≈ 20–60 ns/bit ⇒ 0.03–0.08 h.

**E5. Component efficiency audit $\eta_c$ and pruning.**
- *Method:* from the E0 fork snapshots, run each of ≈ 15 component-group ablations (each cmix model family; PPMD order 25/16/12 and heap 3.5/3.0/2.5 GB; SSE stages; the fxcm text model) on 8 warm windows. Record ΔS rate and ΔCPU (ns/bit) and compute $\eta_c$ and $\nu_c$.
- *Output:* a ranked efficiency table; a pruned bank freeing ≥ 20% CPU at < 0.2% payload loss (the hypothesis implied by the 1.7–3% classical contribution); a measured shadow price $\hat\mu_T$.
- *Why critical:* every later candidate needs CPU headroom that does not exist today. *Cost:* CPU-days.

**E10. Article-order optimization.**
- *Method:*
  1. Build an article graph: MinHash (k = 128) of rare-word sets plus link adjacency plus template identity. Edge weight = predicted conditional saving, calibrated on 2,000 article pairs coded with a fast proxy coder (e.g., PPMd-I order 8 primed on article $i$, coding article $j$).
  2. Solve max-weight Hamiltonian path by greedy + 2-opt.
  3. Evaluate the full stream with the proxy, then natively via the E0 infrastructure.
- *Order-file cost:* re-measure; the current file is 199,980 B.
- *Expected:* 0.1–1%. *Cost:* CPU only.

**E11. Structural experts on the lexical pipeline (warm).**
Port the round-6 timestamp, contributor, username and interwiki experts. Re-measure against lexth11c's own revision-tail transform, which already pays ≈ 347 KB of side data, and against warm state. Extend to infobox fields keyed by template name and parameter, with an exact-copy-or-escape expert, only where E0's warm atlas shows field bits ≥ 200 KB. *Expected:* 0.1–0.3%.

**E12. High-confidence precision.**
The reliability analysis shows underconfidence in the 0.999–0.9999 bin (accuracy 0.99988 vs confidence 0.99973), worth ~63–72 B per 2M slice in-sample. Test widening the final probability range (32-bit coder probability, adjusted final clamp) on warm windows. *Expected:* ≈ 15–25 KB full-file (in-sample estimate scaled by T; the warm rate may differ). *Cost:* small.

### Tier 2 — GPU, within or slightly above the $70 cap

**E6. Stable continuation, then ECSQ with λ = 1 and Fisher allocation.**
1. *Continuation protocol:*
   - Adam with zero moments and a 1,000-step linear warmup from 0 to 3e-6;
   - ≥ 64 whole pieces per step with loss on all positions;
   - token-weighted sampling over the full canonical stream;
   - BF16-STE floats;
   - λ = 0 control. Gate: full-stream CE drift ≤ +0.02% after 2,000 steps.
2. *Fisher:* one pass of squared gradients for per-tensor $F_k$.
3. *Arms:*
   - (i) current codebook, λ ∈ {0.5, 1, 2};
   - (ii) uniform ECSQ step, $\Delta_k\propto F_k^{-1/2}$, λ ∈ {0.5, 1, 2};
   - (iii) (ii) at N re-optimized by +26% if E3 supports it.
4. *Metrics:* exported container bytes (real codec), native warm-window payload, Pareto slope versus −2 bits per bit.
- *Expected:* 0.7–1.8 MB. *Cost:* 20–60 GPU-h, roughly $15–50 at assumed marketplace rates (verify).

**E7. Complementarity training.**
- Use the E0 traces: classical first-stage logits and mixer contexts on the training pieces.
- Fit a *static* per-context replica of the final mixer + SSE (logistic regression on the traces).
- Continue training the transformer on $\mathrm{CE}+\beta\cdot$ mixture-BCE (Proposition 5), β ∈ {0.1, 0.3}, from the E6 checkpoint; evaluate natively.
- *Expected:* 0.3–1%. *Cost:* 10–30 GPU-h.

### Tier 3 — architecture (beyond $70; only after Tier 0–2 succeed)

**E8. TIDE-Z small-scale pilot** (go/no-go for a full retrain).
- *Setting:* the first 100M canonical tokens, train = test (prize regime), 64 epochs.
- *Arms at matched weight bytes (±5%):*
  - (a) 12 × 192 baseline;
  - (b) TIDE-Z without memory;
  - (c) TIDE-Z + empty memory;
  - (d) TIDE-Z + shuffled memory;
  - (e) TIDE-Z + real memory.
  Measure MACs/token.
- *Go criterion:* (b) ≥ 1.5% CE better than (a) at ≤ 85% MACs, **and** (e) − (c) ≥ 0.7% with (d) ≈ (c).
- *Cost:* 50–150 GPU-h.

**E9. Full TIDE-Z training and native kernels.** Only on a passed E8. ≈ 200–400 GPU-h plus native kernel engineering, a multi-week project.

### Experiments to stop

Stop these; the evidence is sufficient and the ceiling is negligible:
- OCR, glyph and shape features;
- any-order / Wordle / skeleton factorizations;
- spelling-moment and anagram echoes;
- topic unigrams and paid topic profiles;
- sparse GloVe neighbor graphs;
- final-probability calibration;
- loss-only rarity masking;
- exact-copy field/line edit automata on main text (until E0 shows a ≥ 200 KB warm field budget);
- further "GPU layer differential" bit-exactness work (audit L1).

---

## 5. Additional ideas found in the reports' data

1. **Onset-gated depth.** 41.4% of bits follow a space and 10.4% follow a case control (29% of positions). The simplest test of Proposition 4 adds 2 extra attention+MLP passes, weight-tied to the final sliding-window layer (layer 11), so parameter bytes stay equal.
   - The passes run queries and MLP *only* at those positions.
   - Their keys and values are projections of layer-11 outputs at all positions, so no recurrent state needs every token.
   - Cost: ≈ 0.29 × 2 × 0.45 M MACs + 0.71 × 2 × (2·192²) ≈ +7% average MACs.

   Measure CE against that +7%.
2. **Cheap path for confident positions.** 34.9% of positions have $H_t<0.1$ bit and carry 0.12% of bits. On the classical side, skip *mixing* (not updating) of low-$\eta$ cmix models when the transformer and PPMD agree with confidence > 0.999. Updates must continue so the models stay in sync. Measure CPU saved against bits lost.
3. **Continuation-byte modelling.** Code continuation bytes carry 24% of bits at 2.11 bits/byte. The WRT splits one word choice into up to three decisions. A word-level head at the code-first position that predicts the full 44,515-way identity, marginalized through the code tree (the project's own exact formula), would amortize the whole decision at onset. The round-9 implementation failed only for training-budget reasons (audit L5).
4. **The neural-under-weighting diagnosis.** The fitted shift of ≈ 0.2 in log-odds toward the transformer is a measurable property of cmix's mixer/SSE. If it persists warm (E4), adjust the mixer learning rates and initial NN weight (lexth11c already scales L0/L1 learning rates by 0.6/0.25) rather than bolting on a residual.
5. **Order curriculum.** Slice A (stream start) costs 0.75 bits/byte; its 128 K-window costs range from 0.51 to 1.00 and trend upward within 2 MB. The current order front-loads easy content. Online-learning regret depends on order. Placing heterogeneous, hard articles after the adaptive models have warmed on a broad base is a testable variant of E10.
6. **BF16-grid training for every float.** Any future finetune, QAT or rate study must train free floats on the BF16 grid. Otherwise each touched float silently costs ~2 bytes per copy (audit L3).
7. **Distill a larger teacher into the 6M student.** The preserved 10M (12 × 256) checkpoint can act as a teacher for the deployed 6M at no parameter or CPU cost. Caveat: it was trained on the old FX2-ordered stream, so first verify its CE on the canonical lexical stream with lexical PPMD priors. Distillation in the train = test regime is a known way to exceed the student's own CE optimum. This is a cheap Tier-2 add-on to E6.
8. **RAM shadow price.** The 615 KB RAM margin blocks memory-based levers. PPMD's 3.5 GB heap is the largest allocation. Measure $\nu_{\rm PPMD}$ (bytes lost per MB of heap removed) in E5. If it is small, it funds the TIDE-Z summary bank.
9. **Metadata-tail completion.** Round 6 measured username costs of 37.8 bits for first appearances and 12.1 bits for "seen earlier, not near in time". A username-dictionary expert with frequency-ranked candidates from all earlier records (a decoder-built rank list) addresses the 12.1-bit class. Expected tens of KB.
10. **Fork-based paired evaluation as standard infrastructure.** Any candidate that changes only the final probability can be evaluated in parallel forked children from one warm parent, giving paired, warm and cheap measurements. This should replace cold-slice screening entirely.

---

## 6. Summary of decisions

| Decision | Basis |
|---|---|
| Do E0–E3 before anything else | They remove three Critical flaws and calibrate the theory's two unknowns (ε, κ) |
| Prioritize zero-byte levers | Proposition 1: the parameter count is at the MDL optimum |
| Treat weights as an ECSQ problem with λ = 1 | Proposition 2: up to ~1.4 MB available |
| Fund architecture only through the E8 gate | Proposition 4: worth 1.2–3.5%, but expensive to train |
| Report every result as full-file rate × T minus assets minus CPU price, with CIs | Audit M2, M6, S4 |
| Treat 20% as out of reach with known methods | Proposition 8. Central realistic frontier is ≈ 4.5–6% vs lexth11c (optimistic 9–12%), which still beats the 1% threshold and the reported pending entries |

---

## Appendix — measurements introduced in this document

All are computed from preserved local files: `research_round7_{a..d}2m.bin`, `research_round7_lex_{a..d}_2m_cost.f32` and `research_round7_lex_finalbit_{a..d}2m_p.u16`. The method is described in audit Appendix B.

- **Byte-class bit shares** (§1.2): exact inverse WRT map from `research_round7_wrt.py`, with classes assigned by a decoding state machine.
- **Expected entropy** $H_t=\sum_{k=0}^{7}h(p_{t,k})$, where $p_{t,k}$ is the native Q16 probability of the $k$-th bit given the earlier bits of byte $t$. The pooled realized mean is 1.5108 bits/byte and the expected mean 1.4991.
- **Power-mean factors** R(α), computed as $\big(\overline{a^{1/(1+\alpha)}}\big)^{1+\alpha}/\bar a$ with $a_t=\max(H_t,10^{-6})$.
- **Reliability and in-sample per-bin temperature bound**: 11 confidence bins with a 101-point log-odds multiplier grid; 111.6 / 117.7 / 121.6 / 115.5 B per 2M slice (A / B / C / D).
- **Decoder-visible gates**: $H_t$ thresholds and previous-byte class.
