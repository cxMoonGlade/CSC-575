"""Download the 64 selected recordings and verify individual ZIP members."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,sys,time,wave,zipfile,zlib
from acquire_idmt import HTTPRangeFile,URL,SIZE,BASE,OUT
def acquire(entry):
    dest=(OUT/entry['archive_path']).resolve()
    if not dest.is_relative_to(OUT.resolve()):
        raise ValueError('Archive member is outside the output directory')
    for attempt in range(3):
        try:
            if dest.exists():
                data=dest.read_bytes();transferred=0
            else:
                remote=HTTPRangeFile()
                with zipfile.ZipFile(remote) as archive: data=archive.read(entry['archive_path'])
                transferred=remote.transferred
                dest.parent.mkdir(parents=True,exist_ok=True)
                temporary=dest.with_suffix('.wav.part');temporary.write_bytes(data);temporary.replace(dest)
            if len(data)!=entry['file_bytes'] or f'{zlib.crc32(data)&0xffffffff:08x}'!=entry['crc32']:
                raise RuntimeError('Member size/CRC mismatch')
            with wave.open(str(dest),'rb') as audio:
                meta=dict(sample_rate=audio.getframerate(),channels=audio.getnchannels(),sample_width=audio.getsampwidth(),frames=audio.getnframes(),duration_seconds=audio.getnframes()/audio.getframerate())
            return dict(**entry,local_path=str(dest.relative_to(OUT)),sha256=hashlib.sha256(data).hexdigest(),crc_verified=True,range_bytes_downloaded=transferred,**meta)
        except Exception:
            if attempt==2: raise
            time.sleep(1+attempt)


def main():
    selection=json.loads((OUT/'prospective_selection.json').read_text())
    assert selection['capture_stream']=='acoustic_mic' and selection['tempo_branch']=='slow'
    entries=selection['recordings'];assert len(entries)==64
    if (OUT/'audio_sources.json').exists():
        raise FileExistsError('Preserve the existing audio manifest')
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(acquire,e):e for e in entries}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            if len(results)%8==0 or len(results)==len(entries): print('Saved audio',len(results),'/',len(entries),flush=True)
    results.sort(key=lambda r:r['piece_id'])
    manifest=dict(source_url=URL,official_dataset_url='https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html',license='CC BY-NC-ND 4.0',archive_bytes=SIZE,published_full_archive_md5='06796e08731bccffaed6ae59361486e4',full_archive_md5_verified=False,verification='Only selected HTTP byte ranges were retrieved. Every selected member passed ZIP CRC32 validation; per-file SHA256 values and WAV headers are recorded. The full archive hash was not verified.',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),selection_rule_file='prospective_selection.json',recordings=results,total_recordings=len(results),total_audio_seconds=sum(r['duration_seconds'] for r in results),total_range_bytes=sum(r['range_bytes_downloaded'] for r in results),algorithm_results_inspected=False)
    (OUT/'audio_sources.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['total_recordings','total_audio_seconds','total_range_bytes','full_archive_md5_verified']},indent=2))


if __name__ == "__main__":
    main()
