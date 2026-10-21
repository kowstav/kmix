from pathlib import Path
import importlib.util,json,subprocess,sys,time,traceback,unittest
W=Path('/kaggle/working/hp_round14');sys.path.insert(0,'/root/r14_code_v2')
M={'status':'INSTALLING_PPMD_DEPENDENCY','started':time.time(),'tests':[]}
def save():(W/'preflight_v2.json').write_text(json.dumps(M,indent=2))
try:
    save()
    with (W/'pyppmd_install.log').open('w') as f:
        p=subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','--target','/root/r14_pyppmd','pyppmd==1.3.1'],stdout=f,stderr=subprocess.STDOUT,timeout=240)
    assert p.returncode==0,'Dependency installation failed; inspect log; no notebook submission'
    sys.path.insert(0,'/root/r14_pyppmd')
    suite=unittest.TestSuite()
    for name in ('test_group_weight_storage','test_article_order_ppmd'):
        spec=importlib.util.spec_from_file_location(name,'/root/r14_code_v2/tests/'+name+'.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(m))
    with (W/'preflight_tests_v2.log').open('w') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
    assert result.wasSuccessful() and result.testsRun==4 and not result.skipped
    M.update(status='COMPLETE_FOUR_LINUX_CORRECTNESS_TESTS',finished=time.time(),testsRun=result.testsRun,skipped=len(result.skipped));save()
except BaseException as e:M.update(status='FAIL_PRESERVED',error=repr(e),traceback=traceback.format_exc());save();raise
