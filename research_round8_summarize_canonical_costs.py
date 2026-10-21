import json
from pathlib import Path
R=Path(__file__).parent
ms=[json.loads((R/f'research_round8_canonical_cost_atlas_{s}.json').read_text()) for s in 'ab']
assert all(m['log_posterior_odds_used'] and abs(m['independent_batch_mixture_bits_error'])<1e-5 and abs(m['cost_reconciliation_bits_error'])<1e-5 for m in ms)
total=sum(m['total_native_likelihood_bytes'] for m in ms);costs={}
for m in ms:
 for k,v in m['class_cost_bytes'].items():costs[k]=costs.get(k,0)+v
summary={'scope':'canonical cold 512KiB A/B; all final native code-path bits; no C/D used','total_native_likelihood_bytes':total,'class_cost_bytes':costs,'class_native_cost_percent':{k:100*v/total for k,v in costs.items()},'fixed_KT_saving_bytes':sum(m['KT_total_saving_bytes'] for m in ms),'global_half_identity_Q16_mixture_saving_bytes':sum(m['identity_plus_KT_Q16_saving_bytes'] for m in ms),'batch_exact_mixture_ideal_saving_bytes':sum(m['batch_exact_mixture_ideal_saving_bytes'] for m in ms),'max_stream_vs_batch_roundoff_bits':max(abs(m['independent_batch_mixture_bits_error']) for m in ms),'full_word_or_full_corpus_coverage_claim':False,'recoverable_saving_bound_claim':False}
(R/'research_round8_canonical_cost_atlas_summary.json').write_text(json.dumps(summary,indent=2))
classes='\n'.join(f"| {k} | {v:.3f} | {100*v/total:.3f}% |" for k,v in costs.items())
wordtables=[]
for s,m in zip('ab',ms):
 rows='\n'.join(f"| {r['label']} | {r['occurrences']} | {r['native_bits']/8:.3f} | {r['mean_bits_per_atom']:.3f} |" for r in m['dictionary_words_top100'][:15])
 wordtables.append(f'''### Slice {s.upper()}

| Dictionary word | All occurrences | Cumulative native bytes | Mean bits per atom |
|---|---:|---:|---:|
{rows}
''')
text=f'''# Which words cost the native coder bits?

Canonical lexical cold A0/B102635191, 512KiB each. The native prediction/source hashes, complete category totals, top100 dictionary words and all causal-cluster rows are in the adjacent a/b JSON files. This is a completed finite cost attribution, not a compressed candidate or a full-corpus linguistic analysis.

## Same-event totals

All1MiB of prepared bytes account for {total:.6f}bytes of native ideal arithmetic likelihood. Every coded bit is included. Category reconciliation errors are below1e-5bit. Header synchronization, literal/control bytes, escapes and partial EOF are not discarded. Actual archives have coder/header/termination overhead, so a likelihood saving is not automatically an archive-byte saving.

| Assigned category | Native likelihood bytes | Share of native bit cost |
|---|---:|---:|
{classes}

The predeclared constructor list accounts for12.848% of this sample's native cost. This is useful evidence about allocation, not a bound on all grammatical language or the full archive: the list is incomplete, is not POS tagging, and excludes separate casing/spacing/control costs. Even perfectly predicting all codes in this particular list would erase only their assigned20,189.557bytes while holding the rest fixed; a complete alternative codec also pays structure and ordering. A grammar-only breakthrough cannot be assumed from their raw occurrence frequency. Other dictionary atoms and literal/control channels need joint attention.

## Cumulative difficulty differs from a spectacular single mistake

{''.join(wordtables)}
For example, B's “the” averages2.043bits per dictionary atom but consumes1,807.191bytes cumulatively. “An” costs5.223bits per occurrence yet only390.450bytes in that slice. “Telephone” is a repeatable topic atom with1,013occurrences and4.074bits/atom. A's “of” is already cheap at0.486bits/atom. These are possible specialist targets; their current cost is not recoverable saving, and capitalization/role/all other bits must still be modeled.

A contains3,761distinct dictionary words and B7,778, in a44,515entry dictionary. Those are local slice counts, not the percentage of all200,000linguistic word types previously observed by the actual full decoder. They cannot answer the original first-occurrence coverage question. Rare out-of-dictionary lexical words are partly represented by literal/control/escape sequences here, so this report does not pretend to rank every rare linguistic word. Full warm coverage and exact reconstructed lexical-word attribution remain separate work.

## Causal clusters: a useful negative control

The3840possible contexts use only previous completed atom class, current atom byte depth, current byte bit position and native p1 bucket. No unknown target word or observed current surprise enters the assignment. KT(.5,.5) counts pay their cold estimation through complete prequential loss. On A/B this fixed cluster law loses {abs(summary['fixed_KT_saving_bytes']):.6f}bytes against native identity. A global half-prior mixture with native identity limits ideal regret to1bit per reset and loses {abs(summary['global_half_identity_Q16_mixture_saving_bytes']):.9f}bytes after Q16 rounding. This is not a positive compression result.

Direct posterior storage saturated in the failed v2 audit, irreversibly eliminating an expert. V4 uses cumulative log posterior odds and checks an independently computed batch likelihood normalizer. Its maximum streamed accumulation discrepancy is {summary['max_stream_vs_batch_roundoff_bits']:.9g}bits; the batch ideal regret is0.125byte per slice and the Q16 tax is measured separately. Failed versions and logs remain preserved. This matters for every proposed long-horizon Bayesian expert mixture: an algebraic regret proof does not by itself prove the floating implementation preserves the weights.

## Use this ledger for the attachment's next tests

1. Retain the original native p, target, piece/reset and offset for real residual supervision. Rank cumulative cost and recurrence, then test whether a prefix-visible relation predicts signed residual error after the existing p is known.
2. Compare ordinary and costly occurrences, false associations, constructor/content roles and literal/XML channels. Use same-size generic, shuffled-pair and null controls. Test every activation, not just the ones that helped.
3. Separate unbiased replay, deliberately weighted curriculum and synthetic auxiliary tasks. Fresh synthetic prefixes require consistent regenerated native states/priors if used as supervised core examples.
4. Freeze choices before independent native checks. Measure complete package, CPU/RAM and warmed history. An apparent entropy gap or cost budget is not recovered bytes; coefficients amortize over the full file and cold screens cannot establish that rate.

The experiment protocol was registered before outcomes. No C/D was read for this audit, no core was trained, no paid compute was used and no project data was deleted. See research_round8_canonical_cost_atlas_protocol.md and research_round8_attachment_training_addendum.md.
'''
(R/'research_round8_canonical_cost_atlas_report.md').write_text(text,encoding='utf-8')
print(json.dumps(summary,indent=2))
