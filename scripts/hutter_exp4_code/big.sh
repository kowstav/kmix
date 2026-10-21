#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
while [ ! -f logs/abl.done ]; do sleep 30; done
R=dtok_distrib_ce_long
LR=$(python - <<'PY'
import json
def v(t):
    try: return json.load(open(f'dyn_cache_tok_dtok_distrib_ce_long{t}.json'))['adapted_plus_cache_bpb']
    except Exception: return 9
c = {1e-5: v('_s128'), 5e-6: v('_s128lr05')}
lr = min(c, key=c.get)
if v('_lr2') < 1.2536 - 0.002: lr = 2e-5
print(lr)
PY
)
echo "chosen lr $LR"
python full_tok.py --scheme distrib --run $R --stride 128 --lr $LR --dtokens 40000000 --ent 1.2 --cpu_store --save_mix --tag _big --gpu 0 > logs/full_long_big.log 2>&1
touch logs/big.done
