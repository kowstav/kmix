"""Validate a pulled kernel before reusing an existing private CPU reference."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import urlparse


def parse_successful_push(stdout, owner):
    """CLI exit zero does not imply API success in Kaggle 2.0.2.

    Persist only the verified public resource URL/ref and version. Never retain
    raw CLI output, which may contain authentication diagnostics.
    """
    if 'Kernel push error:' in stdout or 'Kernel push error: see previous output' in stdout:
        raise ValueError('CLI reported a notebook API rejection')
    if any(word in stdout for word in ['not valid dataset sources','not valid kernel sources','not valid competition sources']):
        raise ValueError('CLI did not attach every declared input')
    matches=re.findall(r'Kernel version (?:([0-9]+) )?successfully pushed\.\s+Please check progress at (https://[^\s]+)',stdout)
    if len(matches)!=1: raise ValueError('CLI success resource was not verified')
    version,url=matches[0]; parsed=urlparse(url)
    if parsed.hostname not in ['kaggle.com','www.kaggle.com'] or parsed.query or parsed.fragment:
        raise ValueError('Unexpected notebook resource URL')
    parts=parsed.path.strip('/').split('/')
    if len(parts)!=3 or parts[:2]!=['code',owner] or not re.fullmatch('[a-z0-9-]+',parts[2]):
        raise ValueError('Unexpected notebook owner or slug')
    return {'actual_ref':owner+'/'+parts[2],'url':url,'version':int(version) if version else None}


def normalized_source(raw):
    # Kaggle may change transport line endings. No other text is discarded.
    return raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")


def validate_existing_kernel(folder, expected_metadata, expected_source):
    folder = Path(folder)
    actual = json.loads((folder / "kernel-metadata.json").read_text(encoding="utf-8"))
    for key in ["id", "language", "kernel_type"]:
        if actual.get(key) != expected_metadata[key]:
            raise ValueError("existing kernel differs: " + key)
    for key, value in {"is_private": True, "enable_gpu": False,
                       "enable_tpu": False, "enable_internet": False}.items():
        if actual.get(key) is not value:
            raise ValueError("existing kernel has unverified privacy/resource setting: " + key)
    for key in ["dataset_sources", "competition_sources", "kernel_sources"]:
        if sorted(actual.get(key, [])) != sorted(expected_metadata[key]):
            raise ValueError("existing kernel has different inputs: " + key)
    code = (folder / actual["code_file"]).resolve()
    if not code.is_relative_to(folder.resolve()):
        raise ValueError("existing code path escapes verification directory")
    raw = code.read_bytes()
    if normalized_source(raw) != normalized_source(expected_source):
        raise ValueError("existing kernel source differs; preserve and choose a new versioned ref")
    return {"physical_source_sha256": hashlib.sha256(raw).hexdigest(),
            "normalized_source_sha256": hashlib.sha256(normalized_source(raw)).hexdigest(),
            "comparison": "exact UTF-8 source allowing only CRLF/LF transport normalization",
            "metadata_checked": True}
