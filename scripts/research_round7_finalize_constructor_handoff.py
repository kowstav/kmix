"""Integrate the completed constructor screens and preserve a reproducible handoff."""

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
root=project_root(__file__);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
a=json.loads((project_path('research_round7_constructor_assessment.json', base=root)).read_text())
b=json.loads((project_path('research_round7_constructor_skeleton_v1_assessment.json', base=root)).read_text())
c=json.loads((project_path('research_round7_constructor_skeleton_v2_assessment.json', base=root)).read_text())
n=json.loads((project_path('research_round7_finalbit_local_validation.json', base=root)).read_text())
assert a['all_24_raw_roundtrips']=='PASS' and b['all_16_raw_roundtrips']==c['all_16_raw_roundtrips']=='PASS' and n['status']=='PASS'
heading='## Measured constructor results and current handoff,5October2026'
table='| Representation | zlib9 increase | LZMA6 increase |\n|---|---:|---:|\n'
for assessment,prefix in [(a,'Framed gaps: '),(b,'Two-byte marker: '),(c,'One-byte marker: ')]:
    rows=assessment['matched_codec_aggregate'];modes=list(dict.fromkeys(v['representation'] for v in rows))
    for mode in modes:
        z=next(v for v in rows if v['representation']==mode and v['codec']=='zlib9')
        l=next(v for v in rows if v['representation']==mode and v['codec']=='lzma6')
        table+=f"| {prefix}{mode} | +{z['increase_percent']:.3f}% | +{l['increase_percent']:.3f}% |\n"
section=f'''

{heading}

Updated {stamp}. I11/I11b/I11c all COMPLETE; no constructor or native trace
process remains active. The three experiments made56 matched-codec packet
comparisons over four2M original WRT slices. All56 exact raw reconstructions
and compressor roundtrips PASS; every candidate is larger on every slice.
The following aggregate compares each fixed representation with its own
matched original-source codec. These are not cmix/Hutter record deltas.

{table}

The one-byte-marker paid word-table variant is the least costly skeleton:
zlib original3,623,465B vs candidate3,698,340B (+74,875B,2.066%);
LZMA original2,894,828B vs candidate3,028,020B (+133,192B,4.601%).
Incremental decoder/program cost is excluded from these packet differences,
so adding it cannot rescue these already negative results. Per-slice values,
source/dependency/input/cost hashes and timing are in the preserved JSONs.

The fixed176-word lexicon matches629,700 of1,884,022 ASCII word events
(including markup), but its disjoint original word/case spans carry17.200%
of the sampled native ideal bits. The per-slice shares are7.922/18.083/
17.777/19.690%. This is an accounting result for this heuristic and these
slices, not a universal function-word inventory or whole-corpus bound.
With every other cost fixed, even zero-cost encoding of just these selected
spans cannot deliver20% on this sample. A20% overall target needs gains on
content/structure too, or a different broader scope with measured headroom.

87.345% of1,254,326 constructor gaps have length zero or one, offering no
permutation sharing. Merging ordered case-folded tuples into multisets reduces
distinct template counts by only2.883–6.167% within the four slices. The
observational H(order|multiset) total is11,573.927bits. This is a fitted
descriptive statistic, not an untransmitted probability table or achieved
code length. The pilot's exact raw multiset code pays order ranks; a better
contextual order model could reduce their cost. It does not remove the paid
content stream, slot/escape information or lost cross-channel correlations.

I11 consumed175.321 prototype CPU seconds and176.164 wall seconds; I11b
45.423/45.432 and I11c40.640/40.649s. Reported process peak RSS is593,568/
593,696/593,952KiB. These are Python experiment/runtime peaks and include
process setup/inheritance; they are not measured standalone C++ decoder
requirements, full-corpus runtime, or a qualifying CPU package. No new
parser/weights, neural training, rental, deletion or Goal mutation occurred.

The native final-bit collector also completed all four2M slices with PASS.
All128MB of uint16 traces and8MB original inputs are local; all source input,
trace and preserved native archive hashes match. Independent local blockwise
reconstruction validates64M actual coded-bit probabilities in[1,65535] and
maximum byte-cost error below9.54e-7bits (fixed gate1e-4). Native archives and
EVERY prior float32 byte cost are identical to the preserved baselines.
Individual native user CPU is1236.291/1312.900/1292.865/1313.031s for A/B/C/D;
peak RSS max6,043,696KiB. This proves measurement identity, not new compression.
Local evidence: research_round7_finalbit_local_validation.json and
research_round7_lex_finalbit_2m_v1_{{manifest,results}}.json.

### Next steps and stopping gates for this hypothesis

Do not repeat the losing static layouts or spend$70 merely to reproduce their
generic-codec screens. A still valid hypothesis is a compact CONDITIONAL gap
model exploiting paid decoded left/right content and a better content model.
It needs a new joint distribution Q_C(C)Q_A(A|C)Q_G(G|C,A) and total-length
evaluation, not the old transformer's scores applied to reordered bytes.
The controlled no-retraining alternative is a prefix-only syntax/template
residual on the original final-bit coder, with normalized integer probabilities.

I12 prefix-only constructor-run expert remains PLANNED, not running. It should
use completed ASCII words (including literal I/i), a fixed constructor lexicon,
bounded ordered run/trie state, left content class/ID and punctuation/markup
state. Commit a word only when the decoded separator establishes its boundary;
never choose an expert from the target's future word/length/POS. Maintain a
neutral expert and a global non-constructor fallback; preserve nonzero support.
Build the expert's full word-trie branch probabilities and compare its binary
log-odds to its global-prior expert, then apply a clipped signed residual to
the actual native uint16 p. Quantize every candidate and mixture. Do not add
independent word gains or use a target-dependent activation mask. Test neutral
byte-for-byte identity, all escape/case/EOF bits, sparse memory rescaling and
reset semantics first. Preregister state/row caps and scales; screen A/B32K,
then larger regions ONLY if a priced signal survives. Freeze on development
and confirm on new E/F regions; these A/B/C/D are already examined research
data. A positive screen still needs a native archive, independent decode,
full package bytes and CPU/RAM verification.

Existing pending I04b retrieval/I06 syntax-source-surprise/I07 memory controls/
I08 phonetics/I09 hazards/I10 trained shared residual/P01–P05 retain their
own registered gates. Prioritize high-cost content/first-mention residuals
alongside grammar, given the measured constructor budget. The staged$70
training plan remains unchanged, with no spending or promised rental rates.

### Exact recovery commands and evidence

Use the newest user-supplied session credential only via HP_KAGGLE_BASE, and
the existing kaggle_research_client.mjs bridge. Kernel currently
788f499d-4818-4c63-974e-bc26b298ddf0, session355454655. Read-only status RPC:
research_round7_constructor_all_active_status.py for I11/I11b/native trace;
research_round7_constructor_skeleton_v2_status.py for I11c. All are complete;
no launcher should be run again against its existing exclusive directory.

Directories/logs: constructor_split_v1 / constructor_split_v1_controller.log;
constructor_skeleton_v1 / constructor_skeleton_v1_controller.log;
constructor_skeleton_v2 / constructor_skeleton_v2_controller.log;
lex_finalbit_2m_v1 / lex_finalbit_2m_v1_controller.log, all below hp_round7.
Preserved compact outputs are locally prefixed research_round7_ plus the
corresponding directory/log names. Sources, launches and preregistrations are
also local. I11c source was generated by checked anchor replacements without
editing the measured I11b source. No deletion was needed; persistent free
space at the final existing-job check exceeded8.7GB.

Local reproduction/validation with the bundled Python:

    python research_round7_constructor_assess.py
    python research_round7_constructor_skeleton_assess.py v1
    python research_round7_constructor_skeleton_assess.py v2
    python research_round7_finalbit_local_validate.py

The first constructor assessment has now verified all four local original
inputs, costs, source and result equality. The final-bit validator independently
checks probability alignment/reconstruction and hashes. Constructor source
scripts use Linux resource accounting; run full original experiments on Kaggle
or Linux rather than silently deleting that instrumentation on Windows.
Managed Goal remains usageLimited; no automated continuation may bypass it.
Latest user-directed continuation performed this work, without resuming it.
No20% gain, absolute optimum or qualifying archive breakthrough is claimed.
'''
for file in ['research_round7_constructors_and_variables.md','research_round7_pre_experiment_report.md','research_round7_report.md']:
    p=project_path(file, base=root);text=p.read_text(encoding='utf-8')
    if heading not in text:p.write_text(text+section,encoding='utf-8')

prepath=project_path('research_round7_pre_experiment_report.md', base=root);pre=prepath.read_text(encoding='utf-8')
current='<!-- constructor-current-status -->'
if current not in pre:
    banner='''<!-- constructor-current-status -->
# Current experiment status —5October2026, after constructor screens

No experiment is currently running. I11/I11b/I11c COMPLETE:56 matched-codec
comparisons, all exact raw roundtrips PASS and all archives larger. Best
constructor skeleton:+2.066% zlib9 / +4.601% LZMA6 before added decoder cost.
All four2M native final-bit traces COMPLETE/PASS and preserved locally, with
independent hash/reconstruction controls. No20% or qualifying breakthrough.

Completed earlier: I03b corrected integer echo, I04 directed lag screen,
I05 quantized final-bit32K residual pilot, native/GPU fidelity pilot and both
placement audits. I03b gain is only4.244 ideal bytes/8M before costs; I04/I05
lose; GPU/native fidelity FAILED and larger tests were skipped. These outcomes
must not be promoted as record gains.

Pending: I12 prefix constructor/syntax residual, I04b bounded retrieval, I06
syntax/source-surprise gates, I07 memory controls, I08 phonetics, I09 hazards,
I10 trained shared residual and P01–P05 package/EOF/calibration/macro/full-stream
gates. None has been launched by the constructor continuation. Exact rationale,
definitions, accounting, validation and recovery commands are in the final
`Measured constructor results and current handoff` section of this document
and research_round7_constructors_and_variables.md. Older running statuses
below are historical. Managed Goal remains usageLimited; no auto-resume.
No paid compute, retraining, project deletion or Goal mutation.

'''
    prepath.write_text(banner+pre,encoding='utf-8')

# Rewrite the current checkpoint header while retaining historical entries.
cp=project_path('research_round7_checkpoint.md', base=root);old=cp.read_text(encoding='utf-8')
history=old[old.index('Heartbeat read-only check5October09:10UTC:'):]
header=f'''# Hutter compression research checkpoint —5October2026

Updated {stamp}. Status: research incomplete; no20% or qualifying compression
breakthrough. Latest human proposal (constructors/variables/constants and paid
right context) analyzed and implemented. I11/I11b/I11c COMPLETE:56 exact raw
packet comparisons on ABCD2M, all larger than matched zlib9/LZMA6 baselines.
Least costly skeleton: +2.066% zlib / +4.601% LZMA, before added decoder cost.
176-word constructor list carries17.200% of sampled native bits;87.345% gaps
have0/1 constructors; unordered sharing reduces distinct templates2.883–6.167%.
Detailed mathematics, primary research, code accounting, results and next
architecture: research_round7_constructors_and_variables.md. Pre-experiment
report and integrated report include the complete latest measured handoff.

All four2M native final integer probability traces COMPLETE/PASS. Controller
1097 and children1144/1145 finished; no current constructor/native job remains.
Local128MB traces +8MB inputs have verified hashes and independent byte-cost
reconstruction, maxerror<9.54e-7bits/byte. Existing archive and EVERY prior
cost remain identical. See research_round7_finalbit_local_validation.json;
research_round7_lex_finalbit_2m_v1_results.json/manifest.json. Native CPU user
1236.291–1313.031s/slice; peak6,043,696KiB. Measurement prerequisite, not gain.

I03b completed: +4.243968124 ideal bytes/8M before added costs. I04 directed
lags loses7.847331710B/8M. Quantized I05 pilot loses4.017518270B/64K. Placement
and corrected full-ASCII audits COMPLETE. No losing predictor promoted.

Current kernel788f499d-4818-4c63-974e-bc26b298ddf0, session355454655. Signed
proxy lives only in conversation/runtime. All launchers use exclusive output
and logs; inspect preserved results and never relaunch completed directories.
Read-only continuation RPCs: research_round7_constructor_all_active_status.py
and research_round7_constructor_skeleton_v2_status.py. Remote directories:
hp_round7/{{constructor_split_v1,constructor_skeleton_v1,constructor_skeleton_v2,
lex_finalbit_2m_v1}}. All compact JSONs/logs and original sources are local.

Pending I12 prefix-only constructor/syntax residual (not implemented/running),
I04b retrieval/I06 syntax-source-surprise/I07 memory/I08 phonetics/I09 hazards/
I10 trained residual/P01–P05 as documented; new optimized claims need untouched
E/F regions, full package and independent native decode/CPU/RAM gates.
No neural retraining, paid rental, project deletion or Goal mutation. Staged
$70 training plan preserved. Goal remains usageLimited as last inspected;
heartbeats must not resume/bypass it. Already requested action is not repeated.
Older entries below are historical and superseded by this header.

'''
cp.write_text(header+history,encoding='utf-8')

# A dated snapshot, not an immutable hash assertion about future edited reports.
files=set(project_glob('research_round7_constructor*', base=root))|set(project_glob('research_round7_launch_constructor*', base=root))
files.update(project_glob('research_round7_lex_finalbit_*2m_p.u16', base=root));files.update(project_glob('research_round7_?2m.bin', base=root))
files.update(project_path(v, base=root) for v in ['research_round7_constructors_and_variables.md','research_round7_pre_experiment_report.md','research_round7_report.md',
                             'research_round7_checkpoint.md','research_round7_finalbit_local_validation.json','research_round7_finalbit_local_validate.py',
                             'research_round7_lex_finalbit_2m_v1_manifest.json','research_round7_lex_finalbit_2m_v1_results.json',
                             'research_round7_lex_finalbit_2m_v1_controller.log','research_round7_finalize_constructor_handoff.py'])
files.discard(project_path('research_round7_constructor_asset_manifest.json', base=root))
assets=[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files) if p.is_file()]
(project_path('research_round7_constructor_asset_manifest.json', base=root)).write_text(json.dumps({'utc_snapshot':stamp,'assets':assets,
  'interpretation':'Dated local preservation snapshot; mutable reports may change later. Sources/results/traces remain reproducible.',
  'neural_training':False,'paid_rental_usd':0,'deletions':[]},indent=2),encoding='utf-8')
print(json.dumps({'integrated_reports':'updated','checkpoint':'updated','preserved_assets':len(assets),'UTC':stamp,'active_jobs':[],'neural_training':False,'paid_rental_usd':0,'deletions':[]}))
