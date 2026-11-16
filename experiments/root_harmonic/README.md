# Note fitting for root errors

On the 119 GuitarSet development recordings, fitting fundamental-only note profiles raised duration-weighted chord accuracy from 71.97% to 78.37%. Both progression families improved. Adding geometric harmonic profiles reduced this gain: decay .6 reached 73.07%, and decay .9 reached 63.20%.

| Setting | Chord accuracy | Root accuracy | Wrong-root seconds | Near-boundary accuracy |
| --- | ---: | ---: | ---: | ---: |
| Long-window baseline | 71.97% | 74.48% | 547.08 | 52.56% |
| Fundamental-only NNLS | 78.37% | 80.15% | 422.78 | 56.34% |
| Harmonic decay .6 | 73.07% | 74.71% | 541.86 | 52.31% |
| Harmonic decay .9 | 63.20% | 66.07% | 731.36 | 45.57% |

The strongest result comes from fitting tuned note profiles without modeled upper partials. This comparison supports testing the note representation further; it does not support attributing the improvement to harmonic removal. Root accuracy counts a prediction of N as incorrect on a reference chord. Wrong-root seconds count predictions of a chord with a different root.

The dictionary uses the magnitude response of a periodic Hann-windowed sine at each tuned MIDI pitch from 36 to 95. The harmonic variants sum these responses with amplitudes s^(k-1), retaining partials below Nyquist until their weight falls below 1e-8. Observation bins match the baseline frequency span. SciPy NNLS fits the nonnegative amplitudes before octave folding and L2 normalization. Audio, tuning, frame grid, reference reduction, triad templates, RMS threshold and Viterbi penalty remain fixed.

The experiment is inspired by Mauch and Dixon (2010), but uses the project's STFT and decoder. Their standardized-spectrum comparison reports 79.0% without NNLS and 80.0% with NNLS; their complete system also includes beat aggregation and a dynamic Bayesian network. Reading details and the development diagnosis are in [review.md](review.md).

`results/` preserves all four settings and 476 recording-level rows. The initial development run reused magnitude spectra, frozen tuning and a dictionary cache; its fitting times are not end-to-end inference times. The final `extract_harmonic_features` function reads and processes each file independently, constructs its dictionary, and returns `times`, `rms`, `duration`, `tuning`, `harmonic`, and residual diagnostics. Source snapshots preserve the exact original development code before the uncached extractor was added. The completed [projection control and isolated-chord comparison](../../results/root_optimization/README.md) separate the fitting choice from complete inference cost.

To repeat the comparison from the project root, use the development cache prepared by `experiments/optimization_v2/common.py` and choose a new output directory:

```bash
python experiments/root_harmonic/run.py \
  --project-root . \
  --cache-dir experiments/optimization_v2/cache \
  --output results/root_harmonic_repeat
```

`--help` and importing the runner do not load audio or start experiments. Existing output paths are rejected. A rerun writes `timing.json` to identify reused inputs: the baseline chroma and all tuning estimates come from the cache, each recording's magnitude spectrum is shared across candidates, and each NNLS call constructs its dictionary. These measurements isolate experiment stages; full inference uses the separate uncached extractor.
