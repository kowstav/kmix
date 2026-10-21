<!-- historical-authority-notice -->
> Historical round snapshot. All status blocks and PIDs below are dated evidence. Current corrected conclusions and execution status are in [research_round10_report.md](research_round10_report.md).

# Round9 implementation, experiments and continuation report

Generated 2026-10-06T19:39:14.636692+00:00. Authorized Kaggle session355735431. Paid compute spent **$0**.

The earlier work did not complete thorough testing of all96 ideas. Some screens were proxies, and the selected-core import, exact literal/OOV labels and native export were unfinished. Those implementation gaps, rather than an impossibility result, explain the partial status. This round implements those missing dependencies and additional architecture combinations. It still does not establish best-possible descendants, equivalent LLM-scale research effort, an absolute optimum, a20% archive reduction or a new qualifying record.

The accompanying96-family ledger retains each idea's historical rigor, actual-versus-needed test, combination work, stronger descendant, prerequisites and remaining test. Architecture counts below count actual parameterized arms, not completed idea families.

## Measurement and mathematical contracts

For a binary event with native integer law p_t in[1,65535], the actual probability is p_t/65536. Score every observed bit, including hard/literal/OOV words: L=-sum_t log2(q_t(y_t)). The acceptance objective is **payload bytes plus every shipped model, executable, dictionary, side stream and duplicated asset**, subject to exact independent decoding and eligible CPU/RAM. A reduction in masked loss or common-word loss alone does not qualify.

Let ell_t=log(p_t/(65536-p_t)). The frozen wider source correction is delta_t=theta0+theta1*ell_t+theta2*f_t, with theta=(.0016181118716570748,-.007454085408717222,2.3818512619982752), and f_t=FP32(clip(logit(native_NN_t)-ell_t,-12,12)/12) gated by the previous completed byte's neural validity. Only current before-target sources and decoded history are inputs. The integer expert laws are rounded/clamped sigmoid(ell_t+a*delta_t), with a in{.5,1,1.5,2}, plus identity.

For the adaptive mixture q_t=sum_k w_tk p_tk, after observing y_t update v_tk=w_tk p_tk(y_t), then w_(t+1)k=(1-epsilon)*v_tk/sum_j v_tj+epsilon/K. Here K=5 and epsilon=1-2^(-1/262144). No future difficulty label selects an expert. With epsilon0, product_t q_t(y_t)=sum_k w_0k product_t p_tk(y_t); the independent replay checked this identity. Fixed share permits change of expert over time but adds regret; the finite8policy family is not a global optimum.

For word features, an event becomes available only after its delimiter's encoded bytes complete. Bag-letter statistics, first/last letters, fixed symbolic shape groups and constructor-run state are functions of already completed words. The combined residual is delta'_t=.5*tanh(H([native_sources, word_state, native_disagreement*word_state])). This tests algebra/placement sharing without giving the model a future word. The separate content-first/infill proposal requires a paid ordering/anchor stream or a deterministic decode schedule; this architecture does not implement that different factorization.

For masking, J_lambda=sum_i w_i CE_i/sum_i w_i. Word-frequency thresholds107,1392,8372 are supervision-only and include complete literal/OOV/case spans. They are not decoder inputs. The short/core_long masks change losses only. The later literal_split, known_literals and distributed_core branches test genuinely redacted inputs or a paid constants stream; these are distinct experiments. For mixed classes the necessary condition is N_C*Delta_H_C+N_R*Delta_H_R+8*Delta_package<0. Improved constructors cannot compensate for arbitrarily expensive rare words.

For projected gradients g_C,g_R, a Euclidean projected g'_R=g_R-min(g_C dot g_R,0)*g_C/||g_C||² obeys g_C dot g'_R>=0. The existing arm feeds this gradient through AdamW, so the actual momentum/preconditioned update has no such guaranteed common-loss inequality. A stronger controlled descendant must project the actual update in a frozen diagonal metric or use matched SGD controls. Non-smooth quantization and finite steps also limit any first-order claim.

## Actual implementations and exact procedures

**Causal sequence screen:** eight arms: MLP/GRU/causal attention/dilated TCN, widths32/64. Full bit loss, train A/B, develop C/D, freeze finalists before E/F. Batch16blocks of512bits; fixed64byte resets; AdamW lr.0003, weight decay.01; rungs128/384/1152 with8/4/2survivors. Nonzero-head future-prefix mutation and zero-head identity passed. TCN32's E/F incremental gain over the wider reference totals about-1.24B. Its roughly47KB compressed weight payload does not pay. This rejects those finite fitted arms, not all sequence models or this idea family. Sources: research_round9_sequence_worker.py and research_round9_sequence_v1_results.json.

**Native hidden/TTL screen:** ten arms MLP/GRU/learned four-decay TTL/fixed TTL/channel-permuted GRU, widths32/64. Inputs include all192native hidden channels after the previous byte, delayed byte surprise, previous byte embedding and current native sources. Batch16x128bytes, full bit loss; rungs128/384/1152 and10/4/2survivors. Decay targets1/8/64/512completed bytes, but block resets bound effective retention to128bytes. Fixed channel rotation is a relabeling control, not a semantic null. Best frozen finalists provide only fractions of a byte beyond the wider law; model bytes do not pay. Source: research_round9_hidden_sequence_worker_v2.py and its results.

**Adaptive no-retraining law:** eight posterior policies were evaluated on actual integer expert laws, selected only on A/B, then measured on fit-held-out C/D/E/F. Scaled5 H262144 saves an additional66.62/59.77/61.25/119.53B on those respective512KiB slices over the wider reference. These are likelihood results, not a full archive. New G65M and H375M offsets were frozen before observation; actual native coder integration and independent decode are in adaptive_native_v2. The completed G/H native archives save168B and172B, respectively:340B on1MiB, with exact independent decoding and core/Q16 identity. This is a cold-slice result before new package costs, not a full-corpus or record result.

**Numeric repair:** adaptive_native_v1 validation initially found190one-unit mismatches among4194304bit positions. Direct expert comparison found75expert differences caused by a reference-only weak-scalar float32 multiplication under NumPy. Explicit float64 restored the source-replay worker's coefficient law and made all expert integers match. Native binary, model, coefficients and policy were unchanged; the completed G encode was reused. Preserve adaptive_native_v1 and adaptive_strict_v1 failures and numeric_detail evidence. Do not characterize this as a new fitted improvement or delete failed evidence.

**Whole-word supervision:** independent annotated/native WRT decoders compare every decoded character and encoded-atom consumption. Full words are assembled across literal bytes, dictionary fragments, case controls and apostrophes; complete word-frequency labels map to their entire encoded span. The pilot has262138neural payload bytes after six outer header bytes, including18484literal/OOV encoded word bytes. The original native prior failure on an out-of-alphabet outer header is preserved; v2 explicitly removes only those six framing bytes. Priors are current actual205-way dense native probabilities, not sparsified approximations.

**Actual selected-core finetuning:** recovered original model code and packed lexical tensors; imported all199parameters,5897145total scalars, from the actual selected weight asset SHA948847d9... rather than an unrelated checkpoint. Architecture12layers,width192,d_mlp768, nineKDA/threewindow-attention blocks, learned15level codebook grid.25,8bit small tables, fixed native BF16 row scales and QKV scales. Quantized forward uses STE shadow parameters. Five policies at128steps, lr1e-5, AdamW wd0, grad clip1, matched sampled article-prefix states through4096tokens, final256target loss. Article-level20% development split; same262KiBprefix corpus. Every128step arm slightly worsened ordinary full loss from .5932896bits/symbol. Checkpoints are preserved locally.

**Longer masks/interference:** six arms, seeds6506/6507,128/384/1152rungs, matching training examples per seed. Arms: unweighted,107half,1392half,1392zero,8372half and actual shared-core gradient projection. First seed at1152: unweighted total.59204489, common.42922333, rare2.14548039;107half total.59273922/common.42506939/rare2.19243002;1392zero total.64397079/common.41583180/rare2.82058144. Zero rare loss helps common words but loses substantially overall. Results are diagnostic until native measurement and broader corpus replication. Read core_extension_v1 rather than launching duplicates.

**Native/GPU precision:** captured4096actual step records containing205FP32priors, initial embedding plus12block outputs and205FP32probabilities. Observation leaves the native probability stream unchanged. Integer-valued FP32 dot products eliminate fake-quant floating accumulation error; bounded partial sums below2^24 are required. Explicit FP64 quotient then FP32 cast restores native division rounding at quantizer thresholds. Initial embeddings improve from a.00434max error to below1e-6, but later layers still diverge. The completed fourth diagnostic used native8lane FMA RMS summation and fused recurrent KDA inference; it did not solve parity and worsened the first article. This backend is not declared bit-exact. Native model export and actual codec evaluation can still evaluate trained weights without substituting GPU scores.

**Native checkpoint export:** zero update must reproduce every native tensor byte, including unchanged configuration, BF16scale/codebook and RoPE data. Trained shadows are snapped to the original codebook or int8levels, preserved native scales and raw FP32constants. Pack with the existing container codec, unpack using the actual C++ reader, and assert the raw tensor SHA. V2 proved exact trained tensor import, native neural observations and independent PPMD-coded archive decoding for first-seed unweighted/107half/1392zero. Its archive comparison was initially mislabeled: historical --transformer-only still returns PPMD from Predictor::Predict. Consequently identical39756B archives are not a neural-compression result. core_native_codec_v3 repairs only that diagnostic probability route, independently decodes true neural archives and tests the same trained weights through the unchanged combined CM on A/B/E64KiB; its actual manifest controls current claims. Final combined CM and independent corpus gates remain required.

**Letter/glyph/constructor combinations:** word_events_v1 independently decodes/compares the canonical prefix through the final D window, emitting only complete words within six512KiB slices. word_features_v1 starts A/B fitting only once an E190M event proves A/B extraction passed103.16M. C/D/E/F scoring waits for the complete extraction PASS. Nine arms, two seeds6706/6707, same32width model and matched rungs128/384; best two per seed continue1152. Arms: native-source control, identity, bag+positions, glyph groups, constructor grammar, spelling+grammar, spelling×native-source interaction, all features, deterministic random-word-vector sharing control. Inputs contain no frequency/rare/body/next-word labels. First16slice bytes and crossing words are excluded. Fixed constructor labels are heuristics; they do not identify every true noun or grammar word. Symbolic glyph features do not test OCR or CNN. Native final-bit integration and model cost remain pending.

## Current job snapshot

| Job | Status | PID | Completed rungs/candidates |
|---|---|---:|---:|
| sequence | COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN | 1464 | 14 |
| hidden_TTL | COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN | 1680 | 16 |
| adaptive_replay | COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY | 1711 | 0 |
| whole_word_alignment | COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS | 1505 | 0 |
| core_short | COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING | 1718 | 10 |
| core_long | COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT | 2064 | 36 |
| native_adaptive | COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES | 2181 | 2 |
| core_export | COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON | 2314 | 3 |
| core_native_codec | COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS | 2539 | 0 |
| literal_split | COMPLETE_REVERSIBLE_LITERAL_INPUT_MASK_SPLIT_NATIVE_SCREEN | 2281 | 3 |
| known_literals | COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN | 2437 | 5 |
| known_side_verify | COMPLETE_INDEPENDENT_PAID_SIDE_HINT_RECONSTRUCTION_IDENTITY | 58 | 0 |
| word_softmax | COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN | 2297 | 14 |
| word_softmax_descendant | COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN | 2512 | 16 |
| word_warmstart | COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN | 2752 | 12 |
| title_memory | COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY | 2711 | 0 |
| core_pipeline_profile | WAITING_FOR_CORE_DISTRIBUTED_V2 | 2780 | 0 |
| distributed_core_data | COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS | 2511 | 0 |
| distributed_core | RUNNING | 2602 | 22 |
| word_events | COMPLETE_CAUSAL_WHOLE_WORD_EVENTS | 2192 | 0 |
| word_features | COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN | 2248 | 40 |
| native_layers | COMPLETE_NATIVE_CORE_LAYER_OBSERVATION | 1997 | 0 |
| GPU_layers_v2 | COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL | 2139 | 0 |
| GPU_layers_v3 | COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL | 2201 | 0 |
| GPU_layers_v4 | COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL | 2223 | 0 |
| core_selective | RUNNING | 2821 | 2 |
| word_cache | LOCAL_SNAPSHOT_PENDING |  | 0 |
| model_order | LOCAL_SNAPSHOT_PENDING |  | 0 |

This is a saved snapshot, not a live process claim. Inspect remote manifests and actual PID before reuse/launch. All workers write immutable rung checkpoints and manifests. root scratch is outside the20GB working quota but is not automatically carried to the next Kaggle session; locally preserved evidence and verified bundles are the recovery source.

## Remaining implementation queue and combined strategy

1. Finish current two-seed core, word-feature and exact native adaptive/export jobs. Preserve model, optimizer, RNG, source, config, binary and compact results with SHA manifests. Correct implementation failures with new version names; reuse completed costly traces/encodes.
2. Extend whole-word supervision and exact native priors to distributed article strata, reset-aware contexts and longer tokens; preserve a final untouched confirmation pool. The prefix pilot cannot settle corpus-scale masking or architecture potential.
3. Implement explicit input-redaction versus loss-only masking, common/rare output specialists and a normalized soft router with unmasked total-loss objective. The router must be predictable before the target; encoder-only rarity cannot choose its branch for free. A true constants stream must pay positions, literal bytes and metadata and reconstruct all original contexts.
4. Test the actual-update gradient projection or matched-SGD descendant; compare total/common/rare loss and actual native package. Continue representative unweighted training as its control. Test learned scales/codebooks only with compressed weight cost and native reader parity.
5. The actual44515way word output softmax/spelling composer is implemented in word_softmax_v1. Its fixed literal law and narrow gate performed poorly; word_softmax_v2 now tests learned literal law/gates/temperature and a byte-head control. Finish its recorded tests and exact native integration if gains pay. Then extend the model through the unchanged WRT tree, with exact fallback and integer normalization. Then combine constructor-run state, associative word graph, long prefix memory and native source disagreement. Generic byte residuals cannot stand in for these unimplemented architectures.
6. Develop content-first grammar infilling as its own reversible factorization. Store/order anchors and gap lengths first, then code constructors conditioned on decoded left/right anchors, with permutation/multiset/subset counts priced. Compare ordered templates and a null order-aware model; do not feed future content into a left-to-right decoder for free.
7. Build revision/title/schema copy/edit and symbolic numeric experts with arbitrary-tail fallback. Strong metadata/title descendants are still unimplemented this round; the96ledger names all their contracts and dependencies. Include field reordering/copy residual/side bytes rather than screening raw correlations alone.
8. Jointly ablate surviving laws under the final coder. Adding individual measured gains is invalid because the mixture/weights/context change their conditional benefit. Retrain/refit only on designated development data; price a single shared implementation and all duplicated assets.
9. Qualify finalists on warm full history, all587138826canonical bytes, actual self-contained archive/package, exact original1B SHA, CPU time and peak RAM on eligible hardware. The old C3 peak leaves only615424B under decimal10GB, so cold6GB memory is not sufficient evidence. Rebalance classical allocation and benchmark if new state exceeds that margin.

No paid rental begins merely because a GPU is faster. The $70 plan first requires a measured tokens/s and memory benchmark on a ready implementation. Use15–60minute architecture rungs and matched token budgets, then2–4hour confirmation candidates and longer final continuation only for survivors. A provisional12–24hours of shortlists plus8–16hours of finalists is not a price quote or an estimate for exhaustive96idea research. Reserve$10, impose a$60compute cap including storage/transfer, and allocate from an actual verified all-in hourly price. No such5090benchmark or rental has occurred. The final training plan depends on these native tests and cannot promise20%compression.

## Preservation, deletions and next-agent instructions

Eleven core_training_v2 checkpoint files were copied and SHA-verified in root scratch and the local workspace before their redundant working-disk paths were unlinked. About736MB of working space was recovered; no checkpoint content, original corpus or original selected model was deleted. The exact11source/destination/size/SHA entries are in research_round9_core_checkpoint_relocation_manifest.json. Do not repeat the earlier statement “no filesystem deletions”:11redundant paths were removed after preservation. No other project content was intentionally deleted in this round.

Correct complete native build dependencies are155files, ZIP1106710B, SHA7ae01f60e7f7e4813f1c14c5869af94349c755eff370cfb7b7a3434bbbba0eb3. The earlier archive omitted cpp_infer and is not enough to rebuild. Original training source and actual packed tensor expansion were recovered from the preserved source archive. Isolated pinned runtime packages live in /root/hp_round9/runtime_site_v1; no global torch replacement was made.

Use kaggle_research_client.mjs with the session credential supplied only through HP_KAGGLE_BASE; never persist the signed URL. Text put is not a binary uploader. Use the binary uploader with SHA/CRC validation for archives. Use small detached workers via the Jupyter kernel, not a50second blocking long experiment. Only the latest human-supplied session is authoritative.

Read research_round7_checkpoint.md first, then this report and research_round9_idea_program.json. Inspect RUNNING/FAILED manifests and reuse live jobs; do not replay source generators that overwrite prior status. All96families remain open. Managed Goal is usageLimited and was not resumed/replaced/mutated; automated follow-ups must honor that limit. The requested week ends11October2026.


## Later completed masking and word-architecture work

Actual input masking is no longer only a proposed or loss-only test. literal_split_v1 replaces complete rare encoded word spans by spaces, independently compresses/decodes the main stream with the final CM, and restores every original byte from a paid side stream. Cuts107/1392/8372 lose2106/4451/6814B on65536B. The side codec is zlib9 and is not asserted optimal.

known_literals_v1 is a stronger descendant: decode the rare bytes first, insert them into original context, and execute all native Predict/Perceive updates while skipping their arithmetic intervals. The all-unknown control reproduces the original archive exactly. Original-context hidden trajectories and independent decode match for all3cutoffs. Their net losses after side/container costs are1430/3125/4985B. Redacted-context1392 loses3985B. The already-trained1392zero common specialist reduces the raw-context main archive3770B to3616B, a154B local benefit, but its full split still loses2971B and its model adds85927B per copy. This demonstrates a finite specialist effect, not a successful split or a rejection of stronger constants-first laws. A native sequential side-loader and better side probability/order models remain open.

word_features_v1 completed18runs and40checkpoints. Every E/F finalist has negative joint incremental gain against the wider law; the best grammar seed totals about-0.162B. Learned symbolic letter/glyph/constructor features in these small residual heads therefore do not pay their models. This neither tests a raster OCR model nor exhausts long-memory placement or content-first infilling.

word_softmax_v1 completed8runs/14checkpoints with exact44515way normalized output laws and prefix-tree marginalization. Surviving random-basis heads lose4.264B and5.772B jointly on E/F relative to the stronger causal adaptive law. A stronger descendant, word_softmax_v2, removes its fixed-uniform-literal limitation, learns literal byte probabilities, dictionary/literal mixing and word scale, widens the context gate from.1 to.5, and includes a byte-head control. Ten runs, seeds6906/6907, rungs128/384/1152; select best2/seed then1/seed using C/D, confirm E/F only after selection. These are still finite cold diagnostic models and require native integration if promising.

distributed_core_data_v1 prepared six512KiB fragments from canonical WRT offsets A/B/C/D/E/F. Whole-word body labels include dictionary, literal/OOV and case spans. Raw and genuinely redacted1392 inputs get separate native PPMD prior extraction; an unmodified-prefix neutral control matches existing tokens and priors exactly. Training/evaluation excludes the initial partial article and begins at observed native reset boundaries. A/B train, C/D develop, E/F are held out from core fitting but have been viewed by other families; no untouched discovery claim. These are cold classical priors, not full warm-history training data.

core_distributed_v1 failed during setup because importing the original core replaced its distributed-data manifest variable. No training ran in that failed worker; the failure is preserved. The repaired core_distributed_v2 reuses all prepared data and imports all199parameters/5897145scalars. Its12runs compare raw unweighted, raw1392half, raw1392zero, redacted1392full, redacted1392common and projected actual Adam update, seeds7006/7007, checkpoints128/384. Same sampled article prefixes/targets per seed. Priors are regenerated on redacted inputs, so the model does not receive original-stream context through a stale prior. Redaction still needs the paid side stream for full original reconstruction.

For the corrected gradient descendant, let d=theta_old-theta_Adam and g_C be the current common-loss shadow gradient. Project d*=d-min(g_C dot d,0)g_C/||g_C||² and set theta_new=theta_old-d*. This addresses the earlier mistake of projecting gradients before Adam's momentum/preconditioner. It satisfies the first-order surrogate halfspace in exact arithmetic; shadow float32 rounding, finite step, quantizer discontinuities and native likelihood still require measurement. The actual before/after dot products are recorded. A theorem about a surrogate is not an archive guarantee.

All96families still retain explicit open descendants in the ledger. Completed parameterized runs and shared dependencies must never be counted as96exhausted ideas. Metadata/title/copy/edit, genuine glyph/OCR, paid latent schedules, full constructor-set/order models, long-memory eviction and joint native integration still have missing implementations.


## Additional descendants, corrections and training plan

The corrected diagnostic neural archives are teacher20626B, unweighted20264B,
107half20289B,1392zero22001B on262138B. Gains362/337/-1375B concern that exposed
prefix and exclude model/package growth. Final combined CM and B/E are separate.

The learned-literal/gate word_softmax_v2 completed10runs/16checkpoints; its two
E/F finalists lose5.132B and3.312B relative to the adaptive reference. The stronger
word_warmstart_v1 directly optimizes dictionary-class CE before full-bit training,
addressing gradient starvation when the native/expert gate almost closes. Six
spelling/independent/random runs use seeds7106/7107, word batch256 and bit batch128,
128/384rungs in each phase. Exact event/code matches prevent joined/OOV labels from
being treated as dictionary roots. Every input remains before-target; supervision
labels are never inputs. Evaluate and select by full bit cost, not word CE alone.

title_memory_v1 completed six no-retraining persistent-title copy laws. Titles are
collected only after decoded title-tag bytes, bounded4096B, retained to next title
or page-end. Dictionary-code substring histograms/suffix lengths1/2/4/8/longest
produce normalized byte/bit laws with positive support. One bounded mixture scalar
per law is fit convexly on A/B; identity wins C/D and stays identity E/F. This is
an actual persistent copy law, not a hidden-similarity proxy, but it does not exhaust
case-invariant title entities, contextual placement gates or linked-article memory.

known_literals_side_verify_v2 independently parses each counted side container and
derives all mask/value bytes without the original data or word census. Those files
are byte-identical to the files used by the executed independent native decodes,
and the decoded/restored original hash matches for all5cases. This closes the hint
provenance gap through compositional identity; eligible native wrapper pricing still
requires work. No expensive identical decode was rerun just to repeat that evidence.

core_pipeline_profile_v1 is queued after GPU0 training: record missing zero-update
E/F raw/redacted controls, then test per-document RoPE/KDA/convolution/attention
isolation and packed batches of1/4/8, caps256/1024, Adam lr0, foreach false/true.
Separate GPU outputs and first-document future noninterference must pass before
timing that packed variant. This is a real original-core pipeline benchmark, not
a claim of5090performance or full-corpus/native parity.

Read **research_round9_training_and_5090_plan.md** for detailed short-rung training,
mask/side specialists, word warm-start, actual-update projection, rate-aware QAT,
joint factorial tests, measured timing and$70allocation. It distinguishes a
shortlist allowance from exhaustive96idea cost. Actual marketplace quote and
ready-workload throughput are prerequisites to paid execution; spending remains$0.
The detailed Hutter rule currently uses70000/T hours rather than the FAQ's older
100hour wording. Use its exact package formulas and self-contained CPU/RAM/HDD
contracts: https://hutter1.net/prize/hrules.htm . The official search index lists
July2026total100424672B; the local95914051B competitor remains a distinct stricter
competitive target whose current award status was not independently verified.

Compact evidence bundle1 is locally verified:49361182B,379entries, SHA
f6ecb95b5d2ebc22ee8b5ae7b67e7758d406a4416082dc3dabb6b48db9701f33.
ZIP CRC and every entry's SHA passed. It predates the later title/warm-start/profile
and trained-core archives; those need a second preservation snapshot. Current
linked checkpoint preservation is reported below; source/helper paths are retained.


## Later native measurements and engineered descendants

The final combined-CM comparison is complete. Every entry below is an actually
written native archive with independent decoding and identical encoder/decoder
neural probability trajectories. Values are payload-byte savings versus the same
native teacher on the same 64KiB slice, before model/package cost.

| Model | A | B | E | Initially sorted packed-model growth per copy |
|---|---:|---:|---:|---:|
| Unweighted finetune | 105 | 14 | 20 | 85,922B |
| Cut107, half rare loss | 105 | 18 | 19 | 85,940B |
| Cut1392, zero rare loss | -106 | -118 | -139 | 85,927B |

A overlaps core training. B/E were held out from those fits but seen elsewhere.
Cold 64KiB tests do not justify full-corpus extrapolation. Native decode CPU and
RSS are recorded per candidate in research_round9_core_native_codec_v3_results.json.
The initial model prices use sorted observer tensor order. A separate packing job
recovers the original container order to distinguish repacking overhead from
changed-weight cost; native tensor identity is mandatory before archive reuse.

Direct dictionary-word warm-start followed by full-bit mixture training is complete.
The frozen random-basis seed7106 loses 9.63545B on E and 15.14074B on F, total
24.77620B relative to the stronger adaptive source reference. Spelling seed7107
loses 9.35914B and 15.53255B, total 24.89170B. Better dictionary-only CE did not
produce better full-bit compression. That is a finite negative experiment, not
a rejection of all word models or proof of an optimum.

The unchanged selected-core E/F raw baseline is 1.5019641266 bits/symbol for
190,084 targets: common/unlabelled 1.3821668982, rare 2.3632757110. Compare each
distributed finetune against a zero-update baseline with identical input mode,
targets, resets and contexts. Redacted-symbol losses need their paid literal side
stream before they can be interpreted as original-text compression.

research_round9_core_selective_worker.py tests six arms times seeds7006/7007,
rungs128/384, on the same A/B sampled article prefixes as distributed_core_v2:
unembedding-only (39,360 scalars), recurrent-gates-only (449,307), last-block-only
at learning rate1e-4; all-core3e-5 paired control; the same control plus .01
code-cell penalty; and half rare loss plus that penalty. Every frozen parameter
must remain byte-identical at each rung. For each quantized tensor with minimum
native code-level spacing s and initial w0, the penalty is

    R = mean_tensors mean_elements max(|w-w0|/s - .49, 0)^2.
    J = weighted_full_cross_entropy + .01 R.

This smooth penalty discourages code-index flips. It is not an actual entropy or
compressed-size estimator. Evaluate full C/D and E/F original-symbol losses,
export promising candidates through the native reader, then price packed model
and actual combined-CM archives. Native/GPU arithmetic parity remains unresolved.

research_round9_word_cache.cpp and its worker implement eight no-retraining
completed-word donor probability laws. Keep the last256 completed words, their
actually observed encoded spelling (1..64B), letter bags, and preceding constructor
class. A donor becomes available only after its delimiter completes. Query the
longest matching proper encoded-word prefix among the last8 decoded bytes.
Next-byte donor counts plus .001 Dirichlet smoothing over256 bytes are normalized
within the already known current-bit prefix, then quantized to Q16.

The eight laws are counts, recency8/64/256 words, preceding constructor class,
letter-bag cosine to the fourth power, first-letter equality, and a joint
constructor/letter-bag/last-letter law. Fit one scalar convex mixture coefficient
per law on A/B, select on C/D with identity available, freeze before E/F.
Nonzero future-prefix mutation and exact zero-mixture identity are required.
These are direct output laws rather than hidden-feature proxies. Production
semantic parsing, native independent decoding, model/code/memory pricing and
full warm evaluation remain required. They do not assert an intrinsic semantic
connection merely because two words share letters.


## Snapshot of implemented jobs

| Job | Saved status | PID | Recorded checkpoints |
|---|---|---:|---:|
| sequence | COMPLETE_CAUSAL_SEQUENCE_RESIDUAL_ARCHITECTURE_SCREEN | 1464 | 14 |
| hidden_TTL | COMPLETE_NATIVE_HIDDEN_SEQUENCE_TTL_SCREEN | 1680 | 16 |
| adaptive_replay | COMPLETE_CAUSAL_SOURCE_ADAPTIVE_REPLAY | 1711 | 0 |
| whole_word_alignment | COMPLETE_FULL_WORD_ALIGNMENT_AND_CURRENT_NATIVE_PRIORS | 1505 | 0 |
| core_short | COMPLETE_ACTUAL_SELECTED_CORE_DIAGNOSTIC_MASK_FINETUNING | 1718 | 10 |
| core_long | COMPLETE_TWO_SEED_CORE_MASK_AND_GRADIENT_PROJECTION_PILOT | 2064 | 36 |
| native_adaptive | COMPLETE_FRESH_ADAPTIVE_NATIVE_COLD_ARCHIVES | 2181 | 0 |
| core_export | COMPLETE_EXACT_CORE_EXPORT_AND_NATIVE_NEURAL_CODEC_COMPARISON | 2314 | 0 |
| core_native_codec | COMPLETE_CORRECTED_NEURAL_AND_COMBINED_CM_TRAINED_MODEL_CODECS | 2539 | 0 |
| literal_split | COMPLETE_REVERSIBLE_LITERAL_INPUT_MASK_SPLIT_NATIVE_SCREEN | 2281 | 0 |
| known_literals | COMPLETE_PRICED_KNOWN_LITERAL_BYPASS_AND_COMMON_SPECIALIST_NATIVE_SCREEN | 2437 | 0 |
| known_side_verify | COMPLETE_INDEPENDENT_PAID_SIDE_HINT_RECONSTRUCTION_IDENTITY | 58 | 0 |
| word_softmax | COMPLETE_EXACT_WORD_SOFTMAX_AND_SPELLING_COMPOSER_SCREEN | 2297 | 14 |
| word_softmax_descendant | COMPLETE_LEARNED_LITERAL_WORD_COMPOSER_DESCENDANT_SCREEN | 2512 | 16 |
| word_warmstart | COMPLETE_DIRECT_WORD_WARMSTART_THEN_FULL_BIT_MIXTURE_SCREEN | 2752 | 24 |
| title_memory | COMPLETE_CAUSAL_PERSISTENT_TITLE_COPY_REPLAY | 2711 | 0 |
| core_pipeline_profile | WAITING_FOR_CORE_DISTRIBUTED_V2 | 2780 | 0 |
| distributed_core_data | COMPLETE_DISTRIBUTED_RAW_AND_REDACTED_NATIVE_CORE_INPUTS | 2511 | 0 |
| distributed_core | RUNNING | 2602 | 22 |
| word_events | COMPLETE_CAUSAL_WHOLE_WORD_EVENTS | 2192 | 0 |
| word_features | COMPLETE_CAUSAL_WORD_SPELLING_GLYPH_GRAMMAR_COMBINATION_SCREEN | 2248 | 40 |
| native_layers | COMPLETE_NATIVE_CORE_LAYER_OBSERVATION | 1997 | 0 |
| GPU_layers_v2 | COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL | 2139 | 0 |
| GPU_layers_v3 | COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL | 2201 | 0 |
| GPU_layers_v4 | COMPLETE_NATIVE_GPU_LAYER_DIFFERENTIAL | 2223 | 0 |
| core_selective | RUNNING | 2821 | 2 |
| word_cache | AWAITING_LOCAL_RESULT |  | 0 |
| model_order | AWAITING_LOCAL_RESULT |  | 0 |

Verified local large-model preservation: 110 files, 3109004982.0 bytes. This completed download precedes later word-softmax/distributed checkpoints, which require additional preservation. Source paths, failed workers and manifests remain reproducible evidence.
