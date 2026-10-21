# Source-disagreement fit v2: parser repair, 6 October 2026

All statistical choices, A/B development data, 31 heads, coefficient boxes,
pricing and advancement gates are unchanged from
research_round8_native_stage_fit_protocol.md. V1 failed before any fitted head
or feature outcome: its Python role parser incorrectly assumed every initial
code byte >=240 starts a three-byte word. The WRT alphabet also has two-byte
words with that initial byte; the second byte determines termination.

V2 uses the already executed C++ parser's termination contract: a dictionary
atom finishes at its first decoded byte below208 or after three bytes. Its
independent direct index calculation checks every44515complete dictionary
code and every proper prefix, including the overlapping initial-byte range.
The original v1 worker, failed manifest and directory remain preserved. No
native source export, core training, outcome selection or candidate is repeated.

Run research_round8_native_stage_fit_worker_v2.py in a new native_stage_fit_v2
directory. Exact earlier integer predictions for all31nonzero test heads must
survive future target/source/role mutations; a raw-prefix replay checks the
role transition separately. The source observer's exact archive/Q16/decode
gates remain prerequisites. No C/D outcomes are used in this development fit.
