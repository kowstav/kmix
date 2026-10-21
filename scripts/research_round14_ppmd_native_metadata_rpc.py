import subprocess
print(subprocess.run(['7z','l','-slt','/root/r14_ppmd_native_probe_v2/0/archive.7z'],capture_output=True,text=True,timeout=20).stdout)
