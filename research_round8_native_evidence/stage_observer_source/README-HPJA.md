# lexth11c -- Hutter Prize entry source package (HPJA form)

This tarball is the `SOURCE_PACKAGE` of a self-extracting-form entry for the automated
judging harness (https://github.com/jabowery/HutterPrizeJudgingAssistant). It is the
cmix-lex / fx2-cmix-transformer lineage compressor of `README.md` + `changes.md`, packaged
with the lexth11c transformer weights and the three harness files:

- `install.sh` -- root + network phase: clang-17/lld-17/llvm-17 from apt.llvm.org (jammy for
  QUALIFICATION_OS=ubuntu-22.04; noble also supported) + libstdc++-12-dev, make, binutils, python3,
  UPX 5.1.1 (sha256-verified GitHub release). Installs only.
- `build.sh`   -- offline, UID 65532, source read-only at `/entry`, cwd `/work`: copies the
  tree to `/work/src`, runs `./build_and_construct_comp.sh` with the lexth11c knobs
  (PGO + LTO, UPX 5.1.1 `--ultra-brute`, self-extract assembly) and writes `/work/cmix`.
- `comp9.args` -- argument vector of the compressor (`-e`, `enwik9`, `o`): `./cmix -e enwik9 o`
  compresses `enwik9`, writing the intermediate cmix stream to `o` and the self-extracting
  archive to `archive9`. Running `./archive9` with no arguments writes `enwik9_uncompressed`.

The compressor must be invoked under the file name `cmix` and the archive under `archive9`
(each program opens itself by that name to read the payload appended to its UPX-packed
stub; `src/readalike_prepr/self_extract.h`), hence `COMPRESSOR=cmix`, `ARCHIVE=archive9`,
`DECOMPRESSED_OUTPUT=enwik9_uncompressed` in `entry.env`. Both artifacts are
`upx-overlay`: a UPX 5.1.1 LZMA-packed ELF stub (198,236 bytes) followed by the compressed
dictionary, the compressed article order, the FX2TFWC2 transformer weights and a 16-byte
header (`cmix -h`). Single thread, no GPU, peak RSS < 10 GiB.

`models/lex_h1_run11.tfwc2` (2,978,039 bytes) are the transformer weights (run 11:
12 layers, MLP 768, window 1024, codebook int4 + 8-bit small tables, dynamic activation
scales); `prof_input/` holds the two PGO training inputs. Knobs of record are exported at the
top of `build.sh`. Build of record: `comp9` 3,477,137 bytes, sha256
e77c9a659b31c1358368da0ef49a8683080197b9b14a11b1e6e80a43c94cb463 (Debian bookworm, clang-17 from
apt.llvm.org, UPX 5.1.1). A rebuild on ubuntu-22.04 with this install.sh/build.sh reproduces every
component byte-for-byte except the packed stub (same 198,236-byte size, different bytes: glibc 2.35 vs
2.36 crt objects / libstdc++ 12.3 vs 12.2 headers) and yields a compressor whose output stream is
bit-identical to the record's on a 3 MB enwik8 test.
