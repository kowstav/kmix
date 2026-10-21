#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
P=pmix_tok_dtok_distrib_ce_hut_q4.npy
env TCM_SET=2 TCM_WINIT=0 TCM_APMW=0.25 TCM_LR=0.002 TCM_APM2=1 ./tcm2 distrib_train.u16 distrib_test.u16 $P tcm_hut > tcm_hut.json 2>&1
python blend2.py $P tcm_hut > blend2_hut.json 2>&1
touch logs/huttcm.done
