import pathlib,json
r=pathlib.Path('/kaggle/working/hp_round7')
text=(r/'full_inverse_v1/build.log').read_text();print(json.dumps({'inverse_build_errors':[x for x in text.splitlines() if any(k in x for k in ('error:','undefined reference','fatal error'))][:24],
 'modes':{str(p):oct(p.stat().st_mode&0o777) for p in [r/'lex_finalbit_trace_v1/cmix_trace',r/'calibration_native_v1/cmix_calibrated']}}))
