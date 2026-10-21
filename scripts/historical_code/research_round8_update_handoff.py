from pathlib import Path
import datetime,json,re
R=Path(__file__).resolve().parent
def manifest(name):
 p=R/name
 return json.loads(p.read_text(encoding='utf-8')) if p.exists() else None
fixed=manifest('research_round8_fixed_semantic_manifest.json');directed=manifest('research_round8_directed_memory_manifest.json')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
states=[]
for name,m in [('fixed_semantic_v1',fixed),('directed_memory_v1',directed)]:
 states.append(f"{name}: {m['status']} (controller {m.get('pid')})" if m else f'{name}: latest snapshot RUNNING; inspect remote manifest before continuation')
complete=fixed and directed and fixed['status'].startswith('COMPLETE') and directed['status'].startswith('COMPLETE')
batch='FINITE REGISTERED BATCH COMPLETE. No active round8 job; overall research remains open.' if complete else 'REGISTERED BATCH HAS LIVE FOLLOW-UPS; inspect process snapshot and reuse jobs.'
header=f'''<!-- round8-current-start -->
# Latest handoff — Round8,6October2026

Updated {now}. Authorized human continuation on Kaggle355655943,
kernel e1c130f3-38ee-42f4-8e7e-30f834a5b0e4. Signed proxy is runtime/conversation
only. Managed Goal remains usageLimited: never automatically resume/replace it
or bypass it on heartbeats. No paid rental/core-transformer retraining/deletion.

{batch}

Read research_round8_report.md, research_round8_idea_program.md/JSON (all95
families remain OPEN), and the latest manifests. Do not relaunch completed dirs.
Early lab ledger recovered:18configs54distinct checkpoints270small passes;
reports3000steps, chronology versus old400-step R1 not certified.

Completed new frozen-core work: conditional gate fullABCD2M (generic27.923621B,
geometry/run16.996054B); paid policy-duration optimum (generic96.658488B versus
combined94.908488B/8M); exact finite dyadic weight KT diagnostic839.289567B/copy
before actual container/loader. None is a qualifying package result.

Clean title/XML observer repaired after preserved v1 fixture/v2 comment failures;
v4 fixes224 overlapping constructor/source-surprise keys. Warm source sees94.05%
dictionary words by100M WRT bytes but title/retrieval gates produce no useful gain;
CORE REMAINS COLD in that conditional diagnostic. Frozen GloVe graph covers
43939/44515words,613724B LZMA before framing; finite strength gate rejects it.

Continuous bounded residual discovers weaker semantic signal: frozenAB128K head
gives14.443476B onCD128K versus2.166226generic/3.712878shuffled. All six convex
box fits have numerical certificates <=0.000183B; this is not an absolute optimum.
Independent C++ matches all24integer prediction SHA256s exactly. No20% gain.

Current final follow-ups:
{chr(10).join(states)}
Fixed semantic freezes AB coefficients, confirms fullABCD2M, prices source-ID+
8neighbor sparse graphs, preserves additive counterfactual marginal arrays.
Directed memory rebuilds two1024x8 bounded association tables from true prefix,
fits tiny heads onAB and confirmsCD, no shipped GloVe. Source warm/core cold.
Read protocols and workers for exact contracts and promotion gates.

Final measured additions: frozen semantic191.944362B/8M versusgeneric33.134736B,
only0.012705%of sampled native likelihood cost, before613724B/copygraph. Exact
priced source-row subset selects0rows and loses27.035706B beforeloader. Directed
next-content source warm gives10.087630B onAB256K/8.823959B onCD256K, versus
generic0.571710/2.166226; after64Bcoefficient copies its sample package still loses.
Both have small controlled information, not a qualifying archive. Final summary:
research_round8_final_summary.json. All95families remain open. A new compact
native-hidden-state retrieval cache is DESIGN ONLY, not an active job.

Published full C3 peak9765024KiB=9999384576B; only615424B headroom under decimal
10GB. Existing cold6GB peak is insufficient. Compact shared state is mandatory.
Training70USD staged4/12/36/8/10, spent0. Layer-wise core parity still FAILED;
independent native-final-bit residual training is separately possible.

Remaining: actual C3 container coding, compact native residual, full production
lexical preparation/priors, fully warm core, freshG/H, main-text MDL grammar and
paid endpoint gaps, learned rejection/TTL/placement, training controls and full
self-contained qualifying package. Every new idea still needs all those gates;
no absolute-potential or researcher-equivalence claim. Week objective unachieved,
end11October2026. Older entries below are historical and superseded.
<!-- round8-current-end -->

'''
p=R/'research_round7_checkpoint.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- round8-current-start -->.*?<!-- round8-current-end -->\s*','',s,flags=re.S);p.write_text(header+s,encoding='utf-8')
p=R/'research_round7_report.md';s=p.read_text(encoding='utf-8');s=re.sub(r'<!-- round8-integration-start -->.*?<!-- round8-integration-end -->\s*','',s,flags=re.S)
note='''<!-- round8-integration-start -->
> **Round8 continuation,6October2026:** New actual experiments, repaired feature
> semantics, independent mathematical checks, finite optima, frozen semantic
> signal and remaining qualification gates are in
> [research_round8_report.md](research_round8_report.md).
> [The95-family continuation program](research_round8_idea_program.md) assigns
> stronger descendants and tests to every recoverable idea; none is fully explored.
> No record/package/20% improvement is asserted. Core weights stay frozen;
> no paid rental or deletion. Read the current checkpoint for live/completed jobs.
> Earlier running-status paragraphs below are historical.
<!-- round8-integration-end -->

'''
p.write_text(note+s,encoding='utf-8')
print(json.dumps({'updated':['research_round7_checkpoint.md','research_round7_report.md'],'latest_states':states}))
