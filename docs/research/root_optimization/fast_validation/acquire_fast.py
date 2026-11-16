"""Freeze the complete fast-stream selection, then acquire checked WAV members."""
from pathlib import Path, PurePosixPath
import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import io
import json
import math
import shutil
import stat
import sys
import threading
import time
import urllib.error
import wave
import zipfile
import zlib
from email.utils import parsedate_to_datetime

ROOT = Path('/home/cx/Documents/csc475/Proj')
SOURCE = ROOT / 'docs/datasets/IDMT-SMT-Guitar'
OUTPUT = ROOT / 'docs/datasets/IDMT-SMT-Guitar-fast'
WORK = Path('/tmp/chordrec_root_fast')
CACHE = Path('/tmp/chordrec_opt2')
HELPER = ROOT / 'experiments/optimization_v2/data_sources/acquire_idmt.py'
PREFIX = 'IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/fast/'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def safe_path(base, member):
    relative = PurePosixPath(member)
    if relative.is_absolute() or '..' in relative.parts or '\\' in member:
        raise ValueError('Unsafe archive member path')
    destination = (base / member).resolve()
    if not destination.is_relative_to(base.resolve()):
        raise ValueError('Archive member escapes the data directory')
    return destination


def load_helper():
    original = sys.argv
    try:
        sys.argv = [str(HELPER), '--data-dir', str(OUTPUT), '--range-cache-dir', str(CACHE)]
        spec = importlib.util.spec_from_file_location('fast_range_source', HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.argv = original
    return module


def cached_inventory(helper):
    for name, size in (('idmt_zip_tail.bin', 100000), ('idmt_zip_central.bin', 703155)):
        if (CACHE / name).stat().st_size != size:
            raise ValueError('Expected existing ZIP-directory cache')
    class OfflineRange(helper.HTTPRangeFile):
        def read(self, length=-1):
            if length < 0:
                length = helper.SIZE - self.position
            end = min(self.position + length, helper.SIZE)
            if not any(offset <= self.position and end <= offset + len(data) for offset, data in self.cache):
                raise RuntimeError('Offline inventory requested an uncached range')
            return super().read(length)
    remote = OfflineRange()
    with zipfile.ZipFile(remote) as archive:
        infos = {item.filename: item for item in archive.infolist()}
    assert remote.transferred == 0
    return infos


def prepare():
    if (OUTPUT / 'prospective_selection.json').exists():
        raise FileExistsError('Preserve the existing prospective selection')
    helper = load_helper()
    infos = cached_inventory(helper)
    original_inventory = {row['name']: row for row in json.loads((SOURCE / 'archive_members.json').read_text())}
    selected = sorted((info for name, info in infos.items() if name.startswith(PREFIX) and name.endswith('.wav')), key=lambda info: info.filename)
    if len(selected) != 64:
        raise ValueError('The complete acoustic microphone fast stream must contain 64 WAV files')
    entries = []
    for info in selected:
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ValueError('Symlink archive member')
        known = original_inventory[info.filename]
        if (info.file_size, info.compress_size, info.header_offset, f'{info.CRC:08x}') != (known['size'], known['compressed_size'], known['header_offset'], known['crc32']):
            raise ValueError('Cached ZIP directory differs from the saved inventory')
        audio = PurePosixPath(info.filename)
        annotation = str(audio.parent.parent / 'annotation/chords' / (audio.stem + '.csv'))
        annotation_info = infos[annotation]
        if stat.S_ISLNK(annotation_info.external_attr >> 16):
            raise ValueError('Symlink annotation member')
        source_annotation = safe_path(SOURCE, annotation)
        contents = source_annotation.read_bytes()
        if len(contents) != annotation_info.file_size or zlib.crc32(contents) & 0xffffffff != annotation_info.CRC:
            raise ValueError('Existing annotation differs from its ZIP member')
        entries.append(dict(piece_id=audio.stem.rsplit('_', 1)[0], archive_path=info.filename,
                            file_bytes=info.file_size, compressed_bytes=info.compress_size,
                            header_offset=info.header_offset, crc32=f'{info.CRC:08x}', annotation=annotation,
                            annotation_sha256=hashlib.sha256(contents).hexdigest(),
                            annotation_crc32=f'{annotation_info.CRC:08x}'))
    ids = {entry['piece_id'] for entry in entries}
    previous = json.loads((SOURCE / 'prospective_selection.json').read_text())
    if len(ids) != 64 or ids != {row['piece_id'] for row in previous['recordings']}:
        raise ValueError('Expected the same 64 piece identifiers as the slow stream')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    selection = dict(selected_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     dataset='IDMT-SMT-Guitar V2 ZIP (Zenodo version 1.0.0)', source_url=helper.URL,
                     archive_bytes=helper.SIZE, capture_stream='acoustic_mic', tempo_branch='fast',
                     rule='Include every WAV in dataset4/acoustic_mic/fast. Do not select by labels, coverage or recognizer scores.',
                     scope='The same 64 pieces as the previous slow-stream comparison, performed at the fast tempo. This checks transfer within the existing repertoire.',
                     source_inventory_sha256=digest(SOURCE / 'archive_members.json'),
                     cached_directory_sha256=digest(CACHE / 'idmt_zip_central.bin'),
                     cached_tail_sha256=digest(CACHE / 'idmt_zip_tail.bin'),
                     evaluation_plan_sha256=digest(WORK / 'plan.json'),
                     recordings=entries, audio_download_started=False, algorithm_results_inspected=False)
    save(OUTPUT / 'prospective_selection.json', selection)
    selection_hash = digest(OUTPUT / 'prospective_selection.json')
    save(WORK / 'acquisition_plan.json', dict(created_at_utc=selection['selected_at_utc'],
         source_selection_sha256=selection_hash, source_evaluation_plan_sha256=digest(WORK / 'plan.json'),
         concurrency=2, policy='Require checked HTTP ranges, ZIP CRC32 and per-file SHA256. Retain all 64 pieces. Do not run recognition.',
         helper_sha256=digest(HELPER), acquisition_script_sha256=digest(__file__),
         annotation_policy='Use existing load_chords on fast annotation files. NC maps to N; unknown symbols remain X; no prefix or tail extrapolation.'))
    copied = []
    for entry in entries:
        source = safe_path(SOURCE, entry['annotation'])
        target = safe_path(OUTPUT, entry['annotation'])
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != entry['annotation_sha256']:
            raise FileExistsError('Existing target annotation has different contents')
        shutil.copyfile(source, target)
        copied.append(dict(annotation=entry['annotation'], sha256=digest(target), crc32=entry['annotation_crc32'], source=str(source)))
    save(OUTPUT / 'metadata_sources.json', dict(source_selection_sha256=selection_hash, network_bytes_downloaded=0,
         source='Existing checked IDMT metadata; copied byte-for-byte after verifying ZIP CRC32.', files=copied))
    shutil.copyfile(OUTPUT / 'prospective_selection.json', WORK / 'prospective_selection.json')
    print(json.dumps(dict(recordings=64, source_selection_sha256=selection_hash,
                          compressed_audio_bytes=sum(entry['compressed_bytes'] for entry in entries),
                          copied_annotations=len(copied), audio_downloaded=False)), flush=True)


def download(expected_hash):
    helper = load_helper()
    selection_path = OUTPUT / 'prospective_selection.json'
    if digest(selection_path) != expected_hash:
        raise ValueError('Prospective selection hash changed')
    plan = json.loads((WORK / 'acquisition_plan.json').read_text())
    if plan['source_selection_sha256'] != expected_hash or plan['source_evaluation_plan_sha256'] != digest(WORK / 'plan.json'):
        raise ValueError('Plans changed after selection')
    if plan['helper_sha256'] != digest(HELPER) or plan['acquisition_script_sha256'] != digest(__file__):
        raise ValueError('Acquisition code changed after selection')
    selection = json.loads(selection_path.read_text())
    entries = selection['recordings']
    if len(entries) != 64 or selection['tempo_branch'] != 'fast':
        raise ValueError('Unexpected recording selection')
    if (OUTPUT / 'audio_sources.json').exists() or (OUTPUT / 'validation_manifest.json').exists():
        raise FileExistsError('Preserve the completed acquisition manifests')
    lock = threading.Lock()
    retries = []
    class RetryingRange(helper.HTTPRangeFile):
        def read(self, length=-1):
            for attempt in range(8):
                try:
                    return super().read(length)
                except urllib.error.HTTPError as error:
                    if error.code not in (429, 500, 502, 503, 504) or attempt == 7:
                        raise
                    delay = min(60., 2. ** (attempt + 1))
                    header = error.headers.get('Retry-After')
                    if header:
                        try:
                            delay = max(delay, float(header))
                        except ValueError:
                            try:
                                delay = max(delay, parsedate_to_datetime(header).timestamp()-time.time())
                            except (ValueError, TypeError):
                                pass
                    with lock:
                        retries.append(dict(status=error.code, attempt=attempt+1, delay_seconds=delay, position=self.position))
                        save(WORK / 'network_retries.json', retries)
                    time.sleep(max(0., delay))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    def acquire(entry):
        destination = safe_path(OUTPUT, entry['archive_path'])
        remote = None
        if destination.exists():
            data = destination.read_bytes()
        else:
            remote = RetryingRange()
            with zipfile.ZipFile(remote) as archive:
                data = archive.read(entry['archive_path'])
        if len(data) != entry['file_bytes'] or f'{zlib.crc32(data) & 0xffffffff:08x}' != entry['crc32']:
            raise ValueError('Downloaded WAV size or CRC differs from the prospective selection')
        with wave.open(io.BytesIO(data), 'rb') as audio:
            sample_rate, frames = audio.getframerate(), audio.getnframes()
            if sample_rate <= 0 or frames <= 0 or audio.getnchannels() <= 0:
                raise ValueError('WAV header must describe positive-duration audio')
            metadata = dict(sample_rate=sample_rate, frames=frames, channels=audio.getnchannels(),
                            sample_width=audio.getsampwidth(), duration_seconds=frames/sample_rate)
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix('.wav.part')
            temporary.write_bytes(data)
            temporary.replace(destination)
        return dict(**entry, sha256=hashlib.sha256(data).hexdigest(), crc_verified=True,
                    range_bytes_downloaded=remote.transferred if remote is not None else 0, **metadata)
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(acquire, entry): entry for entry in entries}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            save(WORK / 'acquisition_progress.json', dict(completed=len(results), recordings=sorted(results, key=lambda r:r['piece_id'])))
            print(f'Checked WAVs: {len(results)}/64', flush=True)
    results.sort(key=lambda row:row['piece_id'])
    sys.path.insert(0, str(ROOT))
    from chordrec.idmt import load_chords
    validation = []
    for row in results:
        annotation = safe_path(OUTPUT, row['annotation'])
        if digest(annotation) != row['annotation_sha256']:
            raise ValueError('Copied annotation changed during acquisition')
        reference, _ = load_chords(annotation)
        previous_end = 0.
        for start, end, label in reference:
            if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end <= row['duration_seconds'] + 1e-8 and start >= previous_end - 1e-8):
                raise ValueError(f"Invalid reference extent: {row['piece_id']}")
            previous_end = end
        validation.append(dict(piece_id=row['piece_id'], audio=row['archive_path'], annotation=row['annotation'],
                               audio_sha256=row['sha256'], annotation_sha256=row['annotation_sha256'],
                               duration_seconds=row['duration_seconds'], reference=reference))
    save(OUTPUT / 'audio_sources.json', dict(source_url=helper.URL, archive_bytes=helper.SIZE,
         source_selection_sha256=expected_hash, started_at_utc=started,
         completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         full_archive_md5_verified=False, verification='Selected members passed ZIP CRC32; per-file SHA256 values and WAV headers were checked. The full archive was not downloaded or hashed.',
         concurrency=2, retry_events=retries, recordings=results, total_recordings=64,
         total_audio_seconds=sum(row['duration_seconds'] for row in results), total_range_bytes=sum(row['range_bytes_downloaded'] for row in results), algorithm_results_inspected=False))
    save(OUTPUT / 'validation_manifest.json', dict(source_selection_sha256=expected_hash,
         source_loader_sha256=digest(ROOT / 'chordrec/idmt.py'), recordings=validation,
         recording_count=len(validation), annotation_policy=plan['annotation_policy'], recognition_performed=False))
    print(json.dumps(dict(recordings=64, audio_seconds=sum(row['duration_seconds'] for row in results),
                         source_selection_sha256=expected_hash, validation_manifest=str(OUTPUT / 'validation_manifest.json'), retries=len(retries))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'download'))
    parser.add_argument('--selection-sha256')
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    else:
        if not args.selection_sha256:
            parser.error('download requires the previously saved --selection-sha256')
        download(args.selection_sha256)
