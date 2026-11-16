# Nature writing notes

Routing: manuscript / methods / method + experiments / en / generic. Target: a concise ISMIR course progress report, not a Nature submission.

## Terminology ledger

| Canonical term | Definition or use | Decision |
| --- | --- | --- |
| STFT | Short-time Fourier transform | Expand at first use; retain short/long STFT thereafter |
| CQT | Constant-Q transform | Expand at first use |
| Duration accuracy | Correctly labelled time / scoreable time | Preserve the denominator and existing measured values |
| Near-change accuracy | Accuracy within ±0.2 s of supported reference changes | State that windows are clipped to continuous scoreable spans |
| Recording / progression family | Repeated performances / shared chord progression structure | Do not rename recordings as independent songs |
| Wall-clock runtime | Elapsed audio-to-label time on CPU | Replace ambiguous “CPU time” |
| Selected adaptive rule | The threshold/radius chosen on development data | Preserve the almost-constant weighting result; do not imply a proven adaptive advantage |

## Contribution and continuity

The evidence chain remains: compare shared-control feature representations, select settings on development data, report the frozen comparison, then interpret why the selected adaptive rule offered no accuracy improvement. The weight-activation observation refers explicitly to feature weights; it does not assert a causal explanation for errors. New held-out material is a remaining task rather than an assumed resource.

## Main-text discipline

| Evidence | Role | Location |
| --- | --- | --- |
| Frozen duration and near-change accuracy | Main comparison | README results table |
| Selected constant weight 0 and adaptive activation 0.014% | Interpretation that changes the conclusion | Results paragraph |
| Raw versus decoded long-window accuracy | Support for the role of temporal decoding | Results paragraph |
| One test progression, two zero-scoreable recordings, coverage | Necessary comparison boundaries | Data/results paragraphs |
| Full grid, code snapshots, per-recording scores and case-selection rules | Reproducibility and detailed evidence | Linked result files |

Edits replaced existing clauses rather than appending a new discussion section. Abbreviation expansions and the explicit metric definition increased the README from 1,589 to 1,636 whitespace-delimited words. No result was removed, moved out of view, or strengthened. Code changes are limited to documentation and a figure label; the AST-preservation check is saved separately.

The listening notebook now identifies the long-window comparator, the 57-recording case-selection pool, and the two examples’ reference coverage; all 59 recordings remain in aggregate results. Its code cells are unchanged. The results guide distinguishes recognition outputs from parameter-selection records, preserves the verified 52-combination search count, and states that the selected zero weight applies to the short window. A local kernel registration command makes the notebook setup explicit without requiring a global Jupyter installation.
