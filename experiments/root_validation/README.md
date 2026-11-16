# Frozen comparison on the fast-tempo recordings

This runner compares the unchanged long-window baseline, note projection (primary candidate), and fundamental-only NNLS (secondary candidate) on all 64 IDMT `acoustic_mic/fast` recordings. Each piece ID matches a previously evaluated slow recording, so this tests transfer within the same repertoire. The fast recordings use their own chord annotations.

From the project root, this command checks inputs and saves metadata without recognition:

```bash
.venv/bin/python experiments/root_validation/compare.py \
  --project-root /path/to/Proj \
  --plan /path/to/plan.json \
  --data-root /path/to/Proj/docs/datasets/IDMT-SMT-Guitar-fast \
  --baseline /path/to/Proj/configs/frozen.json \
  --projection /path/to/Proj/configs/note_projection.json \
  --nnls /path/to/Proj/configs/note_nnls.json \
  --previous-selection /path/to/Proj/docs/datasets/IDMT-SMT-Guitar-fast/previous_selection.json \
  --output /path/to/new-preflight
```

For the frozen experiment, use a fresh output path and add `--run`. The runner requires the selection's evaluation-plan hash, all three configuration hashes, the five method hashes in that plan, and every validated audio/annotation hash to match before inference. Parsed references must also match the data validation manifest. No recordings are dropped because of their coverage.

Primary duration accuracy retains supported major/minor chords and the existing `NC`-to-`N` interpretation. Root accuracy and chord-only accuracy exclude reference `N`; predicting `N` on a reference chord is incorrect. Wrong-root duration, same-root quality errors, chord-to-N errors, near/stable accuracy, boundary scores and coverage are saved for every recording. Aggregates use duration sums, with undefined denominators recorded as null.

Each timed method loads and processes the full audio independently. Timing includes resampling, tuning, RMS, spectral features, dictionary construction, projection or NNLS, Viterbi decoding and interval construction. Imports, separate warm-up, raw diagnostics, scoring, hashes and output are excluded. Numerical thread pools are limited to one, jobs are shuffled with seed 20261110, and the OS disk cache is retained. The original configurations, data selection, validation, source files and execution order accompany the results.

The existing baseline and earlier results remain unchanged. This script performs one comparison and does not select parameters or replace the default method.

Six focused checks cover N-aware root scoring, all-N references, duration aggregation with zero coverage, input tampering, changed decoder settings, and changed method code. They use synthetic intervals and a synthetic WAV header; no recognizer inference is needed:

```bash
.venv/bin/python -m pytest tests/test_root_validation.py -q
```

To redraw the cases from saved predictions without running recognition, use a new output directory:

```bash
.venv/bin/python -m experiments.root_validation.figures --run results/root_optimization/fast --output results/fast_figures_repeat
```
