"""Compare three harmonic dictionaries on the fixed development recordings."""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=ROOT,
                        help='Project containing the fixed split, data and development helpers')
    parser.add_argument('--cache-dir', type=Path,
                        help='119-record development cache; defaults to the optimization_v2 cache')
    parser.add_argument('--output', type=Path, default=ROOT/'experiments/root_harmonic/results',
                        help='Fresh output directory; existing paths are never overwritten')
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f'Choose a fresh output directory: {out}')
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    project_root = args.project_root.resolve()
    helper_directory = project_root/'experiments/optimization_v2'
    if not (helper_directory/'common.py').is_file():
        raise FileNotFoundError(f'Development helpers are missing: {helper_directory}')
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(helper_directory))
    import common
    common.ROOT = project_root
    common.CACHE = (args.cache_dir.resolve() if args.cache_dir
                    else helper_directory/'cache')
    # Read the fixed data split from the project and method code from this checkout.
    sys.path.insert(0, str(ROOT))
    import librosa
    import numpy as np
    import soundfile as sf
    spec = importlib.util.spec_from_file_location('chordrec.harmonic', ROOT/'chordrec/harmonic.py')
    harmonic_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = harmonic_module
    spec.loader.exec_module(harmonic_module)
    fit_chroma = harmonic_module.fit_chroma
    from chordrec.model import decode
    items = common.load_records()
    out.mkdir(parents=True)
    config=items[0]['config']
    rows=[]; started=time.perf_counter()
    for number,item in enumerate(items,1):
        t0=time.perf_counter();rec=item['record'];f=item['features'];w=item['weights'];nw=item['near_weights']
        y,sr=sf.read(common.ROOT/rec['audio'],dtype='float32',always_2d=True);y=y.mean(axis=1)
        if sr!=config['sample_rate']:
            y=librosa.resample(y,orig_sr=sr,target_sr=config['sample_rate'],res_type='soxr_hq')
        mag=np.abs(librosa.stft(y,n_fft=8192,hop_length=512,window='hann',center=True,pad_mode='constant'))[:,:len(f['times'])]
        shared_seconds=time.perf_counter()-t0
        for decay in (None,0.0,0.6,0.9):
            start=time.perf_counter()
            if decay is None:chroma=f['long'];diagnostics={}
            else:chroma,diagnostics=fit_chroma(mag,config,f['tuning'],decay)
            pred=decode(chroma,f['rms'],config,True); elapsed=time.perf_counter()-start
            idx=np.arange(len(pred)); chord_weights=w[:24]; root_weights=chord_weights[:12]+chord_weights[12:]
            chord_seconds=float(chord_weights.sum()); chord_pred=pred<24
            root_correct=float(root_weights[pred[chord_pred]%12,idx[chord_pred]].sum())
            root_wrong=float(chord_weights[:,chord_pred].sum())-root_correct
            rows.append(dict(recording=rec['id'],progression=rec['progression'],setting='baseline' if decay is None else f'decay_{decay:g}',correct_seconds=float(w[pred,idx].sum()),scoreable_seconds=float(w.sum()),near_correct_seconds=float(nw[pred,idx].sum()),near_scoreable_seconds=float(nw.sum()),chord_seconds=chord_seconds,root_correct_seconds=root_correct,other_root_seconds=root_wrong,shared_audio_stft_seconds=shared_seconds,fit_decode_seconds=elapsed,**diagnostics))
        if number%10==0 or number==119:
            print(json.dumps({'done':number,'elapsed_seconds':time.perf_counter()-started}),flush=True)
    summary=[]
    for setting in ('baseline','decay_0','decay_0.6','decay_0.9'):
        selected=[r for r in rows if r['setting']==setting]
        def agg(rr):
            keys=('correct_seconds','scoreable_seconds','near_correct_seconds','near_scoreable_seconds','chord_seconds','root_correct_seconds','other_root_seconds','shared_audio_stft_seconds','fit_decode_seconds')
            d={k:sum(r[k] for r in rr) for k in keys}
            d.update(accuracy=d['correct_seconds']/d['scoreable_seconds'],near_accuracy=d['near_correct_seconds']/d['near_scoreable_seconds'],root_accuracy=d['root_correct_seconds']/d['chord_seconds'])
            return d
        summary.append(dict(setting=setting,**agg(selected),families={str(k):agg([r for r in selected if r['progression']==k]) for k in (1,2)}))
    assert abs(summary[0]['accuracy']-common.EXPECTED_BASELINE_ACCURACY)<1e-12
    with (out/'per_recording.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=sorted(set().union(*(r.keys() for r in rows))))
        writer.writeheader();writer.writerows(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    source={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'chordrec/harmonic.py',ROOT/'experiments/root_harmonic/plan.json']}
    (out/'sources.json').write_text(json.dumps(source,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)

    (out/'timing.json').write_text(json.dumps({
        'baseline': 'Decode only; long-window chroma and tuning come from the development cache.',
        'shared_audio_stft_seconds': 'Read, resample and compute the long-window magnitude once per recording.',
        'fit_decode_seconds': 'Dictionary construction, NNLS and decoding; tuning and magnitude are reused.',
        'dictionary_cache': False,
        'full_inference': False,
        'historical_run': 'The archived original run reused a dictionary cache. Its timing is not directly comparable to this uncached-dictionary rerun.'
    }, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    main()
