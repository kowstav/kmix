#!/usr/bin/env python3
"""Bounded no-retraining survey of exact weight-container packing.

Examples:
  python research_round7_weight_pack.py /root/hp/gen/.tfweights --out pack.json
  python research_round7_weight_pack.py weights.bin --save-best pack.best.r7w
  python research_round7_weight_pack.py --unpack pack.best.r7w --restore restored
  python research_round7_weight_pack.py --self-test

All candidates invert to exactly the input bytes. FX2TFWC2 semantic candidates
also require an exact original-container decode/reencode certificate. No floats
are rounded, requantized, trained, or recomputed: omitted RoPE recipes are kept.
Only the public FX2TFWC2 encodings 0..5 and raw FX2TFW01 are understood. Unknown
variants are surveyed as opaque bytes. Stdlib only; installed zstandard is optional.

Format sources, inspected 2026-10-04:
https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/pysrc/weights_compress.py
https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/pysrc/export_weights.py
https://raw.githubusercontent.com/astOwOlfo/fx2-cmix-transformer-v1/main/cpp_infer/src/weights_io_compressed.cpp

Wrapper R7WPK001 is a research format. Its complete header/parameter bytes and
codec framing are charged. C++ decoder/code-library cost is NOT measured here.
Any two-copy saving is a gross weight-blob saving, not a Hutter package result.
"""
from __future__ import annotations

import argparse
import base64
import collections
import hashlib
import json
import lzma
import math
import multiprocessing as mp
import os
import pathlib
import struct
import sys
import time
import zlib

MASK32 = (1 << 32) - 1
MAGIC = b"R7WPK001"
CANON = b"R7CAN001"
HEADER = struct.Struct("<8sBBHQQI")
WIDTHS = {0: 1, 1: 2, 2: 4, 3: 4}
CODECS = {0: "raw", 1: "zlib9", 2: "lzma6", 3: "lzma_delta4", 4: "zstd9"}
DEADLINE = float("inf")


def check_time():
    if time.monotonic() >= DEADLINE:
        raise TimeoutError("survey time budget exhausted")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(data, pos, count):
    if count < 0 or pos < 0 or pos + count > len(data):
        raise ValueError("truncated or invalid tensor stream")


def u32(data, pos):
    need(data, pos, 4)
    return struct.unpack_from("<I", data, pos)[0], pos + 4


def numel(shape):
    n = math.prod(shape)
    if n > 128 * 1024 * 1024:
        raise ValueError("tensor element count exceeds survey bound")
    return n


class Models:
    def __init__(self):
        self.meta = {}
        self.prev = 0
        self.name = {}
        self.raw = [1024] * 256
        self.i4 = [1024] * 16
        self.hi = [1024] * 256
        self.lo = {}
        self.plane = [[1024] * 256 for _ in range(4)]

    def mt(self):
        return self.meta.setdefault(self.prev, [1024] * 256)

    def nt(self, c2, c1):
        return self.name.setdefault((c2, c1), [1024] * 256)

    def lt(self, hi):
        return self.lo.setdefault(hi, [1024] * 256)


class RangeDecoder:
    def __init__(self, data):
        if len(data) < 5:
            raise ValueError("range stream too short")
        self.data, self.pos = data, 1
        self.range, self.code = MASK32, int.from_bytes(data[1:5], "big")
        self.pos = 5

    def bit(self, probs, idx):
        p = probs[idx]
        bound = (self.range >> 11) * p
        if self.code < bound:
            self.range = bound
            probs[idx] = p + ((2048 - p) >> 5)
            bit = 0
        else:
            self.code -= bound
            self.range -= bound
            probs[idx] = p - (p >> 5)
            bit = 1
        while self.range < (1 << 24):
            b = self.data[self.pos] if self.pos < len(self.data) else 0
            self.pos += 1
            self.code = ((self.code << 8) | b) & MASK32
            self.range <<= 8
        return bit

    def tree(self, probs, nbits):
        node = 1
        for _ in range(nbits):
            node = (node << 1) | self.bit(probs, node)
        return node - (1 << nbits)


class RangeEncoder:
    def __init__(self):
        self.low, self.range = 0, MASK32
        self.cache, self.cache_size = 0, 1
        self.out = bytearray()

    def shift(self):
        if self.low < 0xFF000000 or self.low > MASK32:
            carry = self.low >> 32
            self.out.append((self.cache + carry) & 255)
            self.out.extend(bytes([(255 + carry) & 255]) * (self.cache_size - 1))
            self.cache = (self.low >> 24) & 255
            self.cache_size = 0
        self.cache_size += 1
        self.low = (self.low << 8) & MASK32

    def bit(self, probs, idx, bit):
        p = probs[idx]
        bound = (self.range >> 11) * p
        if bit == 0:
            self.range = bound
            probs[idx] = p + ((2048 - p) >> 5)
        else:
            self.low += bound
            self.range -= bound
            probs[idx] = p - (p >> 5)
        while self.range < (1 << 24):
            self.range <<= 8
            self.shift()

    def tree(self, probs, nbits, symbol):
        node = 1
        for k in range(nbits - 1, -1, -1):
            bit = (symbol >> k) & 1
            self.bit(probs, node, bit)
            node = (node << 1) | bit

    def finish(self):
        for _ in range(5):
            self.shift()
        return bytes(self.out)


def record_header(name, dtype, shape, enc=None):
    result = struct.pack("<I", len(name)) + name + bytes([dtype])
    result += struct.pack("<I", len(shape))
    result += b"".join(struct.pack("<I", x) for x in shape)
    if enc is not None:
        result += bytes([enc])
    return result


def parse_records(data, packed_payload_mode=None):
    """Parse raw/canonical records, optionally with known length-changing int4 pack."""
    if data[:8] not in (b"FX2TFW01", CANON):
        raise ValueError("not a supported explicit tensor stream")
    canonical = data[:8] == CANON
    count, pos = u32(data, 8)
    if count > 4096:
        raise ValueError("absurd tensor count")
    records = []
    names = set()
    for _ in range(count):
        check_time()
        start = pos
        n, pos = u32(data, pos)
        if n > 4096:
            raise ValueError("absurd tensor name")
        need(data, pos, n + 1)
        name = data[pos:pos + n]
        pos += n
        dtype, pos = data[pos], pos + 1
        if dtype not in WIDTHS or name in names:
            raise ValueError("invalid dtype or duplicate tensor")
        names.add(name)
        ndim, pos = u32(data, pos)
        if ndim > 8:
            raise ValueError("absurd ndim")
        shape = []
        for _ in range(ndim):
            v, pos = u32(data, pos)
            shape.append(v)
        nval = numel(shape)
        enc = None
        if canonical:
            need(data, pos, 1)
            enc, pos = data[pos], pos + 1
            if enc not in range(6):
                raise ValueError("unsupported encoding")
        omitted = canonical and enc in (4, 5)
        length = 0 if omitted else nval * WIDTHS[dtype]
        use_nibble = (dtype == 0 and not omitted and
                      (not canonical or enc == 1))
        if packed_payload_mode and use_nibble:
            length = 0 if packed_payload_mode == "omit" else (nval + 1) // 2
        need(data, pos, length)
        records.append({"name": name, "dtype": dtype, "shape": shape,
                        "enc": enc, "header": data[start:pos],
                        "data": data[pos:pos + length], "nval": nval,
                        "i4": use_nibble})
        pos += length
    if pos != len(data):
        raise ValueError("trailing bytes in explicit tensor stream")
    return records


def decode_v2(data):
    if data[:8] != b"FX2TFWC2":
        raise ValueError("not public FX2TFWC2")
    count, _ = u32(data, 8)
    if count > 4096:
        raise ValueError("absurd tensor count")
    rd, m = RangeDecoder(data[12:]), Models()
    out = bytearray(CANON + struct.pack("<I", count))

    def meta():
        b = rd.tree(m.mt(), 8)
        m.prev = b
        return b

    for _ in range(count):
        check_time()
        n = meta()
        name, c2, c1 = bytearray(), 0, 0
        for _ in range(n):
            ch = rd.tree(m.nt(c2, c1), 8)
            name.append(ch)
            c2, c1 = c1, ch
        dtype, ndim = meta(), meta()
        if dtype not in WIDTHS or ndim > 8:
            raise ValueError("not a supported public v2 variant")
        shape = [sum(meta() << (8*k) for k in range(4)) for _ in range(ndim)]
        enc, nval = meta(), numel(shape)
        if enc not in range(6):
            raise ValueError("unsupported v2 encoding ID %s" % enc)
        out.extend(record_header(bytes(name), dtype, shape, enc))
        if enc in (4, 5):
            if dtype != 2 or ndim != 2:
                raise ValueError("invalid omitted RoPE recipe")
            continue
        if enc == 1 and dtype != 0 or enc == 2 and dtype != 1:
            raise ValueError("encoding/dtype mismatch")
        if enc == 3 and WIDTHS[dtype] != 4:
            raise ValueError("invalid plane encoding")
        payload = bytearray()
        for k in range(nval * WIDTHS[dtype] if enc != 1 else nval):
            if (k & 65535) == 0:
                check_time()
            if enc == 1:
                q = rd.tree(m.i4, 4)
                if q > 14:
                    raise ValueError("invalid int4 symbol")
                payload.append((q - 7) & 255)
            elif enc == 2:
                # Decode one bf16 element in each pair of iterations.
                if k & 1:
                    continue
                hi = rd.tree(m.hi, 8)
                lo = rd.tree(m.lt(hi), 8)
                payload.extend((lo, hi))
            elif enc == 3:
                payload.append(rd.tree(m.plane[k & 3], 8))
            else:
                payload.append(rd.tree(m.raw, 8))
        out.extend(payload)
        if len(out) > 128 * 1024 * 1024:
            raise ValueError("canonical stream exceeds size bound")
    parse_records(bytes(out))
    return bytes(out)


def encode_v2(canonical):
    records = parse_records(canonical)
    enc, m = RangeEncoder(), Models()

    def meta(b):
        enc.tree(m.mt(), 8, b)
        m.prev = b

    for r in records:
        check_time()
        name, dtype, shape, kind, payload = (
            r["name"], r["dtype"], r["shape"], r["enc"], r["data"])
        if len(name) > 255:
            raise ValueError("v2 name too long")
        meta(len(name))
        c2 = c1 = 0
        for ch in name:
            enc.tree(m.nt(c2, c1), 8, ch)
            c2, c1 = c1, ch
        meta(dtype)
        meta(len(shape))
        for dim in shape:
            for k in range(4):
                meta((dim >> (8*k)) & 255)
        meta(kind)
        for k, b in enumerate(payload):
            if (k & 65535) == 0:
                check_time()
            if kind == 1:
                q = (b if b < 128 else b - 256) + 7
                if not 0 <= q <= 14:
                    raise ValueError("invalid int4 symbol")
                enc.tree(m.i4, 4, q)
            elif kind == 2:
                if k & 1:
                    continue
                lo, hi = b, payload[k + 1]
                enc.tree(m.hi, 8, hi)
                enc.tree(m.lt(hi), 8, lo)
            elif kind == 3:
                enc.tree(m.plane[k & 3], 8, b)
            elif kind == 0:
                enc.tree(m.raw, 8, b)
            else:
                raise ValueError("omitted encoding has unexpected data")
    return b"FX2TFWC2" + struct.pack("<I", len(records)) + enc.finish()


def planes(data, width, inverse=False):
    if width < 1 or width > 256:
        raise ValueError("invalid plane width")
    n = len(data)
    if not inverse:
        return b"".join(data[i::width] for i in range(width))
    out, pos = bytearray(n), 0
    for i in range(width):
        count = (n - i + width - 1) // width if i < n else 0
        out[i::width] = data[pos:pos + count]
        pos += count
    return bytes(out)


def xor_lag(data, lag, inverse=False):
    if not 1 <= lag <= 256:
        raise ValueError("invalid delta lag")
    out = bytearray(data)
    if inverse:
        for i in range(lag, len(out)):
            out[i] ^= out[i-lag]
    else:
        for i in range(lag, len(out)):
            out[i] ^= data[i-lag]
    return bytes(out)


def nibble_pack(data, inverse=False, original_len=None):
    if not inverse:
        symbols = [(b if b < 128 else b - 256) + 7 for b in data]
        if any(not 0 <= b <= 14 for b in symbols):
            raise ValueError("raw i8 tensor is not restricted to [-7,7]")
        out = bytearray((len(symbols) + 1)//2)
        for i in range(0, len(symbols), 2):
            out[i//2] = symbols[i] | ((symbols[i+1] if i+1 < len(symbols) else 0)<<4)
        return bytes(out)
    if original_len is None or len(data) != (original_len+1)//2:
        raise ValueError("invalid packed nibble length")
    out = bytearray()
    for b in data:
        out.extend(((b & 15)-7 & 255, (b >> 4)-7 & 255))
    if any(((b if b < 128 else b-256) + 7) > 14 for b in out[:original_len]):
        raise ValueError("invalid packed nibble code")
    if original_len & 1 and data and data[-1] >> 4:
        raise ValueError("nonzero nibble padding")
    return bytes(out[:original_len])


def tensor_layout(data, nibble=False, delta=False, inverse=False):
    records = parse_records(data, packed_payload_mode=nibble if inverse else None)
    out = bytearray(data[:12])
    for r in records:
        check_time()
        payload, width = r["data"], WIDTHS[r["dtype"]]
        if nibble and r["i4"]:
            payload = nibble_pack(payload, inverse, r["nval"])
        elif width > 1 and payload:
            if inverse:
                payload = planes(payload, width, True)
                if delta:
                    payload = xor_lag(payload, width, True)
            else:
                if delta:
                    payload = xor_lag(payload, width)
                payload = planes(payload, width)
        out.extend(r["header"])
        out.extend(payload)
    return bytes(out)


def tensor_split(data, inverse=False):
    """Exact ints through adaptive range coding, other typed planes stay exposed.

    This retains the int4 entropy model rather than asking LZMA to discover it.
    The outer codec can compress the small float/name/shape portion. The wrapper
    inverse recreates the explicit tensor stream and finally original v2 bytes.
    """
    packet = struct.Struct("<8sQQ")
    if not inverse:
        records = parse_records(data)
        meta = bytearray(data[:12])
        rc, probs, count = RangeEncoder(), [1024] * 16, 0
        for r in records:
            check_time()
            meta.extend(r["header"])
            payload = r["data"]
            if r["i4"]:
                for k, b in enumerate(payload):
                    if (k & 65535) == 0:
                        check_time()
                    symbol = (b if b < 128 else b-256)+7
                    if not 0 <= symbol <= 14:
                        raise ValueError("int4 split requires exact [-7,7] values")
                    rc.tree(probs, 4, symbol)
                count += len(payload)
            elif payload:
                meta.extend(planes(payload, WIDTHS[r["dtype"]]))
        return packet.pack(b"R7SPLIT1", len(meta), count) + bytes(meta) + rc.finish()
    need(data, 0, packet.size)
    magic, nm, count = packet.unpack_from(data)
    if magic != b"R7SPLIT1" or nm > 128*1024*1024 or count > 128*1024*1024:
        raise ValueError("invalid split packet")
    need(data, packet.size, nm)
    meta = data[packet.size:packet.size+nm]
    records = parse_records(meta, packed_payload_mode="omit")
    rd, probs, seen = RangeDecoder(data[packet.size+nm:]), [1024]*16, 0
    out = bytearray(meta[:12])
    for r in records:
        check_time()
        out.extend(r["header"])
        if r["i4"]:
            payload = bytearray()
            for k in range(r["nval"]):
                if (k & 65535) == 0:
                    check_time()
                symbol = rd.tree(probs, 4)
                if symbol > 14:
                    raise ValueError("invalid split int4 symbol")
                payload.append((symbol-7)&255)
            out.extend(payload)
            seen += r["nval"]
        elif r["data"]:
            out.extend(planes(r["data"], WIDTHS[r["dtype"]], True))
    if seen != count:
        raise ValueError("split symbol count differs")
    return bytes(out)


def transform(data, spec, inverse=False, original_len=None):
    kind = spec["kind"]
    if kind == "identity":
        return data
    if kind == "planes":
        return planes(data, spec["width"], inverse)
    if kind == "xor":
        return xor_lag(data, spec["lag"], inverse)
    if kind == "planes_xor":
        if inverse:
            return xor_lag(planes(data, spec["width"], True), spec["width"], True)
        return planes(xor_lag(data, spec["width"]), spec["width"])
    if kind == "gray":
        table = bytes([i ^ (i >> 1) for i in range(256)])
        if inverse:
            inv = bytearray(256)
            for i, b in enumerate(table):
                inv[b] = i
            table = bytes(inv)
        return data.translate(table)
    if kind == "nibble_planes":
        if not inverse:
            return bytes(b & 15 for b in data) + bytes(b >> 4 for b in data)
        if original_len is None or len(data) != original_len * 2:
            raise ValueError("invalid nibble-plane length")
        lo, hi = data[:original_len], data[original_len:]
        if any(b > 15 for b in data):
            raise ValueError("invalid nibble plane")
        return bytes(a | (b << 4) for a, b in zip(lo, hi))
    if kind == "tensor":
        return tensor_layout(data, spec.get("nibble", False), spec.get("delta", False), inverse)
    if kind == "tensor_split":
        return tensor_split(data, inverse)
    raise ValueError("unknown transform")


def codec(data, code, inverse=False):
    if code == 0:
        return data
    if code == 1:
        return zlib.decompress(data) if inverse else zlib.compress(data, 9)
    if code == 2:
        return lzma.decompress(data) if inverse else lzma.compress(data, preset=6)
    if code == 3:
        if inverse:
            return lzma.decompress(data)
        return lzma.compress(data, filters=[{"id": lzma.FILTER_DELTA, "dist": 4},
                                           {"id": lzma.FILTER_LZMA2, "preset": 6}])
    if code == 4:
        import zstandard as zstd
        return (zstd.ZstdDecompressor().decompress(data) if inverse else
                zstd.ZstdCompressor(level=9, threads=0, write_checksum=True).compress(data))
    raise ValueError("unknown codec")


def codec_worker(conn, data, code):
    try:
        t = time.perf_counter()
        packed = codec(data, code)
        ct = time.perf_counter()-t
        t = time.perf_counter()
        unpacked = codec(packed, code, True)
        dt = time.perf_counter()-t
        conn.send((True, packed, ct, dt, sha(unpacked), unpacked == data))
    except Exception as exc:
        conn.send((False, type(exc).__name__ + ": " + str(exc)))
    finally:
        conn.close()


def bounded_codec(data, code, seconds):
    parent, child = mp.Pipe(duplex=False)
    ctx = mp.get_context("spawn")
    proc = ctx.Process(target=codec_worker, args=(child, data, code), daemon=True)
    proc.start()
    child.close()
    try:
        if not parent.poll(seconds):
            proc.terminate()
            proc.join(5)
            raise TimeoutError("codec exceeded %.1fs cap" % seconds)
        result = parent.recv()
        proc.join(5)
        if proc.is_alive():
            proc.terminate()
            proc.join(5)
        if not result[0]:
            raise RuntimeError(result[1])
        if not result[5]:
            raise AssertionError("codec inverse bytes differ")
        return result[1:5]
    finally:
        parent.close()
        if proc.is_alive():
            proc.terminate()
            proc.join(5)


def make_wrapper(packed, spec, code, source_len, base_len, semantic):
    metadata = json.dumps({"transform": spec, "semantic_v2": semantic},
                          sort_keys=True, separators=(",", ":")).encode("ascii")
    return HEADER.pack(MAGIC, code, 1, 0, source_len, base_len, len(metadata)) + metadata + packed


def unpack_wrapper(blob):
    if len(blob) < HEADER.size:
        raise ValueError("truncated wrapper")
    magic, code, version, flags, source_len, base_len, nm = HEADER.unpack_from(blob)
    if magic != MAGIC or version != 1 or flags != 0 or nm > 8192:
        raise ValueError("invalid wrapper header")
    if source_len > 128*1024*1024 or base_len > 128*1024*1024:
        raise ValueError("wrapper exceeds bounded output size")
    need(blob, HEADER.size, nm)
    meta = json.loads(blob[HEADER.size:HEADER.size+nm])
    packed = blob[HEADER.size+nm:]
    image = codec(packed, code, True)
    base = transform(image, meta["transform"], True, base_len)
    if len(base) != base_len:
        raise ValueError("inverse base length differs")
    original = encode_v2(base) if meta["semantic_v2"] else base
    if len(original) != source_len:
        raise ValueError("restored container length differs")
    return original


def entropy(data):
    counts = collections.Counter(data)
    n = len(data)
    return -sum(c * math.log2(c/n) for c in counts.values()) if n else 0.0


def tensor_diagnostics(data):
    records = parse_records(data)
    all_i4 = bytearray()
    tensor_bits, row_bits, row_count = 0.0, 0.0, 0
    rows = []
    for r in records:
        check_time()
        if not r["i4"] or not r["data"]:
            continue
        payload = r["data"]
        # This is the stored exact integer image, never latent fp32 requantization.
        if any(not 0 <= (b if b < 128 else b-256)+7 <= 14 for b in payload):
            continue
        hb = entropy(payload)
        tensor_bits += hb
        all_i4.extend(payload)
        row_len = math.prod(r["shape"][1:]) if len(r["shape"]) >= 2 else len(payload)
        rr = 0.0
        for off in range(0, len(payload), row_len or 1):
            rr += entropy(payload[off:off+row_len])
            row_count += 1
        row_bits += rr
        rows.append({"name": r["name"].decode("utf-8", "replace"),
                     "shape": r["shape"], "count": len(payload),
                     "entropy_bits": hb, "row_entropy_bits": rr,
                     "stored_int_sha256": sha(payload)})
    return {"exact_stored_int4_count": len(all_i4), "global_entropy_bytes": entropy(all_i4)/8,
            "per_tensor_entropy_bytes": tensor_bits/8, "per_row_entropy_bytes": row_bits/8,
            "row_count": row_count, "tensors": rows,
            "warning": "Empirical entropy excludes required model/table costs and is not an achieved size. "
                       "Per-row estimates are biased downward by small samples; no production saving is claimed."}


def specifications(explicit=False):
    out = [{"kind": "identity"}]
    if explicit:
        out += [{"kind": "tensor_split"}]
        out += [{"kind": "tensor", "nibble": x, "delta": d}
                for x, d in [(False, False), (True, False), (True, True)]]
    out += [{"kind": "planes", "width": w} for w in (2, 4, 8, 16)]
    out += [{"kind": "xor", "lag": 1}, {"kind": "planes_xor", "width": 4},
            {"kind": "gray"}, {"kind": "nibble_planes"}]
    return out


def survey_file(path, args):
    check_time()
    size = path.stat().st_size
    if size > args.max_mib * 1024*1024:
        return {"path": str(path), "status": "skipped_size_cap", "input_bytes": size}
    original = path.read_bytes()
    original_sha = sha(original)
    result = {"path": str(path), "input_bytes": len(original), "sha256": original_sha,
              "magic_hex": original[:12].hex(), "rows": [], "semantic_status": "not_attempted",
              "decoder_code_bytes": None, "status": "running"}
    bases = [(original, False, original[:8] == b"FX2TFW01")]
    if original[:8] == b"FX2TFWC2" and not args.no_semantic:
        try:
            t = time.perf_counter()
            canonical = decode_v2(original)
            dsecs = time.perf_counter()-t
            t = time.perf_counter()
            rebuilt = encode_v2(canonical)
            esecs = time.perf_counter()-t
            if rebuilt != original or sha(rebuilt) != original_sha:
                raise AssertionError("public v2 rebuild differs: semantic survey disabled")
            result.update(semantic_status="exact_original_container_rebuild_verified",
                          canonical_bytes=len(canonical), semantic_decode_seconds=dsecs,
                          semantic_encode_seconds=esecs, rebuilt_sha256=sha(rebuilt))
            result["integer_entropy_diagnostics"] = tensor_diagnostics(canonical)
            bases.insert(0, (canonical, True, True))
        except Exception as exc:
            result["semantic_status"] = type(exc).__name__ + ": " + str(exc)
    elif original[:8] == b"FX2TFW01":
        try:
            result["integer_entropy_diagnostics"] = tensor_diagnostics(original)
        except Exception as exc:
            result["raw_parse_warning"] = str(exc)
    codes = [1, 2, 3]
    try:
        import zstandard  # noqa: F401
        codes.append(4)
    except ImportError:
        result["zstd_status"] = "not installed; no installation attempted"
    best = None
    for base, semantic, explicit in bases:
        if explicit:
            try:
                parse_records(base)
            except Exception:
                explicit = False
        specs = specifications(explicit)
        if args.focus_split:
            specs = [{"kind": "tensor_split"}] if explicit else []
        for spec in specs:
            if time.monotonic() >= DEADLINE:
                result["status"] = "time_cap_reached"
                break
            t = time.perf_counter()
            try:
                image = transform(base, spec)
                encsecs = time.perf_counter()-t
                t = time.perf_counter()
                recovered = transform(image, spec, True, len(base))
                invsecs = time.perf_counter()-t
                if recovered != base or sha(recovered) != sha(base):
                    raise AssertionError("transform inverse differs")
            except Exception as exc:
                result["rows"].append({"transform": spec, "semantic_v2": semantic,
                                       "error": type(exc).__name__ + ": " + str(exc)})
                continue
            for code in codes:
                remaining = DEADLINE - time.monotonic()
                if remaining <= 1:
                    result["status"] = "time_cap_reached"
                    break
                try:
                    packed, ct, dt, decoded_image_sha = bounded_codec(
                        image, code, min(args.codec_seconds, remaining))
                    wrapper = make_wrapper(packed, spec, code, len(original), len(base), semantic)
                    # Every codec's decoded image is byte-identical to the same
                    # certified image. Every transform inverse is byte-identical
                    # to the certified base. V2 base->original is independently
                    # exact. This checks the full composition without repeatedly
                    # spending ~millions of range-code operations per codec.
                    if decoded_image_sha != sha(image):
                        raise AssertionError("decoded transformed SHA differs")
                    row = {"transform": spec, "semantic_v2": semantic,
                           "codec": CODECS[code], "codec_id": code,
                           "transformed_bytes": len(image), "codec_bytes": len(packed),
                           "wrapper_metadata_bytes": len(wrapper)-len(packed),
                           "total_blob_bytes": len(wrapper),
                           "saving_per_copy_before_decoder_code": len(original)-len(wrapper),
                           "saving_two_copies_before_decoder_code": 2*(len(original)-len(wrapper)),
                           "transform_seconds": encsecs, "inverse_seconds": invsecs,
                           "compression_seconds": ct, "decompression_seconds": dt,
                           "original_sha256": original_sha, "inverse_base_sha256": sha(recovered),
                           "roundtrip_exact": True,
                           "verification": "exact codec inverse + exact transform inverse + " +
                           ("certified exact entropy-stream rebuild" if semantic else "original byte equality")}
                    result["rows"].append(row)
                    if best is None or len(wrapper) < len(best[0]):
                        best = (wrapper, row)
                    print(json.dumps({"progress": str(path), "semantic": semantic,
                                      "transform": spec, "codec": CODECS[code],
                                      "total_bytes": len(wrapper), "saving": len(original)-len(wrapper)}), flush=True)
                except Exception as exc:
                    result["rows"].append({"transform": spec, "semantic_v2": semantic,
                                           "codec": CODECS[code], "error": type(exc).__name__+": "+str(exc)})
        if result["status"] == "time_cap_reached":
            break
    if best is not None:
        result["best"] = best[1]
        # Explicitly re-run the complete inverse chain for the actual finalist.
        if DEADLINE - time.monotonic() > 2:
            try:
                restored = unpack_wrapper(best[0])
                if restored != original or sha(restored) != original_sha:
                    raise AssertionError("finalist full inverse differs")
                result["best"]["finalist_full_original_sha256"] = sha(restored)
                result["best"]["finalist_full_roundtrip_exact"] = True
                if args.save_best and len(best[0]) < len(original):
                    destination = pathlib.Path(args.save_best)
                    if len(args.inputs) > 1:
                        destination = destination.with_name(destination.name + "." + path.name.lstrip("."))
                    if destination.resolve() == path.resolve():
                        raise ValueError("save-best cannot overwrite source")
                    with destination.open("xb") as f:
                        f.write(best[0])
                    result["saved_best"] = str(destination)
            except Exception as exc:
                result["best"]["finalist_full_roundtrip_error"] = type(exc).__name__+": "+str(exc)
        else:
            result["best"]["finalist_full_roundtrip_status"] = "not repeated: deadline; chained component checks passed"
    if result["status"] == "running":
        result["status"] = "complete"
    result["interpretation"] = ("Existing loader can be kept only behind a new wrapper inverse that restores "
        "the identical original blob. Gross savings exclude C++ inverse/library code, build packing and peak RSS. "
        "Semantic inverse reencodes the adaptive stream at startup; measure that CPU cost before integration. "
        "No numeric weight change or retraining occurred.")
    return result


def self_test():
    global DEADLINE
    DEADLINE = time.monotonic()+90
    for n in (0, 1, 2, 3, 7, 31, 1001):
        data = bytes((i*73+11) & 255 for i in range(n))
        for spec in specifications():
            image = transform(data, spec)
            assert transform(image, spec, True, len(data)) == data, (n, spec)
    raw = b"FX2TFW01"+struct.pack("<I", 3)
    canonical = CANON+struct.pack("<I", 4)
    entries = [(b"w.q", 0, [3, 5], 1, bytes((q-7)&255 for q in range(15))),
               (b"scale", 1, [3], 2, b"\0\x3f\x01\x3f\x02\x40"),
               (b"bias", 2, [2], 3, struct.pack("<II", 0x80000000, 0x7FC01234))]
    for name, dtype, shape, enc, payload in entries:
        raw += record_header(name, dtype, shape)+payload
        canonical += record_header(name, dtype, shape, enc)+payload
    canonical += record_header(b"rope.sin", 2, [17, 32], 4)
    encoded = encode_v2(canonical)
    assert decode_v2(encoded) == canonical
    assert encode_v2(decode_v2(encoded)) == encoded
    for data in (raw, canonical):
        for spec in specifications(True):
            image = transform(data, spec)
            assert transform(image, spec, True, len(data)) == data
    for spec in specifications(True):
        image = transform(canonical, spec)
        for code in (0, 1, 2, 3):
            packed = codec(image, code)
            wrapper = make_wrapper(packed, spec, code, len(encoded), len(canonical), True)
            assert unpack_wrapper(wrapper) == encoded
    diagnostics = tensor_diagnostics(canonical)
    assert diagnostics["exact_stored_int4_count"] == 15
    print(json.dumps({"self_test": "passed", "v2_test_sha256": sha(encoded),
                      "raw_test_sha256": sha(raw)}))


def main():
    global DEADLINE
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("inputs", nargs="*")
    p.add_argument("--out", default="weight_pack_results.json")
    p.add_argument("--save-best", help="write only a beneficial fully verified wrapper; exclusive create")
    p.add_argument("--seconds", type=float, default=540)
    p.add_argument("--codec-seconds", type=float, default=45)
    p.add_argument("--max-mib", type=int, default=64)
    p.add_argument("--no-semantic", action="store_true")
    p.add_argument("--focus-split", action="store_true", help="only semantic int4/float split candidates")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--unpack")
    p.add_argument("--restore")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    if not 1 <= args.seconds <= 600 or not 1 <= args.codec_seconds <= 60 or not 1 <= args.max_mib <= 128:
        p.error("bounds: seconds 1..600, codec-seconds 1..60, max-mib 1..128")
    DEADLINE = time.monotonic()+args.seconds
    if args.unpack:
        if not args.restore:
            p.error("--unpack requires --restore")
        source, dest = pathlib.Path(args.unpack), pathlib.Path(args.restore)
        if source.stat().st_size > args.max_mib*1024*1024:
            p.error("wrapper exceeds input size cap")
        original = unpack_wrapper(source.read_bytes())
        with dest.open("xb") as f:
            f.write(original)
        print(json.dumps({"restored": str(dest), "bytes": len(original), "sha256": sha(original)}))
        return
    if not args.inputs:
        p.error("supply an existing packed/raw weight file")
    output = pathlib.Path(args.out)
    if any(output.resolve() == pathlib.Path(s).resolve() for s in args.inputs):
        p.error("--out cannot overwrite an input")
    started = time.monotonic()
    report = {"version": 1, "purpose": "exact no-retraining survey", "files": [],
              "time_cap_seconds": args.seconds, "decoder_code_accounting": "not measured"}
    for input_name in args.inputs:
        if time.monotonic() >= DEADLINE:
            report["unfinished_inputs"] = args.inputs[len(report["files"]):]
            break
        try:
            report["files"].append(survey_file(pathlib.Path(input_name), args))
        except Exception as exc:
            report["files"].append({"path": input_name, "status": "error", "error": type(exc).__name__+": "+str(exc)})
        report["elapsed_seconds"] = time.monotonic()-started
        output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["elapsed_seconds"] = time.monotonic()-started
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(output), "elapsed_seconds": report["elapsed_seconds"]}))


if __name__ == "__main__":
    mp.freeze_support()
    main()
