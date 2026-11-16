# Writing notes

Routing: manuscript; research; experiments and discussion; English; generic journal/course ISMIR format. Applied the exact user-provided `nature-writing` 1.6.0 and `academic-language-audit` guidance already read in this session.

The argument is that the bounded search found a small development gain that did not recur in the fixed external comparison. The long-window baseline remains the default. The final draft presents measured scores rather than repeated pass/fail wording; threshold details stay in the experiment plan.

| Term | Usage |
| --- | --- |
| duration accuracy | Pooled correctly labelled duration divided by scoreable reference duration. |
| near-change accuracy | The previously fixed ±0.2-second region measure. |
| change in points | Absolute percentage-point difference from the 8,192-sample baseline. |
| candidate | The best development setting; it has not passed the adoption threshold. |
| external comparison | A separate dataset evaluated after settings were fixed; final measured results are included. |
| window length | Changes both temporal averaging and frequency resolution; neither mechanism is isolated here. |

The main table keeps one best modified setting per completed direction and the shared baseline. The follow-up is one paragraph. Individual configurations, performer scores, timing internals and raw outputs remain in the source result files. All comparisons that change the conclusion remain visible.

This is a new, approximately 300-word draft rather than compression of the existing report; no before/after word-count claim is made. Its report integration plan removes the earlier trial chronology before adding the new comparison. The historical GuitarSet test table is retained. The figures, bibliography and PI table remain part of the four-page deliverable.

The proposed tuning-window change was abandoned before any code edit when the 16,384-window follow-up failed. Existing configuration reproduced the selected 4,096/8,192 construction exactly on three development recordings; results are saved in `portability_checks.json`. The temporary check script uses the experiment workspace paths and is not presented as a portable production command.

The final summary includes actual IDMT overall, chord-only, near-change, runtime and NC-agreement values, plus the 64/60 recording distinction. Its evidence links use the intended repository-relative paths. No external result placeholders remain.
