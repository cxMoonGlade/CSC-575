"""Record the fixed acoustic-microphone selection and download subset-4 metadata."""
from pathlib import Path
import datetime,hashlib,json,stat,sys,zipfile
from acquire_idmt import HTTPRangeFile,URL,SIZE,BASE,OUT


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/"prospective_selection.json").exists():
        raise FileExistsError("Preserve the existing selection; use its audio-download command or choose a fresh data directory")
    remote=HTTPRangeFile()
    with zipfile.ZipFile(remote) as archive:
        allinfo=archive.infolist()
        audio=[i for i in allinfo if '/dataset4/' in i.filename and i.filename.lower().endswith('.wav')]
        selected=sorted([i for i in audio if '/dataset4/acoustic_mic/slow/' in i.filename],key=lambda i:i.filename)
        assert len(selected)==64
        piece_ids=[Path(i.filename).stem.rsplit('_',1)[0] for i in selected]
        assert len(set(piece_ids))==64
        selection=dict(selected_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),dataset='IDMT-SMT-Guitar V2 ZIP (Zenodo version1.0.0)',source_url=URL,archive_bytes=SIZE,rule='Choose the case-insensitive lexicographically first capture-stream directory having all 64 piece IDs in its slow-tempo branch. Choose that slow branch. Do not select by labels, coverage, or algorithm scores.',capture_stream='acoustic_mic',tempo_branch='slow',recordings=[dict(piece_id=piece_id,archive_path=i.filename,file_bytes=i.file_size,compressed_bytes=i.compress_size,crc32=f'{i.CRC:08x}') for piece_id,i in zip(piece_ids,selected)],scope='Include all 64 selected recordings regardless of scoreable-label coverage. acoustic_mic and acoustic_pickup capture the same acoustic guitar.',algorithm_results_inspected=False)
        (OUT/'prospective_selection.json').write_text(json.dumps(selection,indent=2)+'\n')
        docs=[i for i in allinfo if i.filename.endswith('SMT_GUITAR_dataset_description.pdf')]
        small=[i for i in allinfo if '/dataset4/' in i.filename and not i.is_dir() and not i.filename.lower().endswith('.wav')]
        requested=docs+small
        print('Small files:',len(requested),'compressed bytes:',sum(i.compress_size for i in requested),flush=True)
        manifest=[]
        for count,i in enumerate(requested,1):
            dest=(OUT/i.filename).resolve()
            if not dest.is_relative_to(OUT.resolve()) or stat.S_ISLNK(i.external_attr>>16): raise RuntimeError('Unsafe path')
            data=archive.read(i) # zipfile verifies CRC on every member.
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
            manifest.append(dict(archive_path=i.filename,local_path=str(dest.relative_to(OUT)),bytes=len(data),crc32=f'{i.CRC:08x}',crc_verified=True,sha256=hashlib.sha256(data).hexdigest(),compressed_bytes=i.compress_size,header_offset=i.header_offset))
            if count%200==0 or count==len(requested): print('Saved metadata',count,'/',len(requested),'range bytes',remote.transferred,flush=True)
        (OUT/'metadata_sources.json').write_text(json.dumps(dict(source_url=URL,archive_bytes=SIZE,archive_full_md5_verified=False,validation='Each ZIP member passed CRC32 validation during decompression; per-file SHA256 values are recorded. The full archive MD5 was not verified because only byte ranges were retrieved.',retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),network_bytes_this_run=remote.transferred,files=manifest),indent=2)+'\n')


if __name__ == "__main__":
    main()
