#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
while [ ! -f logs/big.done ]; do sleep 10; done
P=pmix_tok_dtok_distrib_ce_long_big.npy
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 $P tcm_longbig > tcm_longbig.json 2>&1
python blend2.py $P tcm_longbig > blend2_longbig.json 2>&1
rm -f pmix_tok_dtok_distrib_ce_long.npy
touch logs/bigtcm.done
