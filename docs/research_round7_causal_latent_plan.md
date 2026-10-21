# Causal latent word memory without stored topic hints

This is a finite tested-family proposal, not an attained optimum. It addresses
one limitation of the earlier paid-topic experiment: the old family stored
21,844bytes of sparse topic tables and chose an article specialist using a
paid selector. The new model learns full-support word/topic counts from the
already decoded prefix. Its document posterior is inferred from that prefix,
including completed title words. There is no stored article hint or future
topic choice. Neural weights remain unchanged.

Letw index the existing dictionary words andz indexK topics. The dictionary is
already packaged and its order is available to the decoder. Define a normalized
rank priorr_w proportional to1/(w+16), and positive integer hashes
h_wz in[128,383], deterministically derived from the spelling and topic index.
For stop words useh_wz=256 for every topic. Define:

    C_wz = accumulated integer topic responsibilities,
    C_z  = sum_w C_wz,
    g_w  = number of previously decoded occurrences,
    G_z  = sum_w g_w h_wz,
    R_z  = sum_w r_w h_wz.

The topic distribution, withS=4096,kappa=64,eta=1/16, is

    theta_z(w) = [C_wz + S eta (g_w + kappa r_w) h_wz]
                 / [C_z + S eta (G_z + kappa R_z)].

Its numerator sums exactly to its denominator in exact arithmetic. The
document mixture is

    phi_z = (d_z + S/4) / (sum_z d_z + K S/4),
    Q(w)  = sum_z phi_z theta_z(w).

After the actual word is decoded, its responsibility is proportional to
phi_z theta_z(w). Largest-remainder quantization produces nonnegative integers
a_z whose sum isS. ThenC_wz andC_z increase bya_z,g_w increases by1,andG_z
increases byh_wz. This preserves integer mass accounting. Update the document
posterior by one of four fixed rules:K=8 or16 with whole-article retention, or
integer decay127/128 or255/256. These decays apply per completed dictionary atom: the
128/256 labels are approximate exponential time scales, not hard expiration
and not counts of all ASCII words. Completed title words receive three units of
document evidence; ordinary content words one; stop words zero. The word
still contributes to global/topic counts. Reset only document state when a
complete page marker has been decoded.

Integer counters avoid accumulating fractional responsibility mass. On the
one-billion-byte target there are at most one billion dictionary-atom events;
uint64 counters are sufficient, including their hash-weighted sums. Prototype
floating divisions still need a deterministic production implementation and
measured arithmetic quantization. The current NumPy screen is not a submitted
decoder.

The specialist assigns normalized mass to the prefix-free dictionary tree.
Every literal, syntax, case-control and escape outcome receives zero specialist
mass and therefore pays the neutral branch. For a complete evente,

    P_alpha(e) = (1-alpha) P0(e) + alpha Q(e),
    gain(e) = log2[(1-alpha) + alpha Q(e)/P0(e)].

Q(e)=0 for non-dictionary outcomes. Its probabilities must never activate
after discovering that the unknown target is a dictionary word. The score
uses only the previous event category and decoded article age to select an
adaptive mixture context. It includes all fallback losses. A Bayesian mixture
over the fixed alpha grid and six word families places half its initial mass
on the neutral expert; the mixture's likelihood includes selection uncertainty.
No best-per-event oracle is a realizable compressor.

For native bit prediction, aggregateC_wz and hash-weighted rank/global masses
on the actual WRT prefix tree. Then subtree probabilities evaluate the same
normalizedQ without scanning all44,515 words per coded bit. Update aggregates
only on the observed word's ancestor path. The changing posterior over neutral
and specialist branches within an event gives a normalized bit distribution;
their likelihood ratios telescope to the whole-event screen. Invalid dictionary
code paths retain neutral mass. Context/posterior updates occur only when the
event terminates from its decoded bytes.

Price the incremental native executable twice. Prefix-derived counters are
RAM and CPU costs, not free resources. Do not package NumPy or a dense offline
word/topic table as if it were a small C++ predictor. Full warmed native RSS
must remain below the prize limit, including existing PPMD/NN histories and
tree aggregates. Prototype array bytes and wall time are reported separately.
Any positive ideal gain requires independent-slice, native quantization,
round-trip and package checks before promotion.

The first reused root scorer began at the beginning of the initial page marker.
That synchronization choice could look ahead. Its owned exploratory process
was stopped, all source/logs/results preserved, and no native job touched.
The corrected version starts after the complete marker, which the decoder can
recognize from its prefix. Tests check normalized full-support distributions,
integer responsibility accounting, mixed two/three-byte codes, neutral regret,
and complete post-marker byte charging. Earlier tiny root/new-mention gains
remain provisional until this synchronization rule is applied to them.

The screen evaluates B/C then A/D against actual native lexical final-coder
costs. Each slice starts its own latent state cold. It has no neural SGD,
stored topic table, or unpaid article selector. A rejection eliminates this
specified family; it cannot disprove all semantic memory architectures. A
positive result is only a likelihood result until the native/accounting gates
are complete.

## Audit of prior strength and the isolated V3 comparison

The corrected V2 screen finishes B/C at -1.562/-2.462 bytes before native
code cost. Its learned component is weaker than the label "topic model"
suggests. After M decoded dictionary atoms, a roughly balanced topic has
C_z approximately S M/K, whereas its global prior has mass approximately
S eta 256 M. Thus the prior-to-learned ratio is approximately16K:
128 for eight topics and256 for sixteen. The learned fraction is only about
1/129 or1/257. More generally C_z<=SM and G_z>=128M imply that the learned
fraction cannot exceed1/9 at eta=1/16, even if one topic receives every
responsibility; the additional rank pseudocount reduces it further. This is
a dimensional/scaling weakness of this family, not evidence against semantic
memory as a whole.

V3 normalizes the global/hash base before giving it a fixed topic pseudocount:

    pi_z(w) = [(g_w + kappa r_w) h_wz] / [G_z + kappa R_z],
    theta_z(w) = [C_wz + S kappa_topic pi_z(w)]
                 / [C_z + S kappa_topic],
    kappa_topic = 64 decoded-word equivalents.

The base sums to one for every decoded prefix. Learned mass now grows as
(C_z/S)/(C_z/S+64) instead of remaining suppressed by the entire corpus's
global count. At initialization, predictions equal the V2 distributions.
The document posterior, completed-word updates, alpha grid, event charges,
hashes, reset and decay rules remain identical. No future selector, offline
topic table or neural SGD is introduced. Explicit normalization, initial
equivalence, integer-mass and post-marker tests precede the corpus screen.

One B/C comparison is queued behind the existing V2 and native recovery,
with separate source/output/log files. It is not a duplicate or a broad
hyperparameter search. Its CPU/RAM/package and warm-history feasibility
remain unmeasured until evaluated in native code; changing prior strength
cannot itself establish the requested20% result.
