"""Compare saved predictions on the same reference intervals; run no inference."""
import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def read_intervals(path, reduce_label):
    with path.open() as stream:
        rows = [(float(r['start']), float(r['end']), reduce_label(r['label']))
                for r in csv.DictReader(stream)]
    for index, (start, end, _) in enumerate(rows):
        assert math.isfinite(start) and math.isfinite(end) and end > start, path
        if index:
            assert start >= rows[index - 1][1] - 1e-9, path
    return rows


def category(reference, prediction):
    if prediction == reference:
        return 'correct'
    if prediction is None:
        return 'invalid'
    if prediction == 'N':
        return 'predicted_N'
    if prediction.split(':')[0] == reference.split(':')[0]:
        return 'quality_wrong'
    return 'root_wrong'


def compare(root, first, second, reduce_label, inputs):
    matrix = defaultdict(float)
    files = {}
    for folder in sorted(root.iterdir()):
        if not folder.is_dir() or not (folder / 'reference.csv').exists():
            continue
        paths = [folder / name for name in ['reference.csv', first + '.csv', second + '.csv']]
        inputs.update(paths)
        reference, left, right = [read_intervals(p, reduce_label) for p in paths]
        local = defaultdict(float)
        i = j = k = 0
        while i < len(reference) and j < len(left) and k < len(right):
            rr, aa, bb = reference[i], left[j], right[k]
            start, end = max(rr[0], aa[0], bb[0]), min(rr[1], aa[1], bb[1])
            if end > start and rr[2] not in (None, 'N'):
                key = category(rr[2], aa[2]), category(rr[2], bb[2])
                matrix[key] += end - start
                local[key] += end - start
            boundary = min(rr[1], aa[1], bb[1])
            i += rr[1] <= boundary
            j += aa[1] <= boundary
            k += bb[1] <= boundary
        expected = sum(end - start for start, end, label in reference if label not in (None, 'N'))
        assert abs(sum(local.values()) - expected) < 1e-7, folder
        files[folder.name] = {' -> '.join(key): value for key, value in local.items()}
    shared = sum(value for (a, b), value in matrix.items()
                 if a in ('correct', 'quality_wrong') and b in ('correct', 'quality_wrong'))
    return {
        'first': first, 'second': second,
        'reference_chord_seconds': sum(matrix.values()),
        'matrix_seconds': {' -> '.join(key): value for key, value in matrix.items()},
        'both_roots_correct_seconds': shared,
        'quality_error_seconds_on_shared_root_correct': {
            'first': matrix['quality_wrong', 'correct'] + matrix['quality_wrong', 'quality_wrong'],
            'second': matrix['correct', 'quality_wrong'] + matrix['quality_wrong', 'quality_wrong']},
        'per_recording': files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    sys.path.insert(0, str(project))
    from chordrec.data import reduce_label
    source = project / 'results/root_optimization/fast'
    summary_path = source / 'summary.csv'
    with summary_path.open() as stream:
        summary = {r['method'] + '_' + r['decoder']: r for r in csv.DictReader(stream)}
    inputs = {summary_path, project / 'chordrec/data.py'}
    pairs = [('long_viterbi', 'projection_viterbi'), ('projection_viterbi', 'harmonic_viterbi'),
             ('long_raw', 'projection_raw'), ('projection_raw', 'projection_viterbi')]
    results = [compare(source / 'predictions', a, b, reduce_label, inputs) for a, b in pairs]
    checks = []
    fields = {'correct': 'chord_correct_seconds', 'quality_wrong': 'same_root_wrong_quality_seconds',
              'root_wrong': 'other_root_seconds', 'predicted_N': 'chord_to_n_seconds',
              'invalid': 'invalid_prediction_seconds'}
    for result in results:
        for side, name in enumerate([result['first'], result['second']]):
            margins = defaultdict(float)
            for key, value in result['matrix_seconds'].items():
                margins[key.split(' -> ')[side]] += value
            differences = {category_name: margins[category_name] - float(summary[name][field])
                           for category_name, field in fields.items()}
            differences['total'] = result['reference_chord_seconds'] - float(summary[name]['chord_scoreable_seconds'])
            maximum = max(abs(value) for value in differences.values())
            assert maximum < 1e-7, (name, differences)
            checks.append({'pair': [result['first'], result['second']], 'method': name,
                           'maximum_absolute_difference_seconds': maximum, 'passed': True})
    manifest = [{'path': str(path.relative_to(project)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                for path in sorted(inputs)]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in [('paired_errors.json', results), ('validation.json', checks), ('input_hashes.json', manifest)]:
        (args.output_dir / name).write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps({'pairs': len(results), 'checks': len(checks), 'inputs': len(manifest),
                      'maximum_difference_seconds': max(c['maximum_absolute_difference_seconds'] for c in checks)}))


if __name__ == '__main__':
    main()
