# Development experiments

These scripts compare window length, spectral whitening, and boundary refinement on the 119 GuitarSet development recordings. All comparisons use the frozen tuning, silence rule, and Viterbi penalty of 4. Duration-weighted chord accuracy is the selection metric; accuracy within 0.2 seconds of reference changes is a diagnostic.

The four branches evaluated 30 settings, including repeated controls. None met the selection rule: at least 0.5 percentage points above the 8,192-sample baseline, with no decrease in either progression family.

| Branch | Best candidate | Accuracy (%) | Change from baseline (percentage points) |
| --- | --- | ---: | ---: |
| Baseline | 8,192 samples | 71.9654 | — |
| Resolution | 4,096/8,192 fusion, short weight 0.2 | 72.2238 | +0.2584 |
| Whitening | Long window, strength 0.5 | 71.5489 | −0.4165 |
| Boundary refinement | Radius 0.2 s, short weight 0.5 | 72.0030 | +0.0376 |
| Longer resolution | 16,384 samples | 71.9073 | −0.0581 |

The small development gain does not establish a new validated default. The project retains the 8,192-sample baseline.

From the repository root, with the project dependencies and GuitarSet files installed:

```bash
python experiments/optimization_v2/common.py
python experiments/optimization_v2/resolution/run.py
python experiments/optimization_v2/whitening/run.py
python experiments/optimization_v2/boundary/run.py
python experiments/optimization_v2/long_resolution/run.py
```

The first command prepares `cache/` and `baseline.json`; the others write to `runs/<branch>/`. Use `--work-dir PATH` for a fresh run, `--cache-dir PATH` to reuse features, and `--project-root PATH` when this folder is outside the repository. Each runner also accepts `--output PATH`. Existing results are preserved. Cached scoring timings exclude feature extraction and do not measure complete inference cost.

`original_sources.json` records the original source hashes. `portability_validation.json` records exact score agreement on three development recordings after the path changes.

The optional `data_sources/` scripts retrieve the fixed 64-recording IDMT acoustic-microphone, slow-tempo subset through ZIP byte ranges. Run `acquire_idmt.py`, `idmt_metadata_acquire.py`, then `idmt_audio_acquire.py`, each with the same `--data-dir PATH`. They record per-file CRC32 and SHA256 checks; the full archive MD5 is unverified. The dataset license is CC BY-NC-ND 4.0.
