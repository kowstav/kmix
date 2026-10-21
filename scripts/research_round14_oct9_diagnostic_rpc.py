from pathlib import Path
import sys,inspect,subprocess,json,shutil
sys.path.insert(0,'/root/r14_backend_probe/lib');import pyppmd
print('pyppmd entry points',inspect.getsource(pyppmd.compress),inspect.getsource(pyppmd.decompress),inspect.getfile(pyppmd))
print('native tools',[(n,shutil.which(n)) for n in ('7z','7zz','7za','gcc','clang')])
for arm in ('prune-word','prune-match','prune-indirect','output-fp32'):
    ref='chaoscpp/hutter-r14-native-'+arm+'-v1'
    p=subprocess.run(['kaggle','kernels','status',ref],capture_output=True,text=True,timeout=20)
    print(json.dumps({'ref':ref,'exit':p.returncode,'status':p.stdout.strip() if p.returncode==0 else 'CLI error'}))
