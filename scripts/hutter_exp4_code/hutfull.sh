#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
while [ ! -f runs/dtok_distrib_ce_hut_q4/report.json ]; do sleep 60; done
python -u dtok_full_eval.py --run dtok_distrib_ce_hut_q4 --scheme distrib --bits 4 --gpu 0 > logs/hutfull_eval.log 2>&1
touch logs/hutfull.done
