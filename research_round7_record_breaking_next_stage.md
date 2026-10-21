# Audit and next record-breaking research stage

Prepared 6 October 2026 IST. Status: design and evidence audit; the new architectures below have not been trained or measured. No paid instance, new Kaggle job or Goal mutation is asserted by this document.

## What the completed experiments establish

The runs were real and their outputs are preserved. The final batch contains four 2M-byte final-uint16 replays of 15 causal expert families at four fixed strengths, corrected root/new-mention/EOF screens, six numeric programs, four lossless template packet comparisons, A/B-fitted 128-factor calibration, fresh E/F native encoder/decoder checks, a full preprocessing inverse and 48 exact prior-storage comparisons. Source, binary, input and output hashes are retained. The exact numerical results are in `research_round7_final_batch_summary.json`; both fresh native corrections also pass `research_round7_native_calibration_local_validation.json`.

This is thorough measurement of a bounded set of implementations. It is not a thorough search of the central learned architectures in `idea_arch_1.txt` and `idea_arch_2.txt`. Fixed neighbor boosts do not implement their learned relation function, context-dependent suppression, fitted survival/TTL, trained lexical state or residual transformer. Constructor packet tests through generic codecs do not implement a bidirectional neural infilling codec. The core transformer has not been finetuned in this round. No matched full-history production comparison has been executed. Cold sampled results on the older FX2 stream do not exhaust the production lexical ordering.

The selection was conservative and strongly anchored to the existing pipeline. That helped make likelihood, normalization and package accounting reliable, but limited architectural exploration. A negative narrow screen should reduce the priority of that screen, not veto a learned mechanism with additional interactions. Numerical parity is required for core-transformer continuation; it need not block training an independent residual predictor on native-produced causal features and final-bit probabilities.

An earlier answer also needs correction: the approximately54.9KB packing-component saving is on the older FX2 uniform-Q4 model. It is not a validated saving on the lexical C3 codebook checkpoint, and cannot simply be subtracted from its99.31MB package. It is an observed laboratory component result, not a no-training compression ceiling.

## Exact success criterion

The official awarded reference is100,424,672B. The strongest pending total listed by the benchmark is zmix1.0 at99,312,424B; lexth11c is99,313,750B. The archive-only ranking uses another denominator. Target the strongest complete-package total as well as qualifying under the official rules. [Prize page](https://www.hutter1.net/prize/), [benchmark package totals](https://mattmahoney.net/dc/text.html)

Beating99,312,424B requires a qualified package of at most99,312,423B. A strict reduction greater than20% requires at most79,449,939B. A first reproducible net gain of about1MB is a useful milestone because it is large enough to dominate small packaging differences and validate the research direction. It is not a replacement for the20% objective.

For a frozen transformed stream of length T, final coded improvement delta_h, per-copy model change delta_M and other stored change delta_A:

\[
\Delta S_{\rm saved}=T\,\delta_h/8-2\,\Delta M-\Delta A.
\]

Use the actual copy count and complete package. Replace T=586,459,020 with the production lexical stream length when that stream is verified. All fields are measured; a neural-loss improvement is not automatically delta_h. Full decode, CPU time and RAM remain hard constraints.

## Priority 1: learn a residual against the native final coder

Train a small predictor of the residual that the native coder actually pays. Let p_t be its recorded integer probability of bit1, y_t the true bit, and c_t a feature vector available from already decoded bytes. Candidate probability is

\[
q_t=Q_{16}\{\sigma[\operatorname{logit}(p_t/65536)+r_\theta(c_t)]\}.
\]

Features may include the known bit prefix and position, baseline confidence, completed-word rank/class, constructor-run state, parsed article/title state, distances to completed lexical events and deterministic spelling relations. Never include the unknown target's word identity, POS, length, first-mention status or future neighbor occurrence as an inference feature. Those can be diagnostic or training labels only.

This is distinct from fitting128 constant calibration biases. Train context-dependent interactions, particularly whether a spelling/semantic relation should be activated or suppressed in the present syntax/topic. All excited incorrect candidates must contribute to the normalized loss. Use a low-rank table or small MLP and register hard parameter budgets, initially32KiB and128KiB per stored copy. Those are proposed caps, not achieved container sizes.

The loss is

\[
J(\theta)=-\sum_t\log_2 q_t(y_t)+2L(\theta)+L(\text{new code/assets}).
\]

For the smooth surrogate, the derivative with respect to residual log odds is (q_t-y_t)/ln2. This gives direct training supervision without differentiating the original cmix model bank. Train with the exact forward quantization contract or an explicit straight-through approximation, then select only through actual native coded probabilities and package size.

Keep the baseline predictor's internal updates unchanged. Only its arithmetic-coder probability is corrected. Its internal trajectory then remains the measured baseline trajectory during teacher-forced training and actual encode/decode of the same bytes. Decoder and encoder must compute the same residual from their causal state. A separate head requires its own export/identity tests, but does not require a faithful GPU port of the original transformer. This removes an avoidable dependency from the previous research sequence.

Use a deterministic integer odds map, extending the verified calibration algebra:

\[
A=pF,\quad D=A+(65536-p)2^{20},\quad
q=\operatorname{clip}_{1,65535}\lfloor(65536A+\lfloor D/2\rfloor)/D\rfloor.
\]

The neutral factor F=2^20 must preserve every probability. Register the residual grid, saturation and exp/odds lookup as model/code assets; do not silently substitute a float training function for another CPU inference function. Preserve all outcomes, literal/control bytes and EOF.

## Priority 2: pay for a small article-level latent rather than demanding free hints

This is the most distinct next architecture. The encoder knows the complete article. It chooses a compact discrete latent z_a and transmits it before the article body. The decoder then knows that latent legitimately. It may summarize the topic, entities, spelling family or document schema and can help first mentions before their relevant source word has appeared locally.

Instead of assuming a previous `no` must remind the model of `know`, test whether a small paid topic/entity signal plus causal syntax/memory predicts which familiar word belongs here. The sampled atlas assigns roughly37–43% of final bits to known words first mentioned in a new article; that is a target budget, not recovered compression.

For each article, choose

\[
z_a^*=\arg\min_{z\in\mathcal Z}\left[L(z\mid\text{decoded title})+
\sum_{t\in a}-\log_2 q_t(y_t\mid c_t,z)\right].
\]

This argmin specifies the objective, not a claim of an exact global search. Initially test a finite categorical codebook and then short quantized vectors using a bounded registered search. The complete package cost is

\[
2L(\theta)+L(\text{encoder selector/code})+
\sum_aL(z_a\mid\text{decoded title})+
\sum_t-\log_2q_t(y_t\mid c_t,z_a)+L(\text{other assets}).
\]

If latents are encoded in the archive stream and the compressor computes them, they are paid once in that stream. If an offline latent table is embedded in both submitted binaries, both copies are paid instead. Do not count offline future-dependent latent choices as free causal features. Encoder lookahead is valid only because its selected information is transmitted and encoder runtime is included.

The decoder must know exactly when to read a latent from already decoded framing. Attach it after a complete observed article/title marker; orphan prefix data uses the ordinary fallback. Latent bits do not update the baseline text predictor as if they were original text. Count framing, null-latent flags, codebook/scales, selectors and all articles where the signal is useless. Compressing latents with a title-conditioned prior is itself a priced model.

Compare three modes with the same residual capacity: no latent; a latent computed only from decoded title/history; a paid latent selected using the whole article. For the paid mode register null, categorical and4/8-byte vector budgets, subject to total cost. An oracle that supplies the best latent without its transmitted cost is a diagnostic only. Saving on first mentions while losing on the rest is not enough; optimize the complete normalized stream.

## Priority 3: learn associative lexical memory, including rejection

Implement the actual central hypothesis in the idea files. After a word u completes, a learned shared relation R_theta(u,v,c) proposes a sparse activation for candidate v. Its survival is context-dependent:

\[
m_{t+1,v}=m_{t,v}\exp[-\operatorname{softplus}(h_\theta(c_t,v))]
+g_\theta(c_t,u,v)\,R_\theta(u,v,c_t).
\]

This is a design equation. Bound memory and arithmetic; train its exported forward approximation and charge code/parameters. Use deterministic spelling/morphology features plus a learned low-rank residual, then condition on title, syntax and confidence. The decoder performs the same update only after a completed observed word. False associations and forgotten useful items must both affect the same complete coding loss.

Compare identical-capacity no-memory, exact-word memory, structural memory and shuffled/random-neighbor controls. Include a generic learned capacity control so that extra parameters alone cannot be credited to letter algebra. Train the null-memory control first. Literal/OOV words need an explicitly supported mechanism; an unknown-class fallback is not a completed all-word memory architecture.

The priority is learned first-mention prediction, not an unconditioned increase in every neighbor's probability. A learned gate may legitimately suppress almost all geometric/phonetic relations if they are not useful. Conversely, fixed-boost losses do not establish that the gate cannot learn useful interactions.

## Priority 4: a paid content-first constructor codec

Retain this as an architectural alternative, because generic constructor packets did not test neural right-context infilling. Define an exact reversible split x <-> (C,G,A): C is the ordered content stream, G the ordered constructor choices, and A all alignment, lengths, casing, punctuation and exceptional layout needed for reconstruction.

Evaluate

\[
L(C)+L(A\mid C)+L(G\mid C,A)+L(\text{all models and code}).
\]

Decode C/A first, then let the grammar model use both neighboring content anchors. That makes future content available through paid order of transmission. Preserve constructor order: a bag or subset alone cannot reconstruct the sentence. This branch requires a new trained model for the changed content stream; feeding stripped text into the original model is not a valid model-matched test.

Constructors alone carried about17.2% of the sampled native bit budget, so an intervention confined solely to those bits cannot deliver20% total reduction even if it makes them free. A20% candidate must also improve content, alignment or other payload components. Quantify all three streams before funding a larger infiller.

## Execution sequence and decisive gates

1. Assemble native-produced causal feature/target records for representative complete pieces, with immutable hashes. Use the existing traces for development, then new whole-piece regions; label cold versus warm histories honestly. Production lexical preprocessing must be verified before a complete-record claim.
2. Train the independent residual null/control, learned interactions and paid-latent pilot under the same byte/rate caps. These pilots do not wait for core-GPU parity repair. Preserve the selector, latency and code costs.
3. Advance only a model that improves complete held-confirmation coding after quantization and side information. Confirmation is an engineering guard against a bad extrapolation; the prize does not require generalization to unseen Wikipedia. Later whole-corpus fitting is permitted when its learned information is fully stored and priced.
4. Verify native reference/neutral identity, independent candidate decode and complete uint16 replay. For latents, include their actual arithmetic-coded stream and every null/miss. Never promote a free per-event oracle.
5. In a separate branch, locate the first failing layer/state operation in the existing FX2 GPU parity diagnostic, then verify lexical F0 and representative F1 continuation. The current diagnostic is on the compatible FX2 control; it is not proof that a completed lexical GPU reproduction exists.
6. Fund the$36winning continuation only after native priced confirmation. The two branches compete under the same$70cap; the independent-head pilot uses the existing$12screen allocation, not an additional budget. No live offer is assumed.
7. Build the complete production package for a survivor, decode1B bytes independently, and measure single-core compression/decompression time and peak RAM/disk. The near10GB baseline leaves little headroom; a large cache/head must pay for a tested reduction elsewhere. Cold-piece RSS is not full-run RSS.

Keep the strongest pending comparator and the20%target visible throughout. A successful small pilot is evidence of a path; only a reproducible qualifying full package establishes a record. The negative completed screens, the unexecuted learned branches and the new proposals remain separate in the evidence ledger.
