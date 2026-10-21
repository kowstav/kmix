# Hutter compression research workspace

Current authority: [round 14 integrated report](research_round14_report.md) and
[continuation checkpoint](research_round7_checkpoint.md). Earlier rounds are dated
experimental evidence, not current process status or a proof that their descendants
have reached their potential.

| Read next | Purpose |
|---|---|
| [Pending experiments — read first](PENDING_EXPERIMENTS_HANDOFF.md) | Six-work-package queue, exact procedures, commands, mathematical gates and implementation status |
| [Current CPU execution](research_round14_report.md) | Actual four-core use, completed representative cases, running jobs and versioned failures |
| [CPU handoff and pre-experiment report](research_round14_pre_experiment_report.md) | Exact inputs, immutable sources, how/why/gates for every current job and pending work |
| [Audit repair ledger](research_round14_audit_delta.md) | Original 53 findings plus the third audit's seven groups; experimental gaps remain explicit |
| [Mathematical analysis](research_round14_theory.md) | Objective, shared-byte masking, paid constructor/order laws, finite-precision guards and fair negative evidence |
| [All 96 idea coverage](research_round14_96_coverage.md) | Three audit questions per idea, actual work versus fair tests, stronger descendants and combination dependencies |
| [Measured shortlist](research_round14_shortlist.md) | Native guard, paid right-context mechanism and open CPU resource frontier |
| [Training and 5090 budget](research_round10_training_and_5090_plan.md) | Stable continuation, rate/rarity/word/memory controls and conditional hours within $70 |
| [Results registry](../data/results/registry.jsonl) | One indexed finite result version/job per ID; no automatic upgrade of evidence |
| [Claude flaws audit](CLAUDE_AUDIT_01_FLAWS_REPORT.md) | Original independent audit, preserved unchanged |
| [Claude next-experiment audit](CLAUDE_AUDIT_02_NEXT_EXPERIMENTS_AND_THEORY.md) | Original proposals/theory, preserved unchanged |
| [Claude round-12 verification](CLAUDE_AUDIT_03_ROUND12_VERIFICATION_AND_CPU_RESULTS.md) | Original independent follow-up and other agent's CPU results, preserved unchanged |

[hutter_research/](../hutter_research/) contains the current importable codecs, exact unit/cost/statistical
contracts, integer mixer, carried long-memory bank and paid article-order proxy.
[tests/](../tests/) contains correctness properties. [scripts/kaggle_cpu_round10/](../scripts/kaggle_cpu_round10/) contains the six
historical private CPU kernels. [scripts/kaggle_cpu_round13/](../scripts/kaggle_cpu_round13/) and [scripts/kaggle_cpu_round14/](../scripts/kaggle_cpu_round14/) contain the frozen
four-worker batches; actual references and execution states are recorded in the current checkpoint.

Important result files:

- [BF16 repair results](../data/research_round10_bf16_repair_results.json): neutral byte identity and repaired
  model growth of 38/42/60 bytes per model copy;
- [Native reader results](../data/research_round10_native_reader_results.json): exact independent C++ agreement
  on all 435 tensors in each of four exports;
- [Historical local checks](../data/research_round10_local_checks_results.json): 23 Python checks plus exhaustive
  C++ neutral/integer/retention checks;
- [Private CPU batch manifest](../data/research_round10_private_cpu_batch_manifest.json): exact prepared source/model
  payload and per-kernel hashes;
- [Native BF16 promotion results](../data/research_round9_native_bf16_promotion_v1_results.json): measured prior-session
  BF16-QAT native archives; latest `/root` model artifacts require reproduction.

Preservation bundles are indexed by their validation manifests. The large round-9
extended ZIP was CRC/SHA verified. Its split parts remain duplicate storage; they
have not been removed in round 10. Some later prior-session models were outside
that bundle. A terminal manifest hash does not imply a locally preserved model.

No retraining or native quality claim is inferred from a synthetic property test.
A replay is labelled replay, a raw/gzip experiment is labelled proxy, and a cold
or early warm slice is not relabelled full corpus. Final acceptance uses exact
reconstruction, actual complete-package bytes and eligible production resources.
