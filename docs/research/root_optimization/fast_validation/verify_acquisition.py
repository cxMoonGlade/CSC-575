from pathlib import Path
import datetime,hashlib,json,math,sys,wave,zlib
ROOT=Path('/home/cx/Documents/csc475/Proj')
DATA=ROOT/'docs/datasets/IDMT-SMT-Guitar-fast'
WORK=Path('/tmp/chordrec_root_fast')
sys.path.insert(0,str(ROOT))
from chordrec.idmt import load_chords
from chordrec.data import reduce_label
selection=json.loads((DATA/'prospective_selection.json').read_text())
audio=json.loads((DATA/'audio_sources.json').read_text())
manifest=json.loads((DATA/'validation_manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selection_hash=sha(DATA/'prospective_selection.json')
assert manifest['source_selection_sha256']==audio['source_selection_sha256']==selection_hash
assert datetime.datetime.fromisoformat(selection['selected_at_utc'])<datetime.datetime.fromisoformat(audio['started_at_utc'])
assert len(selection['recordings'])==len(audio['recordings'])==len(manifest['recordings'])==64
sources={r['piece_id']:r for r in audio['recordings']}
assert len(sources)==64
counts={'audio_seconds':0.,'annotated_span_seconds':0.,'supported_chord_seconds':0.,'n_seconds':0.,'unsupported_seconds':0.}
zero=[]
for record in manifest['recordings']:
 source=sources[record['piece_id']]
 path=DATA/record['audio']; annotation=DATA/record['annotation']
 payload=path.read_bytes()
 assert hashlib.sha256(payload).hexdigest()==source['sha256']==record['audio_sha256']
 assert f'{zlib.crc32(payload)&0xffffffff:08x}'==source['crc32']
 assert sha(annotation)==source['annotation_sha256']==record['annotation_sha256']
 with wave.open(str(path)) as w:
  duration=w.getnframes()/w.getframerate()
  assert duration==record['duration_seconds'] and duration>0
 reference,_=load_chords(annotation)
 assert [list(x) for x in reference]==record['reference']
 for a,b,label in reference:assert 0<=a<b<=duration+1e-8 and math.isfinite(a+b)
 counts['audio_seconds']+=duration
 scoreable=0.
 for a,b,label in reference:
  counts['annotated_span_seconds']+=b-a
  reduced=reduce_label(label)
  key='unsupported_seconds' if reduced is None else 'n_seconds' if reduced=='N' else 'supported_chord_seconds'
  counts[key]+=b-a
  if reduced is not None:scoreable+=b-a
 if not scoreable:zero.append(record['piece_id'])
counts['scoreable_seconds']=counts['supported_chord_seconds']+counts['n_seconds']
counts['coverage']=counts['scoreable_seconds']/counts['audio_seconds']
counts['unannotated_seconds']=counts['audio_seconds']-counts['annotated_span_seconds']
result={'recordings':64,'scoreable_recordings':64-len(zero),'zero_scoreable_pieces':zero,'totals':counts,'source_selection_sha256':selection_hash,'selection_precedes_audio_download':True,'all_crc_sha_and_reference_checks_passed':True,'http_retry_events':len(audio['retry_events']),'range_bytes_downloaded':audio['total_range_bytes'],'algorithm_results_inspected':False}
(WORK/'acquisition_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
