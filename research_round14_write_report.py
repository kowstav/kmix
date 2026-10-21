from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parent;E=R/'research_round14_batch_evidence'
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def write(p,s):(R/p).write_text(s,encoding='utf-8')
C=read('research_round14_constructor_analysis_v1.json');W=read('research_round14_word_cost_summary_v2.json')
N=[json.loads((E/f'hutter-r14-native-confirmation-{g}-v1/native-confirmation/manifest.json').read_text()) for g in ('a','b')]
G=json.loads((E/'hutter-r14-group-weight-storage-v1/group-storage/manifest.json').read_text())
F=read('research_round14_full_serialized_verification_v1.json');S=read('research_round14_summary_v1.json')
regions=sorted([r for m in N for r in m['regions']],key=lambda r:r['region'])
assert len(regions)==8 and all(c['exact_independent_inverse'] for r in regions for c in r['cases'])
base=sum(next(c for c in r['cases'] if c['mode']=='pinned')['archive_bytes'] for r in regions)
gain=sum(r['actual_archive_gain_bytes'] for r in regions);warm=sum(r['warm_logloss_gain_bytes'] for r in regions)
native_rows='\n'.join(f"| {r['region']} | {r['cases'][0]['offset']:,} | {r['actual_archive_gain_bytes']:,} | {r['warm_logloss_gain_bytes']:.3f} |" for r in regions)
cat_rows='\n'.join(f"| {k.replace('_',' ')} | {v['coded_bytes']:,} | {v['native_bits']:,.1f} | {100*v['native_bits']/W['total_native_bits']:.2f}% |" for k,v in W['categories'].items())
cut_rows='\n'.join(f"| count < {k} | {v['events']:,} | {v['coded_bytes']:,} | {100*v['native_bits']/W['total_native_bits']:.2f}% |" for k,v in W['thresholds'].items())
cpu_rows='\n'.join(f"| Constructor {role}, 304 cases | {C[role]['worker_CPU_seconds']:,.1f} | {C[role]['wall_seconds']:,.1f} | {C[role]['worker_CPU_seconds']/C[role]['wall_seconds']:.3f} |" for role in ('development','confirmation'))
cpu_rows+='\n'+'\n'.join(f"| Native confirmation {g.upper()}, 4 paired regions | {m['worker_and_descendant_CPU_seconds']:,.1f} | {m['finished']-m['started']:,.1f} | {m['worker_and_descendant_CPU_seconds']/(m['finished']-m['started']):.3f} |" for g,m in zip(('a','b'),N))
cpu_rows+=f"\n| Hard-word alignment, 16 windows | {W['CPU_seconds']:,.1f} | {W['wall_seconds']:,.1f} | {W['CPU_seconds']/W['wall_seconds']:.3f} |"
group_rows='\n'.join(f"| {r['partition']} | {r['groups']} | {r['bytes']:,} | {r['saving_per_copy_before_code']:,} |" for r in G['containers'])
write('research_round14_report.md',f'''# Round 14: completed CPU evidence and current shortlist

Updated 9 October 2026. This integrates the completed round-13/14 jobs, including
independent full-container reconstruction, rather than treating old RUNNING labels
as current state. Current new-session work is recorded in the continuation checkpoint.
Paid spend remains $0. No GPU training occurred in this round.

## Outcome that is actually established

The development-selected integer final-coder guard saves **{gain:,} actual bytes**
against **{base:,} baseline archive bytes** across eight independently decoded
3 MiB confirmation regions ({100*gain/base:.4f}% of those regional payloads).
Every candidate reconstructs its original bytes. The last 1 MiB of each region,
after 2 MiB matched warmup, saves **{warm:.3f} ideal bytes in aggregate**.
The archive total includes reset transients; the warm-only number must not be
confused with that total. This is a small measured improvement, not 20%, a
record, a full-history result or a complete-package win.

Four complete 1 GB raw-text proxy archives also independently reconstruct the
original corpus. The constructor/right-context channel has a reproducible narrow
signal, but its complete factorized codec loses against stronger baselines.
Exact grouped model storage does not improve the original model's byte count.

## Native confirmation: actual archives and the warm distinction

| Region | Canonical start | Whole 3 MiB archive saving, B | Last 1 MiB ideal saving, B |
|---|---:|---:|---:|
{native_rows}

The law was frozen from eight development regions before confirmation quality
was opened. The native integration uses the same eight confirmation regions as
the earlier replay; this verifies coding, not eight additional independent
samples. Each region resets both models at its start, so these are regional
histories, not global snapshots. Eight clusters are below the statistical
contract's ten-cluster bootstrap gate. Deterministic spacing also does not itself
justify a population confidence interval.

Earlier development-native tests saved 1,257 B across four separate 3 MiB archives.
Neutral rebuilds matched the pinned archive and every Q16 probability exactly.
The append-only fixed hidden-memory extension did not beat its matched neutral
extension on confirmation (-0.392 ideal B). This does not test learned TTL,
learned eviction, nonlinear attention or an optimized retrieval architecture.

The guard laboratory executable is 732,320 B versus the pinned 497,104 B.
Two uncompressed copies add 470,432 B. An illustrative stationary extrapolation
of the warm-only rate is only about 29 KB over the canonical corpus. Neither
stationarity nor production packing is qualified; this does not pay the current
laboratory code overhead. The next useful work is code-size/resource engineering
and matched full-history evaluation, not advertising a net package improvement.

## All 608 constructor/conditional-bag cases

Thirty-two disjoint, spread 1 MiB original-text regions, fixed seed 1400831,
sixteen development and sixteen confirmation. Nineteen complete codec arms per
region: Markov, paid coarse-right, uniform multiset order, and sixteen conditional
bag variants crossing left/right/wrong/Markov contexts, beta 0/1 and alpha 1/4.
All 608 paid archives independently reconstruct their exact bytes, including
layout, punctuation, case and literal/OOV data. No correction stream is omitted.

The development-frozen overall choice is coarse_right:4. Its confirmation size
is **5,902,282 B**, versus **5,911,723 B** for the matched Markov factorization:
**9,441 B saved**. However, complete gzip is **5,430,102 B** and zstd is
**4,865,282 B** on those identical regions. The factorization loses **472,180 B**
to gzip and **1,037,000 B** to zstd. It remains a raw-text proxy, not lexth11c.

The development-frozen conditional-bag choice is bag_left1:4. Its confirmation
size is **6,173,417 B**, losing **11,143 B** to the uniform paid bag (6,162,274 B)
and **271,135 B** to coarse-right. This closes the declared finite conditional
count/smoothing sweep; it does not prove that learned grammar or all bag
descendants cannot work. Direct right-context prediction earns a mechanism-level
shortlist; the current paid-bag codec does not earn deployment priority.

Selections, all arm totals and region effects are in
research_round14_constructor_analysis_v1.json. The freeze timestamp and input
manifest hash are preserved separately in constructor_selection_v1.json.

## Complete original-corpus check

| Codec, matched 4 MiB chunk boundaries | Actual framed archive bytes |
|---|---:|
| gzip | 323,066,249 |
| zstd | 278,574,861 |
| direct constructor Markov | 350,344,017 |
| paid coarse-right, alpha 1 | 349,939,776 |

Each container covers exactly 1,000,000,000 original bytes in 239 chunks. A second
decoder parsed the actual serialized frames, offsets, lengths and hashes, then
reconstructed all four whole files to SHA-256
159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc.
Coarse-right saves 404,241 B against the matched factorization, while both lose
substantially to zstd. This full-file alpha-1 protocol was fixed before the
later alpha-4 regional selection; it is not falsely called an exact evaluation
of that later selected arm. It is not a native-coder/package comparison.

## Which words consume native bits?

The corrected scanner independently matches the original WRT decoder at every
decoded character and atom boundary while scanning from the start. It labels
sixteen 1 MiB warm scoring intervals and attributes already measured native
final-coder costs. All bits are accounted for once, including unlabelled bytes.
116,564 word types appear in these scored body spans. The labels and full-corpus
frequency census are offline diagnostics, never free decoder inputs.

| Category | Coded bytes | Native bits | Share of all scored bits |
|---|---:|---:|---:|
{cat_rows}

Constructor words are cheap per event but frequent: `the`, `in`, `a`, `and`,
`of` lead cumulative word-attributed cost. Examples with high mean cost and at
least 32 observed events include `simultaneous`, `accompanying`, `quasi` and
`presently`. The ranking is a description of these intervals, not a claim that
teaching those isolated strings will remove their context-dependent entropy.

| Offline corpus rarity threshold | Body-word events | Attributed coded bytes | Share of all scored native bits |
|---|---:|---:|---:|
{cut_rows}

For example, count < 107 covers about 10.92% of these native bits, not most
compression cost. Removing those training targets does not remove their archive
cost. The other dictionary words account for about 50.27% of bits. A balanced
GPU pilot should measure common/rare gradient interference and total native
codelength; frequency-only masking has no demonstrated advantage yet.

The worker's first version failed on `index` versus the saved `id` field before
scoring. Version 2 checks the full 16-ID manifest contract and completed. Its
failure manifest is preserved and is not negative scientific evidence.

## Exact model-storage descendants

Eighteen whole-model representation-aware arms completed, with original stored
dtypes and exact regeneration of omitted RoPE arrays. Best: 3,030,415 B, versus
the original 2,978,039 B. The later grouped sweep evaluates eighteen actual inner
codec alternatives per group, 454 groups across four fixed partitions:

| Partition | Groups | Actual complete container bytes | Saving per copy versus original, B |
|---|---:|---:|---:|
{group_rows}

All 435 tensors match bit for bit, including an independent native C++ reader
dump. Per-group minima are exact within those fixed, independent framing choices;
that finite optimum does not imply optimal quantization, model training or all
possible codecs. Best grouped result still loses 21,233 B per copy before code.

## Four-core execution and limits

| Work | Worker CPU seconds | Elapsed wall seconds | Average occupied CPU cores |
|---|---:|---:|---:|
{cpu_rows}

R13 full-corpus encode/decode used 3.923 cores on average; R14 independent
serialized reconstruction used about 3.879. The grouped storage job and global
word scanner have setup/tail imbalance; their averages must not be rounded up
to four. Word scanning uses four global-prefix shards of different lengths,
which explains its 2.491-core average. These are four logical CPU lanes, not a
claim of four physical cores or guaranteed fourfold speedup.

The observed Kaggle account limit was five concurrent committed CPU notebooks,
plus the live session. A sixth push was rejected. It was later submitted only
after ordinary slots became free; no quota bypass occurred.

## Failures, recovery and current unresolved CPU work

The PPMd article-order commit failed on real-data inverse checks despite passing
tiny preflight tests. Its partial archives are not promoted to complete results.
A standalone reproduction failed on three of sixteen real-data cases, including
direct library encode/decode without our outer container. Both simple and bounded
decode failed. This isolates a backend/data issue, not an ordering quality loss;
the exact upstream root cause is not established. Repair/stress validation and a
complete rerun remain necessary. No result-dependent subset selection is allowed.

Five new native binaries are built: neutral, word-model removal, match-model
removal, double-indirect removal and full-precision transformer output. The
neutral binary SHA is identical to the previously verified neutral. New-session
six-case native preflight has been launched; longer commits are gated on exact
independent decoding. The first build exposed five `.hpp` files omitted by the
old source-bundle filter. They were restored from the preserved original tree,
hashed, and included in the corrected 140-entry source bundle. Original evidence
and failure logs remain intact. See research_round14_next_native_protocol.md.

On 8 October a remote action was blocked by automatic approval review's account
usage limit. It was not executed or bypassed. The user supplied a new session on
9 October; ordinary review authorized reconnection. The separate managed Goal
was not resumed or replaced. CPU experiments cannot be described as completed
merely because their build or plan exists.

## Preservation, deletion and coverage

The four new local result bundles have verified ZIP CRCs and all 1,298 entry
hashes (996 + 218 + 47 + 37). Four detailed model/native/warm-cost bundles are
also SHA/entry verified locally. The Kaggle CLI retrieved only its first 500
output entries: paginated recovery obtained all 609 listed files per constructor
job, including the missing manifests, without rerunning the experiments.

Deleted earlier in R14: one redundant 75,327,948 B aggregate ZIP after its identical
local copy was verified; four duplicate 101,187,584 B decoder hidden traces after
SHA comparison with retained encoder-side originals. Total 480,078,284 B.
Exact paths, hashes and reasons are in research_round14_pull_manifest.json and
research_round14_detail_preservation.json. No data/model/unique source was deleted.
No further deletion occurred on 9 October at this report checkpoint.

All 96 ideas retain their individual history and stronger-test requirements.
Many learned architectures and CPU descendants remain unimplemented. Finite
experiments cannot certify that every possible descendant can never work, nor
that each idea received the maturity of decades of transformer research.
The coverage delta and shortlist explicitly distinguish tested mechanisms,
historical hints, pending implementations and GPU-only proposals.
''')
facts={'updated':'2026-10-09','native_confirmation_actual_gain_bytes':gain,'native_confirmation_baseline_bytes':base,'native_confirmation_warm_gain_ideal_bytes':warm,
 'constructor_confirmation_gain_vs_markov':9441,'constructor_confirmation_gain_vs_gzip':-472180,'conditional_bag_gain_vs_uniform_bag':-11143,
 'grouped_model_best_bytes':min(r['bytes'] for r in G['containers']),'word_categories':W['categories'],'all96_thoroughly_tested':False,'complete_package_gain_established':False,'paid_usd':0}
write('research_round14_verified_facts.json',json.dumps(facts,indent=2))
print(json.dumps({'native_gain':gain,'warm_gain':warm,'baseline':base,'report_bytes':(R/'research_round14_report.md').stat().st_size}))
