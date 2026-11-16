"""Compare near-boundary and stable-region accuracy in completed runs.

Predeclared for this report: half-width 0.2 seconds, supported reduced-label
changes only, neighborhoods confined to their contiguous scoreable span.
Reads the reference and prediction CSVs saved by the selected run.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import sys

from .evaluate import _normalize, _boundaries, _scoreable_spans


def merge(intervals):
    merged = []
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if merged and a <= merged[-1][1] + 1e-9:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def intersection(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        a, b = max(left[i][0], right[j][0]), min(left[i][1], right[j][1])
        if b > a:
            out.append((a, b))
        if left[i][1] <= right[j][1]:
            i += 1
        else:
            j += 1
    return out


def subtract(spans, pieces):
    result = []
    for a, b in spans:
        cursor = a
        for c, d in pieces:
            if d <= cursor or c >= b:
                continue
            if c > cursor:
                result.append((cursor, min(c, b)))
            cursor = max(cursor, min(d, b))
        if cursor < b:
            result.append((cursor, b))
    return result


def measure(intervals):
    return sum(b - a for a, b in intervals)


def region_scores(reference, prediction, duration, halfwidth=.2):
    if halfwidth <= 0:
        raise ValueError('halfwidth must be positive')
    reference = _normalize(reference, duration)
    prediction = _normalize(prediction, duration)
    spans = _scoreable_spans(reference)
    boundaries = _boundaries(reference)
    near = []
    for start, end in spans:
        near.extend((max(start, b - halfwidth), min(end, b + halfwidth))
                    for b in boundaries if start < b < end)
    near = merge(near)
    stable = subtract(spans, near)
    correct = []
    i = j = 0
    while i < len(reference) and j < len(prediction):
        left, right = reference[i], prediction[j]
        a, b = max(left[0], right[0]), min(left[1], right[1])
        if b > a and left[2] is not None and left[2] == right[2]:
            correct.append((a, b))
        if left[1] <= right[1]:
            i += 1
        else:
            j += 1
    result = {'boundary_halfwidth_seconds': float(halfwidth),
              'reference_boundaries': len(boundaries),
              'scoreable_seconds': measure(spans),
              'correct_seconds': measure(correct)}
    for name, regions in [('near', near), ('stable', stable)]:
        denominator = measure(regions)
        numerator = measure(intersection(correct, regions))
        result[name + '_scoreable_seconds'] = denominator
        result[name + '_correct_seconds'] = numerator
        result[name + '_accuracy'] = numerator / denominator if denominator else None
    assert abs(result['near_scoreable_seconds'] + result['stable_scoreable_seconds'] - result['scoreable_seconds']) < 1e-7
    assert abs(result['near_correct_seconds'] + result['stable_correct_seconds'] - result['correct_seconds']) < 1e-7
    return result


def self_test():
    def close(actual, expected):
        assert abs(actual - expected) < 1e-9, (actual, expected)
    # Neighborhoods at 1.0 and 1.2 s overlap to form [0.8, 1.4] s.
    ref = [(0,1,'C:maj'),(1,1.2,'G:maj'),(1.2,3,'C:maj')]
    pred = [(0,3,'C:maj')]
    r = region_scores(ref,pred,3)
    close(r['near_scoreable_seconds'],.6)
    close(r['near_correct_seconds'],.4)
    close(r['stable_scoreable_seconds'],2.4)
    close(r['stable_accuracy'],1)
    # Gap edges are not boundaries; windows remain within the local span.
    ref = [(0,.4,'C:maj'),(.4,.5,'G:maj'),(.5,.55,'X'),(.55,1,'F:maj')]
    r = region_scores(ref,[(0,1,'C:maj')],1)
    close(r['near_scoreable_seconds'],.3)
    close(r['near_correct_seconds'],.2)
    close(r['stable_scoreable_seconds'],.65)
    assert r['reference_boundaries'] == 1
    # Constant reduced reference (including seventh -> triad) has no near region.
    ref = [(0,1,'C:maj'),(1,2,'C:7')]
    r = region_scores(ref,[(0,1,'C:maj'),(1,2,'G:maj')],2)
    assert r['near_accuracy'] is None and r['reference_boundaries'] == 0
    close(r['stable_scoreable_seconds'],2)
    close(r['stable_accuracy'],.5)
    print('3 analytical region tests passed.')


def read_intervals(path):
    with Path(path).open() as f:
        return [(float(r['start']),float(r['end']),r['label']) for r in csv.DictReader(f)]


def analyze(run, output, halfwidth):
    run = Path(run)
    rows = list(csv.DictReader((run/'per_recording.csv').open()))
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    scored=[]
    for row in rows:
        directory=run/'predictions'/row['recording']
        ref=read_intervals(directory/'reference.csv')
        pred=read_intervals(directory/f"{row['method']}_{row['decoder']}.csv")
        result=region_scores(ref,pred,float(row['audio_seconds']),halfwidth)
        assert abs(result['correct_seconds']-float(row['correct_seconds']))<1e-6
        assert abs(result['scoreable_seconds']-float(row['scoreable_seconds']))<1e-6
        scored.append({key:row[key] for key in ['recording','group','split','method','decoder']}|result)
    with (output/'per_recording_regions.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(scored[0]));writer.writeheader();writer.writerows(scored)
    summary=[]
    for method,decoder in sorted({(r['method'],r['decoder']) for r in scored}):
        selected=[r for r in scored if r['method']==method and r['decoder']==decoder]
        total={'method':method,'decoder':decoder,'recordings':len(selected)}
        for name in ['near','stable']:
            denominator=sum(r[name+'_scoreable_seconds'] for r in selected)
            numerator=sum(r[name+'_correct_seconds'] for r in selected)
            total[name+'_scoreable_seconds']=denominator
            total[name+'_correct_seconds']=numerator
            total[name+'_accuracy']=numerator/denominator if denominator else None
        summary.append(total)
    metadata={'source_run':str(run.resolve()),'boundary_halfwidth_seconds':halfwidth,
              'definition':'Union of neighborhoods around supported, merged reference chord changes, clipped to each contiguous scoreable span. Stable is the remaining scoreable time. Exact interval-duration integration.',
              'inference_scope':'Descriptive paired-recording scores; no independence, statistical significance, or acoustic-boundary correctness claim.',
              'summary':summary}
    (output/'region_summary.json').write_text(json.dumps(metadata,indent=2,allow_nan=False)+'\n')
    print('Saved region analysis:',output)
    return metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--halfwidth',type=float,default=.2)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        self_test()
    if args.run:
        if not args.output:
            parser.error('--output is required with --run')
        analyze(args.run,args.output,args.halfwidth)
