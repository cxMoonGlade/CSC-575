# Progress report

From this directory, build the report with Tectonic:

```bash
tectonic -X compile progress_report.tex
```

The output is `progress_report.pdf`: four A4 pages, including 19 references, using the ISMIR two-column template. Submit this PDF for the individual progress report. Keep `results.tex`, `references.bib`, the style files and `figures/` beside the source when building.

To regenerate the error-analysis figure from saved predictions and annotation diagnostics:

```bash
../.venv/bin/python make_quality_figure.py --project .. --output figures
```

This figure script performs no recognition or parameter tuning. `writing_notes.md`, `language_audit.md` and `evidence_checks.json` record the structural, language and numeric checks separately from the submitted PDF.

The playback figure, `figures/demo_progress.pdf`, is a compact browser view of the saved development-example player. Its predictions, labels and audio are unchanged; surrounding controls are hidden and text is enlarged for a paper column. [Capture notes](demo_capture/figure_notes.md) and [provenance](demo_capture/provenance.json) document the source hashes, playback check and separate CSV output. The archived capture script uses machine-specific browser paths; it is not required to compile the report.

The [rock_6 diagnostic](../docs/research/rock6_third_diagnostic_2026-11-16/README.md) includes its script, recomputed scores and reproduction checks. It uses the frozen recognizer without parameter selection. Its additional plot is supplementary; the submitted report remains four pages.
