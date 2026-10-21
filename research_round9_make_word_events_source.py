from pathlib import Path
s=Path('research_round9_word_alignment.cpp').read_text()
s=s.replace('if(argc!=6)return 10;','if(argc!=7)return 10;')
s=s.replace('uint64_t limit=strtoull', 'std::ifstream wf(argv[6]); std::vector<std::pair<uint64_t,uint64_t>> windows; uint64_t wa,wb; while(wf>>wa>>wb) windows.push_back({wa,wb}); uint64_t completion=0,selected=0;\n uint64_t limit=strtoull')
old='fprintf(out,"%llu\\t%llu\\t%d\\t%s\\n",(unsigned long long)wordlo,(unsigned long long)wordhi,wordtext,word.c_str());wordcount++;'
new='for(size_t w=0;w<windows.size();w++) if(wordlo>=windows[w].first+16 && completion<=windows[w].second) {fprintf(out,"%zu\\t%llu\\t%llu\\t%llu\\t%d\\t%s\\n",w,(unsigned long long)wordlo,(unsigned long long)wordhi,(unsigned long long)completion,wordtext,word.c_str());selected++;} wordcount++;'
assert old in s;s=s.replace(old,new).replace('if(!remaining){flush();','if(!remaining){completion=ftell(in);flush();').replace('for(unsigned char ch:expansion){','completion=hi; for(unsigned char ch:expansion){')
s=s.replace('"native_byte_comparison\\\":\\\"PASS','"native_byte_comparison\\\":\\\"PASS') # keep original comparison contract
Path('research_round9_word_events.cpp').write_text(s)
