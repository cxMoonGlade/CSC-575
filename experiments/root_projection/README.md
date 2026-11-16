# Independent projection control

Independent projection retained most of the fundamental-only NNLS improvement on the 119 development recordings. It achieved 78.02% major/minor accuracy, compared with 71.97% for the baseline and 78.37% for NNLS. Both progression families improved over the baseline, although both remained below NNLS.

| Method | Major/minor accuracy | Root accuracy | Near-change accuracy | Different-root errors |
|---|---:|---:|---:|---:|
| Baseline | 71.97% | 74.48% | 52.56% | 547.08 s |
| Fundamental NNLS | 78.37% | 80.15% | 56.34% | 422.78 s |
| Independent projection | 78.02% | 79.54% | 56.23% | 436.01 s |

Projection fits each fundamental profile separately: `a_j = (D_j.T @ y) / (D_j.T @ D_j)`. It uses the same dictionary and observations as NNLS, then applies the same octave folding and chord decoder. The independent fits ignore profile overlap. The 0.34-percentage-point gap therefore measures the additional benefit of joint fitting under these fixed settings.

Projection and decoding took 2.59 seconds in this selection run. That timing includes dictionary construction but excludes audio loading, spectrum extraction, tuning and RMS. Complete runtime comparisons must include those operations for every method.

The single setting was declared in `plan.md` before inference. `results/summary.json` and `results/per_recording.csv` retain all measurements. The saved NNLS and baseline controls come from the preceding development comparison. No held-out score was used.

`chordrec.projection.extract_projected_features(path, config)` performs uncached audio loading, resampling, tuning, RMS, STFT, dictionary construction and projection. It returns the same time grid and `harmonic` feature key as the NNLS reader. Six focused tests cover the projection formula, overlapping profiles, silence and exact preprocessing parity. Three development recordings also reproduced the selection-run scores exactly through this reader.
