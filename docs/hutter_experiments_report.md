# Hutter Prize experiments: round 2 (Kaggle, 2 Oct 2026)

All code, logs and outputs are in the Kaggle session under `hutter_lab/exp2/`. The earlier lab in `hutter_lab/` was left untouched.

## 1. What the earlier lab had done

All 54 runs (18 ideas x 3 seeds) and every follow-up stage had finished; nothing was left pending. It screened many ideas with very small models (3 layers, 400 training steps), scoring about 2.5 bits per byte (bpb). Results:

| Idea | Result |
|---|---|
| Letter-shape / glyph / orthography features | No gain; within seed noise |
| Skeleton-first and Wordle-feedback coding (PCC) | 2.0 to 6.0 bpb against about 1.4 for plain left-to-right coding on the same 4 KB sample: worse |
| Sorted-dictionary, OCR and pixel encodings of text | All worse than zlib |
| Hard-word "residual" specialist | About 1% gain on a weak base model |
| 2-bit and 3-bit weights | Large losses, but quantised halfway through a 400-step run |

The models were too small and too briefly trained to settle much, so round 2 uses properly sized models.

## 2. Setup for round 2

- **Data:** the full enwik8, split by article. 97.0 MB of training text, 0.7 MB for validation, and 2.29 MB of held-out test articles (250 articles). Test articles are never trained on. This is stricter than the contest, where the model is trained on the very file it compresses.
- **Model:** a byte-level transformer with 6 layers, a 512-byte window, and 6.3M weights at width 288 (similar in size to the record entry's 6M-weight transformer). Each run trains for 6,000 steps on about 197M bytes, roughly two passes over enwik8, taking 23 to 60 minutes on a T4 GPU.
- **Context-mixing (CM) model:** a small C program written for this (`exp2/cm.c`), similar in kind to the counting models in cmix and PAQ: order-0 to order-6 contexts, a word context, a match model and a learned mixer. It warms up on all 97 MB of training text and is then scored on the test articles. It can take the transformer's predictions as an extra input, which gives the "blend" results.
- **Measurement:** all figures are ideal code lengths (−log2 p, summed). A real arithmetic coder adds a negligible amount on top.
- **Seeds:** every run is a single seed, so differences under about 1% are uncertain.

## 3. Results

### 3a. Stored size: more weights at fewer bits, or fewer weights at more bits?

| Run | Weights | Bits per weight | Test bpb | Nominal size | Entropy-coded size |
|---|---|---|---|---|---|
| f288 (float reference) | 6.3M | 16 | 1.483 | 12.3 MB | – |
| q4_288 | 6.3M | 4 (15 levels) | 1.516 | 3.22 MB | 2.63 MB |
| q3_336 | 8.5M | 3 (7 levels) | 1.537 | 3.19 MB | 2.29 MB |
| **t448** | **14.9M** | **ternary (1.58)** | **1.477** | **3.30 MB** | 3.30 MB |
| f448 (float, upper bound) | 14.9M | 16 | 1.393 | 29.5 MB | – |

- **Ternary wins at equal nominal size:** the 2.4-times-larger ternary model beats the 4-bit model by 2.6% and slightly beats the float 6.3M model.
- **The quantisation penalty grows as bits shrink:** 4-bit costs 2.2% against float of the same size (the record entry reported 2.6%), while ternary costs 6.0% against float of the same size. 3-bit was the worst trade of the three.
- **Weight compression is a real lever:** the 4-bit weight values carry only about 3.1 bits of information each, not 3.9, so entropy coding shrinks them by about 20%. If the record entry's 2.9 MB of 4-bit weights behave the same way, that is roughly 0.5 MB, half the 1 MB needed to beat the record. This was not tested on their actual weights, and zmix may already capture some of it.
- **Catches:** after entropy coding, the 4-bit model is 0.67 MB smaller than the ternary one. The ternary model also needs 2.4 times the computation per byte unless the decoder uses add-only kernels, and time is the contest's binding limit.

### 3b. Where the bits go (6.3M float transformer on the test articles)

| Category | Share of bytes | Transformer bpb | Share of bits |
|---|---|---|---|
| Prose, lowercase words | 42.2% | 1.68 | 47.8% |
| Wiki link targets `[[...]]` | 12.8% | 1.64 | 14.2% |
| Capitalised words (names) | 9.0% | 2.00 | 12.2% |
| Punctuation | 3.6% | 2.36 | 5.7% |
| Spaces and newlines | 12.3% | 0.49 | 4.1% |
| URLs | 2.5% | 1.84 | 3.1% |
| Digits | 1.0% | 3.09 | 2.1% |
| XML metadata (ids, timestamps) | 4.0% | 0.55 | 1.5% |
| Everything else | 12.6% | – | 9.3% |

- **The bits are spread out, not concentrated in a few hard words:** the most expensive 10% of bytes carry 42% of the bits, half of all bytes carry 98%, and 37% of bytes cost under 0.1 bit.
- **Choosing the word costs far more than spelling it:** the first letter of a word costs 3.9 bits, the second 1.8, the third 1.5, and letters from the sixth on about 0.6.
- **First mentions cost twice as much as repeats:** a word's first appearance in an article costs 12.4 bits, a repeat 6.2. Words never seen in training cost 24 bits; common words (1,000 or more training occurrences) cost 6.0.
- **The transformer has a window blind spot.** For words that are rare in training and repeated within an article, the cost depends on how far back the previous mention was:

| Previous mention | Transformer (512-byte window) | Same model, 2,048-byte window | CM | Blend |
|---|---|---|---|---|
| Under 512 bytes back | 7.9 bits | 6.6 | 12.2 | 7.2 |
| 512 to 2,048 bytes back | 15.4 bits | **10.3** | 13.2 | 12.4 |
| More than 2,048 bytes back | 14.4 bits | 14.9 | 14.3 | 12.9 |

  Once the earlier mention leaves the window, the cost doubles. The 2,048-byte window cuts the 512-to-2,048 case by a third, so the explanation is confirmed. But that model was worse overall (1.509 against 1.483): with the same training budget it saw fewer, longer samples. A longer window needs more training, or a cheaper long-range mechanism.

### 3c. Online adaptation ("dynamic evaluation")

After scoring each 512-byte window, the model takes one Adam training step on it. A decoder can do exactly the same, because it only uses bytes already decoded. For the ternary model, adaptation starts from the shipped quantised weights, not the training-time float weights.

| Model | Frozen | Best learning rate | Adapted | Gain |
|---|---|---|---|---|
| f288 (float) | 1.483 | 0.00001 | 1.463 | 1.3% |
| t448 (ternary) | 1.477 | 0.00001 | **1.436** | 2.8% |

- **Learning rates above 0.00003 hurt:** 0.0001 gives 1.539 and 0.0003 gives 1.740.
- **Gains concentrate in names and long-range repeats:** for rare repeats 512 to 2,048 bytes back, the cost falls from 15.4 to 13.6 bits.
- **Cost:** each adaptation step is a backward pass, roughly 2 to 3 times the computation of prediction alone. That was not timed on CPU here.

### 3d. Do the gains stack? (ternary model, adaptation, then blending with CM)

| Configuration | Test bpb | Change against the line above |
|---|---|---|
| Ternary transformer, frozen | 1.477 | – |
| + online adaptation | 1.436 | −2.8% |
| + blended with the CM model | **1.405** | −2.2% |
| (frozen ternary + CM blend, no adaptation) | 1.421 | −3.8% against frozen |

They partly overlap, because both fix in-article repetition, but they still stack: 4.9% in total over the frozen ternary model. Against the original 4-bit 6.3M model (1.516) at about the same stored size, the full stack is 7.3% better.

## 4. What this means for the contest

1. **Capacity per stored byte is the biggest lever measured:** 2.4 times the weights is 6% better in float, and ternary keeps most of that at the same storage. Whether it fits depends on making ternary inference fast on one CPU core (add-only kernels, skipping zeros).
2. **Entropy-coding the 4-bit weights** could save about 0.5 MB on a record-sized model at no cost in accuracy. This is the cheapest thing to verify, by checking the record entry's actual weight file.
3. **Online adaptation (2 to 3%)** stacks with blending. It needs a CPU time budget, so adapting only a small part of the network (norms, last layers) is the version to test next.
4. **Long-range repeats** (512 to 2,048 bytes back) are a concrete, measurable leak. A longer window fixes them but needs more training. A sparse long-range attention layer, or feeding the match model's prediction into the transformer, are cheaper options.
5. **The earlier lab's "novel" ideas** (shape features, skeleton or Wordle coding, OCR, sorted dictionaries) all lost to plain left-to-right prediction and are not worth more GPU time.

## 5. Caveats

- Absolute numbers are far from the contest. These models see about 2 passes of data; the record entries train for hundreds to over a thousand passes on the file they compress. Only comparisons between runs are meaningful.
- Single seed per configuration.
- The CM model is a simple stand-in (1.89 bpb alone), much weaker than cmix's. The size of the blending gain will differ in a real entry.
- CPU decode time was not measured. All timings are GPU training times.

## 6. Files (in `hutter_lab/exp2/` on Kaggle)

- `prep.py`: article-disjoint split of enwik8.
- `lm.py`: transformer training with 4-bit, 3-bit and ternary quantisation-aware training, sliding-window evaluation and weight-size report.
- `cm.c`: the context-mixing measurement model, with transformer blending.
- `dyneval.py`: online adaptation.
- `analyze.py`: category, word, distance and model-comparison analysis. Output in `analysis.txt` and `analysis.json`.
- `summary.json`: all run results.
- `runs/<name>/`: `report.json`, `test_cost.npy` (bits per test byte), `model.pt`.
- `logs/`: training logs.
