from pathlib import Path
import sys,zipfile,json,hashlib,unittest
R=Path('/root/r14_scope_contract_tests');R.mkdir()
with zipfile.ZipFile('/kaggle/working/hp_round14/sources_scope_gate_v7.zip.dat') as z:
    for e in json.loads(z.read('source_manifest.json')):
        p=(R/e['path']).resolve();assert p.is_relative_to(R);b=z.read(e['path']);assert hashlib.sha256(b).hexdigest()==e['sha256'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
sys.path.insert(0,str(R));import importlib.util
s=importlib.util.spec_from_file_location('scope_tests','/kaggle/working/test_native_input_contract.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromModule(m));assert r.wasSuccessful() and r.testsRun==2 and not r.skipped
print(json.dumps({'status':'PASS_TWO_NATIVE_INPUT_SCOPE_CONTRACT_TESTS','tests':r.testsRun}))
