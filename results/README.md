# Saved experiments

The original runs use GuitarSet accompaniment recordings and performed chord labels. Follow-up studies add IDMT-SMT-Guitar recordings.

| Directory | Recordings | Purpose |
|---|---:|---|
| `dev_initial` | 20 | Initial implementation and trigger check |
| `parameter_selection` | 119 | Development-only parameter selection |
| `dev_frozen` | 119 | Full development comparison with the selected settings |
| `test_frozen` | 59 | Test comparison after the settings were frozen |
| [optimization_v2](optimization_v2/README.md) | 119 development; 64 IDMT | Window and feature follow-up |
| [root_optimization](root_optimization/README.md) | 119 development; 88 isolated + 64 fast IDMT | Note profiles, root errors and complete inference cost |

The original GuitarSet test comparison remains here as a historical experiment. The current [progress report](../report/progress_report.pdf) focuses on the development comparisons and the fast-tempo IDMT results. The three original recognition runs contain aggregate scores (`summary.csv`), per-recording scores and timings (`per_recording.csv`), timestamped predictions, settings, software versions, and the code snapshot used for recognition and evaluation. `test_frozen/regions/` separates accuracy near annotated changes from the remaining scoreable time. `activation.json` records how often the adaptive rule assigns high short-window weight.

Archived plans and source snapshots describe the experiments as run. The linked experiment READMEs give current reproduction commands.

The selection run caches features to compare 52 method/settings combinations. Its timing is separate from the uncached audio-to-label measurements in `dev_frozen` and `test_frozen`. The selected fixed short-window weight is zero and duplicates long-window predictions, although this implementation still computes both front ends.

To reproduce selection and a frozen run from the project root, use new output directories:

```bash
.venv/bin/python -m chordrec.tune --project-root . --output results/selection_repeat
.venv/bin/python -m chordrec run --config configs/frozen.json --split test --output results/test_repeat
.venv/bin/python -m chordrec.regions --run results/test_repeat --output results/test_repeat/regions
.venv/bin/python -m chordrec.report_figures --run results/test_repeat --output results/test_repeat/figures --baseline long
```

Repeating the saved configuration checks reproducibility. Selecting a new method from these test scores would require fresh held-out material for a new generalization claim.
