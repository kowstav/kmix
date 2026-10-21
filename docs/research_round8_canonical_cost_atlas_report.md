# Which words cost the native coder bits?

Canonical lexical cold A0/B102635191, 512KiB each. The native prediction/source hashes, complete category totals, top100 dictionary words and all causal-cluster rows are in the adjacent a/b JSON files. This is a completed finite cost attribution, not a compressed candidate or a full-corpus linguistic analysis.

## Same-event totals

All1MiB of prepared bytes account for 157145.252732bytes of native ideal arithmetic likelihood. Every coded bit is included. Category reconciliation errors are below1e-5bit. Header synchronization, literal/control bytes, escapes and partial EOF are not discarded. Actual archives have coder/header/termination overhead, so a likelihood saving is not automatically an archive-byte saving.

| Assigned category | Native likelihood bytes | Share of native bit cost |
|---|---:|---:|
| sync_prefix | 886.661 | 0.564% |
| literal_or_control | 52610.351 | 33.479% |
| other_dictionary | 83365.469 | 53.050% |
| constructor_dictionary | 20189.557 | 12.848% |
| escaped_payload | 93.215 | 0.059% |

The predeclared constructor list accounts for12.848% of this sample's native cost. This is useful evidence about allocation, not a bound on all grammatical language or the full archive: the list is incomplete, is not POS tagging, and excludes separate casing/spacing/control costs. Even perfectly predicting all codes in this particular list would erase only their assigned20,189.557bytes while holding the rest fixed; a complete alternative codec also pays structure and ordering. A grammar-only breakthrough cannot be assumed from their raw occurrence frequency. Other dictionary atoms and literal/control channels need joint attention.

## Cumulative difficulty differs from a spectacular single mistake

### Slice A

| Dictionary word | All occurrences | Cumulative native bytes | Mean bits per atom |
|---|---:|---:|---:|
| the | 2727 | 568.449 | 1.668 |
| and | 698 | 248.086 | 2.843 |
| in | 689 | 235.999 | 2.740 |
| of | 3761 | 228.602 | 0.486 |
| king | 719 | 224.882 | 2.502 |
| emperor | 678 | 200.167 | 2.362 |
| a | 326 | 160.024 | 3.927 |
| is | 522 | 155.534 | 2.384 |
| pope | 362 | 133.466 | 2.950 |
| saint | 159 | 115.201 | 5.796 |
| to | 477 | 115.114 | 1.931 |
| becomes | 301 | 101.761 | 2.705 |
| byzantine | 273 | 97.330 | 2.852 |
| first | 136 | 96.113 | 5.654 |
| kingdom | 145 | 96.016 | 5.297 |
### Slice B

| Dictionary word | All occurrences | Cumulative native bytes | Mean bits per atom |
|---|---:|---:|---:|
| the | 7075 | 1807.191 | 2.043 |
| a | 3150 | 1151.337 | 2.924 |
| in | 2408 | 1073.440 | 3.566 |
| and | 2680 | 993.821 | 2.967 |
| to | 3194 | 805.246 | 2.017 |
| for | 1291 | 605.344 | 3.751 |
| of | 3189 | 549.605 | 1.379 |
| telephone | 1013 | 515.825 | 4.074 |
| or | 1001 | 505.087 | 4.037 |
| is | 1831 | 452.637 | 1.978 |
| call | 824 | 446.412 | 4.334 |
| with | 782 | 436.762 | 4.468 |
| that | 851 | 402.064 | 3.780 |
| an | 598 | 390.450 | 5.223 |
| on | 698 | 389.648 | 4.466 |

For example, B's “the” averages2.043bits per dictionary atom but consumes1,807.191bytes cumulatively. “An” costs5.223bits per occurrence yet only390.450bytes in that slice. “Telephone” is a repeatable topic atom with1,013occurrences and4.074bits/atom. A's “of” is already cheap at0.486bits/atom. These are possible specialist targets; their current cost is not recoverable saving, and capitalization/role/all other bits must still be modeled.

A contains3,761distinct dictionary words and B7,778, in a44,515entry dictionary. Those are local slice counts, not the percentage of all200,000linguistic word types previously observed by the actual full decoder. They cannot answer the original first-occurrence coverage question. Rare out-of-dictionary lexical words are partly represented by literal/control/escape sequences here, so this report does not pretend to rank every rare linguistic word. Full warm coverage and exact reconstructed lexical-word attribution remain separate work.

## Causal clusters: a useful negative control

The3840possible contexts use only previous completed atom class, current atom byte depth, current byte bit position and native p1 bucket. No unknown target word or observed current surprise enters the assignment. KT(.5,.5) counts pay their cold estimation through complete prequential loss. On A/B this fixed cluster law loses 4248.086809bytes against native identity. A global half-prior mixture with native identity limits ideal regret to1bit per reset and loses 0.251968074bytes after Q16 rounding. This is not a positive compression result.

Direct posterior storage saturated in the failed v2 audit, irreversibly eliminating an expert. V4 uses cumulative log posterior odds and checks an independently computed batch likelihood normalizer. Its maximum streamed accumulation discrepancy is 7.50739127e-06bits; the batch ideal regret is0.125byte per slice and the Q16 tax is measured separately. Failed versions and logs remain preserved. This matters for every proposed long-horizon Bayesian expert mixture: an algebraic regret proof does not by itself prove the floating implementation preserves the weights.

## Use this ledger for the attachment's next tests

1. Retain the original native p, target, piece/reset and offset for real residual supervision. Rank cumulative cost and recurrence, then test whether a prefix-visible relation predicts signed residual error after the existing p is known.
2. Compare ordinary and costly occurrences, false associations, constructor/content roles and literal/XML channels. Use same-size generic, shuffled-pair and null controls. Test every activation, not just the ones that helped.
3. Separate unbiased replay, deliberately weighted curriculum and synthetic auxiliary tasks. Fresh synthetic prefixes require consistent regenerated native states/priors if used as supervised core examples.
4. Freeze choices before independent native checks. Measure complete package, CPU/RAM and warmed history. An apparent entropy gap or cost budget is not recovered bytes; coefficients amortize over the full file and cold screens cannot establish that rate.

The experiment protocol was registered before outcomes. No C/D was read for this audit, no core was trained, no paid compute was used and no project data was deleted. See research_round8_canonical_cost_atlas_protocol.md and research_round8_attachment_training_addendum.md.
