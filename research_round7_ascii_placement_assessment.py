import collections,json,pathlib
p=pathlib.Path(__file__).parent
rows=json.loads((p/'research_round7_ascii_placement_audit_v1_summary.json').read_text())
counts=collections.Counter();pairs=collections.Counter();n=0
for r in rows:
    n+=r['ascii_word_events']
    for w,v in r['word_stats'].items():counts[w]+=v['count']
    for v in r['example_pairs']:pairs[v['scope'],v['source'],v['target'],v['lag_ASCII_words']]+=v['pair_count']
r={'ascii_word_events':n,'word_counts':dict(counts),
   'now_know_selected_lags':[{'scope':s,'source':u,'target':v,'lag_ASCII_words':d,'count':pairs[s,u,v,d]}
                             for s in ['article','raw_punctuation_segment'] for u,v in [('now','know'),('know','now')]
                             for d in [1,2,3,4]],
   'interpretation':'Full ASCII words including literal I/i and markup; previously inspected cold8M; descriptive, not codec gain or whole corpus'}
(p/'research_round7_ascii_placement_assessment.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
