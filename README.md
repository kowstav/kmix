# Compression CMIX research

Compression research code, experimental results, models, and preserved evidence.

| Folder | Contents |
|---|---|
| [scripts/](scripts/) | Python, JavaScript, PowerShell, and C++ research scripts, recovered sources, and Kaggle batches |
| [docs/](docs/) | Research reports, audits, plans, handoffs, and historical documentation |
| [data/](data/) | JSON results and manifests, logs, binary samples, models, and extracted experiment evidence |
| [archives/](archives/) | Preserved ZIP bundles, compressed artifacts, split archives, and legacy bytecode |
| [hutter_research/](hutter_research/) | Importable codecs, statistical contracts, and native components |
| [tests/](tests/) | Codec correctness and research contract tests |

Start with the [research overview](docs/README.md), the
[round 14 integrated report](docs/research_round14_report.md), the
[continuation checkpoint](docs/research_round7_checkpoint.md), and the
[pending experiments handoff](docs/PENDING_EXPERIMENTS_HANDOFF.md).

Run local scripts from the repository root, for example:

```sh
python -m unittest discover -s tests -p test_research_contracts.py -v
python -m unittest discover -s tests -v
```

Some tests require compiled native programs or additional Python dependencies;
individual experiment scripts may require their original remote environment.
Large models and evidence bundles use Git LFS. Run `git lfs pull` after cloning
to download their contents.

The [relocation index](data/repository_layout.json) maps every original tracked
path to its current location. Local scripts use
[a shared path resolver](scripts/_workspace_layout.py) for dynamic filenames.
Historical JSON records, archived payloads, and the three original Claude audits
retain their recorded contents and hashes. Their recorded remote paths and
historical source hashes describe the original experiments.
Checks that require exact historical source hashes should use the original
[pre-organization commit](https://github.com/kowstav/kmix/tree/66ae3021d128b30ea1a4efa2c5ba5dbb58017e63).
