#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
rm -f knn_ret_dtok_distrib_ce_hut_q4.pt
python dtok.py --scheme distrib --charemb --init dtok_distrib_ce_long2 --seed 2 --steps 8000 --lr 4e-4 --tag _long3 --gpu 1 > logs/dtok_distrib_ce_long3.log 2>&1
while [ ! -f knn_ret_dtok_distrib_ce_long2_ext.pt ]; do sleep 20; done
sleep 30
while [ ! -f logs/final2.done ]; do sleep 20; done
rm -f pmix_ens.npy pmix_tok_dtok_distrib_ce_long2_big.npy
python full_tok.py --scheme distrib --run dtok_distrib_ce_long3 --stride 128 --lr 5e-6 --dtokens 2000 --reuse_ret knn_ret_dtok_distrib_ce_long2_ext.pt --save_mix --tag _r --gpu 1 > logs/full_long3_r.log 2>&1
while [ ! -f logs/final3.done ]; do sleep 20; done
python ens.py pmix_ens3.npy pmix_tok_dtok_distrib_ce_long3_r.npy pmix_ens4.npy > ens4.json 2>&1
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_ens4.npy tcm_ens4 > tcm_ens4.json 2>&1
python blend2.py pmix_ens4.npy tcm_ens4 > blend2_ens4.json 2>&1
touch logs/final4.done
