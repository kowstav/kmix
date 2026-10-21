# All96 idea families: execution and remaining-work ledger

Generated 2026-10-06T19:39:14.636692+00:00. Session355735431. No family is claimed fully explored.

This preserves the round1–7 audit and round8 evidence. Shared infrastructure is credited only to the finite subcase actually implemented. Read the source/result files for executed hyperparameters.


## A01 — Render text to images and recover it by OCR — rounds 1, 3, 7

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 3.

**What rigor was actually evidenced:** Correct information-preservation objection and rough model/CPU economics; reported small raster/OCR screens. No mature neural OCR codec or optimized renderer/residual architecture is evidenced. E1, E2, E8.

**Actual testing versus required testing:** Round 1 reports image/pixel forms worse than zlib. Round 3 emphasizes symbolic geometry instead. A fair literal OCR test needs an injective representation or explicit correction stream, renderer/font and OCR bytes, exact reconstruction, and matched text/raster models and CPU. M1–M3 apply. The cheap screen reasonably lowers priority; it does not prove every visual predictor impossible.

**Combination work evidenced:** Geometry was combined with other features, but a trained OCR predictor plus correction coder was not jointly optimized. No per-idea thinking hours are documented.

**Stronger descendant to implement:** Use a symbolic glyph-equivalence predictor on decoded history before funding image reconstruction; require measured conditional benefit over byte classes.

**Discriminating experiment:** Separate representation codelength from prediction gain; compare render features with the same-size random and symbolic channels.

**Combination partners:** A05, A84. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A02 — Low-resolution glyph codewords plus ambiguity residuals — rounds 1, 7 proposals

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 3.

**What rigor was actually evidenced:** The idea file explains why blur transfers information into corrections. That is a valid constraint, not a measured optimum. E8.

**Actual testing versus required testing:** The earlier report groups low-resolution/pixel attempts without a recoverable separate ledger. Specify the glyph alphabet, collision classes, exact byte/case/Unicode escape, and learn a joint glyph/residual distribution. Compare its complete codelength against a symbolic class/residual codec at equal cost. Do not count discarded ambiguity as compression.

**Combination work evidenced:** Conceptual connection to shape classes exists; no recorded optimized glyph-plus-residual system. This remains a low-priority alternative, not a completed architecture rejection.

**Stronger descendant to implement:** Choose collision classes by paid minimum-description-length partitioning; encode ambiguity with a calibrated conditional residual rather than hope OCR recovers it.

**Discriminating experiment:** Optimize class alphabet and collision correction jointly; count renderer/font, case, Unicode and every escape.

**Combination partners:** A05, A85. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A03 — CNN or other spatial predictor over rendered decoded history — original idea variants

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route T; priority 3.

**What rigor was actually evidenced:** Compute concerns were discussed; no explicit trained causal CNN result is identified. E8.

**Actual testing versus required testing:** Geometry lookup and shape tables are not a CNN. Define deterministic rendering of past context, fixed causal crop/padding and output probabilities; compare a same-budget character CNN and random spatial encoding. Price render/startup cost and every output. A tiny pilot can evaluate whether spatial inductive bias pays before writing a large system.

**Combination work evidenced:** Listed as an alternative expert, not integrated with the transformer/final coder. No evidence of architecture or kernel optimization for this variant.

**Stronger descendant to implement:** Distill a causal spatial-history expert into a tiny symbolic residual if useful; preserve an ordinary character-CNN capacity control.

**Discriminating experiment:** Train identical compute/parameter budgets with glyph versus shuffled geometry; test native cost and an actually smaller distilled export.

**Combination partners:** A06, A83. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A04 — Glyph features and factorized character embeddings — rounds 1, 3; idea 2

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 3.

**What rigor was actually evidenced:** Multiple seeds and random/identity controls in round 3 were better than the initial 400-step screen. The tiny 256-byte embedding saving was recognized. E1, E2, E8.

**Actual testing versus required testing:** Geometry residual gains were approximately 0.105–0.106%, versus random 0.080% and identity 0.072%; attributed incremental signal was about 0.0004 bpb. Test fixed glyph versus equal-rank random/learned projections with matched extra parameters; separately test an actually factorized embedding's stored size. M7 prevents claiming redundant glyph features add information.

**Combination work evidenced:** Geometry was tested alongside residual modeling and classical contexts. It was not extensively co-designed with the later learned word-relation/placement architecture.

**Stronger descendant to implement:** Treat glyph features as a low-rank parameter-sharing basis, then learn a small residual for directions outside that basis.

**Discriminating experiment:** Separate table/model-byte savings from fixed-feature prediction; compare equal-rank random and learned factors.

**Combination partners:** A16, A68. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A05 — Shape-class-first hierarchy and integer shape contexts — rounds 1, 3

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 2.

**What rigor was actually evidenced:** Explicit shape→character factorization and classical comparisons; partial model matching. E2, E8.

**Actual testing versus required testing:** Geometry-context CM scored 1.853 bpb versus random 1.847 and handmade classes 1.842; shape-first 1.917 versus 1.889 baseline, with random shape-first 1.925. Those are particular class choices. Optimize class alphabet/count smoothing and residual distributions under actual class-table cost; compare with ordinary character n-grams in the same mixer and measure CPU.

**Combination work evidenced:** Hierarchical and residual versions were compared, but class design plus stronger learned syntax/word models was not jointly trained. Rejecting these layouts is supported; rejecting every useful character grouping is not.

**Stronger descendant to implement:** Optimize a character-class hierarchy using paid partition decisions and conditional residual counts; do not freeze handmade shape classes.

**Discriminating experiment:** Enumerate a small finite class family with charged selectors; evaluate all literals and matched Markov/CTW controls.

**Combination partners:** A06, A89. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A06 — Confidence-gated orthographic/glyph residual expert — rounds 1, 3, 7

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Valid causal mixture/logit correction equations; small residual screens. The full proposed feature set and learned gate have not been implemented together. E2, E8, E9.

**Actual testing versus required testing:** Early hard-word/shape specialists and later fixed geometry boosts are substitutes for a learned context-dependent residual. Train a compact model using preceding spelling, prefix/suffix, parser state and baseline uncertainty, with all false alarms in normalized loss. Include identical-capacity generic-feature controls and final-bit supervision; freeze/export and confirm natively. A target's observed error cannot select its own gate.

**Combination work evidenced:** Proposal-level synthesis is substantial; tested joint learned orthography × syntax × uncertainty interactions are missing.

**Stronger descendant to implement:** Replace unconditional geometry boosts with an uncertainty-and-parser-conditioned hierarchical gate, then learned residual features if the fixed signals fail.

**Discriminating experiment:** Current conditional_gate_v1 tests the gate; next isolate relation-only, grammar-only and interaction increments over generic calibration.

**Combination partners:** A79, A82, A84. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.


## A07 — Feed additional classical-model predictions into the neural expert

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** The idea file identifies existing signals as inexpensive candidate inputs. No comprehensive input-ablation study is recorded. E8, E17.

**Actual testing versus required testing:** Mixing neural and CM outputs is not training the transformer on extra classical channels. Collect causal model distributions/states, specify their quantized interface, and compare PPMD-only, selected extra channels and equal-width/random controls. Measure extra inference/serialization cost and final coder gain. The baseline update order must expose the signal before the predicted bit.

**Combination work evidenced:** Discussed as a way to reuse already computed information; no recorded trained multi-signal model. Its dependency is native feature collection, not necessarily a full replacement transformer.

**Stronger descendant to implement:** Reuse native classical channels in an external residual first; a later neural input adapter must be initialized to exact identity.

**Discriminating experiment:** Collect pre-update classical probabilities; distinguish extra channel information from equal-size extra residual capacity.

**Combination partners:** A42, A84. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `sequence`: COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN; PID1464. Eight widths/kinds, finite rungs and fixed64-byte block context. Does not implement every shared controller, architecture or long memory.


## A08 — Sorted dictionaries and reversible 2D/aligned symbolic organization — rounds 1, 4, 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 2.

**What rigor was actually evidenced:** Sorting/storage probes and several word-code groupings; no optimized alignment transform with complete reconstruction metadata. E1, E3, E4, E8.

**Actual testing versus required testing:** Round-1 sorted forms lost; round-4 prefix/suffix/distributional groupings improved toy neural loss; round-5 dictionary front-coding grew. These test different objects. A genuine aligned-text codec must preserve occurrence order, row/column placement, exact spelling and exceptions, then train its predictor on that representation. Compare total streams/model cost, not dictionary bytes alone.

**Combination work evidenced:** Word grouping plus letter embeddings was implemented. The broader spatial/alignment transform plus matched neural decoder was not. Do not merge their conclusions.

**Stronger descendant to implement:** Search reversible symbolic alignments with explicit placement/order residuals; preserve the old representation as a selectable component.

**Discriminating experiment:** Count row/column ordering and boundary metadata; a dictionary-only saving is not a text-stream saving.

**Combination partners:** A29, A44. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A09 — Wordle/progressive feedback, multiple proposals and feedback alphabets — rounds 1, 3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 2.

**What rigor was actually evidenced:** Feedback costs, decoder determinism and reversible-refinement mathematics were addressed; equal-model-call comparisons were useful. E2, E7.

**Actual testing versus required testing:** Reported 3/5/9-call Wordle schemes lost 4–20% against parallel character decoding with the same calls. Small early PCC screens also lost. Define full feedback alphabets, rejection/termination and residual probabilities; train on the exact reachable refinement states and optimize a registered proposal policy. Compare richer feedback, binary locks and rank coding at matched CPU/model cost. The single-byte identity explains no inherent advantage, not universal practical failure.

**Combination work evidenced:** Feedback versus direct reveal and skeleton variants were compared. The article retrieval + shared heads + masked decoder proposed in the file was not implemented as a jointly trained system.

**Stronger descendant to implement:** Replace repeated proposal feedback with a normalized multi-proposal prefix code and a paid stopping rule.

**Discriminating experiment:** Charge every wrong guess and feedback symbol; verify coder versus cross entropy and compare optimal direct symbol coding.

**Combination partners:** A13, A14. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A10 — Confidence-ordered any-order/bidirectional decoding — rounds 1, 3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 2.

**What rigor was actually evidenced:** Deterministic position selection and matched decoded-state training were studied. The search over schedules/architectures was limited. E2, E7.

**Actual testing versus required testing:** At 2,500 steps, L2R 1.703 versus block4 2.099, block16 2.450, block64 3.922 bpb. Small own-training-text models also favored L2R. Test optimized schedule entropy/ties, actual reachable state distribution, causal masks for what is decoded, positional design, blockwise caching and multiple paired training budgets. Demonstrate convergence of the comparison rather than assume it from 20 passes. Full right-context information must be paid first.

**Combination work evidenced:** Blocks, skeletons, adaptation and warm starts were explored. No mature bidirectional model with article memory, shared heads and production decoding kernels is evidenced.

**Stronger descendant to implement:** Use paid blockwise ordering with a prefix-reconstructible mask, or a proper latent-variable marginal; never choose confidence order for free.

**Discriminating experiment:** Expose exact decode states and order bits; compare endpoint infill with a separately optimized causal model, including positions.

**Combination partners:** A56, A88. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A11 — Structure/skeleton first, article/block hierarchy and shared heads — rounds 1, 3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 1.

**What rigor was actually evidenced:** Classical and neural skeleton splits were tested. The full hierarchy/shared-network proposal remained only partly represented. E2, E7.

**Actual testing versus required testing:** Classical skeleton costs 1.942–2.000 versus 1.864; stronger skeleton 1.905. Letters became 9.7% cheaper while spaces became 51% more expensive. A fair architecture test jointly optimizes structure, positions, capitalization, markup, residuals and a shared conditional decoder. Measure all streams under M3; compare separately trained heads versus shared heads and charge schedule/state cost.

**Combination work evidenced:** Skeleton + masked prediction/adaptation was tried. Article-level state plus paid structure and retrieval was proposed, not realized. These failed skeleton choices do not exhaust hierarchical factorization.

**Stronger descendant to implement:** Let grammar choose between original sequential coding and skeleton/content factorization per block, with an explicit selector.

**Discriminating experiment:** Use total skeleton, length, case, literal and content costs; optimize block granularity under actual headers and decoder size.

**Combination partners:** A85, A88. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A12 — Word length first with separate/shared structural heads — round 3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 2.

**What rigor was actually evidenced:** Two seeds, explicit length/punctuation/letter costs and classical-blend comparisons constitute a useful focused study. E2, E7.

**Actual testing versus required testing:** Mean neural improvement about 0.77%; final weak-classical blend worsened about 0.20%. The length model saw roughly 15% fewer training bytes. Match raw-text exposure and exact length/case/escape cost, compare shared-head versus independent structure parameters, then evaluate a real final coder. A standalone neural gain is insufficient.

**Combination work evidenced:** Length + classical blend was tested. The proposed length + scratch + TTL + length-aware CM combination was not run, although the report recommended it.

**Stronger descendant to implement:** Model word-ending hazards in the existing prefix tree instead of inserting an unpriced word-length channel.

**Discriminating experiment:** Compare charged length-first coding with tree stopping probabilities; include unseen words, all escapes and partial EOF.

**Combination partners:** A67, A70. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A13 — Whole-word proposals, candidate-rank coding and spelling fallback

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** A plausible rank/escape factorization was specified. No direct mature candidate-rank codec result is recoverable. E7, E18.

**Actual testing versus required testing:** Two-token dictionary groups and later word-tree experts are related, not equivalent. Specify a deterministic prefix-derived ranked candidate set, normalized rank/escape probabilities, exact spelling/case fallback and candidate-search cost. Compare direct word softmax/tree coding, ranked proposals and iterative refinement using the same word features. Misses and selector bits count.

**Combination work evidenced:** Conceptual morphology/retrieval/rank/fallback pipeline exists; no measured end-to-end combination. It should not inherit Wordle's negative result without its own test.

**Stronger descendant to implement:** Use a bounded decoder-built candidate list plus exact spelling fallback; rank probabilities and fallback probability must normalize together.

**Discriminating experiment:** Measure actual cumulative rank/fallback bits, list reconstruction time and tail coverage against the final coder.

**Combination partners:** A67, A70. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_softmax`: COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN; PID2297. Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.

- Round9 `word_softmax_descendant`: COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN; PID2512. Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.

- Round9 `word_warmstart`: COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN; PID2752. Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.


## A14 — Train on decoder-reachable states; autoregressive warm start

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 1.

**What rigor was actually evidenced:** Round 3 explicitly addressed train/decode mismatch, which is valuable. Optimization depth remained bounded. E2, E7.

**Actual testing versus required testing:** Decoded-state matching improved a losing family from 2.633 to 2.485 bpb. Warm-start plus 1,000 steps remained worse than the L2R control. Test on-policy decoded-state sampling, schedule curricula, joint structure/content objectives and equal useful-target/compute controls; ensure warm-start position/mask distribution and optimization are compatible. One failed warm start does not exclude pretrained adaptation.

**Combination work evidenced:** Matched states were combined with skeleton/any-order models. No longer, multi-seed, jointly tuned retrieval/skeleton training followed.

**Stronger descendant to implement:** Generate the training distribution from the actual decoder policy, with a teacher-forced identity bridge and gradual exposure to changed states.

**Discriminating experiment:** Audit position/mask/reachable-state frequencies; validate old loss before optimizing a new order.

**Combination partners:** A10, A93. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `core_long`: COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT; PID2064. Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.


## A15 — Hard-word specialists and targeting cumulative residual cost

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 1.

**What rigor was actually evidenced:** Early reports identified rare names, first letters and long-distance repeats; round 7 used actual final-bit attribution. That diagnostic rigor improved substantially. E1, E3, E9.

**Actual testing versus required testing:** Round 1 reports roughly 1% specialist gain on a weak base. Later atlases show frequent known words can dominate aggregate bits. Rank total final-coded cost, not rare types or striking examples. Train a causal specialist with a confidence gate and all misses, compare generic capacity, and check whether named difficult categories retain gain after the final mixer. Diagnostic target labels cannot become inference features.

**Combination work evidenced:** Diagnostics informed cache and word-model proposals. A residual-cost-trained full lexical specialist has not been executed.

**Stronger descendant to implement:** Allocate specialist capacity by cumulative excess final-bit cost and reuse frequency, with a paid selector and generic control.

**Discriminating experiment:** Use predeclared cost strata, not just rare-word counts; report false activations and conditional gain per stored byte.

**Combination partners:** A64, A91. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A16 — Capacity per stored byte: float, Q4, Q3 and ternary networks — rounds 1–2

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route T; priority 2.

**What rigor was actually evidenced:** Matched data/steps and a capacity/storage table; actual exported file/coder/CPU comparison is missing. Early halfway quantization was especially weak. E1.

**Actual testing versus required testing:** Round 2 reports 6.3M Q4 1.516 bpb, 8.5M Q3 1.537, 14.9M ternary 1.477, 14.9M float 1.393. “Equal size” used nominal budgets, while entropy estimates differ. Train matched rate–distortion frontiers, export every asset, benchmark real ternary sparse/add kernels and compare complete package at eligible CPU time. Parameter multiplication is not free.

**Combination work evidenced:** Ternary + online adaptation + weak CM was tested. Optimized ternary kernels and later production-core retraining were not completed.

**Stronger descendant to implement:** Optimize the measured rate-versus-payload frontier over codebook size, scale precision and architecture width, using actual containers.

**Discriminating experiment:** A larger lower-bit model must beat equal-byte controls after CPU/RAM and duplicated assets, not merely neural perplexity.

**Combination partners:** A43, A90. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A17 — Exact weight entropy coding and conditional tensor codecs — rounds 2, 5, 7

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Strongest on the exact older-FX2 round-7 component: all tensors, independent loaders and native probability/archive identity. Initial generic entropy proposals were only estimates. E1, E4, E11.

**Actual testing versus required testing:** Round 5's simple row/column contexts mostly lost; generic round-7 alternatives were at best 289 bytes larger. Reproducing the published C5 tensor/histogram/column codec saved 28,200 bytes/copy; added packed loader 768/copy leaves 54,864 bytes for two copies. Actual lexical C3 grows 940/copy. Preserve checkpoint-specific results; complete production packaging/PGO remains necessary. Credit the published codec rather than call its reproduction a new architecture breakthrough.

**Combination work evidenced:** Exact packing was combined with BF16 variants and a loader-size screen. Its savings cannot be added to an incompatible lexical checkpoint.

**Stronger descendant to implement:** Search universal tensor partitions, scale-conditioned priors, causal bit planes and predictive index deltas with priced mode selection.

**Discriminating experiment:** Current weight_partition_v1 tests the best dyadic row/column partition; only a complete exact container can be promoted.

**Combination partners:** A40, A41, A43. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `core_pipeline_profile`: WAITING_FOR_CORE_DISTRIBUTED_V2; PID2780. Queued zero-update raw/redacted E/F controls plus unchanged-weight packed training throughput, explicit per-document KDA/convolution/attention/RoPE isolation and foreach optimizer comparisons. lr0 and resident batch; not5090, CPU codec timing or improved archive.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.

- Round9 `model_order`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Recover original container tensor order and independently verify all native reader tensor bytes. Adaptive weight-code order changes must not be confused with training. Native identity permits compositional reuse of the already independently decoded archives.


## A18 — Longer windows, sparse long-range attention and match-fed context — rounds 2–3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 1.

**What rigor was actually evidenced:** Residual-distance atlas and a 2,048-context run; no broad attention/caching design study. E1, E2.

**Actual testing versus required testing:** Rare repeats 512–2,048 bytes back improved 15.4→10.3 bits; overall 1.509 versus 1.483 bpb worsened with changed training circumstances. Match useful exposure and optimizer, then compare larger window, sparse long-range links, recurrent summaries and match-model inputs under equal inference cost. Optimize masks and positional encoding for the extended context.

**Combination work evidenced:** Longer-context observations motivated TTL/cache studies. Sparse attention and a trained match-fed transformer remained proposals, not completed alternatives.

**Stronger descendant to implement:** Make long context a sparse persistent summary with a measured value per CPU/RAM byte; frozen native summaries precede new attention training.

**Discriminating experiment:** Compare equal-memory recency, random retrieval and content summaries; include construction/search cost and warmed-history behavior.

**Combination partners:** A25, A71. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A19 — Full-network decoder-side online adaptation — rounds 2–4

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 2.

**What rigor was actually evidenced:** Decoder-reproducible updates after observed windows and several learning rates; exact CPU/export trajectory remains unverified. E1, E3.

**Actual testing versus required testing:** Float 1.483→1.463, ternary 1.477→1.436 with lr 1e−5; larger rates hurt. Later dictionary adaptation stacked with caches. Implement native update order, starting quantized weights, optimizer state/precision and rescaling identically; price backward passes and storage/RAM. Compare learning schedules at fixed CPU rather than assume the GPU gain qualifies.

**Combination work evidenced:** This is a genuine combined line of inquiry with CM, caches and kNN. It was not optimized into a measured CPU-constrained submission.

**Stronger descendant to implement:** Constrain online adaptation to a deterministic trust region around frozen identity; test statistical residual updates before full neural updates.

**Discriminating experiment:** Verify decoder reproducibility, catastrophic drift, update-time overhead and true full-history amortization.

**Combination partners:** A20, A21. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A20 — Selective adaptation: output head, norms, last MLP/layers — rounds 2, 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 1.

**What rigor was actually evidenced:** Actual production-related head and deeper adaptation code; selective choices were limited. E4, E13.

**Actual testing versus required testing:** Head improves neural loss 0.63% but native archive only 194,669→194,626 bytes. Head + last MLP improves neural loss 0.77% with about 10% added CPU. Test causal gradients and low-rank/norm subsets at equal update time, and assess complete final-coder costs on multiple warm strata. “cmix already does this” is an interpretation of these arms, not a theorem about adaptation.

**Combination work evidenced:** Added to the existing coder; not jointly optimized with learned lexical residuals or a changed base model. Production time headroom can reasonably limit further investment.

**Stronger descendant to implement:** Prefer a low-dimensional final-bit adapter with fixed core features; merge or serialize only an adapter that passes the native objective.

**Discriminating experiment:** Use neutral and equal-capacity generic controls, and measure both offline fitted bytes and zero-shipped-parameter online adaptation.

**Combination partners:** A84, A92. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A21 — Fast article deltas, two-timescale adaptation and reset policies — round 5

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Implemented variations on a slow delta, but a narrow schedule/state search. E4, E13.

**Actual testing versus required testing:** Fast and two-timescale variants reportedly worsened. Specify reset/momentum/carry rules and compare equal update work, regularized fast state, slow shared state and meta-learned initialization. Use held-prefix updates and candidate's own mixer state. A losing untrained fast branch does not disprove a trained adaptation policy.

**Combination work evidenced:** Adaptation timescales were combined experimentally. No architecture-level meta-training or learned article controller is recorded.

**Stronger descendant to implement:** Learn when an article-specific correction should decay or reset, with a global backoff and paid reset policy.

**Discriminating experiment:** Compare abrupt reset, learned hazard and two-timescale updates under actual final-bit loss; no future article length.

**Combination partners:** A25, A66. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.


## A22 — Neural adaptation plus classical context mixing — rounds 2–4

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Actual factorial-style comparisons show overlap and stacking; early CM is explicitly weak. E1, E3.

**Actual testing versus required testing:** Ternary frozen 1.477, adapted 1.436, adapted + CM 1.405; frozen + CM 1.421. These are useful toy results. Repeat with equal stored/model cost and an actual strong final coder, including neutral integration and CPU. Decompose whether adaptation supplies information not already recovered by the stronger mix.

**Combination work evidenced:** Yes, this combination was implemented and measured. That evidence is much stronger than a claim that every later proposal received the same treatment.

**Stronger descendant to implement:** Model residual evidence relative to the final native mixture, with jointly learned gates instead of adding standalone model gains.

**Discriminating experiment:** Compare classical-only, neural-only, external gate and joint mixture; keep identical core update order.

**Combination partners:** A42, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `sequence`: COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN; PID1464. Eight widths/kinds, finite rungs and fixed64-byte block context. Does not implement every shared controller, architecture or long memory.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.


## A23 — Carry transformer state across article boundaries — round 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** A frozen state-carry intervention, not a model trained for the new boundary semantics. E4.

**Actual testing versus required testing:** Reported +11.8% / +1.2% loss on two slices without finetuning. Train a matched carry/reset model, inspect state stability, and compare summaries/retrieval with the same boundary information. Preserve actual causal order and document piece resets. The negative test supports rejecting that frozen intervention; it does not reject learned cross-article memory.

**Combination work evidenced:** Limited to state carry within the existing pipeline. A trained cross-article architecture plus lexical gating was not executed.

**Stronger descendant to implement:** Use bounded cross-article state with deterministic selective reset based only on decoded markup and earlier titles.

**Discriminating experiment:** Test a warmed native stream, reordered exact inverse and reset controls; cold slices cannot settle full-history memory.

**Combination partners:** A27, A95. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A24 — Empty/register scratch slots — round 3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route T; priority 3.

**What rigor was actually evidenced:** Explicit empty versus memory-content controls were a good design decision. Short single-run rankings remain uncertain. E2.

**Actual testing versus required testing:** Plain 1.7439, 128 empty 1.6981, 256 empty 1.7235 bpb after 2,500 steps. Compare equal parameter/compute models, multiple paired seeds, different register placement and longer training; measure whether added capacity or architecture explains the gain. Price registers' parameters and operations.

**Combination work evidenced:** Scratch + keep-alive memory was actually built. Register count and content-model design were not brought to an optimized long-training frontier.

**Stronger descendant to implement:** Convert scratch registers into compressed persistent latent memory with a null-write gate and an explicit compute budget.

**Discriminating experiment:** Compare empty slots, matched ordinary state capacity and random writes before interpreting any learned memory gain.

**Combination partners:** A80, A83. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A25 — Learned context TTL / reuse selection — rounds 3, 7

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** A logistic reuse scorer on 5.3M examples and several memory choices; future-dependent global-frequency/link assumptions were acknowledged. E2, E16.

**Actual testing versus required testing:** Scorer uses age/title/count/frequency; stored words selected by reuse probability × estimated savings / bytes. 128 keep-alive model scores 1.7206 versus its blanked 1.7400. That is not a directly trained gain/hazard optimizer. Fit prefix-visible survival and future **final-bit** benefit, exclude optimistic future statistics, use same-capacity independent controls, and train the exported selector jointly. M8 is essential.

**Combination work evidenced:** Tested with scratch and weak CM. Round-7 fixed TTL16/128 probes did not implement the learned selection or context-dependent survival proposed later.

**Stronger descendant to implement:** Choose retention by expected future conditional log-loss reduction per memory byte, using survival hazards and a neutral rejection state.

**Discriminating experiment:** Test lag-conditioned value versus simple decay and equal-memory recency; charge selection messages if encoder uses future knowledge.

**Combination partners:** A81, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `hidden_TTL`: COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN; PID1680. Ten widths/kinds; four learned/fixed EWMA decays, reset every128bytes. Does not establish persistent TTL beyond a block, optimal eviction or survival controller.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.

- Round9 `title_memory`: COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY; PID2711. Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A26 — Encoder searches helpful context and transmits keep/drop choices — round 3

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 2.

**What rigor was actually evidenced:** Paid selector analysis correctly exposed a large cost for per-candidate choices. The searched coding family was narrow. E2.

**Actual testing versus required testing:** Reported oracle choice costs 10.1% for all candidates, 4.1% top 100, 2.1% top 30, 1.0% top 10. Compare block/article-level amortized selectors, shared priors, structured choices and null mode with actual payload savings. A transmitted selector helping many targets is different from individual keep/drop flags. Do not reject all paid context based on this family.

**Combination work evidenced:** Selector cost was analyzed relative to TTL's budget, not incorporated into a learned complete compressor. Later article latents revisit the broader hypothesis.

**Stronger descendant to implement:** Code keep/drop and context IDs with the selector's own normalized probabilities; optimize benefit minus side bits.

**Discriminating experiment:** Measure total hint plus payload cost, including unsuccessful searched hints and ordering; report any oracle only as an upper bound.

**Combination partners:** A25, A65. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A27 — Linked-article memory and tiny learned knowledge representations — rounds 3, 7

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 1.

**What rigor was actually evidenced:** Link-memory ablation and explanation of reconstructible history versus stored facts. No mature semantic/knowledge architecture. E2, E7, E18.

**Actual testing versus required testing:** Linked-article memory 1.7142 versus blanked 1.7150, with optimistic indexing conditions. Define only already decoded articles as donors, count index/selector model, compare title/link identity, random donors and summary capacity. Learned facts in weights must pay actual bytes; an external knowledge database cannot be assumed available.

**Combination work evidenced:** A link-memory model was trained; broader retrieval + progressive decoding + tiny fact representation stayed conceptual.

**Stronger descendant to implement:** Build a bounded title/link graph from decoded articles and preserve compact relation summaries rather than a huge hidden-state bank.

**Discriminating experiment:** Compare exact title overlap, sampled donors, compressed summaries and a same-memory random bank on warmed data.

**Combination partners:** A55, A71. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A28 — Scratch + learned keep-alive memory + length-aware coding — round 3

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 2.

**What rigor was actually evidenced:** The scratch/TTL pair has actual model ablations; the larger proposed combination is incomplete. E2.

**Actual testing versus required testing:** 128 empty + 128 keep-alive scores 1.7012, versus its blanked half 1.7289; weak-classical blend 1.5518. Same-trained-model blanking is useful but not an independently optimized no-memory control. Run a paired factorial design for scratch, TTL, word length and matched CM, with longer exposure and seeds. Charge full package and CPU.

**Combination work evidenced:** Pairing scratch and TTL was substantive. Adding word length and a length-aware classical model was recommended but not executed; do not describe the entire four-part stack as tested.

**Stronger descendant to implement:** Use one shared memory controller with stopping, retention and word-ending heads so correlated objectives pay one representation cost.

**Discriminating experiment:** Ablate each head and its interactions with identical memory and total parameter bytes.

**Combination partners:** A12, A25, A80. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `hidden_TTL`: COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN; PID1680. Ten widths/kinds; four learned/fixed EWMA decays, reset every128bytes. Does not establish persistent TTL beyond a block, optimal eviction or survival controller.

- Round9 `title_memory`: COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY; PID2711. Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A29 — Frequency, anagram, prefix, suffix and distributional word-code groups — round 4

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route C>T; priority 2.

**What rigor was actually evidenced:** Five explicit layouts with the same word-model architecture/steps; actual code and results survive. Useful representation research, short of mature production optimization. E3, E12.

**Actual testing versus required testing:** Toy bpb: frequency 1.4624; anagram 1.4367; alphabetical 1.4283; suffix 1.4231; distributional 1.3974. Dictionary sizes vary 150–237 KB. Match raw-byte exposure, contexts, actual entropy-packed assets and seeds; test hierarchical/shared morphology alternatives against the strongest production WRT. Code adjacency can help finite models without being intrinsically a shorter word code.

**Combination work evidenced:** Grouping + letter embeddings + miners + token CM was genuinely developed. This positive evidence should not be dismissed because later fixed neighbor boosts fail.

**Stronger descendant to implement:** Jointly optimize reversible word-code assignments and a composer, charging the permutation and preserving original ordering as a fallback.

**Discriminating experiment:** Compare model storage plus all transformed text bits, including out-of-dictionary tails; code remapping normally needs a matched predictor.

**Combination partners:** A08, A68. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A30 — Start-position, end-position and bag-of-letter embeddings — round 4

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 2.

**What rigor was actually evidenced:** Explicit compositional embeddings and two layout comparisons. No isolated equal-capacity random or learned generic-feature control reported. E3, E12.

**Actual testing versus required testing:** Alphabetical 1.4283→1.4069 (1.5%); distributional 1.3974→1.3823 (1.1%). Test each component, tied/untied embeddings, order-sensitive n-grams and same-parameter learned projections at matched exposure. Price embedding tensors and dictionary metadata. Gains establish a promising trained inductive bias in the toy models, not a production percentage.

**Combination work evidenced:** Yes, actual integration with dictionary models and subsequent miners. Optimal basis/rank, quantization and later associative use remain unresolved.

**Stronger descendant to implement:** Use independent positional/multiset bases, then a residual for semantic relations that spelling cannot express.

**Discriminating experiment:** Compare covariance-matched random bases and tied learned codes; remove linearly dependent moment channels before capacity claims.

**Combination partners:** A72, A74. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A31 — Token-level classical CM and mixer topology/initialization — round 4

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Iterative implementation work addressed a concrete failure. This is among the better engineered combination studies. E3, E12.

**Actual testing versus required testing:** Token CM 1.7365 versus byte 1.8245. Initial neural/CM mix 1.2573 worsened the neural 1.2430; changing bias and 12,288→960 weight contexts improved mixing. Compare neutral topology, trained mix and same context budgets on confirmation pieces, then actual range coding/CPU. Seven mixer choices on the test articles introduce selection bias into the final score.

**Combination work evidenced:** Implemented with neural cache/adaptation/kNN and ensembles. Its iteration shows real engineering, but there is no eligible native package evaluation of that final stack.

**Stronger descendant to implement:** Expose token and bit classical distributions to a compact hierarchical residual, with per-source normalization and shared backoff.

**Discriminating experiment:** Keep target event definitions identical; evaluate token-level gains against the actual final bit coder.

**Combination partners:** A42, A67. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A32 — Hidden-state cache over already decoded current text — rounds 4, 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Strict earlier-position masks, normalized continuation distributions and causal confidence buckets in source. Later real-coder screens corrected an accumulator bug. E3, E5, E12.

**Actual testing versus required testing:** Byte model 1.4829→1.4242; dictionary cache also helped. Round-6 final-coder cache only about 0.045%/0.084% after correction. Implement bounded integer/compressed keys and an actual native query path, test same work random/exact controls, and measure warm RAM and eligible CPU. Dense 16K×192 comparisons per byte are not a demonstrated practical search kernel.

**Combination work evidenced:** Extensively stacked with adaptation/kNN/CM. Compression of the cache and joint learning of retrieval/gates were not developed to a prize-feasible frontier.

**Stronger descendant to implement:** Keep compressed prototypes or code-tree continuation summaries, updating only on decoded events, rather than every hidden vector.

**Discriminating experiment:** Measure hit-rate and incremental final-bit information at fixed RAM and search CPU, with recency and random controls.

**Combination partners:** A71, A80. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A33 — Cross-article kNN over decoder-reconstructed hidden states — round 4

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 1.

**What rigor was actually evidenced:** Causal prior training articles, GPU blocked exact retrieval and several datastore sizes; CPU/RAM qualification absent. E3, E12.

**Actual testing versus required testing:** Larger banks improve toy loss; recorded bank reaches 25,792,942 half vectors. This exceeds 10 GB for vectors alone at width288. Test bounded reservoir/article summaries, product/int8 codes, approximate search recall and total CPU/RAM on a native decoder. Preserve availability offsets and price index work; GPU blocked search is not eligible inference.

**Combination work evidenced:** Substantial integration and bank-size scaling, including shared retrieval across snapshots. No engineered resource-feasible replacement bank was measured.

**Stronger descendant to implement:** Replace the 14.86-GB key bank with quantized prototypes, inverted title/link keys and bounded causal deduplication.

**Discriminating experiment:** Include key/value storage, search and startup; compare a warmed bank to cold and random controls without external knowledge.

**Combination partners:** A27, A71, A95. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A34 — Dictionary + algebra + adaptation + cache + kNN + CM — round 4

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** A real multi-component system with intermediate ablations, not merely a proposed combination. Baseline fairness and actual score constraints remained incomplete. E3, E12.

**Actual testing versus required testing:** Matched 18K byte model 1.3752 versus combined 1.2117; byte-cache control 1.325 narrows the relative gain. Later banks/training improve further. Compare useful exposure, parameter/package cost, retrieval availability and CPU at equal budgets. Run all component removals in a matched strong baseline and a complete eligible codec before projecting to enwik9.

**Combination work evidenced:** This is the clearest “yes, experimentally combined” case. It still does not document hours of thought per idea or global architecture optimization.

**Stronger descendant to implement:** Jointly train or adapt only the residual components whose conditional benefits survive the final mixture; share relation and parser state.

**Discriminating experiment:** Use a factorial interaction study and actual total bytes; summing independent component percentages is forbidden.

**Combination partners:** A17, A67, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.


## A35 — Snapshot ensembles, linear/geometric mixtures and shared searches — round 4

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 2.

**What rigor was actually evidenced:** Multiple snapshot combinations, probability normalization and online bucket selection are implemented. Cost and repeated test selection are not fully priced. E3, E12.

**Actual testing versus required testing:** Two/three/four models reach 1.1871/1.1841/1.1824 bpb; shared retrieval slightly worse at 1.1854 than member-specific 1.1841. Measure every stored snapshot, lookup, forward pass and native CPU. Compare compressed deltas, distillation and equal-capacity single models; freeze selection before fresh evaluation. The four-model 20.27% toy gain is not a record comparison.

**Combination work evidenced:** Real diversity and search-sharing experiments occurred. A low-cost distilled joint model and final complete package were not built.

**Stronger descendant to implement:** Distill a geometric mixture into one small decoder, or entropy-code snapshot deltas and share retrieval compute.

**Discriminating experiment:** Price all snapshots, logits normalization and per-token forwards; compare one equal-total-byte model.

**Combination partners:** A92, A41. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.


## A36 — Train/overfit the exact corpus; model description versus payload — rounds 3–4

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route C>T; priority 1.

**What rigor was actually evidenced:** Own-training-text arena and 100 MB scoring recognized the correct fixed-corpus objective. Stored-size accounting remained a proxy. E2, E3, E12.

**Actual testing versus required testing:** Round 4 reports 10-pass byte 18.98 MB and dictionary/cache 18.54 MB using entropy-size estimates and one copy. Build actual quantized containers, include every required copy and code, and independently decode. Corpus-specific training is allowed, but a memorized table/latent must be stored and charged. Evaluate net rate–distortion at the full corpus, not held-out percentage alone.

**Combination work evidenced:** Overfit models were combined with miners; the strongest full stack was scored only on test articles, not encoded as a whole submission.

**Stronger descendant to implement:** Treat corpus-specific neural weights, programs and discrete latents as interchangeable descriptions in a total-cost search.

**Discriminating experiment:** Fit exact corpus if beneficial, but store every corpus-dependent choice; statistical holdouts diagnose unstable search rather than define prize eligibility.

**Combination partners:** A61, A65, A90. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `core_long`: COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT; PID2064. Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.


## A37 — Port fxcm_v26 lexical contexts into the FX2 transformer pipeline — round 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Actual classical-model source integration preserving transformer priors and two native-related comparisons. Resource measurement was noisy. E4.

**Actual testing versus required testing:** Reported slice archives 194,183→193,404 and 428,199→427,132 (0.40%/0.25%). Measure full warm total, matched compiled flags, CPU/RAM and mixer state. It adds roughly 11–15% runtime in those estimates and is already part of the lexical comparator; it cannot count as a new gain on that comparator.

**Combination work evidenced:** Integrated with the existing neural coder and proposed tail/storage changes. Their joint full package was not measured.

**Stronger descendant to implement:** Transfer specific lexical contexts behind a disabled-by-default residual interface before merging entire pipeline state.

**Discriminating experiment:** Validate source feature availability and pointwise native identity; reproduce full production preprocessing and code cost.

**Combination partners:** A42, A93. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A38 — Timestamp-first revision records and revision-ID residual transform — round 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 2.

**What rigor was actually evidenced:** C++/Python byte agreement, whole preprocessing round trips and preserved split line count are strong transform engineering. Model matching was incomplete. E4, E13.

**Actual testing versus required testing:** On 100K records, neural + cmix 810,234→763,359; roughly 114 KB whole-region projection. Reordered metadata changes the model's trained stream. Test a matched retrained/finetuned conditional model, exact reversal and full final package; compare the stream-preserving timestamp expert under the same production baseline.

**Combination work evidenced:** Combined with title-copy transformation for exact inversion. The projected compression sum was not a full joint neural/package result.

**Stronger descendant to implement:** Optimize field ordering and revision residuals jointly with the order descriptor and a reversible record parser.

**Discriminating experiment:** Use a full record inverse and native matched coder; later metadata is paid or unavailable in original order.

**Combination partners:** A47, A56. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A39 — Interlanguage owner-title copy transform — round 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 2.

**What rigor was actually evidenced:** Owner alignment, eight genuine empty-title escapes and 244,173 replacements were handled, with exact transform round trips. E4, E13.

**Actual testing versus required testing:** 30K-block cmix-only 736,486→698,705; around76 KB extrapolation without transformer. Measure neural final coder on all transformed blocks and the actual lexical layout; keep exact escapes/case/ordering. Compare stream-preserving copy experts to avoid the changed-stream training mismatch.

**Combination work evidenced:** Exact inversion combined with the revision transform. Its compression interaction with changed neural data remained a projection.

**Stronger descendant to implement:** Build owner-title references from earlier decoded pages, with a short self/copy/escape hierarchy instead of a fixed external title list.

**Discriminating experiment:** Price references, unmatched labels and language exceptions; test original and altered stream order separately.

**Combination partners:** A50, A55. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A40 — Store selected float parameters as BF16 — round 5

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Actual container and native decoding work, plus loss checks. This is a lossy model-numeric change, not automatically exact storage. E4, E11.

**Actual testing versus required testing:** 2,930,652→2,874,742 bytes/copy; small neural loss differences lead to an estimated108 KB net. Independently distinguish tensors already exactly BF16 from rounded tensors, compare all changed native probabilities, final archive and complete CPU/package. Do not call the model byte-identical when arithmetic values change.

**Combination work evidenced:** Combined with exact C5 codec conversion in round 7 for this older checkpoint. Transfer to nonuniform lexical tables requires its own numeric/export audit.

**Stronger descendant to implement:** Use lossless exponent/mantissa prediction first; only then assess selected BF16 conversions with final-bit sensitivity.

**Discriminating experiment:** An exact mantissa codec preserves core predictions; any truncation requires measured native loss and serialization accounting.

**Combination partners:** A17, A43. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A41 — UPX/LZMA, PGO/LTO, executable pruning and loader costs

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Actual packed executable sizes, UPX integrity and identical compressed output for tested builds. Production flags/profile/unused-code search incomplete. E4, E11.

**Actual testing versus required testing:** UPX 195,584→166,708 per copy; C5 loader adds768 packed bytes in the lab. Compare clean matched production binaries, link maps, PGO input/profile, compiler versions and startup/run memory. A smaller lab binary does not establish the same delta in the submitted production package.

**Combination work evidenced:** Storage and loader tax were correctly combined in bounded component accounting. The full optimized candidate build and qualification are pending.

**Stronger descendant to implement:** Minimize actual packed source/executable and loader size using dead-code elimination and measured build variants.

**Discriminating experiment:** Choose source versus executable packaging according to official multiplicity; include compile/runtime options and all required assets.

**Combination partners:** A17, A95. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A42 — Transformer-aware post-SSE blend and specialist routing

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Actual small final-stage blend test and later neutral-versus-active checks. No exhaustive mixer architecture optimization. E4, E9.

**Actual testing versus required testing:** Round 5 blend worsens about 0.04%; later SX neutral/active archives both grow10/14 bytes on C/D. A new stage can change arithmetic/topology even when uninformative. Use exact identity initialization, shadow original update semantics and the same empty/random stage; then learned conditional gates. Do not infer automatic baseline preservation from a trainable coefficient.

**Combination work evidenced:** Several specialists were integrated, but learning the full residual/mixer interactions was not carried through. A negative topology choice does not dismiss all specialist signals.

**Stronger descendant to implement:** Introduce a normalized post-mixer residual with a true neutral branch and conditional Bayesian context backoff.

**Discriminating experiment:** Current conditional_gate_v1 is one finite branch; compare calibration, random relation, grammar and joint relation at equal gate complexity.

**Combination partners:** A31, A63, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.


## A43 — Post-training scales, pruning, mixed precision and codebook quantization

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Actual weight exports and native cost-versus-size screens in round 7; initial scale/prune choices were coarse. E4, E9, E15.

**Actual testing versus required testing:** Scale×1.05 increased neural loss about 11%. Three zeroing arms save221,742/435,552/1,690,680 two-copy bytes but add130–185/288–442/1,491–3,243 likelihood bytes on 32K prefixes. They fail break-even. Use layer/activation sensitivity, actual codebook values, calibrated scales, mixed precision and optional QAT under M1; ordinal C3 indices are not signed magnitudes. A coarse prune failure does not settle optimal quantization.

**Combination work evidenced:** Container savings and final-coder penalties were jointly assessed. Sensitivity-weighted PTQ/learned rounding, pruning plus trained recovery and new codebooks remain unexecuted variants.

**Stronger descendant to implement:** Optimize per-tensor precision/codebook/scale choices by total native loss plus exact stored bytes, with a paid choice grammar.

**Discriminating experiment:** Measure mixed-precision interactions; baseline parity and lambda-zero stability precede any QAT interpretation.

**Combination partners:** A16, A17, A90. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.

- Round9 `model_order`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Recover original container tensor order and independently verify all native reader tensor bytes. Adaptive weight-code order changes must not be confused with training. Native identity permits compositional reuse of the already independently decoded archives.


## A44 — Article-order coding, dictionary front coding and regeneration

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 2.

**What rigor was actually evidenced:** Real alternate order/dictionary byte counts; regeneration economics and full inversion discussed. E4, E5, E9.

**Actual testing versus required testing:** Delta order208,185 versus201,042; front dictionary114,569 versus100,096, both worse. Test stronger conditional order codecs with complete mapping cost; for regenerated dictionaries prove deterministic tie/order rules, compiler independence, startup CPU and permitted input dependencies. Regeneration in compressor versus decoder has different requirements and cannot erase required archive data by assertion.

**Combination work evidenced:** These are largely isolated packaging probes. Improved dictionary generation/order plus retrained lexical model was not tested as a joint rate–distortion system.

**Stronger descendant to implement:** Search article permutations with an entropy-coded permutation and decoder-built dictionary regeneration, not a free sorted corpus.

**Discriminating experiment:** Verify dictionary order/hash, inverse article order and initialization; minimize permutation plus actual coder cost.

**Combination partners:** A08, A95. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A45 — Higher arithmetic/SSE probability precision

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Round 7 derives a deliberately optimistic restricted bound from actual uint16 bins. Much stronger than a vague precision estimate. E4, E9.

**Actual testing versus required testing:** Bound57.492/59.566 bytes on A/B for the fixed predictor's permissible within-bin choices; not realized improvement. Test exact higher precision coder, normalization, termination and binary tax only if that budget pays. The bound says nothing about changing the predictor or side-information model.

**Combination work evidenced:** Used to deprioritize a small packaging path. No evidence that combining precision changes with a new trained model was evaluated; that would be a separate effect.

**Stronger descendant to implement:** Audit probability rounding and coder interval precision as a shared contract, then change only the interface with identical neutral outputs.

**Discriminating experiment:** Compare exact integer archive bytes and independent decoding; larger softmax precision need not improve a already quantized coder.

**Combination partners:** A63, A70. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A46 — Short compression-aware QAT/weight-entropy continuation — round 6

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 1.

**What rigor was actually evidenced:** Explicit payload + twice-weight-rate objective and quantizer surrogate. Sampling, continuation and numerical fidelity controls were inadequate for a broad conclusion. E5, E13, E20.

**Actual testing versus required testing:** At 100 steps, λ0 neural loss1.5103→1.5465 while λ30→1.5721; λ30 step 200→1.5851 despite lower weight entropy. A deteriorating λ0 cannot establish that rate-aware continuation is intrinsically ineffective. Repair complete-piece/target weighting, optimizer/start state and priors; validate frozen parity, then matched small λ0/0.3/1 arms with actual containers and final-coder loss. Strong regularization is not the whole frontier.

**Combination work evidenced:** Weight-rate and neural loss were optimized together, but not a stable continuation or jointly learned residual architecture. “Only full retraining can work” exceeded the evidence.

**Stronger descendant to implement:** Repair representative continuation, loss weighting and optimizer state before measuring the MDL rate frontier.

**Discriminating experiment:** Require frozen and lambda-zero controls first, then modest rate penalties with actual tensor containers.

**Combination partners:** A90, A93. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `core_long`: COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT; PID2064. Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.

- Round9 `core_pipeline_profile`: WAITING_FOR_CORE_DISTRIBUTED_V2; PID2780. Queued zero-update raw/redacted E/F controls plus unchanged-weight packed training throughput, explicit per-document KDA/convolution/attention/RoPE isolation and foreach optimizer comparisons. lr0 and resident batch; not5090, CPU codec timing or improved archive.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.

- Round9 `model_order`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Recover original container tensor order and independently verify all native reader tensor bytes. Adaptive weight-code order changes must not be confused with training. Native identity permits compositional reuse of the already independently decoded archives.


## A47 — Timestamp from already decoded revision ID, gap-conditioned Laplace mixture — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Causal interpolation, grammar escape, exact digit distributions, online EM and native regional checks are substantial mathematical/engineering work. E5, E14.

**Actual testing versus required testing:** Timestamp + contributor-ID expert saves109,946 bytes over 15,717,594 revision bytes; timestamp accounts for roughly 109,780. Scores deteriorate across late import records, which was measured. Test full warm core, the different lexical time-sorted tail, all bytes/side data and eligible CPU/RAM. Regional success is credible but not a complete-record gain.

**Combination work evidenced:** Combined with contributor and time-neighbor username experts and tested in native mini-stream reconstruction. Production lexical transfer is unverified.

**Stronger descendant to implement:** Use a conditional mixture of timestamp offsets, field schema and preceding-record deltas with hierarchical backoff.

**Discriminating experiment:** All centers must be prefix-visible; assess full digit sequence, false centers and native binary/decimal interface.

**Combination partners:** A51, A58. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A48 — Contributor ID defined by username, then copied — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Causal definition-once relation and native integration; clear distinction between standalone and mixed costs. E5, E14.

**Actual testing versus required testing:** Standalone139 bytes for1,121,627 predicted bytes, but final mix saves only about 307 bytes. Verify definition/collision/format/reset cases and price code/state. The strong coder already handles most known IDs, so standalone compression cannot justify its value alone.

**Combination work evidenced:** Actually integrated with timestamp and username experts. Its small marginal gain must be counted once in the joint region, not added to standalone savings.

**Stronger descendant to implement:** Use a dictionary of observed username-to-ID mappings with an uncertainty-aware edit/fallback model for changes and collisions.

**Discriminating experiment:** Normalize unseen names and changed IDs; include lookup memory and decoder-built mapping cost.

**Combination partners:** A49, A58. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A49 — Username from nearest-in-time earlier record — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Prefix-only time neighbor and confidence buckets; native joint result. E5, E14.

**Actual testing versus required testing:** Adds3,357-byte saving to the timestamp/contributor combination over the revision region. Compare nearest chronological, preceding-stream user and exact-user cache at equal resources; then warm lexical order and complete package. A future timestamp neighbor is unavailable unless transmitted.

**Combination work evidenced:** Actual three-expert joint native system. Long-history/resource and alternative order interactions were not fully optimized.

**Stronger descendant to implement:** Use time-local contributor transitions keyed by causal schema and article state, rather than only the nearest timestamp.

**Discriminating experiment:** Compare temporal-only and schema-only controls and all mismatches; approximate lookup must not use future records.

**Combination partners:** A48, A51. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A50 — Reconstruct owner-title list in stream; interlanguage copy expert — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Exact owner list matches independent Python, 93,707 owners/93,700 blocks; stream-preserving probabilities and round trips are strong. E5, E14.

**Actual testing versus required testing:** Region1,510,303→1,348,777, saving161,526 bytes. Compare full warm production lexical pipeline with matched state. Different shared-load timings do not establish a speedup. Title/case/empty/owner misalignment escapes must remain explicit.

**Combination work evidenced:** Used with the revision experts in the candidate/mini-stream. Their two regional savings sum274,829 bytes, but a single complete package has not measured that sum.

**Stronger descendant to implement:** Use a normalized title-copy trie with language morphology and literal edit alternatives, reconstructed from decoded source fields.

**Discriminating experiment:** Charge root escape, capitalization and nonmatching language forms; measure all interlanguage outcomes.

**Combination partners:** A39, A55. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A51 — Two-center timestamp mixture using the previous record — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Alternative standalone distribution and actual full-mix comparison; a useful negative interaction test. E5.

**Actual testing versus required testing:** Standalone391,618→336,295 (about 55 KB better), yet full mix grows1,088 bytes. Retest mixture weight/contexts under matched warm state if warranted; any surviving arm needs the native total. The result correctly warns that standalone better probability can interact badly with the final mixer.

**Combination work evidenced:** It was tested within the existing structural combination and rejected. That specific failure is evidenced; all possible additional timestamp centers are not exhausted.

**Stronger descendant to implement:** Replace a fixed two-center prior with a priced mixture of several prefix-known timestamp mechanisms and a null center.

**Discriminating experiment:** Learn causal conditional gating rather than select the best center after seeing the target; native code/digit loss is decisive.

**Combination partners:** A47, A60. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A52 — Predict page ID from title/alphabetical neighbors — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Causal neighbor hypothesis and standalone numeric check; no mature conditioned model. E5.

**Actual testing versus required testing:** Interpolation17.9 bits/page versus8.5 for plain delta. Define actual creation-era/order strata, already available neighbors and uncertainty model before enlarging complexity. Use the plain delta and same resources as controls, then final coder. This is a failed simple interpolation, not proof there is no title/creation relation.

**Combination work evidenced:** Screened as an additional metadata channel; no meaningful joint improvement or learned relation followed.

**Stronger descendant to implement:** Use a hierarchical posterior over title-neighbor rank, redirect status and earlier IDs, with literal fallback.

**Discriminating experiment:** Test monotonic-neighbor and random-title controls; include all page IDs, not only high-bit diagnostics.

**Combination partners:** A55, A58. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A53 — Predict timestamp from page ID — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** A direct causal interpolation screen with explicit errors. Limited mechanism/stratification. E5.

**Actual testing versus required testing:** Errors approximately 2^20–2^25 seconds, worse than prior record. Separate creation time from latest revision time, and test only decoder-known article strata. A calibrated conditional mixture must count non-single-revision pages and imports. Without a residual bit budget, this remains low priority.

**Combination work evidenced:** Proposed as another timestamp center; the naive relation was rejected before a full combined learned model.

**Stronger descendant to implement:** Fit a piecewise conditional date model from preceding IDs/titles, using charged segmentation or universal backoff.

**Discriminating experiment:** Compare it against decoded revision-ID prediction at the final coder; neither fitted slopes nor table breaks are free.

**Combination partners:** A47, A52. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A54 — Revision ID from article length, redirect and latest decoded year — round 6

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Distinguishes improved standalone high-bit prediction from actual final-coder gain. E5.

**Actual testing versus required testing:** Top-bit cost8.34→7.05 suggests39 KB standalone, but actual region saves354 bytes. Preserve parsing causality: text-derived year must precede revision field in this stream. Compare formatting/bot-run/time controls, native joint prediction and code price; do not project high-bit savings independently of already strong low digits.

**Combination work evidenced:** Evaluated against the final coder as a metadata extension. No trained multi-feature entity/time model or large gain is evidenced.

**Stronger descendant to implement:** Use causal numeric features only when their source fields have been decoded; marginalize unavailable features.

**Discriminating experiment:** Audit stream order and independent held blocks; high-bit entropy is not additive to existing low-digit modeling.

**Combination partners:** A51, A60. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A55 — Trie of decoded titles and link targets — round 6

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Causal trie and final-coder tests rather than repeat-rate optimism. Search/keying remains coarse. E5.

**Actual testing versus required testing:** +30/+25 archive bytes on A/B, including a large prior string set. Test schema/entity-specific candidate selection, alias/label relations, compact trie traversal and same-cost random donors; generic title membership cannot choose the right target. A failed undifferentiated trie does not test precise current-entity linkage.

**Combination work evidenced:** Added to the strong stack, with little weight accepted. The more targeted entity/field family was proposed and later probed separately.

**Stronger descendant to implement:** Share a title/link trie between entity copies, retrieval keys and new-mention priors, with one bounded memory allocation.

**Discriminating experiment:** Compare cold/warmed states and random keys; price every stored alias if it is not reconstructed from the prefix.

**Combination partners:** A27, A57, A71. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `title_memory`: COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY; PID2711. Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.


## A56 — Virtual replay, field reordering and decoder-known later metadata

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 2.

**What rigor was actually evidenced:** Stream-preserving experts were a practical substitution, but not mathematically equivalent to every replay factorization. E5, E17.

**Actual testing versus required testing:** Full general virtual-replay codec was not implemented. Define the alternative order, transmitted permutations/fields, replay state and conditional probability model; compare total both directions, e.g. time|ID versus ID|time plus source cost. A later field cannot help an earlier unknown value for free. Exact original-byte updates and complete inverse matter.

**Combination work evidenced:** Structural experts realize selected causal relations while preserving the stream. That is substantive engineering, but cannot be described as completion of the broader replay architecture.

**Stronger descendant to implement:** Build a reversible record-local dependency schedule and code the schedule only when it beats sequential original order.

**Discriminating experiment:** Check acyclic availability and block boundaries; later fields cannot be injected without first decoding their paid representation.

**Combination partners:** A38, A88. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A57 — Current-article entity, title, alias and field copies

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Prefix-available candidate generation, normalized whole-field mixtures and corrected EOF accounting. Strong finite-family math, limited semantic coverage. E9, E17.

**Actual testing versus required testing:** Balanced point-copy ideal savings A/B/C/D −2.261/+1.902/+0.649/−1.910 bytes per2M. The proposed capped title/alias/target family did not show a material gain. Test explicit entity identities and actual alias/infobox relations on a warm budget atlas, with equal unrelated-donor controls. No future field may select a donor silently.

**Combination work evidenced:** Shared scorer covers several field relations. Learned entity selection and joint paid latent/syntax interactions were not implemented.

**Stronger descendant to implement:** Use article-conditioned exact and edited entity copies with a gate that rejects unrelated spelling neighbors.

**Discriminating experiment:** Define normalized literal/copy/edit probabilities and compare title-only, schema-only and generic memory controls.

**Combination partners:** A55, A58. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `title_memory`: COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY; PID2711. Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.


## A58 — Schema-keyed probabilistic field edits / pair-HMM

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Marginalizes allowed alignments, normalized emissions and fallback; kernel checked against180 Python tests to below 2.85e−14 bits. E9, E17.

**Actual testing versus required testing:** Corrected field-edit savings −3.495/+0.007/−0.808/−3.527 bytes. A cheapest alignment selected using the unknown target would be invalid; the implemented marginalization avoids that. Test stronger template/path/column keys, banded state limits and learned transition rates at equal donors/CPU. The fixed field-copy edit kernel is not the proposed learned word-relation transducer.

**Combination work evidenced:** Generic field channels share the baseline mixture; no jointly trained schema discriminator or full command-codec/replay alternative.

**Stronger descendant to implement:** Use a proper pair-HMM over decoded field donors with insertion/deletion/substitution/escape mass, selected before the target.

**Discriminating experiment:** Score complete edit paths through forward marginalization; soft edit energy is not automatically a probability or metric.

**Combination partners:** A59, A60. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A59 — Prefix-keyed line copy/edit; digit-masked keys

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Paid four-byte prefix, bounded16 MB/64K-key memory, two donors and all mismatch costs. E9.

**Actual testing versus required testing:** Line exact gives −1.548/+1.029/+1.001/+0.201 ideal bytes; edits −2.822/+3.701/+10.262/+3.711, digit-mask similar. Optimize schema-aware boundaries/key lengths, normalized transition model and startup/RAM/CPU before native integration. The oracle budget is only for these donors and cannot rule out better semantic alignment.

**Combination work evidenced:** Exact versus edit and key masking were compared. No broad combination with grammar/entity/numeric schema models or learned donor choice was tested.

**Stronger descendant to implement:** Detect repeat line schemas with bounded prefix keys, then model numeric/text edits rather than matching whole literal lines.

**Discriminating experiment:** Use decoded line starts only; compare masked keys and same-budget random donors with every nonmatch charged.

**Combination partners:** A58, A61. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A60 — Numeric relations: recurrences, field copies, formats and units

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 1.

**What rigor was actually evidenced:** Bounded causal integer programs, false-alarm costs and explicit formatting/fallback. More advanced field arithmetic remains design only. E17, E21.

**Actual testing versus required testing:** Six programs (last, ±1, difference, same-field last, page-year copy), two strengths plus neutral save −0.498887 ideal bytes across 8M. Test typed columns, signs/zeros/decimals/units and normalized residual intervals, with paid fitted coefficients when offline. Short rational conversions and richer recurrences were proposed but not implemented. The six-program result is not an exhaustive arithmetic search.

**Combination work evidenced:** Programs were mixed causally and compared with paid templates. Joint schema detection and learned arithmetic confidence remain absent.

**Stronger descendant to implement:** Combine unit-aware recurrence, copy and formatting hypotheses as normalized latent programs with a fallback.

**Discriminating experiment:** Score wrong programs as well as successes; include leading zeros, signs, Unicode units and all decimal boundaries.

**Combination partners:** A47, A58, A61. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A61 — Corpus-specific executable macros, program search and numeric templates

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 1.

**What rigor was actually evidenced:** Two-part MDL and paid rule/use framing were specified; actual packet round trips are exact. The broad program-discovery/cover optimizer was not built. E17, E21.

**Actual testing versus required testing:** Bounded numeric-template packets all grew under zlib/LZMA on four slices, despite exact reconstruction. A fixed generic-codec layout is not a native macro predictor. Mine high-final-cost spans, optimize a nonoverlapping priced cover, store literal/rule/selector costs, and compare a native generated-string mixture or command codec with all fallback/replay costs. Exact free selection is diagnostic only.

**Combination work evidenced:** Numeric parameters + literal templates + codecs were tested. Entity fields, learned schema, sparse macro search and baseline replay were not optimized together.

**Stronger descendant to implement:** Use corpus program synthesis with a two-part code: rule definitions, occurrence dispatch, residual literals and exact inverse.

**Discriminating experiment:** Choose shared main-text/schema rules by joint net saving, not numeric templates alone; price overlaps, ordering and dead rules.

**Combination partners:** A36, A59, A65. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A62 — Frozen neural temperature and entropy-dependent calibration

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Finite registered strengths and neutral Bayesian mixtures; specific normalized likelihood comparison. E9.

**Actual testing versus required testing:** Temperature0.6–1.5 left1 best on A/B; adaptive standalone neural mixtures lose about 0.396/2.5 bytes. These are neural distributions, not final coder. Test richer calibration only with held-confirmation and complete normalized byte/bit paths, then native/payload cost. Do not treat a neural temperature loss as a result for a context-dependent lexical residual.

**Combination work evidenced:** Temperature and entropy contexts were combined, but not a trained residual architecture. Reasonably low priority after these finite results.

**Stronger descendant to implement:** Adapt temperature only in prefix-visible uncertainty/slot contexts with an exact neutral branch and universal gate.

**Discriminating experiment:** Current generic arm is a finite test; require integer archive gains beyond packaged code, not standalone neural loss.

**Combination partners:** A42, A63. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.


## A63 — Final-bit calibration and 128 learned integer odds factors

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Strong bounded native verification: exact neutral, deterministic uint64 odds, all candidate bits matched and independent E/F decodes. Narrow learned model. E9, E21, E22.

**Actual testing versus required testing:** Earlier causal calibration +30.194/+4.279 ideal bytes A/B. A/B-fit128-factor model (512 B/copy) saves148.168 ideal bytes across examined8M. Fresh64K E/F archives grow1/3 bytes; candidate code adds1,016 bytes before its model. Thus this calibration is not a winner. Context-dependent interactions require a separate model and priced fresh native test; do not reuse the development gain as confirmation.

**Combination work evidenced:** Baseline confidence × bit position was trained, not spelling/syntax/topic/memory. Exact arithmetic work provides reusable infrastructure but is not a learned lexical architecture.

**Stronger descendant to implement:** Use learned hierarchical integer odds with quantization tax tracked separately and a cheap production implementation.

**Discriminating experiment:** Compare replay and actual range-coded bytes; existing E/F have already been examined and are not fresh holdouts.

**Combination partners:** A42, A45. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.


## A64 — Suffix, root and new-mention word associations

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Causal counts, variable-length WRT parsing, full fallback outcomes and corrected root/EOF versions. Earlier provisional outputs had synchronization/lookahead defects. E9, E10, E21.

**Actual testing versus required testing:** Suffix screen gives7.554/54.905/75.124/29.940 ideal bytes but covers only 23–25% of costs. Corrected root/new-mention family gives41.891 total ideal bytes/8M; all fixed nonneutral arms lose. Test joint syntax/topic gating and native warmed integration after freezing a promising configuration. Never suppress an upcoming word using its unknown identity or declare a partial EOF word complete.

**Combination work evidenced:** Multiple causal associations share mixtures and masks. No trained first-mention predictor, semantic state or interaction controller was executed.

**Stronger descendant to implement:** Make first-mention, repeated-mention and suffix priors conditional on article state and grammar instead of unconditional suppression.

**Discriminating experiment:** Include unknown upcoming word identity, literal paths and partial EOF correctly; inspect remaining cost strata after the gate.

**Combination partners:** A55, A79, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A65 — Paid article topics/profiles and learned discrete/vector latents

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 1.

**What rigor was actually evidenced:** Valid Kraft-priced selectors, complete literal penalties and profile asset tax. The stronger learned conditional latent is design only. E9, E19, E23.

**Actual testing versus required testing:** 32 sparse profiles, seven strengths: selector-paid gains −231.275/−114.586/−89.628/−61.994 bytes before 21,844 B/copy tables. This rejects that sparse unigram family. Train a context-dependent residual conditioned on paid latent; compare no latent, causal title latent and future-informed paid latent at identical capacity. Encode latent/framing/title prior and optimize complete package; do not require the sparse screen to pass as a theorem-level prerequisite.

**Combination work evidenced:** Selector/profile coding was executed. Learned latent × syntax × lexical residual and title-conditioned priors have not been jointly trained.

**Stronger descendant to implement:** Search paid discrete article latents and rule dictionaries that explain several expensive events, rather than only unigram topics.

**Discriminating experiment:** Optimize latent bits plus all payload and decoder bytes; use a marginal/escape model for wrong or missing topic information.

**Combination partners:** A26, A61, A88. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A66 — Causal title/article latent state without transmitted hints

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Prefix-only title/count/topic state and corrected prior-strength comparison. No learned compact semantic recurrent state. E9, E19.

**Actual testing versus required testing:** V2 loses about 2.497/1.562/2.462/2.485 bytes; fixed64-prior V3 B/C loses1.539/2.457. Evaluate causal summaries and context-dependent residuals versus unigram/title counts, same-capacity generic state and paid latent. Future content must not leak into a “causal” state. These count models are not all latent-state architectures.

**Combination work evidenced:** Title/article priors were combined with word-tree specialists. Learned summaries and memory gates remained proposals.

**Stronger descendant to implement:** Build an untransmitted causal article latent from title/link/schema evidence and compress it into predictive summaries.

**Discriminating experiment:** Compare causal versus paid right-context information at equal resource budgets; keep external knowledge in the package if used.

**Combination partners:** A21, A55, A71. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `title_memory`: COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY; PID2711. Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A67 — Word-event prediction through the unchanged WRT code tree

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Exact probability interface, mixed two/three-byte prefixes and literal/escape/EOF corrections; full trained word predictor missing. E9, E18.

**Actual testing versus required testing:** Several additive tree experts were screened; no learned normalized full lexical head. For prefix a, next-byte probability is subtree mass(ab)/subtree mass(a), including all alternatives. Test all controls, escaping and termination, then train matched tree/global heads. Observed word costs cannot recover baseline probabilities of every counterfactual word for a global tilt.

**Combination work evidenced:** Infrastructure supports associations, topics, echo and grammar on one stream. The shared learned lexical model behind this interface has not been trained.

**Stronger descendant to implement:** Attach normalized residuals to the existing dictionary-code tree, preserving literal paths and exact word-ending state.

**Discriminating experiment:** Current gate reuses this interface; a new word head must score all paths, not only observed target-word losses.

**Combination partners:** A13, A70, A84. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `whole_word_alignment`: COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS; PID1505. Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_softmax`: COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN; PID2297. Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.

- Round9 `word_softmax_descendant`: COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN; PID2512. Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.

- Round9 `distributed_core_data`: COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS; PID2511. Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.

- Round9 `word_warmstart`: COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN; PID2752. Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.


## A68 — Spelling composer + low-rank semantic word codes; tied input/output

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 1.

**What rigor was actually evidenced:** Detailed storage/MAC economics and causal input distinction. No measured trained rank 8/16 word-code model in round 7. E18.

**Actual testing versus required testing:** 44515×16 int8 table alone712,240 B/copy requires about 0.01943 final bits/WRT symbol to break even at the old stream length. Compare spelling-only, learned generic codes, tied/untied codes, ranks and actual quantized containers under equal total cost. The target output embedding may be a candidate, but cannot enter the causal state before prediction.

**Combination work evidenced:** Intended to share across syntax, spelling, article and memory heads. That is a cost-aware design, not a measured jointly optimized architecture.

**Stronger descendant to implement:** Factor spelling and semantic code embeddings with tied input/output residuals and actual entropy-coded quantization.

**Discriminating experiment:** Compare composer, pure low-rank and equal-byte untied heads; unseen spellings and tail IDs remain losslessly expressible.

**Combination partners:** A30, A70, A92. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `word_softmax`: COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN; PID2297. Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.

- Round9 `word_softmax_descendant`: COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN; PID2512. Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.

- Round9 `word_warmstart`: COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN; PID2752. Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.


## A69 — Spend expensive computation at word events; multiple deliberation steps

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 2.

**What rigor was actually evidenced:** Operation-count decomposition recognizes byte-head/classical costs; speedup was not measured. E18.

**Actual testing versus required testing:** Old 586.459M WRT symbols /133.923M ASCII words ≈4.379 is an optimistic event ratio, not 4.379× runtime. Build word-triggered recurrent/update kernels and compare K=1/2/4 deliberations with a same-time byte model. Count dictionary fragments, literal spelling, head normalization and unchanged cmix; measure native full-run performance.

**Combination work evidenced:** Proposed with shared lexical heads and memories; no word-event architecture or optimal CPU allocation was executed.

**Stronger descendant to implement:** Trigger expensive reasoning only at decoder-known word events and allocate extra iterations by expected net value.

**Discriminating experiment:** Count full softmax/search/startup, rather than calling the proposal stage O(K); measure exact CPU per word and total.

**Combination partners:** A18, A67, A70. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A70 — Exact tiled word softmax, conditional tree heads and integer normalization

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Granular mathematical/engineering plan: tiled normalizer, subtree interface and bounded fixed-point sums. No trained native implementation. E18.

**Actual testing versus required testing:** Full 65536×44515 float32 logits ≈11.67 GB; rank 16 global scoring ≈95.4T MACs and 5.96T exponentials at the old word count. Proposed tree≤320 child scores is a different model capacity. Implement exact normalization, backward recomputation, deterministic quantization and low-mass fallback, then compare the actual CPU/Pareto frontier. Negative sampling cannot silently replace the coding normalizer.

**Combination work evidenced:** Designed to make lexical architecture affordable. No actual trained global/tree comparison or integrated decoding benchmark supports an optimal choice yet.

**Stronger descendant to implement:** Use an exact conditional tree or tiled full softmax, with integer normalizers and optional bounded candidate/fallback acceleration.

**Discriminating experiment:** Verify normalization, integer parity and all-tail coverage; approximate top-K cannot discard unpriced probability mass.

**Combination partners:** A45, A67, A68. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_softmax`: COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN; PID2297. Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.

- Round9 `word_softmax_descendant`: COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN; PID2512. Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.

- Round9 `word_warmstart`: COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN; PID2752. Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.


## A71 — Bounded prior-article retrieval using title/link keys and summaries

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Explicit completed-article availability and bounded bank; only a coarse retrieval implementation has run. E10, E16, E18, E21.

**Actual testing versus required testing:** Final batch bank up to 1024 completed articles, top 32 counters, ≤4 title-overlap donors, with random-article controls. It did not reveal a large joint gain. Test linked-entity keys, causal learned summaries and warm full history, matching donor availability and overlap strata. Cold slices reset the bank; they do not test a mature global decoder memory. Serialize learned keys but reconstruct decoded content.

**Combination work evidenced:** Combined with fixed syntax/echo/TTL families. Learned semantic selection and a shared contextual decoder remain unexecuted.

**Stronger descendant to implement:** Use compact title/link keyed summaries with deterministic incremental indexing and an explicit top-donor null gate.

**Discriminating experiment:** A cold 2-MB bank is not a full-history test; warmed native probabilities and source reconstruction time are required.

**Combination partners:** A27, A33, A55. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `title_memory`: COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY; PID2711. Six persistent causal title-byte copy laws with lifetime through the article and bounded4096byte titles; normalized within-byte support; convex nonnegative mixture fit on A/B, select C/D. Identity wins and is confirmed E/F. This does not exhaust case-invariant semantic/entity memory, contextual gating, links, field reordering or native integration.


## A72 — Independent positional letter moments / algebraic representations

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 2.

**What rigor was actually evidenced:** Round 7 corrected redundant basis functions and recognized normalized-moment collisions. This is real mathematical scrutiny, not proof of predictive usefulness. E6, E10.

**Actual testing versus required testing:** Moment neighbor audits, fixed graph/lag/echo screens; full learned bilinear placement/semantic model not run. Compare independent polynomial/orthogonal moments, order-sensitive n-grams, counts/length and same-rank learned/random projections. Record collisions and exact relations; words sharing moments do not become interchangeable or uniquely encoded.

**Combination work evidenced:** Moments informed candidate generation, but the proposed learned syntax/context × algebra interactions were not trained. The earlier trained letter embeddings remain separate positive evidence.

**Stronger descendant to implement:** Use only independent letter moments, and add a learned contextual relevance component rather than a higher-degree redundant basis.

**Discriminating experiment:** Geometry arm tests a fixed graph; independent-basis, random covariance and learned relation tests are distinct follow-ups.

**Combination partners:** A30, A74, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A73 — Word glyph geometry as a relational basis / parameter sharing

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 3.

**What rigor was actually evidenced:** Recognized G_k=G A_k, so complete letter moments already contain those fixed linear features. E6, E10.

**Actual testing versus required testing:** Geometry nearest-neighbor/control arms were scored, not a learned geometry-conditioned relation function with matched projections. Fix deterministic glyph rules; compare equal-dimensional random/learned projection and complete spelling moments at identical downstream capacity. Geometry may regularize useful sharing; it cannot be credited as new information merely by adding another feature block.

**Combination work evidenced:** Geometry was combined with fixed echo support. Signed learned relation/gates and morphophonographic channels were not jointly optimized.

**Stronger descendant to implement:** Use glyph similarity as one shared feature of a relational residual, with spelling and semantic exceptions explicitly separated.

**Discriminating experiment:** A same-capacity random-glyph control determines attributable gain; pixel similarity cannot establish semantic association.

**Combination partners:** A04, A72. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A74 — Word edit, prefix/suffix, multiset, morphology and phonetic channels

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Normalization/soft-edit limitations were derived; bounded prefix/suffix/deletion and Soundex variants exist. Learned phonographic/pair-HMM word relations do not. E6, E10, E21.

**Actual testing versus required testing:** Final fixed Soundex/anagram/geometry arms all lose as nonneutral policies; lag diagnostics have substantial matched-random coverage. Test each relation in a trained signed contextual residual with same-degree/work controls. Include deletion/silent-letter rules and learned shared edit costs as separately priced hypotheses; distinguish prefix-derived candidate support from optimal probability. Field edit failures are not word edit tests.

**Combination work evidenced:** Several channels were enumerated and mixed. Their trained complementary interaction, selection and morphology-specific sharing remain untested.

**Stronger descendant to implement:** Combine edit, affix, phonetic and word-class channels in a proper probabilistic relation model with a context-dependent rejection option.

**Discriminating experiment:** Current fixed neighbors are only initialization; test no/know and unrelated lookalikes without hand-picked target hindsight.

**Combination partners:** A58, A72, A80. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A75 — Candidate graph search, exhaustive neighbors and deterministic integer repair

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Strong search-correctness audit. The initial candidate search was discovered to be very poor, then repaired and independently CPU-checked. E10.

**Actual testing versus required testing:** Capped top 8 mean recall3.947% on 133 queries; integer graph99.248%,125/133 full recall **against the original float metric**; all 356,120 integer graph IDs/scores CPU/GPU equal. The residual float-reference differences are not missed searches under the exhaustive integer definition. CPU prototype30.667 s/RSS832,904 KiB. High search recall does not prove useful relations. Optimize indexes/working memory and benchmark compiled startup/native query costs before qualification.

**Combination work evidenced:** Corrected graph was substituted into the same echo screen, a useful controlled repair. It did not trigger training of the full relation model.

**Stronger descendant to implement:** Use deterministic multistage candidate generation with exact score verification, sharing one index across channels.

**Discriminating experiment:** Measure full build/search memory and recall by actual predictive benefit, not nearest-neighbor score recall alone.

**Combination partners:** A27, A71, A74. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A76 — Lag-support diagnostics and restricted oracle ceilings

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N; priority 2.

**What rigor was actually evidenced:** Exact donor availability and bit-weighted budget separated from achievable gains; overlap explicitly acknowledged. E10.

**Actual testing versus required testing:** Dictionary-span support budgets range roughly 5–19% by relation/slice; matched random support is sizable too. These use up to 256 sources and can exceed the actual128-slot echo support. Record union/overlap and realistic memory eviction, then fit a normalized causal scorer charging false positives. Cannot add lag/channel percentages or treat perfect supported-target prediction as an executable.

**Combination work evidenced:** Several supports were compared, but joint coverage union and a trained multi-channel support-to-probability model were not measured.

**Stronger descendant to implement:** Turn lag coverage into an opportunity ledger that accounts for false positives and conditional benefit, not a free-memory oracle.

**Discriminating experiment:** Measure all candidate activations and context availability; a restricted donor ceiling does not bound all architectures.

**Combination partners:** A25, A81. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A77 — Fixed lexical echo, signed boosts, decays and neutral/random controls

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Corrected causal distributions, graph substitution, EOF/fallback and final uint16 replay are carefully engineered. The actual learned architecture is absent. E10, E21.

**Actual testing versus required testing:** Corrected integer echo gross≈4.244 ideal bytes/8M. Final15-family/four-strength mixture gross1.731295 bytes/8M; fixed nonneutral arms lose. This tests fixed activations/decays, not whether context learns to reject bad candidates. Train joint gates/relations under all-outcome final-bit loss; include same-capacity learned generic and shuffled controls, actual native archives and model tax.

**Combination work evidenced:** Many finite experts were mixed, but mixing independent fixed arms is not optimizing feature interactions in a shared architecture.

**Stronger descendant to implement:** Use signed echoes behind a conditional backoff gate and compare strength/decay priors that charge online selection.

**Discriminating experiment:** Current gate tests geometry/grammar interaction; exact-echo and hazard channels are a registered extension, not already completed.

**Combination partners:** A25, A79, A82. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.


## A78 — Directed word placements, lag bins and low-rank distance kernels

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Causal directional counts and a compact recursive low-rank formulation were specified. Only counts/fixed mixtures ran. E6, E10.

**Actual testing versus required testing:** Directed-lag screen gives total−7.847332 ideal bytes/8M. It does not implement z(u)^T M(d)z(v) with trained ranks/time bases. Train signed low-rank directional residuals against final bits, inspect whether grammar/topic interactions are needed, compare previous-word/count and same-rank generic controls. Recursion saves history scans for exponential kernels; Gaussian windows need their own queue/cost model.

**Combination work evidenced:** Counts and echoes were separately/mixture tested. Joint learned placement × associative activation is still missing.

**Stronger descendant to implement:** Use a causal low-rank distance-conditioned placement kernel, with within-sentence slot state and a null transition.

**Discriminating experiment:** Compare class-only versus full-word pairs and random lag kernels; never substitute a known future endpoint for prefix data.

**Combination partners:** A79, A81. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A79 — Syntax/word-slot state, placement heuristics and source surprise

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Causal previous-word class/punctuation and source-only surprise were used. No trained syntax-state/controller architecture. E6, E10, E21.

**Actual testing versus required testing:** 32K residual pilot loses4.017518 ideal bytes/64K; later coarse syntax/source-rank families yield no material gain. Literal I/i and word-boundary coverage were audited. Train small recurrent/transformer slot state using decoded words, markup, punctuation and title; ablate syntax alone, echo alone and interactions. “Now…know” anecdotes (zero sampled short-lag pairs) are not evidence of a general ordering law.

**Combination work evidenced:** Heuristic states combined with fixed residual arms. The proposed learned placement/suppression model was not trained or optimized.

**Stronger descendant to implement:** Infer a coarse slot posterior from the prefix, then refine variable-order constructor histories and lexical class transitions.

**Discriminating experiment:** Current grammar_joint tests coarse syntax/run; true POS and rich syntactic state require separate supervision or priced grammar.

**Combination partners:** A64, A82, A89. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A80 — Learned persistent signed activation, injection, rejection and survival

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** This central idea has equations and subsequent corrections, **not an implemented trained mechanism**. E6, E10, E23.

**Actual testing versus required testing:** Fixed echo/TTL is an incomplete proxy for a_t(v)=λ_t(v)a_{t−1}(v)+I_t(u,v,H_t). Train signed relation, context gate and survival jointly, with bounded memory, exact exported arithmetic and all false associations charged. Surprise may be used only after its source word completes. Compare exact memory, structural/learned memory and equal generic capacity; test first mentions separately from repeats without using future labels as inputs.

**Combination work evidenced:** There is thoughtful written synthesis with placement/residual heads. No end-to-end trained activation × syntax × memory architecture, or hours-per-idea log, supports calling it deeply experimentally optimized.

**Stronger descendant to implement:** Store signed latent activation with learned rejection and a value-based survival rule, sharing persistent state across relation channels.

**Discriminating experiment:** Compare fixed echoes, random activation and learned content-conditioned survival under final-bit supervision and fixed RAM.

**Combination partners:** A25, A74, A81. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `hidden_TTL`: COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN; PID1680. Ten widths/kinds; four learned/fixed EWMA decays, reset every128bytes. Does not establish persistent TTL beyond a block, optimal eviction or survival controller.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A81 — Counterfactual edge savings, hazard, optimal activation and eviction

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route N>T; priority 1.

**What rigor was actually evidenced:** Corrected horizon-versus-next-event mismatch and interacting-edge attribution. These are meaningful theoretical improvements, not empirical calibration. E6, E10, E16.

**Actual testing versus required testing:** No learned counterfactual deletion or hazard model was executed; exponential TTL is not that test. Define immediate state deletion versus full replay, sample paired interventions on prefix-generated edges, estimate next-step hazards and train joint normalized likelihood/rate. Eviction uses expected future final-bit value from available features, never actual future reuse. Edge-wise savings cannot simply be summed.

**Combination work evidenced:** Combined conceptually with sparse activations and MDL, not with trained controllers or native causal counterfactual evaluation.

**Stronger descendant to implement:** Optimize causal expected future log-loss benefit minus state and compute cost; use risk-aware eviction when estimates are uncertain.

**Discriminating experiment:** Next-event hazard and 256-event recurrence are different targets; counterfactual benefit needs normalized full predictions.

**Combination partners:** A25, A76, A80. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A82 — Multi-source/multi-channel log-odds accumulation and activation×placement interaction

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Equations include signed evidence and an interaction term; correlated evidence/double counting was recognized. E6, E10.

**Actual testing versus required testing:** Fixed expert mixtures do not train β_AP a(v)p(v), contextual cross-channel coefficients or suppression. Run factorial removal of channels and interaction terms in the same jointly trained residual, match storage/CPU, clip exported activations and score every outcome. A neutral branch bounds losses only under its precise mixture semantics, not by wishful convergence of coefficients.

**Combination work evidenced:** This is the defining proposed combination; it remains design only. Its failure cannot be inferred from additive fixed unigram probes.

**Stronger descendant to implement:** Model relation and placement jointly with calibrated interactions rather than multiply marginal boosts as independent evidence.

**Discriminating experiment:** Current conditional_gate_v1 gives a finite Bayesian joint family; interpret its increment only after generic/random controls.

**Combination partners:** A06, A79, A84. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `sequence`: COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN; PID1464. Eight widths/kinds, finite rungs and fixed64-byte block context. Does not implement every shared controller, architecture or long memory.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A83 — Shared residual transformer/controllers and multiple specialized heads

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 1.

**What rigor was actually evidenced:** Probability-space correction and parameter-sharing equations are valid proposals; no trained shared syntax/algebra/article/memory residual in round 7. E6, E18, E23.

**Actual testing versus required testing:** The128-factor calibration is not this model, and four independent snapshots are a different architecture. Train shared state with small heads, compare one generic residual versus specialized heads at equal rate/time, measure sequential corrections' final normalizer and exported size. Register rank/state/model byte caps and test literal/control fallback. Avoid making failed simpler screening a universal prerequisite.

**Combination work evidenced:** Written design integrates several ideas; implementation, learned interaction ablations and architecture tuning are absent. This is one of the largest gaps relative to the user's requested research depth.

**Stronger descendant to implement:** Share one compact residual representation with specialist heads and a sparse gate; avoid multiple full transformers for placement.

**Discriminating experiment:** Factorial ablations must separate shared capacity savings, specialization and gate effects under total package bytes.

**Combination partners:** A28, A80, A84. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `sequence`: COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN; PID1464. Eight widths/kinds, finite rungs and fixed64-byte block context. Does not implement every shared controller, architecture or long memory.

- Round9 `hidden_TTL`: COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN; PID1680. Ten widths/kinds; four learned/fixed EWMA decays, reset every128bytes. Does not establish persistent TTL beyond a block, optimal eviction or survival controller.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_softmax`: COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN; PID2297. Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.

- Round9 `word_softmax_descendant`: COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN; PID2512. Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.

- Round9 `word_warmstart`: COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN; PID2752. Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.


## A84 — Independent learned residual against the native final-bit coder

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Later design identifies a way around the unrelated core-GPU parity dependency. Integer calibration infrastructure is verified; the contextual residual is untrained. E22, E23.

**Actual testing versus required testing:** Collect native causal features and y,p16; train q=Q16 σ(logit(p)+rθ(c)) with complete loss plus actual model/code rate. Keep baseline internal updates unchanged, so teacher-forced baseline trajectories remain valid. Compare32/128 KiB-budget contextual models with generic/identity controls, then fresh native decode/package/CPU. Core parity is not required for this independent head; its own export parity is.

**Combination work evidenced:** Proposed to combine syntax, spelling, memory and paid latent. No new model from this proposal has been launched or measured.

**Stronger descendant to implement:** Train or adapt an independent residual directly against immutable native final bits, avoiding the unfaithful core GPU port.

**Discriminating experiment:** Causal features and exact neutral export first; continuous learned residuals remain separate from the current finite online gate.

**Combination partners:** A42, A67, A93. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `sequence`: COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN; PID1464. Eight widths/kinds, finite rungs and fixed64-byte block context. Does not implement every shared controller, architecture or long memory.

- Round9 `hidden_TTL`: COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN; PID1680. Ten widths/kinds; four learned/fixed EWMA decays, reset every128bytes. Does not establish persistent TTL beyond a block, optimal eviction or survival controller.

- Round9 `adaptive_replay`: COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY; PID1711. Eight finite posterior policies; source-replay likelihood only. Previously viewed C/D/E/F are fit-held-out, not untouched discovery data.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_softmax`: COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN; PID2297. Eight actual44515way word output heads, unchanged dictionary code tree and literal fallback; exact normalized probability and causality checks. Fixed.8dictionary/.2uniform literal law and.1expert gate cap; surviving random-basis heads lose versus adaptive reference. No native integration or full package.

- Round9 `word_softmax_descendant`: COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN; PID2512. Ten runs learn literal byte distribution, dictionary/literal gate, word temperature and native/expert gate capped.5, with byte-head control and pruned-kind model construction. Same six cold fragments, finite128/384/1152rungs. Native integration, production framing and fullwarm/package remain open.

- Round9 `word_warmstart`: COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN; PID2752. Six spelling/independent/random models, direct44515class word CE on verified dictionary-only root first-code positions then full-bit mixture loss; two seeds and128/384rungs per phase. Supervised word CE alone is not compression. Full support/native integration/cost and fullwarm qualification remain open.


## A85 — Constructors, content variables and rare constants: reversible split

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route C; priority 1.

**What rigor was actually evidenced:** Exact lexical distinction, framing, literal-word handling, raw reconstruction and native-bit budget were analyzed. Grammar-class semantics remain a heuristic lexicon, not validated POS tags. E24.

**Actual testing versus required testing:** Declared176 constructors carry about 17.1997% of sampled bits;56 generic-codec comparisons all grew. Test lexicon/learned-class alternatives with all tags/model assets charged, exact punctuation/case/markup and content order. Separately optimize C,A,G streams under M3. If only that measured constructor bucket changes, it cannot alone explain a20% total gain; its full-corpus share is unverified.

**Combination work evidenced:** Exact split and layout variants were implemented. A jointly trained content/grammar model was not, so the constructor hypothesis is only partly tested.

**Stronger descendant to implement:** Allow original order or constructor/content split per block, with a paid selector and exact skeleton/constant/literal reconstruction.

**Discriminating experiment:** Repeated sets do not remove placement entropy; measure all streams together against the same final coder.

**Combination partners:** A11, A87, A88. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `whole_word_alignment`: COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS; PID1505. Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `literal_split`: COMPLETE_REVERSIBLE_LITERAL_INPUT_MASK_SPLIT_NATIVE_SCREEN; PID2281. Three actual reversible input-redaction cutoffs on65KiB, final CM encode/decode; positions, literals and container bytes paid. Unchanged model only, Python side wrapper, previously viewed prefix, unmeasured eligible executable cost. Negative finite result does not reject better side models or content-first architectures.

- Round9 `known_literals`: COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN; PID2437. Three raw-context known-literal cutoffs, one masked-context branch and one trained common specialist on65KiB. Native Predict/Perceive still run for skipped coded bytes, independent decode/core identity PASS. All5 lose after the current side price. Full production wrapper, stronger side law, fullwarm/package and independent corpus remain open.

- Round9 `known_side_verify`: COMPLETE_INDEPENDENT_PAID_SIDE_HINT_RECONSTRUCTION_IDENTITY; PID58. Independently parse the paid HPKNOWN container alone, reconstruct every mask/value byte, prove identity with files used in all5 executed native decodes and original reconstruction. No frequency table/original input needed to construct hints; eligible native side-loader/full package still pending.

- Round9 `distributed_core_data`: COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS; PID2511. Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A86 — Constructor sets, multisets and permutation coding

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 2.

**What rigor was actually evidenced:** Explicitly corrected loss of order/multiplicity; exact packet decoding includes order. E24.

**Actual testing versus required testing:** Multiset-plus-order framed layout grows about 19.473% zlib9 /22.204% LZMA6. Most gaps (87.345%) contain0/1 constructors, limiting set amortization in these samples. Test enumerative permutation coding conditioned on already paid anchors, adaptive set priors and exact repeats at equal framing; evaluate total streams rather than assume equal sets are equal sentences.

**Combination work evidenced:** Set identity + order + literal frames was tested. Learned contextual permutation or subset selection was not trained.

**Stronger descendant to implement:** Encode multiset identity and a multinomial/permutation residual, sharing only where the net code actually falls.

**Discriminating experiment:** Charge count vectors, repeated constructors and order; optimize subsets with explicit dictionary and membership costs.

**Combination partners:** A85, A87. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A87 — Ordered constructor templates, shared word dictionaries and subset grammars

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C; priority 1.

**What rigor was actually evidenced:** Actual table/layout variants, charged IDs and raw round trips. Broad subset/compositional grammar model is still unimplemented. E24.

**Actual testing versus required testing:** Ordered framed templates grow18.847%/21.493%; best one-byte skeleton marker + constructor-word table grows2.066%/4.601%. Low reuse of larger gaps argues against these static tables. Train conditional ordered gaps or a reusable grammar with paid derivations, compare direct adaptive gap model, and measure native complete cost. A generic LZMA loss is not a learned grammar loss.

**Combination work evidenced:** Dictionary sharing, markers and gaps were combined iteratively. Content-conditioned neural prediction and learned subset composition were not.

**Stronger descendant to implement:** Use an ordered shared grammar with rule expansion, substitution and literal fallback, jointly selecting profitable rules.

**Discriminating experiment:** A paid MDL grammar must beat total symbol/payload costs; numeric-only frozen packets do not exhaust textual templates.

**Combination partners:** A61, A85, A89. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A88 — Content first, then grammar with both left/right content; neural infilling

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route C>T; priority 1.

**What rigor was actually evidenced:** Valid chain-rule factorization, paid right context and exact alignment requirements are developed. The actual learned codec is design only. E7, E24, E23.

**Actual testing versus required testing:** Skeleton packets and small earlier masked models are partial proxies. Train Q_C(C), Q_A(A|C), Q_G(G|C,A) on their actual decode order, compare left-only/right-only/both anchors and equal total model/compute budgets, then reconstruct exact bytes. Stripped text scored by the old frozen transformer is out of distribution and cannot settle the architecture. “There _ a camel” does not remove the need to code is/was and surrounding layout.

**Combination work evidenced:** Rigorous written combined architecture exists. No joint content-first model or optimized conditional infiller was run.

**Stronger descendant to implement:** Decode paid content/endpoints before constructor gaps, then use a normalized endpoint-conditioned gap model; neural infill comes later.

**Discriminating experiment:** Begin with a strong exact classical gap codec and a causal control; positions, tense alternatives, punctuation and rare constants are charged.

**Combination partners:** A10, A56, A65. Prerequisites: exact inverse / reachability contract; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A89 — Prefix-only constructor-run and syntax expert on unchanged stream

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N; priority 1.

**What rigor was actually evidenced:** Causal completed-word updates and full-bit normalized residual scoring; limited hand-built state. E21, E24.

**Actual testing versus required testing:** Final batch uses constructor-run length/class and prior content rank, with 176-word list and neutral controls. No material gain. Test a learned ordered-run/trie model conditioned on decoded content/punctuation, compare same-sized generic syntax state and morphology, and measure actual integer native coder. An observed gap's future length or next noun must not activate its own gate.

**Combination work evidenced:** Combined with the fixed syntax/memory suite. No trained constructor × content × residual interaction.

**Stronger descendant to implement:** Combine prefix constructor-run evidence with native uncertainty and relation context; strengthen to variable-order histories if coarse gates fail.

**Discriminating experiment:** Current random/grammar/geometry plus-run arms are controls; success needs an increment above generic calibration and native package cost.

**Combination partners:** A79, A82, A87. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `word_events`: COMPLETE_CAUSAL_WHOLE_WORD_EVENTS; PID2192. Completed delimiters control word availability. Features omit rarity/intext labels. Known semantic WRT mode and cold-boundary convention must be replicated in native integration.

- Round9 `word_features`: COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN; PID2248. Eighteen controlled finite word-feature runs. Symbolic groups are not an OCR/CNN architecture; constructor class is not true POS; word-hash control is not an information-theoretic null. This branch does not implement a word output composer or bidirectional infilling; separate word_softmax jobs implement the former.

- Round9 `word_cache`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Eight actual causal completed-word donor laws; last256words,length1..64bytes,proper encoded prefixes through8bytes,recency/letter sharing/preceding constructor context. AB scalar fits,CDselection,EFconfirmation; production parser,native decode,eligible time/memory and full package pending.


## A90 — Representative finetuning/full retraining with correct MDL rate

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 1.

**What rigor was actually evidenced:** Detailed later contracts address useful-token weighting, optimizer, numerical export and actual rate. Those contracts have not been executed. E20.

**Actual testing versus required testing:** Round 6 short λ30 is the actual training evidence; round 7 core finetuning was not run. Require frozen F0 identity, baseline-preserving representative F1 λ0, then matched small-rate arms, actual packed export/final coder and appropriate seeds/pieces. Restore original optimizer if available; otherwise warm-start conservatively and do not change all factors at once. Full scratch retraining is an alternative, not proven necessary.

**Combination work evidenced:** Payload/rate/data/export/CPU dependencies are planned in detail. Learned architecture + rate-aware continuation has not been tested. The $70 stages are caps, not completed spending.

**Stronger descendant to implement:** Fit the rate-distortion frontier using correct representative sampling, native validation and actual weight entropy, staged within 70 USD.

**Discriminating experiment:** Repair lambda-zero continuation and frozen parity before spending on regularized winners; hold cost cap and export gate.

**Combination partners:** A43, A46, A91. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `core_long`: COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT; PID2064. Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.

- Round9 `whole_word_alignment`: COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS; PID1505. Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `known_literals`: COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN; PID2437. Three raw-context known-literal cutoffs, one masked-context branch and one trained common specialist on65KiB. Native Predict/Perceive still run for skipped coded bytes, independent decode/core identity PASS. All5 lose after the current side price. Full production wrapper, stronger side law, fullwarm/package and independent corpus remain open.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `distributed_core_data`: COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS; PID2511. Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.


## A91 — Residual-importance sampling and mixer-aware training objectives

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 1.

**What rigor was actually evidenced:** Importance correction and limitations of a simplified neural/CM surrogate are stated. Design only. E20.

**Actual testing versus required testing:** No residual-importance/mixer-aware training arm is recorded. Fix π_t=η/T+(1−η)c_t/Σc and use1/(Tπ_t) if preserving uniform likelihood; record whether reweighting is intentional. Compare uniform and corrected sampling at equal useful targets, validate surrogate sensitivity against the actual nonlinear mixer, and select by final payload plus exported size. Expensive examples may be training labels, not future inference inputs.

**Combination work evidenced:** Intended to combine difficult-word diagnostics with MDL continuation. No measured joint outcome or optimal allocation of gradient effort exists.

**Stronger descendant to implement:** Sample by residual cost with explicit importance weights preserving the global objective; model mixer response instead of neural-only targets.

**Discriminating experiment:** Compare unbiased importance weighting with uniform/token-weighted controls; report full-corpus rate, not selected difficult examples.

**Combination partners:** A15, A84, A90. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `core_long`: COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT; PID2064. Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.

- Round9 `known_literals`: COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN; PID2437. Three raw-context known-literal cutoffs, one masked-context branch and one trained common specialist on65KiB. Native Predict/Perceive still run for skipped coded bytes, independent decode/core identity PASS. All5 lose after the current side price. Full production wrapper, stronger side law, fullwarm/package and independent corpus remain open.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.


## A92 — Small adapters, merged LoRA, larger teacher and distillation

Status: **OPEN_NOT_IMPLEMENTED_THIS_ROUND**. Route T; priority 2.

**What rigor was actually evidenced:** Correctly prices merged versus unmerged updates and teacher/student costs; no executed round 7 training study. E18, E20.

**Actual testing versus required testing:** 8M/10M structural loads passed, but neural parity failed and inference comparisons were skipped. For core teachers fix parity first; for an independent residual train its own control. Compare merged quantized adapters, separately stored adapters and distilled equal-cost student using actual containers and CPU. “LoRA is small” does not make changed base weights or forward passes free.

**Combination work evidenced:** Proposed with rate-aware finetuning and shared lexical heads. No trained teacher→student or adapter × memory experiment supports a compression estimate.

**Stronger descendant to implement:** Use a larger teacher only in training, distill code-tree/final-bit probabilities, and merge/export a small low-rank adapter.

**Discriminating experiment:** Include teacher calibration and random/identity student controls; price inference student bytes and any retained teacher assets.

**Combination partners:** A20, A35, A68. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

No new implementation/test of this family is recorded in round9. Its existing ideas, controls and cost gates remain required; the family is not rejected.


## A93 — Native/GPU parity, checkpoint reconstruction and lexical configuration

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route V; priority 1.

**What rigor was actually evidenced:** Strict load/shape audits, macro correction and actual pointwise diagnostics; failure preserved. These are prerequisite engineering tasks, not compression gains. E10, E15, E20.

**Actual testing versus required testing:** Correct C3 macros/codebooks enable native round trips; larger checkpoints load structurally. Compatible FX2 GPU pilot fails ordinary-row parity despite matching reset fallbacks. Locate first layer/state divergence, check prior/activation quantization, attention/KDA piece resets and export, then lexical F0. Do not silently relax gates or assume loading proves functional equivalence. Independent residual training needs only its own faithful native interface.

**Combination work evidenced:** This infrastructure supports all core-training variants. Its unresolved state was allowed to delay too many independent architectures; dependency redesign is required.

**Stronger descendant to implement:** Lock checkpoint/configuration, preprocessing and exact native probability contracts before core retraining or representation changes.

**Discriminating experiment:** Pointwise integer tests, carry/reset/quantization boundaries and neutral archive identity; aggregate GPU loss is insufficient.

**Combination partners:** A43, A84, A95. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `whole_word_alignment`: COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS; PID1505. Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.

- Round9 `native_layers`: COMPLETE_NATIVE_CORE_LAYER_OBSERVATION; PID1997. Observes4096native steps,205FP32priors and13activation stages. Observation only; no optimization claim.

- Round9 `GPU_layers_v2`: COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL; PID2139. Integer-dot forward improves first article, but later article probabilities still differ. No native parity PASS.

- Round9 `GPU_layers_v3`: COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL; PID2201. Correctly rounded division repairs initial embeddings substantially. Later quantization/recurrent mismatch remains.

- Round9 `GPU_layers_v4`: COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL; PID2223. Native RMS order and recurrent KDA inference diagnostic. Read recorded errors; no export/parity claim inferred.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `distributed_core_data`: COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS; PID2511. Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.

- Round9 `core_pipeline_profile`: WAITING_FOR_CORE_DISTRIBUTED_V2; PID2780. Queued zero-update raw/redacted E/F controls plus unchanged-weight packed training throughput, explicit per-document KDA/convolution/attention/RoPE isolation and foreach optimizer comparisons. lr0 and resident batch; not5090, CPU codec timing or improved archive.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.

- Round9 `model_order`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Recover original container tensor order and independently verify all native reader tensor bytes. Adaptive weight-code order changes must not be confused with training. Native identity permits compositional reuse of the already independently decoded archives.


## A94 — Training-prior compression, cached native embeddings and data throughput

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route N>T; priority 1.

**What rigor was actually evidenced:** Exact sample prior-storage round trips and full old-transform inverse; cached-embedding equivalence remains a hypothesis. E21, E25.

**Actual testing versus required testing:** 48 storage probes cover107,479,040 bytes; raw zstd9 best fast sample50,901,611 bytes, not guaranteed full ratio. Full old-FX2 inverse reconstructs1 B exact; production lexical data/full priors remain unregenerated. Test streaming decode/read amplification and useful targets/dollar; if caching prior embeddings, prove fixed preprocessing and no other raw-prior use. Storage savings facilitate training; they are not archive gains.

**Combination work evidenced:** Data compression and recovery were executed to support training. Prior-embedding caching plus a complete trained model/export has not been tested.

**Stronger descendant to implement:** Reconstruct or compress native priors and cached inputs with exact index/order checks and bounded throughput buffers.

**Discriminating experiment:** Do not ship training-only caches; compute rented hours from measured throughput and mandatory export/verification reserve.

**Combination partners:** A17, A90, A93. Prerequisites: actual native final-bit trace; prefix-only feature contract; normalized complete outcome support; paired controls; packed-code/model cost and CPU/RAM.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `whole_word_alignment`: COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS; PID1505. Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.

- Round9 `native_layers`: COMPLETE_NATIVE_CORE_LAYER_OBSERVATION; PID1997. Observes4096native steps,205FP32priors and13activation stages. Observation only; no optimization claim.

- Round9 `GPU_layers_v2`: COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL; PID2139. Integer-dot forward improves first article, but later article probabilities still differ. No native parity PASS.

- Round9 `GPU_layers_v3`: COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL; PID2201. Correctly rounded division repairs initial embeddings substantially. Later quantization/recurrent mismatch remains.

- Round9 `GPU_layers_v4`: COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL; PID2223. Native RMS order and recurrent KDA inference diagnostic. Read recorded errors; no export/parity claim inferred.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `distributed_core_data`: COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS; PID2511. Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.

- Round9 `core_pipeline_profile`: WAITING_FOR_CORE_DISTRIBUTED_V2; PID2780. Queued zero-update raw/redacted E/F controls plus unchanged-weight packed training throughput, explicit per-document KDA/convolution/attention/RoPE isolation and foreach optimizer comparisons. lr0 and resident batch; not5090, CPU codec timing or improved archive.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.

- Round9 `model_order`: IMPLEMENTED_OR_PLANNED_AWAITING_LOCAL_RESULT; PIDNone. Recover original container tensor order and independently verify all native reader tensor bytes. Adaptive weight-code order changes must not be confused with training. Native identity permits compositional reuse of the already independently decoded archives.


## A95 — Warm full-history, complete package and eligible CPU/RAM validation

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route V; priority 1.

**What rigor was actually evidenced:** Many mini/native round trips and source/input hashes; no new full qualifying compressor package. E5, E21, E22, E25.

**Actual testing versus required testing:** Four2M lexical-checkpoint/native traces and fresh64K calibration E/F, plus1 B preprocessing inverse. A/B/C/D are cold pieces of the old FX2 transformed stream, not a full production lexical order. Build actual production data/package, run separate complete comp/decomp, verify1 B output hash and count all assets/options. Measure both calibrated CPU runs and peak warm RAM/disk; short-piece RSS and linear runtime projections do not qualify it.

**Combination work evidenced:** Individual components reached substantial correctness evidence. Their full matched joint package, mature memory history and source-to-submission integration remain incomplete. No 20% result or absolute optimum is established.

**Stronger descendant to implement:** Test warmed production history and actual self-contained compressor/archive with every loader, model, dictionary and option counted.

**Discriminating experiment:** Native independent decode of all one billion bytes, CPU Geekbench-normalized limits, peak RAM/disk and unchanged roundtrip hashes.

**Combination partners:** A41, A71, A93. Prerequisites: frozen native/export parity; correct complete-corpus weighted objective; actual asset-size accounting; matched capacity and compute controls.

- Round9 `native_adaptive`: COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES; PID2181. Two new512KiB cold slices with frozen policy. Full warm history, package, cross-CPU, eligible resource and full-corpus checks remain pending.

- Round9 `core_pipeline_profile`: WAITING_FOR_CORE_DISTRIBUTED_V2; PID2780. Queued zero-update raw/redacted E/F controls plus unchanged-weight packed training throughput, explicit per-document KDA/convolution/attention/RoPE isolation and foreach optimizer comparisons. lr0 and resident batch; not5090, CPU codec timing or improved archive.


## A96 — Rarity thresholds, masked losses, gradient allocation and common/rare specialists

Status: **OPEN_WITH_FINITE_DESCENDANT_IMPLEMENTATION**. Route T; priority 0.

**What rigor was actually evidenced:** New masking proposal: prior dictionary-only residual pilot did not test the original core or literals/OOVs.

**Actual testing versus required testing:** Census and tiny dictionary-target residual pilot; exact full-word core masking, representative data, specialists and native package checks were still required.

**Combination work evidenced:** Common/rare gradient diagnostic on a tiny head; the actual shared-core and specialist combinations were unimplemented before round9.

**Stronger descendant to implement:** Keep exact rare context, separate common/rare training gradients and use a normalized expert law with native fallback; charge any decoder frequency lookup.

**Discriminating experiment:** Corpus/article threshold census, masked/soft-weight/unweighted controls, shared-gradient versus frozen-backbone/separate-head controls, all-word native bit cost.

**Combination partners:** A15, A83, A85. Prerequisites: exact word/span mask alignment; matched useful-target exposure; all-target native evaluation; paid normalized class/mixing law.

- Round9 `core_short`: COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING; PID1718. Actual selected5.897M core, five loss-only masks,128steps,262KiBprefix only. Rare inputs remain visible in this branch. Later literal_split/known_literals and distributed_core test other masking subcases; those results must not be retroactively attributed here.

- Round9 `core_long`: COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT; PID2064. Six policies, two seeds and1152steps. Same early corpus and unresolved GPU/native numerical fidelity. Euclidean gradient projection with AdamW has no certified common-loss descent guarantee.

- Round9 `whole_word_alignment`: COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS; PID1505. Exact whole-word and literal/OOV spans on262KiBprefix, matched independently to native decoder. Corpus-wide training alignment remains pending.

- Round9 `core_export`: COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON; PID2314. Exact native-reader tensor roundtrip and native neural probability observations PASS. Important measurement correction: historical --transformer-only runs the network but Predict returns PPMD, so V2 archive sizes did not measure neural compression. V3 repairs that diagnostic and tests combined CM; do not promote V2 zero archive differences as neural results.

- Round9 `literal_split`: COMPLETE_REVERSIBLE_LITERAL_INPUT_MASK_SPLIT_NATIVE_SCREEN; PID2281. Three actual reversible input-redaction cutoffs on65KiB, final CM encode/decode; positions, literals and container bytes paid. Unchanged model only, Python side wrapper, previously viewed prefix, unmeasured eligible executable cost. Negative finite result does not reject better side models or content-first architectures.

- Round9 `known_literals`: COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN; PID2437. Three raw-context known-literal cutoffs, one masked-context branch and one trained common specialist on65KiB. Native Predict/Perceive still run for skipped coded bytes, independent decode/core identity PASS. All5 lose after the current side price. Full production wrapper, stronger side law, fullwarm/package and independent corpus remain open.

- Round9 `known_side_verify`: COMPLETE_INDEPENDENT_PAID_SIDE_HINT_RECONSTRUCTION_IDENTITY; PID58. Independently parse the paid HPKNOWN container alone, reconstruct every mask/value byte, prove identity with files used in all5 executed native decodes and original reconstruction. No frequency table/original input needed to construct hints; eligible native side-loader/full package still pending.

- Round9 `core_native_codec`: COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS; PID2539. Repairs diagnostic-only bit law and independently tests trained weights in actual combined CM on three64KiB slices. V2 neural probability/tensor results remain valid, its archive claims were misnamed. Fullwarm/original-corpus/package, cross-CPU and eligible resources remain open.

- Round9 `distributed_core_data`: COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS; PID2511. Six512KiB fragments with exact whole-word labels, true separator boundaries and independently regenerated raw/redacted1392 PPMD priors. Neutral extraction reproduces earlier tokens/priors exactly. First partial article excluded, cold classical priors; not full warm corpus.

- Round9 `distributed_core`: RUNNING; PID2602. Six policies times two seeds,384steps, actual selected core on A/B, develop C/D and core-fit-held-out E/F. Genuine redacted input with its own regenerated priors; actual Adam proposal projection with matched unweighted control. Quantized/native parity and finite-step first-order guarantees remain unresolved; actual code/export required.

- Round9 `core_selective`: RUNNING; PID2821. Six groups/objectives times two seeds,384steps. Selective unembedding/gates/last block updates versus paired all-core higher-lr and native-code-cell excess-displacement penalty. Penalty proxies code flips,not measured compressed bits. Native export and archive pricing required.