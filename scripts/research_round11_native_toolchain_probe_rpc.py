from pathlib import Path
import json
import subprocess

out={'os':Path('/etc/os-release').read_text(),'llvm17_binary':Path('/usr/lib/llvm-17/bin/clang++').exists(),
     'llvm17_linker':Path('/usr/lib/llvm-17/bin/ld.lld').exists()}
p=subprocess.run(['apt-cache','policy','clang-17','lld-17'],capture_output=True,text=True,timeout=12)
out['apt_policy']=p.stdout[:4000]; out['exit']=p.returncode
print(json.dumps(out))
