def _hp_prepare_trace():
    import pathlib,shutil,subprocess,json
    hp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7')
    dst=hp/'round7_trace'
    if dst.exists():raise RuntimeError('Trace build already exists')
    shutil.copytree(hp/'round7_lab',dst)
    p=dst/'src/coder/encoder.cpp'; s=p.read_text()
    s=s.replace('#include <cmath>\n','#include <cmath>\n#include <cstdio>\n#include <cstdlib>\n#include <cstdint>\nstatic FILE* hp_bit_trace = nullptr;\n')
    anchor='  const unsigned int p = Discretize(p_->Predict());\n'
    if s.count(anchor)!=1:raise RuntimeError('Trace anchor mismatch')
    s=s.replace(anchor,anchor+'  if (std::getenv("LAB_BITTRACE")) {\n    if (!hp_bit_trace) hp_bit_trace = std::fopen(std::getenv("LAB_BITTRACE"), "wb");\n    if (!hp_bit_trace) std::abort();\n    const uint16_t quantized = static_cast<uint16_t>(p);\n    std::fwrite(&quantized, sizeof(quantized), 1, hp_bit_trace);\n  }\n')
    flush='void Encoder::Flush() {\n'
    s=s.replace(flush,flush+'  if (hp_bit_trace) { std::fclose(hp_bit_trace); hp_bit_trace = nullptr; }\n')
    p.write_text(s)
    # Only Encoder changed; reuse matched native model object files.
    worker=out/'build_trace_worker.py'
    worker.write_text('''import pathlib,subprocess,shutil,json
hp=pathlib.Path('/root/hp'); out=pathlib.Path('/kaggle/working/hp_round7'); dst=hp/'round7_trace'
flags=['-DSEED=923','-DUPDATE_LIMIT=3000','-m64','-Wall','-std=c++17','-ffp-model=fast','-fno-exceptions','-fno-threadsafe-statics','-march=x86-64-v3','-mtune=generic','-mrecip=none','-O3','-fdata-sections','-ffunction-sections']
subprocess.run(['clang++-17',*flags,'-c','src/coder/encoder.cpp','-o','encoder.o'],cwd=dst,check=True)
objs=sorted(p.name for p in dst.glob('*.o'))
subprocess.run(['clang++-17','-m64','-Wl,--gc-sections','-std=c++17',*objs,'-s','-o','cmix'],cwd=dst,check=True)
shutil.copy2(dst/'cmix',out/'cmix_round7_trace')
print(json.dumps({'trace_build_complete':True,'binary_bytes':(dst/'cmix').stat().st_size}),flush=True)
''')
    with (out/'build_trace.log').open('w') as log:
        q=subprocess.Popen(['python','-u',str(worker)],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    print(json.dumps({'pid':q.pid}))
_hp_prepare_trace()
del _hp_prepare_trace
