# Frozen wider source residual: actual native coding and decoding

Registered on 6 October 2026 after source_wide_confirmation_v1 finished, and
before this candidate's native archives are produced. This is an implementation
check of an already frozen candidate, not another fit or selection opportunity.

Parent: native_inline_residual_v1, whose zero controls, actual C/D archives and
independent decodes passed. Copy its isolated source tree into a new directory,
preserving every executed parent source, archive and manifest. Replace only the
three coefficients in Predictor::ExternalFinalQ16 with the wider family's frozen
values: 0.0016181118716570748, -0.007454085408717222, 2.3818512619982752.
The native probability, neural source, float32 feature, validity/reset law,
integer probability rounding, internal updates and decoder state remain as
specified in the parent's protocol. Do not feed any exported trace to decoding.

Build with exactly the parent's LLVM17 and model flags. First repeat both A/B
32 KiB zero-mode archive and integer-trace identity controls and independent
decodes. Then encode and independently decode the E/F 512 KiB inputs already
preserved in source_wide_confirmation_v1. These slices were chosen before the
wider confirmation outcomes; no coefficients are refitted on E/F.

Hard gates: candidate Q16 SHA matches the frozen numerical replay; hidden
state SHA equals the unmodified reference; decoder Q16 and hidden SHA equal
encoder SHA; reconstructed raw input is byte exact. Stop on any failed gate
and preserve the failure before a named repair. A negative archive gain is a
result, not a reason to change the model after seeing E/F.

Record raw archive bytes and their difference from each matched native archive,
binary bytes/SHA/delta, compiler and source hashes, CPU time, wall time and peak
RSS separately for encoding and decoding. Embedded coefficients are counted
through binary size rather than charging another parameter copy. Laboratory
executable delta does not establish the production packed loader delta. All
cold slices, model assets, full warm archive and prize resource constraints
must still be accounted for before any qualification or percentage claim.

Directory: hp_round8/native_inline_wide_v1. No project, data or model deletion;
no paid rental or spending; no core weight updates. Never duplicate a live job.
