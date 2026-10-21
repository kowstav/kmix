
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
s=project_path('research_round9_word_alignment.cpp').read_text()
s=s.replace('if(argc!=6)return 10;','if(argc!=7)return 10;')
s=s.replace('uint64_t limit=strtoull', 'std::ifstream wf(argv[6]); std::vector<std::pair<uint64_t,uint64_t>> windows; uint64_t wa,wb; while(wf>>wa>>wb) windows.push_back({wa,wb}); uint64_t completion=0,selected=0;\n uint64_t limit=strtoull')
old='fprintf(out,"%llu\\t%llu\\t%d\\t%s\\n",(unsigned long long)wordlo,(unsigned long long)wordhi,wordtext,word.c_str());wordcount++;'
new='for(size_t w=0;w<windows.size();w++) if(wordlo>=windows[w].first+16 && completion<=windows[w].second) {fprintf(out,"%zu\\t%llu\\t%llu\\t%llu\\t%d\\t%s\\n",w,(unsigned long long)wordlo,(unsigned long long)wordhi,(unsigned long long)completion,wordtext,word.c_str());selected++;} wordcount++;'
assert old in s;s=s.replace(old,new).replace('if(!remaining){flush();','if(!remaining){completion=ftell(in);flush();').replace('for(unsigned char ch:expansion){','completion=hi; for(unsigned char ch:expansion){')
s=s.replace('"native_byte_comparison\\\":\\\"PASS','"native_byte_comparison\\\":\\\"PASS') # keep original comparison contract
project_path('research_round9_word_events.cpp').write_text(s)
