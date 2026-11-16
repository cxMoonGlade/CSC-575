# Where the frozen predictions fail

This analysis covers the original GuitarSet test split and IDMT subset 4, `acoustic_mic/slow`. The later [fast-tempo comparison](../root_optimization/fast_validation/README.md) uses a different set of recordings.

Different-root predictions account for 89.3% of the long baseline's error duration on GuitarSet and 61.2% on IDMT-SMT-Guitar. On IDMT, reference-N errors account for another 32.8%, under the existing NC→N mapping.

| Long baseline | GuitarSet | IDMT-SMT-Guitar |
| --- | ---: | ---: |
| Scored duration (s) | 1438.60 | 1332.38 |
| Error duration (s) | 377.17 | 456.59 |
| Other root (s) | 336.95 | 279.27 |
| Same root, wrong major/minor quality (s) | 26.49 | 26.19 |
| Reference N, predicted chord (s) | 0.00 | 149.84 |
| Reference chord, predicted N (s) | 13.73 | 1.29 |
| Near-boundary error rate | 41.02% | 51.34% |
| Stable-region error rate | 23.60% | 29.77% |

Near means within 0.2 s of a supported reference change, clipped to its scoreable span. Stable is the remaining scored duration. Error rates use each region's duration; proximity alone does not establish a boundary-timing cause. There are no missing or unsupported predictions in these saved runs.

The analysis reads frozen predictions for all 59 GuitarSet recordings and 64 IDMT recordings, including zero-coverage recordings. It uses the evaluator's major/minor reduction and excludes unsupported references and annotation gaps. The saved scores are unchanged. Confusion tables include all 25 reference classes and 27 prediction values (25 classes, missing, unsupported).

Run from the project root with a new output directory:

```bash
.venv/bin/python -m chordrec.error_analysis --output results/error_analysis_repeat
```

[Results](../../../results/error_analysis/) include both methods per dataset, exact durations, confusion tables, input hashes, and systematically selected examples. The [compact figure](../../../results/error_analysis/error_baseline.pdf) shows the long baseline. The [full figure](../../../results/error_analysis/error_decomposition.pdf) includes both methods and regions. Example selection is defined in each `examples.json`; these examples illustrate error categories.
