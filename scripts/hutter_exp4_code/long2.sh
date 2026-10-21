#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
python dtok.py --scheme distrib --charemb --init dtok_distrib_ce_long --seed 1 --steps 14000 --lr 6e-4 --tag _long2 --gpu 1 > logs/dtok_distrib_ce_long2.log 2>&1
python full_tok.py --scheme distrib --run dtok_distrib_ce_long2 --save_mix --gpu 1 > logs/full_long2.log 2>&1
./tcm distrib_train.u16 distrib_test.u16 pmix_tok_dtok_distrib_ce_long2.npy tcm_long2 > tcm_long2.json 2> tcm_long2.err
python blend2.py pmix_tok_dtok_distrib_ce_long2.npy tcm_long2 > blend2_long2.json 2>&1
touch logs/long2.done
