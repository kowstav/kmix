#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
gcc -O3 -march=native -o tcm2 tcm2.c -lm || exit 1
P=pmix_tok_dtok_distrib_ce_long.npy
run() { env TCM_SET=$2 TCM_WINIT=$3 TCM_APMW=$4 TCM_LR=$5 ./tcm2 distrib_train.u16 distrib_test.u16 $P tcmv_$1 > tcmv_$1.json 2>&1; }
run a 0 0 0.75 0.004 &
run b 1 0 0.25 0.002 &
run c 2 0 0.25 0.002 &
run d 2 0 0.5 0.001 &
wait
for v in a b c d; do echo $v; cat tcmv_$v.json; python blend2.py $P tcmv_$v | grep "tcm_mixer"; done > tcmv_summary.txt 2>&1
touch logs/tcmv.done
