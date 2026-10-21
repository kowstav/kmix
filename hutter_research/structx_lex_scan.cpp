// structx_lex_scan: standalone causal run of structx_lex::Expert over a transformed stream.
// Usage: structx_lex_scan <stream.wrt> <vocab.bm> <records.tsv> <summary.json> [owners_out_prefix region_start...]
// * Feeds every byte in order through ByteUpdate (exactly as the predictor does after a byte
//   is coded) and, before each byte, records whether an expert is active and the expert's
//   standalone probability of the actual byte ("direct field predictor" cost).
// * Emits one TSV row per recognized revision timestamp / username / contributor-id line and
//   interlanguage line, with the byte offset of the line start, so an independent parser can
//   check cursor alignment.
// * For each region start, writes the owner list and block index the causal parser holds at
//   that offset (lab input LAB_IW_OWNERS / LAB_IW_BLOCK0 for regional native runs).
#ifndef HP_R14_STRUCTX
#define HP_R14_STRUCTX 2
#endif
#include "structx_lex.h"
#include <cstdio>
#include <cmath>
#include <string>
#include <vector>

int main(int argc, char** argv) {
  if (argc < 5) { std::fprintf(stderr, "usage\n"); return 2; }
  FILE* in = std::fopen(argv[1], "rb"); FILE* vb = std::fopen(argv[2], "rb");
  FILE* rec = std::fopen(argv[3], "wb"); FILE* sum = std::fopen(argv[4], "wb");
  if (!in || !vb || !rec || !sum) return 3;
  unsigned char vbits[32];
  if (std::fread(vbits, 1, 32, vb) != 32) return 4;
  std::vector<bool> vocab(256);
  for (int i = 0; i < 256; ++i) vocab[i] = (vbits[i / 8] >> (i % 8)) & 1;
  std::vector<unsigned long long> starts;
  const char* prefix = argc > 5 ? argv[5] : nullptr;
  for (int i = 6; i < argc; ++i) starts.push_back(std::strtoull(argv[i], nullptr, 10));
  structx_lex::Expert ex(vocab);
  unsigned long long pos = 0, active[5] = {0}, line_start = 0;
  double bits[5] = {0};
  size_t next_start = 0;
  std::string line;
  int c;
  std::vector<unsigned char> buf(1 << 22);
  size_t n;
  while ((n = std::fread(buf.data(), 1, buf.size(), in)) > 0) {
    for (size_t i = 0; i < n; ++i, ++pos) {
      while (next_start < starts.size() && starts[next_start] == pos) {
        std::string path = std::string(prefix) + "_" + std::to_string(pos) + ".owners";
        FILE* o = std::fopen(path.c_str(), "wb");
        if (!o) return 5;
        for (const auto& t : ex.Owners()) { uint32_t m = (uint32_t)t.size(); std::fwrite(&m, 4, 1, o); std::fwrite(t.data(), 1, m, o); }
        std::fclose(o);
        std::fprintf(sum, "{\"region_start\": %llu, \"owners\": %zu, \"block\": %zu}\n", pos, ex.Owners().size(), ex.Block());
        ++next_start;
      }
      c = buf[i];
      if (ex.Active()) {
        double p = ex.ProbByte((unsigned char)c);
        if (p < 1e-12) p = 1e-12;
        active[ex.Kind()] += 1; bits[ex.Kind()] += -std::log2(p);
      }
      const int st = ex.RecState();
      if (c == '\n') {
        // classify the completed line before the expert consumes '\n'
        if (line.size() >= 3) {
          const bool ts = line.compare(0, 3, "\xdf\xcdN") == 0, us = line.compare(0, 3, "\xdf\x87N") == 0,
                     id = line.compare(0, 3, "\xdf\x86N") == 0, iw = line[0] == '[' && ex.InTail();
          if ((ts && st == 2) || (us && st == 3) || (id && (st == 1 || st == 4)) || iw) {
            std::fprintf(rec, "%llu\t%c\t%d\t%d\t", line_start, ts ? 'T' : us ? 'U' : id ? 'I' : 'W', st, ex.LineValid() ? 1 : 0);
            for (unsigned char ch : line) std::fprintf(rec, "%02x", ch);
            std::fputc('\n', rec);
          }
        }
        line.clear(); line_start = pos + 1;
      } else {
        line.push_back((char)c);
      }
      ex.ByteUpdate((unsigned char)c);
    }
  }
  std::fprintf(sum, "{\"bytes\": %llu, \"grammar_violations\": %llu, \"owners\": %zu, \"blocks\": %zu", pos,
               ex.GrammarViolations(), ex.Owners().size(), ex.Block());
  for (int k = 1; k <= 4; ++k) std::fprintf(sum, ", \"active_%d\": %llu, \"direct_bits_%d\": %.6f", k, active[k], k, bits[k]);
  std::fprintf(sum, "}\n");
  std::fclose(in); std::fclose(rec); std::fclose(sum);
  return 0;
}
