// microbenchmark: QW8 (8-bit small matmuls) vs the int4 kernels they replace (prior sparse4 / unembedding dense G8)
#include <chrono>
#include <cstdio>
#include <cstring>
#include <vector>
#include <random>
#include "qmat.h"
#include "qmat_dense.h"
#include "qmat_sparse.h"
using namespace fx2::opt;
struct Buf { std::vector<uint8_t> v; uint8_t* p; explicit Buf(size_t n) : v(n + 128 + QMAT_TAIL_SLACK, 0) { p = reinterpret_cast<uint8_t*>((reinterpret_cast<uintptr_t>(v.data()) + 63) & ~uintptr_t(63)); } };
template <class F> double ns_per_call(F f, int iters) {
  f(); auto t0 = std::chrono::steady_clock::now();
  for (int i = 0; i < iters; i++) f();
  return std::chrono::duration<double, std::nano>(std::chrono::steady_clock::now() - t0).count() / iters;
}
int main() {
  std::mt19937 rng(1);
  auto rw = [&](int lo, int hi) { return static_cast<int8_t>(std::uniform_int_distribution<int>(lo, hi)(rng)); };
  // --- prior: 192 x 205, raw u8 acts with ~50 nonzeros ---
  const int D = 192, V = 205, VP = 224;
  std::vector<int8_t> qw8(D * V), qw4(D * V); std::vector<float> fold(D, 0.01f);
  for (auto& x : qw8) x = rw(-127, 127);
  for (auto& x : qw4) x = rw(-7, 7);
  alignas(64) static uint8_t act[224] = {}; alignas(64) static uint16_t idx[240] = {};
  int nnz = 0; for (int i = 0; i < V; i++) if (i % 4 == 0) { act[i] = static_cast<uint8_t>(1 + (i * 37) % 120); idx[nnz++] = static_cast<uint16_t>(i); }
  for (int k = nnz; k < nnz + 8; k++) idx[k] = idx[nnz - 1];
  Buf wb(qw8_bytes(D, V)); alignas(64) static int32_t corr[256]; alignas(64) static float fld[256];
  QW8 m8 = qw8_build(reinterpret_cast<int8_t*>(wb.p), corr, fld, qw8.data(), fold.data(), D, V, false);
  Buf cb(qsparse4_bytes(V)); alignas(64) static float fold4[192];
  QSparse4 m4 = qsparse4_build(cb.p, fold4, qw4.data(), fold.data(), D, V);
  alignas(64) static float out[256];
  printf("prior 192x205 nnz=%d: qw8 dense %.0f ns | sparse4 int4 %.0f ns\n", nnz,
         ns_per_call([&] { qw8_f32(m8, act, out); }, 200000), ns_per_call([&] { qsparse4_f32(m4, act, idx, nnz, out); }, 200000));
  // --- unembedding: 205 x 192, biased u8 acts ---
  std::vector<int8_t> uw8(V * D), uw4(V * D); std::vector<float> ufold(V, 0.01f);
  for (auto& x : uw8) x = rw(-127, 127);
  for (auto& x : uw4) x = rw(-7, 7);
  alignas(64) static uint8_t uact[192]; for (int i = 0; i < D; i++) uact[i] = static_cast<uint8_t>(60 + (i * 53) % 130);
  Buf ub(qw8_bytes(V, D)); alignas(64) static int32_t ucorr[256]; alignas(64) static float ufld[256];
  QW8 u8 = qw8_build(reinterpret_cast<int8_t*>(ub.p), ucorr, ufld, uw8.data(), ufold.data(), V, D, true);
  Buf db(qdense_bytes(V, D)); QDense u4 = qdense_build(db.p, uw4.data(), ufold.data(), V, D, true);
  printf("unembed 205x192: qw8 %.0f ns | dense G8 int4 %.0f ns\n",
         ns_per_call([&] { qw8_f32(u8, uact, out); }, 200000), ns_per_call([&] { qgemv_f32(u4, uact, out); }, 200000));
  return 0;
}
