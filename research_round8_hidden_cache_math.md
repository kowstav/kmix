# Causal native cache: equations, engineering and decision contract

This is the formal companion to `research_round8_hidden_cache_protocol.md`.
The original C3 neural weights and its classical mixer update trajectory stay
fixed. Statistical fitting of a few residual coefficients is separately priced.

## State and information available to the decoder

Let the coded byte sequence be x_0,...,x_(n-1). After processing byte i the native
transformer emits its existing final quantized activation h_(i+1) in {0,...,255}^192.
This represents the context available before x_(i+1). A piece reset emits an
invalid flag instead. h_0 is invalid. The key is k_i=h_i-128, not h_(i+1).

Before byte t the cache contains pairs (k_i,x_i) only for i<t. After predicting
all eight bits of x_t, insert (k_t,x_t) if valid, then obtain k_(t+1) from the native
trace. Consequently neither the current target nor a future prediction appears
in its own query. Decoded truth, rather than guessed words, updates the cache.
This remains true even when the encoder knows the entire document.

The observation patch reads the existing q5 array through a const getter. It
does not recompute the hidden state, quantize it differently, or feed cache
predictions back into the base models. Equality of native arithmetic archives,
final uint16 traces and independent-decoder hidden traces is a prerequisite.
Source-level plausibility alone is insufficient to establish that property.

## Similarity and projected representation

For nonzero keys use cosine

    s(k,r) = (k dot r)/(sqrt(k dot k)*sqrt(r dot r)).

Zero keys fall back to the prefix prior. Exact top-eight selection breaks ties
by physical row index. Norms are calculated once at insertion. A stored row has
a key, norm and actual subsequent byte; it is never an inferred sentence label.

The registered 32-coordinate projection uses disjoint signed sums:

    u_j = sum_(a=0)^5 sign(hash(9183+6j+a)) k_(j+32a), j=0,...,31;
    z_j = round(127 u_j / max_l |u_l|).

If all u_j are zero, z is zero. The deterministic hash is code, not an uncounted
trained matrix. This map deliberately loses information and may reduce useful
similarity; no claim of injectivity, semantic optimality or Johnson–Lindenstrauss
guarantee is made for this sparse construction.

## Normalized byte distribution and bit conditioning

Let n_t(b) be the count of byte b strictly before t. Its prefix KT prior is

    pi_t(b) = (n_t(b)+1/2)/(t+128).

For the retrieved rows J_t, define weights

    w_i = exp(10 [s(k_t,k_i) - max_(j in J_t) s(k_t,k_j)]).

Subtracting the maximum prevents overflow and leaves normalized weights
unchanged. With alpha=1/2 fixed before results,

    q_t(b) = (1-alpha) pi_t(b)
             + alpha sum_(i in J_t) w_i 1[x_i=b]/sum_(i in J_t) w_i.

Without valid neighbors use pi_t. Every byte has positive mass and sums to one.
For current prefix v of j already decoded bits, let A(v,j) contain all bytes
with that prefix. The probability of next bit 1 is exactly

    q_(t,j)(1|v) = sum_(b in A(v,j), nextbit(b)=1) q_t(b)
                  / sum_(b in A(v,j)) q_t(b).

The product of these eight conditional probabilities along each of the 256
possible byte paths equals q_t(b); the independent self-test checks all paths.
This supplies a genuine counterfactual distribution. A realized native word's
loss trace cannot be substituted for this categorical normalization.

## Retention policies and controls

FIFO128 and FIFO512 replace rows cyclically after the target completes.
Reservoir512 fills its first 512 valid pairs, then draws a reproducible
pseudorandom index modulo the number of valid pairs seen. It replaces a row if
the index is below 512. This implements an Algorithm-R-style policy. The fixed
xorshift generator and modulo reduction introduce sampling imperfections; no
perfectly uniform mathematical sampling theorem is claimed. It nevertheless
retains much older prefix pairs without shipping their locations or contents.

The matched target control permutes target labels across the same valid rows
without changing keys, query neighbors, weights or the target histogram. Thus
it tests key/target association rather than simply extra memory. Ordinary
FIFO512 byte frequencies, mixed with the same KT prior, control for recency.
Permutation tables are research-control overhead and will not accompany a
selected production cache. Cache values across piece resets remain past data;
only invalid query keys fall back. Cross-page retention is therefore legal.

## Residual fitting, finite certificates and combinations

Let p_(t,j) be the unchanged native uint16 probability divided by 65536, and
ell=logit(p). For cache arm a export

    f_a = clip(logit(q_a)-ell, -12, 12),

with zero for an invalid hidden query. The generic head uses bias and ell only.
Individual source heads use [1,ell,f_a]. The joint head uses [1,ell,f_FIFO128,
f_FIFO512,f_projection,f_recency,f_reservoir]. Define

    z = ell + theta dot X, theta in [-1,1]^d;
    F(theta) = sum_i [log(1+exp(z_i)) - y_i z_i].

The Hessian X^T diag(sigmoid(z)(1-sigmoid(z))) X is positive semidefinite.
For any fitted theta, gradient g, and box vertex v_j=-sign(g_j), convexity gives

    min_F >= F(theta) + g dot (v-theta).

The upper-minus-lower bound divided by 8 ln(2) certifies remaining ideal-loss
optimization opportunity within this fixed bounded head. It says nothing about
optimal representations, eviction, smoothing, training or architecture. Quantize
the final probability to clamp(round(65536 sigmoid(z)),1,65535); report its actual
integer savings and the difference from ideal loss. That staircase objective
is not convex, so the ideal certificate must not be relabeled an exact Q16
optimum. A/B fit only; C/D use frozen coefficients. The joint fit measures shared
and complementary effects rather than adding independently reported gains.

## What would make this useful

Raw savings are sum log2(P_candidate(actual_bit)/P_native(actual_bit))/8.
The prize score additionally pays code, both stored coefficient copies, selectors,
all dictionaries/containers, actual coder overhead, and any newly stored assets.
Decoder-built cache contents have no transmitted cost, but consume RAM and CPU.
The individual 512-key packed design is 512*(192+8+1)=102,912 bytes before
alignment, FIFO position, counters and buffers. This is a design accounting,
not measured production RAM. The current research Row uses int16 coordinates
and stores several caches plus permutation tables; report its real larger size.

The published C3 peak is 9,765,024 KiB = 9,999,384,576 bytes. Conservative decimal
10 GB therefore leaves 615,424 bytes. Native KVI8 is already selected. A new
architecture must fit the measured whole-program peak, and its lookup cost must
fit single-core runtime rules. No global retraining is needed for this pilot;
a native residual integration, true warmed-core experiment, unused slices and
full independent package reconstruction remain required before promotion.

If this family loses, the experiment can distinguish whether old memory, key
geometry, projection, recency or coefficient cost caused the loss. Stronger
descendants include whole-word targets at genuine native boundaries, disagreement
selected memory, density-diverse retention, independent past-article memories
and paid learned retention. They require their own normalized code and matched
controls. A small FIFO failure does not disprove those descendants, and a useful
reservoir signal does not establish an absolute optimum.


## Preregistered selective-rejection extension

Before cache results, add quality c=clip((max neighbor cosine-0.8)/0.2,0,1),
zero for an empty or invalid query. The individual gated head includes f and
f*c, so its strength varies with how closely the previous context matches.
The target-permutation control uses identical keys and therefore identical c.
A gated joint head adds these products for FIFO512 and reservoir512 to the
seven-dimensional joint head, totaling nine coefficients and 72 bytes/copy.
It retains the same positive-semidefinite Hessian and finite supporting-plane
certificate because f*c is fixed before the target. Fourteen tested heads
require a four-bit selector. No result-selected threshold is introduced.

The queued executed worker retains one historical field name ending in
`3bit_selector_bytes`; its arithmetic actually subtracts 0.5 byte, i.e. the
registered four-bit selector. Report the value as four-bit pricing. A cosmetic
rename was withheld after automatic review flagged editing a queued worker;
this does not change the experiment or its charged cost. The unexecuted
prototype was preserved under a distinct filename instead.
