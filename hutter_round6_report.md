# Hutter Prize round 6: implementing the expert advice (3 Oct 2026)

This round implements `expert_advice.txt`, following its eight-step sequence as closely as the available compute
allows (Kaggle: 2× T4, 4 vCPU, 31 GB RAM, ~12-hour sessions). Everything is measured on **enwik9** with the record
entry's code (fx2-cmix-transformer-v1, rebuilt from source) and the lab harness from round 5:
- the GPU-probability path is validated to within 4 bytes of the real C++ transformer on 2M tokens;
- per-byte cost dumps come from the **final arithmetic coder**, i.e. after cmix and SSE.

Numbers are bytes unless stated. "Payload" means the arithmetic-coded stream.

## 0. Bottom line

**Verdict on the expert's "decisive question":** does a bounded, exactly reproducible memory still save enough bits
after the record's mixer?
- **For names and phrases, no.** Neural-cache retrieval gains 0.045–0.084% against the final coder; exact-context
  retrieval gains nothing.
- **For exact field relations in the metadata, yes.** Stream-preserving experts cut the two structured tail regions
  by **274,829 bytes** in total, measured with the transformer over the complete regions, with CPU time unchanged:
  - revision records: −113,303 bytes (−7.4%) from the timestamp, contributor-id and username experts;
  - interlanguage blocks: −161,526 bytes (−10.7%) from the owner-title copy expert.
- **Five further expert ideas failed** against the final coder (section 5c). Each looked promising in isolation, but
  the coder already had the information.
- **Compression-aware QAT,** run as a short continuation of the converged model, is about 9× worse than break-even. The
  MDL lever needs a full retrain, which is beyond this compute.

Combined position against the official record (100,424,672):

| Item | Evidence | Saving |
|---|---|---|
| Candidate compressor S1 (final experts), built with the official script | **exact: 3,369,451** (record 3,428,474) | 59,023 |
| Fixed parts of archive9 (code 194,384 + dictionary 100,794 + weights 2,874,742 + header 16) | exact: 3,169,936 (record 3,226,116) | 56,180 |
| fxcm_v26 text model (payload) | two 2M-token slices with transformer: −0.40% and −0.25% | ≈ 234,000–375,000 |
| Structural experts, revision records (payload) | full region, same binary, A/B with transformer | **113,303** |
| Structural expert, interlanguage blocks (payload) | full region, same binary, A/B with transformer | **161,526** |
| **Projected total** | | **≈ 624,000–765,000 (0.62–0.76%)** → S ≈ 99.66–99.80 MB |

**Still not enough for the 1% prize threshold (99,420,425):** 239–380 KB short. Also not below the pending entries
(~99.31 MB).
- The fxcm_v26 range dominates the uncertainty.
- The two expert rows were measured with each region coded alone (cold start), as explained in section 5.

The final expert set is: timestamp (single centre), contributor id, username, and interlanguage title copy. The
two-centre timestamp variant was rejected after its full-system run (section 5).

Note on packing: UPX-LZMA saves ~29 KB per copy on the original code, but fxcm_v26's larger code and the experts
consume almost all of it (code per copy 194,384 vs the record's 195,352).

## 1. The expert's eight steps: what was done

| Step | Status | Notes |
|---|---|---|
| 1. Reproduce a competitive baseline | **Partial** | Full ledger of lexth11c (pending entry, 99,313,750) from its evidence files; repo cloned. A full 50-hour build/run was not possible here. Development stayed on fx2-cmix-T, where the round-5 instruments are validated. |
| 2. Complete cost ledger | **Done for components; partial for regions** | Section 2: S1/S2 components of both entries, per-field cost of the revision records, interwiki cost breakdown. |
| 3. Verify round-5 gains on the baseline | **Done on fx2-cmix-T** | lexth11c already contains the fxcm_v26 port (not double-counted); bf16 floats and UPX-LZMA carry over directly. |
| 4. Bounded causal retrieval expert | **Done (screening)** | Section 3: projected-state neural cache and exact-context memory, scored against the final coder. Structural keys became step 6. |
| 5. Compression-aware QAT | **Done (short-continuation regime)** | Section 4: an MDL objective with a soft rate surrogate, plus a matched λ=0 control. |
| 6. Structural channels | **Done** | Section 5: implemented as *stream-preserving structural experts*, so the transformer sees its original stream. Four kept (−274,829 B over the two tail regions); five further ideas rejected against the final coder (5c). Production-mode round trip passed. |
| 7. Representation / title pass | **Not started** | The expert sequences this last; it needs retraining. |
| 8. Full validation | **Not possible here** | Needs ~2 × 40–50 h on a dedicated machine. Component round trips were done instead (section 6). |

## 2. Cost ledger

### 2a. Components (both entries)

| Component | fx2-cmix-T (official record) | lexth11c (pending) |
|---|---|---|
| UPX'd executable (counted twice) | 195,352 | 198,236 |
| Dictionary (twice) | 100,096 | 100,866 |
| Article order (compressor only) | 201,042 | 199,980 |
| Transformer weights (twice) | 2,930,652 | 2,978,039 |
| Payload | 93,770,082 | 92,559,456 |
| Headers | 32 | 32 |
| **S** | **100,424,672** | **99,313,750** |

**T** = 586,459,020 post-WRT symbols, so saving 1 MB of payload requires 0.01364 bits/symbol.

### 2b. Revision records (243,425 per-article records, 15,717,594 post-WRT bytes)

Cost per field with the transformer, first 100K records:

| Field | bits/record | Share |
|---|---|---|
| revision id | 22.35 | 34.5% |
| page-id delta | 11.89 | 18.3% |
| username | 14.19 | 17.1% |
| timestamp | 10.32 | 15.9% |
| IP address | 28.17 | 9.6% |
| contributor id | 3.73 | 4.5% |

Username cost by category:

| Category | Records | bits each |
|---|---|---|
| Same user in the previous 3 records | 9,099 | 1.7 |
| Among the ±1 h time-neighbours | 21,798 | 7.0 |
| Seen earlier, not near in time | 32,767 | 12.1 |
| First appearance | 14,315 | 37.8 |

### 2c. Vocabulary saturation in the exact enwik9 coding order

Word = run of ASCII letters, case-folded; text = PHDA9 output in reordered article order.

- 133,922,554 occurrences; 1,171,106 distinct words.
- 99.13% of occurrences are repeats; dictionary words cover 90.0% of occurrences.
- Distinct-word coverage: 23.3% / 38.2% / 61.6% / 82.9% at 10 / 25 / 50 / 75% of the file.
- 0.67% of words in the second half are new.

## 3. Retrieval experts against the complete coder (step 4)

Method: the expert's distribution p_R is mixed with the **final coder's** probability q:
q′ = (1−α)·q + α·p_R. The weights come from an online Bayesian mixture over a fixed α grid, per confidence bucket,
updated only after each symbol. This is exactly the marginal gain after cmix and SSE. Insertion into memory is strictly
after decoding.

| Expert (key type) | Slice A (start of stream) | Slice B (article 30,000 on) |
|---|---|---|
| Neural cache: final int8 transformer state, 16K-position window, top-64 cosine, τ=0.02 | **−0.045%** (193,244 → 193,157) | **−0.084%** (427,021 → 426,663) |
| Exact byte context, N = 6 / 24, count-based continuation distribution | +0.001% | +0.000% |

- The neural cache predicts the actual token with mean probability 0.77 on slice A and 0.55 on slice B. It is still
  almost entirely redundant with cmix's match models and the transformer's own attention.
- Its search (16K × 192 multiply-adds per token) would cost about half the transformer's compute. **Not worth
  implementing.**
- Exact-context retrieval is what cmix's match models already do; the mixture correctly gives it no weight.
- An earlier run of this evaluator reported −0.22%. That was a float32 accumulation bug (NumPy 2 promotion), found
  and fixed; the corrected numbers are above.

## 4. Compression-aware QAT (step 5)

Objective: J = CE_bits + λ · 2 · L_W / T, where L_W is a soft-assignment surrogate of −log₂ r(q) over the 15 int4
levels, with r the current level histogram (stop-gradient) and the bf16 row scales passed straight through.

Setup:
- Adam, lr 1e-5, 4 × 32K-token micro-batches per step.
- Training articles: tokens [0, 150M). Evaluation: 479 articles in [150M, 198M), not used by the continuation.
- Measured T4 training throughput: ~11,800 tokens/s per GPU.

| Run | Step | Weight entropy (bits/weight) | Weights, 2 copies | Eval bits/token |
|---|---|---|---|---|
| Start | 0 | 3.786 | 5,554,880 | 1.5103 |
| λ=0 (control) | 100 | 3.796 | 5,569,652 | 1.5465 (+2.4%) |
| λ=30 | 100 | 3.677 | 5,395,051 | 1.5721 (+4.1%) |
| λ=30 | 200 | 3.586 | 5,261,637 | 1.5851 (+4.9%) |

**Reading:**
- Restarting optimisation on this converged model costs +2.4% by itself: the model drifts toward the training subset.
- Beyond that, the rate term bought −0.119 bits/weight (≈ −175 KB over both copies) for another +1.7% loss
  (≈ +1.6 MB of payload). That is roughly 9× worse than break-even.
- The expert's MDL argument still stands for a *full* retrain (the pending entries retrained from scratch). It can't be
  realised as a short continuation, and a full retrain needs both much more GPU time and PPMD priors for the whole
  stream (we have 34%).
- One correction to my round-5 note: post-training re-quantisation is also very damaging (+11% loss for a 5% scale
  change).

## 5. Structural experts (step 6, stream-preserving)

The expert proposed "virtual replay": code a field through a new channel, then replay the original bytes so the
transformer stays in its training distribution. I implemented the same goal more simply:
- The coded stream is **not changed at all**.
- A decoder-causal C++ module (`structx.h`) parses the already-decoded post-WRT bytes. At chosen positions it
  publishes a full next-byte distribution as one extra mixer input.
- One extra layer-0 mixer has its weight set selected by expert kind × confidence × bit position.
- The transformer, PPMD and every other model see exactly the original bytes.
- Zero side information.

| Expert | Prediction | Standalone check on real data |
|---|---|---|
| Timestamp from revision id | Interpolation over earlier (revision id → time) pairs; exact digit probabilities from a 3-component Laplace mixture, conditioned on log₂ of the time gap between the bracketing records (16 contexts, online EM); grammar-valid escape | 5.35 bits/timestamp on the first 100K records (current system pays 10.32). Ids of revisions imported in 2005 carry old timestamps, so the late records are harder; gap conditioning handles this. |
| Contributor id from username | Definition once, then copy | 139 bytes for 1,121,627 predicted bytes over the whole stream |
| Interlanguage title copy | Copy of the owning article's WRT title | Owner list rebuilt in-stream; **byte-identical to an independent Python reference** (93,707 owners, 93,700 blocks) |
| Username from time-neighbour | Username of the nearest-in-time earlier record; confidence per time-gap bucket | Active on 807K bytes |

**Full-region A/B with the transformer:**
- Each region is coded in one piece, with cold-start PPMD priors and GPU transformer probabilities.
- Same binary; `LAB_SX=0` gives an identical topology with a neutral input.

**Whole revision-record region** (15,717,594 bytes, 243,425 records; fxcm_v26 build; transformer probabilities;
cold-start PPMD priors):

| Configuration | Coded size | CPU time |
|---|---|---|
| Experts off (`LAB_SX=0`) | 1,521,604 | 4,662 s |
| Timestamp + contributor-id experts on | **1,411,658 (−109,946, −7.23%)** | 4,680 s |

Attribution from the per-byte cost dumps:

| Field | Off (bits/line) | On (bits/line) | Change |
|---|---|---|---|
| Timestamp | 12.66 | 9.05 | −109,780 B |
| Contributor id | — | — | −307 B (cmix already codes known users' ids almost for free) |
| Every other field | — | — | within ±78 B (nothing got worse) |

The mixed result (9.05 bits) beats both the baseline (12.66) and the expert alone (12.87).

Timestamp gain by record range:

| Records | Bits per timestamp, off → on |
|---|---|
| 0–50K | 10.5 → 5.9 |
| 50–100K | 10.1 → 4.5 |
| 100–150K | 12.2 → 7.6 |
| 150–200K | 15.3 → 13.3 |
| 200–243K | 15.6 → 14.7 |

The last two ranges are mostly redirect articles whose last revisions were imported in 2005 with old timestamps, so the
revision-id→time relation does not hold there.

**Username expert added** (full region, same method; `lexSX2` build):

| Configuration | Coded size |
|---|---|
| Timestamp + contributor id | 1,411,658 |
| + username from the nearest-in-time earlier record | **1,408,301 (−3,357)** |

- Attribution: username 243,781 → 240,370 B (9.50 → 9.36 bits/line).
- Every other field moved by ±27 B or less.
- Small, because cmix already exploits a user repeating within the last few records. The expert only adds the
  time-neighbour relation.

**Two-centre timestamp model rejected** (`lexSX3`):
- In stream order, 26–39% of the late records are within 1 hour of the previous record. This version therefore adds
  the previous record's time as a second Laplace centre (responsibility-weighted online EM, posterior weight per gap
  context).
- Standalone, it cut the timestamp expert's own cost from 391,618 to 336,295 bytes.
- **In the full system it was 1,088 bytes worse** (1,409,389 vs 1,408,301). The timestamp field rose by 1,079 B and
  nothing else moved.
- Reason: the previous record's timestamp sits about 60 bytes back in cmix's own context, so cmix already uses
  "close to the previous record". The second centre only made the revision-id centre less sharp.
- **The final version is therefore the single-centre one (v2).** v3 is kept as `structx_v3.h`.

**Whole interlanguage region** (15,873,956 bytes, 93,700 blocks; owner titles as the in-stream parser produces them;
same binary, `LAB_SX=0` off):

| Configuration | Coded size | CPU time |
|---|---|---|
| Experts off | 1,510,303 | 4,846 s |
| Owner-title copy on | **1,348,777 (−161,526, −10.69%)** | 4,363 s |

The CPU difference comes from different machine load during the two runs; the expert itself is a string compare.
This is twice the round-5 cmix-only extrapolation (~76 KB). The transformer resets per article and never sees the
owner's title next to its interlanguage block, so the copy is new information for the whole system, not only for cmix.

**Caveat on all region A/Bs:** each region is coded alone, so PPMD, cmix and the transformer start cold. In the full
file, cmix's word and dictionary models will already know the title words. The interwiki gain may therefore be
somewhat smaller there. The timestamp gain is information cmix cannot obtain any other way.

### 5c. Further experts screened against the final coder (all rejected)

Each idea was first scored the way section 3 scores retrieval: the expert's probability of the actual symbol is mixed
with the **final coder's** probability (per-byte cost dumps), using an online Bayesian mixture over an α grid.

| Idea | Why it looked promising | Result against the final coder |
|---|---|---|
| Page id from title order (early page ids were assigned roughly alphabetically) | Page-id deltas cost 251 KB | Title-neighbour interpolation costs 17.9 bits/page vs 8.5 for a plain delta model: no relation at this scale |
| Page id → timestamp, as a third centre for the late records (single-revision pages: last edit = creation) | Late records cost 14–16 bits/timestamp | Interpolation error ≈ 2^20–2^25 s, worse than the previous record. No signal. |
| Revision id from article features already decoded: length, redirect flag, **latest year mentioned in the text** | Standalone, the year cut the revision id's top bits from 8.34 to 7.05 bits/record (−39 KB) | **−354 B.** Over the whole region the coder pays only 15.57 bits/revision id (the 22.35 measured earlier was the first 100K records only); bot runs make the low digits predictable from neighbouring records |
| Link-target expert: a trie of decoded titles and earlier link targets, predicting bytes inside `[[…]]` | Link targets are 53% of slice A's coded bytes | **+30 B (slice A), +25 B (slice B, 630K prior strings).** The transformer + cmix already code them at 0.25–2 bits/byte, and the mixture gives the trie no weight even when one candidate remains |
| Two-centre timestamp (above) | −55 KB standalone | +1,088 B in the full system |

Lesson: three of these five looked large in isolation. Building an expert is only worthwhile after it has been scored
against the final coder's own costs.

**Compared with the round-5 text transform:**
- The transform reached −114 KB, but it changed the stream and pushed the transformer out of distribution (its loss
  on the records rose from 0.70 to 0.86 nats).
- The expert gets the same gain with the stream untouched, zero side data, and no line-count constraint.
- Full virtual replay (coding the timestamp first, then replaying the original bytes) would carry the same information
  as this order-preserving expert. The two directions measured almost the same:
  - revision id given timestamp: 6.13 bits with cmix;
  - timestamp given revision id: 5.35 bits standalone.

  So virtual replay was not needed here.

## 6. Correctness checks performed

- **Structural experts, end to end (production mode).** A self-consistent mini-stream:
  - contents: the first 400 articles, the original tail header, their 400 revision records and the interlanguage
    blocks of their 399 owners;
  - no lab side files, so the owners come from the in-stream article parser, as in a real run;
  - all four experts active (timestamp 4,210 bytes, contributor id 1,952, interwiki 58,888, username 3,188), final
    block index = owner count = 399;
  - real C++ transformer: 462,360 → 26,359 bytes → decompressed in a separate process **byte-identically**;
  - repeated for the rejected v3: 26,366 bytes, also identical.
- **Earlier round trip** (lab owners file): 1.6 MB of real tail bytes → 119,456 bytes → identical.
- **Final candidate binary** (`cand_final2/run/cmix`, 3,369,451 bytes) run on enwik9 in a fresh directory:
  - it self-extracts a dictionary and article order identical to the reference (md5 b3a9cf9f…, 68fa9a4f…);
  - it reproduces the reference token stream and article boundaries byte for byte (md5 f6cf44af…, 852b8136…);
  - 9 min.
- **Expert distributions** normalised to within 1.1e-14 at every active position.
- **Parser equivalence.** The in-stream owner parser over the full 586 MB stream equals the Python reference.
- **Round-5 transforms** (revision residual, title copy): exact round trip on the full 932 MB main part; line count
  preserved (13,146,906).
- **bf16 weight container:** Python round trip bit-exact; C++ loader verified; loss +0.0036% on 20M tokens.
- **UPX-LZMA binary:** `upx -t` passes; compressed output identical to the unpacked binary.

## 7. What remains open

- Full-file compression and independent decompression of the final candidate (`cand_final2`, S1 = 3,369,451). This
  is the decisive test and needs a dedicated machine for ~4 days. It would also replace the cold-start region numbers
  with warm ones.
- A lexth11c-based core. Its `payload_lex` already time-sorts the revision records (paying ~347 KB of side data). The
  timestamp expert would compete with that transform, so it must be re-measured there. The interwiki expert
  (−161.5 KB, the largest single gain this round) and the username expert should transfer directly.
  - If they transfer unchanged, lexth11c would land near 99.15 MB.
  - That beats the pending entries, but not by 1% of them (98.32 MB would be needed).
- Compression-aware *retraining* from scratch on the full stream (beyond this compute).
- Representation and title-pass studies (step 7).

## 8. Files

- Report: this file.
- Code: `round6/` next to it.
  - `structx.h`, `sxpatch.py`: structural experts (final v2) and predictor integration.
  - `structx_v3.h` (rejected two-centre timestamp), `structx_v1.h` (first version).
  - `sx_test.cpp`: standalone tests.
  - `rtpatch.py`, `roundtrip.sh`: lab decompression and round trip.
  - `mk_mini.py`, `roundtrip2.sh`, `rt2_go.sh`: production-mode mini-stream round trip.
  - `build_candidate2.sh`, `cand_check2.sh`: final candidate build and self-extraction check.
  - `pid_eval.py`, `ts_pid.py`, `rid_eval.py`, `rid2.py`, `lt_eval.py`: the rejected expert screens of 5c.
  - `cache_eval.py`, `ctx_eval.py`: retrieval evaluation against the final coder.
  - `qat_rate.py`, `qat_pkg.py`: MDL QAT and package-cost evaluation.
  - `vocab_sat.py`, plus all round-5 tools.
- Kaggle:
  - logs in `/kaggle/working/hp_round5/`, `/kaggle/working/hp_round6/` and `/root/hp/results/`;
  - final candidate in `/root/hp/cand_final2/run/`.
- **Nothing was deleted** from `/kaggle/working`. New builds went into new directories (`cand_final2`, `cand_check2`,
  `rtSX2`, `rtSX3`) instead of overwriting the old ones.
