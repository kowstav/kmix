import fs from 'node:fs';
import crypto from 'node:crypto';
const base=process.env.HP_KAGGLE_BASE;
if(!base) throw new Error('HP_KAGGLE_BASE required');
const [remote,local,expected]=process.argv.slice(2);
const bytes=fs.readFileSync(local);
const hash=crypto.createHash('sha256').update(bytes).digest('hex');
if(hash!==expected) throw new Error('Local source hash differs from declared immutable bundle');
try {
 const response=await fetch(base+'/api/contents/'+remote,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'file',format:'base64',content:bytes.toString('base64')}),signal:AbortSignal.timeout(60000)});
 if(!response.ok) throw new Error('HTTP '+response.status+' during binary upload');
 const meta=await response.json();
 if(meta.size!==bytes.length) throw new Error('Remote metadata size mismatch');
 console.log(JSON.stringify({uploaded:remote,bytes:bytes.length,source_sha256:hash,remote_hash_and_CRC_verification_still_required:true}));
} catch(e) {
 console.error(String(e.message).replaceAll(base,'[SESSION_URL]').replaceAll(new URL(base).pathname,'[SESSION_PATH]'));
 process.exitCode=1;
}
