# Stronger no-core-retraining descendant: contextual error memory

Status: specification only, registered6October2026 while the dictionary-atom v1 job is running. This file does not assert execution or a beneficial result. It is a different hypothesis from next-byte/next-word neighbor boosting. Reuse the canonical native exports; do not duplicate core inference. All95families remain open.

## Mechanism and causal sample selection

For each completed encoded atom retain its context-start hidden key h_i, its complete existing code a_i, and the native integer bit probabilities p_i,b actually used along that code. Store only observed probabilities, never counterfactual logits claimed from the observed path. In a query atom hold h_t fixed at its start. Before predicting bit b, the decoder already knows prefix beta. Donors are eligible only when their *completed historical* codes share beta and contain the next bit. Their historical y_i,b and p_i,b are consequently paired at the same prefix event as the query. Eligibility uses the decoded query prefix, not its unknown word or eventual length.

This differs from an oracle which selects a useful donor after observing the target: all donor ranking/weights and the correction are computed before the next bit. A future mutation must leave earlier queries invariant. Memory eviction occurs only after the target atom finishes. Literal/escape/root/partial-EOF paths retain explicit identity handling.

## Correct the residual rather than recreate the base distribution

Let l_i=logit(p_i,b/65536) and define nonnegative, normalized weights w_i from a current-prefix metric. A contextual intercept delta minimizes

    F(delta)=sum_i w_i [log(1+exp(l_i+delta))-y_i,b*(l_i+delta)]
             + (lambda/2)*delta^2.

For lambda>0, F is strongly convex:

    F'(delta)=sum_i w_i [sigmoid(l_i+delta)-y_i,b]+lambda*delta,
    F''(delta)=sum_i w_i sigmoid(l_i+delta)(1-sigmoid(l_i+delta))+lambda >=lambda.

The unique root can be bracketed and solved by safeguarded Newton/bisection. Since the first term of the derivative is in [-1,1], the root lies in [-1/lambda,1/lambda]. With a sign-preserving bracket of width epsilon, distance error is at most epsilon and objective excess is at most (lambda+1/4)*epsilon^2/2; verify the derivative and independent grid minimum on toy data. Empty donor set yields delta=0 exactly. The exported probability is Q16(sigmoid(logit(p_t/65536)+delta)). Its loss is a normalized Bernoulli loss, not an unnormalized word score.

An equivalent one-step Newton approximation at identity is

    delta_N = sum_i w_i (y_i,b-p_i,b/65536)
              / [lambda + sum_i w_i p_i,b/65536*(1-p_i,b/65536)].

It exposes the intuition: errors contribute signed innovation; confident correct predictions do not become misleading positive hints merely because their word occurs. This approximation is a separate registered arm, not the solved optimum. Both estimate a locally shared bias; neither is universally optimal for a nonstationary text process.

## Geometry, controls and predicted probability compatibility

Compute raw, centered or positive diagonal prefix-standardized key similarities in one current coordinate system. Consider

    unnormalized_w_i = exp(tau*cos_current(h_t,h_i)
                           -(l_i-l_t)^2/(2*sigma^2)).

A probability-compatibility factor reduces extrapolation from donors whose original coder confidence differs substantially from the current confidence. It is known from p_t before decoding. Choose K nearest *eligible* donors; normalize after selecting them. Prior means/variances and all stored pairs are prefix-reconstructed. Stronger subsequent variants can use the fixed unembedding's predictive/Fisher geometry, provided current hidden scaling and full normalization are reproduced; this remains design only.

Matched control: permute whole (code, observed p-path) value records among the same stored keys. Keep each historical outcome and its associated native probabilities together, preserving marginal calibration. Shuffling only targets creates artificial errors and is not an adequate residual-memory null. Also include global calibration, prefix-only error memory without hidden keys, recency, null memory and a matched cost/adaptation control. Store a variant selector if one is chosen offline; causal Bayesian selection still pays online regret, state and code.

## Capacity and resources

A word target's native path contains at most24 uint16 probabilities: at most48 bytes per row,512rows=24,576B in addition to the approximately464KB single-bank atom design. Prefix probability paths can instead use a small chosen fixed precision, but this changes feature statistics and needs an exact separate test. Existing model/dictionary memory should be reused. Full measured incremental RSS, main-process peak and single-core search time are hard gates. Do not simply add another bank to a baseline with only615,424B decimal-RAM headroom.

## Registered next experiment and promotion

First use corrected canonical A/B512K native exports already being generated. Fit no core parameters. Predeclare lambda in {0.25,1,4}, sigma=2, tau=100, K=8, FIFO512. The executable family has22sources: raw/centered/diagonal geometry × actual/paired-value-permutation × three lambdas (18), prefix-only deterministic eight-donor and recency eight-donor controls (2), and raw lambda1 one-step Newton actual/permutation (2). The prefix-only control selects by a fixed prefix/slot hash, without the hidden key. No hyperparameters are selected from confirmation. Charge discrete choice and code. The finite best root certificate is not a guarantee that its predictive distribution improves compression.

For efficient replay each row retains the original uint16 native p path plus **binary32 cached logit(double(p/65536))**. The root solves the explicitly approximated-logit problem, with double arithmetic and a checked derivative, and exports binary32 residual features. These numerical contracts are part of the experiment, not an assertion of bit equality with an unrounded ideal historical model. The original probability/outcome pair is retained for auditing. A packed-key bank including both paths/logits has a nominal177,160B design, before alignment/state and code; this residual needs no global atom count tree. The research parser still keeps a sorted code array for validity checks. Measure actual production peak separately.

The fixed causal Bayesian policies assign half prior mass to identity and half to four generic calibration candidates plus four residual strengths for each of22sources,93candidates total. Report global and24context policies separately, ideal regret and Q16 tax. Bounded A/B fitted generic/individual/joint logistic heads are separate from this zero-shipped-coefficient online alternative. Their box-optimum certificates concern the ideal fitted objective only. Candidate confirmation requires the same preliminary64B priced advancement gate; code/CPU/RAM/native gates follow rather than being waived.

Freeze all A/B choices before conditional C310M/D520M evaluation. Require at least64 preliminary bytes after any shipped coefficient/selector, then check incremental savings beyond generic and matched-null controls. This is a deliberately low initial screening gate, not a full package-cost threshold. A positive signal advances to a native arithmetic-coder implementation with unchanged internal core updates, independent decoding and wider warmed slices. Every promising combination is then ranked by total package, CPU and RAM, never by summed standalone percentages.

This descendant is falsifiable: if local errors are not predictably shared beyond base confidence/prefix, its new source loses to controls. That would reject this finite contextual-intercept branch. It would leave learned nonlinear conditional relations, persistent value-based retention, paid future-information latents and representation changes open.
