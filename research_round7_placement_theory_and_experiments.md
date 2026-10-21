# Placement, spelling triggers and residual compression

5 October 2026. Latest measured status13:38UTC: I03b and I04 complete, both
native32K identity/decode gates PASS, both quantized residual pilot slices
complete (total-4.017518270B/64K input). The4x2M final-bit collector is active
as PID1097. C/D traces completed with full archive/cost identity at13:46UTC;
their32MB/16M-bit traces are being preserved locally. A/B1144/1145 are active.
No meaningful
compression gain or20% result. Older launch statuses below are historical.
This analysis addresses the new community proposals and records
the experiments actually run or launched. Reputation does not establish a
compression result. The useful hypothesis is a directed, timed, context-dependent
correction to the current coder. Neither a spelling relation nor grammatical
regularity guarantees additional bits saved after that coder.

## What the proposals get right, and what needs correction

Already decoded words can create deterministic candidate memories shared by
encoder and decoder. No per-occurrence reminder needs transmission if selection,
timing, eviction and prediction are computed from the same decoded prefix.
Model/code/table costs and CPU/RAM still count. The original archive contains
the entire sequence of choices, syntax, casing and literal spelling, rather than
only unique words. Repeated words retain a conditional information cost.

“Now I know” is a useful lag-two example in ASCII-word units. “Know now” has a different direction
and lag. Neither is an English ordering law: “now know,” “now we all know,”
quotations, titles and markup also occur. Likewise “the” has strong placement
regularities but should not receive a hard zero outside a guessed slot.
Measure the actual corpus, and preserve a normalized fallback. A crucial
engineering correction: this dictionary contains single-letter a and s, but
not i. DICT-event lags therefore omit literal I/i; the count screen's lag two
is not necessarily a two-word English lag. A separate full-ASCII-word audit
was run, including4878 occurrences of i across these four slices. Its1,884,022
ASCII words contain zero now→know or know→now pairs at lags1–4, within either
an article or the raw punctuation segments. This is sample evidence, not a
whole-corpus language claim. The examples are not a demonstrated large target.

“Diamond” can generate spelling/phonetic neighbors, but die/dye/almond/mound
are not independent semantic components of diamond. Many overlapping letters
also produce irrelevant candidates. Structural generation, selection and timing
are different hypotheses and require separate controls.

Letter moments and glyph geometry are useful inductive biases, not extra source
information. For character one-hot vectors e_c, let

    A_k(w) = sum_j psi_k(j/|w|) e_{w_j}.

With bases 1,u,1-u,u²,(1-u)², there are only three independent channels:
A_(1-u)=A_0-A_u and A_(1-u)²=A_0-2A_u+A_(u²). If g(c)=G e_c,
glyph moments are G A_k, a linear transform of those same character moments.
Length, phonetic rules and richer positional features can change the inductive
bias, but “advanced algebra” does not supply new entropy. Normalized moments
can lose length completely; measured collisions include a/aaaaaa.

## The precise compression criterion

Let H_t be the entire decoded prefix, S_t the limited state retained by the
baseline, P_0 its distribution and Q a normalized candidate distribution. Under
the actual conditional law R, the expected ideal saving is

    E_R log2[Q(Y|H)/P_0(Y|H)]
      = D_KL(R || P_0) - D_KL(R || Q).

The objective is to remove baseline redundancy. A deterministic feature phi(H)
has I(Y;phi(H)|H)=0; it can still help a limited predictor because
I(Y;phi(H)|S)>0. This distinguishes useful recovered history from an assertion
that information has appeared for free.

An observed ten-bit word costs -log2 P_0(w|H)=10. Recalling its spelling does not
erase those bits. Raising its probability can reduce cost, but reduces other
outcomes' probability, and those errors must be charged. For a one-word logit
boost a, baseline probability p and true NEXT-WORD probability r,

    q = p exp(a) / [1 + p(exp(a)-1)],
    B(a) = r log2(q/p) + (1-r) log2[(1-q)/(1-p)],
    a* = logit(r) - logit(p).

At q=r the maximum B equals the Bernoulli KL divergence D_KL(r||p), not ten
free bits. A probability of recurrence anywhere in the next256 words cannot
replace r in this next-word equation.

## Placement estimation without neural retraining

At completed dictionary-word event t, source u=w_(t-d) has known lag d. Keep
prefix-only directed counts C_(d,u)(v). A source exposure is an observed target
position at that lag within the same article, rather than every source counted
as a guaranteed future opportunity. Define the normalized global prior and row:

    g_t(v) = [N_t(v) + 64 r_rank(v)] / [N_t + 64],
    e_(d,u),t(v) = [C_(d,u),t(v) + 32 g_t(v)] / [C_(d,u),t + 32].

Unavailable sources/rows use g_t. Sources are chosen before the target; all
counts update only after the target is decoded. Rows persist across articles;
source queues reset at the completed page marker. Thus there are no invented
cross-article lag pairs, while previously learned language statistics remain.

The I04 screen fixes lags {1,2,4,8,16,64} and mixture weights
{1/2,1/4,1/8,1/16,1/32,1/32}. Lag two was included before the first launch to
address the new human proposal. Memory is8192 total rows across all six lags,
32 targets per row. Row LRU is touched on updates only. At a new edge, remove
the smallest (count,word-ID) edge and subtract its count; then add count1 for
the observed target. No evicted count is silently reassigned to that target.
Rescale retained counts by ceil(c/2) at row total2^20. Every retained row remains
normalized. Future production payload estimates for edges/row keys exclude
hash indexing, LRU, alignment, global counts, source queue and executable code;
actual native RSS/package must be measured.

To avoid confusing common-word frequency with placement, the later residual
model should estimate log e_(d,u)(v)-log g_t(v), and then learn the correction
still missing relative to the final coder. Raw co-occurrence lifts are only
descriptive: syntax/topic and the current model may already explain them.

## Syntax, directed low rank and timed echoes

A compact subsequent score is

    eta_t(v) = b_t(v) + z(v)^T W s_t
             + sum_(i<t) sum_r B_r(t-i)
                 [U_r^T z(w_i)]^T[V_r^T z(v)]
             + sum_(active u) a_t(u,v) G_t(u,v).

s_t uses prefix punctuation, case, page/title state and earlier word classes.
The matrices U and V differ: direction is preserved. B_r can be a compact
lag bin or decay basis; signed terms can reject as well as activate. Context
features cannot include the current target, its eventual code width, future
error or the best retrospectively selected donor. A candidate's earlier
occurrence status can be computed from history for each candidate; using the
actual target's future occurrence class to choose a gate would leak it.

For a sparse trigger graph, update after source u is decoded:

    a_(t+1)(v) = lambda(v) a_t(v) + R(u,v) G(H_t,u,v).

The active-state bound, pruning, quantization and decay are part of the codec.
Lazy decay can reduce state-update work; top-K construction and querying are
not automatically O(K), and tree normalization must also be accounted for.
Repeated related sources are correlated evidence. Summing their log-odds as
independent confirmations can overcount them; shrinkage and matched controls
must establish the gain of an interaction term.

For first-recurrence timing, use the at-risk hazard

    h_d(v) = Pr(T_v=d | T_v>=d, prefix available at that prediction),
    Pr(T_v<=W) = 1 - product_(d=1..W)(1-h_d)

under a specified fixed/conditional hazard process. With changing future
contexts, the window probability also averages over those contexts. Fitting a
window recurrence classifier does not supply the per-step hazards. Article end
and dataset end are censoring events; future labels may train/diagnose a model
but may not become decoding features. Neural or table parameters trained on the
corpus must be stored and charged.

## Exact integration with the existing WRT stream

For a word expert e(v) frozen at word start and WRT code prefix a, derive

    e(b|a) = sum_[code(v) starts ab] e(v)
             / sum_[code(v) starts a] e(v).

The expert needs a declared root dictionary/escape/literal gate; it cannot
silently ignore case, punctuation or literal spellings. Prefixes at truncated
EOF must receive their descendant probability and actual baseline cost.
I04 reuses the validated additive-root construction: every post-marker literal,
case/escape and complete/partial dictionary event is charged. It is not the
globally tilted baseline P_0(v) exp(eta(v))/Z(H).

The actual-cost trace records only P_0 along the observed path. It does not
contain final-coder probabilities for every unobserved word. A205-class neural
output is also not the final cmix distribution. Evaluating a global word tilt
would require appropriate counterfactual branches and their normalizer.

A practical alternative is a locally normalized binary correction. For each
actual coded bit, with final baseline p_i and causal expert e_i,

    q_i = sigmoid(logit(p_i) + beta(c_i)^T f_i),

where f_i contains known syntax/age/state, clipped expert-versus-prior log-odds,
and bounded interactions. Online updates occur after the actual bit:

    beta <- beta - alpha (q_i-y_i) f_i

with specified regularization, learning schedule and reproducible arithmetic.
This is prefix-only online estimation, not a free offline trained selector.
Quantize q_i to the coder's integer probability grid and score both outcomes;
the identity branch must return the original integer p_i exactly. These bit
corrections define a valid sequential code, but generally differ from a global
word tilt. Final native roundtrip, package size and judge CPU/RAM remain gates.

## Wordle passes and multiple small transformers

If g=f(H) is a deterministic guess and R_g is an invertible correction map,

    Q(w|H) = Q_R(R_g(w)|g,H).

The correction cost is exactly a different model's cost of w. There is no
inherent information-theoretic gain from filling words first. A useful transform
may make a bounded model easier to train; any position map, uncertainty mask,
answer-derived skeleton, future context or correction count must still be
encoded. Probability refinement is the lower-risk first experiment.

Multiple independent transformers add storage and CPU. Prefer one shared
word-state trunk with placement, spelling and memory heads; add separate models
only when their priced residual contribution survives ablation. Arithmetic
beauty or predicting common words more accurately is insufficient if the base
already predicts them or the errors on hard words erase the gain.

The full objective is J=L_payload/8+B_comp+B_decomp+B_aux, counting every model,
table and runtime included in either program. In a duplicated wrapper layout,
new weights/code may count twice. For example, the proposed44515-word rank16
int8 table alone is712240 bytes per copy: its two copies need about.01943 final
bits per586459020-WRT-symbol stream to break even, before any other overhead.
Online state is reproducible and not a static archive table, but consumes RAM,
startup and decoder time. No paid rental has been launched; the existing$70
training plan is gated on native fidelity and priced residual evidence.

Measured bit budgets also temper the “common words dominate” argument. In these
8M cold input bytes, the dictionary-code occurrences of the average1.907 bits
each, and of average1.094 bits. All12 named/common DICT labels together carry
only5.456% of the full native ideal bits. The's complete-code share is1.609%.
An oracle reducing only those code spans to zero while every other span is
unchanged still cannot reach20%; selectors, errors and added code lower its
practical return. These are restricted span budgets, not unrestricted/global
bounds. Broader content-word first mentions remain a separate research target.

## The actual I05 residual pilot and its result

The pilot is implemented in research_round7_bit_placement_residual.py, rather
than remaining a proposed logistic gate. It uses the same six lag rows and
fixed lag mixture as I04. A dictionary binary trie stores prefix rank mass,
prefix-learned global mass and DFS leaf intervals. Sparse retained row counts
within an interval give exact subtree probabilities without enumerating44515
words at every bit. Trie path products equal the word probabilities in tests.

For each bit's known code prefix a, define the placement-versus-global contrast

    delta_m = clip(logit e_m(bit=1|a) - logit g(bit=1|a), -8, 8),
    q_(m,beta) = sigmoid(logit p_0 + beta delta_m).

The fixed strengths are {-1,-.5,-.125,.125,.5,1}: seven placement families,
42 candidates plus the exact neutral baseline. Each model is rounded to the
uint16 probability grid [1,65535]; zero corrections return the original integer
p_0. A prefix-only Bayesian selector starts with mass1/2 on neutral and1/84 on
each candidate. Its contexts use known bit index, completed code-prefix length,
article-event-age bucket and previous atom category. The weighted selected
integer probability is rounded again; exact integer probabilities are scored.
Posterior updates use actual bits only after prediction. Quantizing the mixture
means an unquantized one-bit-per-context regret bound must not be asserted.

The word-type first branch cancels between expert and global prior, so a
dictionary-only heuristic cannot manufacture a type hint for literal/case data.
When the actual prefix leaves the word trie or a literal escape is active,
delta=0. The parser completes words using already decoded bytes, updates rows
after the complete code and scores every post-marker bit, including truncated
EOF. I/i remains outside the learned DICT sequence; an eventual full-word
placement state would require delimiter-based causal parsing and its own test.

Both native A/B32K controls passed archive identity, old-cost identity, final
trace length/range and independent decode. Reconstruction maximum errors versus
float32 byte costs are4.765e-7 and7.705e-7 bits/byte. Trace native user times
are66.852/66.098s; peak RSS5651732/5798496KiB. This is a lab instrumentation
measurement, not the full qualifying runtime or a new compressed archive.

The residual pilot loses2.235405729 ideal bytes on A and1.782112540 on B,
total4.017518270B lost over64K input. Prototype times58.64/56.14s. It therefore
does not justify deployment or neural spending. Its complete32K results, exact
baseline traces, dictionary and source are preserved locally. The larger2M
collector supplies reusable final probabilities for subsequent syntax,
source-surprise and retrieval residual hypotheses, rather than automatically
promoting this losing pilot.

I04's final A/B/C/D results are-2.496075207/-1.561330466/-2.340943676/
-1.448982361B, total-7.847331710B. Its prototype wall times181.09/196.95/
184.15/180.81s and reported process peaks592928KiB are recorded; this peak
includes prototype/launch state, not a claim about a packed native row table.

## Measured evidence and actual jobs

- Corrected I03b echo finished all four2M slices: A=-2.496618648B,
  B=+4.542206739B, C=+.097987503B, D=+2.100392530B. Total+4.243968124 ideal
  bytes over8M input, before code/CPU/RAM. No production promotion.
- Graph construction was repaired independently:99.248% float-top8 recall on
  fixed queries, and all356120 IDs/scores reconstructed exactly on one CPU in
  30.67s. That is a candidate-search result, not compression.
- I04 directed-placement screen launched as PID119 on session355454655 at
  ~13:02UTC. A=-2.496075207B and B=-1.561330466B were complete at13:11UTC;
  C/D were pending at that check. Normalization, causal direction, deterministic
  eviction, retained-count rescaling, reset and EOF tests pass.
- Native final-bit build PID127 completed. V1 failed before native inference
  because /usr/bin/time is absent. The496320-byte trace executable is preserved,
  as are source/build/failure logs. Compiler restoration used the official LLVM
  signed repository and17.0.6; packages were installed with removals disabled.
  Source trace hashes match the local checked transformation. See
  [LLVM package source](https://apt.llvm.org/).
- V2 identity checks launched as PID1077 at~13:15UTC, reusing that binary and
  measuring each child with Linux wait4. An explicit -d is used for decode.
  Required gates: reference/candidate archives exact; costs exact to previous
  2M prefix;8N uint16 final probabilities; reconstructed costs within1e-4bits
  per byte; independent byte-exact A/B32K decode. No residual gain claimed.
- Placement-example audit launched as PID1084 at~13:15UTC. It counts directed
  pairs at lags1–8/16/32/64 within articles and raw punctuation segments, and
  records complete-code bit budgets for the named examples/common words.
  Whole-slice lifts are descriptive, not causal codec features or bits saved.

For every promising result, freeze design/hyperparameters before new independent
E/F regions, then implement the exact native probability update, independently
decode the archive, price the full package, and measure CPU time/peak RAM on
the qualifying path. A/B/C/D have been examined repeatedly and are screens,
not untouched confirmation. No20% model or package improvement, absolute
optimum, full retraining, paid compute or project deletion is claimed.
