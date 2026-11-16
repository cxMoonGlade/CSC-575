# Low-register chord evidence

Archived branch summary. The command below records the original experiment checkout; use the [current reproduction instructions](../README.md#reproduction) from the project root.

Adding low-register evidence did not improve development-set chord accuracy. The experiment used the same long-window spectrum, tuning, silence rule and Viterbi penalty as the frozen baseline. An additional chroma covered MIDI 36–59. Four settings mixed the original triad scores with either low-register root energy or low-register triad scores, at weights 0.1 and 0.2.

| Setting | Major/minor accuracy | Root accuracy | Different-root errors | Same-root quality errors |
|---|---:|---:|---:|---:|
| Baseline | 71.97% | 74.48% | 547.08 s | 55.05 s |
| Root weight 0.1 | 71.12% | 74.46% | 547.47 s | 73.15 s |
| Root weight 0.2 | 66.57% | 69.18% | 663.30 s | 57.03 s |
| Triad weight 0.1 | 71.92% | 74.79% | 540.27 s | 62.85 s |
| Triad weight 0.2 | 71.35% | 74.82% | 539.53 s | 76.13 s |

The 0.1 triad mixture reduced different-root errors by 6.81 seconds but added 7.80 seconds of same-root quality errors. Root accuracy therefore improved while chord accuracy fell. Stronger root weighting also hurt overall accuracy. Low-register pitch energy was insufficient to justify changing the baseline in these 119 development recordings.

The lower band can contain chord inversions and upper harmonics; it does not directly identify the root. These results evaluate this fixed band and the four declared mixtures. Both development progression families and every setting are retained in `results/root_bass/summary.json` and `per_recording.csv`. Baseline chroma and decoded labels matched exactly for all 119 recordings. Seven new checks and the existing suite passed (77 checks total).

Run from the experiment checkout:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python experiments/root_optimization/bass/run.py \
  --project-root /home/cx/Documents/csc475/Proj \
  --cache-dir /tmp/chordrec_opt2/cache \
  --output results/root_bass_repeat
```

The development cache and helper are produced by `experiments/optimization_v2/common.py`. The runner rejects nondevelopment records and reproduces the saved baseline accuracy before accepting results. Timings in the shared scorer cover only result lookup and score aggregation here; they are not decoding or full-pipeline timings. No runtime advantage is reported.
