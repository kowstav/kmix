from pathlib import Path
r=Path(__file__).parent
old=(r/'research_round7_lex_finalbit_trace_worker.py').read_text(encoding='utf-8')
head=old[old.index('import datetime'):old.index('\ndef main():')]
head=head.replace("OUT = pathlib.Path('/kaggle/working/hp_round7')", "OUT = pathlib.Path('/kaggle/working/hp_round7')")
head=head.replace("DEST = OUT / 'lex_finalbit_trace_v1'", "DEST = pathlib.Path('/kaggle/working/hp_round8/native_hidden_trace_v1')")
head=head.replace("TREE = pathlib.Path('/root/hp/lex_finalbit_trace_v1')", "TREE = DEST / 'tree'")
head=head.replace('timeout=500)', 'timeout=1200)')
head=head.replace('from research_round7_lex_finalbit_trace_patch import exact_lab_changes, patch_texts', "import sys\nsys.path.insert(0, '/kaggle/working/hp_round7')\nfrom research_round7_lex_finalbit_trace_patch import exact_lab_changes, patch_texts")
body=r'''
def hidden_patch():
    header=TREE/'cpp_infer/src/opt/model_opt.h';cpp=TREE/'cpp_infer/src/opt/model_opt.cpp';pred=TREE/'src/predictor.cpp'
    h=header.read_text();c=cpp.read_text();p=pred.read_text()
    anchor='  const float* last_logits() const;'
    assert h.count(anchor)==1
    h=h.replace(anchor,anchor+'\n  // Observation only: final dynamically quantized biased-u8 representation.\n  const uint8_t* last_hidden_q8() const;')
    anchor='const float* TransformerOpt::last_logits() const { return impl->logits; }'
    assert c.count(anchor)==1
    c=c.replace(anchor,anchor+'\nconst uint8_t* TransformerOpt::last_hidden_q8() const { return impl->q5; }')
    anchor='  if (transformer_probs_writer_) {\n'
    assert p.count(anchor)==1
    export=r"""  // Trace belongs to the NEXT byte; reset rows cannot query stale activations.
  if (const char* path = std::getenv("LAB_HIDDENTRACE")) {
    static FILE* hp_hidden_file = std::fopen(path, "wbx");
    if (!hp_hidden_file) std::abort();
    unsigned char row[193] = {};
    if (!last_of_piece) {
      row[0] = 1;
      std::memcpy(row + 1, transformer_->last_hidden_q8(), 192);
    }
    if (std::fwrite(row, 1, sizeof(row), hp_hidden_file) != sizeof(row)) std::abort();
  }
"""
    p=p.replace(anchor,export+anchor)
    # Anchor validation precedes all mutations.
    for path,text in [(header,h),(cpp,c),(pred,p)]:path.write_text(text)
    return {str(path.relative_to(TREE)):sha(path) for path in [header,cpp,pred]}

def main():
    assert not DEST.exists(), 'No duplicate native hidden trace launch'
    assert shutil.disk_usage(OUT).free>3_000_000_000
    DEST.mkdir()
    m={'status':'RUNNING','pid':os.getpid(),'session':355655943,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_retraining':False,'paid_rental_usd':0,'deletions':[],'scope':'observation-only native hidden trace and cold-core diagnostic','controls':[],'exports':[]}
    def save(stage):
      m['stage']=stage;(DEST/'manifest.json').write_text(json.dumps(m,indent=2));print(json.dumps({'status':m['status'],'stage':stage}),flush=True)
    try:
      assert sha(OUT/'lex_audit/lex_h1_run11.tfwc2')==WEIGHT_SHA
      save('isolated source restoration');m['sources']=extract_sources();m['hidden_patch_sha256']=hidden_patch()
      save('exact compiler restoration');path=restore_compiler();env={**os.environ,'PATH':path}
      m['compiler']=subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0];m['classical_flags']=FLAGS;m['transformer_flags']=TF
      save('native observation-only build');start=time.monotonic()
      with (DEST/'build.log').open('x') as f:subprocess.run(['make','-B','-j2','cmix','CC=clang++-17','CM_OPT=-O2','CFLAGS_DEFINES='+FLAGS,'CFLAGS_TF_DEFINES='+TF],cwd=TREE,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1800)
      m['build_wall_seconds']=time.monotonic()-start;binary=DEST/'cmix_hidden_trace';shutil.copy2(TREE/'cmix',binary);m['binary']={'sha256':sha(binary),'bytes':binary.stat().st_size}
      weights=OUT/'lex_audit/lex_h1_run11.tfwc2';base=OUT/'lex_finalbit_trace_v1/cmix_trace'
      e={k:v for k,v in env.items() if not k.startswith('LAB_')};e.update(LAB_RAW='1',LAB_VOCAB=str(OUT/'preserved/data/vocab.bm'),LAB_DICT=str(OUT/'preserved/gen/.dict'),LAB_KEEP_TEMP='1')
      for s in 'ab':
       raw=(OUT/'preserved/slices'/(s+'2m.bin')).read_bytes()[:32768];inp=DEST/(s+'32k.bin');inp.write_bytes(raw);runs={}
       for mode,program in [('reference',base),('hidden',binary)]:
        d=DEST/(s+'_'+mode);d.mkdir();(d/'.dict').symlink_to(OUT/'preserved/gen/.dict');ee={**e,'LAB_BITTRACE':str(d/'final_p.u16')}
        if mode=='hidden':ee['LAB_HIDDENTRACE']=str(d/'hidden.q8')
        runs[mode]=timed([str(program),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,ee,s+'_'+mode)
       a,b=DEST/(s+'_reference'),DEST/(s+'_hidden');assert (a/'out.cmx').read_bytes()==(b/'out.cmx').read_bytes();assert (a/'final_p.u16').read_bytes()==(b/'final_p.u16').read_bytes()==(OUT/'lex_finalbit_2m_v1'/s/'final_p.u16').read_bytes()[:16*len(raw)];assert (b/'hidden.q8').stat().st_size==193*len(raw)
       d=DEST/(s+'_decode');d.mkdir();(d/'.dict').symlink_to(OUT/'preserved/gen/.dict');runs['decode']=timed([str(binary),'--transformer',str(weights),str(b/'out.cmx'),'decoded.bin'],d,{**e,'LAB_HIDDENTRACE':str(d/'hidden.q8')},s+'_decode');assert (d/'decoded.bin').read_bytes()==raw;assert (d/'hidden.q8').read_bytes()==(b/'hidden.q8').read_bytes()
       m['controls'].append({'slice':s,'archive_identity':True,'integer_trace_identity':True,'raw_decode_exact':True,'hidden_encode_decode_identical':True,'hidden_bytes':193*len(raw),'hidden_sha256':sha(b/'hidden.q8'),'archive_sha256':sha(b/'out.cmx'),'accounting':runs});save('32K native identity/decode '+s+' PASS')
      m['status']='NATIVE_IDENTITY_PASS_EXPORTING';save('cold128K hidden trace export')
      for s in 'abcd':
       src=OUT/'preserved/slices'/(s+'2m.bin') if s in 'ab' else OUT/(s+'2m.bin');inp=DEST/(s+'128k.bin');inp.write_bytes(src.read_bytes()[:131072]);d=DEST/(s+'_128k');d.mkdir();(d/'.dict').symlink_to(OUT/'preserved/gen/.dict');ee={**e,'LAB_BITTRACE':str(d/'final_p.u16'),'LAB_HIDDENTRACE':str(d/'hidden.q8')};account=timed([str(binary),'-n','--transformer',str(weights),str(inp),'out.cmx'],d,ee,s+'_128k');p=(d/'final_p.u16').read_bytes();assert p==(OUT/'lex_finalbit_2m_v1'/s/'final_p.u16').read_bytes()[:16*131072];rows=np.fromfile(d/'hidden.q8',np.uint8).reshape(-1,193);assert len(rows)==131072 and np.all(rows[:,0]<=1)
       m['exports'].append({'slice':s,'input_bytes':131072,'input_sha256':sha(inp),'hidden_sha256':sha(d/'hidden.q8'),'hidden_valid_rows':int(rows[:,0].sum()),'final_p_sha256':sha(d/'final_p.u16'),'integer_trace_identity':True,'accounting':account});save('cold128K export '+s+' PASS')
      m.update(status='COMPLETE_NATIVE_HIDDEN_IDENTITY_AND_EXPORTS',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save('ready for preregistered causal cache replay')
    except BaseException as ex:m.update(status='FAIL',error=repr(ex),traceback=traceback.format_exc());save('failure preserved; no automatic duplicate launch');raise

if __name__=='__main__':main()
'''
(r/'research_round8_native_hidden_trace_worker.py').write_text(head+body,encoding='utf-8')
print('Generated observation-only native worker')
