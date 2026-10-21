#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
python full_tok.py --scheme distrib --run dtok_distrib_ce_long --stride 128 --lr 5e-6 --dtokens 2000 --reuse_ret knn_ret_dtok_distrib_ce_long2_ext.pt --save_mix --tag _r --gpu 0 > logs/full_long_r.log 2>&1
while [ ! -f logs/final4.done ]; do sleep 20; done
rm -f pmix_tok_dtok_distrib_ce_long_big.npy pmix_ens3.npy pmix_ens4.npy
python ens.py pmix_tok_dtok_distrib_ce_long_r.npy pmix_tok_dtok_distrib_ce_long2_ext.npy pmix_ens5a.npy > ens5a.json 2>&1
python ens.py pmix_ens5a.npy pmix_tok_dtok_distrib_ce_long3_r.npy pmix_ens5.npy > ens5.json 2>&1
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_ens5.npy tcm_ens5 > tcm_ens5.json 2>&1
python blend2.py pmix_ens5.npy tcm_ens5 > blend2_ens5.json 2>&1
touch logs/final5.done
