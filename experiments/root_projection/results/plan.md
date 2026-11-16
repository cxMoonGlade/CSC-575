# Fundamental projection control

The fundamental-only nonnegative least-squares (NNLS) dictionary improved development chord accuracy. Test whether independent projections onto the same profiles preserve this gain without solving a constrained joint fit for every frame.

Use exactly one new setting. For the existing decay-zero dictionary D and observed magnitude spectra Y, compute each note activation as a_j(t) = max(0, D_j^T Y_t / ||D_j||²). The maximum only protects numerical nonnegativity; both inputs are nonnegative. Fold the 60 note activations into 12 pitch classes and apply the unchanged L2 normalization, silence rule and Viterbi decoder. Use the same observed bins, tuning, 8,192-sample Hann window, pitch range and frame grid as NNLS.

This fits each profile separately. It ignores overlap between neighbouring profiles, so it is not algebraically equivalent to NNLS. The comparison tests whether joint fitting materially improves the chord output in this setting.

Evaluate all 119 development recordings. Compare duration-weighted major/minor accuracy, root accuracy, different-root error seconds, near-change accuracy and both progression families against the saved baseline and decay-zero NNLS. Retain all results. Use only this projection formula; do not sweep thresholds, regularizers or profile widths. Cached fitting timings are diagnostic; complete audio-to-label timing is required before claiming an end-to-end speed advantage.

A cheaper projection is preferable if its development chord accuracy matches or exceeds NNLS without a progression-family loss. If its accuracy is lower, report the measured accuracy–cost tradeoff rather than treating approximate score equality as equivalent labels.

Writing scope: manuscript / methods / experiments / en / generic. Terms retained: fundamental-only dictionary, independent projection, NNLS, duration accuracy. The equation and overlap assumption state what the cost comparison changes; no new mechanism or generalization claim is added.
