from pathlib import Path
import datetime,hashlib,json,re
R=Path(__file__).parent
lex=json.loads((R/'research_round8_lexical_full_prepare_manifest.json').read_text(encoding='utf-8'))
assert lex['full_inverse_exact'] and lex['status']=='COMPLETE_LEXICAL_PREPARATION_FULL_INVERSE'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
note=f'''<!-- canonical-status-start -->
## Current authoritative continuation — {now}

Kaggle355655943: dictionary-atom cache_v1 running PID1491. Inspect its manifest
before launching anything; reuse this job. Registered source/protocol/worker:
research_round8_atom_cache_protocol.md and research_round8_atom_cache_worker.py.
Native cold512K slices A0/B102635191; conditional C310M/D520M. A/B32K reference
archive identity and independent hidden-state decode precede exports. No paid
compute, no core retraining, no project deletions.

Full correct lexical preparation and inverse COMPLETE. Prepared587138826B,
SHA7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce,
including679489side bytes plus16footer bytes. Exact original1B reconstruction
SHA159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.
Remote hp_round8/lexical_full_prepare_v1/lexical_full_ready.wrt preserved.
Preparation CPU89.179715s/RSS1688764KiB; inverse CPU415.462029s/RSS1517616KiB.
Scratch12,865,151,805 apparent bytes, below100GB; no cleanup/deletion performed.
Full native entropy archive and full qualification remain unexecuted. Utilities
skip only packed self-unpacking when verified assets are explicitly provided;
inverse changes only a separate scratch copy.

New comparator rechecked today: pending cmix-neif1.0 (5October) reports95914051B
total; >20% needs<=76731240B. Official awarded comparator stays100424672B.
Read research_round8_competitor_update.md; do not call the pending entry awarded
or locally reproduced. Its source audit may improve combination directions but
is not a measured project improvement.

51native/metric heads completed, ideal convex certificates<0.05B; no priced
advancement. Old G/H candidate checks unexamined and on old FX2 transformedstream.
Old cold diagnostics used different article order; canonical new slices are a
separate provenance. Initial189file evidence ZIP is immutable and verified;
extensions need their own compact source/results bundle. All95families OPEN.

Managed Goal stillusageLimited; never resume, replace, mutate or bypass it on
heartbeats. This explicit human turn authorizes ordinary research only. Week
ends11October. Training$70plan unchanged, spent$0. Core GPU parity stillfails;
independent residual training can use native features without that port.
Older entries below are historical and superseded.
<!-- canonical-status-end -->

'''
p=R/'research_round7_checkpoint.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- canonical-status-start -->.*?<!-- canonical-status-end -->\s*','',s,flags=re.S);p.write_text(note+s,encoding='utf-8')
p=R/'research_round8_native_extension_summary.json';s=json.loads(p.read_text(encoding='utf-8'));s.update(lexical_preparation='COMPLETE; exact full preprocessing inverse, not entropy archive',canonical_prepared_bytes=lex['prepared']['bytes'],canonical_prepared_sha256=lex['prepared']['sha256'],new_running_branch={'experiment':'atom_cache_v1','pid':1491},reported_pending_competitor_bytes=95914051);s['manifests'].append({'file':'research_round8_lexical_full_prepare_manifest.json','sha256':hashlib.sha256((R/'research_round8_lexical_full_prepare_manifest.json').read_bytes()).hexdigest()});p.write_text(json.dumps(s,indent=2),encoding='utf-8')
p=R/'research_round8_report.md';s=p.read_text(encoding='utf-8');marker='<!-- canonical-preparation-results -->';s=s.split(marker)[0].rstrip() if marker in s else s.rstrip();s+='''

<!-- canonical-preparation-results -->

## 17. Correct lexical stream and exact full preprocessing inverse

The correct lexical order is now reproduced and independently inverted through the original native preprocessing code. The dictionary equals the old stream's dictionary, but the article order does not. The canonical final prepared stream is **587,138,826B**, SHA256 `7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce`. It contains the586,459,321B pre-tail stream plus679,489B side information and16B footer. Side SHA256 `98bae9de75b13b0a4f66f33cd24f1c45b145237eb4f99b363c9cb4e6ef918d95`. The complete inverse produces exactly1,000,000,000B with original SHA256 `159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc`.

Preparation used89.179715CPU-user seconds,100.801471wall seconds,1,688,764KiB peak RSS; inverse415.462029CPU-user seconds,427.816229wall seconds,1,517,616KiB RSS. Build38.146831CPU-user seconds. Remote scratch12,865,151,805 apparent bytes. This accounts only the preparation/inverse utility, not entropy coding. The utility bypasses packed self-unpacking only with explicitly verified assets, while the actual transformations remain unchanged. R1 inverse mutates a separate encoded scratch copy. All original models/data and both transformed streams remain preserved; **no project files were deleted**.

This completes a fidelity prerequisite; it provides no compression improvement. A full canonical entropy archive, fully warmed native comparison, code/model accounting and qualifying single-core execution remain open. A new registered dictionary-atom memory experiment uses this correct stream and is running, with exact A/B32K reference/decode controls before512K exports. It repairs internal-code-byte targeting, adds a compact prefix-interval probability representation, and compares geometry, error retention, permutations, recency and causal Bayesian versus fitted gates. See `research_round8_atom_cache_protocol.md`. The result is pending, not a success claim.

## 18. New competitive reference and updated target

A source check on6October found cmix-neif1.0, submitted5October, reporting **95,914,051B total** (pending verification). The official awarded record remains100,424,672B; the preserved lexical model's own comparator remains99,313,750B. A strict>20% reduction from the new reported entry requires<=76,731,240B. The new target and fixed-C3-asset arithmetic are in `research_round8_competitor_update.md`. A matched improvement against our lexical model would still need a complete comparison with this newer entry. [Official awarded reference](https://www.hutter1.net/prize/index.htm), [current benchmark entries](https://mattmahoney.net/dc/text.html), [competitor source](https://github.com/marwoelk/cmix-neif-1.0).

All95families remain OPEN. The successful full preprocessing inverse,51bounded cache-head certificates and finite tensor/program optima are material reproducibility/math results. They are not an absolute compression optimum, a qualifying gain,20%, or work equivalent to the historical research effort behind attention/LLMs. The per-family program explicitly distinguishes completed finite methods, design-only learned architectures and required deeper/native/full checks.
''';p.write_text(s,encoding='utf-8')
p=R/'research_round7_finetuning_execution_plan.md';s=p.read_text(encoding='utf-8');marker='<!-- canonical-training-update -->';header=f'''<!-- canonical-training-update -->
> Updated6October2026: correct full lexical preparation/inverse now PASS,
> T=587138826, SHA7826ff63dedd526c119dda08e6e044be8fa8f6e89a55f3d6b1f3447cdfc5c1ce.
> That specific data gate is completed; full native priors, zero-update export,
> frozen GPU parity and lambda-zero continuation remain open. Old FX2/T figures
> below are historical provenance, not the current training stream. A newly
> reported pending cmix-neif package is95914051B; >20% target<=76731240B.
> For unchanged C3assets6754294B this means payload<=69976946B; these are targets,
> not forecasts. Full details: research_round8_competitor_update.md. No paid
> instance/training launched; the$70stages and$0spending remain unchanged.
<!-- canonical-training-update-end -->

''';s=re.sub(r'<!-- canonical-training-update -->.*?<!-- canonical-training-update-end -->\s*','',s,flags=re.S);p.write_text(header+s,encoding='utf-8')
p=R/'research_round7_report.md';s=p.read_text(encoding='utf-8');marker='<!-- native-extension-integration -->';header='''<!-- native-extension-integration -->
> **6October native extension:**51cache-head variants completed; none advances
> after priced A/B selection. Correct lexical stream587138826B now reproduces
> all1B original bytes exactly through its full preprocessing inverse. Full
> entropy coding remains open. Registered dictionary-atom cache experiment is
> running on that corrected stream. New pending competitor reports95914051B;
> complete source/results and new targets: research_round8_report.md sections16–18.
> All95families unfinished, no20%/qualifying result,$0spending,no deletions.
<!-- native-extension-integration-end -->

''';s=re.sub(r'<!-- native-extension-integration -->.*?<!-- native-extension-integration-end -->\s*','',s,flags=re.S);p.write_text(header+s,encoding='utf-8')
print(json.dumps({'canonical_inverse':'PASS','stream_bytes':587138826,'current_job':1491,'all_ideas_open':True}))
