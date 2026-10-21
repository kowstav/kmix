import json,tempfile,unittest
from pathlib import Path
try:
    import resource
except ImportError:
    n=None
else:
    from hutter_research import cpu_round13_native as n

@unittest.skipIf(n is None,'Linux resource accounting required; run on Kaggle')
class NativeInputContractTests(unittest.TestCase):
    def test_preflight_cannot_silently_satisfy_larger_scope(self):
        old=n.ASSET
        try:
            with tempfile.TemporaryDirectory() as d:
                n.ASSET=Path(d);(n.ASSET/'input.bin').write_bytes(b'x'*65536)
                (n.ASSET/'r13_assets.json').write_text(json.dumps({'regions':[{'file':'input.bin'}]}))
                with self.assertRaisesRegex(ValueError,'16384 differs from declared 65536'):
                    n.archive_case(0,'unused',True,65536)
        finally:n.ASSET=old

    def test_short_source_is_rejected_before_native_execution(self):
        old=n.ASSET
        try:
            with tempfile.TemporaryDirectory() as d:
                n.ASSET=Path(d);(n.ASSET/'input.bin').write_bytes(b'x'*32768)
                (n.ASSET/'r13_assets.json').write_text(json.dumps({'regions':[{'file':'input.bin'}]}))
                with self.assertRaisesRegex(ValueError,'32768 differs from declared 65536'):
                    n.archive_case(0,'unused',False,65536)
        finally:n.ASSET=old
