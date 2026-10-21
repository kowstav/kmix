#!/bin/bash
# usage: labrun.sh RUNNAME SLICEPREFIX [load] [extra env assignments...]
# runs the lab compressor on slice SLICEPREFIX.bin; with "load" uses SLICEPREFIX.probs.f16
name=$1; slice=$2; mode=$3; shift 3
dir=/root/hp/runs/$name; rm -rf $dir; mkdir -p $dir; cd $dir; ln -sf /root/hp/gen/.dict .dict
export LAB_RAW=1 LAB_VOCAB=/root/hp/data/vocab.bm LAB_DICT=/root/hp/gen/.dict LAB_COST=$dir/cost.f32
for kv in "$@"; do export "$kv"; done
BIN=${LAB_BIN:-/root/hp/lab/cmix}
if [ "$mode" = "load" ]; then
  export LAB_KEEP_PPMD=1
  nohup bash -c "time $BIN -n --transformer /root/hp/gen/.tfweights --load-transformer-probs $slice.probs.f16 $slice.bin out.cmx" > run.log 2>&1 &
else
  nohup bash -c "time $BIN -n --transformer /root/hp/gen/.tfweights $slice.bin out.cmx" > run.log 2>&1 &
fi
echo launched $name
