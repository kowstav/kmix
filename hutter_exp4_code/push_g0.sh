#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
python full_tok.py --scheme distrib --run dtok_distrib_ce_long --stride 128 --lr 5e-6 --dtokens 40000000 --ent 1.2 --cpu_store --save_mix --tag _big --gpu 0 > logs/full_long_big2.log 2>&1
touch logs/push_g0.done
