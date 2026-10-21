# Testing coverage, 5090 hours and the rarity-mask experiment

6October2026. Actual measured archive improvement of20%: **not achieved**.
Thorough completion of every idea: **not achieved**. Best possible descendants:
**not established**. These answers apply even when a small convex subproblem
has a valid numerical optimum certificate. A finite certified basis is a
different claim from a globally optimal architecture or research effort
comparable to the development of attention/LLMs.

## Coverage and what still has to be built

The recovered round1–7 audit contains95distinct families. Its historical route
counts are31no-offline-training,34no-offline-first/conditional-training,
9new-codec,10training,9new-codec-plus-training,2qualification. Thus53historical
families have a conditional training route, not95independent ready-to-run
neural models. Six attachment proposals map into these families. The user's
new frequency-mask/gradient-allocation proposal is now explicitlyA96; it adds
one training family. This reconciles the **current** ledger to96without
inventing a recovered96th historical item. The historical audit remains intact.

Implemented descendants include exact native probability instrumentation,
probability/outcome-paired causal memory, strongly convex signed-error roots,
bounded source-conditioned fits, equal-capacity delayed/permuted controls and
constant-time online role residuals. Historical screens also include spelling,
structure, ordering and representation variants. However, jointly trained
retention/rejection, ordered constructor infill, nonlinear relation gating,
matched-capacity visual inductive biases and the new masking architecture are
not all executed. Some earlier tests were proxies rather than the architecture
the user described. The per-family ledger records these gaps explicitly.

The current engineering work makes the hypotheses testable: immutable source
hashes, exact integer-law observation, independent decodes, prefix causality,
supporting-plane optimization certificates, normalized outcome laws and
package/whole-resource gates. Further work includes the actual architectures,
optimizer/kernel/export parity, matched target exposure and independent/full
codec tests. There is no defensible point at which we can certify that an idea
has reached its absolute potential or that a descendant must work.

## How much 5090 time to reserve

**Paid5090hours needed now for the small residual/finite CPU pilots:0.** The
freeT4timing probe completed with unchanged model parameters: the833parameter
MLP processed16.71million resident bit targets/second; the2033parameter GRU,
sequence128,batch256, processed11.49million. Median32768target steps took
.001961/.002852seconds, using35.1/101.4MB peak allocated device memory.
These repeated-resident-batch/FP32/zero-lr timings exclude CPU generation,
full dataset movement, actual learning and native export. They are not proof
of compression, nor5090performance. Native bf16 support measuredfalse even
though PyTorch's default emulation-aware capability flag returnedtrue.

**For the more demanding transformer/architecture shortlist, reserve at most
4billed5090hours for readiness and a
throughput pilot; then a focused12–24GPU-hour screening tranche if its measured
price fits the existing dollar caps.** Reserve a further8–16GPU-hours for two
finalists only if unweighted independent/native gains justify it. This is a
planning allowance for a shortlist, not an estimate for exhaustively optimizing
all96families. It includes repairs/evaluation allowance; total compute depends
on architecture and useful-target throughput. Two cards for one hour consume
twoGPU-hours. Do not rent before preparing data and export tests.

The measured Kaggle host has two15GiB TeslaT4s, compute capability7.5, and
PyTorch2.10.0+cu128. Many prototypes can run here without a5090. The core
native/GPU numerical mismatch remains an implementation/export gate; faster
hardware alone does not solve it. FP16/FP32 residual pilots and CPU codec
experiments can use Kaggle. The reported PyTorch bf16 capability flag must not
be treated as a measured native-bf16 throughput result on this older hardware.
The exact timing evidence is research_round8_residual_throughput_results.json.

Measure100warm steps, synchronize the device, separately time data loading,
forward/backward and export/evaluation, and record median/p90steady-state
useful targets per second. A step must include its global batch, unmasked
target count and gradient accumulation. For an experiment list,

    GPU-hours = sum_i(seeds_i * useful_targets_i / targets_per_GPU_second_i)
                /3600 + GPU-hours_reserved_for_setup_and_evaluation.

Here is one explicit, auditable shortlist budget. Use18initial arms at128steps;
continue6to384and3to1152. This costs

    18*128 + 6*(384-128) + 3*(1152-384) =6144steps/seed.

Two seeds cost12288steps. If the declared global useful batch is2^20targets,
that is12,884,901,888target exposures. It means the following **throughput
scenarios**, not measured5090performance:

| Useful targets/GPU-second | Two-seed short ladder | Extend two finalists/seed from1152to3000 |
|---:|---:|---:|
|100,000|35.79GPU-hours|21.53additionalGPU-hours|
|250,000|14.32GPU-hours|8.61additionalGPU-hours|
|500,000|7.16GPU-hours|4.31additionalGPU-hours|

A batch of32768would divide those times and exposures by32; it would not
provide the same experiment. Residual bit targets and transformer byte targets
are different units and must never be mixed in this arithmetic. Real tensor
shapes, padding, masks, optimizer, precision and CPU preprocessing determine
throughput. I will replace the scenario with an actual5090benchmark before
committing a paid schedule.

For scale, testing96families with3arms,2seeds and just128steps at that large
batch costs73728steps:85.90GPU-hours at250kuseful targets/second, before
engineering/evaluation. Extending every arm to1152would cost773.09GPU-hours.
Those are illustrative exhaustive grids, not the proposed schedule; many
families are CPU/codec problems, while some new architectures need much more
work than this grid. A single honest all-ideas hour requirement is unavailable.

The public newer competitor's1000bf16-pass recipe corresponds to roughly400
GPU-hours at its author's stated multi-card rate. Our goal is a much shorter,
compatible continuation or residual pilot; reproducing that recipe is a
different budget. [Primary training recipe](https://github.com/marwoelk/cmix-neif-1.0/blob/1c9ea5ed57ec9718bcb681d20b79e81a60b7a728/training/tf/3_train/README.md).

Vast prices depend on live offers and include compute, storage and transfer;
no5090offer has been reserved or charged. Maintain the dollar gates:4readiness,
12pilot,36best continuation,8export/native qualification,10contingency =70.
At an **illustrative all-in**.50/hour, the12pilot dollars buy24billedhours;
at1/hour they buy12. These are budget examples, not current quotes. Transfer
charges and persistent storage must be subtracted separately when they are not
included in the hourly rate. [Vast primary pricing documentation](https://github.com/vast-ai/docs/blob/main/guides/instances/pricing.mdx).

## Whether hard words hurt common-word prediction

It is plausible and testable; it is not established for this core. Shared
parameters can receive conflicting gradients. Ifg_Candg_Rare common/rare
gradients, a small update produces

    Delta L_C ≈ -eta*(||g_C||^2 + lambda*g_C^T*g_R).

When the dot product is negative, reducinglambda can improve that local
common-loss change. But the complete objective also includes rare-word loss,
curvature and changes in shared context representations. Rare words may help
topic/entity prediction. Frequency is not identical to difficulty; a rare name
with a strong copied context can be cheap, and a common article choice can be
uncertain. Measure **signed total bit cost**, gradient geometry and per-class
native loss rather than infer interference from high surprise alone.

The first mask experiment keeps rare words in the input and masks only their
training target loss. Removing/replacing rare context is a separate, potentially
damaging intervention. Weight0,.25,.5,1on rare targets supplies an interpretable
ladder. Always evaluate all words. A frozen-backbone/separate-head control tests
whether shared-gradient interference rather than capacity or target exposure
explains the result. Keep the update count, useful targets and actual work
visible: a mask can make an apparently equal-step run receive fewer targets.

There is also a precise normalization reason to prefer a specialist over blind
loss removal. In an ideal categorical example at fixed contexth, letPbe the
true word law,r=P(R|h), and assign training weights1to common words andlambda
to rare words. An unconstrained weighted-log-loss optimum is

    q_lambda(w|h)=a(w)*P(w|h)/Z(h), Z(h)=1-r+lambda*r.

Its excess ordinary all-word loss is

    KL(P||q_lambda)=log Z(h)-r*log lambda >=0.

Forlambda=0andr>0this diverges: zeroing rare losses does not make their coding
cost disappear. This is an ideal categorical derivation, not a claim that the
byte transformer's finite-capacity training reaches that law. Masking can still
help a constrained shared representation, but only if reduced approximation/
optimization error outweighs its objective bias and rare fallback costs.
An independently calibrated class mass and normalized specialist conditionals
preserve that mass instead of silently reallocating it to common words.

The stronger descendant is a common specialist plus a rare/native specialist.
For disjoint word setsC,R,

    q(w|h)=pi(h)*q_C(w|h), w in C;
    q(w|h)=(1-pi(h))*q_R(w|h), w in R.

The class probability is paid. We cannot consult the unknown current word to
pick its cheaper expert for free. Soft normalized mixtures and causal prefix
counts are legal alternatives; a fallback keeps every exact outcome reachable.
Translate the word law into the native code-prefix law with exact normalization,
including literal, case, escape and layout outcomes.

Global/article final frequencies are permitted as offline training labels.
If decoding needs them, the table or mask must be shipped and charged, or
reconstructed causally. A full article's final counts are not known before it
is decoded. Within-article count cutoffs also label many repeatedly used global
common words as locally rare. The completed full-corpus census measures these
differences; its tokenizer coverage/exclusions are explicit in
research_round8_rarity_mask_protocol.md.

## Short-run decisions and combinations

Use the first128steps to find bugs and obvious gains;384tests adaptation;
1152compares curves. Preserve25%of continuation compute for ambiguous curves,
since architecture rankings can cross. Promote by the unweighted all-target
native score and actual serialized size. A short negative proxy neither closes
the original family nor guarantees that longer training rescues it.

First combine A96with shared residual/special headsA83and hard-word memoryA15.
Compare unweighted, masked and separate-head versions at equal capacity.
Add spelling/phonetic relations only when they improve signed errors over a
frequency-matched permutation control. Add retention/TTL only when useful
donors are demonstrated. Test constructor/content ordering as a paid reversible
codec with actual slot/position/exceptions costs. This is an explicit dependency
ladder; a large all-at-once combination would hide which components pay for
their bytes and inference cost.

The free-T4 partial dictionary-mask residual training is now complete; it is
reported in research_round8_rarity_residual_pilot_report.md. Ten arms/two seeds,
128/384/1152 steps and 36 saved rungs took56.79wall seconds. Masking gave no
consistent held-out total advantage over unweighted training. Original
transformer gradients and full literal/OOV masks are still untested. This
measured small pilot reinforces the current0paid5090hour requirement; it does
not estimate the time for the larger architecture experiments.

The complete lexical census found127,049,170tokens and1,208,329types across
243,425complete pages under its stated tokenizer. Global singleton tokens are
0.482459%of occurrences, whereas article-singletons are24.788358%. Masking those
policies therefore removes radically different supervision. Frequencies and
every word's article statistics are preserved in the20MBgzipTSV; see
research_round8_rarity_census_report.md. Do not confuse these lexical counts
with native bit-cost or dictionary-mask fractions.

No project models/data have been deleted and no paid rental or original core
training has started. Exact full preprocessing inverse is complete; a new full native
entropy archive and CPU/RAM-qualified record improvement remain open.
