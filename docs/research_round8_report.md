# Round 8: deeper frozen-core research and continuation

6 October 2026. Kaggle session **355655943**. This report records new executed
experiments, mathematical guarantees, implementation defects and remaining work.
It does not certify a record, a 20% improvement, an absolute optimum, or that any
of the 95 idea families has reached its ultimate potential. The current batch
uses the original neural weights unchanged. Statistical fitting of a small
residual is identified separately from transformer retraining.

The portfolio is [research_round8_idea_program.md](research_round8_idea_program.md)
and its machine-readable JSON: every one of the 95 recoverable idea families has
a stronger descendant, discriminating test, dependencies, combination partners,
formal contracts and historical limitations. These entries are a research
program, not 95 completed experiments. The original depth audit remains
[research_round1_to_round7_idea_audit.md](research_round1_to_round7_idea_audit.md).

## 1. What changed in the work

The first extension replaces fixed unconditional boosts with joint normalized
predictions and a hierarchical Bayesian context model. The second changes TTL
into a paid, optimally segmented prediction program, allowing encoder search
without free future knowledge. The third optimizes exact model-description
partitions within a declared grammar. The fourth fixes title parsing and warms
context from genuine earlier decoded bytes. The fifth introduces semantic
co-occurrence relationships rather than more spelling moments. The sixth tests
continuous residual strengths and provides a convex supporting-plane certificate
within a bounded family.

These are materially different tests from repeatedly changing a hand-picked
boost. They still cover restricted mechanisms. Fully learned retention,
rich grammatical placement, endpoint-conditioned constructor coding, full
production lexical preprocessing, exact native integration and full package
verification remain unfinished. A losing restricted mechanism does not rule out
those stronger versions.

Two defects in earlier evidence were found in source-level checks. XML tag words
contaminated title keys, and distinct constructor/source-surprise context states
collided numerically. Both are now separated and tested. Earlier outputs remain
preserved; they are not rewritten as corrected measurements.

## 2. Objective and what mathematical rigor means here

For the actual package convention minimize

\[
 S= B_{payload}+B_{compressor}+B_{archive\ stub}+B_{assets}
\]

with the official multiplicities for the chosen executable form. Assets include
weights, dictionaries, graph/rule tables, fitted coefficients, side messages,
order descriptions and loaders. Minimize S subject to exact reconstruction and
the CPU, RAM and disk restrictions. A decoder must not access external pretrained
files or a network; offline encoder research or training can use GPUs. Rechecked
6 October: [official detailed rules](https://www.hutter1.net/prize/hrules.htm).

The accepted record on the official page is 100,424,672 bytes. Strictly more than
20% improvement would require **at most 80,339,737 bytes**. This is a target, not a
forecast. A public candidate and a self-extracting archive-only benchmark have
different accounting; do not compare either silently to the official package.
[Official prize page](https://www.hutter1.net/prize/index.htm).

Define the available information before event t by
\(\mathcal F_t=\sigma(x_{<t},\text{stored assets},\text{decoder state})\).
Every prediction and gate is measurable with respect to this information.
Transmitted context choices expand the available information only after they
are decoded. A predicted guess is not the same thing as a previously decoded
correct symbol: the latter is safe shared context, the former needs a defined
rejection/correction process.

For bit probability p and score f, use
\(q=\sigma(\operatorname{logit}p+f)\). This is a normalized Bernoulli.
For a full word model, \(q(w)\propto p(w)e^{f(w)}\) also needs its normalizer over
every possible word and fallback path. A correct observed word's improved score
alone does not establish compression; all competing mass and false activations
are charged. Most relation and placement proposals fail when that cost is omitted.

Four distinct kinds of claim must be kept apart:

1. A mathematical identity or bound for an explicitly declared class.
2. An independent implementation check of that identity.
3. Measured integer prediction or actual range-coded bytes on fixed inputs.
4. A qualifying, self-contained full package with independent reconstruction.

This batch has results of kinds 1–3, principally integer prediction diagnostics.
It has not produced kind 4. Rigor does not require complicated-looking notation;
it requires a valid event model, a complete cost ledger, falsifiable comparisons,
independent checks, and claims scaled to what was demonstrated.

No finite list of prototypes proves an absolute architecture optimum. The
unrestricted shortest-program problem has the familiar computability obstacle;
with completely fixed executable formats and finite execution bounds, exhaustive
search becomes finite in principle but vastly impractical. Our precise optima
below are within stated partition, segmentation or bounded linear families.

## 3. Evidence foundation and recovered earlier experiments

The session initially had two idle Tesla T4 GPUs and approximately 7.8 GB free
persistent working space. It retained original rounds, checkpoints, native
binaries, the exact dictionary, four 2M inputs, uint16 final-bit probability
traces, and the full old-FX2 transformed stream. No deletion was needed.

The native trace is the final probability after the original mixture, not a
standalone transformer logit. A postprocessor replay therefore asks whether its
feature adds evidence after everything that the current final coder already
uses. The original core trajectory is unchanged. Full integration must preserve
its decoded-symbol update trajectory; it cannot replay research traces at decode.

Inputs A/B/C/D and their trace hashes are retained in the asset manifest and
original round7 records. Each trace is 32M bytes for a 2M-byte input. The dictionary
is 411,996 bytes with 44,515 ASCII word IDs; it is not an enumeration of every
distinct word/string in enwik9. Cold-start old-FX2 slices are a research comparator,
not a reproduced full lexical production preprocessing pipeline.

Read-only recovery found 18 early neural configurations, three seeds each,
54 distinct checkpoint hashes and 270 reported small reconstruction passes.
These include causal, glyph, linear, orthographic, shape, shuffled, prior,
quantization, PCC binary/geometry/structure/Wordle and related configurations.
The recovered records report 3,000 training steps; they must not be silently
equated with the old prose description of a 400-step first-round screen.
OCR, residual, retrieval, skeleton and distillation reports were also recovered.
They partially close the prior source gap without certifying the missing chronology.
See [recovered ledger](../scripts/research_round8_recovered_round1/README.md) and
[session source inventory](../data/research_round8_session_readiness.json).

## 4. Conditional joint gate: completed full A/B/C/D replay

Protocol: [conditional gate](research_round8_conditional_protocol.md).
Implementation: C++17, g++ -O3; immutable original observer source is included.
Twenty-five candidates contain exact identity, intercept and temperature controls,
separate relation/run strengths, joint strengths and nonlinear interaction terms:

\[
 q_{\theta,t}=Q16\{\sigma(l_t+\theta_a a_t+\theta_b b_t+
 \theta_{ab}\tanh a_t\tanh b_t)\}.
\]

Four matched arms use generic calibration, rank/length random relation plus run,
grammar plus run, and integer spelling geometry plus run. Context partitions are
bit position, native-probability band, code-parser state, punctuation, preceding
word class and event-age band. The declared maximum is 20,873 nodes. A local prior
puts 1/2 on identity and 1/48 on each other candidate. Each internal node puts
1/2 on stopping and 1/2 on splitting.

If local and child cumulative log likelihoods are ell and s, the posterior
stopping probability is sigmoid(ell-s). Compute each prediction bottom-up before
using the decoded bit, then update saved pre-observation likelihoods. In exact
arithmetic this is the Bayesian marginal over the declared tree prunings and
candidate assignments. Hence

\[
 L_{mix}\leq L_{T,\theta}-\log_2\pi(T,\theta).
\]

The guarantee prices model selection. It does not imply the gate's candidate
features contain new information or that Q16 has zero tax. Actual rounded gains
and tax are reported separately. An independent Python rational batch marginal
matches the C++ online predictions to 2.22e-16. Prefix noninterference and integer
identity checks pass. This is a prediction check, not a new complete archive.

Over all four 2M slices, generic saves **27.923621 ideal-coded Q16 bytes**;
random+run 15.596461; grammar joint 15.280457; geometry+run 16.996054. These are
likelihood-derived byte equivalents before executable, assets and framing. No
relation arm beats the generic control. Full replay uses about 323–385 CPU user
seconds and roughly 97M bytes RSS per slice for all four arms together. Research
trace buffers and replay binary costs are not production incremental costs.

Conclusion: this finite conditional family supplies no package candidate. It
does not exhaust variable-order grammar, learned relevance or rich lexical heads.

## 5. Paid policy TTL: exact optimum in a finite grammar

Protocol: [paid schedules](research_round8_paid_schedule_protocol.md).
The encoder may choose a policy with future knowledge if it sends the policy and
its duration first. Divide byte positions into fixed 1,024-byte units. A segment
pays its policy prior and an Elias-gamma duration, and a global mode pays one bit.
For K candidates the identity prior is 1/2 and all others 1/[2(K-1)].

Let A_c(j) be cumulative gain for policy c through unit j. The exact recurrence is

\[
 D(j)=\max_{i<j,c}\{D(i)+A_c(j)-A_c(i)-L_{ID}(c)-L_\gamma(j-i)\}.
\]

Induction on the last segment gives the optimum within this grammar. The reported
gain is max(0,D(B))-1 bits. This is not a free best-expert oracle and not a learned
memory TTL controller. Independent enumeration of all compositions and labels
in four small cases agrees exactly; contiguous coverage and neutral headers pass.

ABCD 2M each: generic programs save **96.658488 bytes** after these side-code
charges; the combined 97-option relation/grammar/generic family saves **94.908488**.
Each nongeneric arm saves 25.750734. Additional family choices make the combined
program more expensive than generic. About 150–175 CPU user seconds per slice
cover all candidates and all five optimizations.

The A32K pilot saved about 79 bytes and full A2M about 78: much of the opportunity
is startup, not a proportional bulk gain. Do not project that pilot per megabyte.
Code, graph and actual packet framing remain unpaid. No native implementation was
promoted because the measured margin is inadequate for the current module.

Stronger follow-up: optimize article/schema-aligned segments with a paid grammar,
then a conditional policy-ID prior. Every altered grammar needs its own code
length and inverse. If policy-only gains remain tiny, change the source signal
instead of repeatedly enlarging the segmentation search.

## 6. Exact weight descriptions: limited positive diagnostic

Protocol: [weight partition](research_round8_weight_partition_protocol.md).
The exact raw dump has 435 arrays and 39,559,303 bytes, including data that the C3
recipe reconstructs rather than stores. It is not the current model cost.
The scan uses 219 int8 tensors and 5,870,484 symbols.

For counts n_i over a declared alphabet of k symbols the KT marginal is

\[
 P(x)=\frac{\Gamma(k/2)}{\Gamma(N+k/2)}
 \prod_i\frac{\Gamma(n_i+1/2)}{\Gamma(1/2)}.
\]

The code pays a split/stop decision. A dyadic axis partition has
\(C_v=\min(1+C_{KT}(v),1+C_{left}+C_{right})\).
Terminal blocks stop at 4,096 symbols or an unsplittable axis. Two selector bits
and eight alphabet metadata bits per tensor select homogeneous/row/column modes.
This yields the best description in this separable finite grammar, not the best
possible weight codec.

Counts-only empirical entropy is 23,242,630.014828 bits; homogeneous KT cost is
23,258,445.849352; priced best partition cost 23,253,921.532814. Comparing both
modes with the same per-tensor 10-bit outer charge gives **839.289567 bytes saved
per model copy**. Comparing priced best with the uncharged homogeneous number
gives only 565.539567; mixing those conventions would exaggerate the result.
Independent exact rational KT error is 5.33e-15 bits and enumeration of 26 dyadic
descriptions matches the DP to 3.55e-15 bits. Worker wall time was 0.438 seconds;
standalone user/RSS accounting was not collected for that phase.

No arithmetic-coder/container, scale/float/RoPE recipe, loader or native model
parity was implemented here. An 839-byte statistical description improvement is
not a real C3 container improvement. Earlier uniform-Q4 savings apply to the
older model; applying that format to current lexical C3 previously grew it by
940 bytes per copy. Quantization alphabets and container recipes matter.

## 7. Title semantics, namespace repair and genuine prefix memory

Original Expert::chars parsed ASCII words from `<title>` itself while the title
flag was active, putting the common word `title` in title keys. Related-page
selection therefore had spurious overlap. This violated the intended feature
semantics, although it remained a causal, normalized predictor. It must not be
used as proof that proper title retrieval was tested.

CleanExpert skips tag and metadata words, handles quoted `>` characters, waits
for complete entities, commits only completed lexical words, and retains only
completed past article summaries. It does not parse every Unicode/XML grammar;
its ASCII observer scope is explicit. Self-tests include literal/entity forms,
tag exclusion, donor availability, EOF nonflush and mass normalization.

Failure history is preserved:

| Version | Observed issue | Repair/evidence |
|---|---|---|
| v1 | Test expected four aardvark events; fixture has three | Correct fixture assertion, retain failed binary/log |
| v2 | B contains a tag/comment exceeding the 4,096-byte buffer limit | v3 uses bounded 129-byte prefix, quote state and three-byte terminator tail |
| v3 | Runs and passes; old context namespaces still overlap | v4 uses disjoint feature-key namespaces |
| v4 | Complete A/B128K, no promotion | Independent key-space enumeration and clean parser tests pass |

Old constructor and source-surprise keys overlap on 224 synthetic states.
For example, key 1600 represents both a constructor state and a different
source-surprise state. The replacement uses dedicated high bits for the kind and
disjoint packed fields. Exhaustive enumeration gives 876 distinct reachable
kind/state keys rather than the old union of 652. This changes evidence attribution
and possibly prediction; it does not change old archived results retrospectively.
[Namespace audit](../data/research_round8_context_namespace_audit.json).

v4's six arms are generic, persistent exact title, matched random title,
title spelling geometry, past-title retrieval and matched random donors. Only
real clean text activates title/grammar residuals. No arm meets the registered
64-byte combined improvement over controls on two 128K pilots. Persistent title
gains about 0.743 byte on A and loses about 0.243 on B before package cost.

Next, the statistical source is reconstructed incrementally from the real
earlier full old-FX2 stream up to A/C/B/D's synchronization. This is a genuine
prefix-memory test; the **core probabilities are still cold slice probabilities**.
It cannot be called a full warmed-coder result. All A prediction hashes match
the independent cold A traversal, and the full source slice bytes match inputs.

Before scoring C at 100M transformed bytes, 41,868/44,515 dictionary words had
appeared (94.05%); before B at 102,635,191, 41,933 (94.20%); before D at 180M,
43,192 (97.03%). Those positions are about 17.1%, 17.5% and 30.7% of this
586,459,020-byte transformed stream, not of the raw one-billion-byte input.
Counts cover this clean ASCII dictionary observer, not the proposed 200K unique
word inventory. Source counts do not say that the model predicted each word
correctly without correction bits.

Warm-source generic and five lexical arms remain within fractions of a byte of
identity; there is no useful measured warm-source gain. The 1024-entry past bank
fills, but available words and helpful word choices are different quantities.
Reconstructing prefix source state and evaluating four pilots took 175.11 CPU
user seconds, 176.48 wall seconds and 1,016,276 KiB peak RSS in this research
implementation. It loaded the full source file for verification; a production
decoder would stream earlier bytes. Future bytes never choose features.

## 8. Semantic descendant: co-occurrence instead of letter moments

Spelling geometry cannot reliably infer that `no` and `know` are semantically
related. It can encode a useful bias under constrained capacity, but more moment
polynomials do not supply arbitrary missing semantics. This branch tests external
frozen semantic information explicitly, charges it, and compares the same words'
spelling relationships and shuffled relation controls.

The [Stanford GloVe release](https://nlp.stanford.edu/projects/glove/) derives
vectors from global word co-occurrence; that is a different source of information
from spelling. Use the author's 2024 Wikipedia+Gigaword 50D vectors, licensed
PDDL 1.0. Download 301,036,094-byte zip; stream only matching dictionary rows
without extracting the 842,192,707-byte member. Source hash and HTTP metadata are
recorded. Selected 44,515×50 float32 vectors plus header take 8,903,128 bytes.

43,939 dictionary words have vectors, 576 missing words use a declared self-only
fallback. Take eight cosine neighbors excluding source, constructors and words
shorter than three letters. Graph construction uses GPU research; CPU decoding
requires only frozen IDs. Graph size is **712,240 raw bytes**, zlib9 652,866 or
LZMA6 613,724 before loader/framing. The graph is a shipped model, not free context.

The semantic last-content arm follows the most recent completed content word;
a second semantic topic arm combines title and the most recent 16 content words.
Shuffled controls match frequency bands and spelling lengths. All arms share
constructor-run evidence, candidate family and context gate. The sparse word
distribution is normalized against the same prefix-frequency prior. Constructor,
case, nonlexical, escape and partial EOF bits remain included.

Parser tests and normalization pass (semantic error 6.77e-15). A/B128K complete;
every semantic/generic/spelling/shuffled arm loses approximately 0.19–0.27 byte
under the gate. Every best fixed candidate also selects identity once its prior
and mode are charged. No arm passes the 64-byte advance gate. This does not make
the embedding itself useless in a better architecture; it rejects this sparse
neighbor excitation mechanism. The graph cannot be justified by these gains.

## 9. Continuous residual: current finite-family follow-up

Protocol: [continuous strength](research_round8_continuous_protocol.md).
This removes the coarse-strength confound after the preceding failure. It exports
all pre-observation relation/run features and native probabilities, fits a small
statistical model on A/B, and evaluates unchanged coefficients on C/D. The core
transformer remains frozen. No neural finetuning is represented as complete.

For X=[1,logit(p),a,b] and theta in [-1,1]^4,

\[
 f(\theta)=\sum_t[\operatorname{softplus}(l_t+X_t\theta)
 -y_t(l_t+X_t\theta)].
\]

The gradient is X'(q-y) and Hessian X'diag(q(1-q))X, positive semidefinite.
An optimizer alone is not a certificate. Convexity gives

\[
 f(\theta)-f^*\leq\nabla f(\theta)'(\theta-v),\qquad
 v_i=-1\text{ if }\nabla_i f\geq0,\ v_i=1\text{ otherwise}.
\]

The explicit gate is at most 0.05 byte of numerical optimum gap in this box.
Independent finite differences, Hessian quadratic forms and a dense 1D check
validate the calculus and supporting-plane computation. Results are then rounded
with the actual uint16 rule. Four coefficients cost 32 bytes per shipped copy;
the generic control has two, so it pays 16. Mode/arm selectors, graph and loader
are additional. A development ideal optimum is not a production compression bound.

The v1 worker had a syntax error before execution; the controller log and source
hash are preserved in a failure manifest. The v2 repair changes only the missing
parenthesis and is syntax-checked before upload. The results table generated
below is authoritative for final status; do not relaunch its completed directory.

### Continuous fit: measured outcome and its stronger descendant

All six development fits pass the <=0.05-byte supporting-plane certificate;
the largest numerical gap is 0.000183 byte. This certifies the ideal optimum
only within the recorded feature/box family. Semantic last-content strength is
0.05319, well below the previous positive grid minimum of 0.25. Thus the original
finite-strength test did miss a weak positive signal.

Fixed A/B128K coefficients give semantic last-content 6.747915 Q16 bytes gain
on A/B and 14.443476 on C/D. Generic gives 0.571710 and 2.166226; shuffled
last-content gives 1.009695 and 3.712878; spelling gives 1.078605 and 1.402845.
Both semantic test slices are positive before costs. This is specific evidence
for conditional semantic information, not a significant compression breakthrough.
The coefficient and 614KB graph costs still swamp these sample gains.

The independent C++ implementation then matches all 24 Python uint16 prediction
SHA256s exactly, with gain differences below 3e-12 bytes. It freezes the same
heads for full ABCD2M confirmation. To test a cheaper descendant, last-content
source marginals compare each semantic prediction to the same head with its
relation feature disabled. Because the core and feature trajectory depend only
on original decoded bytes and coefficients are fixed, those source marginals
are additive. A table with uint16 source ID and eight uint16 neighbors costs
18 bytes per selected row per copy. With two copies, the finite best subset is

\[
 G_{sparse}=G_{off}+\sum_v\max(0,G_v-36)-4-64-1/8\quad\text{bytes}.
\]

This prices row IDs, targets, count, coefficients and mode; module/framing still
cost more. It is a useful finite optimum, not permission to select word hints
with free future knowledge. Full confirmation and sparse selection status are
recorded below. [Fixed and sparse protocol](research_round8_fixed_semantic_protocol.md).

### Directed memory: the next graph-free descendant

The expensive semantic graph suggests a different source of relations: learn
directed word associations incrementally from earlier decoded text. A new
registered source has two direct-mapped 1024-row tables, one for next content
word and one for up to eight prior content words in the same article. Each row
keeps eight targets/counts with deterministic collision replacement,
Space-Saving updates and bounded counters. A hypothetical packed layout uses
69,632 bytes for the two row arrays; actual instrumented layout is wider and
reported. It is decoder state, not a free model: code, time, classification,
regret and full RAM still count.

The next and wider models have frequency/length/content-class matched shuffled
controls and an exact-recency control. They share constructor-run evidence.
State is warmed on genuine earlier full-source bytes, while native core traces
remain cold. A/B128K fit bounded heads; C/D evaluate the frozen heads. This
tests usefulness of earlier decoded relations without shipping GloVe. It does
not implement a globally optimal retention controller or rich learned syntax.
[Directed memory protocol](research_round8_directed_memory_protocol.md).

## 10. Resource-aware combination architecture

The published C3 full package sources report compressor + archive 99,313,750
bytes: compressor 3,477,137 and archive 95,836,613. The archive contains stub
198,236, dictionary 100,866, weights 2,978,039, payload 92,559,456 and header 16.
These are historical source values, not a new full execution in this batch.
The compressor also stores article order. Read the exact executable ledger
before selecting a package comparator.

Published full peak **9,765,024 KiB = 9,999,384,576 bytes** leaves only **615,424
bytes** under conservative decimal 10GB. Cold-slice 6GB peaks do not provide full
memory headroom. The raw semantic graph alone exceeds that margin. Accepting
10GiB instead would change the margin, so use the conservative interpretation
until the intended unit is clarified by the rules/organizer.

A prospective compact interface should share these components:

1. Existing dictionary strings/code IDs and native parser; avoid separate regex
   copies, duplicate tries and image/glyph tables in each expert.
2. One bounded deterministic semantic/orthographic candidate index, with a null
   relation and exact spelling fallback. New immutable tables are priced.
3. One prefix count system; a uint32 Fenwick array over 44,515 IDs costs about
   178KB. WRT code prefixes map to at most a small number of ID intervals.
4. One article/title/grammar state with sparse integer records and value-aware
   retention. Sharing state does not establish value-aware retention as implemented.
5. One compact residual/gate evaluated only when its prefix conditions are met,
   preserving normalized predictions and the original core updates.

For example, a depth-two 73-node, 25-candidate gate with 16-bit weights is roughly
3.7KB of candidate state before child/counter fields. This is a design calculation,
not a tested replacement for the floating Bayesian gate. Weight quantization,
underflow and regret must be measured before substitution. If extra state cannot
fit, reduce another native allocation deliberately and measure the coding loss;
do not pretend the shared memory is free. Likewise, compressed on-disk graph size
is not resident size after ordinary full decompression.

Independent component savings are never added blindly. For component j, measure
its incremental package gain conditional on selected set A:
\(G(j\mid A)=S(A)-S(A\cup\{j\})\).
Shared compute/state can make some combinations cheaper, while redundant evidence
can make prediction worse. A small factorial study should compare native,
generic gate, relation, grammar, memory, pairs and the joint model under the same
capacity/CPU budget, then select the actual priced package. This batch already
shows relation families can lose their apparent value after generic calibration.

## 11. Next sequence, with concrete descendants rather than repeated boosts

These remain unexecuted unless listed as measured below. All 95 specific routes
and combinations are retained in the per-idea program. Order work by prerequisites
and potential final-bit information, not by whether an approach resembles the
record holder.

**First: native opportunity and interface.** Reproduce full lexical preprocessing
and original priors; verify full inverse. Generate actual warmed native features
in a streaming form. Group residual coding cost into completed constructor spans,
content/named entities, first versus repeated mentions, literal/OOV spellings,
numeric/schema data and markup. Include separators and unsynchronized prefixes.
Earlier placement counts and toy losses are insufficient to locate the full
production opportunity. Existing E/F are examined; preregister new G/H.

The earlier full-ASCII audit covers 1,884,022 word events in the already examined
8M transformed-byte samples: `the` appears 101,915 times, `know` 232, `no` 1,465,
`now` 804 and `diamond` nine. These counts support measuring corpus-wide relevance
before designing around illustrative words. They are not a language universal.
For the fixed 176-word constructor list, constructor spans carry about 17.2% of
sample native bit cost; common grammatical words are often cheap per occurrence.
The measured gap structure has about 87.3% gaps with zero or one constructor,
and multiset sharing reduces distinct template counts only 2.9–6.2% on these
samples. Even eliminating all those constructor-span bits would not by itself
be a >20% total-package improvement on these same samples. A broader grammar
could improve content as well; that remains a different hypothesis to test.

**Second: altered no-core-retraining predictors.** Extend the repaired source to
bounded variable-order constructor suffixes with a null/backoff prior, directed
prefix-learned co-occurrence rather than cosine similarity, affix/phonetic channels
with calibrated rejection, and numeric/schema hypotheses with full false-activation
cost. Compare each with the same generic and same-memory random control. Use
continuous/conditional diagnostics to determine which signal survives the final
coder before integrating a larger gate. Warm both the source and core for the
actual production test. Keep time-to-live as survival/value per RAM byte, rather
than assume any repeated word deserves permanent memory.

**Third: paid right context and reusable textual structure.** Implement a real
ordered constructor/content split with exact lengths, punctuation, case and rare
constants. Decode paid content endpoints first; then encode normalized grammar
gaps conditioned on both endpoints. Start with a classical variable-order gap
model and MDL-selected ordered templates, with the original order as a paid
fallback. A constructor multiset still pays order/multiplicity entropy:
\(\log_2(m!/\prod_i n_i!)\) for a uniform order model; a better conditional model
can reduce it but cannot omit it. For repeated template rules, optimize definition
cost, occurrence IDs, overlapping coverage and residuals jointly. Existing numeric
packets and weak skeleton proxies do not exhaust this textual grammar branch.

For a sequence partition, paid latent z and reconstruction rules r, minimize
\(L(z,r)+L(content\mid z,r)+L(gaps\mid content,z,r)+L(exceptions)\), plus module
bytes. Encoder search may use the whole document only through these paid choices.
The example `there _ a camel` improves after `camel` only if that endpoint is
already decoded or paid; tense and all alternative completions remain probabilistic.

**Fourth: exact-description frontier.** Improve the real C3 container with causal
scale/exponent/bitplane prediction and shared tensor priors, implementing the
smallest exact loader and pointwise model identity. Convert the measured dyadic
KT proposal to actual bytes only if the module can fit its margin. Separate
lossless model representation from lossy quantization; then use the latter only
with native rate/distortion validation. The raw 39MB dump includes regenerable
arrays and cannot be used as the alleged current model cost.

**Fifth: learned residuals and core training.** Rich relevance, retention,
constructor placement and compact semantic factors are genuine training branches.
They can share a tiny residual state and output head. Train directly on native
final-bit features without waiting for the unfaithful GPU core port; require
identity export, causal inputs and actual native integer checks. Core finetuning
still requires layer-wise frozen parity and representative token-weighted data.
See [detailed training plan](research_round7_finetuning_execution_plan.md).

These are stronger hypotheses, not promised successful versions. Failed
descendants should generate a different mechanism where the evidence suggests
one, not a claim that enough mathematical sophistication guarantees success.

### Source-idea mathematics: corrections that matter in implementation

Both [idea_arch_1.txt](idea_arch_1.txt) and [idea_arch_2.txt](idea_arch_2.txt)
are useful architecture proposals. Their fully learned mechanisms are not
represented as implemented by the restricted tests above. Several details need
correction before a serious implementation:

1. The proposed moments are linearly dependent: A_(1-u)=A_0-A_u and
   A_((1-u)^2)=A_0-2A_u+A_(u^2). Use an independent basis, such as discrete
   orthogonal polynomials over word positions, rather than paying for redundant
   features. If glyph vectors are fixed linear functions of one-hot letters,
   G_k=T A_k. Their possible value is a parameter-sharing bias or a compact
   representation, not new information absent from the letter basis.
2. Soft-min edit energy is a useful proposal score, but finite-temperature path
   multiplicity means it is not automatically a metric or a calibrated word
   probability. A proper pair-HMM needs insertion/deletion/substitution transition
   and stopping probabilities, or the finite candidate row must be normalized
   explicitly. Count unseen spellings and escapes separately. Do not infer a
   positive-semidefinite kernel merely from exp(-edit energy).
3. A final-bit trace does not expose the core's counterfactual whole-word
   distribution P_0(w|H). Each hypothetical WRT code would change subsequent
   core states. Use an independently normalized word expert projected through
   the known code tree and a calibrated bit residual, or actually perform a
   costed state-cloned counterfactual evaluation. The new experiments use the
   former interface; they do not pretend to know all core word probabilities.
4. The echo optimum q*=r is correct for the probability of the exact event being
   coded. In a next-word Bernoulli calculation, r must be next-word occurrence
   probability, not occurrence at any time in a 256-word horizon. Learn a survival
   hazard over delay, then derive next-event probabilities and future retention
   value. Otherwise the controller can repeatedly overboost a word that is likely
   sometime but unlikely now.
5. Adding source-word log-odds does not make correlated hints independent. Use a
   calibrated joint score, interactions and rejection; compare conditional gain
   after the existing coder. The finite joint gate, continuous heads and source
   marginals above make this cost explicit in restricted settings.
6. O(K) describes updating K known candidates, not necessarily finding them or
   normalizing a full word model. Account for ANN/lexical index construction,
   search, full softmax or exact tree conditionals and cache misses. An eviction
   value must use expected counterfactual future coding benefit, with negative
   activations and estimation uncertainty, rather than raw similarity or a free
   target-known oracle.

A shared learned successor can use an event-level latent state
\(h_{r,t+1}=e^{-\Delta_t/\tau_r}h_{r,t}+I_r(z(u_t),s_t)\), updated only after
the completed decoded word. A causal slot state s_t and signed activation h_t
jointly produce a normalized code-tree residual; explicit null writes and null
predictions preserve a baseline branch. Training should optimize actual final-bit
loss plus priced quantized parameters. A code-tree classifier can avoid a full
vocabulary softmax if every conditional branch is normalized, but its node
representations, literal/word mixture, case and stopping support are still part
of the implementation. This is a design, not a completed model.

Another graph-free descendant worth implementing separately is a bounded cache
of the **existing native transformer's** pre-word hidden states and subsequently
decoded target words. Project/quantize keys, store values only after they become
known, retrieve a small donor set, and project a normalized donor distribution
through WRT prefixes behind a null gate. This uses semantic information already
in the stored core rather than a new GloVe table. It needs native feature export
at the exact pre-observation state, neutral probability identity, key/value timing,
same-memory recency/shuffled controls and warmed history. The earlier 14.86GB
all-history bank does not settle a 128/512/2048-entry compact cache. It is not
implemented in the initial batch. Section 15 now executes a native byte-target
variant; this whole-word-target version remains unimplemented.

## 12. Training budget and the relevant mathematical target

The existing $70 plan is unchanged: $4 compatibility pilot, $12 matched screens,
$36 selected winner, $8 export/native verification and $10 reserve. **Spent $0**.
No Vast rental has been created. Hardware-hour estimates must use measured useful
targets/sec and the current chosen offer including storage, rather than a guessed
5090 headline rate. Keep full-checkpoint/export reserves before spending the rest.

For a residual independent of the frozen core use native l_t and causal features
h_t, with a zero-initialized correction f_theta(h_t):

\[
 J(\theta)=\sum_t -\log_2\operatorname{Bern}(y_t;
 \sigma(l_t+f_\theta(h_t)))+8mB_{packed}(\theta).
\]

m is the actual package multiplicity. Sampling expensive events requires inverse
sampling weights to preserve the corpus objective. Train the generic equal-byte
head and feature-shuffled controls with identical data/compute. Export actual
quantized parameters and evaluate Q16/native loss; neural perplexity alone is not
the selected objective. An identity branch protects reconstruction support, not
the final rate from a poorly calibrated module.

For core training, F0 zero-update load/export must match the native baseline,
then F1 lambda-zero representative continuation must be stable, before rate
penalties are ranked. The old GPU/native parity test failed and remains a gate.
That failure does not logically block a separately trained final-bit residual.
Do not use old article-uniform/prefix-truncated sampling or blindly restore the
bad lambda30 surrogate. Keep metadata, tail, case, fallback and reset positions.

For old transformed length T=586,459,020, a claimed 20,084,935-byte payload saving
would require about 0.27398 final bits per transformed byte if other costs were
fixed. The new diagnostic gains are nowhere near that scale. The post-training
gain remains unknown; neither a 20% forecast nor a hard impossibility follows
from these fixed-feature results. Only a priced native training pilot can inform it.

## 13. Reproduction and safe handoff

Local sources, protocols and manifests use the `research_round8_` prefix. Remote
root is `/kaggle/working/hp_round8`. New session kernel is
`e1c130f3-38ee-42f4-8e7e-30f834a5b0e4`. Signed proxy credentials remain only in
conversation/runtime; never place them in reports or bundles. The Node bridge
`kaggle_research_client.mjs` accepts HP_KAGGLE_BASE and read/put/download/exec
operations. Worker launchers use exclusive output directories and controller logs.
Inspect completed manifests before any continuation; reuse a live PID rather
than duplicate a job. v1 failure evidence is preserved even when v2 succeeds.

Compact bundle includes exact experiment sources, binaries, manifests, tests,
graph and selected vectors, with per-file hashes. Large original GloVe zip and
regenerable continuous feature exports remain remote; their provenance/hashes
are preserved. Native models and source corpus are preserved in the older roots.
Use the evidence hash ledger to verify download/extraction before rerunning.

No project deletion, paid rental or original-transformer retraining occurred in
this batch. The managed Goal remains usage-limited and has not been resumed or
replaced. This work follows the latest explicit human continuation; scheduled
heartbeats must not bypass that limit. The overall week objective remains open,
with end date 11 October 2026. Current measured status and CPU/cost tables follow.

<!-- generated-round8-results -->

## 14. Final measured batch ledger

Generated 2026-10-06T08:29:39.163245+00:00. All registered jobs in this batch completed; the overall research and all 95 families remain open. No qualifying archive or 20% gain. Figures below are likelihood-derived integer-prediction byte equivalents except where an explicit finite side-code or diagnostic description is stated.

| Joint gate, ABCD2M (8M) | Gain before module/assets/framing, bytes |
|---|---:|
| generic | 27.923620853 |
| random_plus_run | 15.596461065 |
| grammar_joint | 15.280456963 |
| geometry_plus_run | 16.996053758 |

| Paid policy programs, ABCD2M | Gain after policy/duration/mode only, bytes |
|---|---:|
| generic | 96.658487999 |
| random_plus_run | 25.750734030 |
| grammar_joint | 25.750734030 |
| geometry_plus_run | 25.750734030 |
| combined | 94.908487999 |

| Frozen AB128K continuous head, full ABCD2M | Integer prediction gain before assets, bytes |
|---|---:|
| generic | 33.134735648 |
| semantic_last_content | 191.944362250 |
| shuffled_last_content | 56.500859803 |
| spelling_last_content | 29.181234278 |
| semantic_topic_context | 147.716122873 |
| shuffled_topic_context | 35.644928934 |

The semantic last-content head is positive on all four full slices. The approximate native cold-sample likelihood cost from the existing float32 cost arrays is 1,510,771.473 byte equivalents. Its 191.944362-byte gain is approximately **0.012705%** of that sample cost. This is neither an archive measurement nor a full production extrapolation. The full graph is 613,724 LZMA bytes per copy before framing, requiring 1,227,448 bytes for two copies; the measured signal does not justify it.

The exact finite source-row subset selects 0 rows on combined ABCD. Its best priced result is -27.035706162 bytes before loader, so ordinary native mode wins. Maximum combined marginal for any source is 0.978874871 byte versus 36 bytes charged per selected row. The independent subset enumeration passes. This rejects that specific row format/frozen head at this scale; it does not bound compressed factors or all retention mechanisms.

| Directed source warm, native core cold; AB fit, CD frozen test | AB128K+128K gain | CD128K+128K gain | AB after two coefficient copies and selector | Certificate gap (bytes) |
|---|---:|---:|---:|---:|
| generic | 0.571710 | 2.166226 | -31.803290 | 0.000000278 |
| directed_next_content | 10.087630 | 8.823959 | -54.287370 | 0.000000765 |
| shuffled_next_content | 1.942886 | 2.411964 | -62.432114 | 0.000003132 |
| exact_content_echo | 3.279588 | 4.291250 | -61.095412 | 0.000008912 |
| directed_window8 | 2.446863 | 2.196954 | -61.928137 | 0.000031690 |
| shuffled_window8 | 0.678658 | 2.258525 | -63.696342 | 0.000008221 |

Next-content associations have a small positive controlled signal; widening to eight-content co-occurrence does not improve it here. These parameters are fitted statistical models with a frozen original transformer. Full warmed-core and actual code costs remain required. The independent source tests pass; instrumented association arrays occupy 106,496 bytes, while 69,632 bytes is a packed-layout design estimate. No graph or current-word target is supplied to the predictor.

| Research execution phase | CPU user seconds | Peak RSS KiB |
|---|---:|---:|
| conditional all4arms a_2m | 322.770781 | 96596 |
| conditional all4arms b_2m | 384.751257 | 96480 |
| conditional all4arms c_2m | 383.030783 | 96540 |
| conditional all4arms d_2m | 376.012742 | 96668 |
| paid all5programs a_2m | 149.923439 | 96524 |
| paid all5programs b_2m | 173.190464 | 96744 |
| paid all5programs c_2m | 174.676246 | 96664 |
| paid all5programs d_2m | 167.444063 | 96408 |
| fixed all6heads a_2m | 96.896142 | 98160 |
| fixed all6heads b_2m | 167.311149 | 97920 |
| fixed all6heads c_2m | 167.494448 | 98068 |
| fixed all6heads d_2m | 184.797309 | 97944 |
| title/retrieval warm-source | 175.113455 | 1016276 |
| directed warm-source/export | 126.389282 | 1016376 |

Continuous fit/evaluate wall time: 12.332879s. Directed fit/evaluate wall time: 17.491135s. Those in-process fitting phases do not have separate wait4 user/RSS accounting; do not reuse exporter-only RSS as their measurement. Research binaries include instrumentation, duplicate source structures and traces; their size/peak is not the compact native incremental cost. Actual native package, Geekbench-normalized time and full peak gates are unexecuted.

Authoritative compact machine-readable results: [research_round8_final_summary.json](../data/research_round8_final_summary.json). Sources, individual controls, coefficients, prediction hashes and failure traces remain in their corresponding manifests and evidence bundle. No dataset/model deletion or paid expense. The $70 training plan remains staged and unexecuted.


## 15. Native representation cache extension (registered, running)

The first evidence bundle validated 189 files. Subsequent work now instruments
the current native C3 hidden representation without changing its probabilities.
The first A32K arithmetic archive and final Q16 trace are exactly unchanged.
Full independent decoding and the B identity controls must pass before any fit.
Controller repairs are documented in the checkpoint; failures remain intact.

This extends the design-only pre-word cache proposed above into an actual native
**byte-target** pilot. Its full equations and engineering are in
[research_round8_hidden_cache_math.md](research_round8_hidden_cache_math.md),
and the preregistered protocol is
[research_round8_hidden_cache_protocol.md](research_round8_hidden_cache_protocol.md).
Fourteen heads compare FIFO128, FIFO512, a fixed 32-coordinate projection, long-lived
reservoir512, matched target permutations, ordinary recency, generic calibration
confidence-gated rejection and joint models. A/B development fitting is frozen on C/D. None of these is
yet a measured cache compression gain. Production/native integration, true warm
history, fresh slices and package qualification remain open.

The actual Predictor already instantiates KVI8, so its documented 1.7 MB cache
saving cannot be claimed again as space for this extension. The conservative
full-program margin remains 615,424 bytes. A successful compact production
cache must be measured inside that whole-program peak.

<!-- native-cache-extension-results -->

## 16. Completed native-cache descendants and baseline correction

Updated 2026-10-06T09:50:13.968927+00:00. All 14 first-cache and 37 altered-cache heads completed. Original transformer weights unchanged; fitted statistical coefficients and prefix-learned means/counts are distinguished from neural retraining. No qualifying archive or 20% gain.

The read-only native patch exposes existing q5[192] before the next byte. Both A/B32K arithmetic archives and final uint16 traces are identical to the unchanged reference; independent decoding exactly recovers raw input and hidden records. Four full128K traces also match the preserved native trace. These are genuine native identity tests, not a GPU approximation.

| First native cache head | A/B gain, bytes | Frozen C/D gain, bytes | A/B after two coefficient copies + 4-bit selector | Ideal convex certificate gap, bytes |
|---|---:|---:|---:|---:|
| generic | -0.405318024 | -1.640862684 | -32.905318024 | 0.000005441 |
| hidden192_fifo128 | 5.253642708 | 3.485361892 | -43.246357292 | 0.000001720 |
| hidden192_fifo512 | 4.903517446 | 5.217939823 | -43.596482554 | 0.000605209 |
| hidden32_fifo512 | 6.356370240 | 4.879521701 | -42.143629760 | 0.000209068 |
| shuffled_targets_same_cache | 2.468407657 | 0.270555531 | -46.031592343 | 0.000018040 |
| plain_recency_fifo512 | 2.717575604 | 1.703438154 | -45.782424396 | 0.000011657 |
| hidden192_reservoir512 | 0.746130830 | -1.828612989 | -47.753869170 | 0.000325724 |
| shuffled_targets_reservoir512 | 1.289131431 | -0.224846209 | -47.210868569 | 0.000851730 |
| joint_hidden_and_recency | 7.438808048 | 5.936008500 | -105.061191952 | 0.000366004 |
| gated_fifo512 | 7.970678948 | 4.504563260 | -56.529321052 | 0.000008273 |
| gated_shuffled_fifo512 | 6.219394256 | -0.466655726 | -58.280605744 | 0.000001659 |
| gated_reservoir512 | 3.877568687 | -5.735698571 | -60.622431313 | 0.000053863 |
| gated_shuffled_reservoir512 | 2.582365055 | -2.478283619 | -61.917634945 | 0.000255957 |
| joint_gated_hidden_and_recency | 12.309824598 | 1.456574215 | -132.190175402 | 0.001803096 |

The executed first-cache worker has a historical field name mentioning3bits, but its arithmetic correctly subtracts0.5byte for the registered four-bit selector. Most ungated cache strengths are negative. Therefore these small gains mostly indicate an anti-expert/calibration, not successful positive semantic recall. The joint first-cache head gains5.9360085bytes on C/D before any assets; the gated joint gains1.4565742. Longer uniform retention loses. All first-cache A/B gains lose to coefficient copies before loader.

The next descendant changes geometry and retention: the same current prefix coordinate system centers both query and donors; diagonal variance scaling has positive weights; sharper normalized K1/K8 kernels replace weak bandwidth; a separate cache retains only already-observed >2bit native errors. Signed and nonnegative recall fits distinguish correction from recall. Equations and the exact17source families are in [research_round8_metric_cache_protocol.md](research_round8_metric_cache_protocol.md). A/B chooses; C/D is now a previously seen exploratory check.

| Altered metric/retention head | A/B gain, bytes | Exploratory C/D gain, bytes | A/B after coefficient copies + 6-bit selector | Certificate gap, bytes |
|---|---:|---:|---:|---:|
| generic | -0.405318024 | -1.640862684 | -33.155318024 | 0.000005441 |
| raw_soft_signed | 4.903571874 | 5.217935028 | -43.846428126 | 0.000064062 |
| raw_sharp_k1_signed | 1.546208905 | 1.850138244 | -47.203791095 | 0.000076001 |
| raw_sharp_k8_signed | 1.650392894 | 1.874934989 | -47.099607106 | 0.001772920 |
| raw_tau100_signed | 4.926604188 | 5.074749233 | -43.823395812 | 0.000116484 |
| centered_k1_signed | 1.477470353 | 1.444316344 | -47.272529647 | 0.000027681 |
| centered_k8_signed | 1.726063876 | 1.675899401 | -47.023936124 | 0.000084758 |
| whitened_k1_signed | 1.411833567 | 1.555637975 | -47.338166433 | 0.000222675 |
| whitened_k8_signed | 1.546426839 | 1.916534177 | -47.203573161 | 0.001591584 |
| shuffled_raw_k1_signed | 0.542829663 | -1.564393135 | -48.207170337 | 0.000003573 |
| shuffled_centered_k1_signed | 0.123934717 | -1.373791389 | -48.626065283 | 0.000044176 |
| shuffled_whitened_k1_signed | 0.398695156 | -1.204161196 | -48.351304844 | 0.000022756 |
| hard_centered_k1_signed | 4.412992872 | -4.699374432 | -44.337007128 | 0.000001775 |
| hard_centered_k8_signed | 4.611678483 | -4.882859287 | -44.138321517 | 0.000011748 |
| shuffled_hard_centered_k1_signed | -0.387836035 | -1.790024069 | -49.137836035 | 0.000001952 |
| hard_whitened_k1_signed | 4.554640698 | -5.213843281 | -44.195359302 | 0.000000451 |
| hard_whitened_k8_signed | 4.891378066 | -5.579087913 | -43.858621934 | 0.000011045 |
| shuffled_hard_whitened_k1_signed | -0.399740826 | -1.730535280 | -49.149740826 | 0.000003161 |
| raw_soft_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000012851 |
| raw_sharp_k1_positive | -0.405305635 | -1.640789642 | -49.155305635 | 0.001700412 |
| raw_sharp_k8_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000006092 |
| raw_tau100_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000000179 |
| centered_k1_positive | -0.405305635 | -1.640789642 | -49.155305635 | 0.001415754 |
| centered_k8_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000000095 |
| whitened_k1_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000006006 |
| whitened_k8_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000002140 |
| shuffled_raw_k1_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000016067 |
| shuffled_centered_k1_positive | -0.405346834 | -1.640741596 | -49.155346834 | 0.001316052 |
| shuffled_whitened_k1_positive | -0.405318024 | -1.640862684 | -49.155318024 | 0.000015967 |
| hard_centered_k1_positive | 4.412992872 | -4.699374432 | -44.337007128 | 0.000001775 |
| hard_centered_k8_positive | 4.611678483 | -4.882859287 | -44.138321517 | 0.000005910 |
| shuffled_hard_centered_k1_positive | -0.387841416 | -1.790023236 | -49.137841416 | 0.000038926 |
| hard_whitened_k1_positive | 4.554640698 | -5.213843281 | -44.195359302 | 0.000000297 |
| hard_whitened_k8_positive | 4.891378066 | -5.579087913 | -43.858621934 | 0.000005578 |
| shuffled_hard_whitened_k1_positive | -0.399734343 | -1.730540400 | -49.149734343 | 0.000036444 |
| joint_signed | 10.900473564 | 2.144166161 | -101.849526436 | 0.004341158 |
| joint_positive | 4.595169245 | -5.110127801 | -108.154830755 | 0.000621083 |

After coefficient copies/selector the best fitted A/B head is generic at-33.155318bytes; identity wins. The64byte priced advancement gate fails, so no candidate is tested on G310M/H520M. Their cold native baselines independently decode exactly, including hidden-state equality, and remain available as unexamined candidate checks. Those baselines are on the old transformed stream, not canonical lexical production. No parameter/hyperparameter setting was chosen from their outcomes.

| Phase | CPU user seconds | Peak RSS KiB |
|---|---:|---:|
| native hidden export a128K | 111.042363 | 5861812 |
| native hidden export b128K | 121.206369 | 5962080 |
| native hidden export c128K | 119.466663 | 5963960 |
| native hidden export d128K | 119.239042 | 5958472 |
| first-cache all-source export a128K | 7.165080 | 78140 |
| first-cache all-source export b128K | 7.089180 | 159004 |
| first-cache all-source export c128K | 6.941529 | 198948 |
| first-cache all-source export d128K | 7.006272 | 238896 |
| metric-bank all-source export a128K | 127.418119 | 78264 |
| metric-bank all-source export b128K | 127.821495 | 249136 |
| metric-bank all-source export c128K | 128.055114 | 321896 |
| metric-bank all-source export d128K | 127.647093 | 394608 |
| fresh g128K encode | 121.649419 | 5963584 |
| fresh g128K decode | 119.528718 | 5963472 |
| fresh h128K encode | 120.858340 | 5894320 |
| fresh h128K decode | 117.419771 | 5894144 |

These are whole research-child lifecycle peaks; launcher inheritance, retained NumPy data and multiple controls can affect them. They are not native incremental cache RAM. The first fit/controller used144.780873CPU-user seconds and815,104KiB across its child lifecycle. The second fitting wall phase is86.494343seconds; its worker did not isolate fitting CPU/RSS from exports. A selected512key design is102,912bytes before layout/control, with3,080bytes for prefix mean/variance. Actual whole-program native peak and single-core time remain untested. Existing KVI8 cannot supply another1.7MB saving.

The native-controller failures are preserved: missing /usr/bin/time; restored reference binary lost executable permission; omitted -d decoder mode. Repairs reused the successful build and A encodings, then kept exact gates. The first successful A encoding process accounting was not persisted by the failed controller; it is not reconstructed as a precise measurement. No original models/data were overwritten or deleted.

A material baseline audit now proves that the old article order SHA256 `4d0fa5313c753c1ecf71e91a83e285894cdde20049711456e6514c07eb85c581` differs from the lexical source order `eecd462c29319bab185b48229c4d09ab52f16ca9c582e8e32eff9a7c2a7de39e`; both dictionaries equal `4c8568cca9343b9a6212477880f56f8efd162f8784224a25edd043097d36215a`. This does not invalidate matched cold diagnostic comparisons, but it prevents extrapolating them to the complete record. An isolated full lexical preparation/inverse utility is now running, without neural coding or spending. It uses ample remote /root scratch rather than deleting preserved project assets. The correct full prepared stream must be preserved and hashed before production-native experiments or training.

Next descendants still open: boundary-aligned whole-word targets, value/diversity retention, predictive-distribution/Fisher geometry using existing core parameters, structured factual/schema memories, paid constructor/content ordering, learned conditional residuals and core finetuning. Losing37fixed heads does not rule those out. Full warmed native history and full package reproduction are also still open. All95families remain unfinished.

<!-- canonical-preparation-results -->

## 17. Correct lexical stream and exact full preprocessing inverse

The correct lexical order is now reproduced and independently inverted through the original native preprocessing code. The dictionary equals the old stream's dictionary, but the article order does not. The canonical final prepared stream is **587,138,826B**, SHA256 `7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce`. It contains the586,459,321B pre-tail stream plus679,489B side information and16B footer. Side SHA256 `98bae9de75b13b0a4f66f33cd24f1c45b145237eb4f99b363c9cb4e6ef918d95`. The complete inverse produces exactly1,000,000,000B with original SHA256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`.

Preparation used89.179715CPU-user seconds,100.801471wall seconds,1,688,764KiB peak RSS; inverse415.462029CPU-user seconds,427.816229wall seconds,1,517,616KiB RSS. Build38.146831CPU-user seconds. Remote scratch12,865,151,805 apparent bytes. This accounts only the preparation/inverse utility, not entropy coding. The utility bypasses packed self-unpacking only with explicitly verified assets, while the actual transformations remain unchanged. R1 inverse mutates a separate encoded scratch copy. All original models/data and both transformed streams remain preserved; **no project files were deleted**.

This completes a fidelity prerequisite; it provides no compression improvement. A full canonical entropy archive, fully warmed native comparison, code/model accounting and qualifying single-core execution remain open. A new registered dictionary-atom memory experiment uses this correct stream and is running, with exact A/B32K reference/decode controls before512K exports. It repairs internal-code-byte targeting, adds a compact prefix-interval probability representation, and compares geometry, error retention, permutations, recency and causal Bayesian versus fitted gates. See `research_round8_atom_cache_protocol.md`. The result is pending, not a success claim.

## 18. New competitive reference and updated target

A source check on6October found cmix-neif1.0, submitted5October, reporting **95,914,051B total** (pending verification). The official awarded record remains100,424,672B; the preserved lexical model's own comparator remains99,313,750B. A strict>20% reduction from the new reported entry requires<=76,731,240B. The new target and fixed-C3-asset arithmetic are in `research_round8_competitor_update.md`. A matched improvement against our lexical model would still need a complete comparison with this newer entry. [Official awarded reference](https://www.hutter1.net/prize/index.htm), [current benchmark entries](https://mattmahoney.net/dc/text.html), [competitor source](https://github.com/marwoelk/cmix-neif-1.0).

All95families remain OPEN. The successful full preprocessing inverse,51bounded cache-head certificates and finite tensor/program optima are material reproducibility/math results. They are not an absolute compression optimum, a qualifying gain,20%, or work equivalent to the historical research effort behind attention/LLMs. The per-family program explicitly distinguishes completed finite methods, design-only learned architectures and required deeper/native/full checks.


<!-- session355735431-integration-start -->
## 19. Attached curriculum and resumed canonical experiments — 2026-10-06T12:09:15.241318+00:00

The9,969B attachment was read in full. Its useful additions are cost-weighted opportunity mining, paired error replay, acceptance/rejection, causal synthetic relation tasks and an unweighted finish. Weighted objectives, plug-in cluster entropy and altered-prefix priors need the corrections in [research_round8_attachment_assessment.md](research_round8_attachment_assessment.md). The detailed controlled training ladder is in [research_round8_attachment_training_addendum.md](research_round8_attachment_training_addendum.md), within the unchanged$70cap and$0spending. All six new mapped proposals remain open.

Session355735431 preserved four canonical native512K exports and A/B atom features. Old355655943 became unreachable during fitting. The corrected resumed worker completes11bounded heads without repeating core inference. Future-target/hidden noninterference and32K independent native decode/reference identity are reused and hash-checked. All ideal support-plane certificates are below0.05byte. These certify a continuous finite box objective only; Q16, package and warmed-history optima are separate.

| Canonical atom head | A/B Q16 gain bytes | After two coefficient copies + 4-bit selector | Ideal supporting-plane gap bytes |
|---|---:|---:|---:|
| generic | 5.653032535 | -26.846967465 | 0.00394792665 |
| raw_word | 6.325384505 | -42.174615495 | 2.41839222e-10 |
| permuted_raw_word | 5.898203523 | -42.601796477 | 0.00467415852 |
| centered_word | 6.396554002 | -42.103445998 | 2.73297481e-10 |
| permuted_centered_word | 5.989836647 | -42.510163353 | 0.00484432819 |
| white_word | 6.446761606 | -42.053238394 | 3.08752197e-10 |
| permuted_white_word | 6.030069682 | -42.469930318 | 0.00488301141 |
| word_recency | 9.923581757 | -38.576418243 | 4.86052899e-10 |
| centered_hard_word | 15.767434220 | -32.732565780 | 1.8292447e-09 |
| permuted_centered_hard_word | 5.635124195 | -42.864875805 | 0.00405858654 |
| joint | 28.249721346 | -84.250278654 | 1.09744214e-08 |

Fixed causal global/context policies save-0.255883569/-1.465964140bytes on A/B. The best priced fit is generic at-26.846967465bytes. The joint head's28.249721346raw bytes versus generic5.653032535 suggests a small finite interaction; its112.5byte assets dominate this1MiB screen. Most ordinary recall coefficients are negative; the hard-word coefficient is positive. The registered64B advancement gate fails and C/D candidate evaluation is not performed.

This is a finite screening decision, not a proof that full-file amortization or trained retention fails. Those coefficients would be stored once per package copy over the full file; cold reset samples do not establish the warmed rate. A new weak-signal branch needs a predeclared full-rate/code-size test and independent or honestly exploratory checks. Do not scale28bytes to587M and call it an achieved archive saving.

The stronger paired contextual-error memory is launched in error_memory_resume_v2, PID136 at launch; verify current manifest and actual child process, do not duplicate. It preserves probability/outcome pairs, estimates a strongly convex local signed correction, matches prefix events and compares actual/permuted keys, recency and prefix-only controls. The canonical cost atlas is COMPLETE; canonical A/B attribution and stable causal-mixture diagnostic preserved locally. Its global Bayesian mixture required log posterior odds; a batch likelihood-normalizer identity independently checks its streamed result. All failures/repairs and exact executable sources are preserved in the handoff.

The new competitor source audit is [research_round8_neif_architecture_audit.md](research_round8_neif_architecture_audit.md). Causal reminders, online word models and recurrent final-bit corrections support stronger descendants of the user's ideas. Their alphabet/training/state/resource contracts differ from this core; no competitor code or model has been adopted. The pending95,914,051B target still requires<=76,731,240B for>20%; no such result is demonstrated.

Current count:62native/metric/atom fitted heads complete. All95families remain OPEN. No absolute optimum, LLM-development-equivalent effort, qualifying full archive or20%gain is claimed. Exact full preprocessing inverse is complete; full entropy archive/CPU/RAM qualification is open. No project deletion; spending$0. See research_round8_session355735431_extension_status.json for machine-readable handoff.
<!-- session355735431-integration-end -->








<!-- current-native-rarity-integration-start -->
## 20. Native source observation, stronger residuals and rarity allocation —2026-10-06T15:06:38.167328+00:00

The completed24paired-error heads certify their ideal boxes to<=.05byte but
fail the registered priced gate; best priced result-26.971967465B.
The27constant-time role policies are considerably cheaper to replay, about8CPU
seconds/slice for the full research sweep, yet actual roles save4.468373421B
versus generic4.576862926B and permuted roles4.623679192B. Their best selector-
priced gain3.998679192B fails64B. This does not settle nonlinear learned roles.
The complete native cost atlas attributes constructor atoms12.8477% of A/B
ideal bit cost; the remaining dictionary53.0499%, literal/control33.4788%.
Common frequency is not equivalent to recoverable native entropy.

The observer exports19actual core channels before consuming each target,
preserving both full A/B512K archives and every native integer probability,
plus independent32K decodes. Its observation files are not decoder assets.
V1fit failed before fitting due to overlapping2/3byte WRT initial codes;
V2preserves the failure and checks all44515codes/proper prefixes. It supplies
stronger source disagreement/role interactions and a128bit-delay control.
Its exact earlier integer laws pass future target/source/role noninterference.
Source fit status:COMPLETE31heads; best priced A/B42.446535646B; advancementFalse.
Independent weak-source confirmation:COMPLETE_WEAK_SOURCE_INDEPENDENT_Q16_CONFIRMATION, launchPID1208; separate preregistered weak-signal branch, original64B gate still fails.
Actual inline result:COMPLETE_NATIVE_INLINE_RESIDUAL_COLD_CODING_DECODE; launchPID1235; C/Dactual archive gain127B, lab binary delta768B; full/package qualification open.
Nested wider coefficient family:COMPLETE_WIDER_SOURCE_FINITE_BOX; launchPID1306; development priced gain81.72835071134426B; E/FstatusCOMPLETE_FRESH_WIDER_SOURCE_EF_Q16_CONFIRMATION, launchPID1316.
Fresh E/F frozen wider Q16 gain153.8376543026439B; both improve and beat generic:True.
Actual wider native result:COMPLETE_NATIVE_INLINE_WIDE_COLD_CODING_DECODE; launchPID1329; actual E/Farchive gain154B; matched lab binary delta784B; full/package qualification open.
The first source bound had derivative-329.141nats toward a larger coefficient;
an extended-box fit removes this artificial limitation without changing features.
Fresh E/Fconfirmation passed; the old C/Dresults cannot be relabeled fresh.

|Registered head|A/B Q16 gain bytes|After2coefficient copies +5bit selector|Ideal box gap bytes|
|---|---:|---:|---:|
|generic|5.653032535|-26.971967465|0.00394793|
|raw_source_00|5.753265621|-42.871734379|0.00444905|
|raw_source_01|5.696299980|-42.928700020|0.00437825|
|raw_source_02|5.268685490|-43.356314510|0.00409061|
|raw_source_03|5.694072609|-42.930927391|0.00440782|
|raw_source_04|66.272132000|17.647132000|6.626e-05|
|raw_source_05|5.309418900|-43.315581100|0.00411487|
|raw_source_06|45.131347849|-3.493652151|5.24098e-08|
|raw_source_07|5.800561154|-42.824438846|0.00406394|
|raw_source_08|6.205074590|-42.419925410|0.00439173|
|raw_source_09|5.757499676|-42.867500324|0.00434113|
|raw_source_10|12.742733618|-35.882266382|7.45483e-09|
|raw_source_11|7.731102444|-40.893897556|0.00481612|
|raw_source_12|5.653032535|-42.971967465|0.00394793|
|raw_source_13|77.928651151|29.303651151|8.25663e-05|
|preSSE_difference|20.016545311|-28.608454689|2.6707e-05|
|FXCM_difference|5.653032309|-42.971967691|0.000258785|
|neural_difference|89.296266329|40.671266329|1.70545e-08|
|raw_joint|187.697030508|-68.927969492|4.95804e-08|
|three_difference_joint|99.827507591|19.202507591|8.57406e-06|
|raw_plus_difference_joint|243.081909582|-61.543090418|2.47109e-06|
|delayed_raw_joint|6.639481883|-249.985518117|0.0046227|
|interaction_joint|146.701745659|2.076745659|2.09707e-09|
|neural_conflict|61.376004401|12.751004401|2.35479e-07|
|neural_valid|91.071535646|42.446535646|1.94977e-08|
|neural_FXCM_conflict_valid_joint|129.881297530|33.256297530|0.00511158|
|role_only|9.149088916|-119.475911084|7.59952e-10|
|role_difference_joint|103.253973793|-73.371026207|1.04133e-05|
|role_raw_joint|190.334598892|-162.290401108|6.39814e-08|
|role_interaction_joint|149.994870326|-90.630129674|2.08434e-08|
|delayed_role_only|6.734155597|-121.890844403|0.00458893|

These figures are development outcomes. Only a predeclared advancement and
frozen independent/native/full-package qualification can establish a candidate.
The historical95family audit remains unchanged; A96now formalizes the user's
frequency-threshold mask/gradient/specialist proposal. Its corpus census is
COMPLETE_RARITY_CENSUS_DIAGNOSTIC; launchPID1192; read its manifest, no masking training yet. Partial dictionary-target residual experiment:COMPLETE_PARTIAL_DICTIONARY_MASK_RESIDUAL_TRAINING; launchPID1400; partial dictionary-target training of a161parameter residual; original transformer/OOV masking/native qualification open.
No full-word/original-transformer mask training is claimed. Detailed equations, controls,
step/throughput GPU-hour arithmetic and70dollar gates are in
research_round8_5090_hours_and_rarity_plan.md and rarity_mask_protocol.md.
No best-possible descendant or LLM-equivalent research effort is established.
All96current families remainOPEN; no absolute optimum/20%archive result.
<!-- current-native-rarity-integration-end -->


<!-- round9-authoritative-implementation -->
## Round9 implementation continuation

Actual selected-core finetuning, full-word literal/OOV labels and new sequence/TTL/word architecture implementations now exist. The prior status in this report is historical. Read research_round9_report.md and research_round9_all96_execution_ledger.md for current work, measured limits and every unfinished family. No20% or qualifying record result is asserted.
