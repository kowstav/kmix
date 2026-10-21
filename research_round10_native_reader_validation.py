"""Independently compare native C++ tensor decoding with the Python specification.

This tests storage, dtype promotion, tensor order and RoPE regeneration. It does
not claim native probability equivalence or archive savings after BF16 rounding.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import numpy as np
from hutter_research import native_weights, tensor_io

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "research_round10_bf16_repaired_models"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    binary = ROOT / "hutter_research/weights_dump.exe"
    manifest = {
        "id": "R10-E1-native-reader", "status": "RUNNING",
        "started": time.time(), "platform": "Windows x86-64 GCC",
        "reader_binary_sha256": sha(binary), "cases": [],
        "archive_gate": "PENDING; new rounded models require new native archives",
    }
    output = ROOT / "research_round10_native_reader_results.json"

    def save():
        output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    save()
    for name in ["neutral", "unweighted", "cut107_half", "cut1392_zero"]:
        source = DEST / f"{name}.tfwc3"
        decoded_path = DEST / f"{name}.native.tfw"
        start = time.monotonic()
        result = subprocess.run([str(binary), str(source), str(decoded_path)],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        expected = native_weights.read_tensor_file_v3(str(source))
        actual = tensor_io.read_tensor_file(str(decoded_path))
        assert set(expected) == set(actual)
        rows = []
        for tensor, (dtype, values) in expected.items():
            if dtype == 1 and not tensor.endswith(".scale"):
                values = (values.astype("<u4") << 16).view("<f4")
                dtype = 2
            native_dtype, native_values = actual[tensor]
            assert dtype == native_dtype, (name, tensor, dtype, native_dtype)
            assert values.shape == native_values.shape, (name, tensor)
            assert values.tobytes() == native_values.tobytes(), (name, tensor)
            rows.append({"name": tensor, "dtype": dtype, "elements": values.size,
                         "sha256": hashlib.sha256(values.tobytes()).hexdigest()})
        row = {"name": name, "model_bytes": source.stat().st_size,
               "model_sha256": sha(source), "native_decoded_sha256": sha(decoded_path),
               "tensor_count": len(rows), "all_tensor_dtype_shape_bytes_equal": True,
               "wall_seconds": time.monotonic() - start, "tensors": rows}
        manifest["cases"].append(row)
        save()
        print(json.dumps({k: v for k, v in row.items() if k != "tensors"}), flush=True)
    manifest.update(status="COMPLETE_NATIVE_READER_ALL_TENSORS_EXACT", finished=time.time())
    save()


if __name__ == "__main__":
    main()
