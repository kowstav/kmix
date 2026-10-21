# Fixed continuous semantic confirmation and paid sparse graph

Registered after the continuous AB128K fit and CD128K confirmation, before full
2M results. Core stays frozen. Freeze all six heads from continuous_strength_v2;
do not refit on full slices. Export each float32 source signal before prediction
as in the fitting records, promote it to double, then compute the Q16 probability.
First reproduce all six Python prediction SHA256s and gains on A/B/C/D128K with
the independent C++ implementation; abort on any integer difference.

Run each head on existing A/B/C/D2M traces with identical repaired prefix features,
record integer gains, bit counts, per-interval cost, CPU/system/wall/RSS and hashes.
These regions are examined confirmation, not fresh G/H. Original core update
trajectory and features depend on original decoded bytes, not corrected guesses.

For last-content semantic arm additionally evaluate a=0 under the same fixed
coefficients and constructor-run feature. For each completed source word v collect

 G_v=sum_{t:source_t=v} log2(q_full(y_t)/q_off(y_t))/8.

Because the head is frozen and features depend only on true decoded history,
turning off source v changes no subsequent core or feature trajectory. These
marginals are additive for a graph whose only source is last completed content.
This separability does not extend automatically to adaptive gates, multi-word
topic sources, changed stream order or hypothetical decoder errors.

Define a concrete sparse graph description: uint16 K, then K sorted rows of
uint16 source ID plus eight uint16 neighbor IDs =18 bytes/row. Use the complete
prefix-frequency prior when no row is present. With m=2 shipped copies and the
fixed binary64 coefficients, the finite best subset for an encoded input has

 G_sparse=G_off+sum_v max(0,G_v-36)-4-64-1/8 bytes.

This charges source IDs, neighbors, count, coefficients and a mode bit. Loader,
parser/grammar module, framing, actual source-index RAM and real native coding
remain additional. If all subsets lose, select original native mode; do not call
an unpriced source-word ranking a gain. Independent brute-force subset enumeration
on small synthetic marginals must match the recurrence. Store per-source marginal
arrays and selected IDs. A/B source selection may be frozen for C/D confirmation;
an all-data optimized selector is legal only as a priced corpus-specific choice,
not as an untouched test. Report both distinctly.

Full-source graph compressed cost is also reported. Neither a small positive
feature gain nor this finite-subset optimum demonstrates a record or rules
compliance. Promising priced margins require compact native integration, new
G/H and warmed production data before full package testing.
