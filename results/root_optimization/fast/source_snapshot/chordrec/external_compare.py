"""Compare two frozen configurations on the prospectively selected IDMT subset."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import platform
from pathlib import Path
import random
import time

import numpy as np
import soundfile as sf

from .data import reduce_label
from .evaluate import evaluate
from .idmt import load_chords
from .regions import region_scores
from .run import recognize, save_csv, save_json, save_intervals, summarize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError('Choose a new output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    selection_path = args.data_root / 'prospective_selection.json'
    selection = json.loads(selection_path.read_text())
    configs = {'long': json.loads(args.baseline.read_text()),
               'fixed': json.loads(args.candidate.read_text())}
    if any(c.get('status') != 'frozen' for c in configs.values()):
        raise ValueError('Both configurations must be frozen before evaluation')
    expected_shared = dict(sample_rate=22050, hop_length=512, n_fft_long=8192,
                           midi_min=36, n_octaves=5, silence_db=-45.0,
                           switch_penalty=4.0, boundary_tolerance=0.1)
    for method, config in configs.items():
        if any(config.get(key) != value for key, value in expected_shared.items()):
            raise ValueError(f'{method} differs from the frozen shared settings')
    if configs['fixed'].get('n_fft_short') != 4096 or configs['fixed'].get('fixed_weight') != 0.2:
        raise ValueError('Expected the frozen 4096/8192 candidate with short weight 0.2')
    if configs['long'].get('tuning') != configs['fixed'].get('tuning'):
        raise ValueError('Both methods must use the same tuning policy')
    records = selection['recordings']
    if len(records) != 64 or len({record['piece_id'] for record in records}) != 64:
        raise ValueError('Expected 64 distinct prospectively selected pieces')
    if selection.get('capture_stream') != 'acoustic_mic' or selection.get('tempo_branch') != 'slow':
        raise ValueError('Expected the prospectively selected acoustic_mic/slow stream')
    prefix = 'IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/slow/'
    if any(not record['archive_path'].startswith(prefix) or '..' in Path(record['archive_path']).parts for record in records):
        raise ValueError('A selected path is outside the declared capture stream')
    prepared = []
    annotation_audit = []
    symbols = Counter()
    for record in records:
        audio = args.data_root / record['archive_path']
        annotation = audio.parent.parent / 'annotation/chords' / (audio.stem + '.csv')
        reference, pairs = load_chords(annotation)
        duration = sf.info(audio).duration
        if not reference or reference[-1][1] > duration:
            raise ValueError(f'Invalid annotation extent: {annotation}')
        symbols.update(pairs)
        reduced = [(a, b, reduce_label(label)) for a, b, label in reference]
        span = reference[-1][1] - reference[0][0]
        annotation_audit.append(dict(
            recording=record['piece_id'], audio_seconds=duration,
            first_annotated_beat=reference[0][0], last_annotated_beat=reference[-1][1],
            annotated_span_seconds=span, unannotated_seconds=duration-span,
            supported_chord_seconds=sum(b-a for a,b,label in reduced if label not in (None,'N')),
            no_chord_seconds=sum(b-a for a,b,label in reduced if label=='N'),
            unsupported_reference_seconds=sum(b-a for a,b,label in reduced if label is None),
            annotation_sha256=hashlib.sha256(annotation.read_bytes()).hexdigest(),
        ))
        prepared.append((record, audio, reference, duration))
    save_json(args.output / 'configurations.json', configs)
    save_json(args.output / 'selection.json', selection)
    save_json(args.output / 'symbol_mapping.json', [dict(raw=a,converted=b,occurrences=n) for (a,b),n in sorted(symbols.items())])
    save_json(args.output / 'annotation_audit.json', dict(
        policy='Beat intervals only. NC is interpreted as N, although the guide does not define NC. Unsupported labels remain excluded; no prefix or tail labels are added.',
        primary_metric='Duration accuracy includes supported chords and N.',
        chord_only_diagnostic='Exclude reference N intervals without changing model predictions.',
        recordings=annotation_audit,
    ))
    source_files = sorted(Path(__file__).parent.glob('*.py'))
    save_json(args.output / 'sources.json', {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files})
    for source in source_files:
        destination = args.output / 'source_snapshot' / 'chordrec' / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    save_json(args.output / 'environment.json', dict(
        python=platform.python_version(), platform=platform.platform(),
        packages={name:importlib.metadata.version(name) for name in
                  ('numpy','scipy','librosa','soundfile','mir_eval','matplotlib')},
        thread_environment={key:os.environ.get(key) for key in
                            ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
    ))
    validation_path = args.data_root / 'validation_manifest.json'
    if validation_path.exists():
        (args.output / 'input_validation.json').write_bytes(validation_path.read_bytes())
    save_json(args.output / 'inputs.json', {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (selection_path,args.baseline,args.candidate)})
    started = time.perf_counter()
    for method, config in configs.items():
        recognize(prepared[0][1], method, config)
    warmup = time.perf_counter() - started
    rng = random.Random(20261107)
    rng.shuffle(prepared)
    rows = []
    order = []
    for i, (record, audio, reference, duration) in enumerate(prepared,1):
        folder = args.output / 'predictions' / record['piece_id']
        save_intervals(folder / 'reference.csv', reference)
        methods = list(configs)
        rng.shuffle(methods)
        for method in methods:
            features, weights, decoded, raw, seconds = recognize(audio, method, configs[method])
            if abs(features['duration'] - duration) > 1e-9:
                raise ValueError('Decoded audio duration differs from its validated header')
            order.append(dict(recording=record['piece_id'],method=method))
            for decoder, prediction in [('viterbi',decoded),('raw',raw)]:
                metrics = evaluate(reference,prediction,duration,tolerance=.1)
                regional = region_scores(reference,prediction,duration,.2)
                chord_reference = [(a,b,'X' if label=='N' else label) for a,b,label in reference]
                chord_metrics = evaluate(chord_reference,prediction,duration,tolerance=.1)
                row = dict(recording=record['piece_id'],group=record['piece_id'],split='external',method=method,decoder=decoder,audio_seconds=duration,runtime_seconds=seconds if decoder=='viterbi' else None,**metrics)
                row.update({key:regional[key] for key in ('near_correct_seconds','near_scoreable_seconds','near_accuracy','stable_correct_seconds','stable_scoreable_seconds','stable_accuracy')})
                row.update(chord_correct_seconds=chord_metrics['correct_seconds'],chord_scoreable_seconds=chord_metrics['scoreable_seconds'])
                rows.append(row)
                save_intervals(folder / f'{method}_{decoder}.csv',prediction)
        save_csv(args.output / 'per_recording.csv',rows)
        print(f'[{i}/64] {record["piece_id"]}',flush=True)
    summary = summarize(rows)
    for item in summary:
        part = [r for r in rows if r['method']==item['method'] and r['decoder']==item['decoder']]
        for region in ['near','stable','chord']:
            numerator = sum(r[region+'_correct_seconds'] for r in part)
            denominator = sum(r[region+'_scoreable_seconds'] for r in part)
            item.update({region+'_correct_seconds':numerator,region+'_scoreable_seconds':denominator,region+'_accuracy':numerator/denominator if denominator else None})
    save_json(args.output / 'summary.json',summary)
    save_csv(args.output / 'summary.csv',summary)
    save_json(args.output / 'run.json',dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),recordings=len(records),audio_seconds=sum(x[3] for x in prepared),warmup_seconds=warmup,run_order=order,runtime_definition='Serial audio-to-label wall time including file reading, resampling, tuning, required transforms, fusion, decoding and interval construction. No feature cache; imports, warm-up, scoring and output are excluded.',reference_policy='Between first and last annotated beats; NC is interpreted as N although the guide does not define NC. Unknown symbols remain X. No prefix or tail extrapolation. Chord-only scores exclude reference N intervals.'))
    print(json.dumps(summary,indent=2),flush=True)

if __name__ == '__main__':
    main()
