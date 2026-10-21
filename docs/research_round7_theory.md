# Round 7: no-retraining mechanisms worth testing

Prepared 4 October 2026. This is a research proposal, not an experimental result. I read rounds 3–6, the idea files, and the local round-5 analysis and adaptation code. I did not access or modify Kaggle, delete files, or run the compressor. No local AGENTS.md was present in the workspace listing.

## Decision and scale

The best supported direction is to preserve the original post-WRT stream and add probability models for precise relations that the existing predictors cannot easily recover. Round 6's owner-title and revision-time relations are evidence for that direction. They are not evidence for another generic byte cache: the exact-context, title-trie, dense state-cache, adaptive-head and cross-article-state experiments already make those poor first choices.

The round-6 baseline ledger needs its previously identified 1,316-byte reconciliation, and structural gains need warm-history/main-text controls. Use the strongest reproducible core, not a weaker core to make percentage gains look larger.

Using the report's official total S=100,424,672 and payload=93,770,082 bytes, a 20% total reduction means approximately 20,084,934 bytes saved. If fixed parts do not shrink, that requires a 21.42% payload reduction, or 0.2740 bits per 586,459,020 WRT symbols. The duplicated transformer weights together are only 5.86 MB. Even deleting all of them would not reach the target, and would damage prediction. The measured structural savings are 0.275 MB. A 20% result must recover major main-text redundancy or use a fundamentally better model; minor packaging changes cannot supply it.

There is no general computable procedure for finding the optimum over all lossless compressors: unrestricted shortest-program compression is not computable. With precisely specified finite executable-size and runtime bounds, exhaustive search is theoretically finite, but computationally infeasible at this scale. For a fixed predictor, arithmetic coding already approaches its assigned negative log probability. Large improvement requires changing the probability model or representation and paying the complete description cost. We can certify the best result among a bounded, specified tested family, not claim a global optimum.

## Common mechanism: preserve the neural model's stream

All proposed first experiments use the original symbol order. The transformer, PPMD, cmix and SSE update on exactly the decoded original bytes. A specialist changes the final coded probability, not the model's observations. This avoids the measured out-of-distribution loss from changing metadata representation.

Let Q_B be the baseline's sequential distribution and let H_j be a causal specialist. At a syntactically detected field boundary, use

    Q(x) = w_B Q_B(x) + sum_j w_j H_j(x),  with w_B + sum_j w_j = 1.

Weights and specialist state are derived from the decoded prefix. Update posterior responsibilities only after coding each bit. For a deterministic copy candidate s, H_s puts all its probability on s, including its terminator. If the decoded next bit disagrees, that candidate's posterior becomes zero. For a match to an expected bit b:

    w_s' = w_s / [w_s + (1-w_s) q_B(b)]

in the two-hypothesis case. This mixture charges one field-level fallback penalty, -log2(w_B), when the field does not fit any deterministic candidate. It avoids repeatedly treating the remaining alphabet as uniform. For edit automata, replace the deterministic candidate with a normalized finite-state distribution and filter its state causally.

Implement this after the final baseline predictor where possible, without adding an unconditional new mixer to unrelated main text. Always compare unpatched baseline, patched-neutral baseline, and active specialist. The posterior and finite-state arithmetic must be reproducible with deterministic integer/fixed-point updates, including rescaling.

Candidate selection is part of the probability model. An encoder may search using the target only if it transmits the choice and includes the corresponding cost. It may not select a helpful donor for free. A mixture over prefix-selected donors is valid. Actual-symbol cost files permit retrospective scoring, but unavailable future fields cannot enter the candidate list.

For semantic parsing, mirror the existing inverse-WRT process on already decoded bytes, retaining exact WRT byte spans and their semantic boundaries. Do not assume the raw XML/wiki markup survives unchanged. A field boundary becomes active only when its delimiter and necessary nesting state have been decoded. Unknown/ambiguous/oversized structures fall back to baseline.

## 1. Article-scoped entity and field relations

**Hypothesis.** A decoder knows the owning article's title, earlier aliases, infobox facts and completed link targets. Exact relations between these values and later surface forms can help first mentions or long-range repeats, even though a global trie cannot choose the correct title from hundreds of thousands of alternatives.

**First candidates.** Full current title; title without a parenthetical disambiguator; title with underscores/spaces converted consistently; an already decoded explicit alias; a previously decoded field with the same entity identity; a link label related to its decoded target. Generate only small, transparent transformations. Do not introduce transliteration tables or arbitrary suffix rules before a measured residual class supports them. Preserve exact spelling/case in stored forms; normalized variants do not replace the original data.

**Activation and causality.** Activate at recognized template parameter values, link label starts, article lead starts, caption/entity-name positions, and other precisely parsed boundaries. The title precedes the body. An alias/field is inserted only after its complete original bytes are decoded. For piped links, the target is available before the label; that specific relation is useful even if a target-prefix trie was redundant. For ordinary prose, activate at a word boundary with a tightly capped candidate set; confidence must come from past outcomes and decoded context, never the actual upcoming word.

**Probability.** Mix the full-field string candidates with Q_B. Back off confidence from boundary type × title/alias relation × case/length compatibility to a global prior. Use a small Bayesian grid of initial copy odds; update from completed outcomes. This is structurally narrowed prediction, not assigning a large uniform cache mass to all article words.

**Resources.** Current-article memory can be capped at 64 aliases, 128 completed facts and 64 KiB exact strings; very long values are skipped. Candidate count ≤8 per active boundary. Byte/bit prediction requires comparisons and a few scalar posterior updates, no extra transformer forward passes. A compiled rule bank is likely small; its actual packed marginal size is measured twice, not assumed free.

**Falsification.** Attribute final-coder costs to title/alias/target-related fields before building the production expert. Compare full-title only, transformed-title only, explicit-alias only and combined versions. Reject if candidate mass predominantly lands on already cheap symbols or if a disjoint confirmation slice has nonpositive gain after mismatches. A global title trie is not a substitute for this test. The affordable first screen should establish at least tens of kilobytes net and a plausible full-file budget; a small success should be reported as small.

## 2. Schema-keyed copy/edit automata for noncontiguous templates

**Hypothesis.** Near-repeated infoboxes, citations, sports/geographic records, navigation templates and list entries share a schema while variable fields interrupt long exact matches. A short byte suffix and an exact-string trie do not retain the correct template-field/column relation across those interruptions. A schema-keyed edit model can.

**Prefix-selected donors.** Key memory by decoded template name, parameter name/path, section family or table header/column. Use the last 1–4 complete values/rows under a key. A second key may include an already decoded discriminator such as country/type/date, but never the unknown value. Learn donor weights from earlier fields. Keep a bounded deterministic LRU/clock replacement policy.

**Distribution.** Start with exact whole-field copies. Then test a small probabilistic edit transducer: copy donor symbol, substitute one symbol, insert a literal, delete a donor symbol, or terminate. Literal emissions use an explicitly normalized escape distribution. Edit rates and donor weights are estimated after each completed field. A bounded band limits the number of alignment states; cap candidate field lengths and outstanding insertion runs. A dynamic-programming filter maintains the summed probability of all valid alignments. This is a distribution over possible next bytes, not a cheapest alignment selected using the unknown future.

An alternate command codec could transmit donor/rank + edit script and replay the reconstructed original bytes into all predictors. That might obtain larger savings, but it must also pay mode, donor, edit, termination and binary costs. Do not call the encoder's best donor free. First prefer the sequential mixture, which is simpler to validate and keeps all baseline states synchronized.

**Resources.** Begin with a 64 MiB donor byte arena, ≤250,000 indexed values, ≤4 donors/key and 1,024-byte maximum value. Use compact array entries, not millions of heap objects. Active state cap ≤64 per donor; at most a few hundred scalar transitions per active byte. Profile active-byte fraction and total runtime before expanding memory. The total process must remain below the prize RAM bound; 64 MiB additional memory is a cap, not a license to exceed an already full baseline.

**Falsification.** Compare keying by schema with shuffled or unrelated keys using the same memory/candidate budgets. Compare exact copy with edit model. Match improvement must survive code length from substitutions, insertion ambiguity and initial donor odds. If the final coder already gives ≤1–2 bits to most donor matches, a standalone compression success is insufficient. Reject donors whose final-mixture gain does not exceed the cost of maintaining their state. This is the highest-ceiling candidate here if repeated structured main-text content carries a large residual-bit share, which has not yet been measured.

## 3. Coupled numeric/algorithmic prediction in fields and tables

**Hypothesis.** Serial numbers, years, ordered list indices, coordinates, dates, measurements and table columns may follow short arithmetic programs. The current timestamp expert demonstrates that a specific integer relation can help. Extending the principle requires schema and column identity, not another unconstrained numeric prior.

**Causal model family.** For each already decoded column/field key, test constant value; last value; last difference; short integer linear recurrence; repeated number from another already decoded field; date/number reformatting; and bounded rational unit conversions only where source and units are already known. Each candidate renders a precise byte string with its known formatting. Formatting details—sign, leading zeroes, decimal point, separators, unit suffix and digit width—are model state, not ignored residuals. Keep a grammar escape for invalid/irregular values. Do not assume a checksum or age/date equality unless the relevant source fields precede the target.

Use a normalized integer residual model for imperfect relations. Prefix probabilities for decimal digits can be computed by intersecting the numeric range of a decoded digit prefix with the residual distribution. Intervals and tails must be evaluated stably, with deterministic arithmetic. For small model sets, mixtures of rendered integer candidates are simpler and safer than sophisticated continuous fitting.

**Causality.** A model is fit only to completed rows/fields. An observed recurrence is not added until enough earlier terms have been decoded. No record reordering, peeking at later cells, or offline coefficient choice without counting stored coefficients. Numeric relation parameters learned online need no archive table, but their code is counted.

**Resources.** Cap 16 hypotheses and a few small integer sufficient statistics per schema key. Total state ≤8 MiB for the first test; all computations use bounded integer operations. Activate on digit spans only, avoiding extra transformer work. Large values/overflow fall back to baseline.

**Falsification.** First measure final-coded bits in eligible numeric spans and the bit-weighted frequency of a correct prefix-causal relation. Compare schema-aware predictors with last-number and formatting-only controls. Abandon a family if its ideal recoverable budget is <100 KB or its real mix fails a confirmation slice. This is likely an engineering gain rather than a 20% source; it should not consume the majority of research time unless the residual atlas reveals a unexpectedly large numeric budget.

## 4. Corpus-specific executable macros, priced as a model

**Hypothesis.** Large groups of boilerplate/stub/list paragraphs may be generated by a short program with a few parameters (owner title, ordinal, already decoded field, or an explicit residual). Unlike free-context hints, a macro can reconstruct a long span and pays its model cost once across many uses. This is a high-risk route toward much larger gain, if substantial near-duplicate material survives PHDA/WRT preprocessing and the baseline still pays for it.

**Search family.** Restrict programs to literal strings, references to already decoded article fields, exact escaping/case conversions, short integer formatting operations, and bounded repetition. Discover candidate families offline from expensive spans. Freeze and serialize selected macros as model data. This is model construction without neural retraining; the literal pool, rule instructions, ranks and parameters are all counted. Do not hard-code a corpus database into the executable and omit its size.

**Selection and coding.** At a decoder-visible start boundary, mix macro-generated string distributions with Q_B, or explicitly code a macro ID plus parameters/residual edits. An encoder using future data to choose a macro must pay that choice. A macro referring to a future article or field must store/transmit it, or be rejected. Reconstruct original WRT bytes and replay their exact updates; a transform that bypasses model updates is not the same comparator.

**Accounting.** For a macro family g, evaluate

    G_g = baseline bits covered - [macro model bits × actual package copies
           + use IDs/parameters + literal/edit residuals + all mode/escape costs].

Use a covered-span allocation so overlapping families do not double-count gains. Optimizing a finite cover/program dictionary is a tractable local search objective; it is not a proof of shortest possible compression. A two-part MDL program only survives if G_g>0 on the complete corpus after all package costs.

**Resources.** Bound literal pool to 256 KiB for the first sweep, program length to 32 instructions, candidate expansions to ≤8 per recognized boundary, and maximum output span to 4 KiB. Memory <16 MiB initially. Pure string/integer rules require no GPU and no additional neural model. Large generic semantic programs, OCR, external knowledge and large language models are excluded from this first family.

**Falsification.** The decisive first diagnostic is an optimistic priced cover of actual high-cost spans. If even perfect macro/use selection with real literal/rule costs cannot approach 1–2 MB, do not implement a complex codec. If the cover is large, include true IDs/parameters and causal availability before claiming gain. Use mismatching/rejected families as controls. This is the most speculative proposal, but its ceiling is larger than adding another small probability correction.

## Residual atlas and immediate experiment order

Never import round-4 enwik8 bit shares or its 20.27% result as a statement about the present record. It used weaker models, more training and a four-model ensemble. The current final coder needs its own atlas.

For each complete word/field/span retain: original-stream offsets, WRT offsets, article ID, syntax/field/column key, exact spelling, word occurrence number in article and prefix, title/alias relation, previous occurrence distance, final baseline bits, standalone neural bits if available, and candidates derivable before the span begins. Rank by cumulative final bits, not word count or low raw model probability alone. Weight tail/rare-word categories by their actual total bit budget.

Use at least four article-stratified pieces: early titles, mature-history main text, long articles and a late/redirect-heavy piece. Include title/field distributions, rare/common article lengths and markup/table frequencies. Development selectors may see earlier observed costs, but a production activation rule must not use the upcoming symbol's cost. Maintain an independent confirmation piece for decisions and a full-file final comparison. Fixed-corpus optimization is allowed; confirmation pieces diagnose sampling artifacts, not a requirement to generalize to a different corpus.

First implement the common finite-candidate field-mixture scorer. It can screen entity copies, exact schema copies and rendered numeric candidates with the same auditable math. It must emit per-class gain, mismatch cost, activation count, active bytes, RAM and CPU operations. Stream probability/cost data in chunks; do not create another hundreds-of-gigabytes dense-distribution dump on the full disk.

Stop gates: (1) an optimistic diagnostic ceiling too small to cover code and integration cost; (2) no gain on matched final-coder confirmation; (3) topology effects absorb the gain; (4) violated CPU/RAM bounds; or (5) an independent decoder cannot reconstruct exact bytes. After passing gates, compare the complete package against the same baseline and perform native production round trips. A “breakthrough” label requires that measured result, not an oracle ceiling or extrapolated weak-baseline percentage.

Priority: entity/field candidates first because the existing title expert provides evidence; exact schema copies second; numeric programs third in parallel if their bit budget supports them; schema edit automata and macro discovery only after the simple screens reveal substantial residual mass. The strongest plan is to let these measured budgets choose the next search branch.
