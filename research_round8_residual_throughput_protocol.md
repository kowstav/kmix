# Free Kaggle residual throughput probe,6October2026

Timing only, not an architecture/compression/training result. Read the first
32768native bit events ofA, their pre-target staged features and actual targets.
Construct a24float input shape, a24->32->1MLP and a24->16GRU->1causal
sequence model. Measure FP32forward/backward plus AdamW step with learning
rate0: model parameters must remain bit-identical. No production weights,
training corpus, exported coder or account billing change.

Global batch32768bit targets; GRUsequence length128and batch256. Four warm
steps,12timed steps, CUDA synchronization, separately recorded preload time,
median/p90step time, useful bit targets/GPU-second and peak device memory.
Use one free T4. The finite warmed input batch, precision, tensor/kernel shapes
and recurrent resets are recorded. This is a steady GPU kernel/data-resident
measurement; CPU generation/full dataset transfer/native export and longer
optimizer learning are not measured. It cannot be converted into5090throughput
using a guessed speed ratio, nor into transformer byte-target throughput.

The purpose is to identify prototypes that fit the current free session before
requesting paid compute. Exact native exported inference remains a separate
gate for any trained residual. No model update or measured archive gain is
claimed from this probe. Retain compact result/source hashes; no deletion.
