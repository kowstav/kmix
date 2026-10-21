# Round 13: mathematical analysis, kept separate from measurements

7 October 2026. This file derives design constraints and testable descendants.
Observed sizes, timings and execution states belong in research_round13_report.md.
None of the equations establishes an absolute optimum, a 20% gain, or the best
possible descendant of an unrestricted idea family.

## 1. The optimization problem that actually matters

Let x be the exact original corpus, T = 587,138,826 its preserved canonical bytes,
and q the complete decoder-reproducible coding law. Minimize

    S = B_payload(q, x) + sum_j m_j B_j,
    subject to exact reconstruction, eligible CPU time and peak RAM.

The asset term includes every executable, model, dictionary, selector, layout,
literal/OOV stream and option at its actual package multiplicity. The preserved
package counts model and executable copies twice. The current measured historical
package is 99,313,750 B. A 20% reduction requires less than 79,451,000 B; with
unchanged assets this means saving about 0.27064 bits per canonical byte. Improving
one proxy channel by 20% does not imply improving this package by 20%.

For a neural model rate R in bits and mean final loss in bits per coded byte,

    J(theta) = mean_CE_final(theta) + m R(theta)/T.

Lambda = 1 expresses the actual storage exchange rate. A sum over n scored bytes
uses n*m*R/T. Natural-log losses require multiplying the bit-valued term by ln(2).
If averaging individual bit losses, both denominators use 8*T. No double
normalization or unexplained lambda = 30 is allowed. GPU NN loss remains a
diagnostic until its effect on the final native coder is measured.

Compute is a hard feasibility constraint. A fitted shadow price can rank feasible
choices; it cannot turn an over-time or over-RAM decoder into an eligible one.
The historical full decoder's 9,999,384,576 B peak leaves only 615,424 B below a
10 GB decimal ceiling. Laboratory regional RSS is not this full-file peak.

## 2. Free history, useful state and transmitted hints

Write H for complete decoded history, Z for the model's retained state and
F = f(H) for a deterministic context miner. Then

    I(X_next; F | H) = 0,

but I(X_next; F | Z) can be positive when Z has forgotten a useful distinction.
Thus lexical echo, title memory, morphology, glyph geometry, context TTL and
retrieval can improve a limited predictor without adding information to history.
They must still improve the complete normalized law enough to pay their code,
state, searches and CPU. Structural resemblance alone is not evidence of that
conditional benefit; signed/null descriptors and ordinary lexical controls are
needed. Word type coverage and token frequency coverage are different quantities.

An encoder may search using future bytes. A decoder cannot reconstruct the
search's winning future-dependent choice unless it is transmitted or obtained
from decoded state. For hints h, evaluate L(h) + L(x|h), not only L(x|h).
Reordering can validly expose future content earlier, but its order/layout stream
and the changed distribution/reset behavior must be charged and tested.

## 3. Constructors, variables and order

For literal/content channel V, layout/case G and constructor sequence C, a valid
content-first factorization is

    L = L(V,G) + L(C | V,G) + container/model costs.

The paid right literal is then available to the grammar decoder. Coarse length,
vowel, plural-s and capitalization classes deliberately pool observations, unlike
a huge sparse anchor hash. Left and deterministic wrong anchors are controls.
All probability distributions must stay positive and identically normalized in
encoder and decoder. The R13 codec implements hierarchical integer smoothing.

Let B be the constructor multiset and U its multiset-permutation rank. Because
C is recoverable from (B,U),

    H(C|V,G) = H(B|V,G) + H(U|B,V,G).

A set representation also needs multiplicities. Merely finding fewer bags/sets
than ordered patterns does not remove order or count information. Equally, a
poor uniform permutation model does not prove all bag models useless.

The full-corpus census's empirical plug-in difference H_hat(C)-H_hat(B) totals
about 1,447,957 bits. Its uniform multiset-order code costs about 17,363,273 bits.
These are descriptive, same-data quantities before pattern/model costs, not an
achieved archive or an entropy bound on the native coder. Their difference
suggests testing a conditional order model rather than declaring the bag family
closed. The next finite descendant can use

    q_t(w) proportional to 1[n_t(w)>0] * n_t(w)^beta * r(w|past, paid anchors),

with beta fixed in advance and integer-normalized positive frequencies. Decrement
the known remaining count after decoding; update r only after that observation.
Compare beta=0/1, uniform remaining counts and direct ordered coding, including
the full bag metadata channel. A learned grammar/infilling architecture is a
separate unimplemented model, not the same as this coarse CPU head.

## 4. Rarity masking and gradient interference

For a weighted loss E[w(Y,H)*(-log q(Y|H))], the unrestricted optimum satisfies

    q_w(y|h) proportional to w(y,h) p(y|h).

At a word-level softmax, assigning zero weight to rare-word outcomes can drive
their optimum probability to zero even though the full corpus still contains
them. This is a changed objective, not a free compression saving.

The existing core predicts WRT bytes, however. Masking all byte losses inside
rare-word spans does NOT automatically imply q(rare_word)=0 or zero probability
for every byte used by those words. Bytes are shared with common words. Its
optimum instead uses E[w|byte=b,H=h]*p(b|h). This distinction limits the simple
masking theorem; it must not be used to reject every masked-byte descendant.

Rare-target gradients can interfere with common-target gradients in a finite
network. Measure their dot products, norms and common/rare/full final codelength
changes. A negative dot product at one checkpoint is not proof of persistent
harm, nor a reason to omit literal recovery costs. Test rates before masking,
equal-target training controls, nonzero rare floors, KL anchoring and typed
common/rare specialists. If input is redacted, generate the priors and states for
that redacted input; original full-input priors would leak information.

A valid typed codec pays the common/rare type law and the rare literal/OOV
channel, or mixes fully normalized experts with a prefix-visible gate. Neither
the current target's rarity label nor its original spelling is a free decoder
feature. Full literal/OOV masking and original-core continuation are still GPU
work, not completed by the CPU constructor proxy.

## 5. Integer residuals, memory controls and guarded combinations

The residual starts from the native Q16 probability and applies bounded integer
odds corrections. Native probabilities enter as an identity base, so an all-zero
residual is exactly neutral. Preserve all original 16 features; append eight
memory features at indices 16..23. Overwriting original predictors confounds a
memory comparison. All-neutral appended features must produce bit-identical
predictions and updates to the original-feature arm.

R13 carries four exponential horizons of two fixed hidden projections. Its
means use high-precision integer accumulators, so slow horizons continue moving.
Reset/OOV rows have no stale activation and advance the byte decay clock. The
short-reset and zero-memory arms are required controls. These tiny fixed
projections do not test learned TTL, attention, kNN or an optimal eviction policy.

For an ideal exact Bayesian/fixed-share mixture of K positive experts, prior
1/K and switch probability epsilon, a path with s switches obeys the codelength
bound

    L_mix <= L_path + log2(K)
             + (n-1-s)*log2(1/(1-epsilon)) + s*log2(K/epsilon).

This follows by lower-bounding that path's probability in the mixture. It is not
automatically the bound of the implemented Q32 posterior/Q16 probability codec:
posterior floors, fixed-share rounding and output rounding add terms. R13's
integer guard therefore makes no unqualified worst-case identity-regret claim.
It must be measured against actual native archives. Learning an SGD residual by
itself also has no universal no-harm guarantee.

A stronger alternative is a paid block selector: maintain all shadow expert
states from decoded bytes, encode each block under the registered alternatives,
and store the chosen block law plus framing. For the registered block coders its
size is the sum of their actual minimum block sizes plus actual selection/frame
costs. This is a valid encoder search, not a free future hint. It still pays
all required decoder code/state, and reset arithmetic blocks must be compared
against a baseline with identical boundaries. This descendant is not implemented
or claimed to beat the preserved whole-stream native coder.

## 6. Native integration and resource engineering

The pinned arithmetic coder uses uint(1 + 65534*p_float). A candidate integer
probability must enter both coders directly; converting it to p=q/65536 and then
applying the old float discretizer changes the law. R13 adds a common PredictQ16
interface to both encoder and decoder, including their known-bit observer paths.
The neutral mode retains the original discretization. Native mixers keep their
own cached predictions for updates; the final residual does not silently feed
back as a replacement training probability.

Source changes, compiler flags, probability tables and exact weights are frozen.
Neutral probability trajectories and archive hashes must match the pinned coder
before attributing a gain to the residual. Every candidate must independently
decode. Laboratory recompilation without the original PGO is not a production
time or executable-size qualification. CPU threading flags alone cannot make a
sequential bit coder parallel: independent experiments/regions use four process
lanes, while a genuine whole-file history remains sequential unless a verified
parallel formulation preserves that history.

## 7. What a negative experiment can establish

No finite sweep proves that every future descendant of an unrestricted idea
cannot work. Stop a declared configuration at its finite endpoint; record the
data/reset regime, controls, effect size and unresolved mechanism. Reopen with a
material change and newly registered controls. Do not call a nonsignificant
zero-difference test equivalence. Adjacent windows sharing history are one
dependence cluster. R13 has eight confirmation regions, below the bootstrap
implementation's ten-cluster minimum, and deterministically spaced regions do
not alone justify a population confidence interval.

Combinations also need actual testing: G_AB-G_A-G_B may be positive or negative.
Neither submodularity nor redundancy is guaranteed. Fit/select on development,
freeze the choice, and then open confirmation. Do not add separate proxy gains
into an alleged package improvement or relabel a cold/regional state as the
full-file global state.
