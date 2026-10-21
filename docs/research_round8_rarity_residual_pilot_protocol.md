# A96 partial pilot: native dictionary-word masks, frozen backbone

Registered 6 October 2026 before training. This executes a small learned residual,
not finetuning of the original transformer and not complete testing of A96.
The original predictor and all its online updates remain frozen to the recorded
native traces. Keep every input/context. Mask only offline loss contributions
of complete dictionary-code spans after a recognized page boundary. Literal,
escape, case, layout and unaligned prefix events always retain loss. This pilot
does not mask rare OOV words encoded as literal bytes. Global frequencies are
from the completed original-text census, whose scope excludes XML metadata;
using them as a native-atom training policy does not relabel that census as
native dictionary frequencies. No frequency lookup is used by inference.

Check all 44,515 dictionary codes and proper prefixes against the v2 prefix
contract. Mark the entire encoded span only after the offline target word is
resolved. These labels may inspect training targets; predictor features may
not. Starting slice fragments are kept unmasked until a recognized page marker.

Native bit predictor: offset is the frozen wider three-coefficient source law.
Add an 8->16->1 tanh MLP (161 parameters) with zero-initialized output layer.
Eight causal features: native logit/12, previous-valid neural disagreement,
FXCM disagreement, pre-SSE disagreement, native uncertainty, bit position/7,
previous completed hidden-row validity, and constant 1. Feature formulas use
the original pre-target stage channels and actual native Q16 probabilities.
No target-word or frequency label enters the feature matrix.

Ten arms: unweighted plus rare weights 0, .25, .5 at corpus count cutoffs
107, 1392, 8372 (the census's approximately 95%, 85%, 70% retained lexical
occurrence policies). Seeds 6106 and 6107. FP32, AdamW lr=.001, weight_decay=0,
batch=32768 nonzero-loss bit targets sampled with replacement. A/B first
393216 bytes each are training; last 131072 bytes each are development. Report
nonzero, inspected/sampled and weighted target exposures separately; a zero-mask
arm samples its active pool and consequently sees more common targets. This
is a useful-target-matched screen, not equal common-target exposure or equal
original-transformer work. Save this confound explicitly.

Train all ten arms for 128 steps. Keep unweighted and the best four masked arms
by two-seed development all-target Q16 loss, continue to 384. Keep unweighted
and the best two masked arms, continue to 1152. This small screening ladder has
no claim that a short negative closes a family. Save every rung/checkpoint,
including negative arms. No C/D arm scoring before the finalist list is frozen.
Then score C/D with already preserved native source traces; these are held-out
from this fit but were used in earlier unrelated diagnostics, so do not call
them globally untouched data. Every bit participates in evaluation. Split
signed gains into masked dictionary targets and remaining targets as well as
total; compare to both original Q16 law and wider residual.

Use FP64 NumPy inference from saved FP32 parameters to define the reference
integer law. Check FP32 GPU vs FP64 reference loss/CDF discrepancies rather than
pretending they are identical. Serialized parameter bytes are real checkpoints;
count both model copies and a declared arm selector. Inference source/binary,
CPU/RAM, warm streams and native encoder/decoder still require qualification.
Only a positive separately priced, independently improving finalist can advance
to a new native integration protocol; do not infer archive saving from this
pilot alone. Report whether its 1288 parameter bytes exceed cold-slice savings.

Mechanism diagnostic: on fixed training batches measure gradients of common
and masked-rare losses, their norms/cosine and dot product, at initialization
and selected final checkpoints. This concerns this residual's parameters, not
the original transformer's shared gradients. Labels remain offline. Zero-law
identity must hold at initialization for all 65535 native integers. Test
feature prefix causality independently by altering future raw/hidden rows.

Directory hp_round8/rarity_residual_pilot_v1. Free T4 only, no paid spend,
no project/data/model deletions. Preserve FAIL outputs before a named repair.
