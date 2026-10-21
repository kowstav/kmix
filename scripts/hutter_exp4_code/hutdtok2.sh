#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
while [ ! -f runs/dtok_distrib_ce_hut_q4/report.json ]; do sleep 60; done
python -u full_tok.py --scheme distrib --run dtok_distrib_ce_hut_q4 --stride 128 --lr 5e-6 --gpu 0 --save_mix > logs/full_distrib_ce_hut_q4.log 2>&1
echo done > logs/hutdtok.done
