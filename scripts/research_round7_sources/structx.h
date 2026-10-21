// structx.h -- decoder-causal structural experts for the PHDA9 metadata tail.
//
// The coded stream is left untouched (the transformer stays in-distribution). The
// experts parse the already-coded post-WRT bytes and, at selected positions, publish a
// full next-byte distribution that the cmix mixer receives as one extra input:
//
//  * TS  : revision timestamp  "\xdf\xcdN" '0' DAY 'J' SEC '\n'  predicted from the
//          record's revision id (coded on the line before) by interpolating the
//          (revision id -> time) pairs of all earlier records; exact digit
//          probabilities from a 3-component Laplace mixture over seconds.
//  * UID : contributor id line "\xdf\x86N" DIGITS after a "\xdf\x87N" NAME line:
//          the id last seen with the same name (definition once, then copy).
//  * IW  : interlanguage link "[" LANG 'J' TITLE "]": TITLE predicted as a copy of
//          the WRT title of the article owning the current block (the k-th article
//          whose body lost its "L/\xdf\xa7N" (</text>); blocks end with that pattern).
//
// Everything is integer/double arithmetic on decoded data only; the same code runs
// identically in compressor and decompressor.
#ifndef STRUCTX_H
#define STRUCTX_H

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

namespace structx {

class Expert {
 public:
  // vocab: 256 flags of bytes present in the stream (probabilities only on these)
  explicit Expert(const std::vector<bool>& vocab) : vocab_(vocab) {
    for (int i = 0; i < 256; ++i) dist_[i] = 0;
    sep_ = std::string("\x0a\x0a", 0);  // set by SetSeparator
  }
  // article separator ("  <page>\n    <title>" after WRT) and the "</title>" pattern
  void SetPatterns(const std::string& separator, const std::string& title_end) {
    sep_ = separator;
    title_end_ = title_end;
  }
  // Lab: externally supplied owner titles (as the stream parser would have produced
  // them) and the index of the first interlanguage block inside the coded slice.
  void SetOwners(const std::vector<std::string>& owners, size_t first_block) {
    owners_ = owners;
    block_ = first_block;
    owners_external_ = true;
    in_tail_ = true;
    rec_state_ = 0;
  }

  // ---- test hooks ----
  double ProbByte(unsigned char c) const {
    double s = 0;
    for (int i = 0; i < 256; ++i) s += dist_[i];
    return s > 0 ? dist_[c] / s : 0;
  }
  double DistSum() const { double s = 0; for (int i = 0; i < 256; ++i) s += dist_[i]; return s; }
  const std::vector<std::string>& Owners() const { return owners_; }
  size_t Block() const { return block_; }

  // ---- interface used by the predictor ----
  bool Active() const { return active_; }
  int Kind() const { return kind_; }          // 0 none, 1 TS, 2 UID, 3 IW, 4 USER
  int ConfBucket() const { return conf_bucket_; }
  // probability that the next bit is 1 given the bits of the current byte so far
  // (partial = 1 followed by the coded bits, as cmix's bit_context_)
  float PredictBit(unsigned int partial) const {
    if (!active_) return 0.5f;
    int nbits = 0;
    unsigned int p = partial;
    while (p > 1) { p >>= 1; ++nbits; }
    const unsigned int prefix = partial - (1u << nbits);
    const int shift = 8 - nbits;  // remaining bits incl. the next one
    const unsigned int lo = prefix << shift, hi = lo + (1u << shift);
    const unsigned int mid = lo + (1u << (shift - 1));
    double n1 = 0, n = 0;
    for (unsigned int c = lo; c < hi; ++c) { n += dist_[c]; if (c >= mid) n1 += dist_[c]; }
    if (!(n > 0)) return 0.5f;
    double q = n1 / n;
    if (q < 1e-4) q = 1e-4;
    if (q > 1 - 1e-4) q = 1 - 1e-4;
    return (float)q;
  }

  // called once per completed byte, before the next byte is predicted
  void ByteUpdate(unsigned char c) {
    // feedback for the adaptive confidences of copy experts
    if (active_ && (kind_ == 2 || kind_ == 3 || kind_ == 4)) {
      const bool hit = (c == expected_);
      unsigned int& h = hits_[kind_][conf_ctx_];
      unsigned int& t = tries_[kind_][conf_ctx_];
      h += hit; t += 1;
      if (t > 1023) { h >>= 1; t >>= 1; }
      if (!hit) copy_ok_ = false;
    }
    TrackArticles(c);
    if (c == '\n') {
      EndLine();
      line_.clear();
    } else {
      line_.push_back((char)c);
      // a tail line starting with '[' ends the revision records (interlanguage region)
      if (in_tail_ && line_.size() == 1 && c == '[') rec_state_ = 0;
    }
    Plan();
  }

 private:
  // ---------------- article tracking (owners of interlanguage blocks) ----------------
  void TrackArticles(unsigned char c) {
    recent_.push_back((char)c);
    if (recent_.size() > 64) recent_.erase(0, recent_.size() - 64);
    if (!sep_.empty() && recent_.size() >= sep_.size() &&
        recent_.compare(recent_.size() - sep_.size(), sep_.size(), sep_) == 0) {
      FinishArticle();
      in_article_ = true; in_title_ = true; title_.clear(); has_text_end_ = false;
      return;
    }
    if (!in_article_) return;
    if (in_title_) {
      title_.push_back((char)c);
      if (title_.size() >= title_end_.size() &&
          title_.compare(title_.size() - title_end_.size(), title_end_.size(), title_end_) == 0) {
        title_.resize(title_.size() - title_end_.size());
        in_title_ = false;
      } else if (title_.size() > 4096) {
        in_title_ = false;
      }
    }
    static const char kTextEnd[] = "L/\xdf\xa7N";
    if (recent_.size() >= 5 && recent_.compare(recent_.size() - 5, 5, kTextEnd, 5) == 0)
      has_text_end_ = true;
  }
  void FinishArticle() {
    if (in_article_ && !owners_external_ && !has_text_end_) owners_.push_back(title_);
    in_article_ = false;
  }

  // ---------------- line classification ----------------
  static bool IsDigits(const std::string& s, size_t from) {
    if (from >= s.size()) return false;
    for (size_t i = from; i < s.size(); ++i) if (s[i] < '0' || s[i] > '9') return false;
    return true;
  }
  void EndLine() {
    const std::string& L = line_;
    static const std::string kRev("\xdf\x99N"), kId("\xdf\x86N"), kTs("\xdf\xcdN"),
        kUser("\xdf\x87N");
    if (L == kRev) {
      if (!in_tail_) { in_tail_ = true; FinishArticle(); }
      rec_state_ = 1;  // expect revision id
      return;
    }
    if (rec_state_ == 1 && L.compare(0, 3, kId) == 0 && IsDigits(L, 3)) {
      cur_rev_ = strtoll(L.c_str() + 3, nullptr, 10);
      rec_state_ = 2;  // expect timestamp
      return;
    }
    if (rec_state_ == 2 && L.compare(0, 3, kTs) == 0) {
      have_ts_ = false;
      long long t;
      if (ParseTs(L, &t)) {
        if (ts_predicted_) UpdateResidualModel(t - ts_center_);
        rev_time_.emplace_hint(rev_time_.lower_bound(cur_rev_), cur_rev_, t);
        cur_ts_ = t; have_ts_ = true;
      }
      ts_predicted_ = false;
      rec_state_ = 3;
      return;
    }
    if (rec_state_ == 3 && L.compare(0, 3, kUser) == 0) {
      cur_user_ = L.substr(3);
      if (have_ts_) time_user_.emplace(cur_ts_, cur_user_);
      rec_state_ = 4;  // expect uid
      return;
    }
    if (rec_state_ == 4 && L.compare(0, 3, kId) == 0 && IsDigits(L, 3)) {
      user_uid_[cur_user_] = L.substr(3);
      rec_state_ = 3;
      return;
    }
    if (in_tail_ && !L.empty() && L[0] == '[') rec_state_ = 0;
    // interlanguage block boundary
    static const char kTextEnd[] = "L/\xdf\xa7N";
    if (in_tail_ && rec_state_ == 0 && L.size() >= 5 &&
        L.compare(L.size() - 5, 5, kTextEnd, 5) == 0)
      ++block_;
  }

  static bool ParseTs(const std::string& L, long long* t) {
    // "\xdf\xcdN" '0' DAY 'J' SEC
    if (L.size() < 7 || L[3] != '0') return false;
    size_t j = L.find('J', 4);
    if (j == std::string::npos || j == 4) return false;
    long long d = 0, s = 0;
    for (size_t i = 4; i < j; ++i) { if (L[i] < '0' || L[i] > '9') return false; d = d * 10 + (L[i] - '0'); }
    if (j + 1 >= L.size()) return false;
    for (size_t i = j + 1; i < L.size(); ++i) { if (L[i] < '0' || L[i] > '9') return false; s = s * 10 + (L[i] - '0'); }
    *t = d * 86400 + s;
    return true;
  }

  // ---------------- planning the next byte's distribution ----------------
  void Plan() {
    active_ = false; kind_ = 0; conf_bucket_ = 0;
    const std::string& L = line_;
    if (rec_state_ == 2 && L.size() >= 3 && L.compare(0, 3, "\xdf\xcdN") == 0) {
      if (L.size() == 3 && !ts_predicted_) StartTs();
      if (ts_predicted_ && PlanTs()) { active_ = true; kind_ = 1; }
      return;
    }
    if (rec_state_ == 3 && have_ts_ && L.size() >= 3 && L.compare(0, 3, "\xdf\x87N") == 0) {
      // username: copy of the user of the nearest-in-time earlier record
      const size_t j = L.size() - 3;
      if (j == 0) {
        copy_ok_ = false;
        if (time_user_.empty()) return;
        auto it = time_user_.lower_bound(cur_ts_);
        long long best = -1;
        if (it != time_user_.end()) { best = it->first - cur_ts_; cand_user_ = it->second; }
        if (it != time_user_.begin()) {
          auto pv = std::prev(it);
          if (best < 0 || cur_ts_ - pv->first < best) { best = cur_ts_ - pv->first; cand_user_ = pv->second; }
        }
        int g = 0;
        while (g < 3 && (1LL << (4 * (g + 1))) <= best) ++g;  // <16 s, <256 s, <4096 s, more
        user_gap_bucket_ = g;
        copy_ok_ = true;
      }
      if (!copy_ok_ || j > cand_user_.size()) return;
      expected_ = j < cand_user_.size() ? (unsigned char)cand_user_[j] : (unsigned char)'\n';
      conf_ctx_ = user_gap_bucket_;
      PlanCopy(kUserKind);
      return;
    }
    if (rec_state_ == 4 && L.size() >= 3 && L.compare(0, 3, "\xdf\x86N") == 0) {
      auto it = user_uid_.find(cur_user_);
      if (it == user_uid_.end()) return;
      const std::string& u = it->second;
      const size_t j = L.size() - 3;
      if (j == 0) copy_ok_ = true;
      if (!copy_ok_ || j > u.size()) return;
      expected_ = j < u.size() ? (unsigned char)u[j] : (unsigned char)'\n';
      conf_ctx_ = j < 3 ? (int)j : 3;
      PlanCopy(2);
      return;
    }
    if (in_tail_ && rec_state_ == 0 && !L.empty() && L[0] == '[' && block_ < owners_.size()) {
      const size_t colon = L.find('J', 1);
      if (colon == std::string::npos) return;
      const std::string& own = owners_[block_];
      if (own.empty()) return;
      const size_t j = L.size() - colon - 1;  // title bytes coded so far
      if (j == 0) copy_ok_ = true;
      if (!copy_ok_ || j > own.size()) return;
      expected_ = j < own.size() ? (unsigned char)own[j] : (unsigned char)']';
      conf_ctx_ = (j == 0 ? 0 : j < 4 ? 1 : j < own.size() ? 2 : 3);
      PlanCopy(3);
      return;
    }
  }

  void PlanCopy(int kind) {
    const unsigned int h = hits_[kind][conf_ctx_], t = tries_[kind][conf_ctx_];
    const double p = (h + 0.5) / (t + 1.0);
    for (int i = 0; i < 256; ++i) dist_[i] = 0;
    int nv = 0;
    for (int i = 0; i < 256; ++i) if (vocab_[i]) ++nv;
    const double rest = (1 - p) / (nv > 1 ? nv - 1 : 1);
    for (int i = 0; i < 256; ++i) if (vocab_[i]) dist_[i] = rest;
    dist_[expected_] = p;
    active_ = true; kind_ = kind;
    conf_bucket_ = p < 0.5 ? 0 : p < 0.9 ? 1 : p < 0.99 ? 2 : 3;
  }

  // ---------------- timestamp numeric expert ----------------
  void StartTs() {
    ts_predicted_ = false;
    if (rev_time_.size() < 2) return;
    auto hi = rev_time_.lower_bound(cur_rev_);
    auto lo = hi;
    if (hi == rev_time_.end()) { --hi; lo = hi; --lo; }
    else if (hi == rev_time_.begin()) { lo = hi; ++hi; }
    else { --lo; }
    const long long r0 = lo->first, r1 = hi->first, t0 = lo->second, t1 = hi->second;
    double c;
    if (r1 == r0) c = (double)t0;
    else c = t0 + (double)(t1 - t0) * (double)(cur_rev_ - r0) / (double)(r1 - r0);
    ts_center_ = (long long)std::floor(c + 0.5);
    // interpolation uncertainty grows with the time gap between the bracketing records
    const long long gap = t1 > t0 ? t1 - t0 : t0 - t1;
    int g = 0;
    while (g < 15 && (1LL << (g + 1)) <= gap + 1) ++g;
    gb_ = g;
    if (!gb_init_[g]) {
      gb_init_[g] = true;
      const double s = (double)(1LL << g);
      b_[g][0] = 1 + s / 16; b_[g][1] = 10 + s / 2; b_[g][2] = 1000 + 4 * s;
      w_[g][0] = 0.6; w_[g][1] = 0.3; w_[g][2] = 0.1;
    }
    ts_predicted_ = true;
  }
  void UpdateResidualModel(long long e) {
    // EM-style online update of a 3-component Laplace mixture over residual seconds
    const double ae = std::fabs((double)e);
    double r[3], z = 0;
    double* w = w_[gb_];
    double* b = b_[gb_];
    for (int k = 0; k < 3; ++k) { r[k] = w[k] * std::exp(-ae / b[k]) / (2 * b[k]); z += r[k]; }
    if (!(z > 0)) { r[0] = r[1] = 0; r[2] = 1; z = 1; }
    for (int k = 0; k < 3; ++k) {
      r[k] /= z;
      w[k] = 0.99 * w[k] + 0.01 * r[k];
      const double rate = 0.03 * r[k];
      b[k] = (1 - rate) * b[k] + rate * std::max(ae, 0.5);
      if (b[k] < 0.5) b[k] = 0.5;
    }
    if (b[1] < 4 * b[0]) b[1] = 4 * b[0];
    if (b[2] < 4 * b[1]) b[2] = 4 * b[1];
    const double sw = w[0] + w[1] + w[2];
    for (int k = 0; k < 3; ++k) w[k] = std::max(w[k] / sw, 1e-4);
  }
  // P(t in [a, b]) under the mixture (integers, inclusive)
  double Mass(long long a, long long b) const {
    if (b < a) return 0;
    double m = 0;
    for (int k = 0; k < 3; ++k) m += w_[gb_][k] * (Cdf(b + 0.5, k) - Cdf(a - 0.5, k));
    return m < 0 ? 0 : m;
  }
  double Cdf(double x, int k) const {
    const double z = (x - (double)ts_center_) / b_[gb_][k];
    return z < 0 ? 0.5 * std::exp(z) : 1 - 0.5 * std::exp(-z);
  }
  // mass of all times whose day string starts with digits D (decimal prefix of day >= 1)
  double DayPrefixMass(long long dpref, int dlen) const {
    double m = 0;
    long long lo = dpref, hi = dpref;  // days with this decimal prefix
    for (int ext = 0; ext <= 6 - dlen; ++ext) {
      m += Mass(lo * 86400, (hi + 1) * 86400 - 1);
      lo *= 10; hi = hi * 10 + 9;
    }
    return m;
  }
  double SecPrefixMass(long long day, long long spref, int slen) const {
    double m = 0;
    long long lo = spref, hi = spref;
    for (int ext = 0; ext <= 5 - slen && lo <= 86399; ++ext) {
      m += Mass(day * 86400 + lo, day * 86400 + std::min(hi, 86399LL));
      lo *= 10; hi = hi * 10 + 9;
    }
    return m;
  }
  bool PlanTs() {
    // line so far: "\xdf\xcdN" + rest
    const std::string rest = line_.substr(3);
    double P[256];
    for (int i = 0; i < 256; ++i) P[i] = 0;
    if (rest.empty()) {
      P['0'] = 1;
    } else {
      const size_t j = rest.find('J');
      if (j == std::string::npos) {
        // day digits after the leading '0'
        const std::string D = rest.substr(1);
        long long dv = 0;
        for (char ch : D) dv = dv * 10 + (ch - '0');
        const int dl = (int)D.size();
        for (int c = (dl == 0 ? 1 : 0); c <= 9; ++c) P['0' + c] = DayPrefixMass(dv * 10 + c, dl + 1);
        if (dl > 0) P['J'] = Mass(dv * 86400, dv * 86400 + 86399);
      } else {
        long long dv = 0;
        for (size_t i = 1; i < j; ++i) dv = dv * 10 + (rest[i] - '0');
        const std::string S = rest.substr(j + 1);
        long long sv = 0;
        for (char ch : S) sv = sv * 10 + (ch - '0');
        const int sl = (int)S.size();
        const bool zero = (sl == 1 && S[0] == '0');
        if (!zero) {
          for (int c = (sl == 0 ? 1 : 0); c <= 9; ++c) {
            const long long np = sv * 10 + c;
            if (np <= 86399) P['0' + c] = SecPrefixMass(dv, np, sl + 1);
          }
          if (sl == 0) P['0'] = Mass(dv * 86400, dv * 86400);  // second "0" exactly
        }
        if (sl > 0) P['\n'] = Mass(dv * 86400 + sv, dv * 86400 + sv);
      }
    }
    double tot = 0;
    int nvalid = 0;
    for (int i = 0; i < 256; ++i) { tot += P[i]; if (P[i] > 0) ++nvalid; }
    for (int i = 0; i < 256; ++i) dist_[i] = 0;
    if (!(tot > 0)) return false;
    // escape: uniform over the grammar-valid next bytes
    static const double kEsc = 2e-3;
    int ngram = 0;
    bool valid[256] = {false};
    {
      const size_t j = rest.find('J');
      if (rest.empty()) { valid['0'] = true; }
      else if (j == std::string::npos) {
        for (int c = (rest.size() == 1 ? 1 : 0); c <= 9; ++c) valid['0' + c] = true;
        if (rest.size() > 1) valid['J'] = true;
      } else {
        const std::string S = rest.substr(j + 1);
        if (!(S.size() == 1 && S[0] == '0')) for (int c = (S.empty() ? 0 : 0); c <= 9; ++c) valid['0' + c] = true;
        if (!S.empty()) valid['\n'] = true;
      }
      for (int i = 0; i < 256; ++i) ngram += valid[i];
    }
    double maxp = 0;
    for (int i = 0; i < 256; ++i) {
      if (!valid[i]) continue;
      dist_[i] = (1 - kEsc) * P[i] / tot + kEsc / ngram;
      if (dist_[i] > maxp) maxp = dist_[i];
    }
    conf_bucket_ = maxp < 0.5 ? 0 : maxp < 0.9 ? 1 : maxp < 0.99 ? 2 : 3;
    return true;
  }

  // state
  std::vector<bool> vocab_;
  double dist_[256];
  bool active_ = false;
  int kind_ = 0, conf_bucket_ = 0, conf_ctx_ = 0;
  unsigned char expected_ = 0;
  bool copy_ok_ = false;
  static const int kUserKind = 4;
  unsigned int hits_[5][4] = {{0}}, tries_[5][4] = {{0}};
  std::multimap<long long, std::string> time_user_;  // record time -> username (WRT bytes)
  std::string cand_user_;
  int user_gap_bucket_ = 0;
  long long cur_ts_ = 0;
  bool have_ts_ = false;
  std::string line_, recent_, sep_, title_end_, title_, cur_user_;
  bool in_article_ = false, in_title_ = false, has_text_end_ = false, in_tail_ = false;
  bool owners_external_ = false;
  std::vector<std::string> owners_;
  size_t block_ = 0;
  int rec_state_ = 0;
  long long cur_rev_ = 0, ts_center_ = 0;
  bool ts_predicted_ = false;
  std::multimap<long long, long long> rev_time_;
  std::unordered_map<std::string, std::string> user_uid_;
  int gb_ = 0;                       // gap bucket of the current prediction
  bool gb_init_[16] = {false};
  double w_[16][3], b_[16][3];       // per-bucket Laplace mixture (weights, scales in s)
};

}  // namespace structx

#endif  // STRUCTX_H
