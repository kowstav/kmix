# Guard plus match pruning: frozen confirmation, 9 October 2026

Development is complete: four exact pairs, 10 B payload penalty versus guard,
6.745555 ideal warm B penalty, approximately 24 MiB less RSS. Joint executable
is 217,540 UPX bytes versus 218,608 for guard, saving 1,068 B per deployed copy.
Joint-versus-neutral development payload gain is 1,247 B; interaction is -8 B.
These quantities are not added across incompatible corpus sizes.

Advance this fixed candidate as a package/RAM tradeoff. No rates, features,
tables, binaries or model weights change. The sole harness change selects region
IDs and records the run label. A uses 8,10,12,14 and B uses 9,11,13,15, each
3 MiB with 2 MiB warmup and an independently decoded actual archive. Preserve
the baseline guard Q16/archive hashes and match the historical guard on all
eight regions. Existing N/M probabilities may calculate byte interaction only;
do not compare CPU across hosts. Do not choose a subset after seeing outcomes.

Both configurations are privately prepared; submit A into the fifth available
slot and B only after A completes normally. Four pinned processes per notebook,
one core each, 10.3-hour limit, no GPU, no paid resource, no duplicate push.
If timing remains inconsistent, record it as unresolved and use counterbalanced
A/B/B/A repeats before any deployment speed claim. Confirmation does not qualify
full-stream RAM, wall time, global history or complete-package superiority.
