"""Contracts for relocating a workspace with dynamic and historical paths."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts._workspace_layout import ROOT, project_glob, project_path, project_root


class RepositoryLayout(unittest.TestCase):
    def test_all_original_files_have_a_destination(self):
        layout = json.loads((ROOT / 'data/repository_layout.json').read_text())
        missing = [new for new in layout['files'].values() if not (ROOT / new).is_file()]
        self.assertEqual(missing, [])
        self.assertEqual(len(set(layout['files'].values())), len(layout['files']))

    def test_original_paths_resolve_to_the_index(self):
        layout = json.loads((ROOT / 'data/repository_layout.json').read_text())
        for old, new in layout['files'].items():
            with self.subTest(path=old):
                self.assertEqual(project_path(old), ROOT / new)

    def test_dynamic_outputs_go_to_their_folder(self):
        for name, folder in [('research_round99_results.json', 'data'),
                             ('research_round99_report.md', 'docs'),
                             ('research_round99_evidence.zip', 'archives'),
                             ('research_round99_worker.py', 'scripts')]:
            self.assertEqual(project_path(name), ROOT / folder / name)

    def test_current_paths_are_not_remapped(self):
        self.assertEqual(project_path('data/repository_layout.json'), ROOT / 'data/repository_layout.json')
        self.assertEqual(project_path('hutter_research/contracts.py'), ROOT / 'hutter_research/contracts.py')
        self.assertEqual(project_root(__file__), ROOT)

    def test_non_root_and_absolute_paths_stay_literal(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            self.assertEqual(project_path('research_round14_report.md', base=base), base / 'research_round14_report.md')
            absolute = base / 'research_round14_report.md'
            self.assertEqual(project_path(absolute), absolute)

    def test_legacy_glob_finds_only_matching_root_names(self):
        layout = json.loads((ROOT / 'data/repository_layout.json').read_text())
        expected = {ROOT / new for old, new in layout['top_level_paths'].items()
                    if old.startswith('research_round10_') and old.endswith('.py')}
        self.assertEqual(set(project_glob('research_round10_*.py')), expected)
        self.assertEqual(set(project_glob('kaggle_cpu_round10/*/kernel-metadata.json')),
                         set((ROOT / 'scripts/kaggle_cpu_round10').glob('*/kernel-metadata.json')))


if __name__ == '__main__':
    unittest.main()
