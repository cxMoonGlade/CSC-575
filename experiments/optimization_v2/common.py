"""Development-only feature cache and exact-duration comparison helpers."""
from pathlib import Path
import argparse
import os, sys, json, time
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ.setdefault(key,'1')
import numpy as np
HERE = Path(__file__).resolve().parent
EXPECTED_BASELINE_ACCURACY = 0.7196539813497197


def add_common_arguments(parser):
    """Add project, result, and feature-cache locations to a runner."""
    parser.add_argument('--project-root', type=Path, default=HERE.parents[1])
    parser.add_argument('--work-dir', type=Path, default=HERE)
    parser.add_argument('--cache-dir', type=Path, default=None)
    return parser


_path_parser = add_common_arguments(argparse.ArgumentParser(add_help=False))
_path_args, _ = _path_parser.parse_known_args()
ROOT = _path_args.project_root.resolve()
BASE = _path_args.work_dir.resolve()
CACHE = _path_args.cache_dir.resolve() if _path_args.cache_dir else BASE / 'cache'
sys.path.insert(0, str(ROOT))
from chordrec.audio import extract_features
from chordrec.data import load_reference,reduce_label
from chordrec.model import LABELS,decode
from chordrec.tune import exact_overlap_weights
from chordrec.regions import merge
from chordrec.evaluate import _normalize,_boundaries,_scoreable_spans


def load_config():
    """Require the same configuration used in the recorded experiments."""
    actual=json.loads((ROOT/'configs/frozen.json').read_text())
    expected=json.loads((HERE/'frozen_config.json').read_text())
    if actual != expected:
        raise ValueError('Project frozen configuration differs from this experiment')
    return actual


def load_records():
    manifest=json.loads((CACHE/'manifest.json').read_text())
    cfg=load_config()
    expected = json.loads((ROOT/'configs/guitarset_split.json').read_text())['records']
    expected = sorted((record for record in expected if record['split'] == 'development'), key=lambda record: record['id'])
    if len(manifest) != 119 or len({record['id'] for record in manifest}) != 119:
        raise ValueError('Expected exactly 119 distinct development recordings')
    if any(record['split'] != 'development' or record['progression'] not in (1, 2) for record in manifest):
        raise ValueError('The experiment cache may contain only development progressions 1 and 2')
    if sorted(manifest, key=lambda record: record['id']) != expected:
        raise ValueError('Cache manifest does not match the project development split')
    if cfg['switch_penalty'] != 4 or cfg['n_fft_short'] != 2048 or cfg['n_fft_long'] != 8192:
        raise ValueError('These experiments require the frozen 2048/8192 configuration and penalty 4')
    result=[]
    for rec in manifest:
        with np.load(CACHE/f"{rec['id']}.npz",allow_pickle=False) as data:
            f={k:data[k] for k in ('times','rms','short','long','duration','tuning')}
            f['duration']=float(f['duration']);f['tuning']=float(f['tuning'])
            result.append(dict(record=rec,features=f,reference=load_reference(ROOT/rec['annotation'],'performed'),weights=data['weights'],near_weights=data['near_weights'],config=dict(cfg)))
    return result


def score(name,items,predict):
    rows=[]
    started=time.perf_counter()
    for item in items:
        labels=np.asarray(predict(item))
        frames=item['features']['times'].size
        if labels.shape!=(frames,) or labels.dtype.kind not in 'iu' or np.any((labels<0)|(labels>=len(LABELS))):
            raise ValueError('Prediction must have one valid integer label per frame')
        index=np.arange(frames)
        w,n=item['weights'],item['near_weights']
        rows.append(dict(recording=item['record']['id'],progression=item['record']['progression'],performer=item['record']['id'].split('_')[0],correct_seconds=float(w[labels,index].sum()),scoreable_seconds=float(w.sum()),near_correct_seconds=float(n[labels,index].sum()),near_scoreable_seconds=float(n.sum())))
    def aggregate(part):
        correct=sum(r['correct_seconds'] for r in part);valid=sum(r['scoreable_seconds'] for r in part)
        nc=sum(r['near_correct_seconds'] for r in part);nv=sum(r['near_scoreable_seconds'] for r in part)
        return dict(recordings=len(part),correct_seconds=correct,scoreable_seconds=valid,accuracy=correct/valid if valid else None,near_accuracy=nc/nv if nv else None,near_correct_seconds=nc,near_scoreable_seconds=nv)
    summary=dict(name=name,**aggregate(rows),families={str(k):aggregate([r for r in rows if r['progression']==k]) for k in (1,2)},performers={str(k):aggregate([r for r in rows if r['performer']==k]) for k in sorted({r['performer'] for r in rows})},cached_prediction_seconds=time.perf_counter()-started)
    return summary,rows


def prepare():
    folder=CACHE
    if folder.exists() and any(folder.iterdir()):
        raise FileExistsError('Choose an empty cache directory to preserve existing features')
    if (BASE/'baseline.json').exists():
        raise FileExistsError('Choose a fresh work directory to preserve the baseline')
    folder.mkdir(parents=True,exist_ok=True)
    BASE.mkdir(parents=True,exist_ok=True)
    cfg=load_config()
    manifest=json.loads((ROOT/'configs/guitarset_split.json').read_text())
    records=sorted((r for r in manifest['records'] if r['split']=='development'),key=lambda r:r['id'])
    assert len(records)==119 and all(r['progression'] in (1,2) for r in records)
    for i,r in enumerate(records,1):
        features=extract_features(ROOT/r['audio'],cfg,required=('short','long'))
        ref=load_reference(ROOT/r['annotation'],'performed')
        normalized=_normalize(ref,features['duration'])
        bounds=_boundaries(normalized);spans=_scoreable_spans(normalized)
        near=merge([(max(a,b-.2),min(c,b+.2)) for a,c in spans for b in bounds if a<b<c])
        near_reference=[(max(a,c),min(b,d),label) for a,b,label in normalized if label is not None for c,d in near if min(b,d)>max(a,c)]
        weights=exact_overlap_weights(features['times'],features['duration'],ref,LABELS,reduce_label)
        nw=exact_overlap_weights(features['times'],features['duration'],near_reference,LABELS,reduce_label)
        np.savez_compressed(folder/f"{r['id']}.npz",**features,weights=weights,near_weights=nw)
        if i%20==0 or i==len(records):print('Cached',i,'/',len(records),flush=True)
    (folder/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
    items=load_records()
    summary,rows=score('long8192_penalty4',items,lambda item:decode(item['features']['long'],item['features']['rms'],item['config']))
    assert abs(summary['accuracy']-EXPECTED_BASELINE_ACCURACY)<1e-12
    (BASE/'baseline.json').write_text(json.dumps(dict(summary=summary,rows=rows),indent=2)+'\n')
    print(json.dumps(summary),flush=True)

if __name__=='__main__':
    parser=add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.parse_args()
    prepare()
