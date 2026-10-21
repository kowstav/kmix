#include "predictor.h"
#include <vector>
#include <stdlib.h>
#include <stdio.h>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <cstdarg>
#ifdef __F16C__
#include <immintrin.h>
#endif

void Fail(const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  fprintf(stderr, "\ncmix error: ");
  vfprintf(stderr, fmt, args);
  fprintf(stderr, "\n");
  va_end(args);
  exit(1);
}

namespace {

const size_t kHalfBufferSize = 1 << 22;  // 4M halfs = 8MB per buffer

uint16_t FloatToHalf(float f) {
  uint32_t x;
  memcpy(&x, &f, 4);
  uint32_t sign = (x >> 16) & 0x8000;
  int32_t exp = (int32_t)((x >> 23) & 0xFF) - 112;  // half-biased exponent
  uint32_t mant = x & 0x7FFFFF;
  if (exp >= 31) return sign | 0x7C00;  // overflow, infinity and NaN
  if (exp <= 0) {  // subnormal half (or zero)
    if (exp < -10) return sign;
    mant |= 0x800000;
    int shift = 14 - exp;
    uint16_t h = mant >> shift;
    uint32_t rem = mant & ((1u << shift) - 1), half = 1u << (shift - 1);
    if (rem > half || (rem == half && (h & 1))) ++h;
    return sign | h;
  }
  uint16_t h = sign | (exp << 10) | (mant >> 13);
  uint32_t rem = mant & 0x1FFF;
  if (rem > 0x1000 || (rem == 0x1000 && (h & 1))) ++h;  // round to nearest even
  return h;
}

// Note: subnormal halves (values below 2^-14) decode to HALF their true
// value (the exponent term below would be 113-e in an exact decode). The
// F16C bulk path decodes exactly, so only the last n%8 elements of a
// conversion are affected. This quirk is part of the probability rounding
// contract of --save-ppmd-probs/--load-transformer-probs and of the transformer
// path, which reproduces the file pipeline bit-for-bit; changing it would
// change the coded probabilities.
float HalfToFloat(uint16_t h) {
  uint32_t sign = (uint32_t)(h & 0x8000) << 16;
  uint32_t exp = (h >> 10) & 0x1F;
  uint32_t mant = h & 0x3FF;
  uint32_t x;
  if (exp == 0) {
    if (mant == 0) {
      x = sign;
    } else {  // subnormal half: normalize
      int e = 0;
      while (!(mant & 0x400)) {
        mant <<= 1;
        ++e;
      }
      mant &= 0x3FF;
      x = sign | ((uint32_t)(112 - e) << 23) | (mant << 13);
    }
  } else if (exp == 31) {
    x = sign | 0x7F800000 | (mant << 13);
  } else {
    x = sign | ((exp + 112) << 23) | (mant << 13);
  }
  float f;
  memcpy(&f, &x, 4);
  return f;
}

void FloatsToHalves(const float* src, uint16_t* dst, size_t n) {
  size_t i = 0;
#ifdef __F16C__
  for (; i + 8 <= n; i += 8) {
    _mm_storeu_si128(reinterpret_cast<__m128i*>(dst + i),
        _mm256_cvtps_ph(_mm256_loadu_ps(src + i), _MM_FROUND_TO_NEAREST_INT));
  }
#endif
  for (; i < n; ++i) dst[i] = FloatToHalf(src[i]);
}

void HalvesToFloats(const uint16_t* src, float* dst, size_t n) {
  size_t i = 0;
#ifdef __F16C__
  for (; i + 8 <= n; i += 8) {
    _mm256_storeu_ps(dst + i, _mm256_cvtph_ps(
        _mm_loadu_si128(reinterpret_cast<const __m128i*>(src + i))));
  }
#endif
  for (; i < n; ++i) dst[i] = HalfToFloat(src[i]);
}

// The encoded article separator ("  <page>\n    <title>" after the WRT
// dictionary transform), as vocabulary indices of the enwik9 preprocessed
// stream. Validated against the dictionary encoding by
// SaveArticleBoundaries in runner.cpp; article boundaries correspond
// exactly to the occurrences of this sequence.
const unsigned char kArticleSeparator[15] = {
    0x08, 0x08, 0x25, 0xac, 0x65, 0x27, 0x05,
    0x08, 0x08, 0x08, 0x08, 0x25, 0xac, 0x68, 0x27};

// Articles longer than this are cut into pieces of exactly this many tokens
// (plus a shorter last piece), each a fresh transformer context — the same
// splitting the training data loader applies (split_article_lengths with
// max_article_tokens = 2^17). Must not exceed the transformer's rope table
// (131072 positions).
const unsigned long long kMaxArticleTokens = 1ULL << 17;

// The transformer's vocabulary: the 205 byte values of fx2-cmix's
// dictionary-preprocessed enwik9 stream, in ascending order, i.e. the token
// index -> byte mapping the shipped weights were trained with. It is fixed
// here rather than taken from the input's extracted vocabulary so that the
// same weights can be used on streams whose byte set differs (cmix-lex's
// payload_lex side blob, enwik8, ...): bytes outside this set are coded with
// the ppmd's distribution and reset the transformer context (see
// TransformerByteUpdate). A retrained model with a different vocabulary must
// update this table.
const unsigned int kTransformerVocabSize = 205;
const unsigned char kTransformerVocab[kTransformerVocabSize] = {
    0x03,0x05,0x06,0x07,0x09,0x0a,0x0c,0x12,0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27,
    0x28,0x29,0x2a,0x2b,0x2c,0x2d,0x2e,0x2f,0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,
    0x38,0x39,0x40,0x4a,0x4b,0x4c,0x4d,0x4e,0x4f,0x50,0x51,0x52,0x53,0x58,0x5b,0x5c,
    0x5d,0x5e,0x5f,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6a,0x6b,0x6c,0x6d,
    0x6e,0x6f,0x70,0x71,0x72,0x73,0x74,0x75,0x76,0x77,0x78,0x79,0x7a,0x80,0x81,0x82,
    0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,0x90,0x91,0x92,
    0x93,0x94,0x95,0x96,0x97,0x98,0x99,0x9a,0x9b,0x9c,0x9d,0x9e,0x9f,0xa0,0xa1,0xa2,
    0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,0xaf,0xb0,0xb1,0xb2,
    0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xb9,0xba,0xbb,0xbc,0xbd,0xbe,0xbf,0xc0,0xc1,0xc2,
    0xc3,0xc4,0xc5,0xc6,0xc7,0xc8,0xc9,0xca,0xcb,0xcc,0xcd,0xce,0xcf,0xd0,0xd1,0xd2,
    0xd3,0xd4,0xd5,0xd6,0xd7,0xd8,0xd9,0xda,0xdb,0xdc,0xdd,0xde,0xdf,0xe0,0xe1,0xe2,
    0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb,0xec,0xed,0xee,0xef,0xf0,0xf1,0xf2,
    0xf3,0xf4,0xf5,0xf6,0xf7,0xf8,0xf9,0xfa,0xfb,0xfc,0xfd,0xfe,0xff
};

}  // namespace

HalfFileWriter::HalfFileWriter(const std::string& path) : path_(path),
    buffer_(kHalfBufferSize) {
  file_ = fopen(path.c_str(), "wb");
  if (!file_) Fail("cannot open %s for writing", path.c_str());
}

HalfFileWriter::~HalfFileWriter() {
  Flush();
  fclose(file_);
}

void HalfFileWriter::Write(const float* values, size_t n) {
  if (used_ + n > buffer_.size()) Flush();
  FloatsToHalves(values, buffer_.data() + used_, n);
  used_ += n;
}

void HalfFileWriter::WriteHalves(const uint16_t* values, size_t n) {
  if (used_ + n > buffer_.size()) Flush();
  memcpy(buffer_.data() + used_, values, n * sizeof(uint16_t));
  used_ += n;
}

void HalfFileWriter::Flush() {
  if (used_ == 0) return;
  if (fwrite(buffer_.data(), sizeof(uint16_t), used_, file_) != used_) {
    Fail("failed writing to %s (disk full?)", path_.c_str());
  }
  used_ = 0;
}

HalfFileReader::HalfFileReader(const std::string& path,
    unsigned long long num_distributions, unsigned int vocab_size)
    : path_(path), buffer_(kHalfBufferSize) {
  file_ = fopen(path.c_str(), "rb");
  if (!file_) Fail("cannot open %s for reading", path.c_str());
  fseeko(file_, 0, SEEK_END);
  unsigned long long size = ftello(file_);
  fseeko(file_, 0, SEEK_SET);
  unsigned long long expected = num_distributions * vocab_size * 2;
  if (size != expected) {
    Fail("--load-transformer-probs: %s has %llu bytes but exactly %llu were "
        "expected (%llu input bytes x %u vocabulary size x 2 bytes per "
        "float16); the file is too %s", path.c_str(), size, expected,
        num_distributions, vocab_size, size < expected ? "short" : "long");
  }
}

HalfFileReader::~HalfFileReader() {
  fclose(file_);
}

void HalfFileReader::Read(float* values, size_t n) {
  if (available_ < n) {
    memmove(buffer_.data(), buffer_.data() + pos_,
        available_ * sizeof(uint16_t));
    pos_ = 0;
    available_ += fread(buffer_.data() + available_, sizeof(uint16_t),
        buffer_.size() - available_, file_);
    if (available_ < n) {
      Fail("unexpected end of file while reading %s", path_.c_str());
    }
  }
  HalvesToFloats(buffer_.data() + pos_, values, n);
  pos_ += n;
  available_ -= n;
}

Predictor::Predictor(const std::vector<bool>& vocab,
    const PredictorOptions& options) : manager_(),
    sigmoid_(100001), vocab_(vocab), ppmd_only_(options.ppmd_only),
    transformer_only_(options.transformer_only),
    num_input_bytes_(options.num_input_bytes) {
  for (int i = 0; i < 256; ++i) {
    if (vocab_[i]) vocab_bytes_.push_back(i);
  }
  vocab_size_ = vocab_bytes_.size();
  // Uniform, so that the loss of the first byte — predicted before the
  // transformer has produced anything — is counted the same way the byte
  // mixer's initial state makes it count outside --transformer-only.
  probs_scratch_.assign(vocab_size_, 1.0f);
  if (options.transformer_only && options.transformer_weights.empty()) {
    Fail("--transformer-only runs the transformer, but no transformer "
        "weights are available");
  }
  if (!options.save_ppmd_probs.empty()) {
    ppmd_probs_writer_.reset(new HalfFileWriter(options.save_ppmd_probs));
  }
  if (!options.load_transformer_probs.empty()) {
    // The loaded distributions stand in for the transformer's output, so the
    // transformer must be the model that would otherwise have run.
    if (options.transformer_weights.empty() && !ppmd_only_) {
      Fail("--load-transformer-probs replaces the transformer's output "
          "distributions, but no transformer is enabled: the lstm would be "
          "run instead");
    }
    transformer_probs_reader_.reset(new HalfFileReader(
        options.load_transformer_probs, options.num_input_bytes, vocab_size_));
    // The loss of the loaded distributions is the transformer's loss.
    print_transformer_loss_ = true;
  }
  if (!options.transformer_weights.empty() && !ppmd_only_ &&
      !transformer_probs_reader_) {
    transformer_.reset(new fx2::opt::TransformerOpt(
        options.transformer_weights.c_str(), fx2::opt::AttnKind::KVI8));
    half_scratch_.resize(kTransformerVocabSize);
    transformer_probs_.resize(kTransformerVocabSize);
    transformer_prior_.resize(kTransformerVocabSize);
    print_transformer_loss_ = true;
    if (!options.save_transformer_probs.empty()) {
      transformer_probs_writer_.reset(
          new HalfFileWriter(options.save_transformer_probs));
    }
  }
  for (int i = 0; i < 256; ++i) byte_to_index_[i] = -1;
  for (unsigned int i = 0; i < vocab_size_; ++i) {
    byte_to_index_[vocab_bytes_[i]] = i;
  }
  for (int i = 0; i < 256; ++i) tf_byte_to_index_[i] = -1;
  for (unsigned int i = 0; i < kTransformerVocabSize; ++i) {
    tf_byte_to_index_[kTransformerVocab[i]] = i;
  }
  if (transformer_) {
    unsigned int oov = 0, missing = 0;
    for (int b = 0; b < 256; ++b) {
      if (vocab_[b] && tf_byte_to_index_[b] < 0) ++oov;
      if (!vocab_[b] && tf_byte_to_index_[b] >= 0) ++missing;
    }
    fprintf(stderr, "transformer vocabulary: %u bytes; input vocabulary: %u "
        "bytes, of which %u outside the transformer's (coded with the ppmd's "
        "distribution, each resets the transformer context); %u transformer "
        "bytes unused by this input\n", kTransformerVocabSize, vocab_size_,
        oov, missing);
  }
  // 0xFF is not a vocabulary index, so the window cannot match the
  // separator before 15 real tokens have been seen.
  memset(separator_window_, 0xFF, sizeof(separator_window_));
  if (ppmd_only_ || transformer_only_) {
    AddPPMD();
    return;
  }
  AddBracket();
  // With load_transformer_probs the ppmd is not run: its mixer input is a
  // constant and the transformer's distributions come from the file.
  if (!transformer_probs_reader_) AddPPMD();
  fxcm_model_.emplace();
  fxcm_neutral_input_ = sigmoid_.Logit(0.5f);
  for (int raw = -2047; raw <= 2047; ++raw) {
    float p = fxcm_model_->RawPredictionProbability(static_cast<short>(raw));
    if (p < 1.0e-4f) p = 1.0e-4f;
    else if (p > 1.0f - 1.0e-4f) p = 1.0f - 1.0e-4f;
    fxcm_stretched_inputs_[raw + 2047] = sigmoid_.Logit(p);
  }
  fxcm_stretched_inputs_[4095] = fxcm_neutral_input_;
  AddWord();
  AddMatch();
  AddDoubleIndirect();
  AddMixers();
  auxiliary_size_ = 2;
}

void Predictor::FreeFxcmMemory() {
  if (fxcm_model_) fxcm_model_->FreeMemory();
}

unsigned long long Predictor::GetNumModels() {
  unsigned long long num = 0;

  // models
  num += bracket_model_->NumOutputs(); // bracket
  num += fxcm_model_->NumOutputs();
  num += direct_models_.size();
  num += match_models_.size();
  num += indirect_ns_models_.size();
  num += indirect_r_models_.size();
  num += 1;  // ppmd byte model (a constant input with
             // --load-transformer-probs)
  num += byte_mixer_->NumOutputs();
#if LEXT_LSTM
  num += lstm_mixer_->NumOutputs();  // the online lstm mixer's bit prediction
#endif
#if LEXT_TF_APM & 2
  num += 1;  // LEXT_TF_APM mode 2: the APM-refined transformer prediction
#endif
  return num;
}

// lext_big CMIX_L0_LR_SCALE / CMIX_L1_LR_SCALE (BIG_NOTES.md §6): compile-time
// scales on the learning rates of the two final cmix mixer layers.
// CMIX_L0_LR_SCALE multiplies the learning rate of every layer-0 mixer (the 23
// AddMixer(0, ...) calls in AddMixers(), 0.0005..0.005); CMIX_L1_LR_SCALE that
// of the layer-1 mixer (AddMixer(1, ..., 0.0003)). Mixer::Perceive uses the
// rate as update = learning_rate_ * (Logistic(p_) - bit) (then the step-count
// decay 1.0/0.7/0.3/0.2, untouched). The multiplication is only compiled when
// the knob is defined (*_SET is derived from that), so the default token
// stream is exactly today's. Not a learning rate and therefore not scaled:
// the 1.0e-4 of layers_.emplace_back(sigmoid_, 1.0e-4) is MixerInput's eps,
// the clamp of SetInput's probabilities to [eps, 1 - eps] before Logit.
#ifdef CMIX_L0_LR_SCALE
#define CMIX_L0_LR_SCALE_SET 1
static_assert(CMIX_L0_LR_SCALE > 0.0 && CMIX_L0_LR_SCALE <= 100.0,
    "CMIX_L0_LR_SCALE must be in (0, 100]");
#else
#define CMIX_L0_LR_SCALE 1.0f
#define CMIX_L0_LR_SCALE_SET 0
#endif
#ifdef CMIX_L1_LR_SCALE
#define CMIX_L1_LR_SCALE_SET 1
static_assert(CMIX_L1_LR_SCALE > 0.0 && CMIX_L1_LR_SCALE <= 100.0,
    "CMIX_L1_LR_SCALE must be in (0, 100]");
#else
#define CMIX_L1_LR_SCALE 1.0f
#define CMIX_L1_LR_SCALE_SET 0
#endif

void Predictor::AddMixer(int layer, const unsigned long long& context,
    float learning_rate) {
#if CMIX_L0_LR_SCALE_SET
  if (layer == 0) learning_rate *= CMIX_L0_LR_SCALE;
#endif
#if CMIX_L1_LR_SCALE_SET
  if (layer != 0) learning_rate *= CMIX_L1_LR_SCALE;
#endif
  if (layer == 0) {
    mixer_0_.emplace_back(
        layers_[layer].Inputs(), layers_[layer].ExtraInputs(), context,
      learning_rate, mixer_0_.size());
  } else {
    mixer_1_.emplace_back(
        layers_[layer].Inputs(), layers_[layer].ExtraInputs(), context,
      learning_rate, mixer_1_.size());
  }
}

void Predictor::AddBracket() {
  bracket_model_.emplace(manager_.bit_context_, 200, 10, 100000, vocab_);
  const Context& context = manager_.AddBracketContext(manager_.bit_context_, 256, 15);
  direct_models_.emplace_back(context.GetContext(), manager_.bit_context_, 30, 0,
      context.Size());
  indirect_ns_models_.emplace_back(manager_.nonstationary_, context.GetContext(),
      manager_.bit_context_, 300, manager_.shared_map_);
}

// lext_big knobs: PPMD model order and sub-allocator size in MB (cmix-lex: 25 / 14000).
#ifndef PPMD_ORDER
#define PPMD_ORDER 25
#endif
#ifndef PPMD_MEM_MB
#define PPMD_MEM_MB 14000
#endif
void Predictor::AddPPMD() {
  byte_model_.emplace(PPMD_ORDER, PPMD_MEM_MB, manager_.bit_context_, vocab_);
}

void Predictor::AddWord() {
  float delta = 200;
  std::vector<std::vector<unsigned int>> model_params = {
  {0},
   {0, 1}, 
      {1}, 
      {1, 2},
      {1, 3}, 
       {2, 3},
       {3, 4},
      {1, 2, 4},
      {2, 3, 4},
       {2}
      };
  for (const auto& params : model_params) {
    const Context& context = manager_.AddSparseContext(manager_.words_, params);
    indirect_ns_models_.emplace_back(manager_.nonstationary_, context.GetContext(),
        manager_.bit_context_, delta, manager_.shared_map_);
  }

  std::vector<std::vector<unsigned int>> model_params2 = {
  {0}, 
  {1}, 
      {1, 3},
       {1, 2, 3}, 
       {7, 2}};
  for (const auto& params : model_params2) {
    const Context& context = manager_.AddSparseContext(manager_.words_, params);
    match_models_.emplace_back(manager_.history_, context.GetContext(),
        manager_.bit_context_, 200, 0.5, 2000000, &(manager_.longest_match_));
    if (params[0] == 1 && params.size() == 1) {
      indirect_r_models_.emplace_back(manager_.run_map_, context.GetContext(),
          manager_.bit_context_, delta, manager_.shared_map_);
    }
  }
}

void Predictor::AddMatch() {
  float delta = 0.5;
  int limit = 200;
  unsigned long long max_size = 2000000;
  std::vector<std::vector<int>> model_params = {
  {0, 8}, 
  {1, 8}, 
  {7, 4},
      {11, 3}, 
      {13, 2}, 
  };

  for (const auto& params : model_params) {
    const Context& context = manager_.AddContextHashContext(manager_.bit_context_,params[0], params[1]);
    match_models_.emplace_back(manager_.history_, context.GetContext(),
        manager_.bit_context_, limit, delta, std::min(max_size, context.Size()),
        &(manager_.longest_match_));
  }
}

void Predictor::AddDoubleIndirect() {
  float delta = 400;
  indirect_ns_models_.emplace_back(manager_.nonstationary_, manager_.ind1,  manager_.bit_context_, delta, manager_.shared_map_);
  indirect_ns_models_.emplace_back(manager_.nonstationary_, manager_.ind2,  manager_.bit_context_, delta, manager_.shared_map_);
  indirect_ns_models_.emplace_back(manager_.nonstationary_, manager_.ind3,  manager_.bit_context_, delta, manager_.shared_map_);
  indirect_ns_models_.emplace_back(manager_.nonstationary_, manager_.ind5,  manager_.bit_context_, delta, manager_.shared_map_);
}

unsigned int Discretize(float p) {
  return 1 + 4094 * p;
}
// lext_big CMIX_L0_MIXER_MASK (Hutter time/memory study): bit i (0..22) keeps
// layer-0 mixer i in the list below (default: all 23). Every consumer sizes
// itself from mixer_0_.size(), so a masked mixer simply does not exist: no
// dot product, no weight update, no weight-set memory. Changes the output.
#ifndef CMIX_L0_MIXER_MASK
#define CMIX_L0_MIXER_MASK 0x7fffffu
#endif
static_assert((CMIX_L0_MIXER_MASK & 0x7fffffu) != 0, "CMIX_L0_MIXER_MASK must keep at least one layer-0 mixer");

void Predictor::AddMixers() {
  unsigned int vocab_size = 0;
  for (unsigned int i = 0; i < vocab_.size(); ++i) {
    if (vocab_[i]) ++vocab_size;
  }
  // With the transformer the lstm is never run: the byte mixer only carries
  // the externally set distribution, so the lstm (and its memory) is not
  // allocated. Nothing after this point draws from rand(), so skipping the
  // lstm's initialization does not shift any other model's random state.
  byte_mixer_.emplace(1, manager_.bit_context_, vocab_,
      vocab_size, transformer_ ? nullptr :
      new Lstm(vocab_size, vocab_size, 170, 1, 128, 0.03, 10));
#if LEXT_LSTM
  // LEXT_LSTM: the online lstm mixer (cmix-lex's 170 cells / horizon 128 /
  // learning rate 0.03), fed the ppmd's distribution (1), the transformer's
  // (2) or both concatenated (3, lstm input 2 * vocab_size). Constructed after
  // byte_mixer_, the default build's last rand() consumer, so its weight
  // initialization only appends to the random sequence -- identically on the
  // compression and the decompression side.
  lstm_mixer_.emplace(manager_.bit_context_, vocab_, vocab_size,
      LEXT_LSTM == 3 ? 2u : 1u);
#endif

  for (int i = 0; i < 2; ++i) {
    layers_.emplace_back(sigmoid_,
        1.0e-4);
  }

  unsigned long long input_size = GetNumModels();
  std::cout << "num models " << input_size << "\n";
  layers_[0].SetNumModels(input_size);

  if (CMIX_L0_MIXER_MASK & (1u << 0)) AddMixer(0, manager_.mx9, 0.005);  // mixer 0
  if (CMIX_L0_MIXER_MASK & (1u << 1)) AddMixer(0, manager_.mx10, 0.0005);  // mixer 1
  if (CMIX_L0_MIXER_MASK & (1u << 2)) AddMixer(0, manager_.mx11, 0.005);  // mixer 2
  if (CMIX_L0_MIXER_MASK & (1u << 3)) AddMixer(0, manager_.mx12, 0.0005);  // mixer 3
  if (CMIX_L0_MIXER_MASK & (1u << 4)) AddMixer(0, manager_.mx13, 0.005);  // mixer 4
  if (CMIX_L0_MIXER_MASK & (1u << 5)) AddMixer(0, manager_.mxx, 0.001);  // mixer 5
  if (CMIX_L0_MIXER_MASK & (1u << 6)) AddMixer(0, manager_.recent_bytes_[2], 0.002);  // mixer 6
  if (CMIX_L0_MIXER_MASK & (1u << 7)) AddMixer(0, manager_.line_break_, 0.0007);  // mixer 7
  if (CMIX_L0_MIXER_MASK & (1u << 8)) AddMixer(0, manager_.longest_match_, 0.0005);  // mixer 8
  if (CMIX_L0_MIXER_MASK & (1u << 9)) AddMixer(0, manager_.mx19cxt, 0.002);  // mixer 9
  if (CMIX_L0_MIXER_MASK & (1u << 10)) AddMixer(0, manager_.auxiliary_context_, 0.0005);  // mixer 10
  if (CMIX_L0_MIXER_MASK & (1u << 11)) AddMixer(0, manager_.mx18, 0.001);  // mixer 11
  if (CMIX_L0_MIXER_MASK & (1u << 12)) AddMixer(0, manager_.mx7, 0.001);  // mixer 12
  if (CMIX_L0_MIXER_MASK & (1u << 13)) AddMixer(0, manager_.wordscxt, 0.005);  // mixer 13
  if (CMIX_L0_MIXER_MASK & (1u << 14)) AddMixer(0, manager_.b2streamcxt, 0.001);  // mixer 14
  if (CMIX_L0_MIXER_MASK & (1u << 15)) AddMixer(0, manager_.mx5, 0.001);  // mixer 15
  if (CMIX_L0_MIXER_MASK & (1u << 16)) AddMixer(0, manager_.mx6, 0.005);  // mixer 16
  if (CMIX_L0_MIXER_MASK & (1u << 17)) AddMixer(0, manager_.b3streamcxt, 0.001);  // mixer 17
  if (CMIX_L0_MIXER_MASK & (1u << 18)) AddMixer(0, manager_.mx8, 0.001);  // mixer 18
  if (CMIX_L0_MIXER_MASK & (1u << 19)) AddMixer(0, manager_.mx17, 0.005);  // mixer 19
  if (CMIX_L0_MIXER_MASK & (1u << 20)) AddMixer(0, manager_.mx16, 0.005);  // mixer 20
  if (CMIX_L0_MIXER_MASK & (1u << 21)) AddMixer(0, manager_.mx14, 0.005);  // mixer 21
  if (CMIX_L0_MIXER_MASK & (1u << 22)) AddMixer(0, manager_.mx15, 0.005);  // mixer 22

  input_size = mixer_0_.size() + auxiliary_size_;
#if LEXT_LSTM
  // Predict() puts the lstm mixer's stretched prediction at index
  // mixer_0_.size() + 2 of layers_[1], after the fxcm and byte mixer inputs
  // (auxiliary_size_ stays 2: the auxiliary context is unchanged).
  input_size += 1;
#endif
#if LEXT_TF_APM & 2
  input_size += 1;  // the APM-refined transformer prediction (after the lstm slot, if any)
#endif
  layers_[1].SetNumModels(input_size);

  AddMixer(1,manager_.zero_context_, 0.0003);

  layers_[0].SetExtraInputSize(mixer_0_.size());

}
int lstmpr=0, lstmex=0;
#if FXCM_TF_MIXER >= 2
// lext_big FXCM_TF_MIXER=2: confidence bucket 0..3 of the byte mixer's
// (transformer's) bit prediction, |p - 0.5| in steps of 1/8; read by fxcm_v26.
int lstmconf=0;
#endif
float byte_mixer_output=0.0f;
float Predictor::Predict() {
  if (ppmd_only_ || transformer_only_) {
    float p = byte_model_->Predict()[0];
    // Keep the prediction away from 0 and 1 for the arithmetic coder.
    if (p < 0.001f) p = 0.001f;
    if (p > 0.999f) p = 0.999f;
    return p;
  }
  unsigned int input_index = 0;
  auto bracket_model_output = bracket_model_->Predict()[0];
  layers_[0].SetInput(input_index++, bracket_model_output);

  const unsigned int fxcm_model_outputs = fxcm_model_->NumOutputs();
  const short* fxcm_raw_outputs = fxcm_model_->RawPredictions();
  unsigned int fxcm_active_outputs = fxcm_model_->ActivePredictions();
  if (fxcm_active_outputs > fxcm_model_outputs) fxcm_active_outputs = fxcm_model_outputs;
  // fxcmv1 emits outputs densely from zero; carrying an active count avoids
  // a hot per-bit mask scan and the old unused float prediction mirror.
  // The lookup table is already clamped to MixerInput's stretched range, so
  // these 560-ish assignments can skip duplicate bounds checks.
  for (unsigned int j = 0; j < fxcm_active_outputs; ++j) {
    layers_[0].SetStretchedInputUnchecked(
        input_index, fxcm_stretched_inputs_[fxcm_raw_outputs[j] + 2047]);
    ++input_index;
  }
  for (unsigned int j = fxcm_active_outputs; j < fxcm_model_outputs; ++j) {
    layers_[0].SetStretchedInputUnchecked(input_index, fxcm_neutral_input_);
    ++input_index;
  }
  auto fxcm_model_index = input_index - 1;
  

  for (unsigned int i = 0; i < direct_models_.size(); ++i) {
    const std::valarray<float>& outputs = direct_models_[i].Predict();
    for (unsigned int j = 0; j < outputs.size(); ++j) {
      layers_[0].SetInput(input_index, outputs[j]);
      ++input_index;
    }
  }

  for (unsigned int i = 0; i < match_models_.size(); ++i) {
    const std::valarray<float>& outputs = match_models_[i].Predict();
    for (unsigned int j = 0; j < outputs.size(); ++j) {
      layers_[0].SetInput(input_index, outputs[j]);
      ++input_index;
    }
  }
 
  for (unsigned int i = 0; i < indirect_ns_models_.size(); ++i) {
    const std::valarray<float>& outputs = indirect_ns_models_[i].Predict();
    for (unsigned int j = 0; j < outputs.size(); ++j) {
      layers_[0].SetInput(input_index, outputs[j]);
      ++input_index;
    }
  }
 
  for (unsigned int i = 0; i < indirect_r_models_.size(); ++i) {
    const std::valarray<float>& outputs = indirect_r_models_[i].Predict();
    for (unsigned int j = 0; j < outputs.size(); ++j) {
      layers_[0].SetInput(input_index, outputs[j]);
      ++input_index;
    }
  }
  layers_[0].SetInput(input_index++,
      byte_model_ ? byte_model_->Predict()[0] : 0.5f);

  float byte_mixer_override = -1;

  if (byte_mixer_output == 0 || byte_mixer_output == 1) byte_mixer_override = byte_mixer_output;
  layers_[0].SetInput(input_index++, byte_mixer_output);
  auto byte_mixer_index = input_index - 1;
#if LEXT_LSTM
  layers_[0].SetInput(input_index++, lstm_mixer_output_);
  const unsigned int lstm_mixer_index = input_index - 1;
#endif
#if LEXT_TF_APM & 2
  {
    const float st_tf = TfApm::Stretch(byte_mixer_output);
    const float a = fabsf(st_tf);
    const int cls = a < 1.0f ? 0 : (a < 3.0f ? 1 : (a < 5.0f ? 2 : 3));
    const float q = tf_apm_in_.Predict(byte_mixer_output,
        static_cast<int>(manager_.bit_context_ & 255u) * 4 + cls);
    layers_[0].SetInput(input_index++, q);
  }
  const unsigned int tf_apm_index = input_index - 1;
#endif
#if LEXT_TF_APM
  tf_apm_predicted_ = true;
#endif

  float auxiliary_average = Sigmoid::Logistic(layers_[0].Inputs()[fxcm_model_index]) + Sigmoid::Logistic(layers_[0].Inputs()[byte_mixer_index]);
  auxiliary_average /= auxiliary_size_;
  manager_.auxiliary_context_ =auxiliary_average * 15;

  for (unsigned int i = 0; i < mixer_0_.size(); ++i) {
    float p = mixer_0_[i].Mix();
    layers_[0].SetExtraInput(i, p);
    layers_[1].SetStretchedInput(i, p);
  }
  layers_[1].SetStretchedInput(mixer_0_.size(), layers_[0].Inputs()[fxcm_model_index]);
  layers_[1].SetStretchedInput(mixer_0_.size() + 1, layers_[0].Inputs()[byte_mixer_index]);
#if LEXT_LSTM
  layers_[1].SetStretchedInput(mixer_0_.size() + 2,
      layers_[0].Inputs()[lstm_mixer_index]);
#endif
#if LEXT_TF_APM & 2
  layers_[1].SetStretchedInput(mixer_0_.size() + 2 + (LEXT_LSTM ? 1 : 0),
      layers_[0].Inputs()[tf_apm_index]);
#endif

  float p = Sigmoid::Logistic(mixer_1_[0].Mix());
  p = sse_.Predict(p);
#if LEXT_TF_APM & 1
  {
    // final refinement keyed by the transformer's confidence (see tf-apm.h)
    const float st_tf = TfApm::Stretch(byte_mixer_output);
    int b = static_cast<int>(st_tf + 8.0f);
    if (b < 0) b = 0;
    if (b > 15) b = 15;
    const unsigned int bc = manager_.bit_context_ & 255u;
    const int bpos = bc ? 31 - __builtin_clz(bc) : 0;
    const int agree = ((p >= 0.5f) == (byte_mixer_output >= 0.5f)) ? 1 : 0;
    const float q = tf_apm_final_.Predict(p, (b * 8 + bpos) * 2 + agree);
    p = (p + 3.0f * q) * 0.25f;
    if (p < 0.0001f) p = 0.0001f;
    if (p > 0.9999f) p = 0.9999f;
  }
#endif
  if (byte_mixer_override >= 0) {
    return byte_mixer_override;
  }
  return p;
}

void Predictor::WritePpmdProbs() {
  const std::valarray<float>& p = byte_model_->BytePredict();
  for (unsigned int i = 0; i < vocab_size_; ++i) {
    probs_scratch_[i] = p[vocab_bytes_[i]];
  }
  ppmd_probs_writer_->Write(probs_scratch_.data(), vocab_size_);
}

void Predictor::LoadTransformerProbs() {
  transformer_probs_reader_->Read(probs_scratch_.data(), vocab_size_);
  for (unsigned int i = 0; i < vocab_size_; ++i) {
    // Guard against zero (and NaN) probabilities, which would degenerate the
    // bit-level predictions fed to the arithmetic coder. Only probability
    // ratios matter downstream, so no renormalization is needed.
    if (!(probs_scratch_[i] >= 1e-6f)) probs_scratch_[i] = 1e-6f;
  }
  byte_mixer_->SetProbs(probs_scratch_.data());
}

// Replaces the lstm's byte-level update: feeds the completed byte and the
// ppmd's distribution to the pretrained transformer and passes the
// transformer's output distribution (over the next byte) to the byte mixer.
//
// The distributions cross the model boundary exactly as they did in the
// offline pipeline the transformer was trained and evaluated on
// (--save-ppmd-probs -> float16 file -> training / --load-transformer-probs):
// the
// ppmd's prior is rounded to float16 the way WritePpmdProbs writes it, and
// the output row goes through the same float16 rounding and >= 1e-6 guard
// LoadTransformerProbs applies to a file row.
//
// Articles (delimited by kArticleSeparator, and cut at kMaxArticleTokens
// like the training data loader splits them) are independent transformer
// contexts: the KV caches and recurrent states are reset at each piece's
// first token, the piece's last token is never fed (its successor starts a
// fresh context), and at the tokens the transformer therefore cannot
// predict — the first token of each piece — the ppmd's (float16-rounded)
// distribution is passed downstream instead.
void Predictor::TransformerByteUpdate() {
  const std::valarray<float>& p = byte_model_->BytePredict();
  // The ppmd's prior over the transformer's vocabulary (the mass the ppmd
  // puts on bytes outside it is simply not shown to the transformer).
  for (unsigned int i = 0; i < kTransformerVocabSize; ++i) {
    transformer_prior_[i] = p[kTransformerVocab[i]];
  }
  FloatsToHalves(transformer_prior_.data(), half_scratch_.data(),
      kTransformerVocabSize);

  int token = tf_byte_to_index_[manager_.bit_context_];
  const bool out_of_vocabulary = token < 0;
  memmove(separator_window_, separator_window_ + 1,
      sizeof(separator_window_) - 1);
  separator_window_[sizeof(separator_window_) - 1] =
      out_of_vocabulary ? 0xFF : (unsigned char)token;
  ++article_tokens_;

  // A byte the transformer has no token for cannot be fed to it; it is
  // treated like an article end: the current context is abandoned and the
  // next in-vocabulary byte starts a fresh one. (Inside the payload_lex side
  // blob at the end of the cmix-lex stream this effectively switches the
  // transformer off and passes the ppmd's distribution through.)
  bool last_of_piece = out_of_vocabulary ||
      memcmp(separator_window_, kArticleSeparator, sizeof(kArticleSeparator))
          == 0 ||
      article_tokens_ >= kMaxArticleTokens;
  if (last_of_piece) {
    // The next token starts a fresh context; its distribution is the ppmd's.
    HalvesToFloats(half_scratch_.data(), transformer_probs_.data(),
        kTransformerVocabSize);
    article_tokens_ = 0;
  } else {
    if (article_tokens_ == 1) transformer_->begin_article();
    transformer_->step((uint8_t)token, half_scratch_.data(),
        transformer_probs_.data());
    FloatsToHalves(transformer_probs_.data(), half_scratch_.data(),
        kTransformerVocabSize);
    HalvesToFloats(half_scratch_.data(), transformer_probs_.data(),
        kTransformerVocabSize);
  }
  if (transformer_probs_writer_) {
    transformer_probs_writer_->WriteHalves(half_scratch_.data(),
        kTransformerVocabSize);
  }
  // Scatter to the input's vocabulary order. Bytes the transformer does not
  // model keep the ppmd's probability; only ratios matter downstream
  // (ByteModel::Predict normalizes), so the sum need not be exactly one.
  for (unsigned int i = 0; i < vocab_size_; ++i) {
    int k = tf_byte_to_index_[vocab_bytes_[i]];
    probs_scratch_[i] = k >= 0 ? transformer_probs_[k] : p[vocab_bytes_[i]];
    if (!(probs_scratch_[i] >= 1e-6f)) probs_scratch_[i] = 1e-6f;
  }
  // With --transformer-only there is no byte mixer: probs_scratch_ is the
  // final destination of the distribution (and what the loss is measured on).
  if (byte_mixer_) byte_mixer_->SetProbs(probs_scratch_.data());
}

// Accumulates -ln p(byte) for the byte that just completed, where p is the
// distribution (normalized over the vocabulary) the byte mixer used to
// predict it: the transformer's output, or the loaded one with
// --load-transformer-probs.
// Must run before that distribution is replaced with the next byte's.
// Prints the running average every million tokens and at the last token.
void Predictor::AccumulateTransformerLoss() {
  double sum = 0, prob = 0;
  if (byte_mixer_) {
    const std::valarray<float>& p = byte_mixer_->BytePredict();
    for (int byte : vocab_bytes_) sum += p[byte];
    prob = p[manager_.bit_context_];
  } else {
    // --transformer-only: the distribution was left in probs_scratch_.
    for (unsigned int i = 0; i < vocab_size_; ++i) sum += probs_scratch_[i];
    int index = byte_to_index_[manager_.bit_context_];
    if (index >= 0) prob = probs_scratch_[index];
  }
  double ratio = sum > 0 ? prob / sum : 0;
  if (!(ratio > 1e-38)) ratio = 1e-38;  // avoid inf from zero probabilities
  transformer_loss_sum_ -= std::log(ratio);
  ++transformer_tokens_;
  if (transformer_tokens_ % 1000000 == 0 ||
      transformer_tokens_ == num_input_bytes_) {
    fprintf(stderr, "\r%*s\r", 70, "");  // clear the progress line
    printf("transformer loss: %.6f nats/token over %llu tokens\n",
        transformer_loss_sum_ / transformer_tokens_, transformer_tokens_);
    fflush(stdout);
  }
}

#if LEXT_LSTM
// LEXT_LSTM: byte-level update of the online lstm mixer, run right after the
// transformer byte mixer's update for the same completed byte (so, like
// cmix-lex's lstm, it is stepped once per byte and predicts the next one).
// Its input for predicting the next byte is
//   1: the ppmd's distribution byte_model_->BytePredict() -- exactly what
//      cmix-lex fed its lstm (the transformer is not consulted);
//   2: the transformer byte mixer's distribution: the probs_scratch_ row
//      TransformerByteUpdate() just handed to byte_mixer_->SetProbs(), read
//      back scattered to byte values through byte_mixer_->BytePredict()
//      (bytes outside the vocabulary are 0 there and have no lstm input), so
//      the lstm learns online to correct the frozen transformer;
//   3: both, concatenated [ppmd ; transformer] (lstm input 2 * vocab_size).
// The lstm is then stepped with the completed byte, as ByteMixer::ByteUpdate
// does, and its output distribution yields the mixer's bit predictions.
void Predictor::LstmMixerByteUpdate() {
#if LEXT_LSTM == 1 || LEXT_LSTM == 3
  if (byte_model_) {
    const std::valarray<float>& p = byte_model_->BytePredict();
    for (int j = 0; j < 256; ++j) lstm_mixer_->SetInput(0, j, p[j]);
  }
  // (--load-transformer-probs runs no ppmd: the block stays zero.)
#endif
#if LEXT_LSTM == 2 || LEXT_LSTM == 3
  {
    const std::valarray<float>& q = byte_mixer_->BytePredict();
    for (int j = 0; j < 256; ++j) {
      lstm_mixer_->SetInput(LEXT_LSTM == 3 ? 1 : 0, j, q[j]);
    }
  }
#endif
  lstm_mixer_->ByteUpdate();
}
#endif  // LEXT_LSTM

void Predictor::Perceive(int bit) {
  if (ppmd_only_ || transformer_only_) {
    byte_model_->Perceive(bit);
    // Mirrors how ContextManager::UpdateContexts maintains bit_context_,
    // which the ppmd reads the completed byte from.
    bool byte_update = manager_.bit_context_ >= 128;
    manager_.bit_context_ += manager_.bit_context_ + bit;
    if (byte_update) {
      manager_.bit_context_ -= 256;
      // Before WritePpmdProbs and TransformerByteUpdate overwrite the
      // distribution the completed byte was predicted with.
      if (print_transformer_loss_) AccumulateTransformerLoss();
      byte_model_->ByteUpdate();
      if (ppmd_probs_writer_) WritePpmdProbs();
      if (transformer_) TransformerByteUpdate();
      manager_.bit_context_ = 1;
    }
    return;
  }
  bracket_model_->Perceive(bit);

  for (unsigned int i = 0; i < direct_models_.size(); ++i) {
    direct_models_[i].Perceive(bit);
  }
  for (unsigned int i = 0; i < match_models_.size(); ++i) {
    match_models_[i].Perceive(bit);
  }
  for (unsigned int i = 0; i < indirect_ns_models_.size(); ++i) {
    indirect_ns_models_[i].Perceive(bit);
  }
  for (unsigned int i = 0; i < indirect_r_models_.size(); ++i) {
    indirect_r_models_[i].Perceive(bit);
  }

  if (byte_model_) byte_model_->Perceive(bit);

  byte_mixer_->Perceive(bit);
#if LEXT_LSTM
  lstm_mixer_->Perceive(bit);
#endif

  for (auto& mixer: mixer_0_) {
    mixer.Perceive(bit);
  }
  for (auto& mixer: mixer_1_) {
    mixer.Perceive(bit);
  }

  sse_.Perceive(bit);
#if LEXT_TF_APM
  if (tf_apm_predicted_) {
#if LEXT_TF_APM & 1
    tf_apm_final_.Update(bit);
#endif
#if LEXT_TF_APM & 2
    tf_apm_in_.Update(bit);
#endif
    tf_apm_predicted_ = false;
  }
#endif

  bool byte_update = false;
  if (manager_.bit_context_ >= 128) byte_update = true;

  manager_.UpdateContexts(bit);
  if (byte_update) {
    if (print_transformer_loss_) AccumulateTransformerLoss();
    bracket_model_->ByteUpdate();

    for (unsigned int i = 0; i < direct_models_.size(); ++i) {
      direct_models_[i].ByteUpdate();
    }
    for (unsigned int i = 0; i < match_models_.size(); ++i) {
      match_models_[i].ByteUpdate();
    }
    for (unsigned int i = 0; i < indirect_ns_models_.size(); ++i) {
      indirect_ns_models_[i].ByteUpdate();
    }

    for (unsigned int i = 0; i < indirect_r_models_.size(); ++i) {
      indirect_r_models_[i].ByteUpdate();
    }

    if (byte_model_) {
      byte_model_->ByteUpdate();
      if (ppmd_probs_writer_) WritePpmdProbs();

      if (transformer_) {
        TransformerByteUpdate();
      } else {
        const std::valarray<float>& p = byte_model_->BytePredict();
        for (unsigned int j = 0; j < 256; ++j) {
          byte_mixer_->SetInput(j,p[j]);
        }

        byte_mixer_->ByteUpdate();
      }
    } else {
      // --load-transformer-probs: the ppmd and the transformer are not run;
      // the byte-level distribution comes from the file instead.
      LoadTransformerProbs();
    }
#if LEXT_LSTM
    // After the ppmd's and the transformer byte mixer's updates for this
    // byte, whose new distributions are the lstm mixer's inputs.
    LstmMixerByteUpdate();
#endif
  }
  byte_mixer_output = byte_mixer_->Predict()[0];
#if LEXT_LSTM
  lstm_mixer_output_ = lstm_mixer_->Predict()[0];
#endif
  lstmpr=Discretize(byte_mixer_output);
  lstmex=byte_mixer_->ex;
#if FXCM_TF_MIXER >= 2
  lstmconf=std::min(3, (int)(fabsf(byte_mixer_output - 0.5f) * 8));
#endif
  fxcm_model_->Perceive(bit);
  if (byte_update)manager_.bit_context_ = 1;
}

void Predictor::Pretrain(int bit) {
  bracket_model_->Predict();
  fxcm_model_->Predict();
    
  for (unsigned int i = 0; i < direct_models_.size(); ++i) {
    direct_models_[i].Predict();
  }
  for (unsigned int i = 0; i < match_models_.size(); ++i) {
    match_models_[i].Predict();
  }
  for (unsigned int i = 0; i < indirect_ns_models_.size(); ++i) {
    indirect_ns_models_[i].Predict();
  }
  for (unsigned int i = 0; i < indirect_r_models_.size(); ++i) {
    indirect_r_models_[i].Predict();
  }

  bracket_model_->Perceive(bit);
  fxcm_model_->Perceive(bit);
    
  for (unsigned int i = 0; i < direct_models_.size(); ++i) {
    direct_models_[i].Perceive(bit);
  }
  for (unsigned int i = 0; i < match_models_.size(); ++i) {
    match_models_[i].Perceive(bit);
  }
  for (unsigned int i = 0; i < indirect_ns_models_.size(); ++i) {
    indirect_ns_models_[i].Perceive(bit);
  }
  for (unsigned int i = 0; i < indirect_r_models_.size(); ++i) {
    indirect_r_models_[i].Perceive(bit);
  }

  bool byte_update = false;
  if (manager_.bit_context_ >= 128) byte_update = true;
  manager_.UpdateContexts(bit);
  if (byte_update) {
    bracket_model_->ByteUpdate();

    for (unsigned int i = 0; i < direct_models_.size(); ++i) {
      direct_models_[i].ByteUpdate();
    }
    for (unsigned int i = 0; i < match_models_.size(); ++i) {
      match_models_[i].ByteUpdate();
    }
    for (unsigned int i = 0; i < indirect_ns_models_.size(); ++i) {
      indirect_ns_models_[i].ByteUpdate();
    }
    for (unsigned int i = 0; i < indirect_r_models_.size(); ++i) {
      indirect_r_models_[i].ByteUpdate();
    }
    manager_.bit_context_ = 1;
  }
}
