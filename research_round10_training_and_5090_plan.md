# Training and architecture plan within $70

7 October 2026. This is a staged research budget, not a promise of a compression
rate or a measured 5090 runtime. Paid spending remains $0. The user requested
completion of the feasible CPU stage before providing a GPU session.

## Decision objective

For canonical length T = 587,138,826, optimize actual package bytes:

    S(theta) = L_final_payload(theta) + sum_j m_j * B_j(theta).

Here m_j is the actual multiplicity of each model, executable, dictionary, side
stream and option. For the preserved lexical package, model weights are counted
twice. With mean final loss in bits per canonical byte and model rate R in bits,

    J(theta) = mean_CE_final_bits(theta) + m * lambda * R(theta) / T.

Lambda = 1 corresponds to the size trade-off. A sum over n scored targets uses
n*m*lambda*R/T; a natural-log loss multiplies the bit-valued rate by ln(2). The
old lambda = 30 run cannot establish that rate-aware training fails at lambda = 1.
These formulas use bits per canonical byte, summing its eight coded-bit losses.
If the optimizer instead averages individual bit losses, use 8*T as the target
count and divide the per-byte loss/rate term consistently by eight.

Final loss means the complete coding law, including rare/OOV/literal bytes. NN
loss is a diagnostic. The final mixer can absorb, amplify or negate a neural
improvement, so there is no assumed 1:1 NN-to-payload elasticity.

## Prerequisites and exact data handling

1. Finish native CPU evaluation of the repaired BF16 exports, portable mixer
   and component diagnostics. Read the existing live-job manifests first. The
   3–9 MiB sequential prefixes are matched-warm diagnostics, not representative
   corpus estimates. A positive candidate needs broader warm evaluation.
2. Preserve the original 1,000,000,000-byte corpus identity, canonical lexical
   stream, dictionary and order map. Use the actual native 205-symbol vocabulary
   and 5,897,145-parameter core. No alternative preprocessing is silently mixed in.
3. Prepare a registered set of representative production-reset/article pieces:
   article positions, lengths, redirects, metadata, prose, tables/references and
   literal/OOV names. Sampling may use corpus annotations during offline training;
   those annotations are not free decoder hints. Document the target population
   and sampling probabilities, with fitting/development/confirmation roles.
4. Produce PPMD priors using the correct native history and vocabulary. Reusing
   raw priors for redacted input is invalid. Cold independently generated priors
   are a declared surrogate and do not satisfy the warm objective. Full dense
   fp16 priors would occupy about 241 GB; do not create that cache blindly. Measure
   exact block compression, cache only registered samples and use a sequential
   native producer where possible. Training storage is distinct from decoder RAM.
5. Treat each scored position once in the declared objective. Context-only warmup
   and padding have zero target weight; record useful targets separately from
   forward tokens. For piece i sampled with probability p_i, weighted loss A_i and
   fixed global normalization W, use minibatch mean(A_i/p_i)/W. Do not divide by
   the random minibatch's weight sum.

For long recurrent state, fixed-reset pieces must reproduce the actual production
reset law. A truncated context is an approximation, not genuine native history.
During TBPTT, carry state and detach gradients without wiping the memory. Keep
parameters fixed during each accumulation episode if exact forward continuity
under one parameter vector is required. Updating parameters between chunks makes
carried state stale; label and compare that approximation instead of ignoring it.

## One-hour 5090 setup and throughput pilot

Before choosing paid hours, obtain a live all-in price including storage/transfer,
CPU, RAM and billing increments. NVIDIA specifies [32 GB VRAM for the 5090](https://www.nvidia.com/en-gb/geforce/graphics-cards/50-series/rtx-5090/); that does not determine
throughput or CPU decoding feasibility. The pilot is a bounded measurement, with
checkpoint/output preservation before shutdown.

Pin repository/source hashes, image, Python/PyTorch/CUDA/kernel versions, compiler,
seeds and packed model. Import the neutral model and validate native decoded
tensors. Check individual versus packed documents at the proposed context sizes,
including future-document mutation and aggregate gradient agreement. The old
4-document/256-token packing passed its GPU batching test; 8-document and
1024-token packing failures prohibit extrapolating that implementation unchanged.

Start with one 4096-target piece and its genuine context/state, then try 2 and
4 pieces if memory allows. Record median/p90 step time, valid targets/second,
forward tokens/second, data wait, peak allocated/reserved VRAM and host RAM.
Measure at least 20 warmed steps and a short real optimizer run, not just lr=0.
Use 4 documents only if its semantics agree with separate-document execution.

The measured Tesla T4 profile reached approximately 824 and 3,430 useful targets/s
for one and four 256-token documents, respectively, with lr=0 and resident data.
Those are measurements of that particular short pipeline, not a 5090 forecast.

Exact per-row GPU/native probability equality is removed as a veto on trying
training. Compare aggregate paired loss over matched article/reset clusters and
declare an equivalence margin tied to the effect being studied. A nonsignificant
t-test is not an equivalence test. Re-evaluate candidate rankings with native
inference. Independent native encoder/decoder agreement remains exact.

## Stage A: stable continuation and rarity allocation

Use the selected original core, original quantizer and BF16 deployment grid.
If a compatible optimizer state is available, restore it. Otherwise initialize
zero moments with a gradual 64–128 update warmup and a conservative learning-rate
screen, initially 1e-6, 3e-6 and 1e-5. Hold the same initialization, data order,
schedule, batch/targets and number of parameters fixed in paired controls. Treat
weight decay as a registered variable; fresh AdamW/decay on a converged memorizing
model can cause drift before revealing an idea's effect.

Register six principal variants, two seeds each:

- unweighted all-word continuation;
- mild global-frequency loss weighting;
- mild article-frequency loss weighting;
- a context-dependent soft weighting/curriculum that returns to full loss;
- a protected-common-gradient proposal with a matched unweighted control;
- a selective norm/gate or last-block update with matched capacity and schedule.

Thresholds should correspond to declared corpus quantiles or occurrence counts,
not arbitrary numbers chosen after seeing the loss. Keep 107/1,392/8,372 only as
historical reproduction arms. Compare rare weights 0.5 and 0.1 before considering
zero as a curriculum. Distinguish training loss masking, input redaction, paid
literal insertion and a deployed common/rare router; they are different codecs.

For an unrestricted weighted-loss model, its optimum tilts probabilities toward
the weighted outcomes. Zero rare weight can therefore damage all-word likelihood.
Finite shared-capacity models may still benefit from better gradient allocation,
curriculum or specialization. Measure common loss, rare loss and final total;
neither the KL identity nor a tiny zero-mask run resolves that engineering question.

Let g_C be the common-loss gradient and d the proposed descent direction, so
theta_new = theta - eta*d. Project the actual Adam/decay proposal, not merely
the raw gradient:

    d* = d - min(g_C dot d, 0) * g_C / ||g_C||^2.

If ||g_C|| is zero, skip that projection instead of dividing by zero.
Then g_C dot d* >= 0, a first-order local statement. It does not guarantee a finite
update after BF16/code-grid projection. Use the realized quantized update and
re-evaluate common loss; report step size, curvature remainder and noisy gradient
estimation. Two-group constrained proposals may protect both gradients when
feasible, but do not create an unconditional improvement guarantee.

Checkpoint rungs are 128, 384 and 1024 updates. Use full declared scored pieces
and record real useful-target counts. Prune only after the unweighted control is
stable, enough targets/classes are covered and development evidence has power.
An early negative rung rejects that finite schedule, not the architecture.

At each retained rung: original-order/BF16 export, native reader validation,
actual model bytes and matched native combined-CM loss/archive. A transformer-only
flag must not be assumed to code neural probabilities; the old flag returned PPMD.

## Stage B: entropy-constrained deployment and complementary training

After stable continuation, add rate penalties at lambda in {0.5, 1, 2}, with lambda
0 retained as the stable control. Differentiate a declared surrogate for code
occupancy and float-plane cost; measure actual native container bits at checkpoints.
Squared distance outside an old quantization cell is not an entropy rate estimator.
Near-uniform fixed quantizer indices do not rule out rate-aware training, and
high-rate scalar theory does not guarantee its gain for this finite learned model.

Allocate precision by final-likelihood sensitivity and actual storage growth.
Compare selected BF16/FP32 constants, quantized codebooks and per-layer updates.
Use exact model-byte changes rather than a nominal bits/parameter label. The new
exports demonstrate 38–60 byte growth per copy for three old trained models;
prior BF16-QAT manifests show 23/19 bytes. Their compression gains still need
warm reproduction and whole-package evaluation.

For complementarity, a frozen linear logit mixer with NN coefficient w has
natural-log gradient w*(q_mix-y) with respect to its NN logit. If the NN coefficient
is already inside z_mix, multiplying mixture-BCE by w again double-weights trust.
SSE contributes its derivative; online mixer feedback changes future state.
A frozen-mixer surrogate is an approximation. Train paired NN-CE and mixture-aware
arms, then refresh native evaluations instead of claiming the frozen surrogate
optimizes the full production coder exactly.

## Stage C: adequate word and memory descendants

The expensive shortlist is determined by CPU evidence, not by attempting 96 full
architectures simultaneously. Two promising families have concrete discriminators:

**Word architecture.** A spelling composer versus independent word embeddings,
with random-basis and byte-head controls at equal capacity. Warm-start full-word
root supervision; jointly train representation, literal/OOV support and the
dictionary/literal gate; finish on all-bit final loss. Record the number and
frequency of seen classes. Exact code-tree marginalization and native normalization
precede compression claims. Letter/multiset/phonetic features can share statistical
strength; they do not supply unseen words for free.

**Long memory.** Compare carried lexical/title memory and projected native-state
memory against no-memory and 128-byte reset controls. Episodes should cover at
least 64 KiB and exceed the tested horizon; use several articles when testing
cross-article retrieval. CPU code already implements fixed 1,024/32,768/131,072-byte
decay summaries with exact fixed-point state. Learned retention/eviction needs
adequate state-carrying training, not another 128-byte reset.

For a small decay bank, an analytic eligibility trace can retain long-horizon
derivatives without backpropagating the whole transformer history. If

    c_t = a*c_(t-1) + (1-a)*v_(t-1),
    e_t = c_(t-1) + a*e_(t-1) - v_(t-1),

then e_t = dc_t/da when v is independent of a. With a=exp(-1/tau),
da/dlog(tau)=a/tau. This is exact for that frozen-input decay channel, not for a
fully endogenous transformer with arbitrary state dependencies. Compare it with
carried TBPTT and a fixed-timescale bank; keep insert-after-decode semantics.

The combined descendant is a word-boundary controller that uses normalized
spelling/semantic proposals, bounded decoder-rebuilt memory and the final-coder
trust law. First test each factor and paired interactions. A full factorial of
three finalists is eight arms; choose an appropriately aliased design for more
factors. Synergy and redundancy can have either sign. Do not add individual gains
or impose an assumed universal discount.

## Conditional experiment hours

The following calculation uses four pieces with 4096 useful targets each, giving
16,384 useful targets/update. Padding/context/data stalls can lower that number;
the run logger supplies the actual count. The experiment portfolio is a shortlist,
not thorough testing of all 96 families.

| Allocation | Useful targets under this assumption |
|---|---:|
| Six continuation variants × two seeds × 384 updates | 75.5 million |
| Three survivors × two seeds × 640 further updates | 62.9 million |
| Two rate/mixture variants × two seeds × 384 updates | 25.2 million |
| Four word/memory/control variants × two seeds × 384 updates | 50.3 million |
| **Total** | **214 million** |

Training hours = total useful targets / (measured useful targets/s × 3600).

| Sustained useful targets/s | Pure training time for that shortlist |
|---:|---:|
| 3,000 | 19.8 hours |
| 10,000 | 5.94 hours |
| 30,000 | 1.98 hours |

These are arithmetic scenarios. Add measured setup, cache/deployment evaluation,
checkpointing and data stalls; no fixed multiplicative “5090 speedup” is assumed.
Long-memory/word variants can have different throughput and need separate pilots.
Reaching 6000 steps is unnecessary for every arm, but 384 steps cannot establish
the best architecture or conclusively reject an undertrained one.

One full canonical pass at those rates takes approximately 54.4, 16.3 and 5.44
hours, respectively. From-scratch reproduction of hundreds of pretraining passes
is a different scale of compute. A $70 budget supports targeted continuation and
architecture screening much more plausibly than an exhaustive replacement-model
retrain. Any larger budget request should follow a reproducible native advantage.

## Dollar allocation and hard stop

Proposed allocation: $12 for persistent CPU qualification, $8 for measured GPU
setup/throughput, $40 for the best training shortlist, and $10 reserve for storage,
transfer or a failed instance. These are spending caps, not verified quotes or
authorization for a newly purchased host. At all-in GPU price p dollars/hour,
the $48 GPU allocation buys at most 48/p hours; use a live quote before renting.
Vast charges compute, storage and transfer separately, and stored data can remain
billable while an instance is stopped; include those costs in the cap. See the
[provider's pricing documentation](https://github.com/vast-ai/docs/blob/main/guides/instances/pricing.mdx).
CPU evaluation should run on separate free/dedicated CPU resources so an idle
GPU is not billed through a 55-hour decode.

Stop before exceeding the account/billing/budget limits, preserve resumable
checkpoints, and never restart rejected/usage-limited work automatically. Paid
hardware has not been launched. No scientifically honest calculation currently
guarantees a record or a 20% reduction from this budget.
