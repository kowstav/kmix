"""Submit the six authorized private CPU jobs once, respecting ordinary quotas.

Run only after the asset worker reports COMPLETE. The CLI token stays in the
runtime environment. Neither stderr nor any credential is copied into results.
"""

# Resolve local assets after the repository directory reorganization.
try:
    if __package__ == "scripts":
        from ._workspace_layout import project_root, project_path, project_glob, project_iterdir
    else:
        from _workspace_layout import project_root, project_path, project_glob, project_iterdir
except ModuleNotFoundError as _layout_error:
    if _layout_error.name != "_workspace_layout":
        raise
    # Standalone workers retain their original layout on remote machines.
    from pathlib import Path as _LayoutPath
    def project_root(filename):
        return _LayoutPath(filename).resolve().parent
    def project_path(name="", *, base=None):
        return (base if base is not None else project_root(__file__)) / name
    def project_glob(pattern, *, base=None):
        return (base if base is not None else project_root(__file__)).glob(pattern)
    def project_iterdir(*, base=None):
        return (base if base is not None else project_root(__file__)).iterdir()

from pathlib import Path
import json
import os
import subprocess
import time
import hashlib
import re
import sys
import io
import zipfile
import csv

W = Path(os.environ.get('HP_DISPATCH_ROOT', '/kaggle/working/hp_round10'))
OUT = W / os.environ.get('HP_DISPATCH_MANIFEST', 'private_cpu_submission_manifest.json')
assert not OUT.exists(), "inspect/reuse the existing submission manifest"
assets = json.loads((W / "private_cpu_assets_manifest.json").read_text())
assert assets["status"] == "COMPLETE_PRIVATE_CPU_ASSETS_PREPARED_NOT_UPLOADED"
S = Path(assets["kernels_dir"])
sys.path.insert(0, str(S.parent / "code"))
from hutter_research.dispatch_contracts import validate_existing_kernel, parse_successful_push
DATASET = "chaoscpp/hutter-round10-private-cpu-assets-v1"
M = {"status": "AUTHENTICATING", "started": time.time(), "pid":os.getpid(), "private": True,
     "GPU": False, "paid_usd": 0, "jobs": [], "dataset": DATASET, "deletions": []}


def save():
    OUT.write_text(json.dumps(M, indent=2))


def call(arguments, timeout=180):
    result = subprocess.run(["kaggle", *arguments], capture_output=True, text=True, timeout=timeout)
    combined = result.stdout + result.stderr
    missing = result.returncode != 0 and any(text in combined.lower() for text in
        ["404", "not found", "does not exist", "could not find"])
    # Return diagnostics only to the caller. Persist no raw authentication logs.
    return result.returncode, missing, result.stdout


def owned_exists(kind, ref):
    # Kaggle 2.0.2 returns 403 from status for an absent ref. Confirm absence
    # through the authenticated owner's listing rather than treating 403 as 404.
    code, _, output = call([kind, 'list', '--mine', '--search', ref.split('/',1)[1], '--csv'])
    assert code == 0, 'authenticated owned-ref inventory inaccessible; stop before writes'
    lines = output.splitlines()
    starts = [i for i,line in enumerate(lines) if line.startswith('ref,')]
    if not starts:
        assert any(message in output.lower() for message in ['no datasets found','no kernels found','no results found']) or any(line.strip()=='Not found' for line in lines), 'unknown owned-list schema'
        return False
    rows = list(csv.DictReader(lines[starts[0]:]))
    assert len(rows) < 20, 'filtered inventory may be paginated; inspect before inferring absence'
    return any(row['ref'] == ref for row in rows)


try:
    if not os.environ.get("KAGGLE_API_TOKEN"):
        from kaggle_secrets import UserSecretsClient
        os.environ["KAGGLE_API_TOKEN"] = UserSecretsClient().get_secret("KAGGLE_API_TOKEN")
    save()
    if not owned_exists('datasets', DATASET):
        code, _, _ = call(["datasets", "create", "-p", assets["upload_dir"]], timeout=1200)
        assert code == 0, "private dataset creation rejected; do not retry or bypass a limit"
        M["dataset_action"] = "CREATED_PRIVATE"
    else:
        M["dataset_action"] = "REUSED_EXISTING"
    M["status"] = "CHECKING_DATASET_AND_SUBMITTING"
    save()
    ready = False
    for pause in [0, 5, 10, 20, 30, 30, 30]:
        if pause:
            time.sleep(pause)
        code, _, output = call(["datasets", "status", DATASET])
        assert code == 0, "dataset readiness inaccessible; preserve the dispatch instead of retrying auth/quota failures"
        ready = bool(re.search(r"\b(ready|complete)\b", output, re.I))
        if ready:
            break
    assert ready, "dataset not ready within bounded backoff; resume after an external state change"
    # Reuse an existing immutable asset only after reading and verifying it.
    verify = S.parent / (OUT.stem + '_dataset_verification')
    verify.mkdir(exist_ok=False)
    code, _, _ = call(['datasets', 'download', DATASET, '-p', str(verify)], timeout=1200)
    assert code == 0, 'private dataset delivery could not be verified'
    delivered = list(verify.glob('*.zip'))
    assert len(delivered) == 1
    with zipfile.ZipFile(Path(assets['upload_dir'])/'round10_cpu_assets.zip') as reference:
        expected = json.loads(reference.read('asset_manifest.json'))
    with zipfile.ZipFile(delivered[0]) as wrapper:
        nested = [name for name in wrapper.namelist() if name.endswith('round10_cpu_assets.zip')]
        if nested:
            assert len(nested) == 1
            raw = wrapper.read(nested[0])
            assert hashlib.sha256(raw).hexdigest() == assets['asset_zip_sha256']
            archive = zipfile.ZipFile(io.BytesIO(raw))
        else:
            archive = wrapper
        manifests = [name for name in archive.namelist() if name.endswith('asset_manifest.json')]
        assert len(manifests) == 1
        metadata = json.loads(archive.read(manifests[0]))
        assert metadata == expected, 'existing asset metadata differs; do not overwrite'
        prefix = manifests[0][:-len('asset_manifest.json')]
        for name, row in metadata['files'].items():
            raw = archive.read(prefix+name)
            assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    M['delivered_assets_all_entry_SHA_verified'] = True
    M['downloaded_wrapper_preserved'] = str(delivered[0])
    save()
    for folder in sorted(S.iterdir()):
        metadata = json.loads((folder / "kernel-metadata.json").read_text())
        assert metadata["is_private"] and not metadata["enable_gpu"] and not metadata["enable_tpu"]
        ref = metadata["id"]
        if owned_exists('kernels', ref):
            # An existing version may be running or finished. Never overwrite it
            # based on an old notebook/session PID or an unchanged poll.
            verify = S.parent / ("existing_kernel_" + folder.name)
            verify.mkdir(exist_ok=False)
            pull_code, _, _ = call(["kernels", "pull", ref, "-p", str(verify), "-m"])
            assert pull_code == 0, "existing kernel source/metadata inaccessible; no assumed reuse"
            checked = validate_existing_kernel(verify, metadata, (folder / "main.py").read_bytes())
            M["jobs"].append({"id": ref, "action": "REUSED_EXISTING_SOURCE_AND_METADATA_VERIFIED", **checked})
            save()
            continue
        code, _, push_output = call(["kernels", "push", "-p", str(folder)], timeout=240)
        checked_push=None
        if code==0:
            try: checked_push=parse_successful_push(push_output,ref.split('/')[0])
            except ValueError: pass
        M["jobs"].append({"id": ref, "action": "SUBMITTED" if checked_push else "REJECTED_OR_UNVERIFIED",
                          "CLI_exit_code": code, "verified_push":checked_push})
        save()
        assert checked_push, "CPU kernel API submission rejected or unverified; respect quotas and inspect before any new write"
    M.update(status="COMPLETE_PRIVATE_CPU_SUBMISSION_DISPATCH", finished=time.time())
    save()
except BaseException as error:
    M.update(status="BLOCKED_OR_FAILED_NO_AUTOMATIC_RETRY", error_type=type(error).__name__,
             error="Credential/API/CLI or a verified dispatch gate failed; no automatic retry and no raw auth logs recorded.", finished=time.time())
    if isinstance(error, AssertionError):
        M['failed_gate'] = str(error)
    save()
    raise SystemExit("Dispatch blocked; inspect the sanitized submission manifest.") from None
