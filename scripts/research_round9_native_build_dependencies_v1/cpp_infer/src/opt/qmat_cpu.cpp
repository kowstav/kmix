#include "qmat_cpu.h"

#include <cpuid.h>

#include <cstdlib>

#include "qmat.h"

namespace fx2 {
namespace opt {

namespace {
bool detect() {
#if !TF_AVX512
  return false;  // the AVX-512 objects are not part of this build
#else
  const char* force = std::getenv("FX2_FORCE_AVX2");
  if (force && force[0] == '1') return false;
  unsigned a, b, c, d;
  if (!__get_cpuid(1, &a, &b, &c, &d)) return false;
  const bool osxsave = (c >> 27) & 1;
  if (!osxsave) return false;
  // XCR0: bits 1,2 (SSE/AVX state) and 5,6,7 (opmask, ZMM_Hi256, Hi16_ZMM) must be enabled by the OS
  unsigned xlo, xhi;
  __asm__ volatile("xgetbv" : "=a"(xlo), "=d"(xhi) : "c"(0));
  if ((xlo & 0xe6u) != 0xe6u) return false;
  if (__get_cpuid_max(0, nullptr) < 7) return false;
  __cpuid_count(7, 0, a, b, c, d);
  const bool f = (b >> 16) & 1, bw = (b >> 30) & 1, vl = (b >> 31) & 1, vnni = (c >> 11) & 1;
  return f && bw && vl && vnni;
#endif
}
}  // namespace

bool cpu_has_avx512_vnni() {
  static const bool v = detect();
  return v;
}

}  // namespace opt
}  // namespace fx2
