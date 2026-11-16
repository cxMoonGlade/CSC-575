"""Test frequency-axis spectral whitening before the existing chroma projection.

The experiment uses development recordings only. Cached evaluation timings are
not measurements of uncached audio-to-label runtime.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time

for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(variable, '1')
os.environ.pop('LIBROSA_CACHE_DIR', None)

import librosa
import numpy as np
from scipy.ndimage import median_filter
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common
ROOT = common.ROOT
from chordrec.audio import normalize_chroma
from chordrec.model import decode

STRENGTHS = (0.0, 0.5, 1.0)
METHODS = ('short', 'long', 'equal')
WIDTH_HZ = 300.0
FLOOR_FRACTION = 0.05


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def write_plan(output):
    """Save the complete grid before reading audio or scoring candidates."""
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'plan.json'
    if path.exists():
        raise FileExistsError('Use a new output directory for a new experiment')
    save_json(path, dict(
        recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis='Frequency-axis median whitening improves major/minor template matching by reducing local spectral amplitude imbalance.',
        development='All 119 recordings in progression families 1 and 2 only.',
        baseline='Unwhitened long STFT with the frozen shared switch penalty of 4.',
        spectral_envelope='For each frame, median-filter magnitude across in-range frequency bins with reflected edges. Divide magnitude by (median + floor)^strength before the unchanged chroma projection.',
        width_hz=WIDTH_HZ,
        width_rule='2 * round(width_hz / (sample_rate / n_fft) / 2) + 1 bins; the bin-centre span is approximately 300 Hz.',
        floor_fraction=FLOOR_FRACTION,
        floor_rule='0.05 times the maximum in-range magnitude in each frame, with a 1e-12 minimum.',
        choice_rationale='The fixed width spans multiple spectral bins at both resolutions. The floor limits amplification of weak inter-peak energy. Neither choice is optimized in this experiment.',
        strengths=list(STRENGTHS), methods=list(METHODS), settings=9,
        shared_controls='Cached tuning, original Hann STFT settings, pitch range, frame centres, RMS silence rule, triad templates, and switch penalty 4.',
        equality_check='Strength 0 must match cached chroma and predictions for short, long, and equal fusion.',
        candidate_gate='At least 0.5 percentage points above the unwhitened long baseline overall, with nonnegative accuracy change in each development family.',
        reporting='Report every setting, pooled/near-change/family scores, and extraction timing. No test access or promotion to the default.',
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    ))


def whiten_block(magnitude, size, strength, envelope=None):
    """Whiten an in-range magnitude block, retaining zero-strength identity."""
    if strength == 0:
        return magnitude
    if envelope is None:
        envelope = median_filter(magnitude, size=(size, 1), mode='reflect')
    floor = np.maximum(FLOOR_FRACTION * magnitude.max(axis=0, keepdims=True), 1e-12)
    return magnitude / np.power(envelope + floor, strength)


def extract_whitened(item, audio_root):
    """Reuse the cached tuning and frame grid while extracting new chroma."""
    cfg = item['config']
    samples, original_sr = sf.read(audio_root / item['record']['audio'], dtype='float32', always_2d=True)
    y = samples.mean(axis=1)
    sr, hop = int(cfg['sample_rate']), int(cfg['hop_length'])
    if original_sr != sr:
        y = librosa.resample(y, orig_sr=original_sr, target_sr=sr, res_type='soxr_hq')
    times = np.arange(1 + len(y) // hop, dtype=np.float64) * hop / sr
    times = times[times <= item['features']['duration']]
    np.testing.assert_array_equal(times, item['features']['times'])
    tuning = item['features']['tuning']
    minimum, bins = int(cfg['midi_min']), 12 * int(cfg['n_octaves'])
    results, errors, widths = {}, {}, {}
    for method in ('short', 'long'):
        n_fft = int(cfg[f'n_fft_{method}'])
        magnitude = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop, win_length=n_fft, window='hann', center=True, pad_mode='constant'))
        basis = librosa.filters.chroma(sr=sr, n_fft=n_fft, tuning=tuning, octwidth=None, norm=2, base_c=True)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        lower = librosa.midi_to_hz(minimum - 0.5 + tuning)
        upper = librosa.midi_to_hz(minimum + bins - 0.5 + tuning)
        mask = (frequencies >= lower) & (frequencies < upper)
        basis[:, ~mask] = 0
        block = magnitude[mask]
        size = 2 * round(WIDTH_HZ / (sr / n_fft) / 2) + 1
        envelope = median_filter(block, size=(size, 1), mode='reflect')
        widths[method] = dict(bins=size, bin_centre_span_hz=(size-1)*sr/n_fft)
        for strength in STRENGTHS:
            adjusted = magnitude.copy()
            adjusted[mask] = whiten_block(block, size, strength, envelope)
            chroma = normalize_chroma(basis @ adjusted)[:, :len(times)]
            assert chroma.shape == item['features'][method].shape
            assert np.all(np.isfinite(chroma))
            results[(method, strength)] = chroma
            if strength == 0:
                difference = float(np.max(np.abs(chroma - item['features'][method])))
                errors[method] = difference
                np.testing.assert_allclose(chroma, item['features'][method], rtol=1e-7, atol=1e-7)
    return results, errors, widths


def self_test():
    block = np.arange(35, dtype=np.float64).reshape(7, 5)
    assert whiten_block(block, 3, 0) is block
    for strength in STRENGTHS:
        silent = whiten_block(np.zeros((7, 5)), 3, strength)
        np.testing.assert_array_equal(silent, 0)
        constant = whiten_block(np.ones((7, 5)), 3, strength)
        assert np.all(np.isfinite(constant))
        np.testing.assert_allclose(normalize_chroma(constant), normalize_chroma(np.ones((7, 5))))


def main():
    parser = common.add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument('--output', type=Path, default=common.BASE/'runs/whitening')
    parser.add_argument('--plan-only', action='store_true')
    args = parser.parse_args()
    if not (args.output / 'plan.json').exists():
        write_plan(args.output)
    if args.plan_only:
        return
    if any(path.name != 'plan.json' for path in args.output.iterdir()):
        raise FileExistsError('Choose a fresh output directory to preserve prior outputs')
    if (args.output / 'summary.json').exists():
        raise FileExistsError('This experiment already has results')
    self_test()
    items = common.load_records()
    assert len(items) == 119
    assert all(item['record']['split'] == 'development' and item['record']['progression'] in (1, 2) for item in items)
    assert all(item['config']['switch_penalty'] == 4 for item in items)
    start = time.perf_counter()
    equality, extraction_rows = [], []
    for index, item in enumerate(items, 1):
        started = time.perf_counter()
        values, errors, widths = extract_whitened(item, common.ROOT)
        item['whitened'] = values
        extraction_rows.append(dict(recording=item['record']['id'],seconds=time.perf_counter()-started))
        equality.append(dict(recording=item['record']['id'], **errors))
        if index % 10 == 0 or index == len(items):
            print(f'Extracted {index}/{len(items)} development recordings', flush=True)
    extraction_seconds = time.perf_counter() - start
    save_json(args.output / 'extraction.json', dict(total_seconds=extraction_seconds, per_recording=extraction_rows, widths=widths, identity_max_error=max(max(r['short'],r['long']) for r in equality), equality=equality, runtime_scope='Audio read/resample, both STFTs, frequency medians, and all three strengths; cached tuning. Includes initial library overhead. Not a per-setting end-to-end runtime comparison.'))
    summaries, all_rows = [], []
    for strength in STRENGTHS:
        for method in METHODS:
            name = f'{method}_strength_{strength:g}'
            def predict(item):
                if method == 'equal':
                    chroma = normalize_chroma(.5 * item['whitened'][('short', strength)] + .5 * item['whitened'][('long', strength)])
                else:
                    chroma = item['whitened'][(method, strength)]
                labels = decode(chroma, item['features']['rms'], item['config'])
                if strength == 0:
                    original = normalize_chroma(.5*item['features']['short'] + .5*item['features']['long']) if method == 'equal' else item['features'][method]
                    np.testing.assert_array_equal(labels, decode(original, item['features']['rms'], item['config']))
                return labels
            summary, rows = common.score(name, items, predict)
            summary.update(method=method, whitening_strength=strength)
            summaries.append(summary)
            all_rows.extend(dict(setting=name, **row) for row in rows)
            print(name, summary['accuracy'], summary['near_accuracy'], flush=True)
    baseline = next(row for row in summaries if row['name'] == 'long_strength_0')
    for summary in summaries:
        summary['delta_pp'] = 100 * (summary['accuracy'] - baseline['accuracy'])
        summary['near_delta_pp'] = 100 * (summary['near_accuracy'] - baseline['near_accuracy'])
        summary['family_delta_pp'] = {k:100*(v['accuracy']-baseline['families'][k]['accuracy']) for k,v in summary['families'].items()}
        summary['passes_candidate_gate'] = summary['whitening_strength'] > 0 and summary['delta_pp'] >= .5 and min(summary['family_delta_pp'].values()) >= 0
    save_json(args.output / 'summary.json', summaries)
    with (args.output / 'per_recording.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)
    best = max((row for row in summaries if row['whitening_strength'] > 0), key=lambda row:row['accuracy'])
    save_json(args.output / 'result.json', dict(best=best,baseline=baseline,passes_candidate_gate=best['passes_candidate_gate'],test_access=False,promoted=False,identity_predictions_equal=True,analytic_tests='Zero-strength identity, silent finite-zero output, and constant-spectrum normalized invariance passed.',code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),common_sha256=hashlib.sha256(Path(common.__file__).read_bytes()).hexdigest()))
    print(json.dumps(dict(best=best['name'], accuracy=best['accuracy'], delta_pp=best['delta_pp'], passes_candidate_gate=best['passes_candidate_gate'])),flush=True)


if __name__ == '__main__':
    main()
