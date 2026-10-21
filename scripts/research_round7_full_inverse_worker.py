import datetime,hashlib,json,os,pathlib,shutil,subprocess,tarfile,traceback
R=pathlib.Path('/kaggle/working/hp_round7');D=R/'full_inverse_v1';W=pathlib.Path('/root/hp/full_inverse_v1');assert not D.exists() and not W.exists();D.mkdir();W.mkdir(parents=True)
m={'status':'RUNNING','pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'original FX2 WRT/PHDA/article-order inverse, not entropy-coded full archive','paid_rental_usd':0}
def save():(D/'manifest.json').write_text(json.dumps(m,indent=2))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
save()
try:
 prefix='src/fx2-cmix-transformer-v1/'
 with tarfile.open(R/'preserved/research_sources_and_candidates.tar.gz') as t:
  for member in t.getmembers():
   if not member.isfile() or not member.name.startswith(prefix):continue
   relative=member.name[len(prefix):]
   if relative.startswith(('.git/','models/')):continue
   p=(W/'source'/relative).resolve();assert p.is_relative_to((W/'source').resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(member).read())
 src=W/'source'
 main=r'''#include <cstdio>
#include <iostream>
#include <string>
#include <vector>
#include "src/preprocess/preprocessor.h"
#include "src/readalike_prepr/article_reorder.h"
#include "src/readalike_prepr/misc.h"
#include "src/readalike_prepr/phda9_preprocess.h"
int main(int argc,char**argv){if(argc!=3)return 2;FILE*in=fopen(argv[1],"rb"),*dict=fopen(".dict","rb"),*out=fopen(".input_decomp","wb");if(!in||!dict||!out)return 3;preprocessor::Decode(in,out,dict);fclose(in);fclose(out);fclose(dict);split4Decomp();phda9_resto();::sort();cat(".intro_decomp",".main_decomp_restored_sorted","un1_d");cat("un1_d",".coda_decomp",argv[2]);return 0;}
'''
 (src/'inverse.cpp').write_text(main)
 cmd=['g++','-O2','-std=c++17','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-I.',str(src/'inverse.cpp'),str(src/'src/preprocess/preprocessor.cpp'),str(src/'src/preprocess/dictionary.cpp'),'-o',str(D/'inverse')]
 with (D/'build.log').open('x') as log:subprocess.run(cmd,cwd=src,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
 # Record successful generated-scratch deletions; refuse deletion outside this isolated workspace.
 audit=r'''#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int remove(const char *p){static int(*real)(const char*)=0;if(!real)real=dlsym(RTLD_NEXT,"remove");char path[PATH_MAX];if(realpath(p,path)){const char*root=getenv("HP_DELETE_ROOT");if(!root||strncmp(path,root,strlen(root))||path[strlen(root)]!='/'){errno=EPERM;return -1;}}int rc=real(p);if(rc==0){const char*log=getenv("HP_DELETE_LOG");int fd=log?open(log,O_WRONLY|O_CREAT|O_APPEND,0600):-1;if(fd>=0){dprintf(fd,"%s\n",p);close(fd);}}return rc;}
'''
 (src/'delete_audit.c').write_text(audit);subprocess.run(['gcc','-shared','-fPIC',str(src/'delete_audit.c'),'-ldl','-o',str(D/'delete_audit.so')],check=True)
 shutil.copyfile(R/'preserved/gen/.dict',W/'.dict');env=dict(os.environ);env.update(LD_PRELOAD=str(D/'delete_audit.so'),HP_DELETE_ROOT=str(W),HP_DELETE_LOG=str(D/'generated_scratch_deletions.txt'))
 with (D/'inverse.log').open('x') as log:
  p=subprocess.Popen([str(D/'inverse'),str(R/'full_stream_regen_v2/full_ready.wrt'),str(W/'enwik9_reconstructed')],cwd=W,env=env,stdout=log,stderr=subprocess.STDOUT);m['child_pid']=p.pid;save();_,status,u=os.wait4(p.pid,0);rc=os.waitstatus_to_exitcode(status)
 assert rc==0,('inverse failed',rc);target=W/'enwik9_reconstructed';m.update(reconstructed_bytes=target.stat().st_size,reconstructed_sha256=sha(target),user_seconds=u.ru_utime,max_rss_kbytes=u.ru_maxrss)
 assert target.stat().st_size==1000000000 and m['reconstructed_sha256']=='159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'
 m['deletions']={'manual_project_deletions':[],'generated_scratch_remove_calls':(D/'generated_scratch_deletions.txt').read_text().splitlines() if (D/'generated_scratch_deletions.txt').exists() else [],'reason':'original inverse program removes its own intermediate files; originals and preserved evidence protected'}
 m.update(status='PASS_FULL_PREPROCESS_INVERSE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print(json.dumps(m))
except BaseException as e:m.update(status='FAIL',error=repr(e),traceback=traceback.format_exc());save();raise
