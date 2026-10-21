import pathlib,json,hashlib,shutil
P=pathlib.Path('/kaggle/working/hp_round7');T=pathlib.Path('/kaggle/working/hp_round8/native_hidden_trace_v1/tree');o={'disks':{s:dict(zip(['total','used','free'],shutil.disk_usage(s))) for s in ['/root','/kaggle/working']},'assets':{},'phase_delete_lines':{}}
for name,p in [('old_order',P/'preserved/gen/.new_article_order'),('lex_order',T/'src/readalike_prepr/data/new_article_order'),('lex_dict',T/'dictionary/english.dic'),('old_dict',P/'preserved/gen/.dict')]:o['assets'][name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for n in ['src/readalike_prepr/misc.h','src/readalike_prepr/article_reorder.h','src/readalike_prepr/phda9_preprocess.h']:
 p=T/n;lines=p.read_text(errors='replace').splitlines();hits=[i for i,s in enumerate(lines) if any(v in s for v in ['remove(', 'unlink(', 'split4Comp(', 'selfextract_comp(', 'void cat', 'int cat'])];inds=sorted({j for i in hits for j in range(max(0,i-1),min(len(lines),i+5))});o['phase_delete_lines'][n]=[{'line':i+1,'text':lines[i]} for i in inds]
print(json.dumps(o))
