"""Preserve measured placement conclusions, launch details and source hashes."""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

import datetime,hashlib,json,pathlib
ROOT=project_root(__file__)
marker='## Session355454655 placement continuation,5October13:38UTC'
pre='''

## Session355454655 placement continuation,5October13:38UTC

This section supersedes historical running/pending statuses above. I03b and
I04 completed all four2M slices; I03b gains4.243968124 ideal bytes before costs,
I04 loses7.847331710B. Both native32K final-bit identity/old-cost/decode checks
PASS. The quantized I05 residual pilot loses4.017518270B/64K. Do not promote
these predictors or price them as record improvements. Precise equations,
word-lag nuance, methods and evidence are in
research_round7_placement_theory_and_experiments.md.

The fresh kernel is788f499d-4818-4c63-974e-bc26b298ddf0. Keep its signed proxy
URL only in runtime/conversation. Use the existing kaggle_research_client.mjs
with HP_KAGGLE_BASE set from the latest user-supplied URL. Never paste the
signed credential into a script/report. Existing Goal remains usageLimited;
it was neither resumed nor replaced. This was an explicitly requested human
continuation; automated follow-ups must not bypass that limit.

### Current jobs and exact continuation

Only the larger final-bit collector remains active at the last check:
research_round7_lex_finalbit_2m_worker.py, controller PID1097, persistent output
/kaggle/working/hp_round7/lex_finalbit_2m_v1 and log
lex_finalbit_2m_v1_controller.log. C/D child PIDs1101/1102 were active13:36UTC;
their traces had18,223,104/18,063,360 bytes at that check. Each complete trace
must have32,000,000 bytes for16,000,000 uint16 probabilities. A/B are queued.
The4x2M collection should add128MB traces,32MB cost files and small archives/
logs, and needs no model/data deletion. Persistent free space was8,836,071,424B
at13:36UTC. Elapsed time/partial file length never substitutes for PASS.

1. Query /api/kernels using the latest session. Inspect active commands and
   preserved outputs before restoring or launching anything. The old session
   became inaccessible at09:52–09:56UTC; the new session recovered all I03b
   results, proving that inaccessible proxy did not mean missing results.
2. Execute the local RPC research_round7_finalbit_active_status.py through the
   bridge: node kaggle_research_client.mjs exec KERNEL_ID
   research_round7_finalbit_active_status.py. It reads summary/manifest/results,
   trace lengths, active commands and disk space. Reuse active children; avoid
   repeated unchanged checks. Native traces are partial until their child exits
   and archive, cost, alignment and reconstruction controls pass.
3. Download manifest.json/results.json and completed slice files with the
   bridge's download command. New files are lex_finalbit_2m_v1/{a,b,c,d}/
   final_p.u16, cost.f32, out.cmx and compress.log. The controller compares
   candidate archive bytes to the preserved old archive and EVERY float32 byte
   cost to the old costs, checks8N probabilities in[1,65535], and reconstructs
   costs in65536-byte blocks to bound transient RAM. Threshold1e-4 bits/byte
   remains unchanged. Linux wait4 records each child CPU/RSS; overlapping wall
   completion polls have the stated practical delay. Preserve failures.
4. I05 pilot source is research_round7_bit_placement_residual.py; launcher is
   research_round7_launch_bit_placement_residual.py. It already completed in
   bit_placement_residual_pilot_v1; DO NOT run that launcher again. All tree
   mass equivalence/integer identity/literal escape/partial EOF tests pass.
   A/B results, log and hashes should be preserved. The native32K source/raw/
   final traces and dictionary are local, allowing independent reproduction.
5. The four2M traces are reusable measurements of the existing final coder.
   The losing32K residual grid must not be automatically promoted. A larger
   screen needs a distinct immutable output directory, explicit2M inputs/
   trace hashes, parser/EOF identity tests and priced native confirmation for
   any positive result. Frozen hypotheses and new E/F regions must provide
   confirmation; A/B/C/D have already been examined repeatedly.

### Completed jobs, why they were run, and remaining gates

I04 tested directed placement beyond undirected echo. Fixed lags1/2/4/8/16/64,
8192 shared rows,32 edges/row, gamma32, rank prior64, deterministic LRU/edge
discard/rescaling, reset source queue per article, retained learned counts.
The root additive expert charged every post-marker literal/case/escape/code/
EOF outcome. No gain: A/B/C/D=-2.496075207/-1.561330466/-2.340943676/
-1.448982361B. Prototype wall181.09/196.95/184.15/180.81s, reported process
peak592928KiB. Metadata includes eviction counters, input/cost/dictionary and
dependency hashes. Fixed-row payload estimates omit indexing/LRU/alignment;
they are not a full runtime/package claim.

Native trace V1 used the exact original lex source, all original lab anchors,
roundtrip hooks, classical and actual inference macros, no PGO/LTO, portable
x86-64-v3/-mrecip=none and isolated source tree. Clang17.0.6/lld17 were restored
from the official signed LLVM repository; package removal was disabled. V1
compiled but lacked /usr/bin/time before inference. Its logs/results remain.
V2 research_round7_lex_finalbit_trace_finish.py reused that496320-byte binary,
used Linux wait4 and explicit -d, and independently passed A/B32K native
identity/decode. Never rerun V1's failing controller or restore its wrong
decode command. Future use/recovery should reuse the preserved binary and V2
controls, checking exact hashes before execution. Both final trace controls
and their complete native time/RSS are local JSON evidence.

I05 tested the missing conditional log-odds instead of a standalone word head.
Prefix trie/global mass and sparse row counts derive exact binary word-expert
probabilities. Seven lag/mix families times signed strengths-1/-.5/-.125/
.125/.5/1 plus neutral produce43 models. Expert-minus-global log-odds are
clipped±8. Models and selected mixture are rounded to[1,65535]; exact zero
corrections preserve original p. Prefix-only Bayesian contexts use bit position,
known code-prefix length, article age and previous atom type. No target word,
future code width or hindsight donor chooses a context. Candidate likelihood
is NOT a global P0 word tilt; every post-marker bit is scored. Native candidate
compression/decode remains required for a positive result; current pilot loses
2.235405729/1.782112540B on A/B, wall58.64/56.14s.

The example-pair DICT audit completed all four slices. The follow-up full-ASCII
audit is essential because i is not in this dictionary: DICT lags skip literal
I/i. Both diagnostics ran on Kaggle and their parser fixtures pass. Full ASCII
audit counted1,884,022 words including4878 i,232 know and804 now. There are zero
now→know/know→now pairs at ASCII lags1–4 in these samples. This is not a global
linguistic rule or proof that directed placement is useless. The dictionary
the/of codes already average1.907/1.094 bits; all12 named/common DICT labels
carry5.456% of full native ideal bits. Restricting gains to those spans cannot
alone deliver20%, even with an unpriced perfect oracle. Focus broader content
first mentions and residual error, rather than just the hand-picked examples.

Pending I04b cross-article retrieval; I06 syntax/source-surprise gates; I07
matched memory/control ablations; I08 richer spelling/phonetic controls; I09
hazards; I10 shared trained residual model; P01–P05 remain as registered.
Priority after trace completion is a preregistered syntax/surprise residual
screen and bounded previous-article retrieval, with exact neutral, random and
empty controls. Neural SGD/rental remains gated on useful priced evidence or
an explicitly justified training-only hypothesis. The$70 staged training plan
is unchanged; no money has been spent. Verify actual rental offers before any
purchase. No absolute optimum,20% model/package improvement or qualifying
archive has been achieved. No model/data/project deletion occurred.
'''
report='''

## New community placement proposals and measured continuation,5October13:38UTC

The proposals contain a valid causal mechanism: decoded words can generate
timed candidates and syntax can select/suppress them. Their examples are not
evidence of a substantial residual gain. Structural similarity does not
automatically encode semantics; glyph moments are linear transforms of letter
moments, and the five proposed polynomial moments have rank3. Literal Wordle
guess/correction is a different probability model, without an inherent entropy
advantage. Direction, distance, normalization, selector cost and delayed causal
updates matter. The precise derivations and code are in
research_round7_placement_theory_and_experiments.md.

Recovered completed I03b gains only4.243968124 ideal bytes/8M before overhead.
The actual new directed lag test I04 loses7.847331710B/8M. A subsequent
quantized final-bit residual pilot loses4.017518270B/64K, after exact native
archive/byte-cost/independent-decode controls passed on both32K slices. These
results reject deployment of these tested versions; they do not prove that
every placement, retrieval or trained residual architecture is futile.

The new trace instrumentation preserves original predictors and outputs final
uint16 p(bit=1) before Perceive. V1's missing timing utility failure is retained;
V2 reused its build with Linux wait4 and explicit -d. Native trace user times
66.852/66.098s, peaks5651732/5798496KiB; both archives/costs match reference
exactly and independent decoded inputs match. Traces and dictionary are local.
Four2M final-bit collections are now active under controllerPID1097; C/D native
children1101/1102 were active13:36UTC and A/B queued. Archive bytes/cost arrays
must match preserved controls completely before any trace is used as evidence.

A subtle placement issue was tested rather than ignored: I/i is literal and
absent from this dictionary, so DICT lags differ from English word lags. A
separate full-ASCII audit counted1,884,022 words in these four2M slices and no
now→know/know→now at word lags1–4. The's dictionary codes average1.907 bits,
of's1.094; all12 named/common DICT labels carry only5.456% of full native ideal
bits. These restricted sampled budgets, excluding other words/literals/case,
are not global bounds. Broader content-word first mentions remain the larger
target. Local assessments preserve both lag units explicitly.

No meaningful/20% compression breakthrough or absolute optimum is claimed.
No neural retraining, paid rental, project deletion or Goal mutation occurred.
The pre-experiment registry includes all exact sources, jobs, parameters,
tests, failures, gates and continuation steps. Reuse active native work.
'''
for name,text in [('research_round7_pre_experiment_report.md',pre),('research_round7_report.md',report)]:
    path=project_path(name, base=ROOT);old=path.read_text(encoding='utf-8')
    if marker not in old and (name!='research_round7_report.md' or '## New community placement proposals and measured continuation,5October13:38UTC' not in old):
        path.write_text(old+text,encoding='utf-8')
names=['research_round7_directed_lag_screen.py','research_round7_bit_placement_residual.py',
       'research_round7_lex_finalbit_trace_patch.py','research_round7_lex_finalbit_trace_worker.py',
       'research_round7_lex_finalbit_trace_finish.py','research_round7_lex_finalbit_2m_worker.py',
       'research_round7_placement_pair_audit.py','research_round7_ascii_placement_audit.py',
       'research_round7_finalbit_active_status.py','research_round7_placement_theory_and_experiments.md',
       'research_round7_pre_experiment_report.md','research_round7_report.md','research_round7_checkpoint.md',
       'research_round7_placement_assessment.json','research_round7_ascii_placement_assessment.json',
       'research_round7_lex_finalbit_trace_v2_results.json','research_round7_wrt_dictionary.bin',
       'research_round7_lex_finalbit_a32k.bin','research_round7_lex_finalbit_b32k.bin',
       'research_round7_lex_finalbit_a32k_p.u16','research_round7_lex_finalbit_b32k_p.u16',
       'research_round7_bit_placement_residual_pilot_v1_summary.json']
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'point-in-time local placement/trace source and evidence; mutable reports change after future updates',
   'assets':[{'path':n,'bytes':(project_path(n, base=ROOT)).stat().st_size,'sha256':hashlib.sha256((project_path(n, base=ROOT)).read_bytes()).hexdigest()} for n in names],
   'neural_training':False,'paid_rental_usd':0,'deletions':[]}
(project_path('research_round7_placement_asset_manifest.json', base=ROOT)).write_text(json.dumps(r,indent=2))
print(json.dumps({'preserved_assets':len(names),'handoff_updated':True,'deletions':[]}))
