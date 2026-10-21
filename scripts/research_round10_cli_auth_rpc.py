import os,json,contextlib,io,subprocess
try:
 if not os.environ.get('KAGGLE_API_TOKEN'):
  from kaggle_secrets import UserSecretsClient
  os.environ['KAGGLE_API_TOKEN']=UserSecretsClient().get_secret('KAGGLE_API_TOKEN')
 p=subprocess.run(['kaggle','kernels','list','--mine','--page-size','5','--csv'],capture_output=True,text=True,timeout=40)
 # Do not print stderr: an authentication implementation might echo a token.
 print(json.dumps({'credential_loaded':True,'CLI_exit_code':p.returncode,'owned_notebooks_csv':p.stdout if p.returncode==0 else None,'failure_type':'CLI_AUTH_OR_API_FAILURE' if p.returncode else None}))
except Exception as e:
 print(json.dumps({'credential_loaded':False,'failure_type':type(e).__name__,'message':'Secret missing or inaccessible; no credential values logged.'}))
