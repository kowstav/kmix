
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
import ast,base64,hashlib,json,zipfile
R=project_root(__file__);O=project_path('kaggle_cpu_round14', base=R);zpath=O/'sources_guard_match_confirm_v8.zip';entries=[]
with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted((project_path('hutter_research', base=R)).rglob('*')):
        if not p.is_file() or p.suffix not in ('.py','.cpp','.h','.hpp','.inc') or '__pycache__' in p.parts:continue
        b=p.read_bytes();name=p.relative_to(R).as_posix()
        if p.suffix=='.py':ast.parse(b.decode('utf-8'))
        z.writestr(name,b);entries.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    z.writestr('source_manifest.json',json.dumps(entries,indent=2))
blob=zpath.read_bytes();digest=hashlib.sha256(blob).hexdigest();jobs=[]
template=(O/'hutter-r14-guard-match-development-v1/main.py').read_text()
start=template.index('b=base64.b64decode(');end=template.index("\nr=Path(",start)
template=template[:start]+"b=base64.b64decode("+repr(base64.b64encode(blob).decode())+");assert hashlib.sha256(b).hexdigest()=="+repr(digest)+template[end:]
for role,regions in [('a',[8,10,12,14]),('b',[9,11,13,15])]:
    slug='hutter-r14-guard-match-confirm-'+role+'-v1';d=O/slug;d.mkdir()
    main=template.replace("if __name__=='__main__':main()", "if __name__=='__main__':main(regions="+repr(regions)+",run_label='confirmation_"+role+"')")
    ast.parse(main);(d/'main.py').write_bytes(main.encode())
    meta=json.loads((O/'hutter-r14-guard-match-development-v1/kernel-metadata.json').read_text());meta.update(id='chaoscpp/'+slug,title=slug)
    (d/'kernel-metadata.json').write_text(json.dumps(meta,indent=2))
    jobs.append({'ref':meta['id'],'folder':slug,'role':role,'region_ids':regions,'main_sha256':hashlib.sha256(main.encode()).hexdigest()})
with zipfile.ZipFile(O/'kernels_guard_match_confirm_v8.zip','x',zipfile.ZIP_DEFLATED) as z:
    for j in jobs:
        for p in (O/j['folder']).iterdir():z.write(p,p.relative_to(O).as_posix())
prep={'source_sha256':digest,'jobs':jobs,'binary_unchanged':True,'gpu':False,'workers_per_job':4}
(O/'prepared_guard_match_confirm_v8.json').write_text(json.dumps(prep,indent=2));print(json.dumps(prep))
