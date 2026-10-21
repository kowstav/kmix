# P4 freeze addendum (v13): execution-path fix, no scientific change

The v12 development notebooks failed before any byte was coded.
`chaoscpp/hutter-r14-structx-development-a-v1` and `-b-v1` (pushed 05:57 UTC) both ended
`FAIL_PRESERVED` with `PermissionError(13)`. The harness executed `cmix_structx*` directly
from the read-only Kaggle dataset mount, which carries no execute permission. Their
outputs and push receipts are preserved as failures, not rewritten.

The live gate did not catch this: its asset directory lived in `/root` with execute
permission set. Every other R14 harness copies binaries to scratch and sets execute first.

The only change in v13 (`hutter_research/cpu_round14_structx.py`): binaries are copied from
the asset directory to `ROOT/bin`, set executable and re-verified by SHA-256 before use. No
mode, region, rate, store, feature, threshold, binary or analysis rule changes.

Before any v13 commit, a re-gate must run the v13 code path against a read-only,
non-executable copy of the identical assets. That reproduces the notebook mount
condition. It must reproduce the v12 gate's exact archive and Q16 hashes for region 4,
modes 1, 2 and 3 (16 KiB). New references use the `-v2` suffix.
