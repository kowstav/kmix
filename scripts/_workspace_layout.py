"""Resolve local research paths after separating code, documents, and evidence.

Historical evidence retains its original filenames, remote paths, and hashes.
The relocation index translates those original local names without rewriting
the recorded evidence or the contents of preservation archives.
"""
from functools import lru_cache
import fnmatch
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@lru_cache(maxsize=1)
def _paths():
    return json.loads((ROOT / 'data/repository_layout.json').read_text(encoding='utf-8'))['top_level_paths']


def project_root(filename=None):
    """Return the repository root, independently of the invoking directory."""
    return ROOT


def project_path(name='', *, base=None):
    """Resolve an original local path; absolute and non-root paths stay literal.

    Existing relocated paths use the exact index. New root outputs are routed
    by type, so rerunning a report or collector does not clutter the root.
    """
    base = ROOT if base is None else Path(base)
    path = Path(name)
    if path.is_absolute() or base != ROOT:
        return base / path
    normalized = str(name).replace('\\', '/')
    if normalized in ('', '.'):
        return ROOT
    first, slash, rest = normalized.partition('/')
    paths = _paths()
    if first in paths:
        return ROOT / paths[first] / rest if slash else ROOT / paths[first]
    if first in {'scripts', 'docs', 'data', 'archives', 'hutter_research', 'tests'}:
        return ROOT / path
    if first.startswith('.') or first in {'README.md', 'LICENSE', 'LICENSE.md'}:
        return ROOT / path
    suffix = Path(first).suffix.lower()
    if suffix in {'.py', '.mjs', '.ps1', '.cpp', '.h', '.exe'}:
        folder = 'scripts'
    elif suffix in {'.zip', '.gz', '.zlib', '.7z', '.tar', '.bz2', '.xz'} or 'extended_parts' in first:
        folder = 'archives'
    elif suffix in {'.md', '.txt'} and 'decoded' not in first:
        folder = 'docs'
    elif suffix or first.startswith('research_round'):
        folder = 'data'
    else:
        return ROOT / path
    return ROOT / folder / path


def project_glob(pattern, *, base=None):
    """Find files using a root pattern written for the original flat layout."""
    base = ROOT if base is None else Path(base)
    if base != ROOT:
        yield from base.glob(pattern)
        return
    if '/' in pattern.replace('\\', '/'):
        first, _, tail = pattern.replace('\\', '/').partition('/')
        if not any(c in first for c in '*?['):
            yield from project_path(first).glob(tail)
            return
    seen = set()
    for logical, physical in _paths().items():
        if fnmatch.fnmatchcase(logical, pattern):
            candidate = ROOT / physical
            if candidate.exists() and candidate not in seen:
                seen.add(candidate)
                yield candidate
    # Include files generated since the reorganization and stable root packages.
    for folder in (ROOT, ROOT / 'scripts', ROOT / 'docs', ROOT / 'data', ROOT / 'archives'):
        for candidate in folder.glob(pattern):
            if candidate not in seen:
                seen.add(candidate)
                yield candidate


def project_iterdir(*, base=None):
    """Iterate the original logical root using relocated physical paths."""
    base = ROOT if base is None else Path(base)
    if base != ROOT:
        yield from base.iterdir()
        return
    seen = set()
    for physical in _paths().values():
        candidate = ROOT / physical
        if candidate.exists() and candidate not in seen:
            seen.add(candidate)
            yield candidate
    for candidate in ROOT.iterdir():
        if candidate.name not in {'scripts', 'docs', 'data', 'archives'} and candidate not in seen:
            yield candidate
