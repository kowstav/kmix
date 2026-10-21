# Hutter Prize round 5: working on the real record pipeline (enwik9), 3 Oct 2026

Everything here was measured on **enwik9** with the actual record entry's code
(fx2-cmix-transformer-v1, rebuilt from source), unlike rounds 2–4, which used toy models on enwik8.
Numbers are bytes unless stated. "Slice" = a 2M-token piece of the real post-WRT stream.

## 0. Bottom line

| Item | Status | Saving vs record |
|---|---|---|
| cmix-lex `fxcm_v26` text model ported into fx2-cmix-T | measured on 2 slices with the transformer | ≈ 0.25–0.40% of the payload ≈ **234–375 KB** |
| Revision-record transform (timestamp first, revision id as a residual) | C++ written, exact round trip on all of enwik9; measured with the transformer | ≈ **114 KB** |
| Interlanguage-link title-copy transform | C++ written, exact round trip; measured **without** the transformer | ≈ 76 KB (expect less with the transformer) |
| Weight file: float32 parameters stored as bf16 | built, decoder verified in C++, loss checked on 20M tokens | **108 KB** (both copies, net of loss) |
| UPX `--best --lzma` instead of `-9` | verified identical output | **58 KB** |
| **Total (projected)** | | **≈ 0.55–0.73%**, S ≈ 99.69–99.87 MB |

- **This does not yet reach the 1% prize threshold** (S < 99,420,425). It is also not below the two pending
  September entries at ~99.31 MB.
- The modelling gains are extrapolated from 2M-token slices and cold-start runs. None of this has been through a full
  50-hour compress/decompress run.
- The most important lesson: **the record's cmix stack absorbs almost any "adaptive" improvement to the
  transformer.** Only genuinely new information or plain byte savings survive.

## 1. The landscape (researched first)

| Entry | Total S | Notes |
|---|---|---|
| **fx2-cmix-T** (Vladimir Ivanov, official record, 24 Jul 2026) | **100,424,672** | archive9 96,996,198 + comp 3,428,474 |
| cmix-obias (official) | 108,521,870 | LSTM era |
| cmix-lex (official) | 109,671,639 | fxcm_v26 text model + metadata tail transform + new article order |
| lexth11c (pending, 27 Sep) | 99,313,750 | cmix-lex + transformer, weights retrained for quantisation/compressibility |
| zmix (pending) | ≈ 99.3 MB | weights retrained with a compression-aware loss, Zig rewrite, dictionary derived at compression time |
| rata-cmix (LTCB only) | 100,219,121 | 575 models, online LSTM expert: only −0.15% |

Rules: S = len(comp9) + len(archive9). Each program must run in under 70,000/T hours, where T is the Geekbench-5
single-core score (≈ 49 h on the i7-1165G7 reference), on one core, with ≤ 10 GB RAM and no GPU.

## 2. What I set up on Kaggle

- **Remote control:** a Jupyter websocket client running commands on the Kaggle session (2× T4, 4 vCPU, 31 GB RAM).
  Scratch work lives in `/root/hp` (1.1 TB overlay, not persistent).
- **Correct dataset:** enwik9 downloaded and verified (md5 `e206c3450ac99950df65bf70ef61a12d`).
- **Record rebuilt from source** (clang-17, PGO, UPX): my compressor is 3,427,158 bytes vs the official 3,428,474.
  The difference is UPX/compiler version.
- **Data dump:** the post-WRT token stream (586,459,020 tokens, 205 symbols) and article boundaries (243,427 chunks).
  PPMD priors were stored in a sparse format (≈ 15–33 entries/token instead of 205) for the first 198.6M tokens.
  The full pass was stopped at 34% to free the CPU.
- **GPU harness for the record's transformer on T4:** windowed attention plus the fla Kimi kernels, 63K tokens/s.
  It writes probability files with exactly the C++ semantics (PPMD prior at piece starts, 2^17-token pieces).
- **Lab build of the compressor.** All features are env-gated and inert by default:
  - code any slice of the real stream;
  - forced vocabulary;
  - dictionary pre-training;
  - keep PPMD when loading transformer probabilities;
  - per-byte cost dumps;
  - "no neural model" mode.
- **Validation of the method.** On a 2M-token slice:
  - real C++ transformer → 194,665 bytes; GPU probabilities → 194,669 bytes;
  - transformer loss after 1M tokens 0.462220 vs 0.462240 nats.
  
  A/B tests on slices are therefore faithful.
- **Fidelity bug found and fixed:** `cmix -n` deletes `./.dict`, which fxcm loads, so the first lab runs had fxcm
  without its dictionary. With it restored, slice A improves 0.25%. All A/B numbers below use the fixed setup.

## 3. Anatomy of the record (measured)

**Compressor (S1):**

| Part | Bytes |
|---|---|
| UPX'd code | 195,352 |
| cmix-compressed dictionary | 100,096 |
| article order | 201,042 (compressor only) |
| transformer weights | 2,930,652 |
| header | 16 |

**Archive:**
- archive9 = code + dictionary + weights + payload (≈ 93.77 MB) + header.
- The weights cost 5.86 MB in total because they are counted twice.
- The decompressor restores article order by sorting on page id, so the order file is not in the archive.

**Stream:**
- 586.5M tokens.
- The last 45.3M tokens are PHDA9 metadata:
  - 243,425 revision records (24.7 MB before WRT): page-id delta, revision id, timestamp, contributor;
  - interlanguage-link blocks (14.6 MB).

**Transformer:**
- Architecture: d = 192, 12 layers (9 Kimi linear attention + 3 sliding-window-1024), vocabulary 205.
- Input: the PPMD order-25 distribution.
- Weights: 5,868,864 int4 values at 3.786 bits each; near-uniform and i.i.d.

**What cmix adds over the transformer alone:** −2.97% on slice A and −1.70% on slice B. The transformer is the
system.

## 4. Experiments

### 4a. Gains

| Experiment | Result |
|---|---|
| fxcm_v26 port (cmix-lex's text model; fx2-cmix-T's PPMD kept, so the transformer's priors are bit-identical) | slice A 194,183 → 193,404 (**−0.40%**); slice B 428,199 → 427,132 (**−0.25%**). The cmix side uses ~36–50% more CPU (noisy under contention), roughly +11–15% total runtime. |
| Revision ids from timestamps | Ids are 99.9% monotone in time. Causal interpolation leaves a median residual of 9 (≈ 7.8 bits vs ≈ 24.7). On 100K records: cmix-only 900,641 → 769,713 (−14.5%); **with the transformer 810,234 → 763,359 (−5.8%)**, ≈ −114 KB over all records. The C++ transform matches the Python reference byte for byte, round-trips the full 932 MB main part exactly, and keeps the 13,146,906-line count the decompressor's split relies on. |
| Interlanguage-link title copies | 36% of 659,263 links repeat the article's English title, which the decoder already has. Block k belongs to the k-th article whose body lost its `</text>`; alignment checked across all 93,700 blocks. A title copy becomes `[xx:]`; the 8 genuine empty titles are escaped. On 30K blocks, cmix-only: 736,486 → 698,705 (−5.1%); copies drop from ≈40 KB to 5.6 KB. The C++ version round-trips together with the revision transform (244,173 copies replaced). |
| Weight container: new encoding for float32 tensors with bf16-exact values | 2,930,652 → **2,874,742** per copy. Loss +0.0036% on 20M tokens (≈ 3.7 KB over the stream). The C++ decoder was rebuilt and checked: transformer loss 0.452575 vs 0.452494 on 300K tokens. |
| UPX with LZMA | 195,584 → **166,708** per copy. `upx -t` passes, and compressed output is byte-identical to the unpacked binary. |

### 4b. No gain (measured, then dropped)

| Experiment | Result |
|---|---|
| Online adaptation of the output head (test-time training, carried across articles) | Transformer loss −0.63% at lr 1e-3, but the final archive changed only −0.02% (194,669 → 194,626). cmix's mixers already do this. |
| Online adaptation of the head plus the last MLP | −0.77% at transformer level; not worth +10% CPU given the above. |
| Fast per-article deltas, two-timescale deltas | worse than the single slow delta |
| Transformer context carried across articles (no fine-tuning) | +11.8% (slice A), +1.2% (slice B) worse |
| Final transformer-aware blend after the SSE stage | +0.04% worse |
| Re-quantising weights after training | scales ×1.05 → loss +11% (0.594 → 0.660); the QAT model is locked to its grid |
| Context modelling of the int4 weights | i.i.d.: best is per-tensor at 2,775,037 vs 2,777,390 global; row, column and neighbour contexts are worse |
| Delta-coded article order | 208,185 vs 201,042 (worse) |
| Front-coded dictionary | 114,569 vs 100,096 (worse) |
| Arithmetic precision | final SSE 15-bit, coder 16-bit; ≈ 10 KB at stake |

## 5. The community (Kaggle forum) ideas

**Post 1: context miners, unique words, search, letter-algebra encodings**

- **"The archive only holds unique words?"** No: it holds −log₂ p of every decision. Round 4 measured this:
  - 97.6% of word occurrences are repeats;
  - letters of never-seen words are only ~4% of archive bits;
  - choosing the next known word is ~35%.
- **Decoder-side "context miners" fed from earlier predictions.** This is what context mixing already does: the
  record runs ~600 such miners at zero archive cost. Measured here, extra adaptive miners on top of the transformer
  are absorbed (−0.63% transformer loss → −0.02% final).
- **Encoder-side search for helpful hints.** The choice must be transmitted. Round 3 measured that at 1–10% of the
  archive, more than it saves.
- **"Overfit, no generalisation needed."** Already done: 592 epochs on enwik9 itself. The limits are weights
  counted twice and CPU time.
- **Anagram / shared-letter / "algebra" word codes.** Real gains in round 4 on small enwik8 models (−1.4% to −5.8%).
  However:
  - the record's dictionary is already grouped semantically;
  - any new encoding changes the token stream, which forces a full transformer retrain (~200 RTX-5090 GPU-hours,
    not feasible on Kaggle).
- **"Analyse the words the model struggles with."** This was the useful part. It led to the two working
  transforms, where an earlier item is the hint for a later one: article title → interlanguage titles, and
  timestamp → revision id.

**Post 2: context TTL**

- The record already has a learned TTL: 9 Kimi linear-attention layers whose forget gates learn how long to keep
  information, plus 1,024-token attention and cmix match models over the whole history.
- Round 3's keep-alive memory gave −1.3% on small models, but it needs retraining.
- A second model choosing what to keep is free if causal and too expensive if it uses lookahead.
- OCR and glyph ideas were already tested in rounds 1–3: worse than zlib, or about 0.0004 bits/byte.

## 6. Caveats

- Slice results come from 2M-token pieces with cold cmix models. Steady-state effects over 586M tokens may differ.
- The interlanguage transform has only been measured without the transformer. For the revision transform, the
  transformer cut the gain from −14.5% to −5.8%, so expect a smaller real gain here too.
- The fxcm_v26 CPU cost was measured on an overloaded shared CPU. A clean timing is still needed to confirm the
  50-hour limit holds; my estimate of the record's runtime suggests headroom on the reference machine.
- No full enwik9 compress/decompress round trip has been run. That needs ~2 × 40–50 hours on a dedicated machine.

## 7. Kaggle disk and deletions

- **Nothing was deleted.** The old `hutter_lab/` (19 GB) in `/kaggle/working` is untouched.
- Scratch lives in `/root/hp` (59 GB, on the non-persistent overlay).
- A 3 MB backup of scripts, patches, logs and the new weight file is in `/kaggle/working/hp_round5/`.
- All scripts and patches are also copied to `round5/` next to this report.

## 8. Next steps (most promising first)

1. Build one candidate from fxcm_v26 + both tail transforms + the bf16 weight file + UPX LZMA. Time it cleanly, then
   do a full round trip on a dedicated machine.
2. Recover the transformer's share on the transformed tail. Options: a short fine-tune of the transformer on
   transformed records, or feeding the timestamp-predicted id to cmix as a context instead of rewriting the text.
3. More decoder-side cross-references in the tail:
   - partial and transliterated title matches (the remaining ~516 KB per 30K blocks of link titles);
   - other record fields.
4. Combine with the pending entries' main lever: retraining the weights for compressibility and quantisation. This
   needs far more GPU than Kaggle offers.
5. Shrink the code (remove debug paths) and code the order file conditioned on enwik9: tens of KB.
