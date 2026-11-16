# Initial development run

November 7, 2026. Twenty GuitarSet accompaniment recordings from performer `00`, using progressions 1 and 2 and performed chord labels. No test recording was scored.

Command from the project root:

```bash
.venv/bin/python -m chordrec run --performer 00 --output results/dev_initial
```

Use a fresh output directory to repeat the run.

- `summary.csv` / `summary.json`: aggregate results, with and without decoding.
- `per_recording.csv`: scores, coverage, timing errors, and full inference runtime by recording.
- `predictions/`: reference labels and each method's timestamped predictions.
- `examples/`: chroma/weight/timeline plots and an HTML audio player.
- `config.json`, `selection.json`, `environment.json`: settings, selected recordings, and software versions.
- `source_snapshot/` and `sources.json`: the exact recognition/evaluation code used for this run.
- `adaptive_diagnostics.json`: high short-window weighting occurs on 78.91% of frames; this does not establish its cause.

The fixed-weight method uses 0.5 in this initial run and duplicates equal fusion. Parameters are not yet selected or frozen. Accuracy excludes unsupported reference chords; supported labels cover 75.69% of the audio. Boundaries are measured against the dataset's score-derived segmentation.

The plot/player were subsequently regenerated with corrected context labels and player event handling; `presentation_sources.json` records those code versions. A later resampling endpoint fix affects none of these 20 recordings.
