# Audit corrections and current execution contract

7 October 2026, India time. Both CLAUDE audit documents have been read completely.
This document supersedes earlier inferential verdicts; preserved measurements and
historical source files remain evidence, including their mistakes.

## Findings accepted and corrections required

The audit is right about the principal experimental gaps. Tiny cold slices cannot
establish a stationary full-file effect. A memory warmed on earlier text cannot
fairly compete against a cold baseline. Fixed coefficients are paid once per
counted package copy, not once per development sample. Original-model training
was not adequately represented by short residual-head fits. The full original
file was part of the pretrained model's training set; “fit-held-out” describes
only an additional fitting procedure, not unseen pretraining data.

The earlier BF16 storage problem is now measured. Original-order export removed
30,032 bytes of neutral repacking overhead per copy. The completed BF16-grid QAT
and original-type export produced these recorded native combined-CM measurements:

| Model | Model bytes | Growth per copy | B payload saving | E payload saving |
|---|---:|---:|---:|---:|
| BF16 QAT unweighted | 2,978,062 | 23 | 68 | 49 |
| BF16 QAT half rare loss | 2,978,058 | 19 | 70 | 51 |

Each payload test covers 65,536 bytes, with its own unchanged native teacher.
B participates in these models' continuation fitting; E does not, but was used
by other research branches. Native reader identity, independent reconstruction
and encoder/decoder neural trajectory identity are recorded in the manifests.
These values are measurements from the prior session, not a full-file saving.
The latest `/root` artifacts did not survive its replacement; the terminal
manifests survived. Therefore fresh preservation/reproduction remains necessary.
Do not turn a manifest hash into a claim that the corresponding artifact exists.

The previous ~85 KB model-growth break-even is retracted as a decision about
finetuning potential. It priced an export that changed tensor order and promoted
formerly BF16 floats. The ~56 KB ordered export growth also does not apply to
the repaired BF16 models. Both were valid byte counts for those particular
containers, but invalid evidence that finetuning necessarily costs that much.

## Corrections to the companion's own theory

These matter because fixing our work must not replace one unsupported inference
with another.

1. **Entropy along the realized bit path is not a before-byte gate.** Let
   q(0)=q(1)=1/2 for the first bit. Conditional second-bit probabilities are
   1/2 after zero and 0.01 after one. The observed-path entropy is either 2 or
   approximately 1.08 bits, depending on the unknown first bit. The actual
   before-symbol entropy is their probability-weighted average, approximately
   1.54 bits. Averaging paths yields the entropy identity; choosing a path's
   computation budget before the symbol would leak its outcome. The full neural
   205-way distribution is available before a byte and supplies a legitimate
   entropy gate. Previous-byte class and current bit-prefix information are also
   legitimate at their respective decision times. Measured path-entropy cost
   shares remain descriptive; the proposed entropy-directed CPU savings are not
   established by them.

2. **Failure to reject a difference is not an equivalence test.** A test with
   |t| < 2 can accept a very imprecise comparison. Use a predeclared equivalence
   margin and require the confidence interval to lie inside it. Evaluate native
   aggregate loss and checkpoint rankings on matched contexts. Exact per-row
   GPU agreement is removed as a gate to attempting training; independent native
   encoding and decoding remain exact requirements. The upstream engine's
   documented aggregate agreement is evidence for its own tested configuration,
   not automatic certification of our newly modified GPU backend.

3. **The parameter-count optimum is conditional.** The formula
   N* = kappa epsilon P0/(m b) follows from the local log-linear payload model,
   with consistent bit units and m counted weight copies. The estimates epsilon
   and kappa were not measured for this trained canonical production pipeline.
   A toy scaling observation and an assumed kappa in [0.8, 1] do not prove that
   adding parameters cannot help. Log-linear and power-law extrapolations must
   not be interchanged, particularly over factors of 35 or 63. These scenarios
   provide research hypotheses, not lower bounds on attainable archive size.

4. **Lloyd-Max does not generally equalize index probabilities.** At high rate,
   fixed-rate squared-error point density is proportional to p(x)^(1/3).
   Cell probability is therefore approximately proportional to p(x)^(2/3),
   which is nonuniform unless the source is uniform. Near-uniform indices alone
   do not prove that the trained quantizer optimizes the wrong objective.
   End-to-end likelihood distortion also differs from scalar weight MSE.
   Gaussian/Laplacian high-rate comparisons motivate ECSQ experiments, but do
   not guarantee 0.7–1.4 MB from this finite 15-level quantizer.

5. **Combination redundancy need not be positive.** With XOR information,
   two individually useless features are useful jointly. Define measured
   interaction I_AB = G_AB - G_A - G_B, which can have either sign. Do not assume
   submodularity or impose a universal 0.7–0.85 discount. A factorial design must
   state its aliasing; a resolution-V design is appropriate when interpreting
   pair interactions, and untested higher interactions remain unidentifiable.

6. **Greedy plus 2-opt has no generic near-optimality guarantee** for an arbitrary
   asymmetric article graph. Measure proxy objectives before/after, retain the
   original order as a control and charge the actual compressed permutation.
   A changed permutation need not cost the same 199,980 bytes.

7. **The MDL objective must use one normalization.** With mean bit loss and
   model rate R measured in bits, use J = mean_CE_bits + m lambda R/T, with
   lambda = 1 for the exact size trade-off. For a sum over n sampled targets,
   multiply the regularizer by n/T. Natural-log loss additionally requires a
   factor ln(2) on the bit-valued rate. The companion's sum-loss plus rate/T
   expression underweights the rate unless the “sum” is actually a mean.
   Its mixture-gradient formula is correct for a frozen linear logit mixer in
   natural-log units; SSE adds its derivative, and an online adaptive mixer
   responds to changed neural outputs. Weighting mixture-BCE again by w_NN
   double-weights trust if z_mix already contains that coefficient.

8. **A fixed shadow price cannot certify eligibility.** CPU and memory limits
   remain hard constraints. A measured shadow price can rank feasible designs;
   an assumed 50 KB/CPU-hour cannot buy permission to exceed a time limit.
   Early adjacent warm windows are correlated and do not establish the audit's
   nominal nine-percent relative uncertainty for independently sampled windows.
   Proposed 4.5–6%, 9–12%, and GPU-hour ranges remain conditional scenarios.

## Repaired statistical and training protocol

Use before-target predictors, complete support, exact reconstruction and the
same coding history on both sides. For independent randomly sampled clusters,
estimate a stratum-weighted byte-saving rate and a cluster-bootstrap interval.
Only after stationarity and sampling assumptions are justified may a rate be
multiplied by the canonical length. Charge every actual asset multiplicity once.
Register untouched confirmation windows and the finite tested family; account
for multiple comparisons. Historical reused slices are exploratory evidence.

Per-window normalization `(weighted CE sum)/(batch weight sum)` is replaced
in new experiments by a fixed corpus normalization. For piece i selected with
probability p_i and weighted loss sum A_i, an unbiased with-replacement estimate
of J = sum_i A_i/W is the minibatch mean of A_i/p_i divided by known W. Piece
boundaries, context and resets define the objective and must match the declaration.

Continuation should restore optimizer state when available, or compare a slow
warmup with matched zero-moment controls; record useful targets and forward
tokens separately. Full-piece loss, representative sampling and BF16-grid
deployment precede rate or rarity-policy conclusions. A token-weighted sampling
plan must price its normalization correctly. Longer TTL experiments carry state
between BPTT blocks, detach gradients without wiping memory, and use episodes
longer than the memory horizon. Word-output tests need class coverage and a
jointly trained representation; the short frozen-core heads did not test that.

## Scope and execution constraints

Kaggle session 355888412 has four vCPUs, no GPU and about 31 GiB visible RAM.
The CLI authentication test succeeded for account `chaoscpp`; no credential
values were logged. Private CPU notebook commits are authorized. Outputs must
be explicitly preserved before each session ends.

The native CPU preflight and a dependent 9,437,184-byte sequential prefix run
were launched once. The latter predeclares a 1,048,576-byte warmup and 16 later
512 KiB windows. These are **early-region warm diagnostics**, not a complete
warm corpus or independent full-file strata. A connection failure must be
resolved by reading the existing manifests, never by launching duplicates.

A 55–60 hour single-thread full warm run cannot be completed inside an ordinary
12-hour Kaggle session just by submitting six notebooks. Independent notebooks
can parallelize configurations and replay, but splitting the file with cold
classical state would reproduce the flaw. A persistent CPU host or tested state
serialization is required for the complete production qualification. No paid
host has been rented. The user's GPU-session request comes after the CPU stage;
GPU-dependent experiments will be recorded separately rather than simulated on
CPU and called complete.

New importable code and mathematical tests live in `hutter_research/` and `tests/`.
The two Claude documents are preserved unchanged. The results registry, finite
96-idea scope and issue-by-issue repair ledger are the status authorities.
Historical reports remain dated evidence; they cannot prove current job liveness.
