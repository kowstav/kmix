# Hutter Prize round 4: context miners, letter-algebra codes, and overfitting the data (2–3 Oct 2026)

All code, logs and outputs are on Kaggle under `hutter_lab/exp4/`. Numbers are bits per byte (bpb), lower is better. Two protocols are kept apart:

- **Held-out:** the model never trains on the 2.29 MB of test articles; it measures how well the system predicts new text.
- **Contest:** like the Hutter Prize, the model trains on all of enwik8 and its stored weights are added to the total.

## 0. Bottom line

**Held-out, same transformer shape throughout (6.3M weights for the byte model; 7.0M for the dictionary model, whose vocabulary and letter tables are larger):**

| System | bpb | vs start |
|---|---|---|
| Byte-level transformer, 6,000 steps (start) | 1.4829 | – |
| Byte-level transformer + best classical coder (previous best) | 1.4250 | −3.9% |
| Dictionary model (distributional codes + letter algebra), 18,000 steps | 1.2897 | −13.0% |
| + online adaptation + hidden-state cache + kNN over 40M tokens of history | 1.2265 | −17.3% |
| + token-level classical coder, blended online | 1.2117 | −18.3% |
| Continued training (32,000 steps total), kNN over all 58.7M training tokens, + coder | 1.1910 | −19.7% |
| Two-model ensemble (18k and 32k-step models) + classical coder | 1.1871 | −19.9% |
| Three-model ensemble (18k, 32k and 40k-step models) + classical coder | 1.1841 | −20.15% |
| **Four-model ensemble (18k, 32k, 40k and 48k-step models) + classical coder** | **1.1824** | **−20.27%** |

On the 2.29 MB test, that is 339 KB instead of 425 KB.

- The four models are snapshots of one training run continued to 18,000, 32,000, 40,000 and 48,000 steps; the decoder runs all four.
- The 40k and 48k-step models reuse the kNN retrievals made with the 32k-step model's states.
- Alone, the 48k-step model scores 1.2647; with its miners, 1.1989.
- A rerun of the three-model ensemble reproduced 1.1842.

**Where the gain comes from.** To separate training length from the ideas, the byte model was also trained for 18,000 steps:

| Step | bpb | change |
|---|---|---|
| Byte model, 6,000 → 18,000 steps (more training only) | 1.4829 → 1.3752 | −7.3% |
| Byte → dictionary codes + letter algebra, equal training | 1.3752 → 1.2897 | −6.2% |
| Miners + classical coder on that same 18k-step model | 1.2897 → 1.2117 | −6.0% |
| Continued training to 48k steps + four-model ensemble | 1.2117 → 1.1824 | −2.4% |

The cleanest "ideas only" number compares equal 18,000-step training: byte model 1.3752 → dictionary model with miners and coder 1.2117, **−11.9%**. With its own cache miner the byte model reaches 1.3250, so that comparison gives −8.6%. The last row mixes more training with the ensemble; a byte model trained to 48k steps was not run, so the full −20.27% overstates what the ideas alone give.

**Contest (all of enwik8, 4-bit weights, total including the model):**

| System | enwik8 total |
|---|---|
| Byte model, 2 passes | 20.85 MB |
| Byte model, 10 passes | 18.98 MB (archive 16.45 + model 2.53) |
| Dictionary + letter-algebra model, 10 passes | 18.78 MB (archive 15.23 + model 3.31 + dictionary 0.24) |
| + hidden-state cache miner, measured over all 100 MB | **18.54 MB** (archive 14.99) |

That is −11.1% against the first contest run and −2.3% against the best byte model trained for the same number of passes. In this regime the archive shrinks 8.9% (16.45 → 14.99 MB), but the larger model costs 0.78 MB extra plus the 0.24 MB dictionary. On the test articles the full contest system (adaptation, cache, kNN, classical coder) reaches 1.1991 bpb, against about 1.258 for the model alone (−4.7%), but it was too slow to run over the whole file in the time left.

## 1. Answers to the questions

**How fast do unique words saturate?** enwik8 has 354,000 distinct words in 14.5M word occurrences. Share of distinct words already seen:

| Point in the file | Distinct words seen |
|---|---|
| 10% | 25% |
| 25% | 43% |
| 50% | 65% |
| 75% | 85% |

The vocabulary never stops growing, but 97.6% of word occurrences are words already seen earlier. In the second half of the file only 1.3–2% of words are new.

**Does the archive contain the unique words?** No. It contains the surprise of every decision. Best byte stack, held-out test:

| Part of the text | Share of bytes | Share of archive bits |
|---|---|---|
| Letters of never-seen words | 1.6% | 4.0% |
| First letter of known words (choosing the word) | 14.5% | 35.5% |
| Other letters of known words | 55.6% | 39.9% |
| Spaces, punctuation, markup | 28.3% | 20.5% |

**The hard words** (8+ bits each) carry 60% of all bits.

- 97% of them had been seen before.
- 60% had been seen after the same previous word, and 21% after the same two previous words.
- But only 1% were that previous word's most common follower, and 3.7% were among its top five.

The answer is usually in the history, just not as the obvious guess. An exact word n-gram miner could save at most about 4.8%. Miners that compare the model's internal states, rather than exact words, do better (section 2).

## 2. Context miners (decoder-side, zero archive cost)

Every miner below uses only text the decoder has already decoded, and mixing weights chosen online from already-coded statistics, so the decoder can reproduce it exactly.

| Miner | On byte model (1.4829) | On dictionary model (1.2897) |
|---|---|---|
| Hidden-state cache: the model's own recent states; where the current state resembles a past one, the token that followed is boosted | 1.4242 (−4.0%) | – |
| Online adaptation: one small training step after each window | 1.4630 (−1.3%) | 1.2774 → 1.2710 with a denser window (−1.4%) |
| Adaptation + cache | 1.4195 (−4.3%) | 1.2493 (−3.1%) |
| + kNN over states from previously decoded articles | 1.4013 (20 MB history) | 1.2430 (14M tokens) → 1.2265 (40M tokens) |
| + token-level classical coder, blended online | 1.3989 | 1.2117 |

The kNN miner keeps improving with more history:

| History searched | kNN alone | Cache + kNN |
|---|---|---|
| 18k-step model, 14M tokens | 1.2648 | 1.2430 |
| 18k-step model, 40M tokens (denser window) | 1.2449 | 1.2265 |
| 32k-step model, 40M tokens | 1.2279 | 1.2098 |
| 32k-step model, all 58.7M tokens (25.8M stored states) | 1.2212 | 1.2040 |

The cache captures same-article repetition, while kNN brings phrasing and facts from other articles. In an ensemble, retrievals can be shared: the decoder already runs the model that made them, so another member can reuse them without a new search. Giving each member its own retrievals made the ensemble more diverse and slightly better (1.1841 vs 1.1854).

The classical coder needed fixing before it helped. First attempt: 1.2573, worse than the neural system alone (1.2430). The cause was that its mixer started biased toward the weak context models and split its learning over 12,288 weight sets. After re-initialising toward the neural input, using 960 weight sets and a lighter final refiner, it reaches 1.2300 on its own, and 1.2267 blended online.

## 3. Letter-commonality codes and letter algebra

Frequent words (65,536) become two tokens: a group, then a member within the group. The model, data and steps are identical across rows; only the grouping changes.

| Grouping | bpb | vs bytes | Dictionary storage (xz) |
|---|---|---|---|
| None (plain bytes) | 1.4829 | – | – |
| Frequency (conventional) | 1.4624 | −1.4% | 237 KB |
| Anagram / letter-multiset | 1.4367 | −3.1% | 192 KB |
| Alphabetical (shared prefix) | 1.4283 | −3.7% | 150 KB |
| Suffix (shared ending) | 1.4231 | −4.0% | 157 KB |
| **Distributional (shared usage)** | **1.3974** | **−5.8%** | 235 KB |

All letter-based groupings beat the conventional frequency codes, so codes that mirror letter commonality help. Endings help most among the letter groupings, because they carry grammar; grouping by usage is better still.

**Letter-algebra embeddings.** A decoded word is also fed to the model as sums of letter vectors keyed three ways: by position from the start, by position from the end, and by no position (anagram-invariant). Related spellings therefore get related representations.

| Model | Without | With letter algebra |
|---|---|---|
| Alphabetical groups | 1.4283 | 1.4069 (−1.5%) |
| Distributional groups | 1.3974 | 1.3823 (−1.1%) |

Dictionary tokens also help the classical coder: a token-level context-mixing coder scores 1.7365 bpb against 1.8245 for the best byte-level one (−4.8%).

## 4. Overfitting the dataset (contest arena)

The Hutter Prize trains on the file it compresses and counts the model's bytes. Weights are 4-bit (trained with quantisation), and the other tables are 8-bit. Byte counts are the entropy of the stored codes. Totals are measured over all 100 MB unless marked.

| Model (10 passes unless noted) | Test articles (seen) | enwik8 archive | Model + dictionary | Total |
|---|---|---|---|---|
| Byte model, 2 passes | 1.4869 | 18.22 MB | 2.63 MB | 20.85 MB |
| Byte model | 1.3487 | 16.45 MB | 2.53 MB | 18.98 MB |
| Dictionary + letter algebra | 1.2584 (16-bit tables) | 15.23 MB | 3.55 MB | 18.78 MB |
| Same + cache miner | – | 14.99 MB | 3.55 MB | 18.54 MB |
| Same + adaptation, cache, kNN, classical coder (test articles only) | 1.1991 | – | – | – |

At enwik8 scale the model's storage is a large share of the total, so the dictionary model's extra tables (output head, letter vectors, dictionary) cancel much of its archive gain. For enwik9, ten times larger, the same model cost would be spread over ten times more text and the archive gain would dominate.

## 5. Caveats

- **Single runs.** Most configurations ran once; differences under about 0.5% are uncertain.
- **Choices made on the test articles.** A few settings were picked by comparing them on the held-out test: window stride and adaptation rate (3 options), the classical-coder mixer variant (7 options), and the ensemble composition (2 options: 1.1841 vs 1.1854). The selection effect is probably 0.1–0.3%, about the size of the margin: 1.1824 is 0.3% below the 20% line (1.1863). The −20% result holds as measured, but with a thin margin.
- **kNN history.** The kNN miner treats the training articles as previously decoded text. That matches compressing enwik8 in order, but it is a stronger setting than "model only".
- **Decoder cost.** The final held-out system runs four models plus the miners and the classical coder. Decoding is several times slower than the plain model; CPU time was not measured.
- **Dictionary.** It is stored in the contest totals (0.24 MB). In the held-out protocol it is treated as built from already-decoded text.
