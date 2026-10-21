import pathlib, tarfile, json, subprocess
out=pathlib.Path('/kaggle/working/hp_round7')
archive=out/'preserved/research_sources_and_candidates.tar.gz'
rows=[]
with tarfile.open(archive,'r:gz') as tar:
    for item in tar:
        n=item.name
        if 'lex' in n or 'makefile' in n.lower() or n.endswith('main.cpp'):
            rows.append({'name':n,'bytes':item.size,'regular':item.isfile()})
        if item.isfile() and ('lex' in n) and ('readme' in n.lower() or n.endswith('config.json') or n.endswith('export_weights.py')):
            f=tar.extractfile(item)
            txt=f.read(60000).decode('utf8',errors='replace') if f else ''
            (out/('audit_'+pathlib.PurePosixPath(n).name)).write_text(txt)
            print('SOURCE',n,txt[:5000])
(out/'preserved_lex_inventory.json').write_text(json.dumps(rows,indent=2))
print('LEX_INVENTORY',json.dumps([r for r in rows if ('lex' in r['name']) and (r['bytes']>100000 or r['name'].count('/')<5)],indent=2)[:18000])
print('PTQ_RUNNING','\n'.join(x for x in subprocess.check_output(['ps','-eo','pid,etime,rss,args'],text=True).splitlines() if 'cmix_round7_v5 ' in x))
