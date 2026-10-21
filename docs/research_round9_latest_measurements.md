# Latest measurement authority

Read [research_round10_report.md](research_round10_report.md) and the hash-indexed
[results registry](../data/results/registry.jsonl).

Original model 2,978,039 B; new CPU BF16 repairs 2,978,077 / 2,978,081 / 2,978,099 B
(growth 38 / 42 / 60 B per copy). Four independent native readers match all 435
tensors each. Rounded-model archive results are pending.

Prior BF16-QAT native manifests: growth 23/19 B per copy; E 65,536-byte payload
savings 49/51 B. Those latest /root artifacts were lost; preserve/reproduce before
promotion. Cold G/H adaptive-law archive saving: 340 B per combined 1 MiB.
No warm full-file saving or current eligible package result is established.

The old measurement summary is preserved in
[historical_reports/research_round9_latest_measurements_through_20261007.md](historical_reports/research_round9_latest_measurements_through_20261007.md).
