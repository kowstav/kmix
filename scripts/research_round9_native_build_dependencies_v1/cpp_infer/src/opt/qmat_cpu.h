// qmat_cpu.h -- runtime CPU feature check for the AVX-512 kernel dispatch (TF_AVX512, qmat.h).
// qmat_cpu.cpp is compiled with the BASELINE flags (x86-64-v3): it must never contain an AVX-512
// instruction itself, and it is the only code that decides which path a host runs.
#pragma once

namespace fx2 {
namespace opt {

// true iff the CPU and the OS support AVX-512 F + BW + VL + VNNI (cpuid leaf 7 + XCR0 opmask/ZMM state),
// i.e. exactly the feature set the qmat_*_avx512.cpp objects are compiled for (Tiger Lake, Ice Lake,
// Sapphire Rapids, Zen 4, ...). Cached after the first call. FX2_FORCE_AVX2=1 in the environment forces
// false (A/B testing of the two paths on one host). Always false in a -DTF_AVX512=0 build.
bool cpu_has_avx512_vnni();

}  // namespace opt
}  // namespace fx2
