#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
R=dtok_distrib_ce_long
python dyn_cache_tok.py --scheme distrib --run $R --stride 128 --lr 1e-5 --tag _s128 --gpu 0 > logs/abl_s128.log 2>&1
python dyn_cache_tok.py --scheme distrib --run $R --stride 256 --lr 2e-5 --tag _lr2 --gpu 0 > logs/abl_lr2.log 2>&1
python dyn_cache_tok.py --scheme distrib --run $R --stride 128 --lr 5e-6 --tag _s128lr05 --gpu 0 > logs/abl_s128lr05.log 2>&1
touch logs/abl.done
