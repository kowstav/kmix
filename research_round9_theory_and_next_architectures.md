# Exact objectives, descendants and remaining architecture work

This is a continuation specification, not a certificate of an absolute optimum.
The 96-family execution ledger is authoritative about actual implementation.

## What masking changes mathematically

For a fixed decoder context h, let P(y|h) be the target conditional distribution
and let positive loss weights be w(y,h). Minimizing weighted cross-entropy gives

    q_w(y|h) = w(y,h) P(y|h) / sum_z w(z,h) P(z|h).

Derive this with a Lagrange multiplier for sum_y q(y|h)=1: the derivative of
-sum_y w(y,h)P(y|h)log q(y|h) + lambda(sum_y q-1) is zero at the expression
above. Thus weighted training deliberately changes the optimum, even with
unlimited model capacity. Zero weights leave ignored outcomes unconstrained and
can eliminate their support. Decompression still needs those outcomes coded by
a complete-support law or an explicitly paid second stream.

For a word-level model with a known candidate frequency mask, inverse weighting
can recover P from q_w after normalization. Our deployed model predicts encoded
bytes, and the current byte may belong to many candidate words. A future word's
rarity label is unavailable to the decoder. Dividing its realized probability
by a future rarity label would therefore be invalid. Exact correction would
require marginalizing candidate word identities and their complete spelling
paths, or a paid class selector. Temperature/mixture calibration on full loss
is a practical approximation; it requires independent native validation.

Better descendants than permanent zero masking are: an easy-first curriculum
that returns to full loss; a full-support predictable common/rare mixture;
projection of the actual optimizer displacement; and precision/rate-aware
selective adaptation. Test each against matched full-loss controls. A benefit
to common words does not prove a reduction in total archive size.

Current labels cover ASCII letters/apostrophes and all dictionary, literal/OOV,
case-control and fragment bytes that make up those words. Unicode-aware word
segmentation/case folding and numeric/entity classes remain separate required
experiments. Unlabelled markup and non-ASCII bytes retain full loss. Do not call
these labels a comprehensive Unicode rarity census.

## Two passes, constructor sets and legitimate lookahead

Let an invertible transform produce content C, constructor sequence G, and
reconstruction metadata M from X. The charged objective is

    L_2pass = L(C,M) + L(G | C,M) + L(transform/decoder/model assets).

Right anchors are available in pass two because C has already been decoded.
They can be useful. They have not become free information: their first-pass
code, locations, lengths, order and exceptions must be counted. If a constructor
bag has n items with multiplicities n_j, a uniform order index alone requires
log2(n! / product_j n_j!) bits. A learned conditional permutation law can improve
that cost; treating equal bags as equal ordered sequences is not lossless.

A useful no-retraining descendant is a finite LM bridge. For known left context
l and an already decoded right anchor r, enumerate a decoder-reproducible finite
set of constructor phrases g and normalize

    q(g | l,r) = q_base(g,r | l) / sum_g' q_base(g',r | l).

The actual phrase, candidate family/order and fallback must have a complete
code. Gap markers must be invertible and escaped; they cannot be chosen from the
realized missing phrase without paying that choice. Cache a prefix state, run
each candidate plus the right anchor, then code the selected candidate with
integer frequencies. Inspect actual native state size, branching CPU time and
RAM. Three attention KV rings plus KDA states already consume megabytes per
branch; the baseline has very little RAM margin. GPU encoder speed does not
remove decoder CPU constraints.

An exact refactorization of the *same* joint distribution cannot improve its
likelihood: q_base(C,M)q_base(G|C,M)=q_base(X). Gains come from a better approximate
joint law or cheaper representation/assets, not rearranging the chain rule alone.
The paid rare-literal split tests do not implement this constructor bridge.
This architecture remains unimplemented and must not be marked tested.

## A stronger retraining architecture for word sharing

The previous word heads used frozen native byte-hidden features. They did not
jointly train a semantic word input path. Their negative finite results do not
settle the following architecture:

1. Assemble completed dictionary atoms and literal characters causally. Feed a
   shared small character encoder of the completed word into the existing core
   through a learned gate. Literal/OOV and mixed atom/literal words need a proper
   parser; a dictionary atom is not always an entire linguistic word.
2. Add a hierarchical word/atom output head matching the exact WRT code tree.
   At a node n, score its children j using context h and character-derived word
   or subtree features e_j:

       pi(j | h,n) = softmax_j(h^T A e_j + b_j).
       P(word w | h) = product_{nodes on path(w)} pi(child_w | h,node).

   This is normalized by construction and evaluates only the reached nodes.
   A flat 44,515-way softmax at every decoded word would be costly on CPU.
   Subtree features can be deterministic means of dictionary-word character
   features, computed from the shipped dictionary and trained shared encoder.
3. Maintain a literal-byte branch with positive support and a learned
   dictionary/literal router. Update latent branch probabilities after each
   observed code byte. Include case controls, dictionary fragments, markup,
   escapes and OOV literals in the exact original-symbol objective.
4. Let constructor/content experts share most of the backbone. Route using
   before-target state, not the realized class. Jointly train the router and
   both distributions using full original-symbol likelihood. Use common/rare
   masks only as controlled curriculum/interference experiments.

Start with width16/24/32 character features, kernel widths2/3/5 and a small gated
projection into the existing192 channels. Compare shared character features,
matched random features, independent word embeddings and a native-byte-head
control. Do not add a large embedding table merely to pass a token-loss screen.
Budget parameter bytes and CPU operations before launching. A bounded LRU of
derived word features avoids a full dense dictionary table; measure actual RAM
and any PPMD-memory tradeoff required to stay under the limit.

Fit using broad articles across the corpus, matched useful-target budgets,
two seeds and 128/384/1152-style short rungs. Freeze finalists using development
full bit cost plus actual model size. Confirm on articles untouched by this
architecture search and run real native encode/decode. First prototype can
freeze the backbone; a genuine architecture test must include a controlled
joint-training variant. These variants are not yet implemented.

## Native precision and parameter-rate engineering

The original asset is internally FX2TFWC3 despite its .tfwc2 filename. Native
reader dumps promote small BF16 tensors to FP32. Repacking that dump as public
V2 changed both the coder and original storage types. Corrected V3 packing in
the original order reproduces the original asset byte for byte; it recovers
about29KB per trained copy from the earlier sorted/public-V2 packing.

Many trained convolution and small-tensor values subsequently required FP32
storage. The BF16-QAT descendant rounds every originally BF16 parameter read
in its owning module's forward, with STE gradients, and preserves parameter
names/checkpoint structure. Eighty-eight parameter reads are covered explicitly.
At export, round and store those original BF16 fields, then verify the native
promoted tensor SHA. Do not reuse an old archive after changing tensor values.

The code-cell penalty tests a different question. If s is a conservative minimum
native code-level spacing, max(|w-w0|/s-.49,0)^2 discourages leaving the original
cell. It is not the weight codelength. The current high-learning-rate penalty
variants lost full loss; alternate tensor weighting, actual packing-in-the-loop
selection, calibrated learning rates and constrained code-index edits remain
possible descendants. Distinguish penalties on code flips from the BF16 precision
cost of formerly half-precision parameters.

## Why no absolute or 20% claim follows

An optimum over arbitrary compressor programs is related to shortest-description
complexity and is not generally computably certifiable. Even within a finite
architecture family, a few runs do not certify the global parameter optimum.
Every compression claim needs exact output, full charged bytes, reproducible
decoder, and eligible CPU/RAM/time. Use a finite, inspectable promotion contract
instead of calling a descendant the best possible one.
