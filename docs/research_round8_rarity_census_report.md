# Corpus rarity counts and what they imply for masking

Completed6October2026 in the authorized Kaggle session. No training, paid
compute, deletion or measured compressed-size improvement is implied.

The original1,000,000,000byteenwik9member SHA256 matches the preserved source.
The scan includes243,425complete XML pages,243,418with nonempty text, and
excludes a9,743byte incomplete terminal page. Its declared ASCII casefold
word tokenizer finds127,049,170occurrences and1,208,329distinct spellings.
These include wikitext; they exclude numbers, non-ASCII spellings, punctuation
and XML metadata. They are different from the native44,515dictionary entries
and205byte output alphabet. Word/article frequency rows for every observed
spelling are preserved in research_round8_word_article_frequencies.tsv.gz.

| Masking rule | Lexical occurrences removed |
|---|---:|
| Corpus count<2(singletons) |0.482459%|
| Corpus count<16 |2.079652%|
| Corpus count<64 |3.945845%|
| Corpus count<128 |5.390779%|
| Corpus count<1024 |13.267915%|
| Article count<2(singletons within each article) |24.788358%|
| Article count<4 |44.148096%|
| Article count<8 |58.909218%|
| Article fraction<0.1% |20.935032%|
| Article fraction<0.5% |52.706987%|
| Article fraction<1% |65.391876%|
| Article fraction<2% |76.543847%|

612,960types—50.7279%of observed distinct spellings—are corpus singletons,
but contribute only0.482459%of lexical occurrences. **A large fraction of
rare types is not a large fraction of target exposures or compressed bits.**
Whether those types consume disproportionate native bit cost requires exact
word-to-coded-span alignment and native losses; the census does not supply
that measurement. A rare token can be copied cheaply, whereas a common
grammatical choice may remain uncertain.

Local singleton masking leaves no retained lexical targets in74,472nonempty
articles, versus a tiny global-occurrence removal fraction. Redirects/stubs
and short text are part of this observed population. Global and article rules
therefore need matched-retention controls rather than identical numeric
cutoffs. Counts107,1392,8372yield corpus retained fractions95.0182%,85.0025%,
70.0001%, respectively, keeping equal-count classes intact. Start the mild
training intervention with count<16,<64,<128 and compare0/.25/.5/1rare
weights before spending on aggressive masks. The more aggressive quantiles
remain registered diagnostic/conditional arms, not selected winners.

Keep every rare word in the input context. Mask only its aligned target loss
unless a separately priced rare channel is implemented. Compare a common
specialist with native/rare fallback against shared masking at equal parameter,
target-exposure and compute budgets. Evaluate all native bits and report common,
rare, literal/layout and total gains; no saving is earned by dropping targets.
Global/article future counts are offline labels. A decoder lookup/table or
article mask is charged; an alternative inference rule must use past counts.

The scan used453.950083CPU seconds,455.994417wall seconds and760,008KiB
peakRSS. Its gzipfrequency table is19,981,248B with SHA256
a0e69465241c0bc8ac1cb255219b5f2ba76d957c6e1df8d1a0cc07ed00527f2a.
This research table is not a submitted decoder asset. The original/data/models
were preserved. Exact executed worker/protocol hashes and all threshold counts
are in research_round8_rarity_census_results.json. A96training remainsOPEN.
