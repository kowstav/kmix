# Executable research ladder for the attached curriculum idea

6 October 2026. Design and budget controls, not a trained compression result. Canonical lexical preprocessing and full inverse are now exact. The original core GPU port still fails parity. Native features allow a separate residual predictor to be trained without that port. Spending remains $0; the total budget remains $70. Read the complete proposal assessment in `research_round8_attachment_assessment.md` alongside this document.

## 1. Train an explicit correction to the probability actually coded

For native coded bit t, retain p_t in integer units 1..65535, y_t, a prefix-visible feature vector z_t, reset/piece identifiers and exact stream offset. Let l_t=log(p_t/(65536-p_t)). A student produces a scalar correction d_theta(z_t), and q_t=sigmoid(l_t+d_theta). Evaluate the exported Q16 value floor(65536*q_t+.5), clamped to 1..65535. The training loss is the ordinary unweighted Bernoulli negative log likelihood of every retained useful event. Current observed surprise can prioritize training records; it cannot be an inference input for the current unknown target.

For fixed basis phi(z), d=theta^T phi, the objective is convex. Its gradient and Hessian are

    g=sum_t phi_t*(q_t-y_t),
    H=sum_t q_t*(1-q_t)*phi_t*phi_t^T.

Thus a feature has value through predictable *signed error*, rather than merely high frequency or spelling similarity. Around identity the approximate gain in nats is

    -g^T theta - .5*theta^T H theta.

A regularized step is theta=-(H+lambda*I)^(-1)*g. This connects error replay, associative rejection, grammatical placement and native mixer calibration. It does not prove that any particular feature has signal. The existing streamed bounded fits certify only their ideal continuous finite class, not quantized global compression or nonlinear training.

For a nonlinear residual begin with exactly zero output weights and a null gate, so the first exported prediction equals native identity. Keep core internal probabilities and update order untouched: the residual observes the native state and changes only the external arithmetic probability. Updating its state/weights occurs after the decoder obtains y_t. First implement the identical native inference equations and verify zero-update traces before optimizing.

## 2. Data contract and same-event cost mining

The immediate A/B audit uses 512KiB canonical cold slices. It attributes all code-path bits to dictionary atoms, literals, controls, escapes, synchronization and partial EOF. Dictionary word cost excludes its separate capitalization controls. A grammatical word list is a heuristic, not a POS analysis. XML tags and text are not automatically equivalent. All-code cost totals must reconcile. C/D candidate outputs stay untouched until the registered decision, except in a separately labeled amended/exploratory protocol.

For training gather broader native feature traces from exact legal pieces, retaining the production reset and prompt schedule. Do not attach old native priors to a synthetically changed prefix. Use real-data native features for supervised residual loss. Synthetic noun/constructor substitutions can initially train a separate auxiliary relation task, with explicit positive, negative and null cases; using them as actual core training examples requires regenerated tokenization, priors and states.

Use prefix-visible clusters (known word/code prefix, native confidence, previous completed word class, decoded markup role, recurrence/age, prior article-title state). Cluster selection and parameters are paid or deterministically reconstructed. Evaluate all activations, including false triggers. A singleton's zero empirical entropy is not a compression opportunity. Match final-bit costs with final-bit prequential losses; do not subtract conditional word entropy from a cost that also encodes class, case or alignment.

Separate article/block IDs for diagnostics and frozen confirmation. Training may ultimately overfit enwik9: the prize permits a corpus-specific model if all necessary model information is counted. Independent slices are nevertheless necessary to discover whether a proposed mechanism survives outside the examples that selected it. They are a reliability tool, not a requirement to optimize a different corpus.

## 3. Curriculum arms, with objective drift made measurable

First freeze record costs c_t=-log2 native_likelihood_t and define bounded priorities a_t=(epsilon+c_t)^gamma, clipped at a documented maximum. Mix the sampling law with uniform coverage:

    r_t=(1-rho)/N + rho*a_t/sum_j a_j.

R0 uses uniform real records. R1 samples r and multiplies loss by 1/(N*r_t), preserving the real-data objective in expectation. R2 deliberately omits this correction for an early curriculum phase, then finishes on uniform unweighted real records. R3 adds a prefix-valid synthetic auxiliary relation loss to R2; R4 adds retention/rejection supervision. Do not assume a later uniform phase repairs all bias. Measure per-class ordinary-event drift and actual unweighted native loss at every stage.

Match useful-event and compute budgets as well as exported parameter budgets. Repetition is not identical to weighting under Adam, clipping, batching and ordering. Freeze surprise-based priorities within a phase, log the sampler seed and optimizer state, and express warmup/decay in useful target events. The hard-example objective is an intervention arm, not evidence of better real-data coding.

The $12 pilot need not fund all five neural arms. Prefer R0/R1/R2 first, two seeds if affordable, and add R3 only after a measured positive interaction. R4 requires a demonstrated useful memory donor pool; do not train a selection network for donors that contain no conditional signal.

## 4. Small architectures before expensive core finetuning

Architecture A: a bounded convex final-bit adapter with a fixed low-rank interaction basis. Include native l, byte bit position, atom depth, markup/constructor state, a compact neural-state sketch, paired past error, donor age and confidence compatibility. Compare equal-size generic, permuted-pair and random-projection controls. This is an auditable CPU option and gives a stronger baseline for neural curriculum.

Architecture B: a 16-cell recurrent residual, updated after each coded bit, with a small fixed/provable feature sketch. Use one shared recurrent state plus article-local state or a decoded reset flag rather than a large hidden key/value bank. Initialization to exact identity, float arithmetic order, reset flags and the online update schedule are codec contracts. Quantized inference and the exported container must be used during final validation. Width is a test dimension, not a promise that 16 cells suffice.

Architecture C: a sparse causal relation memory. Store completed words/codes and paired native probabilities/errors. Estimate a correction conditioned on the already decoded target prefix; gate it using relation type, confidence, distance and a null alternative. Retention optimizes realized future-use value from earlier decoded events, with deterministic eviction. Offline learned parameters and discrete policy choice are paid; future usefulness cannot be read from the current undecoded suffix. The running contextual-intercept experiment is the no-core-retraining precursor to this architecture.

Constructor/content-first architecture is a separate reversible codec. First decode/pay content tokens, block boundaries, slot counts, literals and a grammar skeleton. Then both left/right content anchors are available to infill the ordered constructor sequence. Its objective is L(content,slots)+L(ordered gaps|decoded content)+L(remaining exact corrections)+L(decoder/model). An unordered set of constructors loses order and multiplicity; it requires an explicit residual. Compare with ordinary sequential coding using an equal model-byte budget. Synthetic infill training alone does not pay these representation costs.

## 5. Package frontier and promotion gates

For candidate residual size B_theta per copy, code increment B_code and other assets B_other, require full realized gain

    sum_t log2(q_t(y_t)/p_t(y_t))/8
       > 2*B_theta + B_code + B_other.

The factor 2 is the current package's duplicated-weights convention, not a universal law; an alternative package needs a measured new ledger. Once a model is chosen, its coefficients are paid once per stored copy over the full file. Subtracting them from a 1MiB screen is a conservative screening rule, not proof of negative full-file gain. The existing 64B development advancement rule remains the registered rule for its finite experiments. An amended weak-signal branch must be predeclared and use fresh pieces or honestly label previously seen checks exploratory.

For a full-file mean bit gain r and canonical T=587,138,826, break-even is r > 8*(2*B_theta+B_code+B_other)/T. Correlated bit events require article/block resampling for uncertainty, not an IID bit-level standard error. Cold slices cannot establish the warmed rate or full CPU/RAM. Report every actual package cost; do not scale a short-slice percentage and call it achieved compression.

The newer pending 95,914,051B reference needs <=76,731,240B for a strict >20% reduction. At fixed C3 assets, the needed payload is <=69,976,946B, 22,582,510B below the preserved C3 payload. That is approximately .307695 additional bits saved per canonical WRT byte. It is a target, not an estimate of what these architectures can deliver.

## 6. Keep the existing $70 ceilings

| Stage | Maximum dollars | Release condition |
|---|---:|---|
| Environment/export readiness | 4 | Exact unchanged residual export, causal/reset tests, host/compiler compatibility |
| Controlled residual pilot | 12 | Native feature provenance; useful-event budget; R0/R1/R2 controls |
| Best continuation | 36 | Positive independent native incremental gain with actual serialized size |
| Export/native qualification | 8 | Quantized exact decoder and package accounting; CPU/RAM checks |
| Contingency | 10 | Needed repair or preservation; no automatic budget expansion |

Before renting, query live offers and record total hourly compute plus storage/bandwidth, driver compatibility, disk, expected transfer/setup time and measured useful-event throughput. Budget hours are cap/total_cost_per_hour, not GPU price alone. Perform a short throughput test and stop at the cap. No current price is assumed. Compare one GPU with additional cards by useful events per dollar and startup overhead; a small residual need not use a 5090. Kaggle's free session remains the first option for finite prototypes.

Core finetuning is still gated by native/GPU fidelity, zero-update container export and a lambda-zero continuation that preserves baseline loss. Only then sweep actual-rate penalties against final native payload. The new competitor's published long training chain is not evidence that a comparable scratch run fits this $70 budget. Warm starting a compatible checkpoint is a distinct experiment. No paid training has started and no before/after compressed-size forecast is justified.
