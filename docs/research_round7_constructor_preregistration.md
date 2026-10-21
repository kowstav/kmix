# I11 constructor/content stream screen — fixed before launch, 5 October 2026

Human proposal: share grammar-word sets/subsets between content-word anchors;
decode content first to make right context available for constructor prediction.
Status at registration: code written, not run on the four measured slices.

Hypotheses: ordered constructor-template reuse may amortize a paid dictionary;
unordered multiset reuse may further help if it exceeds the paid permutation
and framing costs. No assumption that nouns are long words or that grammatical
prediction is exact. No parser model is installed or retrained for this screen.

Fixed protocol: use the explicit function-word lexicon in
research_round7_constructor_split.py, three representations (direct constructor
lists, exact ordered raw-word templates, raw-word multisets plus order ranks),
and two matched codecs (zlib level9 and LZMA preset6). Run all A/B/C/D2M original
WRT slices without selecting lexicons/hyperparameters from the results. A/B
development and C/D check status is retained; all four are previously examined
research data, not a pristine untouched validation corpus. A new untouched
slice is necessary for a subsequent optimized candidate.

Representation: every non-lexicon ASCII word is a content anchor, including
markup labels. This is a fixed heuristic, not a POS/noun assertion. Words are
located with the checked WRT inverse; only disjoint ORIGINAL encoded byte
spans are moved. Raw prefixes, dictionary/case controls, all separators,
punctuation, XML, binary bytes and partial EOF tails are retained verbatim.
Content stream contains framed raw anchors. Gap stream contains constructor
raw spans and framed exact separators. Offline template tables, IDs, lengths,
multiset multiplicities, permutation bits, padding and both compressed-channel
headers are serialized and included in the measured candidate packet.
The decoder does not need a parser/lexicon to reconstruct these raw packets.

Preflight: exhaustive rank/unrank over 243 length5 three-symbol sequences;
empty/duplicate constructor sets; literal uppercase, punctuation, binary,
partial EOF fixtures; each representation/compressor must reconstruct all raw
bytes. Full slice roundtrip is also mandatory. Constructor native cost budget
comes from the existing final-coder byte costs and disjoint spans. Whole-slice
template entropy is descriptive only and is not credited as a free model.

Gate: any matched-codec gain is a representation screening result only. It is
not a gain against cmix/the Hutter record. Charge incremental decoder/model
bytes and benchmark the actual newly ordered streams with a suitable normalized
model before promoting the idea. A content-first grammar model may use decoded
right anchors, but the frozen original-order transformer's original costs
cannot be reused after removing/reordering words. A loss does not prove every
syntax-conditioned architecture loses; it rules out this exact representation.

Launch/recovery on current Kaggle kernel after uploading both new scripts:
execute research_round7_constructor_split.py with --selftest in a subprocess;
if PASS and no existing constructor_split_v1 directory/process, execute
research_round7_launch_constructor_split.py. Outputs:
/kaggle/working/hp_round7/constructor_split_v1/{manifest,summary,a,b,c,d}.json
and constructor_split_v1_controller.log. Destination and log use exclusive
creation. On session failure inspect the preserved directory before relaunching;
never clear/overwrite it to manufacture a clean run. No deletions, paid compute,
training, Goal mutation, or duplicate native trace collection is authorized by
this registration itself; this launch is part of the human continuation.
