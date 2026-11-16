"""Audit the selected fast-stream annotations without reading audio."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import re
import numpy as np
from chordrec.idmt import load_chords
from chordrec.data import reduce_label

ROOT=Path('/home/cx/Documents/csc475/Proj')
DATA=ROOT/'docs/datasets/IDMT-SMT-Guitar'
OUT=Path('/tmp/chordrec_root_fast')
archive=json.loads((DATA/'archive_members.json').read_text())
metadata={r['archive_path']:r for r in json.loads((DATA/'metadata_sources.json').read_text())['files']}
annotations={}
audio={}
for tempo in ('slow','fast'):
    prefix=f'IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/{tempo}/'
    annotations[tempo]={Path(r['name']).stem.rsplit('_',1)[0]:r for r in archive if r['name'].startswith(prefix) and '/annotation/chords/' in r['name'] and r['name'].endswith('.csv')}
    audio[tempo]={Path(r['name']).stem.rsplit('_',1)[0]:r for r in archive if r['name'].startswith(prefix) and r['name'].endswith('.wav')}
assert annotations['fast'].keys()==annotations['slow'].keys()==audio['fast'].keys()==audio['slow'].keys()
assert len(annotations['fast'])==64
records=[]
for piece in sorted(annotations['fast']):
    paths={t:DATA/annotations[t][piece]['name'] for t in ('slow','fast')}
    for tempo,path in paths.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest()==metadata[annotations[tempo][piece]['name']]['sha256']
    reference,symbols=load_chords(paths['fast'])
    _,slow_symbols=load_chords(paths['slow'])
    normalized=[(a,b,reduce_label(c)) for a,b,c in reference]
    duration=collections.defaultdict(float)
    for a,b,c in normalized:
        duration['unsupported' if c is None else 'N' if c=='N' else 'chord']+=b-a
    supported_changes=sum(c!=f for (a,b,c),(d,e,f) in zip(normalized[:-1],normalized[1:]) if c is not None and f is not None and abs(b-d)<1e-8)
    chord_changes=sum(c!=f for (a,b,c),(d,e,f) in zip(normalized[:-1],normalized[1:]) if c not in (None,'N') and f not in (None,'N') and abs(b-d)<1e-8)
    beats={}
    for tempo,path in paths.items():
        lines=[r.strip() for r in path.read_text(encoding='utf-8-sig').splitlines() if r.strip()][:-3]
        beats[tempo]={r.split(',',1)[1].split(':')[0].strip():float(r.split(',',1)[0]) for r in lines}
    samekeys=list(beats['fast'])==list(beats['slow'])
    residual=None
    if samekeys:
        x=np.array(list(beats['slow'].values()));y=np.array(list(beats['fast'].values()))
        design=np.column_stack([x,np.ones_like(x)])
        coefficients=np.linalg.lstsq(design,y,rcond=None)[0]
        residual=float(np.max(np.abs(y-design@coefficients)))
    records.append(dict(piece_id=piece,annotation_archive_path=annotations['fast'][piece]['name'],audio_archive_path=audio['fast'][piece]['name'],annotation_sha256=hashlib.sha256(paths['fast'].read_bytes()).hexdigest(),audio_member_bytes=audio['fast'][piece]['size'],audio_compressed_bytes=audio['fast'][piece]['compressed_size'],audio_member_crc32=audio['fast'][piece]['crc32'],first_beat=reference[0][0],last_beat=reference[-1][1],reference_span_seconds=reference[-1][1]-reference[0][0],chord_seconds=duration['chord'],N_seconds=duration['N'],unsupported_seconds=duration['unsupported'],supported_label_changes=supported_changes,chord_to_different_chord_changes=chord_changes,fast_bpm=int(re.search(r'_(\d+)BPM',paths['fast'].name)[1]),slow_bpm=int(re.search(r'_(\d+)BPM',paths['slow'].name)[1]),same_raw_symbol_sequence=symbols==slow_symbols,same_beat_keys=samekeys,max_affine_timing_residual_seconds=residual,reference_intervals=reference))
result=dict(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Metadata-only audit before any fast-stream audio reading or prediction.',records=records,recordings=64,annotation_parse_issues=[],fast_slow_piece_id_overlap=64,fast_tempi_all_greater=all(r['fast_bpm']>r['slow_bpm'] for r in records),fast_audio_files_present_at_initial_inspection=0,fast_audio_files_read=0,model_runs=0,source_annotation_hashes_verified=128,reference_policy='Use each fast CSV from first through last annotated beat; keep the existing NC-to-N and unknown-to-X conventions.',totals={k:sum(r[k] for r in records) for k in ['reference_span_seconds','chord_seconds','N_seconds','unsupported_seconds','supported_label_changes','chord_to_different_chord_changes','audio_member_bytes','audio_compressed_bytes']},recordings_with_supported_label_changes=sum(r['supported_label_changes']>0 for r in records),recordings_with_chord_to_chord_changes=sum(r['chord_to_different_chord_changes']>0 for r in records),zero_scoreable_piece_ids=[r['piece_id'] for r in records if r['chord_seconds']+r['N_seconds']==0],same_raw_symbol_sequences=sum(r['same_raw_symbol_sequence'] for r in records),same_beat_key_sequences=sum(r['same_beat_keys'] for r in records),alignment_status='CSV times are finite and strictly increasing. Audio-duration containment, temporal agreement with the audio and waveform-processing provenance have not been verified.',source_reading_notes='source_audit.md')
path=OUT/'metadata_preflight.json'
if path.exists():raise FileExistsError(path)
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
