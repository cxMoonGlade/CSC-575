# Candidate configuration and report integration

Archived integration plan for the window-fusion follow-up. The measurements and configuration below retain their original scope; the [current report](../../../report/progress_report.pdf) uses the later research framing.

The selected development candidate needs no new production feature option. It is the existing fixed-fusion method with these configuration values:

```json
{
  "n_fft_short": 4096,
  "n_fft_long": 8192,
  "fixed_weight": 0.2,
  "switch_penalty": 4.0
}
```

The current extractor estimates tuning with `n_fft_long`, so this configuration retains the experiment's 8,192-sample tuning estimate. The unsuccessful 16,384-sample follow-up reused an 8,192-derived estimate; reproducing that setting through the normal extractor would require an independent tuning-window option. Since it was not selected, no such option or production patch is proposed.

For portable execution, save a separate candidate configuration and use the existing `fixed` method. Keep the original frozen configuration and results unchanged. Export the new configuration, source hashes, input manifest, labels, coverage and metrics with each comparison. Use a data-root argument and paths relative to that root when packaging the external-data runner; the temporary development helper has machine-specific paths and is an experiment utility.

`verify_portability.py` checks three development recordings. It compares ordinary extraction under the candidate configuration against the experiment's explicit cached-tuning construction, then compares the resulting features and decoded predictions. It does not select parameters or read the old test set.

For the four-page report, keep the historical GuitarSet test table. Replace the initial 20-recording trial paragraph and most of the current discussion with the short development-search outcome. Include the new external comparison only after its outputs have been checked, with its dataset, task, coverage and sample count stated separately. The existing full search records belong in the repository. If space is tight, compress the abstract and repeated settings descriptions before cutting the Related Work or personal PI table.

The first three experiment runners and the follow-up contain 30 scored rows in total (9 + 9 + 7 + 5), including repeated controls. Excluding the extra standalone baseline in the boundary runner gives 29. The manuscript draft avoids this ambiguous total and states the tested directions instead.
