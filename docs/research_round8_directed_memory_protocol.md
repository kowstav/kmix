# Directed prefix memory without a shipped semantic graph

Registered 6 October, after weak continuous semantic gains and before directed
memory results. This descendant replaces pretrained neighbor excitation with
prefix-learned directed associations. It does not claim that cosine semantics or
the original transformer is optimal; the frozen core remains unchanged.

At a completed content word v, update next-content pair (previous content,v)
and a second co-occurrence model for up to eight earlier content words in the
same article. Nearer sources receive integer weight 8-age. Page starts clear
pending sources; learned rows persist across pages. Words enter after their
delimiter/entity completes, never from a prediction guess or unfinished spelling.

Each model has 1024 deterministic direct-mapped rows. A row stores a source ID,
eight target IDs and eight uint16 counts. A key collision replaces a row; within
a row, Space-Saving replaces the smallest count with that count plus the new
weight. Tie breaks use target ID. Counts halve deterministically before overflow.
The packed row design is 34 bytes (2+8*2+8*2), two models 69,632 bytes before
alignment/control fields. Current C++ instrumentation uses wider native structs;
the packed production design is not an achieved RAM result. Decoder-built state
has no transmitted graph cost, but code, function-word classification, regret,
updates, prior counts and RAM must still be paid.

Use normalized sparse rows relative to the same prefix-frequency prior, no
uncounted omissions. Arms: generic, next-content row, same-row target shuffle
matched by frequency band/length/content class, exact content recency, eight-content co-occurrence
row, its matched shuffle. Share the constructor-run residual and repaired parser.
Control shuffling operates on the same stored learned rows and counts, so gains
cannot be attributed merely to a larger history store.

Warm source state causally along the actual earlier full transformed stream;
query A0/C100M/B102635191/D180M first128K with existing cold-core native traces.
This is conditional source opportunity, NOT full warmed-core qualification.
Source queries occur in increasing order; fitting then uses A/B only. Complete
record format and convex bounded head/certificate match continuous_protocol.
Parameters are 16B generic or32B other per copy. No original transformer training.

Test directed pair learning, current-word noninterference, article pending reset,
row/target count bounds, collision replacement, normalization, XML/long-comment
behavior and exact source/input match. Store source prefix event counts and
elapsed CPU/wall/RSS. Run all six heads with frozen A/B coefficients on C/D;
report controls and coefficient cost before any advance. A promising source must
then be tested with fully warmed core and actual compact native coding. No rental,
deletion, external graph requirement or managed Goal change.
