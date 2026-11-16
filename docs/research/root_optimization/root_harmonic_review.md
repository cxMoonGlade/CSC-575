# Independent numerical review

No blocking numerical or alignment error was found in `chordrec/harmonic.py` (reviewed SHA-256 `ed00fa91a67328b6f1cb1b94623dd0c276cf9835149ec927ff32c5d1a3ced9ad`). The analytic periodic-Hann response, retained frequency bins and nonnegative fit were checked independently. Three development recordings also reproduced the baseline tuning, RMS, time grid and duration exactly.

The Hann response differed from direct summation by at most 5.46e-11. Six unit-sine profiles spanning MIDI 36–95 matched a sampled FFT within 9.46e-11. Known nonnegative coefficients were recovered within 1.7e-15 for decay 0, 0.6 and 0.9. On three frames from `00_Funk1-97-C_comp`, NNLS met the nonnegativity and numerical KKT checks; an independent bounded least-squares solver produced the same residual within 7.2e-15. These are implementation checks, not guarantees of chord accuracy.

Installed SciPy 1.18.1 `scipy.optimize.nnls` source and documentation were read. It solves squared spectral residual subject to nonnegative coefficients with an active-set method; an iteration-limit failure raises `RuntimeError`. The implementation does not silently accept that failure. Dictionary scaling uses one common scalar, so differences between pitch profiles do not introduce arbitrary note-specific coefficient units.

The model observes the same FFT bins as the baseline's MIDI range, including the same tuning-dependent half-semitone boundaries. Each dictionary profile adds magnitudes of separately windowed partials. This approximates a musical mixture: phases, inharmonicity and instrument-specific spectral envelopes are not fitted. A smaller spectral residual does not itself guarantee a correct chord label.

The final extractor includes audio decoding, resampling, tuning, RMS, spectrum construction, dictionary construction and per-frame fitting. Its dictionary cache has been removed. A fair runtime comparison must also include the unchanged chord decoder and interval construction, with the same warm-up and thread settings for both methods. Selection-run fitting times alone are not complete audio-to-label costs.

Evidence: `/tmp/root_harmonic_independent_check.py`, corresponding JSON; `/tmp/root_harmonic_extract_check.py`, corresponding JSON. No held-out recording or IDMT score was read during this review.
