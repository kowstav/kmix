# Round 8: conditional combinations with a frozen core

Registered 6 October 2026, session 355655943, before these new results. This is an active research branch, not an assertion that the 95 idea families are exhausted. Original checkpoints/data are preserved. No rental or deletion is authorized by this protocol. Online statistical updates below are adaptation without neural retraining.

## Hypothesis and distinction from round 7

The old fixed-strength relation/placement screens did not optimize a conditional joint predictor. A relation may help only at particular WRT prefixes, uncertainty bands or grammatical states; unconditional addition can double count evidence already in cmix. Test hierarchical Bayesian specialization of two residual signals, including interactions, against identical-size generic and random-relation models. A positive signal is discovery evidence; total native archive and executable cost are the promotion criterion.

For native final probability p_t (uint16 / 65536), and two prefix-derived residuals a_t,b_t, use the finite, explicitly declared candidate family

q_theta,t = Q16(sigmoid(logit(p_t)+theta_a a_t+theta_b b_t+theta_ab tanh(a_t)tanh(b_t))).

Also include exact identity, intercept +/-0.125 and temperatures 0.9/1.1. Identity must return the original integer without a floating round trip. The 25-arm family consists of identity, four generic corrections, four a-only strengths (-0.125,0.25,0.5,1), four b-only strengths, nine joint positive strengths from {0.25,0.5,1} squared, and three interaction corrections with (theta_a,theta_b)=(0.5,0.5) and theta_ab in {-0.5,0.5,1}. Every q is positive and normalized. Negative individual strength is retained to test evidence already absorbed by the core. The interaction family is finite, not an optimal arbitrary nonlinear predictor.

The source residual is log(e_1/e_0)-log(g_1/g_0) along the currently decoded dictionary-code bit tree, clipped to [-8,8], zero where both lexical child branches are not available. e and g are normalized dictionary mass models from the preserved causal observer. This does not invent the full counterfactual word distribution of the core. Non-lexical bits, cases, escapes and partial EOF prefixes are included in the score.

## Hierarchical gate and complexity price

Partition contexts in this fixed order: bit position (8), base probability band (8), parser state (5), preceding punctuation class (4), preceding completed word class (3), and completed-event age band (4). There are at most 20,873 nodes; child arrays are bounded and there is no target-dependent selection or eviction. The gate prior is 1/2 on stopping at an internal node and 1/2 on continuing to the relevant child. At each node, the local mixture has prior 1/2 on identity and 1/48 on each of its 24 other candidates. Update posterior likelihoods only after the decoded bit. Unseen children have their proper initial local mixture.

Let ell_v be the cumulative log likelihood of the local mixture, and s_v of the visited child mixture. Its stopping probability is sigmoid(ell_v-s_v). Its pre-observation prediction is r_v=w_v r_local+(1-w_v)r_child. Leaves always stop. Compute predictions bottom-up, then update each visited likelihood using its saved pre-observation prediction. Update local candidate likelihoods after all predictions are saved.

For exact real internal arithmetic, this equals a Bayesian mixture over context-tree prunings and leaf candidate assignments. Hence L_tree <= L_T,theta - log2 pi(T,theta), where the prior charges each split/stop and each leaf's candidate. This guarantee covers the specified finite class; it does not establish a global optimum. Final Q16 rounding changes codelength: record its actual cumulative tax separately rather than silently applying the ideal bound to a quantized coder. Binary construction/compiler/ABI determinism and native range-coder rounding remain separate gates.

## Registered arms and controls

- generic: a=1,b=clipped native logit; same 25-arm budget and identical hierarchy.
- random_plus_run: a=rank/length-matched deterministic random-word echo residual,b=constructor-run residual.
- grammar_joint: a=coarse syntax residual,b=constructor-run residual.
- geometry_plus_run: a=integer moment-neighbor residual,b=constructor-run residual.

All four run on the identical decoded prefix and native probability trace. Also record their global mixtures, every fixed candidate, tree quantization tax, context count, per-interval gains and excess over the generic/random controls. Keep complete source and binary hashes, wall/user/system time and peak RSS. No target-based gate, future page, target POS, or target word length may enter a prediction.

## Sequence, go/no-go, and stronger descendants

1. Compile with g++ -O3 C++17; independent exact small-sequence mixture enumeration must match hierarchical predictions. Test quantizer/identity, normalization, posterior update order, prefix noninterference, parser completion, cases/escapes and partial-code EOF. Use an independent Python rational/finite-pruning reference, not only copied C++ assertions.
2. A/B 32 KiB integration pilot; abort on invalid parsing/probability/bit accounting, nonfinite likelihood, or memory overflow. Resource or scientific failure is preserved, not overwritten.
3. A/B full 2 MB development slices with all four arms. C/D are already examined slices: label confirmation, not untouched holdout. Do not cherry pick a family with whole-data hindsight and omit its selection cost. A native candidate needs a specific frozen configuration and package-level margin, not just oracle savings.
4. If improvement has a credible margin, choose new unexamined G/H slices from the full old-FX2 stream, generate actual native traces and archives. Existing E/F have been examined and cannot be claimed as new holdout.
5. Integrate the winning compact gate into actual encoder/decoder, preserving the core's decoded-byte update trajectory. Compare exact archive bytes, zero-strength archive identity and independent-process decode. Traces are research artifacts, not supplied to the decompressor. Verify executable/model/dictionary duplication as actually packaged; RAM/startup and full CPU time must satisfy official rules before a qualifying claim.

Potential descendants, contingent on data: learn context ordering with priced description; change generic coarse syntax to bounded variable-order suffix models; combine lag/hazard and relation mass via the same conditional gate; replace static spelling neighbors with prefix-learned associations; use an occurrence-independent global control to distinguish mere recalibration. If the signals have no conditional information, increasing gate complexity cannot produce information; inspect residual cost strata and build a different causal signal. No family is marked fully explored on the basis of this screen.

## Scope limits

The traces are cold-start old-FX2 slice inputs under the C3 lexical predictor, not the full production lexical order. Parser is a decoded ASCII observer; target full-POS infilling requires a separately paid ordering/representation. Calibration savings can dominate a semantic arm; only the incremental difference over matched controls can support that mechanism. These runs do not prove a 20% dataset or package improvement.
