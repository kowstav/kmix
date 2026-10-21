from pathlib import Path
import json,datetime
r=Path(__file__).parent
def rpc(name):
 j=json.loads((r/name).read_text(encoding='utf-8'));return json.loads(''.join(v['text'] for v in j['streams'] if v['name']=='stdout'))
n=rpc('research_round8_native_hidden_finish_v4_launch_result.json');c=rpc('research_round8_hidden_cache_v3_launch_result.json')
text=f'''## ACTIVE NATIVE CACHE EXTENSION — 6 October 2026 09:00 UTC

Kaggle 355655943: native identity/decode/export `hp_round8/native_hidden_trace_v4`
PID {n['launched_pid']}; dependent cache controller PID {c['pid']} writes
`hidden_cache_v3_controller_status.json`. The eventual results directory is
`hp_round8/hidden_cache_v2` (nine heads; seven pre-observation source features).
Read manifests and ps before acting; never duplicate a live job. Controller v3
starts fitting only after all exact native prerequisites pass.

V1 build succeeded but controller required missing /usr/bin/time; v2 used wait4
then found a restored reference binary without executable permission; v3 copied
and chmodded that reference and proved A archive/trace identity, then its decode
invocation omitted -d. V4 uses explicit -d and reuses those completed A encodings
and the existing compiled observation-only binary. All failures/logs preserved;
earlier A encoding process accounting was not saved by the failing controller.
No parity thresholds are relaxed. Decode must reproduce raw data AND hidden
traces. The initial queued cache controller failed its prerequisite and launched
no cache experiment; the new controller is its documented repair.

Registered rigorous method and future paths: research_round8_hidden_cache_math.md
and research_round8_hidden_cache_protocol.md. Short FIFO128/FIFO512, compact
projection, long-term reservoir512, same-history target permutations, recency and
a joint convex head are tested. No hidden-cache compression result exists yet.
This is a frozen-core cold-native diagnostic; actual residual coder integration,
whole-package accounting, warmed-core and fresh slices remain required.

Original nine R8 experiment families are complete. The first evidence bundle is
research_round8_evidence.zip; all 189 files and 24 independent Q16 traces validate.
This native extension is later than that bundle and must be preserved separately.
All 95 families remain open; global optimality and 20% are unproved. The managed
Goal is usageLimited and was not resumed/replaced/mutated. Paid spending $0;
project deletions none. Official signed clang17/lld17 were restored remotely.

'''
p=r/'research_round7_checkpoint.md';s=p.read_text(encoding='utf-8');first=s.find('## ACTIVE ROUND 8 EXTENSION');nextold=s.find('##',first+3) if first>=0 else -1
# Preserve the historical checkpoint verbatim after this authoritative status.
p.write_text(text+s,encoding='utf-8')
report=r/'research_round8_report.md';s=report.read_text(encoding='utf-8');s+='''

## 15. Native representation cache extension (registered, running)

The first evidence bundle validated 189 files. Subsequent work now instruments
the current native C3 hidden representation without changing its probabilities.
The first A32K arithmetic archive and final Q16 trace are exactly unchanged.
Full independent decoding and the B identity controls must pass before any fit.
Controller repairs are documented in the checkpoint; failures remain intact.

This extends the design-only pre-word cache proposed above into an actual native
**byte-target** pilot. Its full equations and engineering are in
[research_round8_hidden_cache_math.md](research_round8_hidden_cache_math.md),
and the preregistered protocol is
[research_round8_hidden_cache_protocol.md](research_round8_hidden_cache_protocol.md).
Nine heads compare FIFO128, FIFO512, a fixed 32-coordinate projection, long-lived
reservoir512, matched target permutations, ordinary recency, generic calibration
and a joint model. A/B development fitting is frozen on C/D. None of these is
yet a measured cache compression gain. Production/native integration, true warm
history, fresh slices and package qualification remain open.

The actual Predictor already instantiates KVI8, so its documented 1.7 MB cache
saving cannot be claimed again as space for this extension. The conservative
full-program margin remains 615,424 bytes. A successful compact production
cache must be measured inside that whole-program peak.
''';report.write_text(s,encoding='utf-8');print('Saved active native/cache handoff with actual PIDs')
