"""Validate frozen note front ends on the IDMT acoustic-microphone fast branch."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import random
import re
import sys
import time

METHODS = ('long', 'projection', 'harmonic')
EXPECTED_SHARED = dict(sample_rate=22050, hop_length=512, n_fft_long=8192,
                       midi_min=36, n_octaves=5, silence_db=-45.0,
                       switch_penalty=4.0, boundary_tolerance=0.1,
                       near_boundary_seconds=0.2)
PREFIX = 'IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/fast/'
SEED = 20261110


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text())


def checked_path(root, member, prefix=PREFIX):
    relative = PurePosixPath(member)
    if relative.is_absolute() or '..' in relative.parts or not member.startswith(prefix):
        raise ValueError(f'Path outside the selected archive branch: {member}')
    resolved = (root / member).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError(f'Missing or escaped input file: {member}')
    return resolved


def check_configs(paths):
    configs = {method:load_json(path) for method, path in paths.items()}
    for method, config in configs.items():
        if config.get('status') != 'frozen':
            raise ValueError(f'{method} configuration is not frozen')
        if any(config.get(key) != value for key, value in EXPECTED_SHARED.items()):
            raise ValueError(f'{method} differs from the frozen shared settings')
        if config.get('tuning') != configs['long'].get('tuning'):
            raise ValueError('The tuning policy differs across methods')
    for method, label in (('projection', 'note_projection'), ('harmonic', 'note_nnls')):
        if configs[method].get('method') != label or configs[method].get('harmonic_decay') != 0.0:
            raise ValueError(f'{method} must use its frozen fundamental-only configuration')
    return configs


def check_plan(project_root, plan_path, selection, config_paths):
    """Link the data selection to the exact previously frozen algorithms."""
    plan = load_json(plan_path)
    if sha256(plan_path) != selection['evaluation_plan_sha256']:
        raise ValueError('The selected data refer to a different evaluation plan')
    if plan.get('methods') != list(METHODS) or plan.get('primary_candidate') != 'projection' or plan.get('order_seed') != SEED:
        raise ValueError('The comparison differs from the prospective methods or ordering')
    expected_configs = {'long':'configs/frozen.json', 'projection':'configs/note_projection.json',
                        'harmonic':'configs/note_nnls.json'}
    if set(plan['config_sha256']) != set(expected_configs.values()):
        raise ValueError('Plan must specify all three frozen configuration hashes')
    for method, relative in expected_configs.items():
        if sha256(config_paths[method]) != plan['config_sha256'][relative]:
            raise ValueError(f'Configuration changed after the prospective plan: {method}')
    required_sources = {'audio.py','model.py','harmonic.py','projection.py','idmt.py'}
    if not required_sources.issubset(plan['method_sha256']):
        raise ValueError('The plan is missing required method hashes')
    for name, expected in plan['method_sha256'].items():
        if Path(name).name != name or sha256(project_root/'chordrec'/name) != expected:
            raise ValueError(f'Method source changed after the prospective plan: {name}')
    return plan


def prepare_record(data_root, selected, validated, previous):
    """Check source bytes and annotation meaning without extracting features."""
    import numpy as np
    import soundfile as sf
    from chordrec.data import reduce_label
    from chordrec.idmt import load_chords
    member = selected['archive_path']
    if not re.fullmatch(r'[A-Za-z0-9_-]+', selected['piece_id']):
        raise ValueError('Piece ID must be one safe filename component')
    if PurePosixPath(member).suffix.lower() != '.wav':
        raise ValueError('The selected recording must be a WAV file')
    audio = checked_path(data_root, member)
    piece = selected['piece_id']
    if re.sub(r'_\d+(?:\.\d+)?BPM$', '', audio.stem) != piece:
        raise ValueError('Audio filename and selected piece ID differ')
    slow_member = previous['archive_path']
    if (not slow_member.startswith('IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/slow/')
            or re.sub(r'_\d+(?:\.\d+)?BPM$', '', PurePosixPath(slow_member).stem) != piece):
        raise ValueError('Previous slow filename does not match the paired piece ID')
    annotation_member = str(PurePosixPath(member).parent.parent / 'annotation/chords' /
                            (PurePosixPath(member).stem + '.csv'))
    annotation = checked_path(data_root, annotation_member)
    if selected.get('annotation', annotation_member) != annotation_member:
        raise ValueError('Prospective annotation path differs from the audio pairing')
    if selected.get('annotation_sha256', validated['annotation_sha256']) != validated['annotation_sha256']:
        raise ValueError('Prospective and validated annotation hashes differ')
    if validated['audio'] != member or validated['annotation'] != annotation_member:
        raise ValueError('Validated paths differ from the prospective selection')
    for path, key in ((audio, 'audio_sha256'), (annotation, 'annotation_sha256')):
        if sha256(path) != validated[key]:
            raise ValueError(f'Input differs from its validated SHA256: {path}')
    if selected.get('file_bytes', audio.stat().st_size) != audio.stat().st_size:
        raise ValueError(f'Audio size differs from the archive manifest: {audio}')
    reference, symbols = load_chords(annotation)
    duration = sf.info(audio).duration
    expected_duration = float(validated['duration_seconds'])
    if abs(duration-expected_duration) > 1e-12:
        raise ValueError('Audio duration differs from the validated header')
    expected_reference = validated['reference']
    if len(reference) != len(expected_reference) or any(
            label != expected[2] or not np.allclose((a, b), expected[:2], atol=1e-12, rtol=0)
            for (a, b, label), expected in zip(reference, expected_reference)):
        raise ValueError('Parsed chord intervals differ from the validated reference')
    if not reference or reference[0][0] < 0 or reference[-1][1] > duration:
        raise ValueError('Reference lies outside the recording')
    reduced = [(a, b, reduce_label(label)) for a, b, label in reference]
    span = reference[-1][1] - reference[0][0]
    piece = selected['piece_id']
    genre = PurePosixPath(member[len(PREFIX):]).parts[0]
    audit = dict(recording=piece, group=piece, tempo_branch='fast', genre=genre,
        audio=member, annotation=annotation_member, previous_slow_audio=previous['archive_path'],
        audio_seconds=duration, annotated_span_seconds=span, unannotated_seconds=duration-span,
        supported_chord_seconds=sum(b-a for a,b,label in reduced if label not in (None,'N')),
        no_chord_seconds=sum(b-a for a,b,label in reduced if label=='N'),
        unsupported_reference_seconds=sum(b-a for a,b,label in reduced if label is None),
        first_annotated_beat=reference[0][0], last_annotated_beat=reference[-1][1],
        audio_sha256=validated['audio_sha256'], annotation_sha256=validated['annotation_sha256'])
    return dict(recording=piece, group=piece, genre=genre, audio=audio, annotation=annotation,
                reference=reference, duration=duration, audit=audit, symbols=symbols)


def prepare(args):
    """Verify the complete prospective fast-branch selection and its paired IDs."""
    selection_path = args.data_root/'prospective_selection.json'
    validation_path = args.data_root/'validation_manifest.json'
    selection, validation = load_json(selection_path), load_json(validation_path)
    if sha256(selection_path) != validation['source_selection_sha256']:
        raise ValueError('Prospective selection changed after validation')
    if (selection.get('capture_stream'), selection.get('tempo_branch')) != ('acoustic_mic','fast'):
        raise ValueError('Expected the prospectively selected acoustic_mic/fast branch')
    selected = selection['recordings']
    validated_rows = validation['recordings']
    if len(selected) != 64 or len({r['piece_id'] for r in selected}) != 64:
        raise ValueError('Expected all 64 distinct prospective piece IDs')
    if len({r['archive_path'] for r in selected}) != 64:
        raise ValueError('Selected audio paths must be distinct')
    validated = {r['piece_id']:r for r in validated_rows}
    if len(validated_rows) != 64 or set(validated) != {r['piece_id'] for r in selected}:
        raise ValueError('Validated and prospectively selected IDs differ')
    previous_selection = load_json(args.previous_selection)
    if (previous_selection.get('capture_stream'), previous_selection.get('tempo_branch')) != ('acoustic_mic','slow'):
        raise ValueError('Previous metadata must describe the acoustic_mic/slow branch')
    previous = {r['piece_id']:r for r in previous_selection['recordings']}
    if len(previous_selection['recordings']) != 64 or set(previous) != set(validated):
        raise ValueError('Slow and fast branches do not contain the same piece IDs')
    prepared = [prepare_record(args.data_root, r, validated[r['piece_id']], previous[r['piece_id']])
                for r in sorted(selected, key=lambda record:record['piece_id'])]
    return selection, validation, prepared, (selection_path, validation_path, args.previous_selection)


def score_prediction(reference, prediction, duration):
    """Keep N in the primary score and exclude it from root and chord-only scores."""
    from chordrec.data import reduce_label
    from chordrec.error_analysis import decompose
    from chordrec.evaluate import evaluate
    from chordrec.regions import region_scores
    metrics = evaluate(reference, prediction, duration, tolerance=.1)
    regions = region_scores(reference, prediction, duration, .2)
    chord_reference = [(a,b,'X' if reduce_label(label)=='N' else label) for a,b,label in reference]
    chord = evaluate(chord_reference, prediction, duration, tolerance=.1)
    decomposition = decompose(reference, prediction, duration, .2)
    categories = decomposition['regions']['all']['categories_seconds']
    chord_seconds = chord['scoreable_seconds']
    root_correct = chord['correct_seconds'] + categories['same_root_wrong_quality']
    n_seconds = metrics['scoreable_seconds'] - chord_seconds
    n_correct = metrics['correct_seconds'] - chord['correct_seconds']
    if abs(root_correct + categories['other_root'] + categories['chord_to_n']
           + categories['invalid_prediction'] - chord_seconds) > 1e-7:
        raise AssertionError('Root-error durations do not partition chord reference time')
    return dict(**metrics,
        **{key:regions[key] for key in ('near_correct_seconds','near_scoreable_seconds','near_accuracy',
            'stable_correct_seconds','stable_scoreable_seconds','stable_accuracy')},
        chord_correct_seconds=chord['correct_seconds'], chord_scoreable_seconds=chord_seconds,
        chord_accuracy=chord['duration_accuracy'], root_correct_seconds=root_correct,
        root_scoreable_seconds=chord_seconds, root_accuracy=root_correct/chord_seconds if chord_seconds else None,
        no_chord_seconds=n_seconds, no_chord_correct_seconds=n_correct,
        no_chord_accuracy=n_correct/n_seconds if n_seconds else None,
        **{f'{key}_seconds':value for key,value in categories.items() if key!='correct'})


def aggregate(rows):
    keys = ('audio_seconds','correct_seconds','scoreable_seconds','excluded_seconds',
            'boundary_matches','reference_boundaries','predicted_boundaries',
            'near_correct_seconds','near_scoreable_seconds','stable_correct_seconds','stable_scoreable_seconds',
            'chord_correct_seconds','chord_scoreable_seconds','root_correct_seconds','root_scoreable_seconds',
            'no_chord_seconds','no_chord_correct_seconds','reference_n_error_seconds','other_root_seconds',
            'same_root_wrong_quality_seconds','chord_to_n_seconds','invalid_prediction_seconds')
    result = {key:sum(r[key] for r in rows) for key in keys}
    result.update(recordings=len(rows), scoreable_recordings=sum(r['scoreable_seconds']>0 for r in rows),
                  chord_scoreable_recordings=sum(r['chord_scoreable_seconds']>0 for r in rows))
    for prefix in ('', 'near_', 'stable_', 'chord_', 'root_'):
        denominator = result[prefix+'scoreable_seconds']
        result['duration_accuracy' if not prefix else prefix+'accuracy'] = (
            result[prefix+'correct_seconds']/denominator if denominator else None)
    result['coverage'] = result['scoreable_seconds']/result['audio_seconds'] if result['audio_seconds'] else None
    result['no_chord_accuracy'] = (result['no_chord_correct_seconds']/result['no_chord_seconds']
                                    if result['no_chord_seconds'] else None)
    hits, refs, preds = (result[key] for key in ('boundary_matches','reference_boundaries','predicted_boundaries'))
    errors = [value for r in rows for value in r['boundary_timing_errors_seconds']]
    result.update(boundary_precision=hits/preds if preds else 0.0,
        boundary_recall=hits/refs if refs else 0.0,
        boundary_f1=2*hits/(refs+preds) if refs+preds else 0.0,
        boundary_mae_seconds=sum(abs(x) for x in errors)/hits if hits else None,
        boundary_mean_signed_error_seconds=sum(errors)/hits if hits else None)
    accuracies = [r['duration_accuracy'] for r in rows if r['duration_accuracy'] is not None]
    times = [r['runtime_seconds'] for r in rows if r['runtime_seconds'] is not None]
    result.update(mean_recording_accuracy=sum(accuracies)/len(accuracies) if accuracies else None,
        total_runtime_seconds=sum(times) if times else None,
        realtime_factor=sum(times)/result['audio_seconds'] if times and result['audio_seconds'] else None)
    return result


def protocol():
    return dict(order_seed=SEED, primary_candidate='projection', secondary_candidate='harmonic (fundamental-only NNLS)',
        baseline='long', primary_metric='Exact duration major/minor accuracy including reference N.',
        root_metric='Correct root, ignoring major/minor quality, over supported reference chord duration only. Reference N is excluded; predicting N on a chord is an error.',
        reference_policy='Between first and last annotated beats only; NC is interpreted as N under the unchanged adapter; unsupported symbols and unannotated audio are excluded.',
        runtime='Uncached audio loading, resampling, tuning, RMS, required spectral features, dictionary construction, projection or NNLS, Viterbi decoding and interval construction. Imports, warm-up, raw diagnostics, scoring, hashes and output are excluded. The OS disk cache is retained.',
        grouping='Each fast piece ID is paired with the same ID in the already evaluated slow branch. Recordings are new tempo renditions, not independent new compositions or unseen progressions.',
        decision='One frozen comparison. No parameter search, threshold adjustment or automatic default replacement follows this test.')


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True, help='Prospective frozen comparison plan')
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--projection', type=Path, required=True)
    parser.add_argument('--nnls', type=Path, required=True)
    parser.add_argument('--previous-selection', type=Path, required=True,
                        help='Previous slow-branch metadata, used only to verify paired piece IDs')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run', action='store_true', help='Run inference after preflight; otherwise save preflight only')
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    for key in ('project_root','plan','data_root','baseline','projection','nnls','previous_selection','output'):
        setattr(args,key,getattr(args,key).resolve())
    if args.output.exists():
        raise FileExistsError(f'Choose a new output directory: {args.output}')
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ.pop('LIBROSA_CACHE_DIR',None)
    sys.path.insert(0,str(args.project_root))
    import numpy as np
    from threadpoolctl import threadpool_info, threadpool_limits
    from chordrec.isolated_compare import predict
    from chordrec.run import save_csv, save_intervals, save_json
    config_paths = {'long':args.baseline,'projection':args.projection,'harmonic':args.nnls}
    configs = check_configs(config_paths)
    selection, validation, records, manifest_paths = prepare(args)
    plan = check_plan(args.project_root,args.plan,selection,config_paths)
    input_paths = [args.plan] + list(manifest_paths) + list(config_paths.values()) + [r[key] for r in records for key in ('audio','annotation')]
    input_hashes = {str(path):sha256(path) for path in input_paths}
    source_paths = sorted((args.project_root/'chordrec').glob('*.py'))
    source_hashes = {f'chordrec/{path.name}':sha256(path) for path in source_paths}
    source_hashes['compare.py'] = sha256(Path(__file__))
    args.output.mkdir(parents=True)
    save_json(args.output/'configurations.json',configs)
    save_json(args.output/'evaluation_plan.json',plan)
    save_json(args.output/'selection.json',selection)
    save_json(args.output/'previous_selection.json',load_json(args.previous_selection))
    save_json(args.output/'input_validation.json',validation)
    save_json(args.output/'inputs.json',input_hashes)
    save_json(args.output/'sources.json',source_hashes)
    for path in source_paths+[Path(__file__)]:
        relative = Path('chordrec')/path.name if path in source_paths else Path('compare.py')
        target = args.output/'source_snapshot'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(path.read_bytes())
    symbols = Counter(pair for r in records for pair in r['symbols'])
    save_json(args.output/'symbol_mapping.json',[
        dict(raw=a,converted=b,occurrences=n) for (a,b),n in sorted(symbols.items())])
    save_json(args.output/'annotation_audit.json',[r['audit'] for r in records])
    save_json(args.output/'protocol.json',protocol())
    preflight = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),recordings=len(records),
        input_hashes_verified=True, prospective_selection_verified=True, paired_piece_ids_verified=True,
        inference_performed=False, primary_candidate='projection',
        audio_seconds=sum(r['duration'] for r in records),
        chord_seconds=sum(r['audit']['supported_chord_seconds'] for r in records),
        no_chord_seconds=sum(r['audit']['no_chord_seconds'] for r in records))
    save_json(args.output/'preflight.json',preflight)
    if not args.run:
        print(json.dumps(preflight,indent=2),flush=True)
        return preflight
    with threadpool_limits(limits=1):
        started = time.perf_counter()
        for method in METHODS:
            predict(records[0]['audio'],method,configs[method])
        warmup = time.perf_counter()-started
        save_json(args.output/'warmup.json',dict(recording=records[0]['recording'],seconds=warmup))
        pools = threadpool_info()
        if any(pool['num_threads'] != 1 for pool in pools):
            raise RuntimeError('A numerical thread pool exceeds the single-thread limit')
        save_json(args.output/'environment.json',dict(python=platform.python_version(),platform=platform.platform(),
            packages={name:importlib.metadata.version(name) for name in
                ('numpy','scipy','librosa','soundfile','mir_eval','threadpoolctl')},
            thread_environment={key:os.environ.get(key) for key in
                ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS')},threadpools=pools))
        jobs = [(record,method) for record in records for method in METHODS]
        random.Random(SEED).shuffle(jobs)
        order = [dict(recording=r['recording'],group=r['group'],method=m) for r,m in jobs]
        save_json(args.output/'run_order.json',order)
        rows, grids = [], {}
        for index,(record,method) in enumerate(jobs,1):
            features,decoded,raw,seconds = predict(record['audio'],method,configs[method])
            if abs(features['duration']-record['duration']) > 1e-9:
                raise ValueError('Feature duration differs from the checked audio header')
            grid = dict(frames=len(features['times']),tuning=features['tuning'],
                times_sha256=hashlib.sha256(np.asarray(features['times']).tobytes()).hexdigest(),
                rms_sha256=hashlib.sha256(np.asarray(features['rms']).tobytes()).hexdigest())
            if record['recording'] in grids and grids[record['recording']] != grid:
                raise ValueError('Methods do not share the same time grid, RMS and tuning')
            grids[record['recording']] = grid
            folder = args.output/'predictions'/record['recording']
            save_intervals(folder/'reference.csv',record['reference'])
            for decoder,prediction in (('viterbi',decoded),('raw',raw)):
                metrics = score_prediction(record['reference'],prediction,record['duration'])
                rows.append(dict(recording=record['recording'],group=record['group'],genre=record['genre'],
                    tempo_branch='fast',method=method,decoder=decoder,audio_seconds=record['duration'],
                    runtime_seconds=seconds if decoder=='viterbi' else None,**metrics))
                save_intervals(folder/f'{method}_{decoder}.csv',prediction)
            save_json(folder/f'{method}_features.json',dict(**grid,diagnostics=features.get('diagnostics',{})))
            save_csv(args.output/'per_recording.csv',rows)
            if index%16 == 0 or index==len(jobs):
                print(f'Completed {index}/{len(jobs)} frozen audio-to-label runs',flush=True)
    for path,expected in input_hashes.items():
        if sha256(path) != expected:
            raise ValueError(f'Input changed during the comparison: {path}')
    for path in source_paths:
        if sha256(path) != source_hashes[f'chordrec/{path.name}']:
            raise ValueError(f'Source changed during the comparison: {path}')
    if sha256(Path(__file__)) != source_hashes['compare.py']:
        raise ValueError('Comparison runner changed during the comparison')
    summaries=[]
    for method in METHODS:
        for decoder in ('raw','viterbi'):
            part=[r for r in rows if r['method']==method and r['decoder']==decoder]
            summaries.append(dict(method=method,decoder=decoder,**aggregate(part),
                genres={genre:aggregate([r for r in part if r['genre']==genre]) for genre in sorted({r['genre'] for r in part})}))
    save_json(args.output/'summary.json',summaries)
    save_csv(args.output/'summary.csv',[{key:value for key,value in row.items() if key!='genres'} for row in summaries])
    save_json(args.output/'run.json',dict(completed_at_utc=datetime.now(timezone.utc).isoformat(),
        recordings=len(records),audio_to_label_runs=len(jobs),result_rows=len(rows),warmup_seconds=warmup,
        order_seed=SEED,all_input_and_source_hashes_unchanged=True,protocol=protocol()))
    print(json.dumps(summaries,indent=2),flush=True)
    return summaries


if __name__ == '__main__':
    main()
