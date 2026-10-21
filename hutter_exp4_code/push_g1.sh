#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
python dtok.py --scheme distrib --charemb --init dtok_distrib_ce_long3 --seed 3 --steps 8000 --lr 3e-4 --tag _long4 --gpu 1 > logs/dtok_distrib_ce_long4.log 2>&1
python full_tok.py --scheme distrib --run dtok_distrib_ce_long4 --stride 128 --lr 5e-6 --dtokens 2000 --reuse_ret knn_ret_dtok_distrib_ce_long2_ext.pt --save_mix --tag _r --gpu 1 > logs/full_long4_r.log 2>&1
touch logs/push_g1.done
while [ ! -f logs/push_g0.done ]; do sleep 20; done
rm -f knn_ret_dtok_distrib_ce_long_big.pt
python ens.py pmix_tok_dtok_distrib_ce_long_big.npy pmix_tok_dtok_distrib_ce_long2_ext.npy pmix_e1.npy > ens_e1.json 2>&1
python ens.py pmix_e1.npy pmix_tok_dtok_distrib_ce_long3_r.npy pmix_e2.npy > ens_e2.json 2>&1
rm -f pmix_e1.npy
python ens.py pmix_e2.npy pmix_tok_dtok_distrib_ce_long4_r.npy pmix_e3.npy > ens_e3.json 2>&1
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_e2.npy tcm_e2 > tcm_e2.json 2>&1 &
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_e3.npy tcm_e3 > tcm_e3.json 2>&1 &
wait
python blend2.py pmix_e2.npy tcm_e2 > blend2_e2.json 2>&1
python blend2.py pmix_e3.npy tcm_e3 > blend2_e3.json 2>&1
touch logs/push.done
