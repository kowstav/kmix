# Optimized quantized-matmul kernel suite (qmat). clang++-17 is the
# production compiler (MACHINE.md: gcc spills in the inner loops).
CXX      ?= clang++-17
CXXFLAGS ?= -O3 -march=znver2 -std=c++17 -Wall -Wextra -fno-math-errno -mrecip=none
# -mrecip=none: never let the compiler substitute RCPPS/RSQRTPS estimates for
# a divide or a square root. Their results are only specified to a relative
# error bound and differ between Intel and AMD, which would make the
# compressor and the decompressor disagree on a CPU of the other vendor.
# NO -ffast-math (SPEC forbids it)

BIN := ../../bin/opt
SRCS := qmat_dense.cpp qmat_sparse.cpp
HDRS := qmat.h qmat_dense.h qmat_sparse.h qmat_avx512.h qmat_cpu.h
OBJS := $(BIN)/qmat_dense.o $(BIN)/qmat_sparse.o

all: $(BIN)/test_qmat $(BIN)/bench_qmat $(BIN)/bench_qw8

# AVX-512 VNNI twins (qmat.h TF_AVX512): `make CXXFLAGS='... -DTF_AVX512=1' ../../bin/opt/test_avx512` builds the
# AVX2-vs-AVX512 bitwise equality test (needs an AVX-512 VNNI host to run; exit 2 = SKIP). Only the *_avx512.o
# objects get the feature flags (F/BW/VL/VNNI; not -march=x86-64-v4, which lacks VNNI); the test also enables the
# shapes the production model never dispatches (QMAT_AVX512_ALL_SHAPES).
V512 := -mavx512f -mavx512bw -mavx512vl -mavx512vnni
AVX512_OBJS := $(BIN)/qmat_dense_avx512.o $(BIN)/qmat_sparse_avx512.o $(BIN)/qmat_cpu.o

$(BIN):
	mkdir -p $(BIN)

$(BIN)/%.o: %.cpp $(HDRS) | $(BIN)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BIN)/qmat_dense_avx512.o: qmat_dense_avx512.cpp $(HDRS) | $(BIN)
	$(CXX) $(CXXFLAGS) $(V512) -DQMAT_AVX512_ALL_SHAPES=1 -c $< -o $@
$(BIN)/qmat_sparse_avx512.o: qmat_sparse_avx512.cpp $(HDRS) | $(BIN)
	$(CXX) $(CXXFLAGS) $(V512) -DQMAT_AVX512_ALL_SHAPES=1 -c $< -o $@

$(BIN)/test_avx512: test_avx512.cpp $(OBJS) $(AVX512_OBJS) $(HDRS)
	$(CXX) $(CXXFLAGS) -DQMAT_AVX512_ALL_SHAPES=1 test_avx512.cpp $(OBJS) $(AVX512_OBJS) -o $@ -lm

$(BIN)/kernels.o: ../kernels.cpp ../kernels.h | $(BIN)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BIN)/test_qmat: test_qmat.cpp $(OBJS) $(BIN)/kernels.o $(HDRS)
	$(CXX) $(CXXFLAGS) test_qmat.cpp $(OBJS) $(BIN)/kernels.o -o $@ -lm

$(BIN)/bench_qmat: bench_qmat.cpp $(OBJS) $(BIN)/kernels.o $(HDRS) ../../bench/bench_common.h
	$(CXX) $(CXXFLAGS) bench_qmat.cpp $(OBJS) $(BIN)/kernels.o -o $@ -lm

$(BIN)/bench_qw8: bench_qw8.cpp $(OBJS) $(HDRS)
	$(CXX) $(CXXFLAGS) bench_qw8.cpp $(OBJS) -o $@ -lm

clean:
	rm -rf $(BIN)

.PHONY: all clean
