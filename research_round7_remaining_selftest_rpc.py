import json,pathlib,subprocess
r=pathlib.Path('/kaggle/working/hp_round7');d=r/'remaining_experts_v1';b=d/'selftest';
subprocess.run(['g++','-O2','-std=c++17',str(r/'research_round7_remaining_selftest.cpp'),'-o',str(b)],check=True)
result=subprocess.check_output([str(b),str(r/'preserved/gen/.dict'),str(r/'research_round7_remaining_graph.txt'),str(r/'research_round7_remaining_constructors.txt')],text=True)
(d/'selftest.json').write_text(result);print(result)
