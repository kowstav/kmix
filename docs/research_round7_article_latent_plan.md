# Priced article hints and a possible training extension

5 October2026 IST. Hypothesis, not a breakthrough. The current neural checkpoint
is frozen. The first experiment constructs sparse word profiles without neural
SGD and charges every future-informed choice. Large improvement is unproven.

The earlier causal graphs improve repeats slightly and fail on first mentions.
An alternative is to transmit a compact article hint before the body. An encoder
may inspect the article to choose that hint; its decoder must receive the choice.
Both sides continue updating their original predictors on the exact original
WRT bytes. Hint bits belong to a separate explicitly framed channel and do not
enter the transformer/PPMD stream or shift their positions.

For a finite profile family z and fixed mixing strength a, define a normalized
distribution H_z over complete dictionary atoms. At an event boundary,

    Q_z,a(e | prefix) = (1-a) B(e | prefix) + a H_z(e).

H has zero mass on literal, escape, case and syntax events; their fallback
penalty is -log2(1-a). The variable-length dictionary paths are prefix-free,
including overlapping first bytes of some two/three-byte codes. Within an event,
posterior probabilities telescope across its path; baseline and specialist
states reset to the selected event prior after completing that event. This is
a proper mixture over possible events, not free assignment of mass to the
observed word. Escape length/case/control behavior must be mirrored exactly.

The paid selection objective for article region j is

    G_j(z,a) = sum_events log2[Q_z,a(e)/B(e)] - length(selector(z,a)).

The screen freezes32 topic profiles plus one global content control, each with
at most256 word IDs and positive integer counts summing to65535. Seven fixed
strengths give231 specialist choices. Code0 chooses neutral at a cost of1bit;
code1 followed by8bits chooses a specialist at9bits. Unused IDs are invalid.
Its Kraft sum is1/2+231/512 <=1. The encoder minimizes actual region cost over
this finite family and writes the chosen ID. This future-dependent minimization
is legal because the selector is paid. Choosing a new specialist per unknown
bit without such a code remains invalid.

Profiles are constructed from A/B article TF-IDF vectors via seeded16-dimensional
SVD and32-way clustering, then integer-quantized sparse distributions. C/D do
not fit the tables. Only sparse tables are needed by a decoder; SVD, clustering
and Python dependencies are construction tools. Store the complete table as an
explicit zlib stream and charge its finished byte count twice in this package.
A native implementation must additionally price its actual packed parser,
mixture and zlib decoder costs. Future content is never present as an uncharged
causal feature.

Selectors begin only after an already decoded complete article separator.
Piece starts before synchronization use the original coder. A fixed piece-end
boundary explains a cut final article in this likelihood screen; any production
segmentation uses known block lengths and counts additional framing. Fields
that contain a separator-like byte sequence need precisely the same recognition
at both ends. The screen must not quietly use an offline semantic article label
that the submitted decoder cannot reproduce.

Evaluate final-coder likelihood, not word counts alone. Report profile gain
before selectors, gain after selectors, table size, and all-cost sample totals.
Charging the entire table to each short slice is conservative for that slice;
it does not prove that a positive payload gain fails after full-file amortization.
Conversely, multiplying a few cold samples into a whole-file saving is not a
validated score. Frozen C/D checks precede any expensive full run. If the paid
gain is tiny or negative, do not build a large native topic system.

If the finite sparse family reveals substantial useful topic information, a
future training pilot could condition a lexical head on a transmitted discrete
latent. A small title-conditioned prior P_phi(z | decoded title) can reduce
selector cost. Its parameters/code must be stored. A learned posterior over
article content is an encoder construction procedure, not a decoder input.

For the latent extension, optimize

    J = sum_j [-log2 P_phi(z_j | title_j)
              -log2 P_theta(article_j | title_j,z_j)]
        + 2 R_theta + 2 R_phi + framing + executable costs.

Use actual quantized distributions and exported sizes in selection. The hint
rate cannot be omitted. A full-text bag-of-words or entity database is expensive
side information unless encoded under this objective. Extra parameters, title
priors and latent symbols are alternative expenditures of the same bit budget.

An information-theoretically exact baseline would not acquire a free expected
saving from revealing such a hint: its information cost must be paid. Here the
opportunity is compensating for a finite, misspecified predictor. The magnitude
of that opportunity requires measurement. Topic access, lexical state updates,
spelling composition and stronger quantization-aware training are different
mechanisms whose gains cannot be added without a joint final-coder run.

Any neural pilot stays within the existing $70 ledger, beginning with the $4
throughput/export control. Do not start it merely because these formulas sound
promising. First establish a reproducible stronger baseline, correct priors,
full-piece/token-weighted sampling and a lambda0 continuation control. The
remaining architecture proposal is research_round7_word_model_plan.md.
