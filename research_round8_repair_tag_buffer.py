from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'research_round8_clean_title_v2.cpp').read_text(encoding='utf-8')
replacements={
'string tagbuf,entitybuf;uint64_t page_event0=0;':'string tagbuf,tagtail,entitybuf;uint64_t page_event0=0,tag_truncations=0;',
'punct=3;tag=false;tagbuf.clear();quote=0;':'punct=3;tag=false;tagbuf.clear();tagtail.clear();quote=0;',
'if(tag){tagbuf+=c;if(tagbuf.size()>4096)throw runtime_error("XML observer tag bound exceeded");':'if(tag){if(tagbuf.size()<128)tagbuf+=c;else if(tagbuf.size()==128){tagbuf+=char(0);tag_truncations++;}tagtail+=c;if(tagtail.size()>3)tagtail.erase(tagtail.begin());',
'if(tagbuf.size()>=3&&tagbuf.substr(tagbuf.size()-3)=="-->")close_tag();':'if(tagtail=="-->")close_tag();',
"if(c=='<'){commit();tag=true;tagbuf.clear();quote=0;continue;}":"if(c=='<'){commit();tag=true;tagbuf.clear();tagtail.clear();quote=0;continue;}",
'auto events=x.events;x.chars("uncompleted&#",3);':'x.chars("<!--"+string(6000,\'x\')+">\\\"abc\\\"--> the ",1);if(x.tag||x.tagbuf.size()>129||x.tag_truncations!=1)throw runtime_error("bounded long comment");auto events=x.events;x.chars("uncompleted&#",3);',
}
for a,b in replacements.items():
    assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
(R/'research_round8_clean_title_v3.cpp').write_text(s,encoding='utf-8')
for name in ['worker','launch']:
    s=(R/f'research_round8_clean_title_v2_{name}.py').read_text(encoding='utf-8')
    s=s.replace('clean_title_v2','clean_title_v3')
    if name=='worker':
        s=s.replace("'repair':'Self-test fixture expected 4 aardvarks but contains 3; only the assertion changes. v1 source/binary/log/manifest preserved.'", "'repair':'v1 fixture-count repair preserved; v2 failed on a >4096-byte tag/comment. v3 keeps a bounded 129-byte tag prefix and 3-byte closing tail, and tracks quotes independently; adds a 6000-byte comment test. No probability-family or promotion threshold change.'")
        s=s.replace("pilots=[evaluate(s,131072) for s in 'ab'];pairs=", "pilots=[evaluate(s,131072) for s in 'ab'];old=json.loads((R/'clean_title_v2/a_128k.json').read_text());new=m['results'][0];assert [a['prediction_hash'] for a in old['arms']]==[a['prediction_hash'] for a in new['arms']], 'A replay changed unexpectedly';m['a_predictions_match_completed_v2']=True;save();pairs=")
    (R/f'research_round8_clean_title_v3_{name}.py').write_text(s,encoding='utf-8')
