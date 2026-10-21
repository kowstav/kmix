from pathlib import Path
import json
import tempfile
import unittest
from hutter_research.dispatch_contracts import validate_existing_kernel,parse_successful_push


class Dispatch(unittest.TestCase):
    def test_exit_zero_is_not_API_success(self):
        with self.assertRaises(ValueError):
            parse_successful_push('Kernel push error: notebook quota exceeded','owner')
        with self.assertRaises(ValueError):
            parse_successful_push('No error but no verified resource URL','owner')

    def test_creation_returns_actual_title_slug(self):
        line='Kernel version 1 successfully pushed. Please check progress at https://www.kaggle.com/code/owner/actual-title-slug'
        result=parse_successful_push(line,'owner')
        self.assertEqual(result['actual_ref'],'owner/actual-title-slug')
        self.assertEqual(result['version'],1)
        with self.assertRaises(ValueError): parse_successful_push(line,'different-owner')
        with self.assertRaises(ValueError):
            parse_successful_push('The following are not valid dataset sources\n'+line,'owner')

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.source = b"print('finite CPU protocol')\n"
        self.metadata = {"id": "owner/finite-v1", "language": "python", "kernel_type": "script",
                         "is_private": True, "enable_gpu": False, "enable_tpu": False,
                         "enable_internet": False, "dataset_sources": ["owner/immutable-v1"],
                         "competition_sources": [], "kernel_sources": [], "code_file": "main.py"}
        (self.folder / "main.py").write_bytes(self.source)
        self.write_metadata(self.metadata)

    def write_metadata(self, metadata):
        (self.folder / "kernel-metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    def test_exact_source_allows_only_transport_line_ending_change(self):
        (self.folder / "main.py").write_bytes(self.source.replace(b"\n", b"\r\n"))
        self.assertTrue(validate_existing_kernel(self.folder, self.metadata, self.source)["metadata_checked"])
        (self.folder / "main.py").write_bytes(self.source.replace(b"CPU", b"GPU"))
        with self.assertRaises(ValueError):
            validate_existing_kernel(self.folder, self.metadata, self.source)

    def test_wrong_privacy_resource_inputs_or_missing_settings_block_reuse(self):
        variants = [{"is_private": False}, {"enable_gpu": True}, {"enable_tpu": True},
                    {"enable_internet": True}, {"dataset_sources": ["owner/other"]},
                    {"id": "owner/other"}, {"code_file": "../main.py"}]
        for variant in variants:
            with self.subTest(variant=variant):
                self.write_metadata({**self.metadata, **variant})
                with self.assertRaises(ValueError):
                    validate_existing_kernel(self.folder, self.metadata, self.source)
        del_missing = dict(self.metadata)
        del del_missing["is_private"]
        self.write_metadata(del_missing)
        with self.assertRaises(ValueError):
            validate_existing_kernel(self.folder, self.metadata, self.source)
