<!-- training-plan-current-20261005 -->
Current detailed execution plan: `research_round7_finetuning_execution_plan.md`;
machine-readable contract: `research_round7_training_contract.json`. The bounded
no-retraining batch has completed, with no qualifying gain. Old-FX2 inverse and
lossless prior-storage probes pass; full lexical data/priors and neural parity
still gate training. Spent$0; staged total$70. Earlier plan material below is
historical where it conflicts with the current contract.

**Round 7 training research — 4 October 2026, Asia/Calcutta**

This is a budgeted experiment design, not a claim of a compression breakthrough. No Kaggle files were accessed or changed for this subtask, no rental was made, and no Vast.ai account was accessed. Evidence comes from the local round-5/round-6 reports and harness, and the primary sources linked beside the relevant claims. The inherited AGENTS material located in a parent directory concerns an unrelated Orbit Wars project and supplies no Hutter training requirements.

**Recommendation.** Use the existing competitive model and repair continuation fidelity before buying a full retrain. Spend at most $4 on a paid throughput/parity pilot, then at most $12 on matched controls and an MDL sweep. Release the main training allocation only if a candidate improves the final coder after its actual duplicated weight-container cost is counted. There is no evidence supporting a guaranteed 20% improvement or an attained global optimum.

**The objective and the scale of the requested result.**

Let T = 586,459,020 be the post-WRT symbol count, N = 5,868,864 the reported quantized parameter count, P = 93,770,082 the baseline payload bytes and S = 100,424,672 the official total used by the reports. The payload is 1.27913568 bits per transformed symbol. A greater-than-20% reduction in this S requires a package of at most 80,339,737 bytes: more than 20,084,934 bytes saved. With unchanged fixed components, that requires approximately 0.27398244 final-coder bits/symbol saved.

Even making both 2,930,652-byte weight files entirely free would save only 5,861,304 bytes. At least approximately 14.224 MB of additional payload improvement would still be required. That hypothetical does not represent an achievable weight representation: it is a ceiling that demonstrates why weight packing alone cannot supply the requested result. A 20% neural cross-entropy reduction, a 20% perplexity improvement, a 20% payload reduction and a 20% total-package reduction are distinct measurements and must be reported separately.

For a fixed decoder architecture, the training target in bits is

    J_total(theta) = L_final_coder(x; theta) + 2 L_weight_container(theta)
                    + L_compressor_code + L_archive_stub + L_dictionary/order/etc.

Changing the representation or architecture changes the last terms too. The factor two applies to this packaging arrangement; it must be re-enumerated if the compressor/archive arrangement changes. CPU runtime, memory and exact reconstruction are hard feasibility constraints, rather than just soft penalties. The rules count supplied programs as well as compressed data and require single-core CPU execution within the stated time/memory/disk limits. Offline GPU training is not the qualifying inference path. [Official detailed rules](https://www.hutter1.net/prize/hrules.htm)

For a neural-loss surrogate measured in bits/token, the first MDL approximation is

    J_proxy = H_neural + lambda * 2 L_weights_bits / T.

Lambda = 1 corresponds to the stated duplicated-weight accounting, not lambda = 30. The surrogate does not equal final cmix/SSE loss. Final-coder measurements select candidates.

**What round 6 actually establishes.**

Known measurements: 100 steps of lambda = 0 increased evaluation neural loss from about 1.5103 to 1.5465 bits/token; lambda = 30 reached about 1.5721. Compared with the matched control, the rate term reduced the two-copy entropy estimate by about 174,601 bytes while adding approximately 0.025639 bits/token on that evaluation. A direct full-stream extrapolation is approximately 1,879,531 extra payload bytes, about 10.8 times the corresponding break-even rate. This is a failed screen, not an observed final-coder archive regression of that size.

The reported continuation uses only the first 150M tokens, and only about 198.6M tokens have existing priors. Its evaluation is held out from the continuation but was already seen by the original pretrained model. The code audit summarized in the preceding project review found article-uniform sampling, prefix truncation for long articles, fresh optimizer state and omitted later article positions. These can produce distribution drift even with lambda = 0. Neither this experiment nor a scale-inflation probe establishes that balanced continuation cannot work.

Control repair is a prerequisite. If lambda = 0 still degrades broadly, do not interpret subsequent lambda differences as a good reason to spend on a scratch retrain. First isolate input parity, sampling, optimizer, quantization and export behavior.

**Primary-source baseline and numerical contracts.**

The original authors report 8 RTX 5090 GPUs for 26 hours, approximately 208 GPU-hours, and a staged schedule of 320 unquantized, 256 QAT and 16 float32 cooldown epochs. The model uses a byte stream plus PPMD inputs; 4-bit weights and quantized activations enable CPU inference. This is a measured reference cost, not a promise that an arbitrary new training setup will reproduce it. [Original writeup](https://github.com/astOwOlfo/fx2-cmix-transformer-v1/blob/main/writeup.md)

The public recipes currently differ from that prose: `train_6m.py` declares 320 epochs, while `quantize.py` declares 128. Reproducing the paper's 592-epoch schedule requires resolving that discrepancy and pinning a commit/configuration. Never silently label a public-script run as an exact reproduction of the published schedule. The baseline recipe sets a global approximately 2^20-token micro-batch split across ranks, d=192, 12 layers and article-piece length <=2^17. Preserve the effective loss-bearing batch when changing GPU count; do not mechanically copy an ambiguous scaling instruction. [Baseline recipe](https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/training_recipes/train_6m.py)

The QAT recipe explicitly warns that `torch.compile` removes a required bf16-to-float32 scale conversion. It quantizes weights into 15 buckets and activations into 256 buckets, uses quantization-aware forward passes, and retains float32 latent weights. Any compilation experiment must prove that scale rounding and export still match. [QAT recipe](https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/training_recipes/quantize.py)

The cooldown recipe uses float32 activations/attention and a very small learning rate. It is a useful fidelity reference, not evidence that 16 more epochs will improve this project's continuation. [Cooldown recipe](https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/training_recipes/cooldown.py)

The stronger lexth11c entry changes both the quantization contract and the non-neural core: learned/frozen nonuniform int4 codebook, dynamic int8 activation scales, 8-bit small tables and a retrained model. It must be evaluated with its own compatible exporter, loader, PPMD behavior and transformed stream. One cannot swap a lex checkpoint into the older harness and assume fidelity. Its published total is 99,313,750 bytes; its README reports near-limit RSS. [lexth11c source and evidence](https://github.com/Neel49/cmix-lex-transformer/blob/main/README.md)

**Data preparation must precede paid GPU time.**

Full dense float16 PPMD priors require

    T * 205 * 2 = 240,448,198,200 bytes = 240.448 GB.

Tokens, binaries, temporary output, shards and checkpoints add to that. The original README asks for approximately 300 GB for preparation. [Training-data instructions](https://github.com/astOwOlfo/fx2-cmix-transformer-v1)

The local `round5/tfh.py` sparse format stores entries above 0.0007 and reconstructs omitted entries as zero. Its prior format is therefore approximate. Existing near-parity results are useful, but after fine-tuning a model could become more sensitive to the omitted inputs. Revalidate every candidate with production priors. Where possible, store exact float16 inputs in independently compressed shards and decompress only the active shard. Check compressed size on representative early, middle, late and metadata sections before committing to a full dump.

A thresholded 15-33-entry sparse representation would occupy roughly 27-59 GB including counts and before indexing overhead, but that size is not a guarantee for an exact sparse representation. Avoid an 8-byte offset at every token, which would itself cost 4.69 GB. Use block prefix offsets and scan short count blocks. A 100% full-stream data manifest must record checksums, stream/order/dictionary version, vocabulary mapping, PPMD settings, row alignment and piece boundaries.

Generate priors on available CPU while preparing software, without an idle paid GPU. If only 34% of priors are available, label a continuation as subset training. Do not claim a whole-corpus MDL result from that subset. For transformations, regenerate corresponding priors; stale original-stream priors are not valid for a reordered or recoded stream.

Choose an offer's disk allocation from the measured representation size plus an explicit free-space margin. Full dense storage needs >=300 GB; a verified compressed/sharded path may need much less. Dense neural output probability files would again approach 240 GB per checkpoint. Stream them through the lab coder or retain only bounded slice files, scalar true-token probabilities and final cost dumps. Persist model/optimizer state and compact logs; do not retain multiple full probability matrices.

**Representative sampling with correct causal state.**

Use the production article boundaries and deterministic 2^17 splits. Shuffle whole legal pieces and process all of each chosen piece, including the interior of long articles. Sum token losses and divide by the number of eligible target positions, not the number of articles. Mask padding and reset/fallback tokens exactly as inference does. Training can shuffle pieces because their neural states reset, but their PPMD inputs must be those generated in the true coding order.

The public loader supplies each full piece without prefix truncation, drops only incomplete trailing batches and masks padding. For smaller GPUs use gradient accumulation or activation checkpointing, rather than truncating long articles to their first 32K symbols. Its shifted inputs predict token i+1 from input token i and prior row i. Validate that convention against C++ on starts, ends and 2^17 cuts. [Public data loader](https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/pysrc/data.py)

If shorter random training windows become necessary, preserve the exact causal prefix state with burn-in/prefill. For KDA, 1,024 tokens of attention burn-in alone does not reconstruct the recurrent state from the article start. Either use the whole legal piece or use a validated recurrent-state prefill. Any detached-prefix gradient approximation should be documented, while the forward predictions remain identical.

Create a fixed diagnostic manifest of body, titles, link targets, markup, numerical strings, tables, revision fields, interlanguage titles and rare spellings distributed across the whole coding order. Include long-article interiors, early/late redirects and recurring/first-appearance entities. Use token-length weighting for the primary mean. Keep a separate difficult-span set to investigate behavior; do not substitute that set for full-corpus evaluation.

All corpus positions can ultimately be used for Hutter training, since the package cost accounts for memorization. During search, reserve a stable diagnostic set from each continuation to detect drift; describe it as continuation-held-out, not unseen by the baseline. Freeze selection manifests before comparing arms.

**Budget based on measured delivered tokens, not nominal hardware.**

Vast.ai is a host-priced marketplace; costs include compute, continuous storage and transfer. Storage can remain billable on stopped instances. Quote an exact offer immediately before a rental and keep its metadata. The official RTX 5090 page exposed no quotable matching offer during this review; that does not prove that every 5090 listing is unavailable. No usable live rate was obtained, so the rates below are scenarios. [Official pricing](https://docs.vast.ai/guides/instances/pricing), [RTX 5090 page](https://vast.ai/pricing/gpu/RTX-5090)

Reserve $10 for storage, transfer and CPU verification contingency; provisionally allocate $60 to GPU work. If the contingency is inadequate after quoting data transfer or verification, reduce GPU allocation rather than exceeding $70.

| Actual compute rate per GPU-hour | GPU-hours purchasable with $60 |
|---:|---:|
| $0.40 | 150 |
| $0.50 | 120 |
| $0.60 | 100 |
| $0.80 | 75 |
| $1.00 | 60 |

For a multi-GPU listing, distinguish instance dollars/hour from per-GPU dollars/hour. Storage is not simply multiplied by GPU count. Let r be the GPU rate, s the storage dollars/GiB-hour, D the allocated GiB, h the instance hours, n the GPU count and B_in/B_out the transferred GB. Compute all-in cost from the actual offer units:

    cost = n*r*h + s*D*h + transfer_in_rate*B_in + transfer_out_rate*B_out
           + preparation/verification costs.

The screening metric is dollars per billion useful target tokens, including data-loader stalls, QAT overhead and setup time. A cheaper slower GPU can beat a 5090; benchmark a 4090 alternative if its all-in useful-token cost is materially lower. Do not assume theoretical FLOPS or marketplace DLPerf predicts this small model's cost.

For useful throughput v tokens/second/GPU, one equivalent full pass takes T/(3600v) GPU-hours. These are planning scenarios, not 5090 measurements:

| Useful throughput | GPU-hours/full pass | Full-pass equivalents/100 GPU-hours |
|---:|---:|---:|
| 11,800/s (round-6 T4 measurement) | 13.806 | 7.24 |
| 40,000/s | 4.073 | 24.55 |
| 100,000/s | 1.629 | 61.39 |
| 200,000/s | 0.815 | 122.77 |
| 400,000/s | 0.407 | 245.54 |

The original 592-epoch/208-GPU-hour claim implies approximately 463,653 useful tokens/s/GPU averaged across that schedule if each epoch covers the stated T. That derived number is not an independent throughput measurement and must not be transferred to a different QAT kernel or loader. Round-6's 11,800/s has a different implementation and regime.

A literal 208-GPU-hour reproduction fits $60 only at <=$0.28846/GPU-hour, before other expenses. At $0.40/$0.60/$0.80 it would cost $83.20/$124.80/$166.40 for compute. At least approximately $95-$185 total would be prudent for that narrow reproduction, depending on actual ancillary charges; no 20% gain follows from paying that amount. A new 1280-epoch run is not budgeted by analogy alone.

**Concrete spending stages.**

| Stage | Maximum compute spend | Release condition |
|---|---:|---|
| Pilot: environment, full-piece batch, parity and throughput | $4 | Compatible kernels/export and useful-token measurement |
| Control repair and matched lambda sweep | $12 | Baseline-preserving lambda=0, representative data |
| One winning continuation with scheduled rate term | $36 | Positive final-coder-plus-container screen |
| Numerical cooldown, export evaluation and finalist GPU probabilities | $8 | Candidate still beats baseline ledger |
| Ancillary contingency | $10 | Quote storage/transfer/CPU work before use |
| Total ceiling | $70 | Do not rely on credit exhaustion as shutdown |

These are ceilings, not a requirement to consume each allowance. Unspent control budget can be reallocated to the winner. Start with one 5090 because the model is small and avoids multi-GPU setup/communication uncertainty. If a two-GPU pilot demonstrates better delivered tokens/dollar, retain the same effective global batch and use it. Choose on-demand for the short compatibility pilot. Interruptible training is appropriate only after atomic resume checkpoints are verified; include restart/transfer overhead in comparisons. The official CLI supports on-demand, reserved and bid searches, plus storage-size pricing. [Search-offers reference](https://docs.vast.ai/cli/reference/search-offers), [Instance types](https://docs.vast.ai/guides/instances/choosing/instance-types)

An offer search to review, not a command executed in this subtask:

    vastai search offers 'gpu_name=RTX_5090 num_gpus=1 verified=true rentable=true reliability>0.98 direct_port_count>=1' --type on-demand --storage <measured_GiB> --order dph_total --raw

Inspect CPU allocation, RAM, disk bandwidth, driver, rental duration and data-transfer rates as well as price. Match the CUDA/PyTorch/FlashAttention/FLA versions proven by the pilot. Capture GPU power throttling and loader stall statistics during the measured run. Finish export/copy checks before destroying an instance to end billing.

**Pilot and continuation design.**

1. Load an exact exported baseline checkpoint. Require baseline likelihood parity with the existing harness and independently verify C++ quantized inference on at least early/middle/late slices and boundary cases. Keep a fixed baseline checkpoint and hashes. Do not compile QAT until the scale-rounding contract survives export.
2. Benchmark useful targets after compilation/warmup using representative whole pieces. Record allocated vs loss-bearing tokens, throughput, VRAM/RSS, read rate and total elapsed time. Compare native optimized 5090 kernels against the T4 fallback. Include a cold shard transition so the pilot measures I/O reality.
3. Restore original optimizer state if it exists. Otherwise use a conservative warm-start schedule and matched controls. Compare the compatible original Muon/AdamW arrangement with a conservative Adam continuation only if necessary; changing both optimizer and loss simultaneously destroys attribution. Start around the source cooldown's small-LR regime and increase only if control traces support it. No exact LR is known to be optimal.
4. Lock the token stream, QAT levels, rounding, piece semantics, global batch and target manifest. Run lambda=0 first. A frozen zero-update export is a separate sanity control. Permit scale changes only after an initial parity-preserving phase, since post-training scale inflation already failed badly.
5. Screen lambda in {0, 0.3, 1, 3}, all from the same starting checkpoint, with identical token exposure and schedules. Ramp the rate term from zero after the continuation stabilizes. Lambda=30 is not a priority. Use a simple per-tensor categorical rate model initially; add codebooks or hyperpriors only if they reduce the actual packed container after their metadata/decoder costs.
6. Checkpoints should record processed useful tokens and full-pass equivalents, not only steps. Export each meaningful checkpoint, encode its actual weight container and measure its final-coder slice cost. Keep only the initial checkpoint, best qualifying checkpoint and latest resumable checkpoint per active arm.
7. Continue only the best total-size arm. Retain a matched lambda=0 checkpoint at similar exposure. End with numerically faithful export/cooldown only if its measured net effect is positive. Do not assume cooldown always helps.

For rate modeling, R = -sum_i log2 r_tensor(q_i) + scales/codebook/framing bits is a starting proxy. Estimate categorical probabilities with proper smoothing and freeze/stop-gradient only the probability estimator when appropriate. Quantizer assignments need a specified straight-through or soft relaxation. Encode the resulting discrete codes with the production container: soft entropy, hard empirical entropy and actual file bytes should all be logged. The rate term has an extremely small valid gradient scale because T is large; check units and whether CE is in nats or bits. If CE is in nats, the matching weight-rate term in nats is ln(2)*2R/T.

The per-weight entropy trade-off is especially tight. Reducing entropy by 1 bit/weight saves 1.467216 MB across both copies. It tolerates only about 0.020014 bits/token of additional final-coder loss. A 0.1-bit/weight saving tolerates about 0.0020014 bits/token. Quantization-aware training must find this Pareto frontier, not merely make many weights zero.

**Residual-directed training is a hypothesis worth a bounded pilot.**

The difficult-word atlas should aggregate actual final-coder bits, not count surprising examples or word types. Group spans by first/repeated appearance, title/link/metadata role, recurrence distance, article position and spelling family. Known-word selection can dominate novel-spelling bits. Train the main body as well as the metadata: metadata-only improvements cannot plausibly supply the remaining tens of megabytes.

A bounded sampling distribution can combine uniform token exposure with residual importance. For example, pi_t = eta/T + (1-eta)c_t/sum c, where c_t is a frozen nonnegative residual score and eta initially stays large. To preserve the uniform likelihood objective, use importance factor 1/(T*pi_t); otherwise state clearly that an intentionally reweighted objective is being optimized. Freeze or update the atlas between arms, not independently during a comparison. Do not target an example using unavailable future information during decoding; offline training may use the full corpus, while the predictor's inputs remain causal.

An ensemble-aware surrogate may be more relevant than plain neural CE. In the illustrative probability mixture q=alpha p_NN+(1-alpha)p_other, neural log-loss sensitivity is alpha*p_NN/q. This suggests allocating gradient pressure where the neural model influences the final decision. The actual cmix/SSE system is not this simple mixture. Calibrate any surrogate against final-coder A/B tests and account for optimizer dynamics; a weighted neural gain that disappears in cmix is not a package improvement.

A tiny residual adapter is another bounded hypothesis: keep the baseline weights fixed, train a small quantized correction and pay for its code, duplicated parameters and inference. It may contain drift during a pilot, but its storage does not become free merely because training uses LoRA. A merged LoRA update changes the full quantized weight container; an unmerged adapter increases CPU work. Evaluate both representations honestly before retaining either.

**Final-coder validation and decision rules.**

Use same-stream paired differences over a fixed strata manifest. Initially screen with the validated GPU probability path, but check its fidelity for each new quantization configuration. Full-corpus mean neural loss is informative, while actual final-coder payload and packed weight bytes select the candidate. Keep cold-region and warmed/full-stream evaluations separate.

For checkpoint i, compute gain = (baseline_payload - candidate_payload) - 2*(candidate_weight_bytes - baseline_weight_bytes) - other_package_delta. For samples, report their actual byte differences and stratum sizes; extrapolation is labelled as such. Variation across pieces describes sample heterogeneity, not randomness of the fixed enwik9 result. Prefer broad/full-stream neural screening followed by fewer full coder validations over repeatedly optimizing two tiny slices.

If transformer weights change, the downstream mixer learning trajectory can change. Reusing a warmed mixer state generated under different neural outputs is not a complete compression comparison. Either replay from a common valid initialization or use truly matched snapshots at a shared prefix before any model switch, with the switch rule/package cost explicitly represented. The production compressor must use its actual intended model from the intended start.

A survivor needs a complete compression/decompression in separate clean processes, original-file hash agreement, exact comp9+archive9 ledger, peak RSS and single-core runtime calibration. Keep CPU validation capacity separately from GPU training; a idle GPU is an expensive way to buy a long serial decoder run. Qualifying runtime and memory must come from measurements, not the GPU pilot.

Do not spend beyond $70 merely because a learning curve is still decreasing. An extension request should contain the best measured net package gain, the last several checkpoint slopes, remaining uncertainty, exact additional compute cost and a concrete test that can falsify the candidate. A global optimum cannot be certified by a finite architecture/transform search; operationally, maintain a reproducible Pareto frontier over archive bytes, duplicated model bytes, CPU time and memory.

**Expected outcome.** This plan can test whether a faithful, representative MDL continuation improves the current system within a modest budget. It can also reject that approach cheaply. Existing evidence does not justify a 20% prediction. Strong structural experts, the better existing compressor core and exact package engineering should progress concurrently, while this plan supplies a disciplined test of the retraining lever.

**5October native screens refine the pilot.** Coarse no-SGD zeroing of the
original uniform-Q4 BF16 checkpoint saves221742/435552/1690680 bytes over two
weight copies, but adds130–185/288–442/1491–3243 final likelihood bytes on
matched32K A/B prefixes. Every arm fails its initial break-even gate. A29.7%
smaller stored model is not improved prediction. Use these as negative controls,
not as a starting winner or evidence that rate-aware fine-tuning cannot work.
An activation/Fisher-weighted quantizer must address sensitivity heterogeneity;
a cheap count of small coefficients does not. The final coder remains decisive.

The actual lexth11c C3 checkpoint survives (2978039bytes), with nonuniform
codebooks, 8-bit embedding/prior/output tables and dynamic activation scales.
Its wrapper options map to **QMAT_CODEBOOK=1,QMAT_WMAX=21,QMAT_SMALL_W8=1,
TF_ACTQ_DYN=1,TF_AVX512=1** in native C++ compilation. Using TF_CODEBOOK or
TF_SMALL_W8 directly as C++ macros is incorrect and was caught by the native
quantization-range check before coding. Pin the actual macro translation as
well as the public option names. Original uniform-Q4 pruning must not be copied
to nonuniform codebook indices: index magnitude is not weight magnitude, and
even the index representing zero must be read from the actual codebook.

The exact C5 container grows this C3 model by940bytes/copy; retain its existing
container for the stronger baseline. Frozen sparse article-topic profiles also
lose after transmitted selector costs on A/B/C/D. These tests direct the next
pilot toward trained lexical/spelling and structured conditional modeling,
after data/export/continuation controls, rather than another unigram cache.
The priced latent formulation is research_round7_article_latent_plan.md; its
current sparse-profile test failed and provides no justification for paid
latent-model training by itself.
# Additional pilot readiness evidence,5October

The archive contains the original six-million-parameter training/export
recipes and the prior-aware T4 FP32/SDPA harness. Exact source contracts are
preserved in `research_round7_training_readiness_source_audit.json` and
`research_round7_runtime_readiness.json`. The8M/10M state dictionaries load
as raw tensors, but their complete evaluation configurations have not yet
been validated; inferable shapes alone do not establish RoPE, head grouping,
softcaps, reset or activation contracts.

The new Kaggle runtime is Python3.12.13, Torch2.10.0+cu128, Triton3.6.0,
with T4 sm75 and no native BF16 support. Source pyproject declares Python3.11
and Torch2.12. Pinned FLA0.5.1/jaxtyping0.3.11 wheels are available and small,
but FLA also requires fla-core0.5.1 and typing requires wadler-lindig. An
isolated minimal runtime probe should test actual compatibility and native
parity before upgrades, long model evaluation or any$4 paid pilot. Keep
float32 math and checkpoint BF16 scale rounding explicit. A subsequent isolated
fla-core0.5.1/jaxtyping0.3.11/wadler-lindig0.1.3 installation imports successfully
without changing global Torch. Strict structural loads pass for6M12x192,
8M16x192 and10M12x256; unrecorded larger-model settings still need validation.
The queued no-SGD pilot regenerates true native PPMD priors and original/lexical
probabilities on a65536-symbol A prefix, then gates GPU comparisons on native
control agreement. No larger-model logits or training result has yet occurred.

The exact word-head design is further constrained in
`research_round7_word_head_precision_plan.md`. Compare a WRT-prefix-tree head
with an exact low-rank global head under the same useful-token exposure and
packed rate budget. A full65536-by44515 logit matrix alone is approximately
11.67GB in float32; use exact vocabulary tiling with recomputed backward
rather than unpriced sampled normalization. Benchmark complete CPU prediction
including mass aggregation and fallback, not only GPU or matrix throughput.
These architecture pilots compete for the existing allowance; they do not
increase the$70 ceiling.

New final-coder diagnostics on the actual lexical checkpoint attribute
36.845–43.237% of four cold2M slices' bits to known-in-slice words first in
the current article. These sampled residual budgets support prioritizing
article/syntax-conditioned lexical modeling. They do not prove an achievable
gain. A mechanism restricted to that category would need approximately
49.5–58.1% recovery if the same shares held throughout the payload and fixed
components stayed unchanged to meet the21.42% payload target. Do not spend
the$36 winning-branch budget on a tiny unigram-cache improvement.
