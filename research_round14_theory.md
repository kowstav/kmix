# Round 14: deductions and testable combinations

9 October 2026. Measurements belong in research_round14_report.md. This document
does not claim an absolute optimum or a predicted training improvement.

## 1. Optimize the actual package under hard constraints

For exact corpus x and reproducible law q, minimize

    S = B_actual_archive(q,x) + sum_a m_a B_a

subject to exact reconstruction and the prize's eligible encoder time, decoder
time and peak memory. Model/code/dictionary multiplicities are not optional.
The preserved historical 99,313,750 B package has 92,559,456 payload bytes and
6,754,294 asset bytes. A 20% target is 79,451,000 B; unchanged assets require
19,862,750 fewer payload bytes, about 0.27064 bits per canonical byte. Four GB
of RAM saved by pruning does not itself reduce that archive.

For a small controlled change, report a vector

    d = (Delta payload, Delta code/model bytes, Delta encode CPU,
         Delta decode CPU, Delta peak RAM).

Pareto dominance is meaningful without an assumed exchange rate. A pruned design
may be useful despite worse compression if the freed resource enables a tested
combination. It is not a compression improvement until that combination actually
reduces S and satisfies every constraint. Regional RSS cannot qualify full-run
RSS; the historical full decoder had only about 0.6 MB below the decimal 10 GB
limit. KKT stationarity in a smooth local relaxation is not a global theorem for
the discrete, nonconvex architecture search.

## 2. The right-context result motivates a better factorization

Let V be content/literals, G exact layout and C grammar tokens. A reversible
content-first law costs L(V,G)+L(C|V,G). Paying V first makes its right anchors
available, so conditioning on them is causally valid in this decoding order.
The complete cost nevertheless includes the altered content distribution and
all G channels. A conditional grammar improvement cannot simply be subtracted
from the original left-to-right native archive while retaining its old costs.

For a bag B and within-bag ordering U,

    H(C|V,G) = H(B|V,G) + H(U|B,V,G).

Round 14 implements the descendant

    q_t(w) = [1[n_t(w)>0] n_t(w)^beta r_t(w|context)] / Z_t,

where the bag counts are paid and r_t updates only after observing w. Positive
integer frequencies are bounded before arithmetic coding; the known remaining
count decreases only after decoding. Beta=0/1 and smoothing alpha=1/4 have been
tested. Their negative complete-code result is evidence about those finite
models. It does not bound the capacity of a learned infiller.

A stronger next descendant avoids paying a separate multiset per very short run:
use the direct constructor distribution, with a prefix-visible latent syntax
state and a small conditional correction. Alternatively encode only a shared
template identifier plus exact edits when that *entire* branch beats the direct
branch. The branch identifier must be paid. A frame-wise encoder search permits
future-aware choice, but selector, length, reset and template bytes must all be
included. Freeze template construction on development or store its corpus-derived
table; do not treat target-derived grammar as free.

The clean comparison is a four-cell design: direct vs template branch, crossed
with right-anchor vs matched wrong-anchor contexts. Define interaction

    I = G_joint - G_template - G_right.

Its sign is unrestricted. Positive synergy is possible; no generic redundancy
discount or sum-of-gains forecast is justified. This architecture remains a
proposal, not a result of the count-model tests.

## 3. Hard-word masking is a gradient-allocation hypothesis

Native word costs localize expenditure; they do not identify its reducible part.
Use common/rare labels only for training diagnostics or a paid/reproducible type
law. For weighted byte loss, the unrestricted conditional optimum is

    q_w(b|h) proportional to p(b|h) E[w(Y,h) | B=b,H=h].

The alphabet is WRT bytes shared across words. Therefore zero word-span weight
does not generally force all rare-word byte probabilities to zero. At the same
time, optimizing only common targets does not make rare residuals disappear.
The full all-target code remains the acceptance metric.

Measure g_common and g_rare on the same checkpoint and batch with a fixed global
loss normalization. If g_common dot g_rare < 0, the two local descent directions
conflict in Euclidean geometry. Adam's actual preconditioned update is different:
measure g_common^T Delta_theta_rare, not only the raw-gradient cosine. A local
conflict is not evidence of persistent damage or a reason to mask all rare words.

The next finite GPU design crosses rare floor {1,0.5,0.1}, fixed thresholds
{107,1392}, and KL anchoring to the initial model, with equal useful targets and
paired seeds. Use successive halving rather than fully train every crossing.
Compare all-target native bits, common/rare bits, model bytes and stability.
Thresholds derive from the preserved census but their frequency table is a
training asset only; any runtime table must be included in the package.

A typed common/rare specialist must emit a normalized joint law:

    q(w|h) = q(type(w)|h) q(w|type(w),h),

including literal/OOV spelling, exact case and delimiters. An alternative is a
mixture of full-support experts. The decoder may not choose the expert using
the not-yet-decoded word's rarity label. This is the precise route from masking
to a deployable descendant; it requires original-core training and a native
inference path, which the CPU attribution experiment does not implement.

## 4. Probability precision: evaluate the complete feedback path

For a fixed history and target law p, rounding to q changes expected code by
KL(p||q)/ln(2) relative to ideal p. The native coder, however, feeds a learned
mixture and SSE. Changing a neural probability can change later mixer updates;
the total change is not the sum of independent one-row rounding penalties.

The registered precision arm preserves the trained PPMd half prior and every
transformer state update, while retaining float32 output instead of the final
half round trip. It preserves the old floor. This isolates a downstream
probability change from a changed neural prior. Exact independent decoding and
whole native costs, not a softmax-MSE proxy, determine its value. High arithmetic
precision, floor optimization and the existing half-tail subnormal quirk are
different interventions and remain separately untested by this arm.

## 5. Why exact grouped storage has a finite optimum, but not a global one

For a fixed disjoint tensor partition, fixed outer metadata and independently
framed alternatives a in A_g per group,

    B = B_outer + sum_g [B_frame,g + B_g(a_g)].

Consequently min B equals B_outer + sum_g[B_frame,g + min_a B_g(a)]. The exhaustive
18-choice-per-group selection is globally minimal for that finite separable
problem, without enumerating 18^433 combinations. This proof ceases to apply if
groups share entropy state, dictionaries, a learned predictor or changing outer
metadata. The original native codec remains smaller than all tested partitions.

Entropy-constrained retraining optimizes a different objective:

    J = mean_final_bits_per_byte + m R_weights_bits / T.

Use lambda=1 for actual package pricing; lambda in {0,0.5,1,2} maps a measured
rate/distortion frontier. If the loss is a sum over n sampled targets, multiply
the rate term by n. Natural-log losses require consistent ln(2) conversion.
High-rate quantization constants are asymptotic comparisons, not a promised
0.7–1.4 MB saving for the current learned codebook. Near-uniform index occupancy
does not prove the quantizer was optimized for the wrong objective.

## 6. Resource-conditioned combinations worth testing

The strongest practical combination program is staged:

1. Measure native component removals to identify a real CPU/RAM budget.
2. Test the final-output precision change and guard alone, then together.
3. Spend measured headroom on one candidate: longer useful context, a bounded
   learned word/TTL controller, or a stronger complementary output head.
4. Train that architecture on carried-state episodes and actual warm priors;
   verify export parity and complete native behavior before larger training.
5. Compare the *combined* complete package and resources with the unmodified
   baseline on confirmation, then the entire corpus with global state.

Memory F=f(history) adds no information conditional on complete history, but may
add information conditional on the finite model state Z. Thus causally mined
context can help despite being deterministic. Zero conditional mutual information
given full history is not a proof that glyph, morphology, retrieval or TTL can
never help a limited architecture. Conversely similarity of two words alone
does not show a measurable conditional gain.

The high-cost full-history native run remains a separate infrastructure task:
roughly 55–60 historical production hours cannot fit into one 12-hour Kaggle
commit. Parallelizing independent reset regions changes the problem. A persistent
eligible CPU host or validated complete state serialization is needed; neither
is silently charged to the user's $70 without a concrete plan and price.

## 7. Evidence rules for the shortlist

Keep a finite tested version, the original family and its unimplemented
descendants distinct. A noisy null result is not equivalence, and a finite
negative result cannot prove all future descendants impossible. Report exact
controls, data, paid channels, resets, capacity and resources. Do not invent
thinking hours, global optima, full-model parity from a tensor-shape check, or
research maturity from the number of cells in an ideas ledger.
