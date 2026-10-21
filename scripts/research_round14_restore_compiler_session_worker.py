"""New-session restoration; original compiler manifests/logs remain untouched."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time,traceback,urllib.request
W=Path('/kaggle/working/hp_round14');TAG='session356740330_v2';OUT=W/('compiler_restore_'+TAG+'.json')
M={'status':'VERIFYING_OFFICIAL_REPOSITORY','pid':os.getpid(),'started':time.time(),'deletions':[],'source':'https://apt.llvm.org/','changes':[]}
def save():OUT.write_text(json.dumps(M,indent=2))
def command(args,label,timeout):
    with (W/(TAG+'_'+label+'.log')).open('xb') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    assert r.returncode==0,(label,r.returncode)
try:
    assert not OUT.exists();save();assert 'VERSION_CODENAME=jammy' in Path('/etc/os-release').read_text()
    if shutil.which('clang++-17') and shutil.which('ld.lld-17'):M['action']='REUSED_PRESENT_PINNED_COMPILER'
    else:
        raw=urllib.request.urlopen('https://apt.llvm.org/llvm-snapshot.gpg.key',timeout=30).read()
        scratch=Path('/root/hp_round14_llvm17_'+TAG);scratch.mkdir();key=scratch/'llvm17.asc';key.write_bytes(raw)
        r=subprocess.run(['gpg','--show-keys','--with-colons',str(key)],capture_output=True,text=True)
        fingerprint='6084F3CF814B57C1CF12EFD515CF4D18AF4F7421';assert r.returncode==0 and 'fpr:::::::::'+fingerprint+':' in r.stdout
        installed=Path('/usr/share/keyrings/hp-round14-llvm17.asc');repo=Path('/etc/apt/sources.list.d/hp-round14-llvm17.list')
        assert not installed.exists() and not repo.exists();installed.write_bytes(raw)
        repo.write_text('deb [signed-by='+str(installed)+'] https://apt.llvm.org/jammy/ llvm-toolchain-jammy-17 main\n')
        M.update(status='INSTALLING_SIGNED_PINNED_COMPILER',key_sha256=hashlib.sha256(raw).hexdigest(),key_fingerprint=fingerprint,changes=[str(installed),str(repo)]);save()
        command(['apt-get','update','-o','Dir::Etc::sourcelist='+str(repo),'-o','Dir::Etc::sourceparts=-','-o','APT::Get::List-Cleanup=0'],'llvm17_update',450)
        command(['apt-get','install','-y','--no-remove','--no-install-recommends','clang-17','lld-17'],'llvm17_install',700)
        M['action']='INSTALLED_SIGNED_CLANG17_AND_LLD17'
    M.update(status='COMPLETE_PINNED_COMPILER_AVAILABLE',finished=time.time(),clang_version=subprocess.check_output(['clang++-17','--version'],text=True).splitlines()[0],lld_version=subprocess.check_output(['ld.lld-17','--version'],text=True).strip());save()
except BaseException as e:M.update(status='FAIL_PRESERVED_NO_AUTOMATIC_RETRY',error=repr(e),traceback=traceback.format_exc(),finished=time.time());save();raise
