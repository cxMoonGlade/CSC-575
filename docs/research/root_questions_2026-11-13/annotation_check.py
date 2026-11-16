"""Inspect annotation coverage and saved prediction errors without changing models."""
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import mir_eval.chord

project = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(project))
from chordrec.data import reduce_label, load_reference

names = ['long_raw', 'projection_raw', 'long_viterbi', 'projection_viterbi']
inputs = {project / 'chordrec/data.py'}

def read(path):
    inputs.add(path)
    with path.open() as stream:
        return [(float(r['start']), float(r['end']), r['label']) for r in csv.DictReader(stream)]

def category(reference, prediction):
    prediction = reduce_label(prediction)
    if prediction == reference:
        return 'correct'
    if prediction in (None, 'N'):
        return 'unvoiced_or_invalid'
    return 'quality_wrong' if prediction.split(':')[0] == reference.split(':')[0] else 'root_wrong'

def count_changes(rows):
    counts = Counter()
    previous = None
    for start, end, original in rows:
        label = reduce_label(original)
        if previous is not None:
            prev_end, prev_label = previous
            if abs(start - prev_end) < 1e-7 and label not in (None, 'N') and prev_label not in (None, 'N') and label != prev_label:
                kind = 'same_root_quality' if label.split(':')[0] == prev_label.split(':')[0] else 'root_change'
                counts[kind] += 1
        previous = end, label
    return {key: counts[key] for key in ['root_change', 'same_root_quality']}

per_recording = {}
common = defaultdict(float)
by_type = defaultdict(lambda: defaultdict(float))
for folder in sorted((project / 'results/root_optimization/fast/predictions').iterdir()):
    if not folder.is_dir():
        continue
    reference = read(folder / 'reference.csv')
    streams = [reference] + [read(folder / (name + '.csv')) for name in names]
    indices = [0] * len(streams)
    local = defaultdict(float)
    original_duration = defaultdict(float)
    for start, end, label in reference:
        original_duration[label] += end - start
    while all(index < len(stream) for index, stream in zip(indices, streams)):
        current = [stream[index] for index, stream in zip(indices, streams)]
        start = max(row[0] for row in current)
        end = min(row[1] for row in current)
        ref = reduce_label(current[0][2])
        if end > start and ref not in (None, 'N'):
            duration = end - start
            cats = [category(ref, row[2]) for row in current[1:]]
            raw_label = current[0][2]
            _, bitmap, _ = mir_eval.chord.encode(raw_label, reduce_extended_chords=False)
            group = 'triad_pitch_set' if np.array_equal(bitmap, mir_eval.chord.QUALITIES[ref.split(':')[1]]) else 'extended_pitch_set'
            by_type[group]['reference_seconds'] += duration
            for name, cat in zip(names, cats):
                local[name + '/' + cat] += duration
                by_type[group][name + '/' + cat] += duration
            if all(cat in ('correct', 'quality_wrong') for cat in cats):
                common['seconds'] += duration
                for name, cat in zip(names, cats):
                    if cat == 'quality_wrong':
                        common[name + '/quality_wrong'] += duration
            if cats[2:] == ['correct', 'quality_wrong']:
                local['decoded_harm_seconds'] += duration
                local['decoded_harm_raw_categories/' + ' -> '.join(cats[:2])] += duration
                by_type[group]['decoded_harm_seconds'] += duration
            if cats[2:] == ['quality_wrong', 'correct']:
                local['decoded_repair_seconds'] += duration
                by_type[group]['decoded_repair_seconds'] += duration
        boundary = min(row[1] for row in current)
        indices = [index + (row[1] <= boundary) for index, row in zip(indices, current)]
    expected = sum(end - start for start, end, label in reference if reduce_label(label) not in (None, 'N'))
    for name in names:
        assert abs(sum(value for key, value in local.items() if key.startswith(name + '/')) - expected) < 1e-7
    per_recording[folder.name] = {'changes': count_changes(reference), 'original_label_seconds': dict(original_duration), 'error_seconds': dict(local)}

manifest_path = project / 'configs/guitarset_split.json'
inputs.add(manifest_path)
manifest = json.loads(manifest_path.read_text())
dev_counts = Counter()
dev_with_quality_change = []
for record in manifest['records']:
    if record['split'] != 'development':
        continue
    path = project / record['annotation']
    inputs.add(path)
    counts = count_changes(load_reference(path))
    dev_counts.update(counts)
    if counts['same_root_quality']:
        dev_with_quality_change.append(record['id'])

with (project / 'results/root_optimization/fast/summary.csv').open() as stream:
    summary = {row['method'] + '_' + row['decoder']: row for row in csv.DictReader(stream)}
checks = {}
for name in names:
    actual = sum(row['error_seconds'].get(name + '/quality_wrong', 0) for row in per_recording.values())
    difference = actual - float(summary[name]['same_root_wrong_quality_seconds'])
    assert abs(difference) < 1e-7
    checks[name] = difference
inputs.add(project / 'results/root_optimization/fast/summary.csv')
result = {'method_order': names, 'fast_reference_changes': dict(sum((Counter(r['changes']) for r in per_recording.values()), Counter())),
          'development_reference_changes': dict(dev_counts), 'development_recordings_with_same_root_quality_change': dev_with_quality_change,
          'common_root_correct_all_four': dict(common), 'by_reference_pitch_set': dict(by_type), 'per_recording': per_recording,
          'quality_error_check_difference_seconds': checks,
          'input_hashes': [{'path': str(path.relative_to(project)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(inputs)]}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: value for key, value in result.items() if key not in ('per_recording', 'input_hashes', 'development_recordings_with_same_root_quality_change')}, indent=2))
print('rock_6:', json.dumps(per_recording['rock_6']))
print('dev recordings with same-root quality changes:', len(dev_with_quality_change))
