# Compact demonstration figure — 2026-11-16

Writing scope: manuscript / research / experiments caption / zh-to-en / generic ISMIR course report. The existing report terminology is retained: GuitarSet, Long STFT, Projection, reference, CSV. The visible player retains its existing label “Note projection”.

Source: `results/root_optimization/demo_projection/playback.html`, development recording `01_Funk1-97-C_comp`. The browser loads its embedded audio and saved predictions. The selected playback interval is 0–8 s; the timeline includes the player's existing 1 s context and thus displays 0–9 s. A separate playback check selected 0–0.3 s and confirmed that the player stopped at 0.3 s. The source files were not edited.

Capture treatment: the browser hides the full-recording overview, surrounding prose, single-option interval selector, and context/whole-recording buttons; it enlarges existing text and rescales SVG x-coordinates for a single paper column. The interval input, focus/play buttons, reference labels, saved predictions, and coverage row are retained. This is a compact view, not an unmodified full-page screenshot. At 3.2 in wide, its 20 px text is approximately 7.1 pt. The PDF contains native text and vector shapes; the PNG is a 3× browser screenshot. No raster processing was used.

## Caption

Compact player view for a GuitarSet development excerpt. Projection recovers C major where Long STFT predicts E minor. Interval controls support listening; CSV output stores each segment’s start, end and label.

The caption should identify `01_Funk1-97-C_comp` either directly or in adjacent prose. “Recovers C major” describes the evaluated root/quality: the saved reference is `C:maj/3`, so this is not an inversion-recognition claim. The CSV evidence is a separate saved output, not a button shown in the figure.

CSV header and exact first row:

```csv
start,end,label
0.0,9.97297052154195,C:maj
```

## Language audit

### Overall observation

Reviewed the caption, displayed labels, actual saved HTML payload and CSV first row. The claim is restricted to the displayed development example. No general performance or acoustic-mechanism claim is introduced. No new overview or literature statement is present.

### Located decisions

| Location and wording | Issue type | Evidence and effect | Priority | Normal academic expression? | Action | Final wording |
| --- | --- | --- | --- | --- | --- | --- |
| Caption opening: “Compact player view” | Image provenance | Capture hides surrounding components and changes sizing; calling it an unmodified screenshot would be inaccurate. | Medium | Yes; it describes the presentation directly. | Retain | Compact player view for a GuitarSet development excerpt. |
| Caption: “Projection recovers C major where Long STFT predicts E minor.” | Evidence boundary | The saved reference is C:maj/3 and the two saved predictions are C:maj and E:min for the complete displayed interval. | Medium | Yes; bounded by the preceding example description. | Retain | Projection recovers C major where Long STFT predicts E minor. |
| Caption: “CSV output stores each segment’s start, end and label.” | Functional evidence | Verified the adjacent prediction.csv columns and first row; no export button appears in this capture. | Medium | Yes; it describes the saved artifact without inventing a UI control. | Retain | CSV output stores each segment’s start, end and label. |

### Recommendations

Use the figure as evidence for interval listening and aligned predictions. Keep CSV evidence as a separate output description. Preserve the reference inversion label in the figure and the evaluation-vocabulary explanation in Methods. Writing features alone cannot establish AI authorship.

## Reproduction

The browser package and libraries already existed locally. This command produced the staged files:

```bash
LD_LIBRARY_PATH=/tmp/ah-visual-browser-20261019/libs/usr/lib/x86_64-linux-gnu \
  /tmp/ah-visual-browser-20261019/node_modules/node/bin/node \
  /tmp/csc575-rubric-revision-2026-11-16/demo_work/capture_demo.cjs
```

The script uses local absolute paths for this capture; `provenance.json` records source hashes, interval selections, saved labels and presentation changes. It is a capture record, not an added application dependency.
