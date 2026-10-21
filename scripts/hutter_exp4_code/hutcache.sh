#!/bin/bash
cd /kaggle/working/hutter_lab/exp4
python -u dtok_full_cache.py --run dtok_distrib_ce_hut_q4 --limit 2500000 --seg 1000000 --gpu 0 > logs/hutcache_debug.log 2>&1 || exit 1
python -u dtok_full_cache.py --run dtok_distrib_ce_hut_q4 --gpu 0 > logs/hutcache.log 2>&1
touch logs/hutcache.done
