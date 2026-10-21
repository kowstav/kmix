# Joint guard timing repeat (G vs GM, A/B/B/A): frozen protocol, 10 October 2026

Trigger, from `research_round14_guard_match_confirmation_freeze.md`: "If timing remains
inconsistent, record it as unresolved and use counterbalanced A/B/B/A repeats before any
deployment speed claim." After both joint confirmation waves
(`research_round14_joint_confirmation_analysis_v3.json`), G−GM CPU over eight regions has
disagreeing signs (encode 5+/3−, decode 4+/4−), |mean| below one paired SD
(encode 97 ± 618 s, decode 93 ± 538 s) and within-notebook position effects up to 805 s.
Timing is therefore recorded as **unresolved**, and this repeat is required.

Identical registered design to `research_round14_timing_abba_freeze_v1.md`. The only
change is the binary pair: A = `guard_base` (packed16 guard, `5f6e0c7b…`), B =
`guard_match` (`0c29a8c3…`) from `chaoscpp/hutter-r14-guard-match-assets-v1`. Inputs
come from `chaoscpp/hutter-r13-four-lane-cpu-assets-v1`. Regions 8 and 9 follow the same
fixed rule (lowest region of each confirmation half). Lane tasks are (8, AB), (8, BA),
(9, AB), (9, BA). There are four pinned fork workers via `initialize_lane` with thread
variables set to 1, and every run uses the unchanged `cpu_round13_native.archive_case`.
The generalized harness is `hutter_research/cpu_round14_timing_abba_pair.py`; the frozen
v9 module is untouched.

Measured and reported exactly as in v1: encode and decode user+system CPU including
startup, wall time, peak RSS, every per-pair difference, per-region means over AB/BA,
the order-balanced mean, and the time-position effect. Results are descriptive (four
pairs; no interval) and never compared across hosts. Parity: every archive and Q16
hash must equal the joint confirmation reference for that (region, mode): region 8
from joint A, region 9 from joint B. A mismatch stops attribution. Before commit, a
live 16 KiB region-0 gate must reproduce the stored references for both binaries
(guard_base `ed0adaa8…`/`9e8174a1…`, guard_match `d5001d57…`/`275f430c…`).

Resources: one private CPU notebook, 10.3 h deadline, no GPU, no internet, $0. Submit
only into a free slot; never bypass a rejection, never duplicate, no automatic retry.
Scope: same-host relative CPU of regional runs only. No full-stream RSS, production
wall time or package claim.
