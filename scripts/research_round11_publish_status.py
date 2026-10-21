"""Publish current observations without overwriting sealed round-10 evidence."""

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

from pathlib import Path
import hashlib
import json

R=project_root(__file__)
CHECKPOINT='''# Current Hutter research checkpoint

Updated 7 October 2026, 07:55 UTC. Current authority: research_round11_report.md.
Previous round-10 checkpoint is preserved in
historical_reports/research_round7_checkpoint_through_round10_20261007.md.

## Live session and actual execution

CPU session 355983921 is connected; kernel faa5022a-7bc5-48d0-a03d-9d79f7978081.
Kaggle CLI authentication exists in the runtime environment; never print or copy
credentials. Use kaggle_research_client.mjs with the latest signed URL supplied
through HP_KAGGLE_BASE. Local command sandbox currently fails before spawning;
scoped exec_command require_escalated calls have passed automatic review.

Six CLI pushes returned exit zero, but only five actual resources are confirmed.
Creation selected slugs from titles; use chaoscpp/hutter-r10-cpu-article-order-proxy,
...-bf16-cut107-half, ...-bf16-cut1392-zero, ...-bf16-unweighted,
...-component-ppmd. The integer-mixer commit's resource remains unresolved;
CLI exit zero alone is insufficient because the wrapper prints API errors without
raising. Do not duplicate that launch or bypass any quota. Read the saved owner
inventory and ordinary actual-slug status/output APIs. Four model/component jobs
were last RUNNING; article-order COMPLETE and outputs pulled locally.

Private dataset chaoscpp/hutter-round10-private-cpu-assets-v1 was created once.
Every delivered entry SHA was verified. Asset ZIP: 14,923,064 B, SHA
9abfce6c48ca1b4c9d48fe99846e7a98147ea537ce89d67d6580a8cb8bdf2a59.
Preserve all four versioned dispatch manifests; early failures were CLI schema/
delivery fixes before kernel submissions. Current successful action record:
/kaggle/working/hp_round11/private_cpu_submission_v4_manifest.json.

## Active live-session jobs: inspect before any relaunch

- Warm atlas v2 PID 121, native child 125:
  /kaggle/working/hp_round11/warm_atlas_v2/manifest.json.
  Root scratch /root/hp_round11/warm_atlas_v2. Sequential 9,437,184 B from zero,
  1 MiB warmup, sixteen later 512 KiB windows; whole-prefix independent decode
  follows. Traces need ~7.75 GB root scratch. One early dependence cluster.
- Constructor/anchor proxy v1 PID 235:
  /kaggle/working/hp_round11/constructor_proxy_v1/manifest.json.
  Seven declared paid controls on three disjoint 128-page groups.
- Word first-appearance/constructor census v1 PID 237:
  /kaggle/working/hp_round11/word_coverage_v1/manifest.json.
  Full original corpus, strict ASCII casefold and differential comparison with
  the older Unicode-lower-before-regex census. Frequency/appearance labels are
  research assets, not free inference data.
- Exact word-cost v1 PID 240:
  /kaggle/working/hp_round11/word_cost_v1/manifest.json.
  Independently checks full-prefix WRT character decoding and completed word
  positions, then waits for the native cost trace and independent decode. No
  overlap/double-counting of coded word spans is allowed.

## Completed in round 11

- Corrected 16 KiB native preflight: 1,740 B archive, exact independent decode and
  serialized vocabulary identity. The old 4 KiB forced-vocabulary header omitted
  its bitmap; both old failed manifests are preserved locally. Original binary
  and weights unchanged.
- Paid article-order gzip proxy: 512 pages, original 1,542,475 B versus selected
  directed-swap 1,537,161 B, saving 5,314 B including order/length/header charges.
  Both local archive reconstructions match all 512 pages. This is not a canonical
  native or full-package record result.
- Twelve exact weight-codec arms: complete, all 435 native tensors preserved;
  default V3 export reproduces original SHA. Best V4 is original seed=960,
  limit=65536 plus eight paid header bytes, hence no saving. Other tested count
  settings also lose. This closes this finite sweep, not every weight-codec idea.
- Four V4 codec properties and three constructor-codec properties pass. Existing
  round-10 tests and sealed evidence remain historical; source changes must be
  independently verified rather than silently rewriting their old hashes.

## Remaining CPU and GPU work

Preserve terminal notebook outputs locally, including actual archives, accounting
and hashes. Run the declared integer/memory controls against the completed warm
atlas if its private commit cannot be resolved; reuse traces instead of launching
another native observer. Integrate promising laws into actual native encoding and
independent decoding, including neutral core-trajectory controls. Complete
representative strata, package/code size and eligible uncontended CPU/RAM checks.
Full 55-60 hour baseline requires a persistent host or verified exact checkpoints;
independent cold shards cannot replace its sequential state.

All 96 idea protocols: research_round10_96_scope.md; all 53 audit responses:
research_round10_audit_fixes.md and research_round10_audit_response.md. All 96 are
not thoroughly executed, and absolute best descendants are not established.
GPU work remains original-transformer continuation, full literal/OOV masks,
trained word/attention/geometry/TTL architectures and learned combinations.
Conditional 5090 pilot/hours and $70 allocation are detailed in
research_round10_training_and_5090_plan.md. No GPU session is needed yet.

Paid spending $0; no deletions in round 11. Preserve data, models and root scratch
needed by dependents. Managed Goal remains usageLimited and must not be
automatically resumed, replaced or bypassed. Automated follow-ups honor that
limit. Requested research week ends 11 October 2026.
'''

def main():
    (project_path('research_round7_checkpoint.md', base=R)).write_text(CHECKPOINT,encoding='utf-8')
    path=project_path('results/registry.jsonl', base=R)
    rows=[json.loads(line) for line in path.read_text().splitlines() if line]
    additions=[('R11-native-preflight-v4','COMPLETE_NATIVE_PREFLIGHT_PASS_SERIALIZED_VOCABULARY',
        'research_round11_preflight_v4_manifest.json','16 KiB prefix, actual archive 1740 B and independent exact reconstruction'),
        ('R11-article-order-v1','COMPLETE_PAID_ARTICLE_ORDER_GZIP_PROXY',
        'research_round11_article_order_manifest.json','5314 B paid gzip proxy saving; one early raw-page cluster, no production qualification'),
        ('R11-weight-codec-v1','COMPLETE_TWELVE_EXACT_CODEC_ARMS',
        'research_round11_weight_codec_manifest.json','All 435 tensors exact; no tested parameter arm beats original model bytes')]
    for ident,status,evidence,outcome in additions:
        source=project_path(evidence, base=R); assert source.exists()
        value=json.loads(source.read_text()); assert value['status']==status
        row={'id':ident,'status':status,'hypothesis':outcome,'outcome':outcome,
             'gate':'Exact reconstruction or tensor identity; whole-package claims require separate native/resources evidence',
             'data':{'session':355983921,'GPU':False,'paid_usd':0},
             'evidence':{'path':evidence,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}}
        rows=[r for r in rows if r['id']!=ident]; rows.append(row)
    assert len({r['id'] for r in rows})==len(rows)
    path.write_text(''.join(json.dumps(row)+'\n' for row in rows),encoding='utf-8')
    print(json.dumps({'checkpoint':'ROUND11_CURRENT','registry_rows':len(rows),'new_completed_results':len(additions)}))

if __name__=='__main__': main()
