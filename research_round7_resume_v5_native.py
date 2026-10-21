import pathlib,subprocess,json,urllib.request,hashlib,tarfile,io
out=pathlib.Path('/kaggle/working/hp_round7');log=out/'v5_native_retry.log'
if log.exists():raise RuntimeError('Refuse duplicate native retry worker')
p=subprocess.Popen(['python3','-u',str(out/'research_round7_v5_native_worker.py'),'--resume-build'],stdout=log.open('w'),stderr=subprocess.STDOUT,start_new_session=True)
print(json.dumps({'started_native_v5_retry':p.pid}))
url='https://github.com/upx/upx/releases/download/v3.96/upx-3.96-amd64_linux.tar.xz'
data=urllib.request.urlopen(url,timeout=25).read()
tools=out/'tools';tools.mkdir(exist_ok=True)
dest=tools/'upx-3.96'
with tarfile.open(fileobj=io.BytesIO(data),mode='r:xz') as tf:
    entry=tf.getmember('upx-3.96-amd64_linux/upx')
    if not entry.isfile():raise RuntimeError('Not a regular executable')
    content=tf.extractfile(entry).read();dest.write_bytes(content);dest.chmod(0o755)
manifest={'source_url':url,'archive_bytes':len(data),'archive_sha256':hashlib.sha256(data).hexdigest(),'executable_sha256':hashlib.sha256(content).hexdigest(),'version':subprocess.check_output([str(dest),'--version'],text=True)}
(out/'upx_fetch_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest))
