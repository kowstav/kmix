#!/bin/bash
# extend the continued model's datastore to all training tokens (reusing the saved search over the first 40M), then
# ensemble with the long model's system and blend with the classical coder
cd /kaggle/working/hutter_lab/exp4
while [ ! -f knn_ret_dtok_distrib_ce_long2_big.pt ]; do sleep 20; done
sleep 30
python full_tok.py --scheme distrib --run dtok_distrib_ce_long2 --stride 128 --lr 5e-6 --dfrom 40000000 --dtokens 58692761 --ent 1.2 --cpu_store --base_ret knn_ret_dtok_distrib_ce_long2_big.pt --save_mix --tag _ext --gpu 0 > logs/full_long2_ext.log 2>&1
while [ ! -f logs/final2.done ]; do sleep 20; done
python ens.py pmix_tok_dtok_distrib_ce_long_big.npy pmix_tok_dtok_distrib_ce_long2_ext.npy pmix_ens3.npy > ens3.json 2>&1
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_ens3.npy tcm_ens3 > tcm_ens3.json 2>&1 &
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_tok_dtok_distrib_ce_long2_ext.npy tcm_long2ext > tcm_long2ext.json 2>&1 &
wait
python blend2.py pmix_ens3.npy tcm_ens3 > blend2_ens3.json 2>&1
python blend2.py pmix_tok_dtok_distrib_ce_long2_ext.npy tcm_long2ext > blend2_long2ext.json 2>&1
touch logs/final3.done
