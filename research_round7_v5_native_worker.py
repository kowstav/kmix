import pathlib,subprocess,shutil,json,hashlib,time,sys
hp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7');base=hp/'round7_lab';v5=hp/'round7_v5'
if v5.exists():
    if '--resume-build' not in sys.argv:raise RuntimeError('Refuse overwriting an existing build')
else:shutil.copytree(base,v5,symlinks=True)
shutil.copyfile(out/'v5_weights_io_compressed.cpp',v5/'cpp_infer/src/weights_io_compressed.cpp')
flags=['-m64','-std=c++17','-Os','-march=x86-64-v3','-mtune=generic','-mrecip=none','-fno-math-errno','-fdata-sections','-ffunction-sections']
for name,root in [('old',base),('v5',v5)]:
    cmd=['clang++-17',*flags,'-I'+str(root/'cpp_infer/src'),str(out/'research_round7_tensor_dump.cpp'),str(root/'cpp_infer/src/weights_io.cpp'),str(root/'cpp_infer/src/weights_io_compressed.cpp'),'-Wl,--gc-sections','-o',str(out/('tensor_dump_'+name))]
    subprocess.run(cmd,check=True)
subprocess.run(['clang++-17',*flags,'-c','cpp_infer/src/weights_io_compressed.cpp','-o','tf_weights_io_compressed.o'],cwd=v5,check=True)
objs=['bit-context','bracket-context','bracket','byte-mixer','byte-model','combined-context','context-hash','context-manager','decoder','dictionary','direct-hash','direct','encoder','indirect-hash','indirect','interval-hash','interval','match','mixer-input','mixer','nonstationary','fxcmv1','ppmd','predictor','preprocessor','run-map','runner','sigmoid','sparse','sse','tf_weights_io','tf_weights_io_compressed','tf_qmat_dense','tf_qmat_sparse','tf_attn','tf_kda','tf_glue','tf_arena_build','tf_model_opt']
subprocess.run(['clang++-17','-m64','-Wl,--gc-sections','-std=c++17',*[x+'.o' for x in objs],'-s','-o','cmix'],cwd=v5,check=True)
print(json.dumps({'unpacked_original_executable_bytes':(base/'cmix').stat().st_size,'unpacked_v5_executable_bytes':(v5/'cmix').stat().st_size,'all_other_object_files_unchanged':all((base/(x+'.o')).read_bytes()==(v5/(x+'.o')).read_bytes() for x in objs if x!='tf_weights_io_compressed')}),flush=True)
for _ in range(360):
    if 'V5_CODEC_COMPLETE' in (out/'v5_codec.log').read_text():break
    if 'Traceback' in (out/'v5_codec.log').read_text():raise RuntimeError('Python codec failed')
    time.sleep(2)
else:raise RuntimeError('Codec worker did not finish')
results=[]
for name,path in [('reference',out/'reference.fx2tfwc2'),('candidate_bf16',hp/'cand_final2/run/comp_tfweights')]:
    dumps=[];times=[]
    for loader,weights in [('old',path),('v5',out/(name+'.fx2tfwc5'))]:
        dest=out/(name+'.'+loader+'.cpp_raw.bin');started=time.monotonic()
        subprocess.run([str(out/('tensor_dump_'+loader)),str(weights),str(dest)],check=True)
        dumps.append(dest);times.append(time.monotonic()-started)
    if dumps[0].read_bytes()!=dumps[1].read_bytes():raise RuntimeError('Native decoded tensor data differs')
    row={'name':name,'cpp_sorted_tensor_serialization_bytes':dumps[0].stat().st_size,'cpp_sorted_tensor_serialization_sha256':hashlib.sha256(dumps[0].read_bytes()).hexdigest(),'all_native_decoded_tensor_bytes_equal':True,'loader_seconds_old':times[0],'loader_seconds_v5':times[1],'original_executable_bytes':(base/'cmix').stat().st_size,'v5_executable_bytes':(v5/'cmix').stat().st_size}
    results.append(row);(out/'v5_native_verification.json').write_text(json.dumps(results,indent=2));print(json.dumps(row),flush=True)
shutil.copyfile(v5/'cmix',out/'cmix_round7_v5')
print('V5_NATIVE_COMPLETE',flush=True)
