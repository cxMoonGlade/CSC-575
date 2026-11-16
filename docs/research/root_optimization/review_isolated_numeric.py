"""Recompute isolated-chord scores from saved intervals without model inference."""
from pathlib import Path
import csv
import datetime
import hashlib
import json
import math
import subprocess
from collections import Counter,defaultdict

ROOT=Path('/tmp/chordrec_root_v1')
RUN=ROOT/'isolated_results'
DATA=Path('/home/cx/Documents/csc475/Proj/docs/datasets/IDMT-SMT-Guitar-isolated')
rows=list(csv.DictReader((RUN/'per_recording.csv').open()))
summary=json.loads((RUN/'summary.json').read_text())
audit=json.loads((RUN/'annotation_audit.json').read_text())
selection=json.loads((RUN/'selection.json').read_text())
validated=json.loads((DATA/'validation_manifest.json').read_text())
configs=json.loads((RUN/'configurations.json').read_text())
assert len(rows)==528 and len(summary)==6 and len(audit)==88
ids={r['recording'] for r in audit}
assert len(ids)==88
assert len({(r['recording'],r['method'],r['decoder']) for r in rows})==528
assert Counter((r['method'],r['decoder']) for r in rows)==Counter({(m,d):88 for m in ['long','harmonic','projection'] for d in ['raw','viterbi']})
assert {r['method'] for r in rows}==set(configs)
input_hashes=json.loads((RUN/'inputs.json').read_text())
for name,h in input_hashes.items():
 path=Path(name) if Path(name).is_absolute() else ROOT/'validation'/name
 assert hashlib.sha256(path.read_bytes()).hexdigest()==h,name
assert len(input_hashes)==181
assert selection==json.loads((DATA/'prospective_selection.json').read_text())
assert hashlib.sha256((DATA/'prospective_selection.json').read_bytes()).hexdigest()==validated['source_selection_sha256']
source_hashes=json.loads((RUN/'sources.json').read_text())
commit='3f9432e'
commit_full=subprocess.check_output(['git','rev-parse',commit],cwd=ROOT/'validation',text=True).strip()
for name,h in source_hashes.items():
 assert hashlib.sha256((RUN/'source_snapshot'/name).read_bytes()).hexdigest()==h,name
 assert hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:chordrec/{name}'],cwd=ROOT/'validation')).hexdigest()==h,name
validation_by_audio={r['audio']:r for r in validated['recordings']}
audit_by_id={r['recording']:r for r in audit}
paired=defaultdict(list)
for r in audit:
 rel=str(Path(r['audio']).relative_to(DATA))
 expected=validation_by_audio[rel]
 assert r['reference']==expected['reference'] and r['duration']==expected['duration_seconds']
 assert r['group_id']==expected['group_id'] and r['instrument']==expected['instrument']
 paired[r['group_id']].append(r['instrument'])
assert len(paired)==44
expected_instruments=['Fender Strat Clean Neck SC Chords','Ibanez Power Strat Clean Bridge HU Chords']
assert all(sorted(v)==expected_instruments for v in paired.values())


def intervals(path):
 return [(float(r['start']),float(r['end']),r['label']) for r in csv.DictReader(path.open())]

max_error=0
checks=0

def close(a,b,name):
 global max_error,checks
 assert math.isfinite(a) and math.isfinite(b),name
 err=abs(a-b);max_error=max(max_error,err);checks+=1
 assert err<1e-9,(name,a,b,err)

computed=[]
for r in rows:
 rid,m,d=r['recording'],r['method'],r['decoder']
 a=audit_by_id[rid]
 ref=intervals(RUN/'predictions'/rid/'reference.csv')
 assert [list(x) for x in ref]==a['reference']
 pred=intervals(RUN/'predictions'/rid/f'{m}_{d}.csv')
 assert pred and pred[0][0]==0 and pred[-1][1]==a['duration']
 previous_end=0
 for start,end,label in pred:
  close(start,previous_end,'contiguous predictions')
  assert 0<=start<end<=a['duration']
  assert label=='N' or label.split(':')[1] in ('maj','min')
  previous_end=end
 scoreable=sum(end-start for start,end,label in ref)
 counts=dict(correct_seconds=0.,root_correct_seconds=0.,other_root_seconds=0.,same_root_wrong_quality_seconds=0.,chord_to_n_seconds=0.)
 for rs,re,rl in ref:
  assert rl!='N'
  for ps,pe,pl in pred:
   duration=max(0.,min(re,pe)-max(rs,ps))
   if rl==pl:counts['correct_seconds']+=duration
   if pl!='N' and rl.split(':')[0]==pl.split(':')[0]:counts['root_correct_seconds']+=duration
   if pl=='N':counts['chord_to_n_seconds']+=duration
   elif rl.split(':')[0]!=pl.split(':')[0]:counts['other_root_seconds']+=duration
   elif rl!=pl:counts['same_root_wrong_quality_seconds']+=duration
 close(float(r['scoreable_seconds']),scoreable,'scoreable seconds')
 for key,value in counts.items():close(float(r[key]),value,key)
 close(float(r['duration_accuracy']),counts['correct_seconds']/scoreable,'duration accuracy')
 close(float(r['audio_seconds']),a['duration'],'audio duration')
 close(sum(counts[k] for k in ['correct_seconds','other_root_seconds','same_root_wrong_quality_seconds','chord_to_n_seconds']),scoreable,'partition')
 assert r['group']==a['group_id'] and r['instrument']==a['instrument']
 if d=='raw':assert r['runtime_seconds']==''
 else:assert math.isfinite(float(r['runtime_seconds'])) and float(r['runtime_seconds'])>0
 computed.append(dict(recording=rid,method=m,decoder=d,instrument=r['instrument'],group=r['group'],audio_seconds=float(r['audio_seconds']),scoreable_seconds=scoreable,runtime_seconds=float(r['runtime_seconds']) if r['runtime_seconds'] else None,**counts))


def totals(part):
 keys=['audio_seconds','scoreable_seconds','correct_seconds','root_correct_seconds','other_root_seconds','same_root_wrong_quality_seconds','chord_to_n_seconds']
 out={k:sum(r[k] for r in part) for k in keys}
 out.update(recordings=len(part),duration_accuracy=out['correct_seconds']/out['scoreable_seconds'],root_accuracy=out['root_correct_seconds']/out['scoreable_seconds'],total_runtime_seconds=sum(r['runtime_seconds'] for r in part) if all(r['runtime_seconds'] is not None for r in part) else None)
 return out
verified=[]
for saved in summary:
 part=[r for r in computed if r['method']==saved['method'] and r['decoder']==saved['decoder']]
 got=totals(part)
 for key,val in got.items():
  if val is None:assert saved[key] is None
  else:close(saved[key],val,'summary '+key)
 instruments={}
 for instrument in expected_instruments:
  sub=totals([r for r in part if r['instrument']==instrument])
  assert sub['recordings']==44
  for key,val in sub.items():
   if val is None:assert saved['instruments'][instrument][key] is None
   else:close(saved['instruments'][instrument][key],val,'instrument summary '+key)
  instruments[instrument]=sub
 verified.append(dict(method=saved['method'],decoder=saved['decoder'],**got,instruments=instruments))
env=json.loads((RUN/'environment.json').read_text())
assert set(env['thread_environment'].values())=={'1'}
result=dict(reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_commit=commit_full,model_runs_performed=0,prediction_rows=528,method_recordings=264,recordings=88,paired_groups=44,total_audio_seconds=220.,total_reference_seconds=202.725,input_hashes_verified=len(input_hashes),source_snapshot_and_commit_files_verified=len(source_hashes),single_thread_environment=env['thread_environment'],independent_numeric_checks=checks,maximum_absolute_numeric_difference=max_error,selection_and_annotation_hashes_match_frozen_data=True,all_references_match_frozen_manifest=True,paired_instruments_verified=True,runtime_definition_review='Timers include audio read, resampling, tuning, RMS, required STFT, dictionary construction and NNLS or direct projection when applicable, Viterbi, and interval construction. Raw label diagnostics, score aggregation, file output and warmup are excluded. Cached module import lookup occurs inside candidate timing but one-time imports complete in warmup.',summary=verified,conclusion='All three Viterbi methods score 100% major/minor and root accuracy on this isolated-chord check. The result establishes no comparative gain on this task. Raw differences are diagnostics and do not replace the frozen primary comparison.',issues=[])
(ROOT/'isolated_numeric_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='summary'},indent=2))
for row in verified:
 print(row['method'],row['decoder'],row['duration_accuracy'],row['root_accuracy'],row['total_runtime_seconds'])
