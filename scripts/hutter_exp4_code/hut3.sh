#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
python -u dtok_full_eval.py --run dtok_distrib_ce_hut_q4 --scheme distrib --bits 4 --gpu 0 > logs/hutfull_eval.log 2>&1 &
python -u full_tok.py --scheme distrib --run dtok_distrib_ce_hut_q4 --stride 128 --lr 5e-6 --gpu 0 --save_mix > logs/full_distrib_ce_hut_q4.log 2>&1
wait
touch logs/hut3.done
