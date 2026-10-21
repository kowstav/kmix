import datetime,json,os,pathlib,time,traceback
import numpy as np
import research_round7_word_root_causal_v3 as root
from research_round7_word_newmention_screen import NewMentionWords
from research_round7_wrt import load_dictionary
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'root_eof_v3';assert not D.exists();D.mkdir();m={'status':'RUNNING','pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deletions':[]};rows=[]
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2));(D/'results.json').write_text(json.dumps(rows,indent=2))
save()
try:
 root.self_test();root.Words=NewMentionWords;dictionary=load_dictionary(R/'preserved/gen/.dict')
 for n in 'abcd':
  p=R/'preserved/slices'/(n+'2m.bin') if n in 'ab' else R/(n+'2m.bin');cost=R/'lex_finalbit_2m_v1'/n/'cost.f32'
  row=root.screen(p.read_bytes(),np.fromfile(cost,'<f4'),dictionary);row['slice']=n;assert abs(row['score']['baseline_suffix_bits']-float(np.fromfile(cost,'<f4')[row['unscored_prefix_bytes']:].astype(np.float64).sum()))<1e-7
  (D/(n+'.json')).write_text(json.dumps(row,indent=2));rows.append(row);save();print(json.dumps({'P02_slice':n,'saving':row['score'].get('prequential_saving_bytes'),'events':row['score']['events']}),flush=True)
 m['status']='COMPLETE';save()
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
