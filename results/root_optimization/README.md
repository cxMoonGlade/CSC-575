# Note profiles for root errors

Direct projection improved chord and root accuracy on 119 GuitarSet development recordings and a frozen comparison of 64 IDMT fast-tempo recordings. It gave higher chord accuracy than NNLS at lower complete processing cost on the latter set. These fast recordings contain the same pieces as the earlier slow-tempo comparison; unseen repertoire remains untested.

## Development recordings (119)

| Method | Chord accuracy | Root accuracy | Wrong-root duration |
| --- | ---: | ---: | ---: |
| Long STFT | 71.97% | 74.48% | 547.08 s |
| Fundamental-only NNLS | 78.37% | 80.15% | 422.78 s |
| Direct projection | 78.02% | 79.54% | 436.01 s |

All methods share the 8,192-sample spectrum, tuning, pitch range, frame grid, triad templates, silence rule and decoder. The two candidates estimate note strengths before folding octaves into chroma. NNLS fits the note profiles jointly; projection fits each profile separately. Both improved each development progression family. Root accuracy ignores major/minor quality and treats predicted `N` as incorrect on a reference chord.

Adding geometric harmonic partials gave 73.07% and 63.20% chord accuracy for decay 0.6 and 0.9, below the fundamental-only NNLS control. The best changed low-register weighting reached 71.92%: its small root improvement was offset by more major/minor errors. The results therefore favor investigating note-specific weighting; they do not establish harmonic removal as the cause of the gain.

## Isolated-chord comparison (88)

The frozen comparison used all major/minor chord clips in the two chord directories of IDMT-SMT-Guitar's archive `dataset1`. These contain 44 fingering/quality/transposition settings, each recorded with two electric guitars in a separate session. Filename labels match the XML note pitch classes. Evaluation covers the first note onset through the last offset: 202.725 of 220 seconds (92.15%).

| Method | Decoded chord accuracy | Decoded root accuracy | Complete inference |
| --- | ---: | ---: | ---: |
| Long STFT | 100% | 100% | 1.29 s |
| Fundamental-only NNLS | 100% | 100% | 6.04 s |
| Direct projection | 100% | 100% | 1.86 s |

The clips produce a ceiling for all three decoded methods. This comparison cannot establish an improvement on chord progressions. Projection took about 1.44 times the baseline runtime and was 3.25 times faster than NNLS in this run. Times include loading, resampling, tuning, spectral and dictionary construction, fitting, decoding and interval construction on one CPU thread. Imports, warm-up, scoring and output writing are excluded; feature caches are disabled. This is one timed run, with paired instruments rather than independent songs.

## Fast-tempo recordings (64)

The frozen comparison used every recording in IDMT-SMT-Guitar's `dataset4/acoustic_mic/fast` stream, without changing either candidate. Its 64 piece IDs match the earlier slow-tempo set; evaluation uses the fast recordings' own annotations. There are 29.77 minutes of audio and 1,063.79 seconds of scoreable reference (59.56%). Five recordings have no scoreable labels. Of the remaining 59, one has only supported `N` intervals, leaving 58 that contribute to the root metric.

| Method | Chord accuracy | Root accuracy | Near-change accuracy | Complete runtime |
| --- | ---: | ---: | ---: | ---: |
| Long STFT | 64.70% | 73.91% | 50.29% | 9.49 s |
| Direct projection | 67.80% | 78.32% | 54.23% | 10.43 s |
| Fundamental-only NNLS | 66.95% | 78.45% | 54.16% | 44.37 s |

Chord accuracy includes mapped reference `N`; root accuracy uses only the 936.94 seconds of supported chords. All methods agree with 11.72% of mapped `N` time. Projection raises chord accuracy by 3.10 percentage points and root accuracy by 4.41 points. Wrong-root duration falls from 241.39 to 200.03 seconds (17.14%). Its full runtime is 9.86% above the baseline; NNLS takes 4.26 times as long as projection. Timing follows the complete-inference scope above, with each of the 192 file/method jobs run once in shuffled order.

NNLS has a slightly better root score, but more same-root major/minor errors: 37.67 seconds versus projection's 27.41 seconds. Projection improves 30 scoreable recordings, ties on 13 and worsens 16. Seven of eight genre aggregates improve; rock/blues falls by 6.18 percentage points. The [example figure](fast/figures/error_cases.pdf) shows the largest recording-level gain (`jazz_5`, +47.37 points) and loss (`rock_6`, −22.53 points), selected after scoring. Their reference coverage is 34.29% and 86.55%, respectively.

These results support using projection for the present guitar workflow. They do not measure transfer to new pieces. The evaluated set must not be used to select parameters. Reassessment after calibration on separate development data remains exploratory; claims about new repertoire require separate held-out recordings.

## Saved evidence

- The [development example player](demo_projection/playback.html) compares the saved baseline and projection on `01_Funk1-97-C_comp`. In the opening C-major interval, projection corrects the baseline's E-minor prediction. This case was chosen for diagnosis and is not an independent test.
- [NNLS and harmonic controls](harmonic/summary.json), [projection](projection/summary.json), and [low-register candidates](bass/summary.json) retain all development settings and recording-level results.
- [Isolated-chord results](isolated/summary.json), [recording scores](isolated/per_recording.csv), and [protocol](isolated/protocol.json) preserve the frozen comparison, including raw predictions.
- [Fast-tempo results](fast/summary.json), [recording scores](fast/per_recording.csv), and [reproduction instructions](../../docs/research/root_optimization/fast_validation/README.md) preserve the second frozen comparison.
- Independent numeric reviews check the [isolated clips](../../docs/research/root_optimization/isolated_numeric_review.json) and [fast recordings](../../docs/research/root_optimization/fast_validation/numeric_review.json).
- [Research and reproduction notes](../../docs/research/root_optimization/README.md) include the plan, source history and writing audits.

The original 59-recording GuitarSet test and 64-recording IDMT window comparison were not used to select these candidates. Both the 88-clip isolated comparison and the 64 fast recordings have now been evaluated; neither is a tuning set for later revisions.
