# Boundary refinement: development result

The six-setting experiment did not meet the predeclared acceptance gate. The best setting improved pooled duration accuracy by **0.038 percentage points**, below the required 0.5 points. It is an experimental branch, not a replacement for the frozen recognizer.

All settings use the existing long-window decoder with penalty 4 on 119 development recordings. Refinement moves its boundaries using local short/long template scores while retaining the chord sequence. The algorithm receives no reference labels or boundaries.

| Radius (s) | Short weight | Accuracy (%) | Near-change accuracy (%) | Family 1 (%) | Family 2 (%) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | — | 71.965 | 52.560 | 79.398 | 65.070 |
| 0.1 | 0.5 | 71.992 | 52.860 | 79.408 | 65.112 |
| 0.1 | 1.0 | 71.867 | 52.610 | 79.334 | 64.939 |
| 0.2 | 0.5 | 72.003 | 52.864 | 79.430 | 65.113 |
| 0.2 | 1.0 | 71.794 | 52.092 | 79.230 | 64.896 |
| 0.3 | 0.5 | 71.987 | 52.833 | 79.403 | 65.105 |
| 0.3 | 1.0 | 71.694 | 51.633 | 79.096 | 64.826 |

The best setting uses a 0.2-second radius and equal short/long evidence. Both development families improved slightly, by 0.032 and 0.043 points. Its near-change accuracy rose by 0.304 points, and boundary F1 rose from 26.288% to 27.807%. Mean absolute error among matched boundaries fell from 51.60 to 44.01 ms. These boundary scores refer to the dataset's score-derived segmentation.

Refinement moved 650 of 1,226 decoded boundaries and changed 1,133 frame labels. All chord identities, their order, and silence frames were preserved. The number of boundaries inside scoreable reference spans changed from 716 to 712 because a moved boundary can enter or leave an excluded interval; this is not deletion from the decoded sequence.

Only the equal-evidence settings improved pooled accuracy. Using short-window evidence alone reduced it at every radius, with larger losses for larger radii. The measured timing changes are too small to justify this method as the next main improvement under the agreed accuracy criterion. This branch stops after the declared grid.

Cached-feature inference took 0.334 seconds for the baseline and 0.355 seconds for the best setting across all recordings. These figures include decoding and refinement, but exclude audio loading and feature extraction. They are not end-to-end runtimes or a speedup claim.

`results.json` retains every setting and per-recording score. `boundary_diagnostics.json` contains the exact baseline/best boundary analysis; its duration scores agree with the cached overlap scorer. The branch passes 58 tests, including five new refinement tests. No progression-3 audio or annotations were read or evaluated during this experiment.

Reproduce in the original experiment workspace with:

```bash
/home/cx/Documents/csc475/Proj/.venv/bin/python experiment/run.py
```

The runner requires the development cache and `common.py` in the parent experiment directory. It refuses to overwrite existing results.
