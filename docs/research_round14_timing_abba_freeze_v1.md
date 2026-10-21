# Component timing repeat (A/B/B/A): frozen protocol, 9–10 October 2026

Trigger (PENDING_EXPERIMENTS_HANDOFF.md, P1 "Timing follow-up"; confirmation freeze:
"positive aggregate timing with contradictory regional signs calls for an A/B/B/A
timing repeat on the same host before deployment claims"). Rule fixed before the B
wave was opened: an arm/phase is repeated when development proposed a CPU gain
(positive development reduction) and the eight confirmation pairs either disagree in
sign or have |mean| below one paired standard deviation. Evaluated in
`research_round14_confirm_ab_joint_a_analysis_v2.json`: all four arms qualify
(word, match and FP32 in both phases; indirect in encode, where development proposed
3.32%). No arm is selected or dropped on the basis of its timing sign.

Registered regions: **8 and 9**, the lowest-numbered region of each confirmation half,
chosen by that fixed rule before any B-wave value was read. Same 3 MiB inputs, same
2 MiB warmup convention, unchanged binaries (neutral 30b539b3…, word c2ba7d4c…,
match cf8fc836…, indirect c6aca330…, FP32 470d4f8c…) from
`chaoscpp/hutter-r14-native-cpu-assets-v1` and inputs from
`chaoscpp/hutter-r13-four-lane-cpu-assets-v1`.

Design per arm (one private CPU notebook per arm, four arms): four independent
`ProcessPoolExecutor` fork workers, one pinned CPU each via
`cpu_round13_jobs.initialize_lane`, thread variables 1. Lane tasks are
(8, AB), (8, BA), (9, AB), (9, BA): A = neutral, B = arm. Each lane runs its two
archives sequentially on its own pinned CPU, with identical process initialization,
using the unchanged `cpu_round13_native.archive_case` (separate encoder and
independent decoder processes; exact inverse; Q16 trace). Per region the two lanes
form A/B/B/A in time. Lanes have private ROOT/OUT directories so repeated labels
never collide. Every run is kept.

Measured per run: encode and decode user+system CPU of the whole child process
(startup included), wall time, peak RSS, archive and Q16 hashes. Reported: every
per-pair difference (neutral minus arm) for encode and decode separately, per-region
means over the two orders, the order-balanced mean, and the time-position effect
(second-run minus first-run CPU, averaged over AB and BA so the arm effect cancels).
Four pairs per arm are descriptive; no confidence interval is computed. CPU is never
compared across hosts: confirmation-wave absolute times are not mixed with these.

Parity: every archive and Q16 hash must equal the confirmation reference for the same
(region, mode). A mismatch marks `COMPLETE_TIMING_REFERENCE_MISMATCH_STOP_ATTRIBUTION`
and attribution stops. Before any commit, the identical code path must pass a live
16 KiB preflight on region 0 reproducing the stored native preflight archive and Q16
hashes for neutral and the arm (`PASS_16KIB_PREFLIGHT_REFERENCE_PARITY`).

Resources: 10.3-hour deadline per notebook, no GPU, no internet, private, $0, no
paid rental. Expected about 2 archives × (encode + decode) per lane, roughly 5 hours
from prior timings (planning observation only). Five concurrent committed CPU slots
are the observed account limit: submit only into free slots, never bypass a rejection,
never duplicate an accepted reference, no automatic retry. The managed usageLimited
Goal is untouched.

Scope: this qualifies same-host relative CPU of the regional runs only. It does not
qualify full-stream RSS, production wall time, global history, or package size.
Regional peak RSS is reported but cannot qualify the full stream.
