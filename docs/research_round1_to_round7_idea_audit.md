# Audit of ideas and research depth across rounds 1–7

Prepared 6 October 2026, Asia/Calcutta. This is an evidence audit, not a new compression experiment. It covers the recoverable proposals, variants, tests and combinations in the local reports, four idea files, preserved code and round-7 results. Repeated proposals are consolidated into numbered families with their cross-round history. The coverage appendix maps source sections to those families.

## Direct answers to the three questions

**1. No, the evidence does not support saying that every idea received the mathematical and engineering development of a mature architecture research project.** Some work was carefully engineered: causal probability normalization, exact WRT parsing, integer probability replay, independent native decoding, tensor-preserving loaders, and structural experts. Much of the architecture work was exploratory: small models, short training, fixed heuristic substitutions, single configurations or unexecuted designs. A rigorous rejection of a particular implementation was sometimes presented too broadly as a rejection of the underlying idea. That was a methodological weakness.

**2. Real experiments were conducted, but their scope was narrower than the strongest proposals.** Fixed lexical boosts did not implement learned relation selection, suppression and survival. Generic constructor packets did not implement a trained content-first infiller. Short, drifting QAT continuation did not settle compression-aware training. A neural likelihood improvement did not establish a smaller qualifying package. Each entry below records the actual test and the stronger test still required.

**3. There is evidence of substantial combination work, especially in round 4 and the round-6 structural system, but not an exhaustive, deeply optimized search over the proposed architectures.** There is no reliable record of hours spent thinking about each idea or combination. GPU minutes, elapsed calendar time, long reports and numbers of runs cannot establish those thinking hours. I cannot honestly answer “yes, hours on every idea.” The per-entry combination assessments below concern observable designs, implementations and ablations. This time limitation applies to every entry.

Your attention/Transformer comparison is a reasonable standard for asking for a fully specified architecture, controlled experiments and serious implementation work. The [original Transformer paper](https://arxiv.org/abs/1706.03762) describes an implemented architecture and measured task results. Our audit should be judged by similarly inspectable evidence, rather than by claims about intelligence or effort. Neither a mathematical formulation nor a large number of simplified probes establishes an optimal architecture.

## Scope, evidence strength and missing material

The standalone round-1 experiment ledger is **not present in the local inventory**. Round 2 reports 54 earlier runs, described as 18 ideas × 3 seeds, with three-layer models trained for 400 steps. Its summary identifies only grouped families. Therefore I cannot identify all eighteen original configurations or independently reconstruct their controls, losses and failures. Entries below cover every recoverable family; they are not a fabricated list of eighteen round-1 experiments. Recovering that original ledger would permit a finer audit.

A read-only attempt to inspect the newest supplied Kaggle session for that missing ledger returned `Kernel WebSocket connection failed`; no remote inventory was received. This does not establish that the session expired or that the ledger is absent remotely. The report can be completed from the preserved local evidence, with that limitation disclosed. E26.

Rounds 2–6 have narrative reports. Round 4 also has local source and a consolidated results JSON; round 5 has source; important round-6 source is preserved under `research_round7_sources`, although the `round6/` path named in its report is absent. Round-7 evidence is much richer: scripts, manifests, corrected result versions, native traces and local validation. This audit checked records and representative code; it did **not** rerun every historical GPU training job or independently rebuild every older claim. Where only a report survives, “reported” is deliberate.

Evidence labels used below:

| Label | Meaning |
|---|---|
| Reported | Historical result stated in a report; this audit has not reproduced the run |
| Proxy | Simplified model, generic codec, diagnostic ceiling or likelihood screen |
| Bounded native | Actual native archive/probability/round-trip evidence on the specified region |
| Component exact | A specified transform, tensor loader or storage component verified exactly |
| Design only | Equations/implementation plan exist, but the proposed mechanism has not been executed |
| Full qualifying | Complete counted submission, full independent enwik9 decode, measured eligible CPU/RAM/disk; **none of our new candidates has this evidence** |

“Partial rigor” is not the same as “bad experiment.” A small screen can be useful. It becomes inadequate when used to claim a universal negative, an absolute optimum, or a record improvement beyond its comparator.

## Findings that change the interpretation of earlier reports

1. **Round 1 was a preliminary screen.** Four hundred training steps cannot settle a substantially different architecture. The later statement that the novel families were “not worth more GPU time” was stronger than that evidence.
2. **Round 3's any-order losses are real reported losses, not a proof of their proposed cause.** The existence of many mask states does not prove that capacity dilution is the sole explanation. Training distribution, positional representation, schedule and optimization also differ. Within-model blanking removes the between-seed difference but is not “noise-free” evidence of an optimally trained control.
3. **Round 4 has the strongest documented joint exploration, but its 20.27% comparison uses a weak 6,000-step byte baseline.** Longer training and four snapshots contributed. Matched 18,000-step comparisons were 11.9%, or 8.6% against a cached byte control, in the toy system. These are not reductions against the record pipeline.
4. **New source-level accounting correction: round 4's enwik8 “total” is a one-model description-length estimate.** `dtok_full_eval.py:71` adds payload bits/8 + one `ship_bytes` + one dictionary. `dtok_full_cache.py:143` does the same. `ship_bytes` in `full_tok.py:54` estimates categorical entropy and scales; it does not write and measure a complete container with frequency tables, framing and loader. Executables and a second required copy are not present in that total. The reported 18.54 MB cannot be called a finished Hutter package or a verified 2.3% package win. Illustratively, using its rounded figures and duplicating the indicated model/dictionary gives about 22.09 MB versus about 21.51 MB for the byte control, before executable costs. This is an accounting illustration, not a corrected measured submission. Actual packaging can differ; it must be implemented and counted.
5. **Round 4's largest retained-state representation is not prize-sized.** Its recorded 25,792,942 half-precision vectors of width 288 require 14,856,734,592 bytes (14.86 decimal GB) for keys alone, before values, models, index and scratch. `full_tok.py` retains normalized half-precision keys. That configuration cannot satisfy a 10 GB total RAM bound as written. A compact or bounded alternative remains a different research hypothesis.
6. **Round 5's close aggregate GPU/native losses did not establish pointwise parity.** The later round-7 ordinary neural rows fail stricter comparison: mean absolute target-bit difference 0.0260231, maximum 2.01116, mean KL 0.00220386 bits. All 96 reset-fallback rows match. This does not erase independently validated native results; it does weaken reliance on that port for fine loss differences and core continuation.
7. **Round 6's structural gains are meaningful regional results.** The 274,829-byte sum comes from two fully scored tail regions. It is not a warm full-package improvement and has not been established on the different production lexical preprocessing. The lexical revision-tail transform already changes the timestamp opportunity.
8. **The approximately 54.9 KB round-7 packing-component saving belongs to the older uniform-Q4 FX2 checkpoint.** The lexical C3 conversion grows by 940 bytes per copy. Transferring the former saving to the latter package was incorrect.
9. **The completed round-7 batch is a carefully measured finite family, not the complete learned architecture search.** Its 15 fixed causal families save only 1.731295 ideal bytes across 8M input bytes in their shared mixture. The tiny learned calibration gains on development did not survive fresh native E/F: archives grow by 1 and 3 bytes, before model/code tax. Learned contextual memory and a residual transformer remain untrained.
10. **Several stopping dependencies were too restrictive.** Faithful core GPU inference is necessary for trustworthy continuation of that core. It need not block an independent residual model trained on native-produced causal features and final coded probabilities. Failure of an additive unigram expert is not a necessary precondition for success or failure of a context-dependent residual architecture.
11. **The research selection was too anchored to preserving the existing pipeline.** Preserving its stream made tests easier to validate, but it also left the defining learned mechanisms of several proposals untested. Round 5's arguments that cmix already supplies context mining or that Kimi forget gates already provide TTL did not establish that a different learned associative state is redundant. Deterministic features can improve a finite model without adding information beyond the full history. Similarly, an estimated full scratch-training cost did not establish that every adapter, independent residual or changed representation requires that same training procedure.

## Research depth by round

| Round | Mathematical/engineering development actually evidenced | Testing depth versus what was needed | Combination depth actually evidenced |
|---|---|---|---|
| 1 | Recoverable summary of small exploratory models and transforms; original eighteen-idea identities missing | Three seeds reported, but 400-step training and tiny samples do not settle architectures | Original combination ledger unavailable |
| 2 | Capacity/quantization, distance atlas and causal adaptation formulation | Larger models; mostly one seed, weak classical control, nominal/entropy storage and no CPU codec | Ternary + adaptation + classical blending tested |
| 3 | Paid feedback, decoding-state matching, word-length and memory controls | Broader variants and some seeds; short training, ideal losses, optimistic memory statistics and overgeneralized negatives | Scratch + TTL tested; full word-length/scratch/TTL/CM stack proposed only |
| 4 | Implemented dictionary/algebra/miner system and iterative mixer repair | Strongest joint toy experiment; mismatched training baseline, one-copy entropy totals, large GPU retrieval bank and no prize CPU | Substantial actual combinations and ensembles; eligible deployment absent |
| 5 | Native pipeline, exact transforms, loaders and executable packing | Component/slice tests; aggregate GPU parity inadequate, transformed-stream training mismatch and projected joint total | Native components combined partly; complete compression result projected |
| 6 | Causal structural distributions, parser/integration and regional native checks | Strong metadata measurements; QAT control drifts, cold regions/full lexical transfer not resolved | Multi-expert structural combination tested; full package unmeasured |
| 7 | Detailed probability algebra, integer graphs/traces, corrected EOF and independent native checks | Extensive finite probes; little learned architecture execution, cold older-stream samples, no full qualifying package | Many fixed experts mixed; proposed shared learned relation/placement/latent/infiller not trained |

**Thinking-hours evidence is unavailable for all seven rounds.** This table describes inspectable work, not a retrospective estimate of mental effort. Some individual runs have GPU/CPU durations; those durations are not hours of architecture reasoning.

## Mathematical and experimental standard used in this audit

These are the tests a mature implementation should meet. References M1–M9 below let individual entries specify additional requirements without repeating the entire protocol.

**M1 — Complete objective and actual packaging.** Optimize the counted package, not prediction accuracy or nominal parameter bits:

\[
S=B_{\rm payload}+\sum_j m_j B_{\rm asset,j}+B_{\rm framing/options}.
\]

Here each multiplicity \(m_j\) follows the actual submitted representation. Two model copies are appropriate for the pipeline considered in these reports, not a universal axiom for every submission. Measure finished containers and binaries. The [official rules](https://www.hutter1.net/prize/hrules.htm) count compressor plus self-extracting archive, specify alternative accounting, require exact reconstruction without external input, and impose CPU, memory and temporary-disk constraints. Use the published CPU-calibration formula, rather than an unqualified fixed “50 hours.”

**M2 — Causal, complete probability model.** Before decoding \(x_t\), every inference feature must be a function of the known decoder state, previously decoded data, supplied fixed model assets, or explicitly transmitted side information. Future outcomes may be training labels or paid encoder choices. They may not choose an untransmitted gate. Normalize over **all** possible outcomes, including literal words, case, markup, escapes, termination and partial EOF prefixes.

**M3 — Representation cost and right context.** For an exact split \(x\leftrightarrow(C,A,G)\), score

\[
L(C)+L(A\mid C)+L(G\mid C,A)+L(\text{models/code}).
\]

The grammar model may use both content neighbors only after their information has been decoded through C/A. A set does not preserve order or multiplicity. For a multiset with counts \(n_i\), an enumerative order index may need \(\log_2(n!/\prod_i n_i!)\) bits before contextual compression; repeated identical words reduce this permutation count, not the need to represent the actual sequence.

**M4 — Finite predictor versus information.** If memory \(M=f(H)\) is deterministic from full history, \(I(W;M\mid H)=0\). It can still improve a finite baseline representation \(B=g(H)\), for which \(I(W;M\mid B)\) need not vanish. “No new information” does not dismiss a useful feature. Reversible feedback preserves ideal information but may change approximation difficulty. Neither fact guarantees a practical gain.

**M5 — Controlled comparisons.** Record data/order, useful loss-bearing token exposure, model/storage budget, compute, seed, optimization and model calls. Equal steps alone do not imply equal raw-text context or useful training exposure. Match generic-capacity, spelling/random-projection, empty-memory, neutral-stage and shuffled/availability controls. For small stochastic training effects, use multiple paired seeds and report dispersion; deterministic fixed-corpus compression has one exact full-file size. Already examined slices are development data, not fresh confirmation.

**M6 — Faithful implementation and native validation.** Require reference versus neutral byte/probability identity, proper parser tests, independent encoder/decoder processes, exact output hashes, stable integer rounding, and actual archive size. For changed core weights, use the candidate's own causal mixer trajectory. A probability replay is only equivalent when integration leaves baseline state updates unchanged. Report compiler/PGO flags, startup costs, warm RSS and CPU, not GPU speed as a CPU qualification.

**M7 — Feature algebra and generative semantics.** The five proposed moment functions span only three independent functions: \(A_{1-u}=A_0-A_u\) and \(A_{(1-u)^2}=A_0-2A_u+A_{u^2}\). Finite moments can collide. Fixed glyph moments are a linear map of the corresponding one-hot moments; their role is inductive bias/parameter sharing, not extra information. Soft alignment energy \(-\tau\log\sum_\pi e^{-C(\pi)/\tau}\) is not automatically a metric or normalized edit probability. Use a specified score normalizer or a proper pair-HMM with termination.

**M8 — Benefit, hazard and interactions.** A one-candidate optimum \(a^*=\operatorname{logit}(r)-\operatorname{logit}(p)\) requires \(r,p\) to refer to the **same next-event** Bernoulli outcome. Horizon recurrence is \(1-\prod_d(1-h_d)\), not next-word probability. Charge all nonoccurrences and normalization losses. Joint logit fields may double-count correlated evidence; measure interactions, not the sum of individually helped targets. A Bayesian whole-sequence expert mixture pays selection regret; an unpaid best expert per bit is not such a mixture.

**M9 — Stronger test before broader conclusion.** Preregister a finite implementation and development/confirmation protocol. A failed probe can justify stopping that implementation. To reject a broader architecture, test its defining interactions and training procedure, or derive a valid upper bound for the stated family. An oracle's restricted support budget is not an unrestricted entropy limit. Retain alternative branches where the probe omitted the proposed mechanism.

## Per-idea audit: original representation and early model ideas

### A01. Render text to images and recover it by OCR — rounds 1, 3, 7

**1. Rigor applied:** Correct information-preservation objection and rough model/CPU economics; reported small raster/OCR screens. No mature neural OCR codec or optimized renderer/residual architecture is evidenced. E1, E2, E8.

**2. Actually tested → needed:** Round 1 reports image/pixel forms worse than zlib. Round 3 emphasizes symbolic geometry instead. A fair literal OCR test needs an injective representation or explicit correction stream, renderer/font and OCR bytes, exact reconstruction, and matched text/raster models and CPU. M1–M3 apply. The cheap screen reasonably lowers priority; it does not prove every visual predictor impossible.

**3. Combination work:** Geometry was combined with other features, but a trained OCR predictor plus correction coder was not jointly optimized. No per-idea thinking hours are documented.

### A02. Low-resolution glyph codewords plus ambiguity residuals — rounds 1, 7 proposals

**1. Rigor applied:** The idea file explains why blur transfers information into corrections. That is a valid constraint, not a measured optimum. E8.

**2. Actually tested → needed:** The earlier report groups low-resolution/pixel attempts without a recoverable separate ledger. Specify the glyph alphabet, collision classes, exact byte/case/Unicode escape, and learn a joint glyph/residual distribution. Compare its complete codelength against a symbolic class/residual codec at equal cost. Do not count discarded ambiguity as compression.

**3. Combination work:** Conceptual connection to shape classes exists; no recorded optimized glyph-plus-residual system. This remains a low-priority alternative, not a completed architecture rejection.

### A03. CNN or other spatial predictor over rendered decoded history — original idea variants

**1. Rigor applied:** Compute concerns were discussed; no explicit trained causal CNN result is identified. E8.

**2. Actually tested → needed:** Geometry lookup and shape tables are not a CNN. Define deterministic rendering of past context, fixed causal crop/padding and output probabilities; compare a same-budget character CNN and random spatial encoding. Price render/startup cost and every output. A tiny pilot can evaluate whether spatial inductive bias pays before writing a large system.

**3. Combination work:** Listed as an alternative expert, not integrated with the transformer/final coder. No evidence of architecture or kernel optimization for this variant.

### A04. Glyph features and factorized character embeddings — rounds 1, 3; idea 2

**1. Rigor applied:** Multiple seeds and random/identity controls in round 3 were better than the initial 400-step screen. The tiny 256-byte embedding saving was recognized. E1, E2, E8.

**2. Actually tested → needed:** Geometry residual gains were approximately 0.105–0.106%, versus random 0.080% and identity 0.072%; attributed incremental signal was about 0.0004 bpb. Test fixed glyph versus equal-rank random/learned projections with matched extra parameters; separately test an actually factorized embedding's stored size. M7 prevents claiming redundant glyph features add information.

**3. Combination work:** Geometry was tested alongside residual modeling and classical contexts. It was not extensively co-designed with the later learned word-relation/placement architecture.

### A05. Shape-class-first hierarchy and integer shape contexts — rounds 1, 3

**1. Rigor applied:** Explicit shape→character factorization and classical comparisons; partial model matching. E2, E8.

**2. Actually tested → needed:** Geometry-context CM scored 1.853 bpb versus random 1.847 and handmade classes 1.842; shape-first 1.917 versus 1.889 baseline, with random shape-first 1.925. Those are particular class choices. Optimize class alphabet/count smoothing and residual distributions under actual class-table cost; compare with ordinary character n-grams in the same mixer and measure CPU.

**3. Combination work:** Hierarchical and residual versions were compared, but class design plus stronger learned syntax/word models was not jointly trained. Rejecting these layouts is supported; rejecting every useful character grouping is not.

### A06. Confidence-gated orthographic/glyph residual expert — rounds 1, 3, 7

**1. Rigor applied:** Valid causal mixture/logit correction equations; small residual screens. The full proposed feature set and learned gate have not been implemented together. E2, E8, E9.

**2. Actually tested → needed:** Early hard-word/shape specialists and later fixed geometry boosts are substitutes for a learned context-dependent residual. Train a compact model using preceding spelling, prefix/suffix, parser state and baseline uncertainty, with all false alarms in normalized loss. Include identical-capacity generic-feature controls and final-bit supervision; freeze/export and confirm natively. A target's observed error cannot select its own gate.

**3. Combination work:** Proposal-level synthesis is substantial; tested joint learned orthography × syntax × uncertainty interactions are missing.

### A07. Feed additional classical-model predictions into the neural expert

**1. Rigor applied:** The idea file identifies existing signals as inexpensive candidate inputs. No comprehensive input-ablation study is recorded. E8, E17.

**2. Actually tested → needed:** Mixing neural and CM outputs is not training the transformer on extra classical channels. Collect causal model distributions/states, specify their quantized interface, and compare PPMD-only, selected extra channels and equal-width/random controls. Measure extra inference/serialization cost and final coder gain. The baseline update order must expose the signal before the predicted bit.

**3. Combination work:** Discussed as a way to reuse already computed information; no recorded trained multi-signal model. Its dependency is native feature collection, not necessarily a full replacement transformer.

### A08. Sorted dictionaries and reversible 2D/aligned symbolic organization — rounds 1, 4, 5

**1. Rigor applied:** Sorting/storage probes and several word-code groupings; no optimized alignment transform with complete reconstruction metadata. E1, E3, E4, E8.

**2. Actually tested → needed:** Round-1 sorted forms lost; round-4 prefix/suffix/distributional groupings improved toy neural loss; round-5 dictionary front-coding grew. These test different objects. A genuine aligned-text codec must preserve occurrence order, row/column placement, exact spelling and exceptions, then train its predictor on that representation. Compare total streams/model cost, not dictionary bytes alone.

**3. Combination work:** Word grouping plus letter embeddings was implemented. The broader spatial/alignment transform plus matched neural decoder was not. Do not merge their conclusions.

### A09. Wordle/progressive feedback, multiple proposals and feedback alphabets — rounds 1, 3

**1. Rigor applied:** Feedback costs, decoder determinism and reversible-refinement mathematics were addressed; equal-model-call comparisons were useful. E2, E7.

**2. Actually tested → needed:** Reported 3/5/9-call Wordle schemes lost 4–20% against parallel character decoding with the same calls. Small early PCC screens also lost. Define full feedback alphabets, rejection/termination and residual probabilities; train on the exact reachable refinement states and optimize a registered proposal policy. Compare richer feedback, binary locks and rank coding at matched CPU/model cost. The single-byte identity explains no inherent advantage, not universal practical failure.

**3. Combination work:** Feedback versus direct reveal and skeleton variants were compared. The article retrieval + shared heads + masked decoder proposed in the file was not implemented as a jointly trained system.

### A10. Confidence-ordered any-order/bidirectional decoding — rounds 1, 3

**1. Rigor applied:** Deterministic position selection and matched decoded-state training were studied. The search over schedules/architectures was limited. E2, E7.

**2. Actually tested → needed:** At 2,500 steps, L2R 1.703 versus block4 2.099, block16 2.450, block64 3.922 bpb. Small own-training-text models also favored L2R. Test optimized schedule entropy/ties, actual reachable state distribution, causal masks for what is decoded, positional design, blockwise caching and multiple paired training budgets. Demonstrate convergence of the comparison rather than assume it from 20 passes. Full right-context information must be paid first.

**3. Combination work:** Blocks, skeletons, adaptation and warm starts were explored. No mature bidirectional model with article memory, shared heads and production decoding kernels is evidenced.

### A11. Structure/skeleton first, article/block hierarchy and shared heads — rounds 1, 3

**1. Rigor applied:** Classical and neural skeleton splits were tested. The full hierarchy/shared-network proposal remained only partly represented. E2, E7.

**2. Actually tested → needed:** Classical skeleton costs 1.942–2.000 versus 1.864; stronger skeleton 1.905. Letters became 9.7% cheaper while spaces became 51% more expensive. A fair architecture test jointly optimizes structure, positions, capitalization, markup, residuals and a shared conditional decoder. Measure all streams under M3; compare separately trained heads versus shared heads and charge schedule/state cost.

**3. Combination work:** Skeleton + masked prediction/adaptation was tried. Article-level state plus paid structure and retrieval was proposed, not realized. These failed skeleton choices do not exhaust hierarchical factorization.

### A12. Word length first with separate/shared structural heads — round 3

**1. Rigor applied:** Two seeds, explicit length/punctuation/letter costs and classical-blend comparisons constitute a useful focused study. E2, E7.

**2. Actually tested → needed:** Mean neural improvement about 0.77%; final weak-classical blend worsened about 0.20%. The length model saw roughly 15% fewer training bytes. Match raw-text exposure and exact length/case/escape cost, compare shared-head versus independent structure parameters, then evaluate a real final coder. A standalone neural gain is insufficient.

**3. Combination work:** Length + classical blend was tested. The proposed length + scratch + TTL + length-aware CM combination was not run, although the report recommended it.

### A13. Whole-word proposals, candidate-rank coding and spelling fallback

**1. Rigor applied:** A plausible rank/escape factorization was specified. No direct mature candidate-rank codec result is recoverable. E7, E18.

**2. Actually tested → needed:** Two-token dictionary groups and later word-tree experts are related, not equivalent. Specify a deterministic prefix-derived ranked candidate set, normalized rank/escape probabilities, exact spelling/case fallback and candidate-search cost. Compare direct word softmax/tree coding, ranked proposals and iterative refinement using the same word features. Misses and selector bits count.

**3. Combination work:** Conceptual morphology/retrieval/rank/fallback pipeline exists; no measured end-to-end combination. It should not inherit Wordle's negative result without its own test.

### A14. Train on decoder-reachable states; autoregressive warm start

**1. Rigor applied:** Round 3 explicitly addressed train/decode mismatch, which is valuable. Optimization depth remained bounded. E2, E7.

**2. Actually tested → needed:** Decoded-state matching improved a losing family from 2.633 to 2.485 bpb. Warm-start plus 1,000 steps remained worse than the L2R control. Test on-policy decoded-state sampling, schedule curricula, joint structure/content objectives and equal useful-target/compute controls; ensure warm-start position/mask distribution and optimization are compatible. One failed warm start does not exclude pretrained adaptation.

**3. Combination work:** Matched states were combined with skeleton/any-order models. No longer, multi-seed, jointly tuned retrieval/skeleton training followed.

### A15. Hard-word specialists and targeting cumulative residual cost

**1. Rigor applied:** Early reports identified rare names, first letters and long-distance repeats; round 7 used actual final-bit attribution. That diagnostic rigor improved substantially. E1, E3, E9.

**2. Actually tested → needed:** Round 1 reports roughly 1% specialist gain on a weak base. Later atlases show frequent known words can dominate aggregate bits. Rank total final-coded cost, not rare types or striking examples. Train a causal specialist with a confidence gate and all misses, compare generic capacity, and check whether named difficult categories retain gain after the final mixer. Diagnostic target labels cannot become inference features.

**3. Combination work:** Diagnostics informed cache and word-model proposals. A residual-cost-trained full lexical specialist has not been executed.

## Per-idea audit: capacity, adaptation and memory development

### A16. Capacity per stored byte: float, Q4, Q3 and ternary networks — rounds 1–2

**1. Rigor applied:** Matched data/steps and a capacity/storage table; actual exported file/coder/CPU comparison is missing. Early halfway quantization was especially weak. E1.

**2. Actually tested → needed:** Round 2 reports 6.3M Q4 1.516 bpb, 8.5M Q3 1.537, 14.9M ternary 1.477, 14.9M float 1.393. “Equal size” used nominal budgets, while entropy estimates differ. Train matched rate–distortion frontiers, export every asset, benchmark real ternary sparse/add kernels and compare complete package at eligible CPU time. Parameter multiplication is not free.

**3. Combination work:** Ternary + online adaptation + weak CM was tested. Optimized ternary kernels and later production-core retraining were not completed.

### A17. Exact weight entropy coding and conditional tensor codecs — rounds 2, 5, 7

**1. Rigor applied:** Strongest on the exact older-FX2 round-7 component: all tensors, independent loaders and native probability/archive identity. Initial generic entropy proposals were only estimates. E1, E4, E11.

**2. Actually tested → needed:** Round 5's simple row/column contexts mostly lost; generic round-7 alternatives were at best 289 bytes larger. Reproducing the published C5 tensor/histogram/column codec saved 28,200 bytes/copy; added packed loader 768/copy leaves 54,864 bytes for two copies. Actual lexical C3 grows 940/copy. Preserve checkpoint-specific results; complete production packaging/PGO remains necessary. Credit the published codec rather than call its reproduction a new architecture breakthrough.

**3. Combination work:** Exact packing was combined with BF16 variants and a loader-size screen. Its savings cannot be added to an incompatible lexical checkpoint.

### A18. Longer windows, sparse long-range attention and match-fed context — rounds 2–3

**1. Rigor applied:** Residual-distance atlas and a 2,048-context run; no broad attention/caching design study. E1, E2.

**2. Actually tested → needed:** Rare repeats 512–2,048 bytes back improved 15.4→10.3 bits; overall 1.509 versus 1.483 bpb worsened with changed training circumstances. Match useful exposure and optimizer, then compare larger window, sparse long-range links, recurrent summaries and match-model inputs under equal inference cost. Optimize masks and positional encoding for the extended context.

**3. Combination work:** Longer-context observations motivated TTL/cache studies. Sparse attention and a trained match-fed transformer remained proposals, not completed alternatives.

### A19. Full-network decoder-side online adaptation — rounds 2–4

**1. Rigor applied:** Decoder-reproducible updates after observed windows and several learning rates; exact CPU/export trajectory remains unverified. E1, E3.

**2. Actually tested → needed:** Float 1.483→1.463, ternary 1.477→1.436 with lr 1e−5; larger rates hurt. Later dictionary adaptation stacked with caches. Implement native update order, starting quantized weights, optimizer state/precision and rescaling identically; price backward passes and storage/RAM. Compare learning schedules at fixed CPU rather than assume the GPU gain qualifies.

**3. Combination work:** This is a genuine combined line of inquiry with CM, caches and kNN. It was not optimized into a measured CPU-constrained submission.

### A20. Selective adaptation: output head, norms, last MLP/layers — rounds 2, 5

**1. Rigor applied:** Actual production-related head and deeper adaptation code; selective choices were limited. E4, E13.

**2. Actually tested → needed:** Head improves neural loss 0.63% but native archive only 194,669→194,626 bytes. Head + last MLP improves neural loss 0.77% with about 10% added CPU. Test causal gradients and low-rank/norm subsets at equal update time, and assess complete final-coder costs on multiple warm strata. “cmix already does this” is an interpretation of these arms, not a theorem about adaptation.

**3. Combination work:** Added to the existing coder; not jointly optimized with learned lexical residuals or a changed base model. Production time headroom can reasonably limit further investment.

### A21. Fast article deltas, two-timescale adaptation and reset policies — round 5

**1. Rigor applied:** Implemented variations on a slow delta, but a narrow schedule/state search. E4, E13.

**2. Actually tested → needed:** Fast and two-timescale variants reportedly worsened. Specify reset/momentum/carry rules and compare equal update work, regularized fast state, slow shared state and meta-learned initialization. Use held-prefix updates and candidate's own mixer state. A losing untrained fast branch does not disprove a trained adaptation policy.

**3. Combination work:** Adaptation timescales were combined experimentally. No architecture-level meta-training or learned article controller is recorded.

### A22. Neural adaptation plus classical context mixing — rounds 2–4

**1. Rigor applied:** Actual factorial-style comparisons show overlap and stacking; early CM is explicitly weak. E1, E3.

**2. Actually tested → needed:** Ternary frozen 1.477, adapted 1.436, adapted + CM 1.405; frozen + CM 1.421. These are useful toy results. Repeat with equal stored/model cost and an actual strong final coder, including neutral integration and CPU. Decompose whether adaptation supplies information not already recovered by the stronger mix.

**3. Combination work:** Yes, this combination was implemented and measured. That evidence is much stronger than a claim that every later proposal received the same treatment.

### A23. Carry transformer state across article boundaries — round 5

**1. Rigor applied:** A frozen state-carry intervention, not a model trained for the new boundary semantics. E4.

**2. Actually tested → needed:** Reported +11.8% / +1.2% loss on two slices without finetuning. Train a matched carry/reset model, inspect state stability, and compare summaries/retrieval with the same boundary information. Preserve actual causal order and document piece resets. The negative test supports rejecting that frozen intervention; it does not reject learned cross-article memory.

**3. Combination work:** Limited to state carry within the existing pipeline. A trained cross-article architecture plus lexical gating was not executed.

### A24. Empty/register scratch slots — round 3

**1. Rigor applied:** Explicit empty versus memory-content controls were a good design decision. Short single-run rankings remain uncertain. E2.

**2. Actually tested → needed:** Plain 1.7439, 128 empty 1.6981, 256 empty 1.7235 bpb after 2,500 steps. Compare equal parameter/compute models, multiple paired seeds, different register placement and longer training; measure whether added capacity or architecture explains the gain. Price registers' parameters and operations.

**3. Combination work:** Scratch + keep-alive memory was actually built. Register count and content-model design were not brought to an optimized long-training frontier.

### A25. Learned context TTL / reuse selection — rounds 3, 7

**1. Rigor applied:** A logistic reuse scorer on 5.3M examples and several memory choices; future-dependent global-frequency/link assumptions were acknowledged. E2, E16.

**2. Actually tested → needed:** Scorer uses age/title/count/frequency; stored words selected by reuse probability × estimated savings / bytes. 128 keep-alive model scores 1.7206 versus its blanked 1.7400. That is not a directly trained gain/hazard optimizer. Fit prefix-visible survival and future **final-bit** benefit, exclude optimistic future statistics, use same-capacity independent controls, and train the exported selector jointly. M8 is essential.

**3. Combination work:** Tested with scratch and weak CM. Round-7 fixed TTL16/128 probes did not implement the learned selection or context-dependent survival proposed later.

### A26. Encoder searches helpful context and transmits keep/drop choices — round 3

**1. Rigor applied:** Paid selector analysis correctly exposed a large cost for per-candidate choices. The searched coding family was narrow. E2.

**2. Actually tested → needed:** Reported oracle choice costs 10.1% for all candidates, 4.1% top 100, 2.1% top 30, 1.0% top 10. Compare block/article-level amortized selectors, shared priors, structured choices and null mode with actual payload savings. A transmitted selector helping many targets is different from individual keep/drop flags. Do not reject all paid context based on this family.

**3. Combination work:** Selector cost was analyzed relative to TTL's budget, not incorporated into a learned complete compressor. Later article latents revisit the broader hypothesis.

### A27. Linked-article memory and tiny learned knowledge representations — rounds 3, 7

**1. Rigor applied:** Link-memory ablation and explanation of reconstructible history versus stored facts. No mature semantic/knowledge architecture. E2, E7, E18.

**2. Actually tested → needed:** Linked-article memory 1.7142 versus blanked 1.7150, with optimistic indexing conditions. Define only already decoded articles as donors, count index/selector model, compare title/link identity, random donors and summary capacity. Learned facts in weights must pay actual bytes; an external knowledge database cannot be assumed available.

**3. Combination work:** A link-memory model was trained; broader retrieval + progressive decoding + tiny fact representation stayed conceptual.

### A28. Scratch + learned keep-alive memory + length-aware coding — round 3

**1. Rigor applied:** The scratch/TTL pair has actual model ablations; the larger proposed combination is incomplete. E2.

**2. Actually tested → needed:** 128 empty + 128 keep-alive scores 1.7012, versus its blanked half 1.7289; weak-classical blend 1.5518. Same-trained-model blanking is useful but not an independently optimized no-memory control. Run a paired factorial design for scratch, TTL, word length and matched CM, with longer exposure and seeds. Charge full package and CPU.

**3. Combination work:** Pairing scratch and TTL was substantive. Adding word length and a length-aware classical model was recommended but not executed; do not describe the entire four-part stack as tested.

## Per-idea audit: dictionary and context-miner systems

### A29. Frequency, anagram, prefix, suffix and distributional word-code groups — round 4

**1. Rigor applied:** Five explicit layouts with the same word-model architecture/steps; actual code and results survive. Useful representation research, short of mature production optimization. E3, E12.

**2. Actually tested → needed:** Toy bpb: frequency 1.4624; anagram 1.4367; alphabetical 1.4283; suffix 1.4231; distributional 1.3974. Dictionary sizes vary 150–237 KB. Match raw-byte exposure, contexts, actual entropy-packed assets and seeds; test hierarchical/shared morphology alternatives against the strongest production WRT. Code adjacency can help finite models without being intrinsically a shorter word code.

**3. Combination work:** Grouping + letter embeddings + miners + token CM was genuinely developed. This positive evidence should not be dismissed because later fixed neighbor boosts fail.

### A30. Start-position, end-position and bag-of-letter embeddings — round 4

**1. Rigor applied:** Explicit compositional embeddings and two layout comparisons. No isolated equal-capacity random or learned generic-feature control reported. E3, E12.

**2. Actually tested → needed:** Alphabetical 1.4283→1.4069 (1.5%); distributional 1.3974→1.3823 (1.1%). Test each component, tied/untied embeddings, order-sensitive n-grams and same-parameter learned projections at matched exposure. Price embedding tensors and dictionary metadata. Gains establish a promising trained inductive bias in the toy models, not a production percentage.

**3. Combination work:** Yes, actual integration with dictionary models and subsequent miners. Optimal basis/rank, quantization and later associative use remain unresolved.

### A31. Token-level classical CM and mixer topology/initialization — round 4

**1. Rigor applied:** Iterative implementation work addressed a concrete failure. This is among the better engineered combination studies. E3, E12.

**2. Actually tested → needed:** Token CM 1.7365 versus byte 1.8245. Initial neural/CM mix 1.2573 worsened the neural 1.2430; changing bias and 12,288→960 weight contexts improved mixing. Compare neutral topology, trained mix and same context budgets on confirmation pieces, then actual range coding/CPU. Seven mixer choices on the test articles introduce selection bias into the final score.

**3. Combination work:** Implemented with neural cache/adaptation/kNN and ensembles. Its iteration shows real engineering, but there is no eligible native package evaluation of that final stack.

### A32. Hidden-state cache over already decoded current text — rounds 4, 6

**1. Rigor applied:** Strict earlier-position masks, normalized continuation distributions and causal confidence buckets in source. Later real-coder screens corrected an accumulator bug. E3, E5, E12.

**2. Actually tested → needed:** Byte model 1.4829→1.4242; dictionary cache also helped. Round-6 final-coder cache only about 0.045%/0.084% after correction. Implement bounded integer/compressed keys and an actual native query path, test same work random/exact controls, and measure warm RAM and eligible CPU. Dense 16K×192 comparisons per byte are not a demonstrated practical search kernel.

**3. Combination work:** Extensively stacked with adaptation/kNN/CM. Compression of the cache and joint learning of retrieval/gates were not developed to a prize-feasible frontier.

### A33. Cross-article kNN over decoder-reconstructed hidden states — round 4

**1. Rigor applied:** Causal prior training articles, GPU blocked exact retrieval and several datastore sizes; CPU/RAM qualification absent. E3, E12.

**2. Actually tested → needed:** Larger banks improve toy loss; recorded bank reaches 25,792,942 half vectors. This exceeds 10 GB for vectors alone at width288. Test bounded reservoir/article summaries, product/int8 codes, approximate search recall and total CPU/RAM on a native decoder. Preserve availability offsets and price index work; GPU blocked search is not eligible inference.

**3. Combination work:** Substantial integration and bank-size scaling, including shared retrieval across snapshots. No engineered resource-feasible replacement bank was measured.

### A34. Dictionary + algebra + adaptation + cache + kNN + CM — round 4

**1. Rigor applied:** A real multi-component system with intermediate ablations, not merely a proposed combination. Baseline fairness and actual score constraints remained incomplete. E3, E12.

**2. Actually tested → needed:** Matched 18K byte model 1.3752 versus combined 1.2117; byte-cache control 1.325 narrows the relative gain. Later banks/training improve further. Compare useful exposure, parameter/package cost, retrieval availability and CPU at equal budgets. Run all component removals in a matched strong baseline and a complete eligible codec before projecting to enwik9.

**3. Combination work:** This is the clearest “yes, experimentally combined” case. It still does not document hours of thought per idea or global architecture optimization.

### A35. Snapshot ensembles, linear/geometric mixtures and shared searches — round 4

**1. Rigor applied:** Multiple snapshot combinations, probability normalization and online bucket selection are implemented. Cost and repeated test selection are not fully priced. E3, E12.

**2. Actually tested → needed:** Two/three/four models reach 1.1871/1.1841/1.1824 bpb; shared retrieval slightly worse at 1.1854 than member-specific 1.1841. Measure every stored snapshot, lookup, forward pass and native CPU. Compare compressed deltas, distillation and equal-capacity single models; freeze selection before fresh evaluation. The four-model 20.27% toy gain is not a record comparison.

**3. Combination work:** Real diversity and search-sharing experiments occurred. A low-cost distilled joint model and final complete package were not built.

### A36. Train/overfit the exact corpus; model description versus payload — rounds 3–4

**1. Rigor applied:** Own-training-text arena and 100 MB scoring recognized the correct fixed-corpus objective. Stored-size accounting remained a proxy. E2, E3, E12.

**2. Actually tested → needed:** Round 4 reports 10-pass byte 18.98 MB and dictionary/cache 18.54 MB using entropy-size estimates and one copy. Build actual quantized containers, include every required copy and code, and independently decode. Corpus-specific training is allowed, but a memorized table/latent must be stored and charged. Evaluate net rate–distortion at the full corpus, not held-out percentage alone.

**3. Combination work:** Overfit models were combined with miners; the strongest full stack was scored only on test articles, not encoded as a whole submission.

## Per-idea audit: production pipeline, metadata and storage

### A37. Port fxcm_v26 lexical contexts into the FX2 transformer pipeline — round 5

**1. Rigor applied:** Actual classical-model source integration preserving transformer priors and two native-related comparisons. Resource measurement was noisy. E4.

**2. Actually tested → needed:** Reported slice archives 194,183→193,404 and 428,199→427,132 (0.40%/0.25%). Measure full warm total, matched compiled flags, CPU/RAM and mixer state. It adds roughly 11–15% runtime in those estimates and is already part of the lexical comparator; it cannot count as a new gain on that comparator.

**3. Combination work:** Integrated with the existing neural coder and proposed tail/storage changes. Their joint full package was not measured.

### A38. Timestamp-first revision records and revision-ID residual transform — round 5

**1. Rigor applied:** C++/Python byte agreement, whole preprocessing round trips and preserved split line count are strong transform engineering. Model matching was incomplete. E4, E13.

**2. Actually tested → needed:** On 100K records, neural + cmix 810,234→763,359; roughly 114 KB whole-region projection. Reordered metadata changes the model's trained stream. Test a matched retrained/finetuned conditional model, exact reversal and full final package; compare the stream-preserving timestamp expert under the same production baseline.

**3. Combination work:** Combined with title-copy transformation for exact inversion. The projected compression sum was not a full joint neural/package result.

### A39. Interlanguage owner-title copy transform — round 5

**1. Rigor applied:** Owner alignment, eight genuine empty-title escapes and 244,173 replacements were handled, with exact transform round trips. E4, E13.

**2. Actually tested → needed:** 30K-block cmix-only 736,486→698,705; around76 KB extrapolation without transformer. Measure neural final coder on all transformed blocks and the actual lexical layout; keep exact escapes/case/ordering. Compare stream-preserving copy experts to avoid the changed-stream training mismatch.

**3. Combination work:** Exact inversion combined with the revision transform. Its compression interaction with changed neural data remained a projection.

### A40. Store selected float parameters as BF16 — round 5

**1. Rigor applied:** Actual container and native decoding work, plus loss checks. This is a lossy model-numeric change, not automatically exact storage. E4, E11.

**2. Actually tested → needed:** 2,930,652→2,874,742 bytes/copy; small neural loss differences lead to an estimated108 KB net. Independently distinguish tensors already exactly BF16 from rounded tensors, compare all changed native probabilities, final archive and complete CPU/package. Do not call the model byte-identical when arithmetic values change.

**3. Combination work:** Combined with exact C5 codec conversion in round 7 for this older checkpoint. Transfer to nonuniform lexical tables requires its own numeric/export audit.

### A41. UPX/LZMA, PGO/LTO, executable pruning and loader costs

**1. Rigor applied:** Actual packed executable sizes, UPX integrity and identical compressed output for tested builds. Production flags/profile/unused-code search incomplete. E4, E11.

**2. Actually tested → needed:** UPX 195,584→166,708 per copy; C5 loader adds768 packed bytes in the lab. Compare clean matched production binaries, link maps, PGO input/profile, compiler versions and startup/run memory. A smaller lab binary does not establish the same delta in the submitted production package.

**3. Combination work:** Storage and loader tax were correctly combined in bounded component accounting. The full optimized candidate build and qualification are pending.

### A42. Transformer-aware post-SSE blend and specialist routing

**1. Rigor applied:** Actual small final-stage blend test and later neutral-versus-active checks. No exhaustive mixer architecture optimization. E4, E9.

**2. Actually tested → needed:** Round 5 blend worsens about 0.04%; later SX neutral/active archives both grow10/14 bytes on C/D. A new stage can change arithmetic/topology even when uninformative. Use exact identity initialization, shadow original update semantics and the same empty/random stage; then learned conditional gates. Do not infer automatic baseline preservation from a trainable coefficient.

**3. Combination work:** Several specialists were integrated, but learning the full residual/mixer interactions was not carried through. A negative topology choice does not dismiss all specialist signals.

### A43. Post-training scales, pruning, mixed precision and codebook quantization

**1. Rigor applied:** Actual weight exports and native cost-versus-size screens in round 7; initial scale/prune choices were coarse. E4, E9, E15.

**2. Actually tested → needed:** Scale×1.05 increased neural loss about 11%. Three zeroing arms save221,742/435,552/1,690,680 two-copy bytes but add130–185/288–442/1,491–3,243 likelihood bytes on 32K prefixes. They fail break-even. Use layer/activation sensitivity, actual codebook values, calibrated scales, mixed precision and optional QAT under M1; ordinal C3 indices are not signed magnitudes. A coarse prune failure does not settle optimal quantization.

**3. Combination work:** Container savings and final-coder penalties were jointly assessed. Sensitivity-weighted PTQ/learned rounding, pruning plus trained recovery and new codebooks remain unexecuted variants.

### A44. Article-order coding, dictionary front coding and regeneration

**1. Rigor applied:** Real alternate order/dictionary byte counts; regeneration economics and full inversion discussed. E4, E5, E9.

**2. Actually tested → needed:** Delta order208,185 versus201,042; front dictionary114,569 versus100,096, both worse. Test stronger conditional order codecs with complete mapping cost; for regenerated dictionaries prove deterministic tie/order rules, compiler independence, startup CPU and permitted input dependencies. Regeneration in compressor versus decoder has different requirements and cannot erase required archive data by assertion.

**3. Combination work:** These are largely isolated packaging probes. Improved dictionary generation/order plus retrained lexical model was not tested as a joint rate–distortion system.

### A45. Higher arithmetic/SSE probability precision

**1. Rigor applied:** Round 7 derives a deliberately optimistic restricted bound from actual uint16 bins. Much stronger than a vague precision estimate. E4, E9.

**2. Actually tested → needed:** Bound57.492/59.566 bytes on A/B for the fixed predictor's permissible within-bin choices; not realized improvement. Test exact higher precision coder, normalization, termination and binary tax only if that budget pays. The bound says nothing about changing the predictor or side-information model.

**3. Combination work:** Used to deprioritize a small packaging path. No evidence that combining precision changes with a new trained model was evaluated; that would be a separate effect.

### A46. Short compression-aware QAT/weight-entropy continuation — round 6

**1. Rigor applied:** Explicit payload + twice-weight-rate objective and quantizer surrogate. Sampling, continuation and numerical fidelity controls were inadequate for a broad conclusion. E5, E13, E20.

**2. Actually tested → needed:** At 100 steps, λ0 neural loss1.5103→1.5465 while λ30→1.5721; λ30 step 200→1.5851 despite lower weight entropy. A deteriorating λ0 cannot establish that rate-aware continuation is intrinsically ineffective. Repair complete-piece/target weighting, optimizer/start state and priors; validate frozen parity, then matched small λ0/0.3/1 arms with actual containers and final-coder loss. Strong regularization is not the whole frontier.

**3. Combination work:** Weight-rate and neural loss were optimized together, but not a stable continuation or jointly learned residual architecture. “Only full retraining can work” exceeded the evidence.

### A47. Timestamp from already decoded revision ID, gap-conditioned Laplace mixture — round 6

**1. Rigor applied:** Causal interpolation, grammar escape, exact digit distributions, online EM and native regional checks are substantial mathematical/engineering work. E5, E14.

**2. Actually tested → needed:** Timestamp + contributor-ID expert saves109,946 bytes over 15,717,594 revision bytes; timestamp accounts for roughly 109,780. Scores deteriorate across late import records, which was measured. Test full warm core, the different lexical time-sorted tail, all bytes/side data and eligible CPU/RAM. Regional success is credible but not a complete-record gain.

**3. Combination work:** Combined with contributor and time-neighbor username experts and tested in native mini-stream reconstruction. Production lexical transfer is unverified.

### A48. Contributor ID defined by username, then copied — round 6

**1. Rigor applied:** Causal definition-once relation and native integration; clear distinction between standalone and mixed costs. E5, E14.

**2. Actually tested → needed:** Standalone139 bytes for1,121,627 predicted bytes, but final mix saves only about 307 bytes. Verify definition/collision/format/reset cases and price code/state. The strong coder already handles most known IDs, so standalone compression cannot justify its value alone.

**3. Combination work:** Actually integrated with timestamp and username experts. Its small marginal gain must be counted once in the joint region, not added to standalone savings.

### A49. Username from nearest-in-time earlier record — round 6

**1. Rigor applied:** Prefix-only time neighbor and confidence buckets; native joint result. E5, E14.

**2. Actually tested → needed:** Adds3,357-byte saving to the timestamp/contributor combination over the revision region. Compare nearest chronological, preceding-stream user and exact-user cache at equal resources; then warm lexical order and complete package. A future timestamp neighbor is unavailable unless transmitted.

**3. Combination work:** Actual three-expert joint native system. Long-history/resource and alternative order interactions were not fully optimized.

### A50. Reconstruct owner-title list in stream; interlanguage copy expert — round 6

**1. Rigor applied:** Exact owner list matches independent Python, 93,707 owners/93,700 blocks; stream-preserving probabilities and round trips are strong. E5, E14.

**2. Actually tested → needed:** Region1,510,303→1,348,777, saving161,526 bytes. Compare full warm production lexical pipeline with matched state. Different shared-load timings do not establish a speedup. Title/case/empty/owner misalignment escapes must remain explicit.

**3. Combination work:** Used with the revision experts in the candidate/mini-stream. Their two regional savings sum274,829 bytes, but a single complete package has not measured that sum.

### A51. Two-center timestamp mixture using the previous record — round 6

**1. Rigor applied:** Alternative standalone distribution and actual full-mix comparison; a useful negative interaction test. E5.

**2. Actually tested → needed:** Standalone391,618→336,295 (about 55 KB better), yet full mix grows1,088 bytes. Retest mixture weight/contexts under matched warm state if warranted; any surviving arm needs the native total. The result correctly warns that standalone better probability can interact badly with the final mixer.

**3. Combination work:** It was tested within the existing structural combination and rejected. That specific failure is evidenced; all possible additional timestamp centers are not exhausted.

### A52. Predict page ID from title/alphabetical neighbors — round 6

**1. Rigor applied:** Causal neighbor hypothesis and standalone numeric check; no mature conditioned model. E5.

**2. Actually tested → needed:** Interpolation17.9 bits/page versus8.5 for plain delta. Define actual creation-era/order strata, already available neighbors and uncertainty model before enlarging complexity. Use the plain delta and same resources as controls, then final coder. This is a failed simple interpolation, not proof there is no title/creation relation.

**3. Combination work:** Screened as an additional metadata channel; no meaningful joint improvement or learned relation followed.

### A53. Predict timestamp from page ID — round 6

**1. Rigor applied:** A direct causal interpolation screen with explicit errors. Limited mechanism/stratification. E5.

**2. Actually tested → needed:** Errors approximately 2^20–2^25 seconds, worse than prior record. Separate creation time from latest revision time, and test only decoder-known article strata. A calibrated conditional mixture must count non-single-revision pages and imports. Without a residual bit budget, this remains low priority.

**3. Combination work:** Proposed as another timestamp center; the naive relation was rejected before a full combined learned model.

### A54. Revision ID from article length, redirect and latest decoded year — round 6

**1. Rigor applied:** Distinguishes improved standalone high-bit prediction from actual final-coder gain. E5.

**2. Actually tested → needed:** Top-bit cost8.34→7.05 suggests39 KB standalone, but actual region saves354 bytes. Preserve parsing causality: text-derived year must precede revision field in this stream. Compare formatting/bot-run/time controls, native joint prediction and code price; do not project high-bit savings independently of already strong low digits.

**3. Combination work:** Evaluated against the final coder as a metadata extension. No trained multi-feature entity/time model or large gain is evidenced.

### A55. Trie of decoded titles and link targets — round 6

**1. Rigor applied:** Causal trie and final-coder tests rather than repeat-rate optimism. Search/keying remains coarse. E5.

**2. Actually tested → needed:** +30/+25 archive bytes on A/B, including a large prior string set. Test schema/entity-specific candidate selection, alias/label relations, compact trie traversal and same-cost random donors; generic title membership cannot choose the right target. A failed undifferentiated trie does not test precise current-entity linkage.

**3. Combination work:** Added to the strong stack, with little weight accepted. The more targeted entity/field family was proposed and later probed separately.

### A56. Virtual replay, field reordering and decoder-known later metadata

**1. Rigor applied:** Stream-preserving experts were a practical substitution, but not mathematically equivalent to every replay factorization. E5, E17.

**2. Actually tested → needed:** Full general virtual-replay codec was not implemented. Define the alternative order, transmitted permutations/fields, replay state and conditional probability model; compare total both directions, e.g. time|ID versus ID|time plus source cost. A later field cannot help an earlier unknown value for free. Exact original-byte updates and complete inverse matter.

**3. Combination work:** Structural experts realize selected causal relations while preserving the stream. That is substantive engineering, but cannot be described as completion of the broader replay architecture.

## Per-idea audit: round-7 frozen specialist search and lexical architectures

### A57. Current-article entity, title, alias and field copies

**1. Rigor applied:** Prefix-available candidate generation, normalized whole-field mixtures and corrected EOF accounting. Strong finite-family math, limited semantic coverage. E9, E17.

**2. Actually tested → needed:** Balanced point-copy ideal savings A/B/C/D −2.261/+1.902/+0.649/−1.910 bytes per2M. The proposed capped title/alias/target family did not show a material gain. Test explicit entity identities and actual alias/infobox relations on a warm budget atlas, with equal unrelated-donor controls. No future field may select a donor silently.

**3. Combination work:** Shared scorer covers several field relations. Learned entity selection and joint paid latent/syntax interactions were not implemented.

### A58. Schema-keyed probabilistic field edits / pair-HMM

**1. Rigor applied:** Marginalizes allowed alignments, normalized emissions and fallback; kernel checked against180 Python tests to below 2.85e−14 bits. E9, E17.

**2. Actually tested → needed:** Corrected field-edit savings −3.495/+0.007/−0.808/−3.527 bytes. A cheapest alignment selected using the unknown target would be invalid; the implemented marginalization avoids that. Test stronger template/path/column keys, banded state limits and learned transition rates at equal donors/CPU. The fixed field-copy edit kernel is not the proposed learned word-relation transducer.

**3. Combination work:** Generic field channels share the baseline mixture; no jointly trained schema discriminator or full command-codec/replay alternative.

### A59. Prefix-keyed line copy/edit; digit-masked keys

**1. Rigor applied:** Paid four-byte prefix, bounded16 MB/64K-key memory, two donors and all mismatch costs. E9.

**2. Actually tested → needed:** Line exact gives −1.548/+1.029/+1.001/+0.201 ideal bytes; edits −2.822/+3.701/+10.262/+3.711, digit-mask similar. Optimize schema-aware boundaries/key lengths, normalized transition model and startup/RAM/CPU before native integration. The oracle budget is only for these donors and cannot rule out better semantic alignment.

**3. Combination work:** Exact versus edit and key masking were compared. No broad combination with grammar/entity/numeric schema models or learned donor choice was tested.

### A60. Numeric relations: recurrences, field copies, formats and units

**1. Rigor applied:** Bounded causal integer programs, false-alarm costs and explicit formatting/fallback. More advanced field arithmetic remains design only. E17, E21.

**2. Actually tested → needed:** Six programs (last, ±1, difference, same-field last, page-year copy), two strengths plus neutral save −0.498887 ideal bytes across 8M. Test typed columns, signs/zeros/decimals/units and normalized residual intervals, with paid fitted coefficients when offline. Short rational conversions and richer recurrences were proposed but not implemented. The six-program result is not an exhaustive arithmetic search.

**3. Combination work:** Programs were mixed causally and compared with paid templates. Joint schema detection and learned arithmetic confidence remain absent.

### A61. Corpus-specific executable macros, program search and numeric templates

**1. Rigor applied:** Two-part MDL and paid rule/use framing were specified; actual packet round trips are exact. The broad program-discovery/cover optimizer was not built. E17, E21.

**2. Actually tested → needed:** Bounded numeric-template packets all grew under zlib/LZMA on four slices, despite exact reconstruction. A fixed generic-codec layout is not a native macro predictor. Mine high-final-cost spans, optimize a nonoverlapping priced cover, store literal/rule/selector costs, and compare a native generated-string mixture or command codec with all fallback/replay costs. Exact free selection is diagnostic only.

**3. Combination work:** Numeric parameters + literal templates + codecs were tested. Entity fields, learned schema, sparse macro search and baseline replay were not optimized together.

### A62. Frozen neural temperature and entropy-dependent calibration

**1. Rigor applied:** Finite registered strengths and neutral Bayesian mixtures; specific normalized likelihood comparison. E9.

**2. Actually tested → needed:** Temperature0.6–1.5 left1 best on A/B; adaptive standalone neural mixtures lose about 0.396/2.5 bytes. These are neural distributions, not final coder. Test richer calibration only with held-confirmation and complete normalized byte/bit paths, then native/payload cost. Do not treat a neural temperature loss as a result for a context-dependent lexical residual.

**3. Combination work:** Temperature and entropy contexts were combined, but not a trained residual architecture. Reasonably low priority after these finite results.

### A63. Final-bit calibration and 128 learned integer odds factors

**1. Rigor applied:** Strong bounded native verification: exact neutral, deterministic uint64 odds, all candidate bits matched and independent E/F decodes. Narrow learned model. E9, E21, E22.

**2. Actually tested → needed:** Earlier causal calibration +30.194/+4.279 ideal bytes A/B. A/B-fit128-factor model (512 B/copy) saves148.168 ideal bytes across examined8M. Fresh64K E/F archives grow1/3 bytes; candidate code adds1,016 bytes before its model. Thus this calibration is not a winner. Context-dependent interactions require a separate model and priced fresh native test; do not reuse the development gain as confirmation.

**3. Combination work:** Baseline confidence × bit position was trained, not spelling/syntax/topic/memory. Exact arithmetic work provides reusable infrastructure but is not a learned lexical architecture.

### A64. Suffix, root and new-mention word associations

**1. Rigor applied:** Causal counts, variable-length WRT parsing, full fallback outcomes and corrected root/EOF versions. Earlier provisional outputs had synchronization/lookahead defects. E9, E10, E21.

**2. Actually tested → needed:** Suffix screen gives7.554/54.905/75.124/29.940 ideal bytes but covers only 23–25% of costs. Corrected root/new-mention family gives41.891 total ideal bytes/8M; all fixed nonneutral arms lose. Test joint syntax/topic gating and native warmed integration after freezing a promising configuration. Never suppress an upcoming word using its unknown identity or declare a partial EOF word complete.

**3. Combination work:** Multiple causal associations share mixtures and masks. No trained first-mention predictor, semantic state or interaction controller was executed.

### A65. Paid article topics/profiles and learned discrete/vector latents

**1. Rigor applied:** Valid Kraft-priced selectors, complete literal penalties and profile asset tax. The stronger learned conditional latent is design only. E9, E19, E23.

**2. Actually tested → needed:** 32 sparse profiles, seven strengths: selector-paid gains −231.275/−114.586/−89.628/−61.994 bytes before 21,844 B/copy tables. This rejects that sparse unigram family. Train a context-dependent residual conditioned on paid latent; compare no latent, causal title latent and future-informed paid latent at identical capacity. Encode latent/framing/title prior and optimize complete package; do not require the sparse screen to pass as a theorem-level prerequisite.

**3. Combination work:** Selector/profile coding was executed. Learned latent × syntax × lexical residual and title-conditioned priors have not been jointly trained.

### A66. Causal title/article latent state without transmitted hints

**1. Rigor applied:** Prefix-only title/count/topic state and corrected prior-strength comparison. No learned compact semantic recurrent state. E9, E19.

**2. Actually tested → needed:** V2 loses about 2.497/1.562/2.462/2.485 bytes; fixed64-prior V3 B/C loses1.539/2.457. Evaluate causal summaries and context-dependent residuals versus unigram/title counts, same-capacity generic state and paid latent. Future content must not leak into a “causal” state. These count models are not all latent-state architectures.

**3. Combination work:** Title/article priors were combined with word-tree specialists. Learned summaries and memory gates remained proposals.

### A67. Word-event prediction through the unchanged WRT code tree

**1. Rigor applied:** Exact probability interface, mixed two/three-byte prefixes and literal/escape/EOF corrections; full trained word predictor missing. E9, E18.

**2. Actually tested → needed:** Several additive tree experts were screened; no learned normalized full lexical head. For prefix a, next-byte probability is subtree mass(ab)/subtree mass(a), including all alternatives. Test all controls, escaping and termination, then train matched tree/global heads. Observed word costs cannot recover baseline probabilities of every counterfactual word for a global tilt.

**3. Combination work:** Infrastructure supports associations, topics, echo and grammar on one stream. The shared learned lexical model behind this interface has not been trained.

### A68. Spelling composer + low-rank semantic word codes; tied input/output

**1. Rigor applied:** Detailed storage/MAC economics and causal input distinction. No measured trained rank 8/16 word-code model in round 7. E18.

**2. Actually tested → needed:** 44515×16 int8 table alone712,240 B/copy requires about 0.01943 final bits/WRT symbol to break even at the old stream length. Compare spelling-only, learned generic codes, tied/untied codes, ranks and actual quantized containers under equal total cost. The target output embedding may be a candidate, but cannot enter the causal state before prediction.

**3. Combination work:** Intended to share across syntax, spelling, article and memory heads. That is a cost-aware design, not a measured jointly optimized architecture.

### A69. Spend expensive computation at word events; multiple deliberation steps

**1. Rigor applied:** Operation-count decomposition recognizes byte-head/classical costs; speedup was not measured. E18.

**2. Actually tested → needed:** Old 586.459M WRT symbols /133.923M ASCII words ≈4.379 is an optimistic event ratio, not 4.379× runtime. Build word-triggered recurrent/update kernels and compare K=1/2/4 deliberations with a same-time byte model. Count dictionary fragments, literal spelling, head normalization and unchanged cmix; measure native full-run performance.

**3. Combination work:** Proposed with shared lexical heads and memories; no word-event architecture or optimal CPU allocation was executed.

### A70. Exact tiled word softmax, conditional tree heads and integer normalization

**1. Rigor applied:** Granular mathematical/engineering plan: tiled normalizer, subtree interface and bounded fixed-point sums. No trained native implementation. E18.

**2. Actually tested → needed:** Full 65536×44515 float32 logits ≈11.67 GB; rank 16 global scoring ≈95.4T MACs and 5.96T exponentials at the old word count. Proposed tree≤320 child scores is a different model capacity. Implement exact normalization, backward recomputation, deterministic quantization and low-mass fallback, then compare the actual CPU/Pareto frontier. Negative sampling cannot silently replace the coding normalizer.

**3. Combination work:** Designed to make lexical architecture affordable. No actual trained global/tree comparison or integrated decoding benchmark supports an optimal choice yet.

### A71. Bounded prior-article retrieval using title/link keys and summaries

**1. Rigor applied:** Explicit completed-article availability and bounded bank; only a coarse retrieval implementation has run. E10, E16, E18, E21.

**2. Actually tested → needed:** Final batch bank up to 1024 completed articles, top 32 counters, ≤4 title-overlap donors, with random-article controls. It did not reveal a large joint gain. Test linked-entity keys, causal learned summaries and warm full history, matching donor availability and overlap strata. Cold slices reset the bank; they do not test a mature global decoder memory. Serialize learned keys but reconstruct decoded content.

**3. Combination work:** Combined with fixed syntax/echo/TTL families. Learned semantic selection and a shared contextual decoder remain unexecuted.

### A72. Independent positional letter moments / algebraic representations

**1. Rigor applied:** Round 7 corrected redundant basis functions and recognized normalized-moment collisions. This is real mathematical scrutiny, not proof of predictive usefulness. E6, E10.

**2. Actually tested → needed:** Moment neighbor audits, fixed graph/lag/echo screens; full learned bilinear placement/semantic model not run. Compare independent polynomial/orthogonal moments, order-sensitive n-grams, counts/length and same-rank learned/random projections. Record collisions and exact relations; words sharing moments do not become interchangeable or uniquely encoded.

**3. Combination work:** Moments informed candidate generation, but the proposed learned syntax/context × algebra interactions were not trained. The earlier trained letter embeddings remain separate positive evidence.

### A73. Word glyph geometry as a relational basis / parameter sharing

**1. Rigor applied:** Recognized G_k=G A_k, so complete letter moments already contain those fixed linear features. E6, E10.

**2. Actually tested → needed:** Geometry nearest-neighbor/control arms were scored, not a learned geometry-conditioned relation function with matched projections. Fix deterministic glyph rules; compare equal-dimensional random/learned projection and complete spelling moments at identical downstream capacity. Geometry may regularize useful sharing; it cannot be credited as new information merely by adding another feature block.

**3. Combination work:** Geometry was combined with fixed echo support. Signed learned relation/gates and morphophonographic channels were not jointly optimized.

### A74. Word edit, prefix/suffix, multiset, morphology and phonetic channels

**1. Rigor applied:** Normalization/soft-edit limitations were derived; bounded prefix/suffix/deletion and Soundex variants exist. Learned phonographic/pair-HMM word relations do not. E6, E10, E21.

**2. Actually tested → needed:** Final fixed Soundex/anagram/geometry arms all lose as nonneutral policies; lag diagnostics have substantial matched-random coverage. Test each relation in a trained signed contextual residual with same-degree/work controls. Include deletion/silent-letter rules and learned shared edit costs as separately priced hypotheses; distinguish prefix-derived candidate support from optimal probability. Field edit failures are not word edit tests.

**3. Combination work:** Several channels were enumerated and mixed. Their trained complementary interaction, selection and morphology-specific sharing remain untested.

### A75. Candidate graph search, exhaustive neighbors and deterministic integer repair

**1. Rigor applied:** Strong search-correctness audit. The initial candidate search was discovered to be very poor, then repaired and independently CPU-checked. E10.

**2. Actually tested → needed:** Capped top 8 mean recall3.947% on 133 queries; integer graph99.248%,125/133 full recall **against the original float metric**; all 356,120 integer graph IDs/scores CPU/GPU equal. The residual float-reference differences are not missed searches under the exhaustive integer definition. CPU prototype30.667 s/RSS832,904 KiB. High search recall does not prove useful relations. Optimize indexes/working memory and benchmark compiled startup/native query costs before qualification.

**3. Combination work:** Corrected graph was substituted into the same echo screen, a useful controlled repair. It did not trigger training of the full relation model.

### A76. Lag-support diagnostics and restricted oracle ceilings

**1. Rigor applied:** Exact donor availability and bit-weighted budget separated from achievable gains; overlap explicitly acknowledged. E10.

**2. Actually tested → needed:** Dictionary-span support budgets range roughly 5–19% by relation/slice; matched random support is sizable too. These use up to 256 sources and can exceed the actual128-slot echo support. Record union/overlap and realistic memory eviction, then fit a normalized causal scorer charging false positives. Cannot add lag/channel percentages or treat perfect supported-target prediction as an executable.

**3. Combination work:** Several supports were compared, but joint coverage union and a trained multi-channel support-to-probability model were not measured.

### A77. Fixed lexical echo, signed boosts, decays and neutral/random controls

**1. Rigor applied:** Corrected causal distributions, graph substitution, EOF/fallback and final uint16 replay are carefully engineered. The actual learned architecture is absent. E10, E21.

**2. Actually tested → needed:** Corrected integer echo gross≈4.244 ideal bytes/8M. Final15-family/four-strength mixture gross1.731295 bytes/8M; fixed nonneutral arms lose. This tests fixed activations/decays, not whether context learns to reject bad candidates. Train joint gates/relations under all-outcome final-bit loss; include same-capacity learned generic and shuffled controls, actual native archives and model tax.

**3. Combination work:** Many finite experts were mixed, but mixing independent fixed arms is not optimizing feature interactions in a shared architecture.

### A78. Directed word placements, lag bins and low-rank distance kernels

**1. Rigor applied:** Causal directional counts and a compact recursive low-rank formulation were specified. Only counts/fixed mixtures ran. E6, E10.

**2. Actually tested → needed:** Directed-lag screen gives total−7.847332 ideal bytes/8M. It does not implement z(u)^T M(d)z(v) with trained ranks/time bases. Train signed low-rank directional residuals against final bits, inspect whether grammar/topic interactions are needed, compare previous-word/count and same-rank generic controls. Recursion saves history scans for exponential kernels; Gaussian windows need their own queue/cost model.

**3. Combination work:** Counts and echoes were separately/mixture tested. Joint learned placement × associative activation is still missing.

### A79. Syntax/word-slot state, placement heuristics and source surprise

**1. Rigor applied:** Causal previous-word class/punctuation and source-only surprise were used. No trained syntax-state/controller architecture. E6, E10, E21.

**2. Actually tested → needed:** 32K residual pilot loses4.017518 ideal bytes/64K; later coarse syntax/source-rank families yield no material gain. Literal I/i and word-boundary coverage were audited. Train small recurrent/transformer slot state using decoded words, markup, punctuation and title; ablate syntax alone, echo alone and interactions. “Now…know” anecdotes (zero sampled short-lag pairs) are not evidence of a general ordering law.

**3. Combination work:** Heuristic states combined with fixed residual arms. The proposed learned placement/suppression model was not trained or optimized.

### A80. Learned persistent signed activation, injection, rejection and survival

**1. Rigor applied:** This central idea has equations and subsequent corrections, **not an implemented trained mechanism**. E6, E10, E23.

**2. Actually tested → needed:** Fixed echo/TTL is an incomplete proxy for a_t(v)=λ_t(v)a_{t−1}(v)+I_t(u,v,H_t). Train signed relation, context gate and survival jointly, with bounded memory, exact exported arithmetic and all false associations charged. Surprise may be used only after its source word completes. Compare exact memory, structural/learned memory and equal generic capacity; test first mentions separately from repeats without using future labels as inputs.

**3. Combination work:** There is thoughtful written synthesis with placement/residual heads. No end-to-end trained activation × syntax × memory architecture, or hours-per-idea log, supports calling it deeply experimentally optimized.

### A81. Counterfactual edge savings, hazard, optimal activation and eviction

**1. Rigor applied:** Corrected horizon-versus-next-event mismatch and interacting-edge attribution. These are meaningful theoretical improvements, not empirical calibration. E6, E10, E16.

**2. Actually tested → needed:** No learned counterfactual deletion or hazard model was executed; exponential TTL is not that test. Define immediate state deletion versus full replay, sample paired interventions on prefix-generated edges, estimate next-step hazards and train joint normalized likelihood/rate. Eviction uses expected future final-bit value from available features, never actual future reuse. Edge-wise savings cannot simply be summed.

**3. Combination work:** Combined conceptually with sparse activations and MDL, not with trained controllers or native causal counterfactual evaluation.

### A82. Multi-source/multi-channel log-odds accumulation and activation×placement interaction

**1. Rigor applied:** Equations include signed evidence and an interaction term; correlated evidence/double counting was recognized. E6, E10.

**2. Actually tested → needed:** Fixed expert mixtures do not train β_AP a(v)p(v), contextual cross-channel coefficients or suppression. Run factorial removal of channels and interaction terms in the same jointly trained residual, match storage/CPU, clip exported activations and score every outcome. A neutral branch bounds losses only under its precise mixture semantics, not by wishful convergence of coefficients.

**3. Combination work:** This is the defining proposed combination; it remains design only. Its failure cannot be inferred from additive fixed unigram probes.

### A83. Shared residual transformer/controllers and multiple specialized heads

**1. Rigor applied:** Probability-space correction and parameter-sharing equations are valid proposals; no trained shared syntax/algebra/article/memory residual in round 7. E6, E18, E23.

**2. Actually tested → needed:** The128-factor calibration is not this model, and four independent snapshots are a different architecture. Train shared state with small heads, compare one generic residual versus specialized heads at equal rate/time, measure sequential corrections' final normalizer and exported size. Register rank/state/model byte caps and test literal/control fallback. Avoid making failed simpler screening a universal prerequisite.

**3. Combination work:** Written design integrates several ideas; implementation, learned interaction ablations and architecture tuning are absent. This is one of the largest gaps relative to the user's requested research depth.

### A84. Independent learned residual against the native final-bit coder

**1. Rigor applied:** Later design identifies a way around the unrelated core-GPU parity dependency. Integer calibration infrastructure is verified; the contextual residual is untrained. E22, E23.

**2. Actually tested → needed:** Collect native causal features and y,p16; train q=Q16 σ(logit(p)+rθ(c)) with complete loss plus actual model/code rate. Keep baseline internal updates unchanged, so teacher-forced baseline trajectories remain valid. Compare32/128 KiB-budget contextual models with generic/identity controls, then fresh native decode/package/CPU. Core parity is not required for this independent head; its own export parity is.

**3. Combination work:** Proposed to combine syntax, spelling, memory and paid latent. No new model from this proposal has been launched or measured.

## Per-idea audit: constructors, right context and training

### A85. Constructors, content variables and rare constants: reversible split

**1. Rigor applied:** Exact lexical distinction, framing, literal-word handling, raw reconstruction and native-bit budget were analyzed. Grammar-class semantics remain a heuristic lexicon, not validated POS tags. E24.

**2. Actually tested → needed:** Declared176 constructors carry about 17.1997% of sampled bits;56 generic-codec comparisons all grew. Test lexicon/learned-class alternatives with all tags/model assets charged, exact punctuation/case/markup and content order. Separately optimize C,A,G streams under M3. If only that measured constructor bucket changes, it cannot alone explain a20% total gain; its full-corpus share is unverified.

**3. Combination work:** Exact split and layout variants were implemented. A jointly trained content/grammar model was not, so the constructor hypothesis is only partly tested.

### A86. Constructor sets, multisets and permutation coding

**1. Rigor applied:** Explicitly corrected loss of order/multiplicity; exact packet decoding includes order. E24.

**2. Actually tested → needed:** Multiset-plus-order framed layout grows about 19.473% zlib9 /22.204% LZMA6. Most gaps (87.345%) contain0/1 constructors, limiting set amortization in these samples. Test enumerative permutation coding conditioned on already paid anchors, adaptive set priors and exact repeats at equal framing; evaluate total streams rather than assume equal sets are equal sentences.

**3. Combination work:** Set identity + order + literal frames was tested. Learned contextual permutation or subset selection was not trained.

### A87. Ordered constructor templates, shared word dictionaries and subset grammars

**1. Rigor applied:** Actual table/layout variants, charged IDs and raw round trips. Broad subset/compositional grammar model is still unimplemented. E24.

**2. Actually tested → needed:** Ordered framed templates grow18.847%/21.493%; best one-byte skeleton marker + constructor-word table grows2.066%/4.601%. Low reuse of larger gaps argues against these static tables. Train conditional ordered gaps or a reusable grammar with paid derivations, compare direct adaptive gap model, and measure native complete cost. A generic LZMA loss is not a learned grammar loss.

**3. Combination work:** Dictionary sharing, markers and gaps were combined iteratively. Content-conditioned neural prediction and learned subset composition were not.

### A88. Content first, then grammar with both left/right content; neural infilling

**1. Rigor applied:** Valid chain-rule factorization, paid right context and exact alignment requirements are developed. The actual learned codec is design only. E7, E24, E23.

**2. Actually tested → needed:** Skeleton packets and small earlier masked models are partial proxies. Train Q_C(C), Q_A(A|C), Q_G(G|C,A) on their actual decode order, compare left-only/right-only/both anchors and equal total model/compute budgets, then reconstruct exact bytes. Stripped text scored by the old frozen transformer is out of distribution and cannot settle the architecture. “There _ a camel” does not remove the need to code is/was and surrounding layout.

**3. Combination work:** Rigorous written combined architecture exists. No joint content-first model or optimized conditional infiller was run.

### A89. Prefix-only constructor-run and syntax expert on unchanged stream

**1. Rigor applied:** Causal completed-word updates and full-bit normalized residual scoring; limited hand-built state. E21, E24.

**2. Actually tested → needed:** Final batch uses constructor-run length/class and prior content rank, with 176-word list and neutral controls. No material gain. Test a learned ordered-run/trie model conditioned on decoded content/punctuation, compare same-sized generic syntax state and morphology, and measure actual integer native coder. An observed gap's future length or next noun must not activate its own gate.

**3. Combination work:** Combined with the fixed syntax/memory suite. No trained constructor × content × residual interaction.

### A90. Representative finetuning/full retraining with correct MDL rate

**1. Rigor applied:** Detailed later contracts address useful-token weighting, optimizer, numerical export and actual rate. Those contracts have not been executed. E20.

**2. Actually tested → needed:** Round 6 short λ30 is the actual training evidence; round 7 core finetuning was not run. Require frozen F0 identity, baseline-preserving representative F1 λ0, then matched small-rate arms, actual packed export/final coder and appropriate seeds/pieces. Restore original optimizer if available; otherwise warm-start conservatively and do not change all factors at once. Full scratch retraining is an alternative, not proven necessary.

**3. Combination work:** Payload/rate/data/export/CPU dependencies are planned in detail. Learned architecture + rate-aware continuation has not been tested. The $70 stages are caps, not completed spending.

### A91. Residual-importance sampling and mixer-aware training objectives

**1. Rigor applied:** Importance correction and limitations of a simplified neural/CM surrogate are stated. Design only. E20.

**2. Actually tested → needed:** No residual-importance/mixer-aware training arm is recorded. Fix π_t=η/T+(1−η)c_t/Σc and use1/(Tπ_t) if preserving uniform likelihood; record whether reweighting is intentional. Compare uniform and corrected sampling at equal useful targets, validate surrogate sensitivity against the actual nonlinear mixer, and select by final payload plus exported size. Expensive examples may be training labels, not future inference inputs.

**3. Combination work:** Intended to combine difficult-word diagnostics with MDL continuation. No measured joint outcome or optimal allocation of gradient effort exists.

### A92. Small adapters, merged LoRA, larger teacher and distillation

**1. Rigor applied:** Correctly prices merged versus unmerged updates and teacher/student costs; no executed round 7 training study. E18, E20.

**2. Actually tested → needed:** 8M/10M structural loads passed, but neural parity failed and inference comparisons were skipped. For core teachers fix parity first; for an independent residual train its own control. Compare merged quantized adapters, separately stored adapters and distilled equal-cost student using actual containers and CPU. “LoRA is small” does not make changed base weights or forward passes free.

**3. Combination work:** Proposed with rate-aware finetuning and shared lexical heads. No trained teacher→student or adapter × memory experiment supports a compression estimate.

### A93. Native/GPU parity, checkpoint reconstruction and lexical configuration

**1. Rigor applied:** Strict load/shape audits, macro correction and actual pointwise diagnostics; failure preserved. These are prerequisite engineering tasks, not compression gains. E10, E15, E20.

**2. Actually tested → needed:** Correct C3 macros/codebooks enable native round trips; larger checkpoints load structurally. Compatible FX2 GPU pilot fails ordinary-row parity despite matching reset fallbacks. Locate first layer/state divergence, check prior/activation quantization, attention/KDA piece resets and export, then lexical F0. Do not silently relax gates or assume loading proves functional equivalence. Independent residual training needs only its own faithful native interface.

**3. Combination work:** This infrastructure supports all core-training variants. Its unresolved state was allowed to delay too many independent architectures; dependency redesign is required.

### A94. Training-prior compression, cached native embeddings and data throughput

**1. Rigor applied:** Exact sample prior-storage round trips and full old-transform inverse; cached-embedding equivalence remains a hypothesis. E21, E25.

**2. Actually tested → needed:** 48 storage probes cover107,479,040 bytes; raw zstd9 best fast sample50,901,611 bytes, not guaranteed full ratio. Full old-FX2 inverse reconstructs1 B exact; production lexical data/full priors remain unregenerated. Test streaming decode/read amplification and useful targets/dollar; if caching prior embeddings, prove fixed preprocessing and no other raw-prior use. Storage savings facilitate training; they are not archive gains.

**3. Combination work:** Data compression and recovery were executed to support training. Prior-embedding caching plus a complete trained model/export has not been tested.

### A95. Warm full-history, complete package and eligible CPU/RAM validation

**1. Rigor applied:** Many mini/native round trips and source/input hashes; no new full qualifying compressor package. E5, E21, E22, E25.

**2. Actually tested → needed:** Four2M lexical-checkpoint/native traces and fresh64K calibration E/F, plus1 B preprocessing inverse. A/B/C/D are cold pieces of the old FX2 transformed stream, not a full production lexical order. Build actual production data/package, run separate complete comp/decomp, verify1 B output hash and count all assets/options. Measure both calibrated CPU runs and peak warm RAM/disk; short-piece RSS and linear runtime projections do not qualify it.

**3. Combination work:** Individual components reached substantial correctness evidence. Their full matched joint package, mature memory history and source-to-submission integration remain incomplete. No 20% result or absolute optimum is established.

## What the combination evidence actually supports

| Combination | Observable work | Unresolved gap |
|---|---|---|
| Ternary + online adaptation + weak CM | Round 2 intermediate arms and joint likelihood | Actual entropy package and ternary/native update CPU |
| Scratch + keep-alive memory | Round 3 trained model plus blanking and capacity variants | Independent optimized controls, seeds, longer training, realistic causal selection |
| Word length + scratch + TTL + length-aware CM | Written recommendation | Full four-part combination not run |
| Dictionary layout + algebra + adaptation + cache + kNN + CM | Round 4 real implementation, intermediate comparisons and scaling | Strong baseline fairness, exact storage, ≤10 GB/native CPU |
| Four snapshots + miners + classical mixer | Round 4 online normalized combination and search-sharing test | All copies/time, test selection, eligible package |
| fxcm + revised metadata + BF16 + UPX | Round 5 components and transform inversion | Joint compression saving is projected; changed-stream model mismatch |
| Timestamp + contributor + username + interwiki | Round 6 native regional integration and mini-stream decode | Warm complete archive and lexical-tail transfer |
| Fixed echo/lag/syntax/retrieval/TTL/phonetics/grammar | Round 7 finite mixtures and final-bit replay | Joint learned interaction/rejection/survival absent |
| Learned relation + placement + hazard + shared residual | Detailed equations and proposed controls | Defining architecture untrained |
| Paid article latent + learned native residual | New costed architecture design | Latent selector/model training and native paid channel unimplemented |
| Content-first + conditional grammar + alignment | Valid factorization and exact packet proxies | Matched trained content/grammar models and native full codec absent |

Combinations should be evaluated on their own joint trajectory. For components A and B, let L0, LA, LB, LAB be matched complete costs. Interaction is I_AB=LAB−LA−LB+L0. Negative I_AB indicates synergy in that comparison; positive indicates overlapping savings or interference. Apply this to payload **and** changed package/compute, using the same dataset/order. Existing reports often provide some pairwise intermediate rows; they do not provide a comprehensive factorial interaction matrix across the learned proposals.

## Corrective research standard and priorities

1. **Stop substituting a weaker mechanism for a central proposal without naming the substitution.** Record “fixed-boost probe” separately from “learned relational memory,” “generic skeleton packet” separately from “trained infiller,” and “entropy estimate” separately from “encoded model.”
2. **Keep two legitimate development branches.** The original-core continuation requires parity repair, exact lexical priors/data and a stable λ0. An independent native-final-bit residual requires causal feature/export identity but can proceed without that core-GPU repair. They compete under the same budget rather than blocking each other.
3. **Test the missing interactions at bounded cost.** Compare generic residual capacity, syntax alone, relation alone, learned syntax×relation, memory survival, and paid latent under actual byte caps. A fixed expert's failure should inform initialization/control, not veto the defining learned hypothesis.
4. **Treat the trained round-4 representation gains as hypotheses worth transfer studies.** The layouts/algebra results have actual positive evidence. Transfer requires the production code/tree, storage tax, matched training exposure and native CPU. It is not justified to extrapolate their percentages directly.
5. **Retain content-first infilling as a separate architecture alternative.** Its static packets lost, but its defining conditional model was not run. Quantify paid content/alignment/grammar costs before funding a larger model; do not promise that grammar alone provides20%.
6. **Measure full qualifying output for any survivor.** Correctness infrastructure is already useful. A large enough priced gain, fresh native confirmation and resource margin should precede a multi-day full run. Do not declare an absolute optimum or assume more budget guarantees a breakthrough.

The present $70 execution allocation remains $4 pilot + $12 controlled screens + $36 winning continuation + $8 export/evaluation + $10 ancillary reserve. These are competing stage caps, not a budget per architecture; recorded rental spending is $0. This audit creates no rental or new experiment. It also does not resume or alter the usage-limited managed Goal.

## Evidence index

These are actual local files. E-codes in entries identify the main evidence; the adjacent historical reports and preserved result scripts give additional detail. Their hashes and proposal-section coverage are recorded in the accompanying audit manifest.

| Code | Evidence |
|---|---|
| E1 | [Round 2 report, including round 1 summary](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:5) |
| E2 | [Round 3 report](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:20) |
| E3 | [Round 4 report](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:83) and [preserved results](/C:/Users/91707/Downloads/compression_cmix/hutter_exp4_results.json) |
| E4 | [Round 5 report](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:97) |
| E5 | [Round 6 report](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:108) |
| E6 | [Placement/algebra proposal](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt) and [associative-memory proposal](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt) |
| E7 | [Original progressive-constraint proposal](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt) |
| E8 | [Original OCR/geometry variants](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt) |
| E9 | [Integrated round 7 report](/C:/Users/91707/Downloads/compression_cmix/research_round7_report.md:215) |
| E10 | [Round 7 experiment registry and mathematical corrections](/C:/Users/91707/Downloads/compression_cmix/research_round7_pre_experiment_report.md:135) |
| E11 | [Exact older-FX2 codec results](/C:/Users/91707/Downloads/compression_cmix/research_round7_v5_codec_results.json) and [lexical-C3 codec results](/C:/Users/91707/Downloads/compression_cmix/research_round7_lex_v5_codec_results.json) |
| E12 | [Word model/training code](/C:/Users/91707/Downloads/compression_cmix/hutter_exp4_code/dtok.py:119), [one-copy full-size calculation](/C:/Users/91707/Downloads/compression_cmix/hutter_exp4_code/dtok_full_eval.py:71), [cache size calculation](/C:/Users/91707/Downloads/compression_cmix/hutter_exp4_code/dtok_full_cache.py:143), [entropy estimator](/C:/Users/91707/Downloads/compression_cmix/hutter_exp4_code/full_tok.py:54), [retained half-key construction](/C:/Users/91707/Downloads/compression_cmix/hutter_exp4_code/full_tok.py:162) |
| E13 | [Round 5 model port](/C:/Users/91707/Downloads/compression_cmix/round5/tfh.py:54) and [head adaptation](/C:/Users/91707/Downloads/compression_cmix/round5/headadapt.c) |
| E14 | [Preserved structural source](/C:/Users/91707/Downloads/compression_cmix/research_round7_sources/structx.h) and [predictor integration](/C:/Users/91707/Downloads/compression_cmix/research_round7_sources/sxpatch.py) |
| E15 | [Native PTQ results](/C:/Users/91707/Downloads/compression_cmix/research_round7_ptq_native_results.json), [native codebook build](/C:/Users/91707/Downloads/compression_cmix/research_round7_lex_codebook_build_results.json), [parity diagnostic](/C:/Users/91707/Downloads/compression_cmix/research_round7_frozen_logits_parity_diagnostic.json) |
| E16 | [Memory information/controls](/C:/Users/91707/Downloads/compression_cmix/research_round7_memory_information_plan.md) |
| E17 | [No-retraining mechanisms and priced program search](/C:/Users/91707/Downloads/compression_cmix/research_round7_theory.md) |
| E18 | [Word architecture plan](/C:/Users/91707/Downloads/compression_cmix/research_round7_word_model_plan.md) and [exact head engineering](/C:/Users/91707/Downloads/compression_cmix/research_round7_word_head_precision_plan.md) |
| E19 | [Paid article hint design](/C:/Users/91707/Downloads/compression_cmix/research_round7_article_latent_plan.md), [causal latent design](/C:/Users/91707/Downloads/compression_cmix/research_round7_causal_latent_plan.md), [local residual tilt distinction](/C:/Users/91707/Downloads/compression_cmix/research_round7_residual_topic_tilt_plan.md) |
| E20 | [Detailed finetuning execution plan](/C:/Users/91707/Downloads/compression_cmix/research_round7_finetuning_execution_plan.md), [training mathematics](/C:/Users/91707/Downloads/compression_cmix/research_round7_training.md) |
| E21 | [Completed batch report](/C:/Users/91707/Downloads/compression_cmix/research_round7_remaining_experiments_report.md:86), [exact summary](/C:/Users/91707/Downloads/compression_cmix/research_round7_final_batch_summary.json) |
| E22 | [Fresh native calibration results](/C:/Users/91707/Downloads/compression_cmix/research_round7_native_calibration_20261005/results.json) and [independent local validation](/C:/Users/91707/Downloads/compression_cmix/research_round7_native_calibration_local_validation.json) |
| E23 | [Latest learned architecture design; explicitly unexecuted](/C:/Users/91707/Downloads/compression_cmix/research_round7_record_breaking_next_stage.md) |
| E24 | [Constructor mathematics, tests and follow-up](/C:/Users/91707/Downloads/compression_cmix/research_round7_constructors_and_variables.md), [constructor split results](/C:/Users/91707/Downloads/compression_cmix/research_round7_constructor_split_v1_summary.json), [single-byte skeleton results](/C:/Users/91707/Downloads/compression_cmix/research_round7_constructor_skeleton_v2_summary.json) |
| E25 | [Full transform/prior result summary](/C:/Users/91707/Downloads/compression_cmix/research_round7_final_batch_summary.json) and [final-bit validation](/C:/Users/91707/Downloads/compression_cmix/research_round7_finalbit_local_validation.json) |
| E26 | [Read-only remote-ledger access outcome](/C:/Users/91707/Downloads/compression_cmix/research_round1_to_round7_remote_access_note.json) |

## Limits on this report's own claims

This catalog contains95 recoverable idea families, not 95 equally independent inventions or95 completed experiments. Original variants are named within the entries; repeated round histories are merged. The absent round 1 ledger and missing original expert-advice document prevent a literal claim to have recovered every original sentence/configuration. The coverage appendix establishes coverage of the extant proposal/report sections, not proof of complete historical records.

I can substantiate that the work had real measurements, useful engineering and several genuine combinations. I cannot substantiate that every idea received prolonged architecture optimization, that all defining learned mechanisms were implemented, that any global optimum was found, or that a new qualifying20% result was achieved. The proper repair is precise implementation and comparison of the missing mechanisms, rather than stronger rhetoric about the existing probes.

<!-- audit-coverage-generated -->

## Coverage appendix: extant proposal and report sections

This mapping is exhaustive for the headings in the four surviving idea files and rounds2–6 reports. The round2 earlier-lab section is the recoverable round1 source. A heading can cover several variants and maps to multiple consolidated families. It does not assert all those families were implemented.

| Source section (line) | Audit families |
|---|---|
| [hutter_prize_idea1.txt:7 — What a "Wordle compressor" would actually encode](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:7) | A09 |
| [hutter_prize_idea1.txt:73 — But random first guesses are probably a bad idea](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:73) | A09, A13 |
| [hutter_prize_idea1.txt:117 — Your word-length model is especially useful](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:117) | A11, A12 |
| [hutter_prize_idea1.txt:166 — You don't necessarily need two complete models](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:166) | A11, A83 |
| [hutter_prize_idea1.txt:184 — Here's where your architecture could beat autoregression](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:184) | A10, A88 |
| [hutter_prize_idea1.txt:232 — A better feedback alphabet than literal Wordle](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:232) | A09 |
| [hutter_prize_idea1.txt:289 — There may be an even better approach: reveal characters by confidence](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:289) | A10 |
| [hutter_prize_idea1.txt:335 — Confidence-ordered bidirectional coding](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:335) | A10 |
| [hutter_prize_idea1.txt:362 — We can still retain Wordle-style whole-word proposals](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:362) | A09, A13 |
| [hutter_prize_idea1.txt:414 — Another version might work even better: candidate rank coding](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:414) | A13 |
| [hutter_prize_idea1.txt:474 — The article-level aspect is possible too](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:474) | A11, A69 |
| [hutter_prize_idea1.txt:515 — A knowledge base could help, but there's a Hutter catch](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:515) | A27, A71 |
| [hutter_prize_idea1.txt:566 — Vector retrieval becomes especially interesting with your architecture](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:566) | A27, A71 |
| [hutter_prize_idea1.txt:599 — One fundamental limit still applies](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:599) | A09, A10 |
| [hutter_prize_idea1.txt:625 — Where I'd modify your original idea](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:625) | A09, A10, A11, A14, A27 |
| [hutter_prize_idea1.txt:676 — One more potentially important change](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea1.txt:676) | A14, A90 |
| [hutter_prize_idea2.txt:7 — Why the full OCR version probably loses](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:7) | A01, A02 |
| [hutter_prize_idea2.txt:51 — But your second idea is much better](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:51) | A04 |
| [hutter_prize_idea2.txt:107 — There's an even better interpretation of your idea](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:107) | A06 |
| [hutter_prize_idea2.txt:164 — Your proposed routing has one subtle problem](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:164) | A06, A15, A42 |
| [hutter_prize_idea2.txt:203 — Character fragments are interesting for a different reason](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:203) | A04 |
| [hutter_prize_idea2.txt:260 — A stronger version of your idea](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:260) | A06, A07 |
| [hutter_prize_idea2.txt:316 — The geometry model doesn't even have to be neural](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:316) | A05 |
| [hutter_prize_idea2.txt:362 — There is also a surprisingly interesting 2D version](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:362) | A08, A29 |
| [hutter_prize_idea2.txt:410 — Model-size economics are better than they initially look](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:410) | A06, A36, A95 |
| [hutter_prize_idea2.txt:482 — How I'd rate the variants](/C:/Users/91707/Downloads/compression_cmix/hutter_prize_idea2.txt:482) | A01, A02, A03, A04, A05, A06, A07, A08 |
| [idea_arch_1.txt:12 — 1. The object we should predict is the *word event*](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:12) | A67 |
| [idea_arch_1.txt:42 — 2. Letter algebra should define relationships, not codes](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:42) | A72 |
| [idea_arch_1.txt:117 — 3. Geometry becomes another basis](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:117) | A73 |
| [idea_arch_1.txt:162 — 4. We should also explicitly model edit relations](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:162) | A74 |
| [idea_arch_1.txt:225 — 5. Now comes the interesting part: **placement algebra**](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:225) | A78 |
| [idea_arch_1.txt:307 — 6. “The” is actually a more important example](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:307) | A79 |
| [idea_arch_1.txt:359 — 7. Combine the algebra and placement model](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:359) | A78, A79, A82 |
| [idea_arch_1.txt:392 — 8. Now implement your “transformer corrects the heuristic” idea—but in probability space](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:392) | A83, A84 |
| [idea_arch_1.txt:451 — 9. Multiple small transformers become residual experts](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:451) | A83 |
| [idea_arch_1.txt:513 — 10. There is a useful theorem about the Wordle idea](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:513) | A09, A13 |
| [idea_arch_1.txt:553 — 11. Hard words really can be “left in the archive”](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:553) | A06, A15 |
| [idea_arch_1.txt:597 — 12. We don't even need to change WRT](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:597) | A67 |
| [idea_arch_1.txt:639 — 13. And then we let cmix decide whether the new model deserves trust](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:639) | A42, A84 |
| [idea_arch_1.txt:693 — 14. The actual objective must be archive size, not accuracy](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:693) | A36, A95 |
| [idea_arch_1.txt:753 — Why the 37–40% category makes this worth trying](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:753) | A15, A64, A67 |
| [idea_arch_1.txt:778 — The architecture I would build](/C:/Users/91707/Downloads/compression_cmix/idea_arch_1.txt:778) | A72, A74, A78, A79, A80, A83 |
| [idea_arch_2.txt:15 — 1. A word creates an “echo field”](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:15) | A74, A77, A80 |
| [idea_arch_2.txt:70 — 2. The relation should have several independent channels](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:70) | A74, A82 |
| [idea_arch_2.txt:97 — Shared prefix](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:97) | A74 |
| [idea_arch_2.txt:106 — Shared suffix](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:106) | A74 |
| [idea_arch_2.txt:115 — Letter multiset](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:115) | A74 |
| [idea_arch_2.txt:131 — Ordered letter algebra](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:131) | A72 |
| [idea_arch_2.txt:159 — 3. Geometry can enter without pretending geometry itself predicts language](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:159) | A73 |
| [idea_arch_2.txt:207 — 4. The important new object is persistent activation](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:207) | A80 |
| [idea_arch_2.txt:271 — 5. But the injection should be learned](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:271) | A79, A80 |
| [idea_arch_2.txt:330 — 6. We can learn which parts of `diamond` matter](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:330) | A80 |
| [idea_arch_2.txt:379 — 7. This becomes much stronger when combined with placement](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:379) | A78, A79, A82 |
| [idea_arch_2.txt:445 — 8. A better mathematical interpretation is “latent lexical priming”](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:445) | A80 |
| [idea_arch_2.txt:495 — 9. It also differs from ordinary semantic embeddings](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:495) | A68, A78, A80 |
| [idea_arch_2.txt:563 — 10. The delay kernel can be learned](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:563) | A78, A81 |
| [idea_arch_2.txt:600 — 11. We should never maintain activations for the entire dictionary](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:600) | A75, A80, A81 |
| [idea_arch_2.txt:665 — 12. This produces “virtual memory”](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:665) | A77, A80 |
| [idea_arch_2.txt:710 — 13. Now combine it with the baseline predictor](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:710) | A67, A82 |
| [idea_arch_2.txt:783 — 14. A small transformer can learn the gate rather than the language itself](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:783) | A79, A83 |
| [idea_arch_2.txt:835 — 15. The residual transformer can also *reject* activations](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:835) | A80, A83 |
| [idea_arch_2.txt:889 — 16. We can train the activation system directly for bits saved](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:889) | A80, A90 |
| [idea_arch_2.txt:933 — 17. More interestingly, train individual lexical edges for *counterfactual bit savings*](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:933) | A81 |
| [idea_arch_2.txt:976 — 18. We could even define the optimal activation value mathematically](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:976) | A81 |
| [idea_arch_2.txt:1054 — 19. Multiple source words should accumulate evidence](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:1054) | A82 |
| [idea_arch_2.txt:1110 — 20. The previous placement model now becomes the second half of the system](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:1110) | A67, A78, A79, A80, A83 |
| [idea_arch_2.txt:1164 — The experiment sequence matters](/C:/Users/91707/Downloads/compression_cmix/idea_arch_2.txt:1164) | A74, A75, A76, A77, A78, A79, A80, A81, A82, A83 |
| [hutter_experiments_report.md:1 — Hutter Prize experiments: round 2 (Kaggle, 2 Oct 2026)](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:1) | A16, A19, A22 |
| [hutter_experiments_report.md:5 — 1. What the earlier lab had done](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:5) | A01, A02, A04, A05, A08, A09, A10, A11, A15, A16 |
| [hutter_experiments_report.md:19 — 2. Setup for round 2](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:19) | A16, A93 |
| [hutter_experiments_report.md:27 — 3. Results](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:27) | A15, A16, A18, A19, A22 |
| [hutter_experiments_report.md:29 — 3a. Stored size: more weights at fewer bits, or fewer weights at more bits?](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:29) | A16, A17 |
| [hutter_experiments_report.md:44 — 3b. Where the bits go (6.3M float transformer on the test articles)](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:44) | A15, A18 |
| [hutter_experiments_report.md:71 — 3c. Online adaptation ("dynamic evaluation")](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:71) | A19 |
| [hutter_experiments_report.md:84 — 3d. Do the gains stack? (ternary model, adaptation, then blending with CM)](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:84) | A22 |
| [hutter_experiments_report.md:95 — 4. What this means for the contest](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:95) | A07, A16, A17, A18, A20 |
| [hutter_experiments_report.md:103 — 5. Caveats](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:103) | A16, A19, A95 |
| [hutter_experiments_report.md:110 — 6. Files (in `hutter_lab/exp2/` on Kaggle)](/C:/Users/91707/Downloads/compression_cmix/hutter_experiments_report.md:110) | A93 |
| [hutter_ideas_report.md:1 — Hutter Prize: a fair test of the two idea files, plus context TTL (round 3, 2 Oct 2026)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:1) | A09, A10, A11, A12, A24, A25, A28 |
| [hutter_ideas_report.md:10 — 0. Bottom line](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:10) | A09, A10, A12, A25, A28 |
| [hutter_ideas_report.md:20 — 1. Fairness rules used](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:20) | A14, A36, A95 |
| [hutter_ideas_report.md:28 — 2. Results](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:28) | A09, A10, A11, A12, A14, A24, A25, A28 |
| [hutter_ideas_report.md:30 — 2.1 Progressive coding inside blocks (equal compute, 2,500 steps, 300 KB slice)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:30) | A10 |
| [hutter_ideas_report.md:43 — 2.2 The Hutter-regime arena (small 0.89M-weight models, about 20 passes, scored on their own training text)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:43) | A10, A36 |
| [hutter_ideas_report.md:55 — 2.3 Training that mimics decompression, and warm starts (2,500 steps, 300 KB)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:55) | A14 |
| [hutter_ideas_report.md:64 — 2.4 Wordle-style feedback against parallel decoding with the same number of model calls](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:64) | A09 |
| [hutter_ideas_report.md:74 — 2.5 Skeleton-first in the classical compressor (online counting, full 2.29 MB test)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:74) | A11 |
| [hutter_ideas_report.md:87 — 2.6 Word-length first, interleaved per word](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:87) | A12 |
| [hutter_ideas_report.md:98 — 2.7 Idea 2: character geometry](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:98) | A04, A05, A06 |
| [hutter_ideas_report.md:107 — 2.8 Online adaptation as a shared add-on (300 KB, one step per 4 KB)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:107) | A19 |
| [hutter_ideas_report.md:114 — 2.9 Context TTL: analysis](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:114) | A15, A25, A26 |
| [hutter_ideas_report.md:132 — 2.10 Context TTL: memory models (2,500 steps each, full test)](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:132) | A24, A25, A27, A28 |
| [hutter_ideas_report.md:156 — 3. What is worth carrying forward](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:156) | A04, A05, A09, A10, A12, A24, A25, A28 |
| [hutter_ideas_report.md:170 — 4. Next steps, most promising first](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:170) | A12, A24, A25, A28 |
| [hutter_ideas_report.md:177 — 5. Caveats](/C:/Users/91707/Downloads/compression_cmix/hutter_ideas_report.md:177) | A25, A28, A95 |
| [hutter_context_miner_report.md:1 — Hutter Prize round 4: context miners, letter-algebra codes, and overfitting the data (2–3 Oct 2026)](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:1) | A29, A30, A31, A32, A33, A34, A35, A36 |
| [hutter_context_miner_report.md:8 — 0. Bottom line](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:8) | A34, A35, A36 |
| [hutter_context_miner_report.md:53 — 1. Answers to the questions](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:53) | A15, A25, A29, A33 |
| [hutter_context_miner_report.md:83 — 2. Context miners (decoder-side, zero archive cost)](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:83) | A19, A31, A32, A33, A34, A35 |
| [hutter_context_miner_report.md:108 — 3. Letter-commonality codes and letter algebra](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:108) | A29, A30 |
| [hutter_context_miner_report.md:132 — 4. Overfitting the dataset (contest arena)](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:132) | A36 |
| [hutter_context_miner_report.md:146 — 5. Caveats](/C:/Users/91707/Downloads/compression_cmix/hutter_context_miner_report.md:146) | A33, A35, A36, A95 |
| [hutter_round5_report.md:1 — Hutter Prize round 5: working on the real record pipeline (enwik9), 3 Oct 2026](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:1) | A37, A38, A39, A40, A41 |
| [hutter_round5_report.md:7 — 0. Bottom line](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:7) | A37, A38, A39, A40, A41 |
| [hutter_round5_report.md:25 — 1. The landscape (researched first)](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:25) | A95 |
| [hutter_round5_report.md:39 — 2. What I set up on Kaggle](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:39) | A93, A94, A95 |
| [hutter_round5_report.md:66 — 3. Anatomy of the record (measured)](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:66) | A15, A36, A95 |
| [hutter_round5_report.md:97 — 4. Experiments](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:97) | A37, A38, A39, A40, A41, A42, A43, A44, A45 |
| [hutter_round5_report.md:99 — 4a. Gains](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:99) | A37, A38, A39, A40, A41 |
| [hutter_round5_report.md:109 — 4b. No gain (measured, then dropped)](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:109) | A20, A21, A23, A42, A43, A44, A45 |
| [hutter_round5_report.md:124 — 5. The community (Kaggle forum) ideas](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:124) | A08, A15, A25, A56, A72 |
| [hutter_round5_report.md:156 — 6. Caveats](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:156) | A93, A95 |
| [hutter_round5_report.md:165 — 7. Kaggle disk and deletions](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:165) | A94 |
| [hutter_round5_report.md:172 — 8. Next steps (most promising first)](/C:/Users/91707/Downloads/compression_cmix/hutter_round5_report.md:172) | A37, A38, A39, A40, A41, A44, A56, A57, A90, A95 |
| [hutter_round6_report.md:1 — Hutter Prize round 6: implementing the expert advice (3 Oct 2026)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:1) | A32, A46, A47, A48, A49, A50, A95 |
| [hutter_round6_report.md:11 — 0. Bottom line](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:11) | A46, A47, A48, A49, A50, A95 |
| [hutter_round6_report.md:48 — 1. The expert's eight steps: what was done](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:48) | A32, A46, A47, A48, A49, A50, A56, A95 |
| [hutter_round6_report.md:61 — 2. Cost ledger](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:61) | A36, A95 |
| [hutter_round6_report.md:63 — 2a. Components (both entries)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:63) | A36, A95 |
| [hutter_round6_report.md:77 — 2b. Revision records (243,425 per-article records, 15,717,594 post-WRT bytes)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:77) | A15, A47, A48, A49, A54 |
| [hutter_round6_report.md:99 — 2c. Vocabulary saturation in the exact enwik9 coding order](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:99) | A15, A25, A33, A71 |
| [hutter_round6_report.md:108 — 3. Retrieval experts against the complete coder (step 4)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:108) | A32, A55 |
| [hutter_round6_report.md:128 — 4. Compression-aware QAT (step 5)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:128) | A46 |
| [hutter_round6_report.md:155 — 5. Structural experts (step 6, stream-preserving)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:155) | A47, A48, A49, A50, A56 |
| [hutter_round6_report.md:247 — 5c. Further experts screened against the final coder (all rejected)](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:247) | A51, A52, A53, A54, A55 |
| [hutter_round6_report.md:274 — 6. Correctness checks performed](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:274) | A93, A95 |
| [hutter_round6_report.md:296 — 7. What remains open](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:296) | A47, A49, A50, A56, A90, A95 |
| [hutter_round6_report.md:309 — 8. Files](/C:/Users/91707/Downloads/compression_cmix/hutter_round6_report.md:309) | A93, A95 |

### Round7 experiment-registry coverage

Registry names are retained for handoff. The report's dated provisional statuses are superseded where later corrected evidence exists. Coverage is not a completion flag.

| Registry item | Audit families |
|---|---|
| L01 | A17 |
| L02 | A17, A40, A41 |
| L03 | A17, A93 |
| L04 | A93, A95 |
| L05 | A57 |
| L06 | A58 |
| L07 | A59 |
| L08 | A62 |
| L09 | A63 |
| L10 | A42 |
| L11 | A64 |
| L12 | A64 |
| L13 | A65 |
| L14 | A66 |
| L15 | A66 |
| L16 | A43 |
| L17 | A45 |
| L18 | A15, A76 |
| L19 | A68, A92, A93 |
| L20 | A93 |
| F01 | A93 |
| I01 | A72, A73, A74, A75 |
| I01b | A75 |
| I01c | A75 |
| I02 | A76 |
| I03 | A77 |
| I03b | A75, A77 |
| I04 | A78 |
| I04b | A71 |
| I05 | A67, A79, A84 |
| I06 | A79 |
| I07 | A24, A25, A32, A71, A77 |
| I08 | A73, A74 |
| I09 | A80, A81 |
| I10 | A68, A69, A70, A83, A84, A90, A92 |
| I11 | A85, A86, A87, A88 |
| I11b | A85, A86, A87 |
| I11c | A85, A87 |
| I12 | A89 |
| P01 | A95 |
| P02 | A64 |
| P03 | A63, A64, A84 |
| P04 | A60, A61 |
| P05 | A94, A95 |

Validation checks 95 ordered entries, three answers for every entry, all mapped source headings, registered experiment IDs, existing evidence files and valid file-line anchors. The accompanying JSON includes source SHA256 hashes, per-entry fields and exact mappings. It validates the report's structure/provenance; it does not reproduce historical experiments.
