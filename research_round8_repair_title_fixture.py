from pathlib import Path
R=Path(__file__).resolve().parent
src=(R/'research_round8_clean_title.cpp').read_text(encoding='utf-8')
needle='x.counts[x.ids.at("aardvark")]!=4'
assert src.count(needle)==1
# Fixture has one title occurrence plus two body occurrences, not four.
(R/'research_round8_clean_title_v2.cpp').write_text(src.replace(needle,'x.counts[x.ids.at("aardvark")]!=3'),encoding='utf-8')
for name in ['worker','launch']:
    s=(R/f'research_round8_clean_title_{name}.py').read_text(encoding='utf-8')
    s=s.replace('clean_title_v1','clean_title_v2').replace('research_round8_clean_title.cpp','research_round8_clean_title_v2.cpp').replace('research_round8_clean_title_worker.py','research_round8_clean_title_v2_worker.py')
    if name=='worker':s=s.replace("'core_retraining':False}","'core_retraining':False,'repair':'Self-test fixture expected 4 aardvarks but contains 3; only the assertion changes. v1 source/binary/log/manifest preserved.'}")
    (R/f'research_round8_clean_title_v2_{name}.py').write_text(s,encoding='utf-8')
