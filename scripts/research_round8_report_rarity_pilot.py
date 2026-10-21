
# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

import collections,json
from pathlib import Path
R=project_root(__file__);m=json.loads((project_path('research_round8_rarity_residual_pilot_results.json', base=R)).read_text());assert m['status']=='COMPLETE_PARTIAL_DICTIONARY_MASK_RESIDUAL_TRAINING'
groups=collections.defaultdict(list)
for row in m['priced_confirmation']:groups[row['arm']].append(row)
table='\n'.join(f"| {name} | {sum(v['CD_gain_vs_original_bytes'] for v in rows)/len(rows):.6f} | {sum(v['CD_gain_vs_wide_bytes'] for v in rows)/len(rows):.6f} | {min(v['CD_gain_vs_wide_bytes'] for v in rows):.6f} to {max(v['CD_gain_vs_wide_bytes'] for v in rows):.6f} |" for name,rows in groups.items())
times=collections.defaultdict(float)
for row in m['rungs']:times[(row['arm'],row['seed'])]=max(times[(row['arm'],row['seed'])],row['training_seconds'])
text=f'''# A96 partial masking experiment: results and stronger follow-up

6 October 2026. **Completed on the free Kaggle T4, without original transformer
updates.** Ten policies, two seeds, three successive screening rungs produced
36 saved model/optimizer checkpoints. Execution took 56.79 seconds including
data loading and evaluation; cumulative synchronized training took
{sum(times.values()):.3f} seconds. The 161-parameter residual used 533,495,808 bytes
peak allocated device memory. These are timings of this small experiment,
not a throughput estimate for the original transformer or a 5090.

The original predictor supplies the offset and eight pre-target source features.
Every input is retained. Complete dictionary-code spans receive rare-loss
weights 0, 0.25 or 0.5 at corpus count cutoffs 107, 1392 and 8372. Unweighted
loss is the control. Known 44,515 dictionary codes and their proper prefixes
were checked. Literal/OOV, case, escape, layout and unaligned slice prefixes
remain in the loss. **This is not the full-word mask requested for all rare
spellings, and it does not measure gradients inside the original transformer.**
Native XML/tag dictionary atoms can also receive semantic-text frequency
labels in this pilot. The full experiment must distinguish metadata and text
spans; the census deliberately excludes XML metadata.

Training uses A/B first 384 KiB per slice; development uses their final 128 KiB.
Every arm reaches 128 steps; five policies reach 384, and unweighted plus the
two best masked policies reach 1152. Each policy uses both seeds. The finalist
list was frozen before this fit's C/D scoring. C/D were used in earlier
unrelated diagnostics, so they are fit-held-out data rather than globally
untouched confirmation. All coded bits participate in evaluation.

## Measured outcome

The table gives two-seed means over C/D, totaling 1 MiB per seed. These are
FP64-reference Q16 likelihood savings, **not actual candidate archive sizes**.

| Policy at 1152 steps | Gain vs original, bytes | Incremental gain vs wider residual, bytes | Seed range of incremental gain, bytes |
|---|---:|---:|---:|
{table}

Masking did not consistently beat the unweighted control. Half-weighting at
the mild cutoff was about 0.327 byte worse on the two-seed mean; zero-weighting
was about 1.690 bytes worse. One zero-mask seed also worsened one independent
slice relative to the wider residual. This small result gives no basis for
declaring masking generally ineffective or selecting a different threshold
after looking at C/D.

Development gains relative to the wider residual were negative for every arm.
For unweighted training, the two-seed development mean moved from -0.573 byte
at 128 steps to -3.716 bytes at 1152. Longer continuation did not repair that
development behavior in this pilot. Early curves can therefore inform spending,
but they do not settle a larger model or a changed architecture.

The residual requires 644 raw FP32 parameter bytes per copy, 1288 for two
copies, before inference code and the wider offset's own package costs. Its
**incremental** improvement is only about 9–12 bytes over the wider law on C/D.
It fails even a parameter-only amortization check on these cold slices.
Neither the earlier wider-law savings nor its costs may be counted twice.
No residual native integration is authorized by this pilot's advancement gate.
Full warm amortization is unmeasured; linear full-file extrapolation is invalid.

## Gradient evidence and its limits

At initialization, a fixed 32768-bit batch at cutoff 1392 contained 32232
common/remaining and 536 masked dictionary targets. The class-mean gradient
cosine was **-0.683385**. At the unweighted final checkpoint it was -0.174743.
Thus conflicting local directions exist in this residual. They neither prove
that rare words harm the original transformer nor establish that masking helps
the total archive. Other cutoffs' rare sample counts can be very small: the
cutoff-107 diagnostic had only eight rare targets in that batch.

For clarity, the worker reports class-conditional mean gradients. Let their
values be bar_g_C and bar_g_R, with rare fraction r. Contributions to an ordinary
batch-mean objective are g_C=(1-r)bar_g_C and g_R=r bar_g_R. Cosine signs are
unchanged, but their update magnitudes must include those fractions. For a
small SGD-like update using g_C+lambda*g_R,

    Delta L_C = -eta [||g_C||^2 + lambda g_C^T g_R] + O(eta^2).

Adam's actual preconditioner, curvature, sampling and normalization differ
from this simplified diagnostic. Zero-mask arms sample their active pools:
the runs match nonzero targets, while common-target exposure differs. That
confound is recorded and needs a second matched-common-exposure control.

## Stronger descendants and discriminating implementation

1. Align literal spellings and native dictionary expansions to complete word
   occurrences, preserving case/control/layout spans and arbitrary side/tail
   bytes. Reconcile each aligned occurrence with the original-text census.
   Current dictionary masks cover only 0.35%/0.54% of A/B bits at cutoff 107,
   versus 8.52%/17.56% at cutoff 8372. Neither is the census's lexical retained
   fraction. Run article-local policies separately; their labels inspect future
   article counts and may be used for training, not free decoder gating.
2. Test the original shared backbone after zero-update native export parity.
   Compare ordinary loss, soft weighting, frozen-backbone specialists and
   separate heads at matched capacity, common exposure and all-target score.
   Measure class gradients on multiple independently sampled article blocks,
   per layer and under the optimizer's metric, instead of relying on this batch.
3. Use a normalized specialist law, with paid class mass and rare/native fallback,
   rather than dropping outcomes. For common/rare disjoint word supports,
   q(w|h)=pi(h)q_C(w|h) or (1-pi(h))q_R(w|h). A code-prefix probability sums
   this word mass over compatible completions; include literal/control mass.
   The unknown current word cannot pick its own cheaper expert for free.
4. Test gradient projection only when interference repeats across blocks. With
   positive definite metric M, define inner(a,b)=a^T M^-1 b and

       g_R' = g_R - min(0, inner(g_R,g_C))/inner(g_C,g_C) * g_C.

   This removes the rare direction's first-order adverse component for common
   loss in that metric. It does not guarantee lower total loss; compare against
   unprojected, class-weight and independent-head controls, including rare bits.
5. Follow a mask/soft-weight warm phase with ordinary all-target calibration,
   as proposed in the attachment. Use a registered continuation budget and
   freeze thresholds/checkpoints before another independent evaluation. No
   stopping decision should depend only on the common-word score.

## Engineering and preservation

All 72 inference-parameter and optimizer-resume files passed per-file SHA and
ZIP CRC checks. They are in research_round8_native_evidence/rarity_residual_models
and the immutable research_round8_rarity_residual_checkpoints.zip, SHA
9c5d77fac64d80dc98615f843fd6dcaaeedf177d97e309c7cddddc9d71593954.
The executed worker/protocol and 36-rung result manifest are preserved.
An independent native probability roundtrip passed all 65535 positive Q16
integers; the zero residual exactly matches the wider reference law. Future
feature/target changes preserve the tested prediction prefix.

GPU FP32 and saved-parameter FP64 inference differed at two integer CDF events
out of 32768 in the comparison, with maximum logit difference 9.45e-7. A future
native integration must implement the declared reference law and verify exact
CDF/decoder identity, rather than assuming GPU parity. No model/data deletion
or paid spend occurred. All 96 current families remain open.
'''
(project_path('research_round8_rarity_residual_pilot_report.md', base=R)).write_text(text,encoding='utf-8')
print(json.dumps({'status':'REPORT_UPDATED','training_seconds':sum(times.values()),'rungs':len(m['rungs']),'all_96_open':True}))
