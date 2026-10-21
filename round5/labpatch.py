# Applies "lab" instrumentation to a copy of fx2-cmix-transformer-v1 (in cwd).
# All features are env-var gated, so with no LAB_* variables set the binary
# behaves exactly like the original.
#   LAB_RAW=1            -n mode: copy input verbatim as the coded stream (no segment headers)
#   LAB_VOCAB=<file>     force the 256-entry vocabulary from a 32-byte bitmap file
#   LAB_DICT=<file>      with -n: pretrain the predictor on this dictionary (as -e does)
#   LAB_KEEP_PPMD=1      with --load-transformer-probs: still run the ppmd as a mixer input
#   LAB_COST=<file>      write ideal code length (bits, float32) of every coded byte
import re, sys, io

def patch(path, old, new, count=1):
    s = open(path, encoding='utf-8').read()
    n = s.count(old)
    assert n == count, f'{path}: anchor found {n} times, expected {count}:\n{old}'
    s = s.replace(old, new)
    open(path, 'w', encoding='utf-8').write(s)

# ---- encoder: accumulate ideal cost
patch('src/coder/encoder.cpp', '#include "encoder.h"\n',
      '#include "encoder.h"\n#include <cmath>\ndouble g_lab_cost_bits = 0;\n')
patch('src/coder/encoder.cpp',
      '  if (bit) {\n    x2_ = xmid;',
      '  g_lab_cost_bits -= std::log2(bit ? p / 65536.0 : (65536.0 - p) / 65536.0);\n  if (bit) {\n    x2_ = xmid;')

# ---- runner: raw mode, forced vocab, dict pretrain, cost dump
patch('src/runner.cpp', 'int Help() {',
      'extern double g_lab_cost_bits;\nint Help() {')
patch('src/runner.cpp',
      '''  for (unsigned long long pos = 0; pos < input_bytes; ++pos) {
    unsigned char c = buffer[pos % buffer_size];
    for (int j = 7; j >= 0; --j) {
      e.Encode((c>>j)&1);
    }''',
      '''  FILE* lab_cost = getenv("LAB_COST") ? fopen(getenv("LAB_COST"), "wb") : NULL;
  for (unsigned long long pos = 0; pos < input_bytes; ++pos) {
    unsigned char c = buffer[pos % buffer_size];
    double before = g_lab_cost_bits;
    for (int j = 7; j >= 0; --j) {
      e.Encode((c>>j)&1);
    }
    if (lab_cost) { float cb = (float)(g_lab_cost_bits - before); fwrite(&cb, 4, 1, lab_cost); }''')
patch('src/runner.cpp',
      '''  e.Flush();
  *output_bytes = os->tellp();''',
      '''  e.Flush();
  if (lab_cost) fclose(lab_cost);
  fprintf(stderr, "\\nLAB ideal cost: %.1f bytes\\n", g_lab_cost_bits / 8);
  *output_bytes = os->tellp();''')
patch('src/runner.cpp',
      '''  } else {
    preprocessor::NoPreprocess(data_in, temp_out, *input_bytes);
  }''',
      '''  } else if (getenv("LAB_RAW")) {
    std::vector<char> buf(1 << 20);
    size_t n;
    while ((n = fread(buf.data(), 1, buf.size(), data_in)) > 0) fwrite(buf.data(), 1, n, temp_out);
  } else {
    preprocessor::NoPreprocess(data_in, temp_out, *input_bytes);
  }''')
patch('src/runner.cpp',
      '''  std::vector<bool> vocab(256, false);
  if (temp_bytes < kMinVocabFileSize) {
    std::fill(vocab.begin(), vocab.end(), true);
  } else {''',
      '''  std::vector<bool> vocab(256, false);
  if (getenv("LAB_VOCAB")) {
    FILE* vf = fopen(getenv("LAB_VOCAB"), "rb");
    if (!vf) Fail("LAB_VOCAB unreadable");
    unsigned char bm[32];
    if (fread(bm, 1, 32, vf) != 32) Fail("LAB_VOCAB short");
    fclose(vf);
    for (int i = 0; i < 256; ++i) vocab[i] = (bm[i / 8] >> (i % 8)) & 1;
  } else if (temp_bytes < kMinVocabFileSize) {
    std::fill(vocab.begin(), vocab.end(), true);
  } else {''')
patch('src/runner.cpp',
      '''    preprocessor::Pretrain(&p, dictionary);
  }
  Compress(''',
      '''    preprocessor::Pretrain(&p, dictionary);
  } else if (getenv("LAB_DICT") && !extraction.ppmd_only && !extraction.transformer_only) {
    FILE* ld = fopen(getenv("LAB_DICT"), "rb");
    if (!ld) Fail("LAB_DICT unreadable");
    preprocessor::Pretrain(&p, ld);
    fclose(ld);
  }
  Compress(''')

# ---- predictor: keep ppmd alongside loaded transformer probs
patch('src/predictor.cpp',
      '  if (!transformer_probs_reader_) AddPPMD();',
      '  if (!transformer_probs_reader_ || getenv("LAB_KEEP_PPMD")) AddPPMD();')
patch('src/predictor.cpp',
      '''    if (byte_model_) {
      byte_model_->ByteUpdate();
      if (ppmd_probs_writer_) WritePpmdProbs();

      if (transformer_) {''',
      '''    if (byte_model_ && transformer_probs_reader_) {
      byte_model_->ByteUpdate();
      LoadTransformerProbs();
    } else if (byte_model_) {
      byte_model_->ByteUpdate();
      if (ppmd_probs_writer_) WritePpmdProbs();

      if (transformer_) {''')
print('lab patch applied')
# keep .dict in -n lab mode (fxcm loads ./.dict when the predictor is constructed)
patch('src/runner.cpp', '''  } else if (mode == 'c' || mode == 'n') {
      remove(".dict");''', '''  } else if (mode == 'c' || mode == 'n') {
      if (!getenv("LAB_RAW")) remove(".dict");''')
print('lab dict-keep patch applied')
# LAB_UNIFORM_NN=1 (no --transformer): run neither the lstm nor a transformer; the byte mixer
# carries a uniform distribution (cmix-only measurements without the slow lstm)
patch('src/predictor.cpp', '''      vocab_size, transformer_ ? nullptr :''',
      '''      vocab_size, (transformer_ || getenv("LAB_UNIFORM_NN")) ? nullptr :''')
patch('src/predictor.cpp', '''        const std::valarray<float>& p = byte_model_->BytePredict();
        for (unsigned int j = 0; j < 256; ++j) {
          byte_mixer_->SetInput(j,p[j]);
        }

        byte_mixer_->ByteUpdate();''', '''        if (getenv("LAB_UNIFORM_NN")) {
          for (unsigned int j = 0; j < vocab_size_; ++j) probs_scratch_[j] = 1.0f;
          byte_mixer_->SetProbs(probs_scratch_.data());
        } else {
        const std::valarray<float>& p = byte_model_->BytePredict();
        for (unsigned int j = 0; j < 256; ++j) {
          byte_mixer_->SetInput(j,p[j]);
        }

        byte_mixer_->ByteUpdate();
        }''')
print('lab uniform-nn patch applied')
