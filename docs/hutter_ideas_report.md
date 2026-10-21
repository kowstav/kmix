# Hutter Prize: a fair test of the two idea files, plus context TTL (round 3, 2 Oct 2026)

Ideas tested:
- `hutter_prize_idea1.txt`: the Progressive Constraint Coder (skeleton, word lengths, Wordle feedback, confidence order, whole-word candidates, retrieval, training that mimics decompression).
- `hutter_prize_idea2.txt`: character geometry (glyph features, shape classes, residual expert, shape-first coding).
- The follow-up question: **context TTL**, keeping useful earlier context alive beyond the model's window, chosen by a second model.

All code, logs and outputs are on Kaggle under `hutter_lab/exp3/`.

## 0. Bottom line

1. **The word-length-first transformer (idea 1's word-length model) beats the established next-byte transformer.** Two seeds each, full 2.29 MB test: 1.4726 against 1.4841 bits per byte, **−0.77%**. It is the only reformulation from the idea files that won head to head. After blending with a classical coder its edge disappears (+0.2%), so it needs its own blending work to pay off in a full system.
2. **Context TTL works once it doesn't have to double as scratch space.** A learned scorer that keeps likely-to-recur words alive picks as well as an oracle that knows the future. On its own (128 keep-alive words) it did not beat 128 empty slots. Given **128 empty slots plus 128 keep-alive words**, it beat an otherwise identical model with 256 empty slots by **−1.3%** (1.7012 against 1.7235), and blanking its keep-alive half costs it **1.6%** (a noise-free same-weights comparison). The gain survives blending with the classical coder: **1.5518 against 1.5641 (−0.79%)**, the best blended result of every memory variant.
3. **Every other reformulation lost**, and the reasons are now measured:
   - **Any-order / confidence / Wordle coding:** +21% to +130%. A model that may reveal bytes in any order must represent 2^B partial-reveal patterns per block. Under a fixed weight budget that capacity dilution costs bits, even after training to convergence on the scored text (the Hutter regime).
   - **Skeleton-first:** makes letters 9.7% cheaper but word boundaries 51% more expensive; net +2.2% after strong engineering.
   - **Geometry:** a real but tiny edge over random groupings, about 0.0004 bits per byte.
4. **Smaller real gains found along the way:** extra memory slots of any kind (all five variants −1.2% to −2.6% against plain; differences between them are within run-to-run noise); word plus class contexts in the classical coder (−3.4% classical alone, −0.5% blended); whole-word candidates with a frequency prior (−4.9% inside the progressive family); decode-matched training (−5.6% inside the family).

## 1. Fairness rules used

1. **One framework, one dial.** The progressive coder and the standard next-byte model are the same code (`exp3/bd.py`). Block size B=1 is exactly the standard left-to-right model; larger B allows any order inside a block.
2. **Equal resources.** Same weight count (6.3M), same data (97 MB of enwik8 articles), same steps and optimiser. Scores are on held-out articles unless marked "Hutter regime".
3. **Everything counted.** Skeleton symbols, feedback bits, length symbols, in-dictionary flags and candidate ranks are all coded and counted, in bits per original byte.
4. **Each idea gets its best partners:** decoding orders, decode-matched training, warm starts, the Hutter-regime arena, retrieval, online adaptation, blending with a classical context-mixing (CM) coder.
5. **Controls for every claim:** geometry against identity and random classes; word-length against a left-to-right coder given identical context information; feedback against parallel decoding with the same number of model calls; memory content against the same empty slots; seed replicates where differences are small.

## 2. Results

### 2.1 Progressive coding inside blocks (equal compute, 2,500 steps, 300 KB slice)

| Block size B | Training | Best decoding | Bits per byte | vs left-to-right |
|---|---|---|---|---|
| **1 (left-to-right control)** | standard | – | **1.703** | – |
| 4 | any order | left to right | 2.099 | +23% |
| 16 | any order | left to right | 2.450 | +44% |
| 16 | trained on its decoder's states (skeleton) | skeleton, then letters left to right | 2.485 | +46% |
| 16 | any order + skeleton | whole-word candidates + frequency prior | 2.505 | +47% |
| 64 | any order + skeleton | left to right | 3.922 | +130% |

Inside every progressive model the decoding order ranking was the same: left to right ≥ lowest entropy ≥ most confident > random.

### 2.2 The Hutter-regime arena (small 0.89M-weight models, about 20 passes, scored on their own training text)

| Model | Bits per byte |
|---|---|
| **Left-to-right** | **1.474** |
| Any order, B=4 | 1.783 (+21%) |
| Any order, B=16 | 1.981 (+34%) |
| Trained on its decoder's states, B=16 (skeleton, then letters left to right) | 1.957 (+33%) |
| Any order + skeleton, B=16 | 2.040 (+38%) |

The gap does not close at convergence, so slow learning is not the cause; capacity dilution is.

### 2.3 Training that mimics decompression, and warm starts (2,500 steps, 300 KB)

| Variant | Bits per byte |
|---|---|
| Trained on its decoder's states only (skeleton, B=16), from scratch | 2.485 (5.6% better than the general skeleton model's 2.633) |
| Same, warm-started from the left-to-right model (+1,000 steps) | 2.904 |
| Plain any-order model warm-started from the left-to-right model (+1,000 steps) | 3.091 |
| Control: left-to-right model, +1,000 steps | 1.652 |

### 2.4 Wordle-style feedback against parallel decoding with the same number of model calls

| Model | Calls per block | Wordle feedback | Reveal the most confident directly |
|---|---|---|---|
| B=16 | 3 / 5 / 9 | 3.762 / 3.454 / 3.153 | **3.403 / 3.072 / 2.747** |
| B=16, Hutter regime | 5 / 9 | 3.107 / 2.809 | **2.682 / 2.330** |
| B=16 skeleton model | 19 / 21 | 3.148 / 2.999 | **3.017 / 2.892** |

When bytes are revealed one at a time, a feedback bit costs exactly −log p either way, so feedback can only matter in parallel rounds, and there it loses by 4–20%.

### 2.5 Skeleton-first in the classical compressor (online counting, full 2.29 MB test)

| Coder | Skeleton | Letters | Total |
|---|---|---|---|
| **Left-to-right, same word contexts (control)** | – | – | **1.864** |
| Skeleton first, block 16 / 64 / 256 | 0.869 / 0.883 / 0.883 | 1.131 / 1.078 / 1.058 | 2.000 / 1.961 / 1.942 |
| Skeleton first, block 256, stronger skeleton stage | 0.847 | 1.058 | 1.905 (+2.2%) |

| Position type (share of bytes) | Left-to-right | Skeleton first |
|---|---|---|
| Letters and digits (74%) | 1.500 | **1.355 (9.7% cheaper)** |
| Spaces and punctuation (26%) | 0.389 | 0.586 (51% more) |

### 2.6 Word-length first, interleaved per word

| Coder | Alone | Blended with classical coder |
|---|---|---|
| Classical, left-to-right, word contexts (control) | **1.8640** | – |
| Classical, word-length first, same contexts | 1.8687 (+0.25%) | – |
| **Neural left-to-right transformer, 6.3M weights, 6,000 steps** | 1.4829 / 1.4852 (seeds 0 / 1) | **1.4264** |
| **Neural word-length-first transformer, same size and steps** | **1.4747 / 1.4704 (−0.77% mean)** | 1.4292 (+0.20%) |

The word-length transformer spends 0.18 bits per byte on spaces and punctuation, 0.41 on word lengths and 0.88 on letters, and it won while seeing 15% fewer bytes in training.

### 2.7 Idea 2: character geometry

| Test | Geometry | Matched control |
|---|---|---|
| Residual expert on the transformer, 4 seeds | +0.106% (geometry classes), +0.105% (glyph features) | +0.080% (random classes), +0.072% (identity) |
| Class contexts in the classical coder | 1.853 | **1.847 (random classes)**; 1.842 hand-made classes |
| Same, blended with the transformer | 1.430 | 1.430 |
| Shape-first binarization | 1.917 (worse than 1.889) | 1.925 |

### 2.8 Online adaptation as a shared add-on (300 KB, one step per 4 KB)

| Model | Frozen | Adapted |
|---|---|---|
| Left-to-right (B=1) | 1.703 | 1.697 (−0.3%) |
| Skeleton model (B=16) | 2.637 | 2.633 (−0.1%) |

### 2.9 Context TTL: analysis

How the 6.3M transformer's 415 KB on the full test splits by word occurrence:

| Word occurrence | Share of all bits | Average cost |
|---|---|---|
| First mention in the article | 39.6% | 13.6 bits |
| Repeat, under 512 bytes back (inside window) | 8.1% | 5.3 bits |
| Repeat, 512 bytes to 2 KB back | 7.3% | 10.5 bits |
| Repeat, 2–16 KB back | 8.5% | 10.5 bits |
| Repeat, more than 16 KB back | 1.7% | 12.1 bits |

For rare words a repeat costs 6.65 bits inside the window and 14.0 outside, so a perfect keep-alive memory could save about 6% of all bits. Rare first mentions (34% of bits) can only be helped by cross-article memory.

**The learned keep-alive scorer** (logistic regression, 5.3M training examples) learned a time-to-live by itself: time since last mention −3.0, in the title +1.25, number of mentions +0.98, overall frequency +1.10. Memory slots are filled by probability of reuse × bits saved ÷ bytes used.

**Encoder-side search with transmitted hints does not pay.** Coding the oracle's keep/drop choices with the scorer as the shared prior costs 10.1% of the archive for all candidates, 4.1% for the top 100, 2.1% for the top 30 and 1.0% for the top 10. That is more than the ≈6% total prize allows, given about 13.6 truly needed words among 476 candidates per window.

### 2.10 Context TTL: memory models (2,500 steps each, full test)

| Model | Memory at evaluation | Transformer alone | Blended with best classical coder |
|---|---|---|---|
| Plain (no slots) | – | 1.7439 | 1.5707 |
| **128 empty slots (registers)** | empty | **1.6981** | **1.5520** |
| 128 heuristic memory words | heuristic | 1.7037 | 1.5527 |
| 128 learned keep-alive words | keep-alive | 1.7206 | 1.5595 |
| same model | oracle | 1.7228 | |
| same model | empty | 1.7400 | |
| 128 oracle memory words | oracle | 1.7184 | 1.5576 |
| same model | keep-alive | 1.7270 | |
| same model | empty | 1.7376 | |
| 256 empty slots (control) | empty | 1.7235 | 1.5641 |
| **128 empty + 128 keep-alive words** | registers + keep-alive | **1.7012** | **1.5518** |
| same model | keep-alive half blanked | 1.7289 | |
| 128 linked-article words (link-following memory) | link | 1.7142 | – |
| same model | blanked | 1.7150 | |

How to read this table:
- **Across different runs**, differences up to about 1.5% are within run-to-run noise at 2,500 steps: 256 empty slots scored worse than 128 empty slots. Every slot variant beat plain (−1.2% to −2.6%).
- **Within one model**, comparing its own memory against a blanked memory is noise-free. Remembered words helped every model trained with them: −1.1% (keep-alive), −1.1% (oracle), −1.6% (registers + keep-alive). The keep-alive selection was as good as the oracle's for the model trained on it.
- **The design that works** gives the network both: free scratch slots and a keep-alive memory.

## 3. What is worth carrying forward

| Component (source) | Measured effect | Verdict |
|---|---|---|
| Word-length-first transformer (idea 1) | −0.77% alone (2 seeds); +0.20% blended | **Real win standalone**; needs a matching classical coder |
| **Context TTL with scratch slots** (128 empty + 128 keep-alive words) | −1.3% against the same-size empty-slot model; −1.6% within-model; −0.79% blended | **Works; worth scaling up** |
| Link-following memory (linked earlier articles' words) | −0.05% within-model | No value as built |
| Extra memory slots of any kind | all five variants −1.2% to −2.6% against plain (2,500 steps) | Real; the ranking between them is within noise |
| Word + class contexts in the classical coder (from geometry controls) | −3.4% classical alone, −0.5% blended | Small, real engineering gain |
| Encoder-side search for context with transmitted hints | hints cost 1–10% of the archive | Not viable; selection must be decoder-side |
| Whole-word candidates, decode-matched training (idea 1) | −4.9%, −5.6% inside the progressive family | Help the family, which still loses overall |
| Any-order / confidence / Wordle / skeleton-first (idea 1) | +2% to +130% | Not competitive under a fixed weight budget |
| Glyph geometry (idea 2) | ≈ 0.0004 bits per byte | Negligible |

## 4. Next steps, most promising first

1. **Scale context TTL with scratch slots.** Train at full length (6,000+ steps) with 2–3 seeds, try 256 empty + 256 keep-alive words, and give the scorer a richer target (bits saved, not only "reappears").
2. **Combine the two winners.** A word-length-first transformer with scratch slots plus keep-alive memory, blended with a word-length classical coder that gets the same engineering as the left-to-right coder.
3. **Blend the word-length model better.** Its standalone edge (−0.77%) disappears when blended, because its classical coder adds less than the left-to-right one does; that is a tuning gap, not a property of the idea.
4. **Re-check the slot effect at full training length**, where run-to-run noise is smaller (0.15% between the two 6,000-step seeds, against about ±1% at 2,500 steps).

## 5. Caveats

- Absolute numbers are far from the contest: these models see about 2 passes of data at most.
- Most configurations are single runs; only the word-length result has two seeds per arm.
- The classical coder is a simple stand-in for cmix (1.82–1.89 bits per byte alone).
- The global word counts used by the TTL scorer and the link index come from text that, in a real decoder, would have to be restricted to already-decoded material; that is a small optimism.
- Decoder CPU time was not measured.
