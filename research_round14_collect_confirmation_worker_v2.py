"""Snapshot terminal confirmation/interaction jobs; never submit or retry jobs.

Version 2 (10 October 2026) only adds explicit joint-confirmation selectors:
--wave joint-a / joint-b select chaoscpp/hutter-r14-guard-match-confirm-{a,b}-v1.
--wave combo still selects joint DEVELOPMENT and must not be relabelled as confirmation.
All download, containment, hash, inverse-claim, disk-reserve and CRC checks are unchanged.

Run on Kaggle: python3 this_file.py --wave a --tag a-YYYYMMDD-HHMM
Use a new tag for a later snapshot. Nonterminal jobs are left untouched.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
import traceback
import zipfile


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate_cases(root, manifest):
    """Check saved archive hashes and claimed inverse evidence, not re-decode."""
    checked = []
    for region in manifest.get('regions', []):
        for case in region.get('cases', []):
            if 'archive_sha256' not in case:
                continue
            matches = [p for p in root.rglob('*.cmx')
                       if p.stat().st_size == case['archive_bytes']
                       and digest(p) == case['archive_sha256']]
            if not matches:
                raise ValueError('archive absent or changed: ' + case['archive_sha256'])
            if case.get('exact_independent_inverse') is not True:
                raise ValueError('case has no exact independent inverse claim')
            checked.append({'region': case['region'], 'mode': case['mode'],
                            'sha256': case['archive_sha256'],
                            'matched_files': [str(p.relative_to(root)) for p in matches]})
    return checked


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wave', required=True, choices=('a', 'b', 'combo', 'joint-a', 'joint-b'))
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.tag):
        parser.error('tag must be a unique lowercase alphanumeric/hyphen name')
    from kaggle.api.kaggle_api_extended import KaggleApi, ApiListKernelSessionOutputRequest
    import requests

    work = Path('/kaggle/working/hp_round14')
    scratch = Path('/root') / ('r14_confirmation_collection_' + args.tag)
    record = work / ('confirmation_collection_' + args.tag + '.json')
    bundle = work / ('confirmation_compact_' + args.tag + '.zip')
    if any(p.exists() for p in (scratch, record, bundle)):
        raise FileExistsError('tag already used; inspect existing evidence before a new snapshot')
    scratch.mkdir()
    status = {'status': 'CHECKING_EXISTING_JOBS', 'wave': args.wave,
              'started': time.time(), 'jobs': [], 'deletions': [],
              'launches': 0, 'archive_verification': 'hash and recorded inverse, not a new decode'}

    def save():
        temporary = record.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(status, indent=2))
        temporary.replace(record)

    save()
    try:
        arms = ('prune-word', 'prune-match', 'prune-indirect', 'output-fp32')
        if args.wave == 'combo':
            slugs = ['hutter-r14-guard-match-development-v1']
        elif args.wave in ('joint-a', 'joint-b'):
            slugs = ['hutter-r14-guard-match-confirm-' + args.wave[-1] + '-v1']
        else:
            slugs = ['hutter-r14-' + a + '-confirm-' + args.wave + '-v1' for a in arms]
        status['collector_version'] = 'v2-explicit-joint-confirmation-selector'
        status['selected_refs'] = ['chaoscpp/' + s for s in slugs]
        api = KaggleApi()
        api.authenticate()
        for slug in slugs:
            ref = 'chaoscpp/' + slug
            response = subprocess.run(['kaggle', 'kernels', 'status', ref],
                                      capture_output=True, text=True, timeout=30)
            states = re.findall(r'KernelWorkerStatus\.([A-Z]+)', response.stdout)
            if response.returncode or len(states) != 1:
                raise RuntimeError('unverified status for ' + ref + '; no launch performed')
            state = states[0]
            row = {'ref': ref, 'state': state, 'observed': time.time(), 'files': []}
            status['jobs'].append(row)
            save()
            if state not in ('COMPLETE', 'ERROR', 'CANCELLED', 'CANCELED'):
                row['collection'] = 'SKIPPED_NONTERMINAL'
                continue
            dest = scratch / slug
            dest.mkdir()
            seen, page_tokens, todo = set(), set(), []
            token, pages = None, 0
            with api.build_kaggle_client() as client:
                while True:
                    request = ApiListKernelSessionOutputRequest()
                    request.user_name, request.kernel_slug = 'chaoscpp', slug
                    request.page_size, request.page_token = 500, token
                    page = client.kernels.kernels_api_client.list_kernel_session_output(request)
                    pages += 1
                    for f in page.files or []:
                        name = f.file_name
                        if name in seen:
                            raise ValueError('duplicate listed output path')
                        seen.add(name)
                        path = (dest / name).resolve()
                        if not path.is_relative_to(dest.resolve()):
                            raise ValueError('unsafe output path')
                        if path.suffix in ('.json', '.log', '.cmx', '.txt', '.py'):
                            todo.append((f.url, path))
                    token = page.next_page_token
                    if not token:
                        break
                    if token in page_tokens:
                        raise ValueError('pagination cycle')
                    page_tokens.add(token)

            def download(item):
                url, path = item
                path.parent.mkdir(parents=True, exist_ok=True)
                with requests.get(url, stream=True, timeout=(20, 120)) as r:
                    r.raise_for_status()
                    with path.open('xb') as f:
                        for block in r.iter_content(1024 * 1024):
                            f.write(block)
                return {'path': str(path.relative_to(scratch)),
                        'bytes': path.stat().st_size, 'sha256': digest(path)}

            with ThreadPoolExecutor(4) as pool:
                row['files'] = list(pool.map(download, todo))
            row.update(listed_files=len(seen), pages=pages,
                       omitted_noncompact_files=len(seen) - len(todo))
            manifests = list(dest.rglob('manifest.json'))
            if state == 'COMPLETE' and len(manifests) != 1:
                raise ValueError('expected one complete experiment manifest for ' + ref)
            if len(manifests) == 1:
                manifest = json.loads(manifests[0].read_text())
                row.update(experiment_status=manifest.get('status'),
                           manifest_sha256=digest(manifests[0]),
                           verified_cases=validate_cases(dest, manifest))
                if state == 'COMPLETE' and not row['verified_cases']:
                    raise ValueError('completed job has no verified native archives')
            row['collection'] = 'COLLECTED_TERMINAL_OUTPUT'
            save()

        entries = [e for row in status['jobs'] for e in row['files']]
        if entries:
            required = sum(e['bytes'] for e in entries) + 20 * 1024 * 1024
            if shutil.disk_usage(work).free < required:
                raise OSError('insufficient durable disk for conservative ZIP bound; scratch retained')
            with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=3) as z:
                for entry in entries:
                    path = scratch / entry['path']
                    if digest(path) != entry['sha256']:
                        raise ValueError('download changed before packaging')
                    z.write(path, entry['path'])
                z.writestr('entries.json', json.dumps(entries, indent=2))
            with zipfile.ZipFile(bundle) as z:
                if z.testzip() is not None:
                    raise ValueError('ZIP CRC failure')
            status['compact'] = {'path': str(bundle), 'bytes': bundle.stat().st_size,
                                 'sha256': digest(bundle), 'entries': len(entries)}
        all_terminal = all(r.get('collection') == 'COLLECTED_TERMINAL_OUTPUT'
                           for r in status['jobs'])
        status.update(status=('TERMINAL_WAVE_SNAPSHOT' if all_terminal else
                              'PARTIAL_SNAPSHOT_NONTERMINAL_JOBS_UNTOUCHED'), finished=time.time())
        save()
        print(json.dumps({'status': status['status'], 'record': str(record),
                          'compact': status.get('compact')}))
    except BaseException as error:
        status.update(status='FAIL_PRESERVED_NO_RETRY', error=repr(error),
                      traceback=traceback.format_exc())
        save()
        raise


if __name__ == '__main__':
    run()
