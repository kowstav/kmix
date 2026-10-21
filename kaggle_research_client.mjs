import fs from 'node:fs';
import crypto from 'node:crypto';

// The session credential is supplied only through an environment variable.
const base = process.env.HP_KAGGLE_BASE;
if (!base) throw new Error('HP_KAGGLE_BASE is required');
const [mode, arg1, arg2] = process.argv.slice(2);
const credentialPath = new URL(base).pathname;
const redact = value => String(value).replaceAll(base, '[SESSION_URL]').replaceAll(credentialPath, '[SESSION_PATH]');
async function request(path, method = 'GET', body) {
  const response = await fetch(base + path, {
    method, headers: body ? {'Content-Type':'application/json'} : {},
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(Math.min(180000, Math.max(40000, Number(process.env.HP_NETWORK_TIMEOUT_MS) || 40000))),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${path.split('?')[0]}`);
  return response.json();
}
async function execute(kernel, code) {
  const session = crypto.randomUUID();
  const msgId = crypto.randomUUID();
  const wsUrl = new URL(base + `/api/kernels/${encodeURIComponent(kernel)}/channels`);
  wsUrl.protocol = 'wss:';
  wsUrl.searchParams.set('session_id', session);
  const result = {kernel, streams:[], errors:[], displays:[], reply:null};
  return await new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let idle = false;
    const timer = setTimeout(() => {ws.close(); reject(new Error('Kernel request exceeded 50 seconds; execution may still be running.'))}, 50000);
    const finish = () => {
      if (idle && result.reply) {clearTimeout(timer); ws.close(); resolve(result);}
    };
    ws.addEventListener('open', () => ws.send(JSON.stringify({
      header:{msg_id:msgId,username:'codex-research',session,msg_type:'execute_request',version:'5.3'},
      parent_header:{},metadata:{},channel:'shell',
      content:{code,silent:false,store_history:false,user_expressions:{},allow_stdin:false,stop_on_error:true},
      buffers:[],
    })));
    ws.addEventListener('message', event => {
      if (typeof event.data !== 'string') return;
      let msg; try {msg=JSON.parse(event.data)} catch {return}
      if (msg.parent_header?.msg_id !== msgId) return;
      const type = msg.msg_type || msg.header?.msg_type;
      if (type === 'stream') result.streams.push({name:msg.content.name,text:redact(msg.content.text)});
      if (type === 'error') result.errors.push({ename:msg.content.ename,evalue:redact(msg.content.evalue),traceback:msg.content.traceback?.map(redact)});
      if (type === 'display_data' || type === 'execute_result') result.displays.push(msg.content.data?.['text/plain'] ?? '[non-text display]');
      if (type === 'execute_reply') result.reply=msg.content;
      if (type === 'status' && msg.content.execution_state === 'idle') idle=true;
      finish();
    });
    ws.addEventListener('error', () => {clearTimeout(timer); reject(new Error('Kernel WebSocket connection failed'))});
  });
}
try {
  let result;
  if (mode === 'get') result = await request(arg1);
  else if (mode === 'download') {
    const response=await request('/api/contents/'+arg1+'?content=1&format=base64&type=file');
    const buffer=Buffer.from(response.content,'base64'); fs.writeFileSync(arg2,buffer);
    result={downloaded:arg1,bytes:buffer.length,local:arg2};
  }
  else if (mode === 'put') result = await request('/api/contents/' + arg1, 'PUT', {type:'file',format:'text',content:fs.readFileSync(arg2,'utf8')});
  else if (mode === 'put-binary') result = await request('/api/contents/' + arg1, 'PUT', {type:'file',format:'base64',content:fs.readFileSync(arg2).toString('base64')});
  else if (mode === 'exec') result = await execute(arg1, fs.readFileSync(arg2,'utf8'));
  else throw new Error('Usage: get API_PATH | put REMOTE_PATH LOCAL_PATH | put-binary REMOTE_PATH LOCAL_PATH | download REMOTE_PATH LOCAL_PATH | exec KERNEL_ID LOCAL_CODE_PATH');
  const output = JSON.stringify(result);
  if (process.env.HP_RESULT_PATH) fs.writeFileSync(process.env.HP_RESULT_PATH,output+'\n');
  console.log(output);
  if (result?.errors?.length || result?.reply?.status === 'error') process.exitCode=1;
} catch (error) {console.error(redact(error.message)); process.exitCode=1}
