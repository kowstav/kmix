"""Causal and neutral contracts for the compiled integer predictor.

Synthetic streams test correctness properties, not compression quality. Native
warm traces and independent archives are the quality/integration experiments.
"""
import json
import pathlib
import struct
import subprocess
import tempfile
import unittest
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXE = ROOT / "hutter_research/integer_mixer_replay.exe"


class ReplayContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.path = pathlib.Path(self.temp.name)
        self.raw = bytes((i * 37 + 13) % 256 for i in range(256))
        self.native = np.full((256, 8), 24000, dtype="<u2")
        self.hidden = np.zeros((256, 193), dtype="u1")
        self.hidden[:, 0] = 1
        self.stage = np.zeros((256, 8, 19), dtype="<f4")
        self.stage[:, :, :14] = .7
        self.stage[:, :, 14:] = .61
        self.stage[:, :, 17] = .82

    def tearDown(self):
        self.temp.cleanup()

    def run_arm(self, arm="full", raw=None, nn=None):
        p = self.path
        (p / "input").write_bytes(self.raw if raw is None else raw)
        self.native.tofile(p / "native")
        self.hidden.tofile(p / "hidden")
        stage = self.stage.copy()
        if nn is not None:
            stage[:, :, 17] = nn
        (p / "stage").write_bytes(b"HPSTG001" + struct.pack("<I", 19) + stage.tobytes())
        args = [str(EXE), *map(str, [p / "input", p / "native", p / "hidden",
                                    p / "stage", p / "output"]), arm, "1000"]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (p / "output").read_bytes(), json.loads(result.stdout)

    def test_identity_matches_every_native_probability_and_cost(self):
        output, result = self.run_arm("identity")
        self.assertEqual(output, self.native.tobytes())
        self.assertEqual(result["baseline_bits"], result["candidate_bits"])

    def test_active_replay_is_prefix_causal(self):
        original, _ = self.run_arm()
        mutation = self.raw[:128] + bytes(b ^ 0xff for b in self.raw[128:])
        changed, _ = self.run_arm(raw=mutation)
        # Include the first bit following the shared prefix: its outcome has
        # not yet been decoded, so it cannot affect that bit's prediction.
        self.assertEqual(original[:128 * 16 + 2], changed[:128 * 16 + 2])
        self.assertNotEqual(original[128 * 16 + 2:], changed[128 * 16 + 2:])

    def test_context_relabeling_is_exact_and_not_a_null(self):
        original, _ = self.run_arm("full")
        relabeled, _ = self.run_arm("relabel")
        self.assertEqual(original, relabeled)

    def test_explicit_neural_ablation_removes_feature_and_confidence(self):
        a, _ = self.run_arm("no_explicit_nn", nn=.51)
        b, _ = self.run_arm("no_explicit_nn", nn=.999)
        self.assertEqual(a, b)

    def test_global_context_is_a_real_ablation(self):
        a, _ = self.run_arm("full")
        b, _ = self.run_arm("global")
        self.assertNotEqual(a, b)

    def test_long_memory_is_prefix_causal(self):
        self.hidden[:, 1:] = np.arange(192, dtype="u1")
        a, _ = self.run_arm("long_memory")
        mutation = self.raw[:128] + bytes(b ^ 0xff for b in self.raw[128:])
        b, _ = self.run_arm("long_memory", raw=mutation)
        self.assertEqual(a[:128 * 16 + 2], b[:128 * 16 + 2])

    def test_carried_memory_differs_from_short_reset_control(self):
        self.hidden[:, 1:] = np.arange(192, dtype="u1")
        a, _ = self.run_arm("long_memory")
        b, _ = self.run_arm("short_memory")
        self.assertEqual(a[:128 * 16], b[:128 * 16])
        self.assertNotEqual(a[128 * 16:], b[128 * 16:])


if __name__ == "__main__":
    unittest.main()
