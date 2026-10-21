# Verified native extension preservation

6 October 2026. Both local and remote bundles pass SHA-256 and ZIP CRC.

New immutable local ZIP: research_round8_native_extension_evidence_20261006.zip,
28,644,346 bytes, 646 entries, SHA
b338507e574640ab2ce64fb564d1e1594eceaf36271b2133eb358a2a745ba713.
Verified remote copy: hp_round8/round8_native_extension_20261006_complete.zip.

Original immutable research_round8_evidence.zip remains unchanged: 11,996,472
bytes, 190 ZIP entries including its manifest, SHA
b322344131ac6e16a0824a491968b793bc34a6a348227dfe03f41acb0d0568df.
Its existing remote copy hp_round8/round8_evidence_20261006_complete.zip also
passed SHA and CRC. Its earlier 189-file count excluded the manifest entry.

Read research_round8_all_binary_bundles_remote_verified.json for remote checks,
research_round8_native_extension_bundle_validation.json for local checks, and
research_round8_native_extension_bundle_manifest.json for per-file hashes and
36 explicitly excluded large trace records. These large traces remain remote;
their compact controls, sources, model/dictionary, exact inputs or reproducible
provenance, and validation manifests are preserved locally.

The later transfer correction does not change the immutable ZIP snapshot.
The legacy kaggle_research_client.mjs `put` mode is **text only**. It must not
upload binary files. Use kaggle_binary_upload.mjs REMOTE_PATH LOCAL_PATH SHA256
with HP_KAGGLE_BASE supplied from the newest authorized conversation link;
never persist that credential. Its corrected format=base64 upload was verified
remotely, rather than inferred from an HTTP success.

The first native extension upload converted binary bytes to text. Its failed
51,746,088-byte copy was renamed, not deleted, to
hp_round8/round8_native_extension_20261006_complete.zip.failed_text_upload.bin,
SHA e99c8c55950cb258eb323d12f5eb2dd71e9420fedbaf1c66508812e8a865e3bf.
The incorrect source-preservation file-count assertion and its v2 required-file
repair also remain preserved. See research_round8_binary_bundle_repair_manifest.json
and research_round8_stage_source_preservation_v2.json.

No project files, models or data were deleted. No paid spending occurred.
Completed narrow/wider native slices and the partial free-T4 masking pilot do
not establish a qualifying full package, 20% improvement or closed idea family.
Current work and pending dependencies are in research_round8_current_answers_20261006.md
and research_round8_session355735431_handoff.md. All 96 families remain open.
