
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

import pathlib
r=project_root(__file__);s=(project_path('research_round7_word_root_causal_v2.py', base=r)).read_text()
a=s.index('        if c==12:');b=s.index('        baseline=float(prefix[i]-prefix[lo])',a)
replacement='''        if c==12:
            if i<len(raw):i+=1;cls='literal_escape'
            else:cls='partial_escape_EOF'
            probs=np.zeros(len(words.family_names))
        elif c>=128:
            code=[c];partial=False
            while code[-1]>207 and len(code)<3:
                if i>=len(raw):partial=True;break
                code.append(inverse_byte(raw[i]));i+=1
            code=bytes(code)
            if partial:
                matches=[j for j,p in enumerate(codes) if p.startswith(code)]
                probs=sum((words.predictions(j,conditional=False) for j in matches),np.zeros(len(words.family_names)))
                cls='partial_dictionary_EOF'
            else:
                if code not in ids:raise ValueError('Invalid code at '+str(lo))
                w=ids[code];probs=words.predictions(w,conditional=False)
                cls='first_in_slice' if words.global_counts[w]==1 else 'known_first_in_article' if w not in words.article.counts else 'article_repeat'
                atoms+=1
        else:probs=np.zeros(len(words.family_names));cls='literal_syntax_or_case'
'''
s=s[:a]+replacement+s[b:]
s=s.replace("'neural_retraining':False},'by_occurrence_class'","'neural_retraining':False,'EOF':'partial prefixes are scored by summed prefix mass; partial escapes pay fallback'},'by_occurrence_class'")
# Fixture accounting checks every truncation after the synchronization marker.
needle="    print(json.dumps({'root_self_test':'passed'"
at=s.index(needle)
s=s[:at]+'''    sep=literal_wrt(SEP,fixture)
    for suffix in [bytes([240]),bytes([240,208]),bytes([12]),bytes([240,128]),bytes([240,208,128])]:
        fragment=sep+suffix
        got=screen(fragment,np.full(len(fragment),8.,np.float32),fixture)
        assert got['score']['baseline_suffix_bits']==len(suffix)*8,('EOF accounting',suffix)
''' + s[at:]
(project_path('research_round7_word_root_causal_v3.py', base=r)).write_text(s)
print('Created isolated v3; v2 and historical results preserved')
