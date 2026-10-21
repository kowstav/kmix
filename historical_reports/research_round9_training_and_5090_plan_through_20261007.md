# Training, architecture search and $70 execution plan

6 October 2026 UTC / 7 October India time. This is a conditional research plan,
not a compression forecast. Paid spending is $0. No 5090 has been rented.
The current completed/active Kaggle evidence is in research_round9_report.md;
research_round9_all96_execution_ledger.md records every still-open family.

The principal earlier gaps were missing actual selected-core import, literal/OOV
alignment, deployment export and architectures behind the proxy tests. These are
implementation gaps, not evidence that the proposed families cannot work. Round9
has implemented several of them. It cannot certify absolute potential, exhaustive
96-family testing, or a guaranteed 20% reduction.

## What is actually established

The native selected model has 5,897,145 trainable scalars in 199 parameters, a
205-symbol alphabet, 12 layers of width192, nine KDA layers and three attention
layers. The imported codebooks, BF16 row scales, activation laws and actual packed
model are preserved. Both seeds of six early-prefix policies reached1152steps.
These were ordinary/mild/severe loss masks and a projected-gradient control.

Full literal/OOV/case word-span loss masking is implemented. Actual input redaction
with a paid side stream is implemented and independently decoded. Original-context
known-literal insertion with arithmetic bypass is implemented: it keeps all native
predictor updates and avoids coding side-supplied symbols twice. A trained common
specialist reduces one bypass main stream by154B, but that split still loses2971B
on65536B before its additional model/package costs. Current side schemes are not
competitive; that does not exhaust more economical side laws or infilling models.

Native tensor export and independent reader/decode checks passed. The historical
`--transformer-only` path still coded with PPMD, so the first equal-size diagnostic
archives were mislabeled. The repaired diagnostic codes the observed neural law:
teacher20626B, ordinary-trained20264B,107half20289B,1392zero22001B on262138B.
Those savings/losses include training-prefix exposure and exclude shipped model
growth. The final combined-CM comparison is a separate running experiment.

Eight word-softmax runs and ten stronger learned-literal/gate descendants were
executed. Neither produced a positive E/F incremental gain over the causal adaptive
reference. Direct dictionary-word supervision followed by full-bit mixture training
is now running to address possible gradient starvation in a nearly closed mixture
gate. Spelling, independent-word embeddings and a random basis have matched schedules.

Distributed native inputs cover six512KiB canonical fragments. Raw and redacted1392
streams each get regenerated native PPMD priors; neutral priors/tokens match exactly.
Six original-core policies times two seeds are running384step pilots with checkpoints
at128/384. They include actual input masking and projection of Adam's actual proposed
update, with a matched unweighted control. These datasets are broader diagnostics,
not full warm corpus coverage. E/F have been seen by other research branches.

## The objective and why common/rare masks must be priced

For a decoder-reachable next-bit law q, measure

    L_bits(theta) = -sum_t log2(q_theta(y_t | decoded_prefix, paid_side)).
    S = payload + all counted executables/models/dictionaries/side streams/options.

Never substitute a masked objective for S. If C and R partition observed targets,
an improvement requires

    N_C * DeltaH_C + N_R * DeltaH_R + 8 * DeltaPackage < 0.

For a two-pass factorization X <-> (Z,Y), use

    L(X) = L(Z) + L(Y | Z) + L(transform and reconstruction code).

Right anchors may help the second pass because they have been decoded from Z.
Their locations, lengths, literal values, ordering and dictionary must all be paid.
An unordered constructor multiset is insufficient: order/permutation/subset choice
has a codelength unless the decoder can reproduce it deterministically.

If raw and rare specialists are both shipped, their benefit must exceed both models,
the before-target router and runtime. A free decoder-side rarity label is invalid.
Our side stream legitimately supplies such labels, but its cost currently outweighs
the common-word benefit. A full-loss soft router is the alternative to a paid hard
split. A frequency mask can still be useful as curriculum or gradient allocation
without becoming the deployed loss/codec.

The trained compact models currently grow by about85922–85940B per copy relative to
the original2978039B model. If two copies are counted, a model adding85927B needs at
least171854B payload savings. Across587138826encoded bytes that alone requires a
mean saving above0.0023416bits/encoded byte. This is a break-even calculation, not
an extrapolation from our small slices. Price actual final containers; even the
zero-update repack adds30032B per copy despite identical native tensors.

## Next training stages and exact controls

1. Finish the active Kaggle jobs and preserve their checkpoint/manifests. Evaluate
   actual combined-CM archives, not only neural loss. Obtain matched zero-update
   E/F scores before interpreting distributed training deltas. Keep the failed
   workers and measurement corrections in the report. Do not relaunch live jobs.

2. Prepare representative training data from complete article/reset pieces across
   the entire canonical stream, including metadata, redirects, tables, references,
   literal/OOV names and tails. Preserve the original1B SHA. Do not skip PPMD mass,
   reuse original-stream priors for redacted inputs, or reset classical state as if
   it were warm history. Use a sequential producer or document a cold-prior surrogate.
   Sampling probabilities and actual useful target counts must be recorded.

3. Keep an unweighted continuation from the same selected model as control. For
   loss weighting, compare lambda1,.5,.1,0 with thresholds107,1392,8372 only after
   confirming the current pilots; avoid expanding every parameter before native
   validation. Normalize masks consistently and report both weight sum and target
   count. Compare total/common/rare costs and context effects, not masked loss alone.

4. For genuine redaction, train with regenerated masked-stream priors, then export
   and test the complete side-plus-main archive against the unweighted control.
   Compare known-original-context and known-masked-context variants. A stronger side
   codec should separate gap lengths, span lengths and literal values, use actual
   ordered dictionary codes and exploit already decoded article-local repetition.
   Every component needs an independent decoder; side-code savings alone do not prove
   a total gain. Keep OOV/case/punctuation/terminal-word fallbacks exact.

5. Test the corrected gradient allocation. With common gradient g_C and Adam's
   proposed displacement d=theta_old-theta_proposed, use

       d* = d - min(g_C dot d,0) * g_C / ||g_C||^2.

   The running experiment records the actual before/after dot products. In exact
   shadow arithmetic this constrains the first-order common-loss change. Quantized
   native outputs, finite steps and float32 rounding still require measurement.
   Compare actual full-loss/native archives with the matched Adam control. Momentum
   history remains part of the algorithm; do not invoke a plain-gradient theorem
   for an unexamined optimizer update.

6. For word composers, warm-start exact44515class dictionary probabilities on verified
   first-code positions, then optimize full bit likelihood with literal fallback.
   Current supervision uses the hidden state before the first code byte and verifies
   the entire encoded word against its dictionary code plus case controls. It never
   supplies the target word to the input. Compare spelling, independent and random
   bases; calibrate against the native adaptive reference; jointly test placement
   state/memory only after the standalone conditional contribution is measured.

7. If word-law benefits survive, prune unused modules and regenerate fixed dictionary
   features. Test learned code trees/hierarchical or tiled normalized softmax against
   exact flat softmax before optimizing CPU kernels. A speed approximation must retain
   positive literal support and be rescored under its actual Q16 law. Add a
   before-target confidence gate only if its reduced CPU cost and compression pass
   together. Quantize learned arrays and measure their compressed codelength.

8. Add rate-aware QAT only after the ordinary continuation is a trustworthy control.
   Candidate objective: L_bits(theta)+beta*R(theta), where R estimates actual shipped
   code indices, sparse update positions and entropy-coded tensor sizes. Periodically
   export and measure the real container, because a smooth R surrogate is insufficient.
   Compare fixed native row scales/codebooks with learned scales/codebooks; sparsely
   changed code indices may be more economical than replacing every model tensor.
   Preserve native raw constants and procedural RoPE identity. Test shared model
   packaging only if the same resulting package satisfies both programs' contracts.

9. After shortlists, test combinations with factorial ablations: adaptive law; chosen
   trained core; chosen word/memory expert; shared router; each pair; the complete
   combination. Baseline source traces are not valid after changing the core/model
   adaptation. Rebuild exact sources and run the real final coder. Individual gains
   cannot be added. Retain a frozen fit/development/confirmation selection protocol.

10. Run the winning self-contained package on the full original corpus, including
    inverse preprocessing, original byte hash, CPU time and peak RAM/HDD. Current
    cold tests have not qualified a record. New cache/head state must fit the very
    small remaining RAM margin or trade against existing PPMD/classical allocations.

## Short experiments, meaningful exposure and engineering

6000steps is not required for every experiment. We already use128/384/1152rungs.
However, "384steps" is not a common unit of evidence: word pretraining uses256word
targets/step, bit heads use128byte contexts/step, and original-core pilots supervise
at most256last targets after a potentially4096token forward context. Record:

    U_i = steps_i * global_batch_i * useful_loss_targets_i,
    F_i = number of tokens actually processed in forward/backward contexts.

Different U/F, optimizer states and representation capacities need matched controls.
Train/test overlap is permitted by a fixed-dataset compression goal, but broad slices
are still needed to avoid choosing a branch based on one favorable local accident.
Repeatability, correct decoding and final total size remain the decisive evidence.

The actual early-prefix1152step T4 runs took249–462seconds per arm, including rung
evaluation, with about260000useful targets. These are measured6M-core pilot timings,
not full-corpus or5090 timings. The distributed first-seed384step arms have taken
roughly207–310seconds at the current snapshot; longer article contexts/evaluation
change cost. Faster GPU hardware alone does not resolve native arithmetic parity.

Before a paid run, benchmark the actual ready workload:100warm steps, synchronize,
then200timed steps. Report median/p90 times for loading, forward, backward, optimizer,
evaluation and export separately. Verify packed variable-length document resets and
RoPE positions against separate-document execution before batching. GPU-resident
priors, pinned staging, packed batches, fused/foreach optimizer updates and cached
quantized weights are optimizations to benchmark, not performance already claimed.
Avoid deliberately keeping devices busy with redundant work.

## 5090 hours and the $70 boundary

The RTX5090 has32GB memory; this is capacity information, not proof our particular
FLa/Torch/export path is compatible or fast. [NVIDIA specifications](https://www.nvidia.com/en-gb/geforce/graphics-cards/50-series/rtx-5090/)

Vast uses marketplace rates; GPU rental, storage and transfer can all contribute
to the bill. Stopping a GPU instance does not eliminate its storage charges.
Choose an actual offer and inspect its complete price before committing money.
[Vast pricing](https://vast.ai/pricing), [official billing documentation](https://github.com/vast-ai/docs/blob/main/guides/reference/billing.mdx)

For ready shortlisted architectures, a provisional allowance is:

| Stage | Aggregate GPU-hours | Work |
|---|---:|---|
| Compatibility/data/export and real throughput probe | 1–4 | One GPU, measured workload, CPU export/native gates |
| Focused architecture screen | 12–24 | 6–12 implemented candidates, two seeds, matched short token budgets |
| Confirmation | 8–16 | Two survivors, longer context/exposure, quantization/export ablations |
| Final continuation | Remainder only if justified | Broad corpus training of a measured survivor |

These are allocation ranges for a shortlist, not a measured requirement and not
exhaustive optimization of96ideas. Two GPUs for one hour cost two GPU-hours. If
r_i is useful targets/GPU-second, compute

    H = sum_i (seeds_i * U_i / r_i) / 3600 + H_setup + H_evaluation.

Reserve$10 and cap compute/storage/transfer at$60. With all-in hourly rate c and
one-off transfer/storage cost b, require c*H+b<=60. Example assumed rates, not quotes:
at c=$.50,$.75,$1.00 and b=$0 the maximum is120,80,60GPU-hours, respectively. Use
less once other costs are known. No automatic top-up, larger budget or rental is
authorized merely by this plan; the user requested a later shortlist before5090work.

## Prize qualification and next-agent handoff

Use the detailed rules rather than the FAQ's older100hour wording: the published
time bound is70000/T hours, with10GB RAM,100GB temporary HDD and no GPU in submitted
programs. Programs must be self-contained and exact; the alternative package size
formula can count separate decompressor assets more than once. Check the current
rules again at submission. [Detailed Hutter rules](https://hutter1.net/prize/hrules.htm)

The official search index currently lists100424672B for the July2026 award. The
95914051B competitor figure preserved in local research is a distinct competitive
target whose present recognition was not verified by the fetched official page;
do not silently call it the awarded record. Use an explicitly dated competitive
target and full package formula for every percentage claim. [Official prize page](https://prize.hutter1.net/)

Read research_round7_checkpoint.md, the round9 report, the96-family ledger and
per-job manifest before running anything. Live IDs and failure repairs are there.
Preserve completed models by SHA before session expiry; root scratch is ephemeral.
Original models/corpus remain preserved. Eleven redundant working checkpoint paths
were removed only after verified root/local preservation; the relocation manifest
documents each. No other project deletions were performed in this continuation.

Managed Goal remains usageLimited and has not been resumed or bypassed by automated
follow-ups. Human-authorized continuation work is recorded separately. The requested
research week ends11October2026; no absolute optimum or20% result is claimed.
