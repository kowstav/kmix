# Registered CPU continuation: component removals and output precision

8 October 2026, before these candidate binaries or quality results exist.

The finite objective is a measured payload/CPU/RAM Pareto comparison, not a claim
that all 96 idea families are exhausted. Four notebooks, four independent process
lanes per notebook. The fifth available committed slot is reserved for repaired
article-order testing. All jobs are private CPU-only; paid spending stays zero.

| Notebook | Candidate(s), each against matched neutral build |
|---|---|
| native-prune-word | Omit AddWord model construction and its dynamically sized prediction/update loops |
| native-prune-match | Omit AddMatch construction and updates; its derived contexts consequently change |
| native-prune-indirect | Omit AddDoubleIndirect construction and updates |
| native-precision | Preserve native PPMd prior rounding, but omit only transformer output float32→half→float32 rounding; retain existing probability floor |

These are controlled family removals, not pure isolation of one arithmetic
kernel: the adaptive mixers must relearn with fewer inputs and some derived
contexts change. Report that interaction rather than calling the differences
intrinsic standalone model value. No model or dictionary changes, no retraining.

Source base: the independently verified round-13 native source archive, SHA-256
9a593b335861569a7c720df0e8e76d85715deb971588b003a714d181e2b42662.
Use the same Clang/LLD 17, common flags and transformer flags as round 13; compile
the final-head mode as neutral. Keep the patched tree and every binary separate
from the preserved source. Archive source hashes, full commands, sizes and logs.

Gate before committing long work: a neutral rebuild and pinned coder must emit
identical archives and Q16 trajectories on 16 KiB, independently decode, and
every candidate must independently decode the same input. A failed gate prevents
submission. This is stronger than successful compilation and small Python tests.

Each notebook tests the existing development regions 0,2,4,6, 3 MiB apiece,
2 MiB warmup then 1 MiB scored. Rotate baseline/candidate order across regions;
pin one sequential region-pair process per CPU ID. Score all bits, actual complete
archive bytes, warm-only logloss, encode/decode user+system CPU and peak RSS.
Do not pool the three overlapping warm subwindows as independent samples.
The full 3 MiB archive includes a reset transient; warm costs exclude it.

Promotion rules fixed now:

- A smaller actual archive on development is eligible for separate confirmation;
  it is not a package win until code multiplicity, full-history time/RAM qualify.
- A pruned arm losing bits can remain a compute candidate only if it reduces
  measured encode and decode CPU and frees a relevant resource. Record the exact
  tradeoff (additional warm bits per saved CPU-second); no assumed future neural
  gain may turn it into a present compression win.
- Compare dimensions using domination, not an invented scalar exchange rate.
  Four regions support a finite screen, not a population equivalence claim.
- Only development survivors are evaluated on frozen confirmation regions and
  combined with the already selected guard. Combinations require measured gains;
  adding individual improvements is invalid.

The output-precision intervention changes downstream native mixing only. The
PPMd input half format and trained transformer recurrence remain unchanged.
Distribution traces must not be advertised as fp32 if the legacy half writer
was requested; reject that debug option in this arm rather than emit stale rows.
The existing half-tail decoding quirk is deliberately preserved in this arm so
that precision and prior fixes are not confounded.

All workers enforce the existing 10.3-hour notebook budget. Full-file global
history remains a separate 55–60-hour production-host or exact-checkpoint task;
regional resets are never relabelled as global warm snapshots.
