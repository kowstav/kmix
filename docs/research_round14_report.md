# Round 14: completed CPU evidence and current shortlist

Updated 9 October 2026. This integrates the completed round-13/14 jobs, including
independent full-container reconstruction, rather than treating old RUNNING labels
as current state. Current new-session work is recorded in the continuation checkpoint.
Paid spend remains $0. No GPU training occurred in this round.

## Outcome that is actually established

The development-selected integer final-coder guard saves **2,587 actual bytes**
against **4,491,669 baseline archive bytes** across eight independently decoded
3 MiB confirmation regions (0.0576% of those regional payloads).
Every candidate reconstructs its original bytes. The last 1 MiB of each region,
after 2 MiB matched warmup, saves **415.558 ideal bytes in aggregate**.
The archive total includes reset transients; the warm-only number must not be
confused with that total. This is a small measured improvement, not 20%, a
record, a full-history result or a complete-package win.

Four complete 1 GB raw-text proxy archives also independently reconstruct the
original corpus. The constructor/right-context channel has a reproducible narrow
signal, but its complete factorized codec loses against stronger baselines.
Exact grouped model storage does not improve the original model's byte count.

## Native confirmation: actual archives and the warm distinction

| Region | Canonical start | Whole 3 MiB archive saving, B | Last 1 MiB ideal saving, B |
|---|---:|---:|---:|
| 8 | 64,000,000 | 328 | 51.668 |
| 9 | 128,000,000 | 318 | 54.440 |
| 10 | 192,000,000 | 317 | 38.469 |
| 11 | 256,000,000 | 351 | 59.685 |
| 12 | 320,000,000 | 300 | 45.539 |
| 13 | 384,000,000 | 337 | 48.291 |
| 14 | 448,000,000 | 310 | 55.526 |
| 15 | 544,000,000 | 326 | 61.941 |

The law was frozen from eight development regions before confirmation quality
was opened. The native integration uses the same eight confirmation regions as
the earlier replay; this verifies coding, not eight additional independent
samples. Each region resets both models at its start, so these are regional
histories, not global snapshots. Eight clusters are below the statistical
contract's ten-cluster bootstrap gate. Deterministic spacing also does not itself
justify a population confidence interval.

Earlier development-native tests saved 1,257 B across four separate 3 MiB archives.
Neutral rebuilds matched the pinned archive and every Q16 probability exactly.
The append-only fixed hidden-memory extension did not beat its matched neutral
extension on confirmation (-0.392 ideal B). This does not test learned TTL,
learned eviction, nonlinear attention or an optimized retrieval architecture.

The guard laboratory executable is 732,320 B versus the pinned 497,104 B.
Those are raw ELF sizes, not production package costs: the historical package
used UPX-packed executables. The 9 October packing experiment measured 232,008 B
for that guard and 209,568 B for its matched lab neutral. Exact integer-table
storage engineering reduces the guard to 218,608 B, pending native parity.
That is 13,400 B saved per guard copy, but still 9,040 B above lab neutral and
20,372 B above the historical 198,236 B production executable. An illustrative
stationary extrapolation of the warm-only gain is only about 29 KB for the corpus.
Neither stationarity nor a complete production package is qualified. Do not
subtract raw executable sizes from a package containing packed executables.

## All 608 constructor/conditional-bag cases

Thirty-two disjoint, spread 1 MiB original-text regions, fixed seed 1400831,
sixteen development and sixteen confirmation. Nineteen complete codec arms per
region: Markov, paid coarse-right, uniform multiset order, and sixteen conditional
bag variants crossing left/right/wrong/Markov contexts, beta 0/1 and alpha 1/4.
All 608 paid archives independently reconstruct their exact bytes, including
layout, punctuation, case and literal/OOV data. No correction stream is omitted.

The development-frozen overall choice is coarse_right:4. Its confirmation size
is **5,902,282 B**, versus **5,911,723 B** for the matched Markov factorization:
**9,441 B saved**. However, complete gzip is **5,430,102 B** and zstd is
**4,865,282 B** on those identical regions. The factorization loses **472,180 B**
to gzip and **1,037,000 B** to zstd. It remains a raw-text proxy, not lexth11c.

The development-frozen conditional-bag choice is bag_left1:4. Its confirmation
size is **6,173,417 B**, losing **11,143 B** to the uniform paid bag (6,162,274 B)
and **271,135 B** to coarse-right. This closes the declared finite conditional
count/smoothing sweep; it does not prove that learned grammar or all bag
descendants cannot work. Direct right-context prediction earns a mechanism-level
shortlist; the current paid-bag codec does not earn deployment priority.

Selections, all arm totals and region effects are in
research_round14_constructor_analysis_v1.json. The freeze timestamp and input
manifest hash are preserved separately in constructor_selection_v1.json.

## Complete original-corpus check

| Codec, matched 4 MiB chunk boundaries | Actual framed archive bytes |
|---|---:|
| gzip | 323,066,249 |
| zstd | 278,574,861 |
| direct constructor Markov | 350,344,017 |
| paid coarse-right, alpha 1 | 349,939,776 |

Each container covers exactly 1,000,000,000 original bytes in 239 chunks. A second
decoder parsed the actual serialized frames, offsets, lengths and hashes, then
reconstructed all four whole files to SHA-256
159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.
Coarse-right saves 404,241 B against the matched factorization, while both lose
substantially to zstd. This full-file alpha-1 protocol was fixed before the
later alpha-4 regional selection; it is not falsely called an exact evaluation
of that later selected arm. It is not a native-coder/package comparison.

## Which words consume native bits?

The corrected scanner independently matches the original WRT decoder at every
decoded character and atom boundary while scanning from the start. It labels
sixteen 1 MiB warm scoring intervals and attributes already measured native
final-coder costs. All bits are accounted for once, including unlabelled bytes.
116,564 word types appear in these scored body spans. The labels and full-corpus
frequency census are offline diagnostics, never free decoder inputs.

| Category | Coded bytes | Native bits | Share of all scored bits |
|---|---:|---:|---:|
| body constructor | 1,536,396 | 3,651,684.7 | 15.55% |
| body dictionary other | 5,135,662 | 11,800,977.9 | 50.27% |
| body literal or oov | 1,774,154 | 3,153,851.6 | 13.43% |
| metadata word | 638,460 | 607,562.6 | 2.59% |
| nonword or unlabelled | 7,692,544 | 4,262,212.1 | 18.16% |

Constructor words are cheap per event but frequent: `the`, `in`, `a`, `and`,
`of` lead cumulative word-attributed cost. Examples with high mean cost and at
least 32 observed events include `simultaneous`, `accompanying`, `quasi` and
`presently`. The ranking is a description of these intervals, not a claim that
teaching those isolated strings will remove their context-dependent entropy.

| Offline corpus rarity threshold | Body-word events | Attributed coded bytes | Share of all scored native bits |
|---|---:|---:|---:|
| count < 2 | 17,427 | 154,762 | 1.97% |
| count < 16 | 75,370 | 611,493 | 5.92% |
| count < 64 | 143,136 | 1,065,122 | 9.29% |
| count < 107 | 181,805 | 1,275,182 | 10.92% |
| count < 128 | 196,584 | 1,347,783 | 11.53% |
| count < 1024 | 489,861 | 2,450,917 | 22.24% |
| count < 1392 | 552,434 | 2,660,826 | 24.44% |
| count < 8372 | 1,114,908 | 4,180,039 | 41.83% |

For example, count < 107 covers about 10.92% of these native bits, not most
compression cost. Removing those training targets does not remove their archive
cost. The other dictionary words account for about 50.27% of bits. A balanced
GPU pilot should measure common/rare gradient interference and total native
codelength; frequency-only masking has no demonstrated advantage yet.

The worker's first version failed on `index` versus the saved `id` field before
scoring. Version 2 checks the full 16-ID manifest contract and completed. Its
failure manifest is preserved and is not negative scientific evidence.

## Exact model-storage descendants

Eighteen whole-model representation-aware arms completed, with original stored
dtypes and exact regeneration of omitted RoPE arrays. Best: 3,030,415 B, versus
the original 2,978,039 B. The later grouped sweep evaluates eighteen actual inner
codec alternatives per group, 454 groups across four fixed partitions:

| Partition | Groups | Actual complete container bytes | Saving per copy versus original, B |
|---|---:|---:|---:|
| whole | 1 | 3,030,505 | -52,466 |
| dtype | 4 | 2,999,272 | -21,233 |
| layer | 16 | 3,032,797 | -54,758 |
| tensor | 433 | 3,070,543 | -92,504 |

All 435 tensors match bit for bit, including an independent native C++ reader
dump. Per-group minima are exact within those fixed, independent framing choices;
that finite optimum does not imply optimal quantization, model training or all
possible codecs. Best grouped result still loses 21,233 B per copy before code.

## Four-core execution and limits

| Work | Worker CPU seconds | Elapsed wall seconds | Average occupied CPU cores |
|---|---:|---:|---:|
| Constructor development, 304 cases | 6,916.9 | 1,765.1 | 3.919 |
| Constructor confirmation, 304 cases | 7,098.0 | 1,801.3 | 3.940 |
| Native confirmation A, 4 paired regions | 75,644.4 | 19,357.9 | 3.908 |
| Native confirmation B, 4 paired regions | 63,528.5 | 16,806.9 | 3.780 |
| Hard-word alignment, 16 windows | 1,957.8 | 785.9 | 2.491 |

R13 full-corpus encode/decode used 3.923 cores on average; R14 independent
serialized reconstruction used about 3.879. The grouped storage job and global
word scanner have setup/tail imbalance; their averages must not be rounded up
to four. Word scanning uses four global-prefix shards of different lengths,
which explains its 2.491-core average. These are four logical CPU lanes, not a
claim of four physical cores or guaranteed fourfold speedup.

The observed Kaggle account limit was five concurrent committed CPU notebooks,
plus the live session. A sixth push was rejected. It was later submitted only
after ordinary slots became free; no quota bypass occurred.

## Completed native component and output-precision wave

All four development notebooks completed, using four matched 3 MiB regions each
and separate native inverses. All 32 archives reconstruct exactly. Across all
hosts, neutral archives and Q16 probability hashes agree for the same region.

| Candidate | Whole-archive saving, B | Last-1-MiB aggregate saving, ideal B | Encode CPU reduction | Decode CPU reduction |
|---|---:|---:|---:|---:|
| Remove word group | -153 | -73.649 | 9.49% | 1.82% |
| Remove match group | -2 | -5.737 | 4.63% | 4.88% |
| Remove double-indirect group | +19 | +7.416 | 3.32% | -0.012% |
| Omit final output FP16 rounding | +7 | +3.438 | 0.96% | 1.62% |

All four baselines total 2,277,259 archive bytes per comparison. These are finite
development effects, not a statistically qualified speed/compression improvement.
The match removal saves roughly 24 MiB of regional peak RAM per run; word removal
saves roughly 42 MiB. RSS is not summed across serial regions. Effective use is
3.75–3.94 CPU cores. Regional CPU signs and magnitudes vary; matched A/B/B/A
repeats are specified before making production speed claims.

Four independent confirmation-A notebooks were submitted at 11:49 UTC on 9 October.
B notebooks are frozen/prepared, not submitted. A/B jointly cover IDs 8–15 with
the same binaries and four pinned workers per notebook. Protocol and source hash
are in research_round14_confirmation_freeze_v1.md and prepared_confirm_v5.json.
These follow-ups retain resource trades rather than pretending small bit penalties
are compression gains. No combination gain has been assumed.

## Repaired article-order sweep and preserved failures

The PPMd article-order commit failed on real-data inverse checks despite passing
tiny preflight tests. Its partial archives are not promoted to complete results.
A standalone reproduction failed on three of sixteen real-data cases, including
direct library encode/decode without our outer container. Both simple and bounded
decode failed. This isolates a backend/data issue, not an ordering quality loss;
the exact upstream root cause is not established. A new native PPMd-H backend
passed all three failing inputs and the complete paid-container stress tests.
The new HPOR14H0 version then completed all 160 planned cases with exact inverses.
Live preflight used p7zip 16.02; the committed image used 7-Zip 23.01. Both identities
are recorded; no cross-backend sizes were mixed into the measured comparison.

The graph was frozen from eight development regions before eight confirmation
regions were evaluated. The selected rare-word graph loses 1,594 B at order 8
(991,762 versus 990,168 B) and 1,577 B at order 16 (979,161 versus 977,584 B).
The direct conditional-PPMd graph also loses on confirmation and is not retroactively
selected instead. This closes the declared finite paid-graph proxy sweep, not
the family of all article-order methods. It does not transfer a negative result
to the canonical native transformer without an actual native test.

Five new native binaries are built: neutral, word-model removal, match-model
removal, double-indirect removal and full-precision transformer output. The
neutral binary SHA is identical to the previously verified neutral. The six-case
native preflight and subsequent four development commits all passed independent
decoding. The first build exposed five `.hpp` files omitted by the
old source-bundle filter. They were restored from the preserved original tree,
hashed, and included in the corrected 140-entry source bundle. Original evidence
and failure logs remain intact. See research_round14_next_native_protocol.md.

On 8 October a remote action was blocked by automatic approval review's account
usage limit. It was not executed or bypassed. The user supplied a new session on
9 October; ordinary review authorized reconnection. The separate managed Goal
was not resumed or replaced. CPU experiments cannot be described as completed
merely because their build or plan exists.

## Preservation, deletion and coverage

The four new local result bundles have verified ZIP CRCs and all 1,298 entry
hashes (996 + 218 + 47 + 37). Four detailed model/native/warm-cost bundles are
also SHA/entry verified locally. The Kaggle CLI retrieved only its first 500
output entries: paginated recovery obtained all 609 listed files per constructor
job, including the missing manifests, without rerunning the experiments.

Deleted earlier in R14: one redundant 75,327,948 B aggregate ZIP after its identical
local copy was verified; four duplicate 101,187,584 B decoder hidden traces after
SHA comparison with retained encoder-side originals. Total 480,078,284 B.
Exact paths, hashes and reasons are in research_round14_pull_manifest.json and
research_round14_detail_preservation.json. No data/model/unique source was deleted.
No original data/model/unique source was deleted on 9 October. The article-order
codec automatically removed 12,608 newly generated temporary 7z files totaling
61,324,909 B, plus 70 preflight scratch files (1,288,112 B); final archives remain.

The completed native/article wave adds 310 locally CRC/SHA-verified entries,
including all 32 native and 160 article-order archives. The 15-entry failure bundle
and ten-entry native CPU asset bundle are also verified. Some large Q16 traces
remain only in the immutable private notebook outputs. Details and next-agent
commands are in PENDING_EXPERIMENTS_HANDOFF.md.

All 96 ideas retain their individual history and stronger-test requirements.
Many learned architectures and CPU descendants remain unimplemented. Finite
experiments cannot certify that every possible descendant can never work, nor
that each idea received the maturity of decades of transformer research.
The coverage delta and shortlist explicitly distinguish tested mechanisms,
historical hints, pending implementations and GPU-only proposals.


## 9 October 17:36 UTC: confirmed A-wave and joint development

Four component A notebooks completed on IDs 8,10,12,14; their 32 native archives
invert exactly, and baseline Q16/archive hashes match the earlier pinned native
confirmation. Whole-archive / warm ideal signed savings:

| Arm | Actual saving B | Warm ideal saving B |
|---|---:|---:|
| Word pruning | -89 | -51.495 |
| Match pruning | -50 | -18.133 |
| Indirect pruning | -24 | -0.760 |
| Output FP32 | +4 | +2.371 |

Effective CPU use was 3.855–3.920 cores. CPU timing varies and some signs reverse;
development speed estimates are not established deployment gains. All four B
confirmation notebooks were successfully submitted; eight-region totals are pending.

Joint guard-plus-match development has eight exact archives over four pairs.
Against guard alone it adds 10 actual B and 6.745555 warm ideal B. Against native
neutral it saves 1,247 actual B and 233.362611 warm ideal B. The interaction is
-8 actual B and -1.009007 warm ideal B; individual savings are not additive.
Mean RSS reduction versus guard is approximately 24 MiB. Joint UPX executable
is 217,540 B, 1,068 B smaller than the exact packed guard. Confirmation advances
this fixed package/RAM tradeoff, not a synergy claim. Paired decode CPU fell 3.03%
but encoding was essentially unchanged; noisy regional signs require repeats.

The corrected actual 64 KiB guard storage gate passed (four guard variants plus
16 KiB neutral), with identical probability/archive hashes and exact independent
inverses. The false 64 KiB label from the earlier truncated test remains explicitly
corrected and preserved. Exact implementation size savings are now transferable
on the tested trajectory; full-stream CPU/RAM and full-package gain are unqualified.

Evidence: `research_round14_confirm_a_joint_analysis_v1.json`, 132-entry A bundle,
33-entry joint bundle, seven-entry gate receipt bundle; all locally SHA/CRC verified.
Current pending procedures: `PENDING_EXPERIMENTS_HANDOFF.md`. $0 spent, no GPU.
