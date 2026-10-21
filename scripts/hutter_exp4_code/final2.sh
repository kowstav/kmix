#!/bin/bash
# final held-out pipeline: continued model with the improved miners, ensemble with the long model, classical blend
cd /kaggle/working/hutter_lab/exp4
while [ ! -f runs/dtok_distrib_ce_long2/report.json ]; do sleep 60; done
python full_tok.py --scheme distrib --run dtok_distrib_ce_long2 --stride 128 --lr 5e-6 --dtokens 40000000 --ent 1.2 --cpu_store --save_mix --tag _big --gpu 1 > logs/full_long2_big.log 2>&1
while [ ! -f logs/big.done ]; do sleep 30; done
python ens.py pmix_tok_dtok_distrib_ce_long_big.npy pmix_tok_dtok_distrib_ce_long2_big.npy pmix_ens.npy > ens.json 2>&1
SET=${TSET:-2}; APMW=${TAPMW:-0.25}; APM2=${TAPM2:-0}
[ -f tcm_best.env ] && source tcm_best.env
env TCM_SET=$SET TCM_WINIT=0 TCM_APMW=$APMW TCM_LR=0.002 TCM_APM2=$APM2 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_ens.npy tcm_ens > tcm_ens.json 2>&1 &
env TCM_SET=$SET TCM_WINIT=0 TCM_APMW=$APMW TCM_LR=0.002 TCM_APM2=$APM2 ./tcm2 distrib_train.u16 distrib_test.u16 pmix_tok_dtok_distrib_ce_long2_big.npy tcm_long2big > tcm_long2big.json 2>&1 &
wait
python blend2.py pmix_ens.npy tcm_ens > blend2_ens.json 2>&1
python blend2.py pmix_tok_dtok_distrib_ce_long2_big.npy tcm_long2big > blend2_long2big.json 2>&1
touch logs/final2.done
