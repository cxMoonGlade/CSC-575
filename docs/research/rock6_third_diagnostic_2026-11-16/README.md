# Third-activation diagnostic for rock_6

The frozen projection recognizer made 9.89 s of decoded same-root quality errors on `rock_6`. During 7.85 s of these errors (79.36%), its correct major template still scored above the minor template at the reference root. The decoded label therefore does not identify the higher-scoring local quality.

| Same-root quality errors | Long STFT | Projection |
| --- | ---: | ---: |
| Raw predictions | 4.5269 s | 4.7359 s |
| Decoded predictions | 0 s | 9.8933 s |

Within projection's decoded quality errors, the major template scored higher for 7.8510 s and the minor template for 2.0424 s; there were no numerical ties. The full 24-template raw prediction was correct for 5.5522 s, had the wrong same-root quality for 1.6708 s, and had another root for 2.6703 s. These are separate partitions: a positive same-root margin does not ensure that the reference chord beats every competing root.

The mean quality margin over the decoded quality errors was −0.00591. Thus the duration with a positive margin alone does not determine the best sequence: the score magnitudes and switching costs also matter. This result supports examining decoder calibration and temporal score patterns. It does not establish whether the minor-third activations came from played notes, harmonics or feature leakage.

## Method and checks

The diagnostic uses the archived `source_snapshot` and `configurations.json` from `results/root_optimization/fast`. It recomputes Long STFT and Projection on the same 55.5 s acoustic-microphone recording at 120 BPM, retaining the frozen switching penalty of 4. The original A7, D7 and E7 annotations provide 48.0330 s of scoreable chord time and reduce to major triads.

For every reference/frame intersection, the script records normalized major- and minor-third activations, their template-score difference, raw and decoded labels, and competing roots. Durations use the recognizer's midpoint frame cells, split at the original annotation boundaries. A score difference within an absolute tolerance of 1e-12 is a numerical tie. Chroma values are feature activations, not acoustic energy or measured note amplitudes.

All four archived prediction tracks were reproduced exactly, including interval boundaries. The category durations matched the archived per-recording table exactly. Audio, annotation, source, configuration, frame-time, RMS and tuning checks passed, and package versions matched the original run. The archive contains no score arrays; the scores were recomputed with the verified implementation and checked against the third-activation formula. No settings were selected or changed.

## Files and reproduction

- [summary.json](run/summary.json): duration partitions and mean margins.
- [diagnostic figure](run/rock6_diagnostic.pdf): third activations, same-root margins, and reference/raw/decoded timelines.
- [reference_cells.csv](run/reference_cells.csv): exact scored intervals and competing-root scores.
- [frame_scores.csv](run/frame_scores.csv): all 24 template scores and normalized chroma for every frame.
- [features.npz](run/features.npz): full arrays, including frames outside the annotated span.
- [validation.json](run/validation.json) and [provenance.json](run/provenance.json): reproduction checks and input hashes.

From the project root, choose a new output directory:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/research/rock6_third_diagnostic_2026-11-16/rock6_diagnostic.py \
  --project-root . --output /tmp/rock6-diagnostic
```

`rock_6` was selected after the original comparison because it had the largest quality-error increase. These diagnostics explain the existing case; new pieces remain necessary for confirmation.
