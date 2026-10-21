# lexth11c — enwik9 self-extracting archive (Hutter Prize format) — artifact package

Status (2026-09-27 00:35 ET): **VERIFIED — clean-room Intel decode CMP_OK (59:26:45 wall, peak RSS 9,597,984 kB, exit 0); AMD partial leg byte-identical over 292.7 MB.** Earlier status: compress phase complete; decode verification in progress (Intel clean-room leg started 12:57 ET,
expected ~80–90 h on Modal's 2-vCPU sandbox; AMD cross-vendor leg queued, waiting for an AMD host). Do not submit until the
decode leg reports CMP_OK and the AMD leg has run — see `lexth11c_enwik9.json` for the live numbers.

| artifact | bytes | sha256 |
|---|---|---|
| `archive9` (self-extracting, `./archive9` writes `enwik9_uncompressed`) | 95,836,613 | a5b9c2e3fe000a0299606da20c4915d992ff09d8fd819f8ac6a640aa0eb0d956 |
| `comp9` (compressor, `./comp9 -e enwik9 out.cmix` also writes `archive9`) | 3,477,137 | e77c9a659b31c1358368da0ef49a8683080197b9b14a11b1e6e80a43c94cb463 |
| **S = archive9 + comp9** | **99,313,750** | |

Layout of `archive9`: decompressor stub (198,236 B, UPX --best --lzma) + compressed dictionary (100,866) + transformer weights
(FX2TFWC3, 2,978,039) + coded payload (92,559,456) + 16-byte header. Layout of `comp9`: stub + dictionary + article order (199,980) +
weights + header.

## Measurements (compress, Modal V2 sandbox, 2 vCPU GenuineIntel model unknown, 12 GiB)
- command: `/usr/bin/time -v -o time.txt ./cmix -e /work/enwik9 out.cmix` (single thread)
- wall 55:24:11 (199,451 s), user 196,733 s, peak RSS 9,765,024 kB (9.31 GiB; Hutter limit 10 GiB), exit 0
- enwik9 sha256 159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc

## Where it stands (LTCB page as of 2026-09-24)
- LTCB enwik9 (archive size): zmix 1.0 96,096,261 (Sep 14) > rata-cmix 96,849,689 > fx2-cmix-transformer 96,996,198. **lexth11c 95,836,613 is
  259,648 B (0.27 %) smaller than zmix** — first place (decode verified 2026-09-27).
- Hutter S: zmix 1.0 (pending, under committee test) 99,312,424; fx2-cmix-transformer (pending) 100,420,830; record fx2-cmix 110,793,128.
  lexth11c is 1,326 B behind zmix; the successor lexth12cb (W=2048 transformer, run12 weights) is projected at ≈98.9–99.0 M.

## What it is
cmix-lex (Kaido Orav; github.com/blahem/cmix-lex) model bank + the fx2-cmix-transformer 6M-parameter transformer (Vladimir Ivanov) retrained
by us on the cmix-lex PPMD stream (lex_h1_run11: 12 layers, d_mlp 768, sliding window 1024, learned 15-level codebook weights on a 0.25 grid,
8-bit small tables, dynamic int8 matmul activations, FX2TFWC3 weight container), with our changes: PPMD heap 3500 MB plain RAM with cut-off,
fxcm maps /2, 12 layer-0 mixers (mask 0x42e72d), L0 LR x0.6 / L1 LR x0.25, PGO+LTO clang-17, x86-64-v3 baseline with runtime-dispatched AVX-512
VNNI kernels confined to two objects, -mrecip=none (vendor-independent), SEED 923 / UPDATE_LIMIT 3000. Build recipe: `lex_build_lexth11c.json`.
Source tree: repo `work/sota/lext_big/` (build driver `work/sota/modal_big.py --variant lexth11c`).

## Files
- `compress_time.txt`, `compress_cmix.log`, `compress_progress.log` — raw logs of the compress run
- `lex_build_lexth11c.json` (build), `lex_smoke3mb_lexth11c.json` (3 MB round-trip smoke, byte-exact), `speed_seq_lexth11c_budget.json`
  (same-sandbox speed A/B vs lexth1c_o2: −5.9 % time)
- `lexth11c_enwik9.json` — compress + decode report (decode_intel_cleanroom, decode_amd_partial); raw decode evidence in `decode_intel/`
