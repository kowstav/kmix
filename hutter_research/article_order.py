"""Paid, reversible article-order proxy. It is not a canonical native-cmix result.

The asymmetric edge proxy is prefix cross-entropy under the previous article's
byte histogram. Search improvements need not transfer to the production model.
"""
import gzip
import hashlib
import json
import struct
from pathlib import Path
import numpy as np


def read_pages(path):
    data = Path(path).read_bytes()
    count, = struct.unpack_from("<I", data)
    offset = 4
    pages = []
    for _ in range(count):
        length, = struct.unpack_from("<I", data, offset)
        offset += 4
        pages.append(data[offset:offset + length])
        assert len(pages[-1]) == length
        offset += length
    assert offset == len(data)
    return pages


def compress(pages, permutation):
    permutation = list(map(int, permutation))
    n = len(pages)
    assert sorted(permutation) == list(range(n))
    identity = permutation == list(range(n))
    order = b"" if identity else gzip.compress(np.asarray(permutation, dtype="<u4").tobytes(), mtime=0)
    lengths = gzip.compress(np.asarray([len(pages[i]) for i in permutation], dtype="<u4").tobytes(), mtime=0)
    payload = gzip.compress(b"".join(pages[i] for i in permutation), compresslevel=9, mtime=0)
    return b"HPORDER1" + struct.pack("<IIII", n, len(order), len(lengths), len(payload)) + order + lengths + payload


def decompress(archive):
    assert archive[:8] == b"HPORDER1"
    n, order_bytes, length_bytes, payload_bytes = struct.unpack_from("<IIII", archive, 8)
    assert len(archive) == 24 + order_bytes + length_bytes + payload_bytes
    offset = 24
    order = list(range(n)) if not order_bytes else np.frombuffer(gzip.decompress(archive[offset:offset + order_bytes]), dtype="<u4").tolist()
    assert sorted(order) == list(range(n))
    offset += order_bytes
    lengths = np.frombuffer(gzip.decompress(archive[offset:offset + length_bytes]), dtype="<u4")
    assert len(lengths) == n
    offset += length_bytes
    raw = gzip.decompress(archive[offset:])
    result = [None] * n
    offset = 0
    for i, length in zip(order, lengths):
        length = int(length)
        result[i] = raw[offset:offset + length]
        offset += length
    assert offset == len(raw)
    return result


def edge_matrix(pages):
    hist = np.asarray([np.bincount(np.frombuffer(page, "u1"), minlength=256) for page in pages], dtype="float64")
    prefix = np.asarray([np.bincount(np.frombuffer(page[:4096], "u1"), minlength=256) for page in pages], dtype="float64")
    log_prob = -np.log2((hist + .5) / (hist.sum(axis=1, keepdims=True) + 128))
    edge = log_prob @ prefix.T
    np.fill_diagonal(edge, np.inf)
    return edge


def cost(edge, order):
    return float(sum(edge[a, b] for a, b in zip(order, order[1:])))


def greedy(edge, start):
    n = len(edge)
    used = np.zeros(n, dtype=bool)
    used[start] = True
    order = [start]
    while len(order) < n:
        row = edge[order[-1]].copy()
        row[used] = np.inf
        target = int(np.argmin(row))
        used[target] = True
        order.append(target)
    return order


def swap_descent(edge, order, max_passes=3):
    # Directed edge accounting: only edges adjacent to the two positions change.
    order = list(order)
    for _ in range(max_passes):
        improved = False
        for i in range(len(order)):
            for j in range(i + 1, len(order)):
                adjacent = {k for k in [i - 1, i, j - 1, j] if 0 <= k < len(order) - 1}
                before = sum(edge[order[k], order[k + 1]] for k in adjacent)
                order[i], order[j] = order[j], order[i]
                after = sum(edge[order[k], order[k + 1]] for k in adjacent)
                if after + 1e-9 < before:
                    improved = True
                else:
                    order[i], order[j] = order[j], order[i]
        if not improved:
            break
    return order


def experiment(pages_path, output):
    pages = read_pages(pages_path)
    assert 16 <= len(pages) <= 1024
    output = Path(output)
    edge = edge_matrix(pages)
    rng = np.random.default_rng(10007)
    orders = {"original": list(range(len(pages)))}
    for i in range(8):
        orders["random_" + str(i)] = rng.permutation(len(pages)).tolist()
    starts = np.linspace(0, len(pages) - 1, 8).astype(int)
    greedy_orders = [greedy(edge, int(start)) for start in starts]
    best = min(greedy_orders, key=lambda order: cost(edge, order))
    orders["greedy_proxy"] = best
    orders["directed_swap_proxy"] = swap_descent(edge, best)
    assert cost(edge, orders["directed_swap_proxy"]) <= cost(edge, best) + 1e-6
    # Select solely on the declared edge proxy. Do not choose the winner using
    # measured gzip bytes, even though all exploratory control scores are saved.
    selected = "directed_swap_proxy"
    rows = []
    for name, order in orders.items():
        archive = compress(pages, order)
        assert decompress(archive) == pages
        (output / (name + ".hporder")).write_bytes(archive)
        rows.append({"name": name, "proxy_bits": cost(edge, order), "archive_bytes": len(archive),
                     "archive_sha256": hashlib.sha256(archive).hexdigest(), "independent_reconstruction_exact": True})
    baseline = next(row for row in rows if row["name"] == "original")["archive_bytes"]
    winner = next(row for row in rows if row["name"] == selected)["archive_bytes"]
    return {"status": "COMPLETE_PAID_ARTICLE_ORDER_GZIP_PROXY", "article_count": len(pages),
            "selected_without_gzip_peeking": selected, "actual_proxy_archive_gain_bytes": baseline - winner,
            "article_order_cases": rows, "limits": "early raw pages, gzip proxy, all control results exploratory; not canonical WRT/native model or eligible executable price"}
