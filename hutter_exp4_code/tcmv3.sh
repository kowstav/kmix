#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
while pgrep -f "tcmv2[.]sh" > /dev/null; do sleep 5; done
gcc -O3 -march=native -o tcm2 tcm2.c -lm || exit 1
P=pmix_tok_dtok_distrib_ce_long.npy
run() { env TCM_SET=$2 TCM_WINIT=$3 TCM_APMW=$4 TCM_LR=$5 TCM_APM2=$6 ./tcm2 distrib_train.u16 distrib_test.u16 $P tcmv_$1 > tcmv_$1.json 2>&1; }
run e 2 0 0.25 0.002 1 &
run f 2 0 0.5 0.002 1 &
wait
for v in e f; do echo $v; cat tcmv_$v.json; python blend2.py $P tcmv_$v | grep "tcm_mixer"; done > tcmv3_summary.txt 2>&1
touch logs/tcmv3.done
