# Further development experiments

I compared three changes on the 119 development recordings: a larger short window, spectral whitening, and refinement of existing chord boundaries. All used the same switch penalty of 4.

| Best tested modification | Accuracy (%) | Change (points) | Near-change accuracy (%) |
| --- | ---: | ---: | ---: |
| Baseline: 8,192 samples | 71.965 | — | 52.560 |
| Fuse 4,096/8,192 samples, short weight 0.2 | 72.224 | +0.258 | 52.759 |
| Long-window whitening, strength 0.5 | 71.549 | −0.416 | 52.003 |
| Refine boundaries within 0.2 s, equal short/long evidence | 72.003 | +0.038 | 52.864 |

Replacing 2,048 with 4,096 samples improved each of the three matched fusion comparisons, which motivated one follow-up with a 16,384-sample window. Its four new settings also failed: the single long window reached 71.907% overall and 51.426% near changes. The search therefore stops here. Window length changes both frequency resolution and temporal averaging; these scores do not isolate either effect.

The 4,096/8,192 blend was the best development candidate, with gains of 0.317 and 0.204 points in the two families. Its fixed comparison on 64 IDMT acoustic-microphone recordings did not reproduce that gain: accuracy was **65.558%**, against **65.732%** for the baseline. Near-change accuracy was 48.613% versus 48.658%. Chord-only accuracy, excluding reference no-chord intervals, was 73.821% versus 74.017%.

The IDMT selection was fixed from metadata before scoring. Scoreable coverage was 61.656% of 36.02 minutes of audio; 60 of 64 recordings have scoreable labels. Full audio-to-label runtime was 13.20 seconds for fusion and 11.76 seconds for the baseline. The adapter interprets `NC` as no chord, although the inspected annotation description does not define it. Both methods agreed with only **1.31%** of 151.84 seconds labelled `NC`. This calls for listening and annotation review before changing the energy-based no-chord rule; it does not establish that `NC` means silence.

The original long-window baseline remains the default. The bounded method search and external comparison are complete; no further settings were selected from the external results. The earlier GuitarSet test table still describes its original frozen comparison.

Saved evidence: [window comparison](resolution/results/summary.json), [spectral whitening](spectral/results/summary.json), [boundary refinement](boundary/results.json), [long-window follow-up](long_resolution/results/summary.json), and [external results](external/summary.json). The [external evaluation plan](external_evaluation_plan.json) records the fixed comparison. [Experiment instructions](../../experiments/optimization_v2/README.md) describe how to reproduce the work.

The table shows the best changed setting in each direction; whitening at strength zero is the baseline. Cached selection times are not end-to-end inference times.

From the repository root, repeat the fixed external comparison with:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python -m chordrec.external_compare \
  --data-root docs/datasets/IDMT-SMT-Guitar --baseline configs/frozen.json \
  --candidate configs/fusion_4096_8192.json --output results/idmt_repeat
```

The runner refuses to overwrite existing output.
