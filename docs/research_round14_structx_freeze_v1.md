# P4 lexical structural experts: frozen protocol v1 (10 October 2026)

Implements PENDING_EXPERIMENTS_HANDOFF.md §P4 on the lexical coder.

## Provenance

The round-6 implementation was located and hashed before porting:
`research_round7_sources/structx.h` (SHA-256 `3470b9e7…`, 455 lines) and its integration
`research_round7_sources/sxpatch.py` (`6b67e97d…`). Their 274,829 B gain belongs to the
older FX2 pipeline and cold structural regions, not to this coder.

New files:
- `hutter_research/structx_lex.h` — parser and four experts;
- `structx_lex_patch.py` — predictor integration; every insertion is under
  `#if HP_R14_STRUCTX`;
- `structx_lex_scan.cpp` — standalone causal scanner;
- `cpu_round14_structx.py` — job harness;
- `research_round14_p4_alignment_check.py` — independent re-serialization check.

## Mechanism (unchanged from round 6 except as stated)

The parser is decoder-synchronous and sees only already-coded bytes of the transformed
stream. It tracks:
- dictionary escape and code grammar (0x0C escape; 1-, 2- and 3-byte codes; case markers
  0x40/0x07/0x06);
- page/title boundaries (`  L\xdf\x98N\n    L\xdf\x9bN` … `L/\xdf\x9bN`);
- the PHDA9 tail record grammar;
- interlanguage blocks.

Any grammar violation makes the rest of that line neutral. The four mechanism-backed
experts and their keys:

| Expert | Predicts | Key |
|---|---|---|
| TS | timestamp | revision id; interpolation, 3-component Laplace mixture per gap bucket, 2e-3 grammar escape |
| UID | contributor id | username, from the last id seen with it |
| USER | username | nearest-in-time earlier record |
| IW | interlanguage title | the owning article's already-reconstructed title |

Copy distributions put p = (hits + 0.5)/(tries + 1) on the expected byte and spread 1 − p
uniformly over the other vocabulary bytes. Byte-to-bit conversion is exact and clamped to
[1e-4, 1 − 1e-4]. Updates happen once per completed byte, after coding. The native layer-0
mixer, keyed by (kind × confidence × bit position), learns the weight online after each
bit. That weight plays the role of the prefix-visible α. Stores are bounded at 262,144
entries with FIFO eviction; regional RSS is measured.

## Modes (`HP_R14_STRUCTX`)

| Mode | Build | SHA |
|---|---|---|
| 0 | pinned neutral, byte-identical binary to R14 neutral | `30b539b3…` |
| 1 | topology-matched neutral expert (extra input 0.5, extra mixer context 0) | — |
| 2 | joint predictor (true keys) | — |
| 3 | wrong-key control | — |

Mode 3's wrong keys: TS uses revision id − 1,000,000; UID uses the previous record's
username; USER uses time − 7 days; IW uses the previous block's owner. The direct field
predictor (expert alone) comes from the standalone scanner.

## Regions (fixed rule, before any native result)

The tails are found by rule on `lexical_full_ready.wrt` (SHA `7826ff63…`):
- revision tail: 554,867,470–570,585,365;
- interlanguage tail: 570,585,365–586,453,046.

Each tail gets four non-overlapping 3 MiB windows (2 MiB warmup, last 1 MiB scored), each
starting at a line start: region ids 0–3 in the revision tail, 4–7 in the interlanguage
tail. Earlier record blocks are development (k = 0, 1 → ids 0, 1, 4, 5); later blocks are
confirmation (k = 2, 3 → ids 2, 3, 6, 7). Every regional history resets at region start;
both arms get the same history.

Interlanguage regions receive, through lab-only `LAB_IW_OWNERS` / `LAB_IW_BLOCK0`, the
owner list and block index the causal parser held at that offset over the preceding
stream. A full-stream decoder would build these itself. Encoder and decoder read the same
file. This is a regional emulation of matched preceding history, not a production archive.

## Gate before any commit

1. Mode 0 builds byte-identical to the pinned neutral.
2. Exact cursor alignment of every parser record against the independent
   re-serialization of the whole tail.
3. Deterministic, crash-free FSM on 4 MiB of arbitrary byte/escape tails.
4. Exact native inverses for modes 1–3 on 16 KiB of a revision region, an interlanguage
   region (with owners) and a synthetic arbitrary byte/escape tail.

## Development jobs (four pinned lanes each, 10.3 h deadline, no GPU, $0)

- **D-A**: modes {1, 2} × regions {0, 1, 4, 5} — joint vs topology-matched neutral, same host.
- **D-B**: modes {3, 0} × regions {0, 1, 4, 5} — wrong-key control and pinned neutral.

Bytes are compared across D-A/D-B: archives are deterministic and host-independent. CPU
is compared only inside one notebook.

## Measures and analysis

- Actual archive bytes;
- warm (last 1 MiB) and all-target ideal bytes;
- encode/decode CPU and RSS;
- per-region rows;
- the direct field predictor's standalone cost on the same windows.

Comparisons:
- expert benefit = B(mode 1) − B(mode 2);
- topology cost = B(mode 0) − B(mode 1);
- control = B(mode 1) − B(mode 3).

Four development clusters: descriptive only, no interval. Fields are never selected after
confirmation is opened.

## Confirmation (after development)

The same frozen binaries and modes {1, 2, 3} on regions {2, 3, 6, 7}. No rate, store,
feature or threshold changes; any change is a new model. Infobox/schema extensions are a
later, separately priced design.
