// R12 streaming warm replay.  Follows the native observer's trace files while
// they grow (regular files: the observer opens them O_EXCL, so FIFOs are not
// possible), runs every arm online over the SAME unchanged native trajectory,
// and punches holes behind the read position so disk use stays bounded.
// Probabilities of all candidate arms are computed strictly before the bit is
// read; arms never feed back into the native coder (replay, not a codec).
//
// usage: stream_replay input.bin final_p.u16 stage.f32 hidden.q8 done_flag out.jsonl
//                      window_bytes abs_offset punch(0/1)
#include "integer_mixer.h"
#include "long_memory.h"
#include <cerrno>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <memory>
#include <chrono>
#include <thread>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <linux/falloc.h>

static bool exists(const char* p) { struct stat s; return ::stat(p, &s) == 0; }

class TailReader {
 public:
  TailReader(const char* path, const char* done, bool punch) : path_(path), done_(done), punch_(punch) {
    while (!exists(path)) { if (exists(done) && !exists(path)) throw std::runtime_error(std::string("trace never created: ") + path);
                            std::this_thread::sleep_for(std::chrono::milliseconds(50)); }
    fd_ = ::open(path, O_RDWR);
    if (fd_ < 0) fd_ = ::open(path, O_RDONLY), punch_ = false;
    if (fd_ < 0) throw std::runtime_error(std::string("cannot open ") + path);
    buf_.resize(1 << 20);
  }
  ~TailReader() { if (fd_ >= 0) ::close(fd_); }
  // Returns false only at true end of stream (writer finished and nothing left).
  bool read_exact(void* dst, size_t n) {
    char* out = static_cast<char*>(dst);
    while (n) {
      if (pos_ == len_) { if (!refill()) return false; continue; }
      size_t k = std::min(n, len_ - pos_);
      std::memcpy(out, buf_.data() + pos_, k); pos_ += k; out += k; n -= k; consumed_ += k;
    }
    if (punch_ && consumed_ - punched_ >= (256ull << 20)) {
      uint64_t upto = (consumed_ / 4096) * 4096;
      if (fallocate(fd_, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE, punched_, upto - punched_) == 0) punched_ = upto;
      else { punch_failed_ = true; punch_ = false; }
    }
    return true;
  }
  bool punch_failed() const { return punch_failed_; }
  uint64_t consumed() const { return consumed_; }
 private:
  bool refill() {
    for (;;) {
      ssize_t r = ::read(fd_, buf_.data(), buf_.size());
      if (r > 0) { pos_ = 0; len_ = size_t(r); return true; }
      if (r < 0 && errno == EINTR) continue;
      if (r < 0) throw std::runtime_error("read error");
      if (exists(done_.c_str())) {   // writer has exited: one last read closes the race
        r = ::read(fd_, buf_.data(), buf_.size());
        if (r > 0) { pos_ = 0; len_ = size_t(r); return true; }
        return false;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
  }
  std::string path_, done_;
  bool punch_, punch_failed_ = false;
  int fd_ = -1;
  std::vector<char> buf_;
  size_t pos_ = 0, len_ = 0;
  uint64_t consumed_ = 0, punched_ = 0;
};

// ---- verbatim round-9 causal adaptive law (research_round9_adaptive_law.cpp) ----
class HPCausalAdaptive {
 public:
  uint32_t Predict(uint32_t native_p, float neural_p, bool previous_valid) {
    const double ell = std::log(double(native_p) / (65536.0 - double(native_p)));
    float feature = 0.0f;
    if (previous_valid) {
      const double nn = std::max(1.0 / 65536.0, std::min(65535.0 / 65536.0, double(neural_p)));
      feature = float(std::max(-12.0, std::min(12.0, std::log(nn / (1.0 - nn)) - ell)) / 12.0);
    }
    const double dot = (0.0016181118716570748 + (-0.007454085408717222) * ell) + 2.3818512619982752 * double(feature);
    const double multipliers[4] = {0.5, 1.0, 1.5, 2.0};
    experts_[0] = native_p;
    for (int k = 1; k < 5; k++) {
      const double z = ell + multipliers[k - 1] * dot;
      const double prob = z >= 0 ? 1.0 / (1.0 + std::exp(-z)) : std::exp(z) / (1.0 + std::exp(z));
      experts_[k] = uint32_t(std::max(1.0, std::min(65535.0, std::floor(65536.0 * prob + 0.5))));
    }
    double mixture = 0.0;
    for (int k = 0; k < 5; k++) mixture += weights_[k] * double(experts_[k]) / 65536.0;
    pending_ = true;
    return uint32_t(std::max(1.0, std::min(65535.0, std::floor(65536.0 * mixture + 0.5))));
  }
  void Observe(int bit) {
    if (!pending_) return;
    constexpr double epsilon = 2.6441431586476938e-06;
    double total = 0.0;
    for (int k = 0; k < 5; k++) {
      const double pk = bit ? double(experts_[k]) / 65536.0 : 1.0 - double(experts_[k]) / 65536.0;
      weights_[k] *= pk; total += weights_[k];
    }
    for (int k = 0; k < 5; k++) weights_[k] = (1.0 - epsilon) * weights_[k] / total + epsilon / 5.0;
    pending_ = false;
  }
  uint32_t expert(int k) const { return experts_[k]; }
 private:
  double weights_[5] = {0.2, 0.2, 0.2, 0.2, 0.2};
  uint32_t experts_[5] = {};
  bool pending_ = false;
};

static uint16_t q16(float p) {
  if (!std::isfinite(p)) throw std::invalid_argument("nonfinite stage probability");
  if (p <= 0) return 1; if (p >= 1) return 65535;
  return uint16_t(std::clamp(uint32_t(double(p) * 65536.0 + 0.5), 1u, 65535u));
}
static uint16_t from_logit(float z) {
  if (!std::isfinite(z)) throw std::invalid_argument("nonfinite stage logit");
  double value = std::clamp(double(z) * 256.0, -4096.0, 4096.0);
  int64_t quantized = value >= 0 ? int64_t(value + 0.5) : -int64_t(-value + 0.5);
  return hp::squash(quantized);
}
// Project's raw-byte classifier (integer_mixer_replay.cpp), kept verbatim.
static unsigned class_raw(unsigned byte) {
  if (byte == ' ') return 0; if (byte == '\n') return 1; if (byte >= 128) return 2;
  if (byte >= 'a' && byte <= 'z') return 3; if (byte >= 'A' && byte <= 'Z') return 4;
  if (byte >= '0' && byte <= '9') return 5; if (byte < 32) return 6;
  if (byte == '<' || byte == '>' || byte == '[' || byte == ']') return 7;
  if (byte == '.' || byte == ',' || byte == ';' || byte == ':') return 8;
  return 9;
}
// Same classes evaluated on the DECODED character (research_round7_wrt.py inverse map).
static unsigned inverse_byte(unsigned c) {
  if (123 <= c && c < 127) c += 80 - 123; else if (80 <= c && c < 84) c -= 80 - 123;
  else if ((58 <= c && c <= 63) || (74 <= c && c <= 79)) c ^= 0x70;
  if (c == 88 || c == 96) c ^= 88 ^ 96;
  return c;
}
static unsigned class_decoded(unsigned byte) { return class_raw(byte >= 128 ? byte : inverse_byte(byte)); }

struct MixerArm { std::string name; hp::OnlineMixer m; bool memory; bool memory_zero; bool decoded_class; };

int main(int argc, char** argv) {
  if (argc != 10) { std::fprintf(stderr, "usage: input final_p stage hidden done out.jsonl window abs_offset punch\n"); return 2; }
  const char* done = argv[5];
  const uint64_t window = std::stoull(argv[7]), abs_offset = std::stoull(argv[8]);
  const bool punch = std::string(argv[9]) == "1";
  std::vector<unsigned char> input;
  { FILE* f = std::fopen(argv[1], "rb"); if (!f) return 3; unsigned char b[1 << 16]; size_t r;
    while ((r = std::fread(b, 1, sizeof b, f)) > 0) input.insert(input.end(), b, b + r); std::fclose(f); }
  FILE* out = std::fopen(argv[6], "w"); if (!out) return 4;
  std::vector<double> nlog(65536);
  for (int i = 1; i < 65536; i++) nlog[i] = -std::log2(double(i) / 65536.0);
  try {
    TailReader fp(argv[2], done, punch), st(argv[3], done, punch), hd(argv[4], done, punch);
    char magic[8]; uint32_t width = 0;
    if (!st.read_exact(magic, 8) || std::memcmp(magic, "HPSTG001", 8) || !st.read_exact(&width, 4) || width != 19)
      throw std::runtime_error("bad stage header");
    std::vector<MixerArm> mixers;
    auto add = [&](const std::string& n, bool neural, bool identity, uint32_t rate, bool mem, bool memzero, bool dec, bool global) {
      mixers.push_back({n, hp::OnlineMixer(neural, false, identity, rate), mem, memzero, dec});
      mixers.back().m.SetGlobalContext(global);
    };
    add("mixer_identity", true, true, 1000, false, false, false, false);
    add("mixer_full_250", true, false, 250, false, false, false, false);
    add("mixer_full_1000", true, false, 1000, false, false, false, false);
    add("mixer_full_4000", true, false, 4000, false, false, false, false);
    add("mixer_full_1000_decodedclass", true, false, 1000, false, false, true, false);
    add("mixer_no_explicit_nn_1000", false, false, 1000, false, false, false, false);
    add("mixer_global_1000", true, false, 1000, false, false, false, true);
    add("mixer_memory_zero_1000", true, false, 1000, false, true, false, false);
    add("mixer_long_memory_1000", true, false, 1000, true, false, false, false);
    HPCausalAdaptive adaptive;
    const size_t NA = mixers.size() + 2;  // + adaptive_law + wider_frozen_a1
    std::vector<std::string> names; for (auto& m : mixers) names.push_back(m.name);
    names.push_back("adaptive_law_r9"); names.push_back("wider_frozen_a1");
    hp::LongMemory memory;
    bool valid = false; unsigned cls_raw = 9, cls_dec = 9;
    double wbase = 0; std::vector<double> warm(NA, 0.0), tot(NA, 0.0); double tbase = 0;
    uint64_t t = 0, wstart = 0; uint64_t identity_mismatch = 0;
    auto flush = [&](bool partial) {
      std::fprintf(out, "{\"type\":\"window\",\"abs_offset\":%llu,\"history_bytes\":%llu,\"bytes\":%llu,\"partial\":%s,\"baseline_bits\":%.6f,\"arms\":{",
                   (unsigned long long)(abs_offset + wstart), (unsigned long long)wstart, (unsigned long long)(t - wstart),
                   partial ? "true" : "false", wbase);
      for (size_t a = 0; a < NA; a++) std::fprintf(out, "%s\"%s\":%.6f", a ? "," : "", names[a].c_str(), warm[a]);
      std::fprintf(out, "}}\n"); std::fflush(out);
      wbase = 0; std::fill(warm.begin(), warm.end(), 0.0); wstart = t;
    };
    auto t0 = std::chrono::steady_clock::now();
    for (; t < input.size(); t++) {
      const unsigned ch = input[t];
      bool ok = true; uint16_t p[8]; float rows[8][19];
      for (int b = 0; b < 8 && ok; b++) ok = fp.read_exact(&p[b], 2) && st.read_exact(rows[b], 76);
      if (!ok) break;  // stream ended mid-byte (encoder stopped); discard incomplete byte
      double bbase = 0; std::vector<double> barm(NA, 0.0);
      for (unsigned bit = 0; bit < 8; bit++) {
        const float* row = rows[bit]; const uint16_t pn = p[bit];
        if (pn == 0) throw std::runtime_error("zero native probability");
        const unsigned y = (ch >> (7 - bit)) & 1;
        std::array<uint16_t, 14> base_sources; base_sources.fill(32768);
        base_sources[0] = q16(row[14]);
        for (unsigned i = 0; i < 12; i++) base_sources[i + 1] = from_logit(row[i]);
        const uint16_t nnq = q16(row[17]);
        auto memf = memory.Features();
        bbase += nlog[y ? pn : 65536 - pn];
        for (size_t a = 0; a < mixers.size(); a++) {
          auto src = base_sources;
          if (mixers[a].memory) for (unsigned i = 0; i < 8; i++) src[i + 5] = memf[i];
          if (mixers[a].memory_zero) for (unsigned i = 0; i < 8; i++) src[i + 5] = 32768;
          const unsigned cls = mixers[a].decoded_class ? cls_dec : cls_raw;
          const uint16_t q = mixers[a].m.Predict(pn, nnq, src, bit, cls, valid);
          if (a == 0 && q != pn) identity_mismatch++;
          barm[a] += nlog[y ? q : 65536 - q];
          mixers[a].m.Observe(y);
        }
        const uint32_t qa = adaptive.Predict(pn, row[17], valid);
        barm[mixers.size()] += nlog[y ? qa : 65536 - qa];
        const uint32_t qw = adaptive.expert(2);  // multiplier 1.0 = frozen wider law
        barm[mixers.size() + 1] += nlog[y ? qw : 65536 - qw];
        adaptive.Observe(y);
      }
      unsigned char h[193];
      if (!hd.read_exact(h, 193)) { break; }
      valid = h[0] != 0; cls_raw = class_raw(ch); cls_dec = class_decoded(ch);
      memory.UpdateHidden(h);
      wbase += bbase; tbase += bbase;
      for (size_t a = 0; a < NA; a++) { warm[a] += barm[a]; tot[a] += barm[a]; }
      if (t + 1 - wstart == window) { t++; flush(false); t--; }
    }
    if (t > wstart) flush(true);
    const double secs = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    std::fprintf(out, "{\"type\":\"summary\",\"bytes\":%llu,\"input_bytes\":%zu,\"baseline_bits\":%.6f,\"identity_mismatch_bits\":%llu,\"punch_failed\":%s,\"consumer_wall_seconds\":%.1f,\"totals\":{",
                 (unsigned long long)t, input.size(), tbase, (unsigned long long)identity_mismatch,
                 (fp.punch_failed() || st.punch_failed() || hd.punch_failed()) ? "true" : "false", secs);
    for (size_t a = 0; a < NA; a++) std::fprintf(out, "%s\"%s\":%.6f", a ? "," : "", names[a].c_str(), tot[a]);
    std::fprintf(out, "}}\n"); std::fclose(out);
  } catch (const std::exception& e) {
    std::fprintf(out, "{\"type\":\"error\",\"what\":\"%s\"}\n", e.what()); std::fclose(out); return 11;
  }
  return 0;
}
