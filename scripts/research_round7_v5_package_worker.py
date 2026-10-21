import pathlib,subprocess,shutil,hashlib,json,os,time
hp=pathlib.Path('/root/hp');out=pathlib.Path('/kaggle/working/hp_round7');upx=out/'tools/upx-3.96'
for _ in range(300):
    if 'V5_NATIVE_COMPLETE' in (out/'v5_native_retry.log').read_text():break
    if 'Traceback' in (out/'v5_native_retry.log').read_text():raise RuntimeError('Native codec verification failed')
    time.sleep(1)
else:raise RuntimeError('Native worker timeout')
rows=[]
for name,root in [('original',hp/'round7_lab'),('v5',hp/'round7_v5')]:
    dst=out/('cmix_'+name+'_upx396_lzma');shutil.copyfile(root/'cmix',dst);dst.chmod(0o755)
    subprocess.run([str(upx),'--best','--lzma',str(dst)],check=True)
    subprocess.run([str(upx),'-t',str(dst)],check=True)
    rows.append({'name':name,'unpacked_bytes':(root/'cmix').stat().st_size,'packed_bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
result={'measurement':'matched unprofiled lab executables; not the final round6 PGO production package','executables':rows,'incremental_packed_loader_bytes':rows[1]['packed_bytes']-rows[0]['packed_bytes'],'reference_two_copy_net_saving_bytes':2*(28200-rows[1]['packed_bytes']+rows[0]['packed_bytes']),'candidate_bf16_two_copy_net_saving_bytes':2*(28199-rows[1]['packed_bytes']+rows[0]['packed_bytes'])}
(out/'v5_package_screen.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
print('V5_PACKAGE_SCREEN_COMPLETE',flush=True)
