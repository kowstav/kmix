# A96: rarity thresholds, gradient allocation and specialist factorization

Registered6October2026 before the frequency census. This is a newly explicit
family, related to historicalA15,A83,A85 and attachmentS01/S02. The recovered
round1–7 ledger has95families; adding this proposal produces96current entries.
This does not establish that every historical idea was recovered or tested.

## Census to execute now

Read the preserved original enwik9.zip without extracting/deleting data.
Verify the original1,000,000,000byte member SHA256
159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.
Stream complete XML<page>records and parse their<text>with ElementTree, which
decodes the XML escape layer. Keep wikitext in its observed form. Define a
lexical token as the ASCII regex[A-Za-z]+(?:'[A-Za-z]+)*, casefolded. Numbers,
non-ASCII spellings, punctuation and XML metadata are excluded. This is a
diagnostic convention, not the native205byte model alphabet or an exhaustive
linguistic vocabulary. Exclude an incomplete terminal page and report its
length. Do not infer a full compression rate from these counts.

For each word report occurrence countf_w, complete-text token fractionf_w/N,
number of containing articlesdf_w, maximum within-article percentage and mean
within-article percentage among its containing articles. Preserve gzipTSV
with every observed word and the compact summary/source hashes. Analyze
corpus count cutoffsf_w<2,4,8,16,32,64,128,256,1024, corpus fractions<1e-6,
1e-5,1e-4, and local fractionsf_wa/N_a<.001,.005,.01,.02. Also compare
local count<2,4,8. Report removed occurrences and removed distinct types or
word/article pairs. The tokenizer's apostrophe rule and article exclusion
remain fixed regardless of outcomes. Full-future counts are offline training
labels; they are not free inference features.

## Controlled training ladder, not yet executed

R0 unweighted full-target baseline. R1 keep every input but zero rare-word
target losses. R2 keep every input and use rare weights.25,.5 rather than0.
R3 common specialist plus unchanged native fallback, with a learned normalized
class/mixing probability. R4 shared backbone with two heads and a stop-gradient
common branch or gradient-projection control. R5 invert the mask as a negative
control. Test corpus-count and article-relative thresholds separately. First
use census cutoffs retaining70%,85%,95% of observed lexical occurrences, with
ties admitted as groups; record the actual fractions rather than split identical
frequency classes to hit an exact requested fraction. Keep source-literal,
escape, case and layout targets in the loss unless their own paid channel is
specified. Align masks to complete word occurrences/encoded spans, not to
shared WRT code bytes. Other words sharing a code byte must remain reachable.

Use matched useful-target exposure and report both actual target exposures and
wall time. Controls retain equal capacity and optimizer schedules. Screen at
128/384/1152optimizer steps only after declaring batch size/sequence length,
targets contributing nonzero loss, seeds and native evaluation offsets. Keep
25% of continuation compute for uncertain/slow early curves, avoiding automatic
rejection of an entire mechanism. Freeze thresholds/architecture before
independent articles/slices. Evaluate every coded event and report common,
rare, literal/layout and total signed bit gains separately. A common-word
improvement does not qualify if rare-word losses outweigh it. Quantized native
export, exact decode and code/model/mask/state resource charges remain gates.

## Mechanism and rigorous tests

Letg_C,g_Rbe gradients of the common and rare losses on shared parameters.
One update usingg_C+lambda*g_Rchanges common loss to first order by
-eta*(||g_C||^2+lambda*g_C^T*g_R). Negative dot products can cause interference;
their existence and aggregate importance in this core are currently unmeasured.
Measure per-layer cosine, norm, Fisher-normalized projections, signed common
loss change and total loss on fixed article blocks. Include frozen-backbone,
separate-head and equal-update controls. A negative local dot product is not
proof that permanent masking improves final codelength; curvature and rare
loss must be included. Use Hutchinson Hessian-vector checks or exact small-head
Hessians to assess whether first-order predictions match actual updates.

For a disjoint common/rare vocabulary partition, a legal word law is
q(w|h)=pi(h)*q_C(w|h) forw inC and(1-pi(h))*q_R(w|h) forw inR.
Both conditional laws normalize on their supports. The class likelihood is
paid: L(w|h)=L(class|h)+L(w|class,h). A soft expert mix is also normalized but
must keep all legal byte/word outcomes reachable. The actual current word's
rarity cannot choose its expert for free. Per-article final frequencies require
a charged table/mask if used during decode, or a causal prefix estimate.
Global training loss priorities need not be shipped if the decoder uses only
the exported predictor; any stored lookup used at inference is charged.

All variants remainOPEN. The census is a diagnostic, not a masking-training
result, proof of core gradient interference, model optimum or archive saving.
