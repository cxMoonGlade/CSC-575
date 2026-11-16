"""Audit saved fast-tempo predictions without extracting audio features."""
from pathlib import Path
import ast
from collections import Counter, defaultdict
import csv
import datetime
import hashlib
import json
import math
import random
import numpy as np
import mir_eval.chord

BASE=Path('/tmp/chordrec_root_fast');RUN=BASE/'results'
PROJECT=Path('/home/cx/Documents/csc475/Proj')
METHODS=('long','projection','harmonic')
TOL=1e-8
checks=0;max_error=0.


def check(actual,expected,where):
    global checks,max_error
    checks+=1
    if expected is None:
        assert actual is None or actual=='',(where,actual,expected)
        return
    assert actual is not None and actual!='',(where,actual,expected)
    a,b=float(actual),float(expected)
    assert math.isfinite(a) and math.isfinite(b),(where,a,b)
    error=abs(a-b);max_error=max(max_error,error)
    assert error<TOL,(where,a,b,error)


def reduction(label):
    if label=='N':return 'N'
    if label=='X':return None
    try:root,bitmap,bass=mir_eval.chord.encode(label,reduce_extended_chords=False)
    except (ValueError,mir_eval.chord.InvalidChordException):return None
    if root<0:return None
    for name,pcs in [('maj',[0,4,7]),('min',[0,3,7])]:
        if np.array_equal(bitmap[:8],np.array([i in pcs for i in range(8)],dtype=int)):
            return f'{root}:{name}'
    return None


def intervals(path):
    return [(float(r['start']),float(r['end']),r['label']) for r in csv.DictReader(path.open())]


def normalize(rows,duration):
    out=[]
    for start,end,label in rows:
        start=max(0.,start);end=min(duration,end);label=reduction(label)
        assert end>start
        if out and abs(start-out[-1][1])<1e-9 and label==out[-1][2]:
            out[-1]=(out[-1][0],end,label)
        else:out.append((start,end,label))
    return out


def merge(windows):
    out=[]
    for start,end in sorted(windows):
        if end<=start:continue
        if out and start<=out[-1][1]+1e-9:out[-1]=(out[-1][0],max(end,out[-1][1]))
        else:out.append((start,end))
    return out


def boundary_positions(rows):
    return [left[1] for left,right in zip(rows[:-1],rows[1:])
            if left[2] is not None and right[2] is not None and left[2]!=right[2] and abs(left[1]-right[0])<1e-9]


def maximum_match_count(ref,pred,tolerance=.1):
    i=j=hits=0
    while i<len(ref) and j<len(pred):
        if pred[j]<ref[i]-tolerance-1e-12:j+=1
        elif pred[j]>ref[i]+tolerance+1e-12:i+=1
        else:hits+=1;i+=1;j+=1
    return hits


def recompute(ref,pred,duration,saved):
    ref=normalize(ref,duration);pred=normalize(pred,duration)
    spans=merge([(a,b) for a,b,label in ref if label is not None])
    boundaries=boundary_positions(ref)
    near=merge([(max(a,t-.2),min(b,t+.2)) for a,b in spans for t in boundaries if a<t<b])
    result=dict(audio_seconds=duration,scoreable_seconds=sum(b-a for a,b,l in ref if l is not None),chord_scoreable_seconds=sum(b-a for a,b,l in ref if l not in (None,'N')),
                correct_seconds=0.,chord_correct_seconds=0.,root_correct_seconds=0.,no_chord_seconds=sum(b-a for a,b,l in ref if l=='N'),no_chord_correct_seconds=0.,near_scoreable_seconds=sum(b-a for a,b in near),near_correct_seconds=0.,reference_n_error_seconds=0.,chord_to_n_seconds=0.,same_root_wrong_quality_seconds=0.,other_root_seconds=0.,invalid_prediction_seconds=0.)
    for rs,re,rl in ref:
        if rl is None:continue
        for ps,pe,pl in pred:
            start,end=max(rs,ps),min(re,pe)
            if end<=start:continue
            dt=end-start
            if rl==pl:
                result['correct_seconds']+=dt
                result['near_correct_seconds']+=sum(max(0.,min(end,b)-max(start,a)) for a,b in near)
            if rl=='N':
                result['no_chord_correct_seconds' if pl=='N' else 'reference_n_error_seconds']+=dt
                continue
            if pl==rl:result['chord_correct_seconds']+=dt
            if pl not in (None,'N') and rl.split(':')[0]==pl.split(':')[0]:
                result['root_correct_seconds']+=dt
                if rl!=pl:result['same_root_wrong_quality_seconds']+=dt
            elif pl=='N':result['chord_to_n_seconds']+=dt
            elif pl is None:result['invalid_prediction_seconds']+=dt
            else:result['other_root_seconds']+=dt
    result['root_scoreable_seconds']=result['chord_scoreable_seconds']
    result['excluded_seconds']=duration-result['scoreable_seconds']
    result['stable_scoreable_seconds']=result['scoreable_seconds']-result['near_scoreable_seconds']
    result['stable_correct_seconds']=result['correct_seconds']-result['near_correct_seconds']
    for prefix in ('','chord_','root_','near_','stable_'):
        den=result[prefix+'scoreable_seconds']
        result['duration_accuracy' if not prefix else prefix+'accuracy']=result[prefix+'correct_seconds']/den if den else None
    result['no_chord_accuracy']=result['no_chord_correct_seconds']/result['no_chord_seconds'] if result['no_chord_seconds'] else None
    result['coverage']=result['scoreable_seconds']/duration
    prediction_bounds=boundary_positions(pred)
    total_refs=total_preds=hits=0;all_ref=[];all_pred=[]
    for a,b in spans:
        r=[x for x in boundaries if a+1e-9<x<b-1e-9]
        p=[x for x in prediction_bounds if a+1e-9<x<b-1e-9]
        total_refs+=len(r);total_preds+=len(p);hits+=maximum_match_count(r,p)
        all_ref.extend(r);all_pred.extend(p)
    pairs=ast.literal_eval(saved['matched_boundary_pairs']);errors=ast.literal_eval(saved['boundary_timing_errors_seconds'])
    assert len(pairs)==len(errors)==hits
    assert len({r for r,p in pairs})==hits and len({p for r,p in pairs})==hits
    for (r,p),e in zip(pairs,errors):
        assert r in all_ref and p in all_pred and abs(r-p)<=.1+1e-12
        assert any(a+1e-9<r<b-1e-9 and a+1e-9<p<b-1e-9 for a,b in spans)
        check(e,p-r,'saved boundary error')
    result.update(boundary_matches=hits,reference_boundaries=total_refs,predicted_boundaries=total_preds,
                  boundary_precision=hits/total_preds if total_preds else 0.,boundary_recall=hits/total_refs if total_refs else 0.,boundary_f1=2*hits/(total_refs+total_preds) if total_refs+total_preds else 0.,
                  boundary_mae_seconds=sum(abs(x) for x in errors)/hits if hits else None,boundary_mean_signed_error_seconds=sum(errors)/hits if hits else None,boundary_timing_errors_seconds=errors)
    return result

rows=list(csv.DictReader((RUN/'per_recording.csv').open()))
assert len(rows)==384 and len({(r['recording'],r['method'],r['decoder']) for r in rows})==384
assert Counter((r['method'],r['decoder']) for r in rows)==Counter({(m,d):64 for m in METHODS for d in ('raw','viterbi')})
audit={r['recording']:r for r in json.loads((RUN/'annotation_audit.json').read_text())}
validation=json.loads((RUN/'input_validation.json').read_text());valid={r['piece_id']:r for r in validation['recordings']}
assert len(audit)==len(valid)==64 and set(audit)==set(valid)
selection=json.loads((RUN/'selection.json').read_text())
previous=json.loads((RUN/'previous_selection.json').read_text())
assert {r['piece_id'] for r in selection['recordings']}=={r['piece_id'] for r in previous['recordings']}==set(valid)
inputs=json.loads((RUN/'inputs.json').read_text())
for path,h in inputs.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
assert len(inputs)==135
sources=json.loads((RUN/'sources.json').read_text())
for name,h in sources.items():
    assert hashlib.sha256((RUN/'source_snapshot'/name).read_bytes()).hexdigest()==h,name
    path=PROJECT/name if name.startswith('chordrec/') else Path('/tmp/chordrec_root_progression_validation/compare.py')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==h,name
plan=json.loads((RUN/'evaluation_plan.json').read_text())
assert hashlib.sha256((BASE/'plan.json').read_bytes()).hexdigest()==selection['evaluation_plan_sha256']
for p,h in plan['config_sha256'].items():assert hashlib.sha256((PROJECT/p).read_bytes()).hexdigest()==h
for p,h in plan['method_sha256'].items():assert sources['chordrec/'+p]==h
configs=json.loads((RUN/'configurations.json').read_text())
for method,p in [('long','configs/frozen.json'),('projection','configs/note_projection.json'),('harmonic','configs/note_nnls.json')]:assert configs[method]==json.loads((PROJECT/p).read_text())
order=json.loads((RUN/'run_order.json').read_text())
expected=[dict(recording=rid,group=rid,method=m) for rid in sorted(valid) for m in METHODS];random.Random(20261110).shuffle(expected)
assert order==expected and len(order)==192
assert [(r['recording'],r['method']) for r in rows[::2]]==[(r['recording'],r['method']) for r in order]
computed=[]
for r in rows:
    rid=r['recording'];folder=RUN/'predictions'/rid
    reference=intervals(folder/'reference.csv');pred=intervals(folder/f"{r['method']}_{r['decoder']}.csv")
    assert [list(x) for x in reference]==valid[rid]['reference']
    assert pred[0][0]==0. and pred[-1][1]==valid[rid]['duration_seconds']
    assert all(abs(left[1]-right[0])<1e-12 for left,right in zip(pred[:-1],pred[1:]))
    got=recompute(reference,pred,float(r['audio_seconds']),r)
    for k,v in got.items():
        if k!='boundary_timing_errors_seconds':check(r[k],v,f'{rid}/{r["method"]}/{r["decoder"]}/{k}')
    runtime=float(r['runtime_seconds']) if r['runtime_seconds'] else None
    if r['decoder']=='raw':assert runtime is None
    else:assert runtime>0 and math.isfinite(runtime)
    computed.append(dict(recording=rid,method=r['method'],decoder=r['decoder'],genre=r['genre'],runtime_seconds=runtime,**got))
for rid in valid:
    grids=[]
    for method in METHODS:
        f=json.loads((RUN/'predictions'/rid/f'{method}_features.json').read_text())
        grids.append({k:f[k] for k in ('frames','tuning','times_sha256','rms_sha256')})
    assert grids[0]==grids[1]==grids[2],rid


def aggregate(part):
    fields=('audio_seconds','correct_seconds','scoreable_seconds','excluded_seconds','boundary_matches','reference_boundaries','predicted_boundaries','near_correct_seconds','near_scoreable_seconds','stable_correct_seconds','stable_scoreable_seconds','chord_correct_seconds','chord_scoreable_seconds','root_correct_seconds','root_scoreable_seconds','no_chord_seconds','no_chord_correct_seconds','reference_n_error_seconds','other_root_seconds','same_root_wrong_quality_seconds','chord_to_n_seconds','invalid_prediction_seconds')
    out={k:sum(r[k] for r in part) for k in fields}
    out.update(recordings=len(part),scoreable_recordings=sum(r['scoreable_seconds']>0 for r in part),chord_scoreable_recordings=sum(r['chord_scoreable_seconds']>0 for r in part))
    for prefix in ('','chord_','root_','near_','stable_'):
        den=out[prefix+'scoreable_seconds'];out['duration_accuracy' if not prefix else prefix+'accuracy']=out[prefix+'correct_seconds']/den if den else None
    out['no_chord_accuracy']=out['no_chord_correct_seconds']/out['no_chord_seconds'] if out['no_chord_seconds'] else None
    out['coverage']=out['scoreable_seconds']/out['audio_seconds']
    hits,refs,preds=[out[k] for k in ('boundary_matches','reference_boundaries','predicted_boundaries')]
    errors=[x for r in part for x in r['boundary_timing_errors_seconds']]
    out.update(boundary_precision=hits/preds if preds else 0.,boundary_recall=hits/refs if refs else 0.,boundary_f1=2*hits/(refs+preds) if refs+preds else 0.,boundary_mae_seconds=sum(abs(x) for x in errors)/hits if hits else None,boundary_mean_signed_error_seconds=sum(errors)/hits if hits else None)
    acc=[r['duration_accuracy'] for r in part if r['duration_accuracy'] is not None]
    times=[r['runtime_seconds'] for r in part if r['runtime_seconds'] is not None]
    out.update(mean_recording_accuracy=sum(acc)/len(acc) if acc else None,total_runtime_seconds=sum(times) if times else None,realtime_factor=sum(times)/out['audio_seconds'] if times else None)
    return out
summary=json.loads((RUN/'summary.json').read_text())
assert len(summary)==6
verified=[]
for row in summary:
    part=[r for r in computed if r['method']==row['method'] and r['decoder']==row['decoder']]
    overall=aggregate(part)
    for key,val in overall.items():check(row[key],val,f'summary {row["method"]}/{row["decoder"]}/{key}')
    genres={}
    for genre,saved in row['genres'].items():
        got=aggregate([r for r in part if r['genre']==genre]);genres[genre]=got
        for key,val in got.items():check(saved[key],val,f'genre {genre}/{key}')
    verified.append(dict(method=row['method'],decoder=row['decoder'],**overall,genres=genres))
base={r['recording']:r for r in computed if r['method']=='long' and r['decoder']=='viterbi'}
projection={r['recording']:r for r in computed if r['method']=='projection' and r['decoder']=='viterbi'}
deltas={rid:projection[rid]['duration_accuracy']-r['duration_accuracy'] for rid,r in base.items() if r['duration_accuracy'] is not None}
win=sum(x>1e-12 for x in deltas.values());tie=sum(abs(x)<=1e-12 for x in deltas.values());loss=sum(x< -1e-12 for x in deltas.values())
zeros=sorted(rid for rid,r in base.items() if r['scoreable_seconds']==0)
n_only=sorted(rid for rid,r in base.items() if r['scoreable_seconds']>0 and r['chord_scoreable_seconds']==0)
assert len(zeros)==5 and len(deltas)==59
runtime=json.loads((RUN/'run.json').read_text());env=json.loads((RUN/'environment.json').read_text())
assert runtime['audio_to_label_runs']==192 and runtime['result_rows']==384 and runtime['recordings']==64
assert all(pool['num_threads']==1 for pool in env['threadpools'])
assert set(env['thread_environment'].values())=={'1'}
report=dict(reviewed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inference_runs_performed=0,rows_verified=384,recordings=64,methods=list(METHODS),jobs_verified=192,run_order_seed=20261110,run_order_matches=True,input_hashes_verified=len(inputs),source_hashes_verified=len(sources),frozen_config_hashes_verified=3,frozen_core_method_hashes_verified=5,feature_grids_rms_and_tuning_match_for_all_recordings=True,all_reference_intervals_match_validated_annotations=True,scoreable_recordings=59,chord_scoreable_recordings=58,zero_scoreable_recordings=zeros,N_only_scoreable_recordings=n_only,independent_numeric_checks=checks,maximum_absolute_numeric_difference=max_error,verification_method='Primary, root, N, error-partition and near/stable duration scores independently recomputed from interval overlaps. Reference reduction uses mir_eval encoding. Boundary counts and maximum matching cardinality independently recomputed; saved pairs and signed timing errors checked against eligible endpoints. Optimal minimum-error tie choice was not independently re-solved. All overall and genre aggregates and full runtimes recomputed.',projection_recording_comparison=dict(wins=win,ties=tie,losses=loss),summary=verified,issues=[])
(BASE/'numeric_review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='summary'},indent=2))
for r in verified:
    if r['decoder']=='viterbi':print(r['method'],r['duration_accuracy'],r['root_accuracy'],r['total_runtime_seconds'])
