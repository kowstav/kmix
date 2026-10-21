from pathlib import Path
import json,shutil,subprocess
print(Path('/etc/os-release').read_text())
print(json.dumps({'tools':{n:shutil.which(n) for n in ('clang++-17','ld.lld-17','upx','gcc','g++')},'working_free':shutil.disk_usage('/kaggle/working').free}))
for prefix in ('hp_round7','hp_round8','hp_round13'):
    print(prefix,[str(p) for p in Path('/kaggle/working',prefix).rglob('*upx*')][:12])
print(subprocess.run(['kaggle','kernels','status','chaoscpp/hutter-r14-article-order-native-v2'],capture_output=True,text=True,timeout=20).stdout)
