"""Test the single predefined follow-up with a 16,384-sample analysis window.

Only development recordings are scored. Every candidate retains the original
8,192-sample tuning estimate, frame grid, RMS rule, and decoding penalty.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import os
import sys
import time

for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ.setdefault(key,'1')
os.environ.pop('LIBROSA_CACHE_DIR',None)

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import common
import numpy as np
from chordrec.audio import extract_features,normalize_chroma
from chordrec.model import decode

SETTINGS=(
    ('single_8192',8192,None,None),
    ('single_16384',16384,None,None),
    ('fixed_4096_16384_w0.2',4096,16384,0.2),
    ('fixed_4096_16384_w0.5',4096,16384,0.5),
    ('fixed_8192_16384_w0.2',8192,16384,0.2),
)


def save_json(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def plan(output):
    """Record the five settings before extraction or scoring."""
    output.mkdir(parents=True,exist_ok=True)
    path=output/'plan.json'
    if path.exists():
        raise FileExistsError('A plan already exists; preserve the completed experiment')
    save_json(path,dict(
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis='A 16384-sample window improves chord evidence through finer frequency resolution; fixed fusion with a shorter window can recover accuracy near changes.',
        motivation='The preceding development experiment improved matched comparisons by replacing a 2048-sample short window with 4096 samples, but its best gain of 0.258444 percentage points missed the 0.5-point gate. This is the one authorized resolution follow-up.',
        split='All 119 development recordings in progression families 1 and 2; no progression-3 inputs or scores.',
        settings=[dict(name=name,first_window=first,second_window=second,first_window_weight=weight) for name,first,second,weight in SETTINGS],
        shared_controls=dict(sample_rate=22050,hop_length=512,tuning='Reuse the cached 8192-derived tuning through explicit config tuning.',pitch_range='MIDI 36-95',rms='Unchanged 2048-sample RMS and -45 dB rule.',switch_penalty=4.0),
        gate='At least 0.5 percentage points above single_8192 in pooled duration accuracy, with nonnegative change in each development family.',
        diagnostics='Report all settings, near-change accuracy, both families, and feature extraction time. Near-change accuracy is diagnostic rather than the selection target.',
        stop='No additional settings or tuning after the results. A successful candidate requires new independent material for validation; the original test set is not used in this round.',
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    ))


def predict(item,first,second,weight):
    chroma=item['resolution_features'][first]
    if second is not None:
        chroma=normalize_chroma(weight*chroma+(1-weight)*item['resolution_features'][second])
    return decode(chroma,item['features']['rms'],item['config'],smooth=True)


def main():
    parser=common.add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument('--output',type=Path,default=common.BASE/'runs/long_resolution')
    parser.add_argument('--plan-only',action='store_true')
    args=parser.parse_args()
    if not (args.output/'plan.json').exists():plan(args.output)
    if args.plan_only:return
    if any(path.name != 'plan.json' for path in args.output.iterdir()):
        raise FileExistsError('Choose a fresh output directory to preserve prior outputs')
    if (args.output/'summary.json').exists():raise FileExistsError('Preserve the saved results')
    recorded=json.loads((args.output/'plan.json').read_text())
    assert recorded['code_sha256']==hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    items=common.load_records()
    assert len(items)==119
    assert all(item['record']['split']=='development' and item['record']['progression'] in (1,2) for item in items)
    started=time.perf_counter();timings=[]
    for index,item in enumerate(items,1):
        before=time.perf_counter();f=item['features']
        cfg=dict(item['config'],n_fft_short=4096,n_fft_long=16384,tuning=f['tuning'])
        assert cfg['switch_penalty']==4.0 and item['config']['n_fft_long']==8192
        new=extract_features(common.ROOT/item['record']['audio'],cfg,required=('short','long'))
        np.testing.assert_array_equal(new['times'],f['times'])
        np.testing.assert_array_equal(new['rms'],f['rms'])
        assert new['duration']==f['duration'] and new['tuning']==f['tuning']
        item['resolution_features']={4096:new['short'],8192:f['long'],16384:new['long']}
        timings.append(dict(recording=item['record']['id'],seconds=time.perf_counter()-before))
        if index%30==0 or index==len(items):print(f'Extracted 4096/16384 chroma: {index}/{len(items)}',flush=True)
    extraction_seconds=time.perf_counter()-started
    summaries=[];all_rows=[]
    for name,first,second,weight in SETTINGS:
        summary,rows=common.score(name,items,lambda item:predict(item,first,second,weight))
        summaries.append(summary);all_rows.extend(dict(setting=name,**row) for row in rows)
        print(name,summary['accuracy'],summary['near_accuracy'],flush=True)
    baseline=summaries[0]
    assert abs(baseline['accuracy']-common.EXPECTED_BASELINE_ACCURACY)<1e-12
    for summary in summaries:
        summary['delta_pp']=100*(summary['accuracy']-baseline['accuracy'])
        summary['near_delta_pp']=100*(summary['near_accuracy']-baseline['near_accuracy'])
        summary['family_delta_pp']={key:100*(summary['families'][key]['accuracy']-baseline['families'][key]['accuracy']) for key in ('1','2')}
        summary['passes_candidate_gate']=summary['delta_pp']>=.5 and min(summary['family_delta_pp'].values())>=0
    eligible=[row for row in summaries if row['passes_candidate_gate']]
    best=max(summaries[1:],key=lambda row:row['accuracy'])
    save_json(args.output/'summary.json',summaries)
    save_json(args.output/'result.json',dict(best_candidate=best,baseline=baseline,eligible_candidates=[row['name'] for row in eligible],test_accessed=False,promoted=False,validation='Exact time-grid, RMS, duration, and cached tuning identity on all 119 recordings; baseline accuracy matches the shared cache.',code_sha256=recorded['code_sha256'],common_sha256=hashlib.sha256(Path(common.__file__).read_bytes()).hexdigest()))
    save_json(args.output/'extraction.json',dict(total_seconds=extraction_seconds,per_recording=timings,scope='Read/resample audio and extract 4096/16384 chroma with cached tuning, including initial library overhead. The 8192 chroma is reused. Not a per-candidate inference benchmark.'))
    with (args.output/'per_recording.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)
    print(json.dumps(dict(best=best['name'],score=best['accuracy'],delta_pp=best['delta_pp'],eligible=[row['name'] for row in eligible])),flush=True)


if __name__=='__main__':main()
