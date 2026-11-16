# Introduction argument revision — 2026-11-16

Applied nature-writing (manuscript / research / introduction / zh-to-en / generic ISMIR course report), followed by academic-language-audit. The general-to-specific structure now moves from the working recognizer to the observed quality-error contrast, then explains the controlled study. The research question is unchanged.

The previous Introduction defined thirds and vocabulary reduction, then jumped from errors concentrated in one seventh-chord recording to varying third strength. The revision gives those variables separate experimental roles: adding the seventh changes the input while preserving the major/minor target; third amplitude controls the intended quality cue. The ideal score prediction supplies a baseline for checking audio features and sequence decisions. The observed decoder difference motivates calibration; it does not establish that a seventh or a weak third caused the recording's errors.

The Introduction and README project description were revised together. All other report prose, measured results, methods, plans, figures, tables, original indicators and bibliography were retained. The three existing overview citations still support the pipeline description; their documented reading scope is in overview_sources.md. This pass did not re-read the cited papers or perform new experiments.

The four-page PDF was rebuilt with the existing template and all four rendered pages inspected. No overfull boxes or unresolved references appeared. The staged bibliography matches the previous build exactly (19 entries).

---

# Publication pass — 2026-11-16

The four-page report, tables, figures and bibliography are unchanged from the reviewed revision below. For publication, the README now explains data preparation and how to open the players. Dataset and overview reading notes clarify their historical scope. The [publication reviews](../docs/research/publication_2026-11-16/report_review.md) record both writing skills and the clean build; current hashes are in `evidence_checks.json`.

---

# Rubric evidence and frozen-score diagnostic — 2026-11-16

Applied nature-writing and academic-language-audit before integration. Routing: manuscript / research / abstract, introduction, methods, results and discussion / zh-to-en / generic ISMIR course report. The revision restores evidence for the original course objectives while keeping the question about third strength and seventh tones. It does not adopt the other model's predicted grade.

## Evidence and interpretation

The completed recognizer provides audio-to-label predictions, playback, fusion comparisons, timing and error analysis. These results explain the move from window fusion to note representations. The new rock_6 diagnostic then strengthens the reason to inspect decoding before assigning an acoustic cause to the quality-error increase.

The diagnostic recomputed scores using verified frozen source and settings. Archived artifacts contained labels and grid/RMS metadata, not score arrays; validation reproduced the saved raw and decoded labels and interval boundaries. It is an exploratory analysis of the already selected recording, not a new evaluation set or model revision.

During 7.850952 s of projection's 9.893311 s of decoded same-root quality errors, the correct-root major template scored above its minor counterpart. This does NOT mean that the correct chord won the full 24-template raw decision for 7.85 s: raw predictions were correct for 5.552177 s of these decoded-error intervals. Other roots remained possible. The duration-weighted mean correct-minus-opposite quality margin across the complete 9.893311 s was negative (-0.00590777), despite the longer positive-margin duration. The paper states the sign and its implication without assigning the error solely to the decoder. Normalized feature activations are not measured acoustic energy or played-note amplitudes; physical third strength remains unmeasured.

| Evidence | Function | Final placement and scope |
|---|---|---|
| Short/CQT/long/adaptive development accuracy 64.56/64.95/71.97/71.66% | Necessary evidence for original O1.2 and O1.3 | Results 4.1; 119 GuitarSet recordings and shared decoding |
| Original fixed short weight zero | Qualification | Same paragraph; selected fixed model equals long STFT, not a positive fusion gain |
| Later blend 72.22% development; 65.56% versus 65.73% on slow IDMT | Explains project direction | Results 4.1; later blend and separate slow64 comparison explicitly distinguished |
| Development and fast64 note-model comparison | Main completed result | Table 1 and Results 4.2; existing measured values retained |
| Boundary F1 27.27/28.90% | Evidence for O2.2 | Results 4.2; 100 ms one-to-one matching defined in Methods |
| Playback and corrected development root error | Demonstration and positive example | Figure 1 and Results 4.2; real saved player data, separate rounded CSV excerpt |
| Raw/decoded durations and paired error locations | Research motivation and necessary qualification | Introduction and Results 4.3; raw and decoded evidence remain distinct |
| Triad/additional-tone error rates and rock_6 concentration | Heterogeneity and scope of question | Figure 2 and Results 4.3; selected after evaluation, no population claim |
| New 7.85/9.89 s margin result and negative mean | Diagnostic evidence supporting calibration priority | Results 4.3; full arrays, raw categories and validation stay with diagnostic artifacts |
| Ideal Cm7 equality and separate calibrations | Mathematical baseline and proposed experiment | Methods 3.2 and Discussion 6; planned work remains future tense |
| Source hashes, detailed settings, source construction and gain check | Provenance and noncentral implementation detail | Run records and README; the report retains comparison conditions needed to interpret results |

## Original basic and expected indicators

The original README objective and PI wording is retained. Table 2 abbreviates it and supplies evidence locations; it does not redefine the objectives.

| Indicator | Evidence now visible in the PDF | Supporting artifact |
|---|---|---|
| O1.1 basic: aligned audio/labels and single-window predictions | Methods 3 and Figure 2(b) | Saved predictions and recording selection |
| O1.2 basic: short, long and CQT features | Methods 3.1 and Results 4.1 numerical comparison | results/parameter_selection/candidate_summary.csv |
| O1.3 expected: fixed and adaptive fusion with shared decoder | Results 4.1 includes adaptive result, fixed-zero caveat and later blend | Original selection plus results/optimization_v2/README.md |
| O1.4 expected: playback, timeline and CSV | Figure 1, its caption and Results 4.2 | Existing demo HTML and separate prediction.csv |
| O2.1 basic: split, settings and versions | Methods 3.3 and Individual Progress 5 | configs/, requirements-lock.txt and run environment records |
| O2.2 basic: duration, coverage and boundary metrics | Methods 3.3, Table 1 and Results 4.2 | Fast summary.csv and evaluator configuration |
| O2.3 expected: recording comparisons, full timing and examples | Table 1, 30/13/16 recording comparison, positive demo and quality-error example; Methods names per-recording records | Saved per_recording.csv and examples |
| O2.4 expected: related work, results and discussion | Sections 2, 4 and 6; status explicitly scoped to this progress report | README and report; final report remains pending |

## Language, figure and preservation checks

- Introduced the working system before the error question and separated completed individual progress from remaining-stage goals. No grade forecast or certification-style claim was added.
- Replaced the vague fusion recap with the shortest comparison needed to explain the direction change. Kept both unsuccessful adaptive/fixed outcomes and the later blend's failed transfer.
- Standardized Long STFT and retained the user's requested “Our research question is:”. Restored the no-chord definition for N and “Decoded” in Table 1's caption after compression.
- Preserved the 19 bibliography entries, original PI meaning and all original measured result values. Existing overview citations and source-reading records were reused; this local revision did not re-read all cited papers or invent new literature claims.
- Figure 1 is a compact view captured from the existing development player. Browser presentation hides surrounding material and adjusts text/coordinates for a paper column; audio, reference labels and prediction data are unchanged. Its CSV row is rounded for display and comes from a separate saved file. The figure does not claim a CSV export button or inversion recognition.
- BUILD.md now links the capture record and diagnostic. It identifies the capture script as machine-specific and keeps the supplementary plot separate from the four-page submission. Its new prose was checked for accurate scope and concise wording.
- Both calibration plans remain explicit: representation-specific penalties selected by chord accuracy on GuitarSet development are frozen before exploratory fast-IDMT rescoring; separate synthetic development penalties are frozen for synthetic confirmation. Source variants remain in one split; comparisons retain raw, shared-penalty and calibrated predictions.
- The ideal Cm7 equality condition and tie-aware recording remain. Tied maximizers do not replace deterministic single-label error rates.
- Detailed synthetic sound construction and gain invariance remain in README. Repetitive result summaries, a general template-system justification, repeated future-model explanation and duplicate individual-work prose were cut. No diagnostic result was promoted to a physical mechanism.

## Approximate prose counts

Algorithm: remove full display-equation, figure and table environments; remove comments, inline math, citations, labels, references, footnotes and headings; strip remaining LaTeX command names; count alphanumeric word tokens, allowing internal punctuation. Tables inserted by macros and figure captions are excluded, so these counts describe body compression rather than total PDF text. “Before” is the project version preceding this staged revision.

| Section | Before | After |
|---|---:|---:|
| Abstract | 98 | 82 |
| Introduction | 228 | 197 |
| Related Work | 139 | 119 |
| Method and Evaluation | 506 | 484 |
| Preliminary Results / Progress and Preliminary Results | 252 | 314 |
| Individual Progress | 109 | 27 |
| Discussion and Next Experiments / Discussion and Remaining Work | 278 | 215 |
| Total counted prose | 1,610 | 1,438 |

Main results grow by 62 counted words to cover missing course evidence and the diagnostic; total counted body prose falls by 172. The original two-panel error figure remains, and one compact demonstration is added. Final build, page-count, bibliography and preservation checks are recorded separately during integration.

Earlier notes below are historical. In particular, their statement that no recognition analysis was run applies only to the prior tie/calibration wording edit, not to this new frozen-score diagnostic.

---

# Tie handling and calibration data — 2026-11-16

Applied `nature-writing` and `academic-language-audit` to the staged report and README before integration. Routing: manuscript / research / method and discussion, with a small introduction cut / zh-to-en / generic ISMIR course report. An independent review checked mathematical scope, data selection and wording.

The Cm7 example now states the general equality condition: C minor and E♭ major have equal scores when root and seventh activations match, regardless of third strength. With root, fifth and seventh set to 1, both are maximizers at all three planned third amplitudes. Ideal-feature analysis will retain deterministic single-label errors and separately record tied maximizers and reference-label membership. The README fixes an absolute score tolerance of 1e-12; this is a planned diagnostic, not a change to the recognizer.

The two calibrations now have explicit data and purposes. Representation-specific penalties selected on the 119 GuitarSet development recordings will be frozen before an exploratory fast-IDMT reassessment. Synthetic sequences have their own development and confirmation split, containing root and same-root quality changes. Source variants remain together. Both selections use duration-weighted chord accuracy; neither uses its evaluation data to choose penalties.

Removed the generic sentence following the research question and a repeated mention of optional model comparisons to make room for these details. The README retains the scoped annotation finding: no same-root quality changes at contiguous scoreable GuitarSet development boundaries. The report does not need this secondary detail to explain separate calibration.

No recognition experiment was run and no measured result, figure, bibliography, original performance indicator or implementation was changed. The three existing overview citations and prior source-reading audits remain applicable; no literature was newly evaluated in this revision. All four rendered pages were inspected. Verification details and preservation hashes are in `evidence_checks.json`.

Earlier notes below are historical; their unspecified development-data wording is superseded by the two calibrations above.

---

# Feedback revision — 2026-11-16

Applied `nature-writing` and `academic-language-audit` to staged report prose, README, table caption and figure labels before integration. Routing: manuscript / research / abstract, introduction, related work, method, results, discussion / zh-to-en / generic ISMIR course report. The research question and the requested phrase “Our research question is” are retained.

## Argument and evidence allocation

The raw same-root quality-error totals are close, whereas their decoded totals differ. Their raw error locations also differ. This motivates testing how seventh-tone presence and third amplitude affect template evidence and how decoding interprets it. The current observation is from the shared-penalty comparison; separately calibrated decoding is planned.

| Evidence | Role | Placement |
|---|---|---|
| Raw 49.58/49.64 s and decoded 19.07/27.41 s | Main observation motivating calibration | Introduction; abstract summarizes without repeating numbers |
| Raw overlap 39.29 s, unique 10.29/10.35 s | Necessary qualification: equal totals do not imply equal locations | Results §4.2 |
| Decoded correct→quality 10.60 s and reverse 2.26 s | Necessary support: changed error categories alone do not explain the finding | Results §4.2 |
| Triad/additional-tone group rates | Error localization | Figure 1(a), computed before rounding from saved durations |
| Overall +8.34 s and rock_6 +9.89 s | Concentration and scope of observation | Results §4.2; post-evaluation selection retained in caption |
| Equal-weight margin and Cm7 competing root | Mathematical baseline for the controlled experiment | Method §3.2, Eq. 2 |
| Coverage decomposition | Interpretation of evaluated time | Method §3.3 |
| Earlier fusion gains did not persist externally | Explains shift from original project objectives | One sentence in Results §4.1; full evidence remains in results/optimization_v2/README.md |
| Boundary definitions and full diagnostics | Supporting implementation evidence | README and saved results; compressed to a repository pointer in PDF |
| Proposed amplitudes, synthetic sources, calibration and decision rules | Future experiment, not completed evidence | Discussion and README |

## Changes and compression

- Replaced the Introduction's repeated recent-paper summary with the four raw/decoded durations. Related Work retains the recent papers and all 19 references in the original citation order.
- Specified equal triad weights and added the same-root score-margin formula. The fixed-root conclusion does not extend to the global 24-class winner.
- Removed the separate equal-RMS mechanism experiment. Whole-clip gain rescaling is an implementation check, consistent with normalization; no new recognition benchmark is reported.
- Defined the principal planned output as margin and error curves against third amplitude, separating major/minor conditions and root/quality errors. The margin compares correct and opposite qualities at the reference root.
- Calibration will select a representation-specific penalty by development chord accuracy, using both root and same-root quality changes. Variants of a source stay in one split; settings are frozen for confirmation.
- The initial stimuli will use unit-RMS sinusoids and six-partial complexes with 1/h weights. Root/fifth amplitudes are 1, third amplitudes {1, 0.5, 0.25}, seventh amplitudes {0, 1}. Exact source groups, registers, durations and phase settings will be fixed in experiment configurations before running the study.
- Short sequences provide the temporal context needed to inspect false switches and missed changes. Later feature or template work depends on the results; a new model is not a prerequisite for the planned diagnostic output.
- Deleted project-justification prose from Discussion and distinguished original proposal indicators from remaining-stage goals.
- Changed Figure 1(a) to percentages. Figure 1(b)'s separate legends, roots, hatching and clipping are unchanged.

## Word-count change

The same approximate prose-token rule excludes display equations and figures. Results §4.1: {'before': 93, 'after': 115}; Results §4.2: {'before': 147, 'after': 148}. Full section counts are in evidence_checks.json.

## Checks and source scope

The current source evidence is unchanged. Coverage is recomputed from the 64 saved annotation-audit records. Raw error overlap and unique durations are summed from the saved paired error matrix. Rate denominators are all supported reference chord time in each group, excluding N, not time conditioned on correct predicted roots. Values displayed after full-precision calculation are 0.92%, 0.67%, 4.15% and 7.18%.

The three previously verified overview sources remain attached to the pipeline background. This revision introduces no new literature claim requiring additional sources; it retains prior reading-depth and six-field source audits in docs/research/recent_chord_literature_2026-11-15/. The feedback check reread Cho's relevant methods, experiment and conclusion passages: the source supports model-dependent penalties in its evaluated setting, not a proven cause for this project's gap. No numerical reproduction of that paper was attempted, and its end-to-end runtime is not established by the passages used here.

An independent staged review checked the mathematical scope, evidence, tense, calibration objective and language. Word counts, numerical checks, PDF validation and file hashes are recorded in evidence_checks.json. Earlier notes below are historical and superseded where they describe an unchanged method or a duration-based Figure 1(a).

---

# Seventh-tone research question — 16 November 2026

Applied nature-writing and academic-language-audit before integrating prose into the project. Routing: manuscript / research / abstract, introduction, related work, discussion / zh-to-en / generic ISMIR course report. The approved question is: **How does an added seventh affect major/minor recognition as third strength varies?**

The report presents completed representation comparisons and exploratory error localization, followed by a planned paired-audio study. The new study has not been run. Calibration is a comparison control; seventh-aware templates and a frozen recent model are extensions. The report remains four pages with 19 cited references. The README uses the same question, status, schedule and bibliography numbering.

## Terminology

| Term | Meaning in this report |
| --- | --- |
| Third strength | Third-tone amplitude relative to fixed root and fifth components; pitch is unchanged. |
| Added seventh | A minor seventh above the root in the initial planned experiment, producing dominant or minor seventh chords. |
| Chord accuracy | Correct duration under the stated major/minor comparison, including reference N. |
| Root accuracy | Root agreement on supported reference chords, excluding reference N. |
| Same-root quality error | Correct root with wrong major/minor type; reported as duration on fixed reference-supported intervals. |
| Raw / decoded | Framewise maximum template score / Viterbi sequence using the stated switching penalty. |

## Argument and evidence placement

| Material | Function | Placement |
| --- | --- | --- |
| Overall improvement under projection | Completed result and necessary context | Table 1; brief direction in abstract; quantified comparison in §4.1. |
| Raw/decoded quality-error durations and paired changes | Main evidence for a narrower question | §4.2, unchanged measurements. |
| Concentration in rock_6 and original A7/D7/E7 labels | Diagnostic and limit of the current observation | §4.2 and Figure 1; third strength remains unmeasured. |
| Triad vs additional-tone reference groups | Conditional error pattern | Figure 1; not a randomized seventh intervention. |
| Transition counts and no-chord diagnostic | Secondary context | Detailed counts stay in README and saved annotation diagnostics; omitted from the new central argument. |
| Seventh presence × third amplitude | Approved future study | §5; paired controls, development/confirmation separation and raw/decoded errors. |
| Original objectives and their completion status | Course requirement | Table 2 and individual section, preserved. |

The introduction follows task → root/quality meaning → seventh-chord label reduction → recent findings → the focused question. Discord and ChordFormer establish component-analysis precedents. Ding et al. supplies a contemporary two-stage comparison, not a claim that our frontend or cause is already validated. Recent event-based work motivates checking true chord changes as well as false switches. The actual source-reading depths and six-field audits are in [the recent review](../docs/research/recent_chord_literature_2026-11-15/review.md).

## Editing and consistency checks

Replaced the broad question and decoder-centred follow-up with the approved acoustic question. Removed the abstract's several performance numbers; their measured values remain in the table. Expanded the musical explanation and experiment logic without shrinking template typography or adding decorative headings. Removed an unspecified claim that recent methods improve recognition. Kept the original performance indicators and changed only the remaining research goals.

The ideal pitch-class control matters because adding a seventh outside both same-root triad templates can shrink their normalized score gap without reversing its sign. A score change is therefore not automatically a quality error. This is a consequence of the existing equal-weight template rule, not a newly measured finding. Paired complete-label changes and root errors remain necessary alongside quality-error durations.

The three verified reviews support the continuous foundational overview. Specific recent findings cite their original papers. Removed five tangential references and added Ding 2026, ChordFormer 2026, Kim–Park 2026 and Phan 2026; corrected Discord's proceedings metadata. Actual methods remain described using the inspected versions. Reference count: 19.

## Approximate section word counts

Counts use alphabetic tokens after removing citation/label commands and LaTeX command names; they include figure captions in the Results section, exclude table macro contents, and should not be interpreted as publisher word counts. The expansion is concentrated in the requested introduction and planned experiment.

| Section | Before | After |
| --- | ---: | ---: |
| Abstract | 101 | 103 |
| Introduction | 123 | 263 |
| Related Work | 164 | 192 |
| Method and Evaluation | 498 | 498 |
| Preliminary Results | 295 | 291 |
| Discussion and Next Experiments | 212 | 309 |
| Individual Progress: Christopher Xu | 87 | 108 |

The source methods section is byte-for-byte unchanged. Results lose four words under this counting rule; no numerical result changes. Figure artwork and both table macros are unchanged. Numeric-source hashes and final PDF checks are recorded in `evidence_checks.json`; recognition tests were not rerun for this writing revision.

---

Earlier revision records follow. Their framing, counts and plans describe earlier versions.

# Language audit revision — 14 November 2026

Applied nature-writing as the core writing skill and academic-language-audit to the proposed edits before integration. Reused the established manuscript / research / English report / generic ISMIR-course framing. This is a local revision, not a change to the research question or experiments.

The Discussion now attributes the increase in quality-error duration to `rock_6`, rather than attributing all quality failures to it. The abstract names the comparison baseline, the paired result states its direction, and the caption names the criterion used to select the example. The Introduction specifies quality-specific smoothing, since root transitions already support other temporal evaluations. Feature extraction replaces chroma processing as the umbrella term. Removed the generic abstract sentence introducing the report's contents.

Verified a third review, Müller's 2021 FMP educational guide, whose chord-recognition section directly covers the pipeline. Three reviews support the Introduction's overview together; the repeated overview sentence in Related Work is removed. README and both bibliography files are synchronized. Specific method and experimental claims retain their original research citations. The source check records actual reading depth and the broader scope of the educational review in `overview_sources.md`.

The final PDF check exposed an isolated schedule fragment under Table 2. Compressed the date sentence without changing its dates or tasks.

The numerical results, figure artwork, methods, evaluation conditions and individual performance indicators are unchanged. No recognition experiments or code tests were rerun for this prose revision. Earlier notes below describe earlier versions and their then-current reference counts.

---

# Figure 1b clipping and reference clarification — 13 November 2026

The reference row contains A7, D7 and E7; all reduce to major triads in the evaluation vocabulary. The caption now identifies these labels rather than using “sevenths” alone. Hatching applies to predictions. Around 15–18 seconds, G:min, D:min and A:min occupy successive intervals, so all three root colours correctly carry hatching.

Replaced the timeline collections with individual rectangles, set each rectangle's clipping region to its own bounds, reduced hatch stroke width to 0.45 points, and redrew the interval outlines. Both the PNG and vector PDF were visually inspected, including a 400-dpi PDF rendering. The interval coordinates and all input predictions are unchanged; predictions are not snapped to reference boundaries. Applied the two writing skills to the revised caption and this explanation.

---

# Figure 1b legend revision — 13 November 2026

Applied the existing academic-language-audit and nature-writing workflow to the figure labels and caption. Visual inspection confirmed that chord names overlap narrow intervals and hatching. Removed in-bar text and added external legends: colour encodes root, while solid/hatched prediction intervals encode major/minor. The reference row is marked “7th”; its displayed labels are A7, D7 and E7. “Other” groups D-sharp and G roots in the displayed predictions; there are no N intervals in this span. The data, interval boundaries, colours and hatch assignments are unchanged.

The figure remains a two-panel scientific plot; a third plotting axis only holds legends. Increased its height to make the legends readable at column width. The report is rebuilt with the same ISMIR settings and checked at its final size. No new experimental result is introduced.

---

# Follow-up: remove the window-fusion narrative — 13 November 2026

This follow-up supersedes the earlier main-text allocation below. Routing remains manuscript / research / introduction, methods and results / zh-to-en / generic. The user requested that past experiments appear only where needed for the current research question.

The evidence chain is now: compare three representations → distinguish root and quality errors → inspect the localized quality loss → design decoder-calibration and controlled-transition tests. The original window-fusion accuracy comparison and its method description are removed from both the report narrative and README. They remain in saved experiment outputs, linked from README. The original PI table is retained because the course asks for status against the design objectives.

| Material | Allocation |
| --- | --- |
| Current representation accuracies and runtime | Core: Table 1 and §4.1, unchanged values |
| Raw/decoded quality errors, paired analysis and reference strata | Core diagnostic and qualification: §4.2 and Figure 1, unchanged |
| Window-fusion tests and isolated-chord ceiling | Historical context: saved results; removed from current Results |
| Earlier selection of λ=4 and shared slow/fast piece IDs | Necessary provenance: retained briefly in Methods |
| Original objectives and completed fusion implementation | Course requirement: retained in individual PI table |

Using the same approximate source-word counting rule as below, the first Results subsection falls from 298 to 177 words (including its table macro); the quality-error subsection remains 221 words. The subtitle now names root and quality errors while retaining the user's report heading and CSC575 author block. The final-goals paragraph was shortened without changing its tasks or dates. No text was added to fill the freed space. The compiled report remains four pages including 19 cited references. Recognition code, configurations and stored predictions are unchanged.

---

## Earlier rewrite record (before this follow-up)

# Four-page report revision — 13 November 2026

Applied `academic-language-audit` and `nature-writing` before integration. Nature-writing routing: manuscript / research / title, abstract, introduction, related work, methods, experiments and discussion / zh-to-en / generic. The target is an individual ISMIR-format course report. Nature guidance is used for argument and sentence editing, not as a journal requirement.

## Structure learned from related papers

The source-reading records are in [literature_audit.md](../docs/research/root_questions_2026-11-13/literature_audit.md) and [followup_sources.md](../docs/research/root_questions_2026-11-13/followup_sources.md). They distinguish inputs, operations, outputs, errors and guarantees, costs, and failure conditions. This revision reuses those audits; it does not claim a new full-text review of all 19 references.

| Paper and inspected structure | Writing choice adopted here |
| --- | --- |
| [Cho, Weiss and Bello, 2010](https://ronw.net/pubs/smc2010-chordreco.pdf): introduction, common system architecture, experiments separating processing choices, conclusions. The source audit records the inspected sections and numerical comparisons. | Define the shared pipeline before reporting feature comparisons. Give uniform decoder calibration a concrete role as a control. |
| [Korzeniowski and Widmer, EUSIPCO 2018](https://new.eurasip.org/Proceedings/Eusipco/Eusipco2018/papers/1570432212.pdf): problem definition, model formulation, experiments, conclusions. Architecture and the temperature/target-smoothing findings were inspected. | State the decoding objective and explain why changing acoustic scores may change the useful penalty. Do not equate neural probability temperature with cosine-score calibration. |
| [Poltronieri, Serra and Rocamora, 2025](https://arxiv.org/html/2509.01588v1): introduction, related work, methods with annotation analysis, evaluation, conclusions. The audit covers methods, tables and ablations. | Present component errors alongside complete-label accuracy, then use the original annotations to interpret a local failure. |

Only organization is borrowed; the report prose is newly written for this project. The title and question name the measured error components. The argument runs from a broad recognition question to the working comparison, the localized quality result, competing explanations and discriminating experiments. A short individual-progress section carries the course-specific PI and final-goal requirements.

The existing ISMIR style is retained, without shrinking its margins or body font. The four-page limit includes references. Nineteen bibliography entries are cited. Cho's proceedings pages were checked against the author's bibliography; the EUSIPCO pages come from its proceedings PDF. Discord is linked to the inspected arXiv v1; unverified proceedings pagination and DOI are omitted.

## Main-text allocation and claim–evidence map

| Material | Function and placement | Evidence and status |
| --- | --- | --- |
| Projection improves complete-label and root accuracy at modest added time | Core result: abstract, Table 1, §4.1 | Saved development and fast summaries; measured in the stated recordings. Abstract gives before/after values, table gives all three methods, prose gives differences and heterogeneity. |
| Window fusion fails to improve the reported comparisons | Necessary context: one §4.1 paragraph | Original GuitarSet test and slow-IDMT results. Full old tables remain in README and saved results. |
| Both decoded representations reduce quality errors, but by different amounts | Core diagnostic: §4.2 | Raw and decoded fast summaries. This prevents attributing the between-method difference to decoding being universally harmful. |
| Previously correct intervals become quality errors | Necessary support: §4.2 paired durations | Paired interval analysis, not a comparison of changing root-correct denominators. |
| Loss is concentrated in an extended-reference example | Qualification plus diagnostic: Figure 1 and §4.2 | Reference pitch-class strata and `rock_6` timeline. Associational, selected after evaluation; not evidence of a general spectral mechanism. |
| Development lacks same-root quality changes | Experiment-design reason: §5 | Annotation diagnostics. Motivates controlled true-change cases rather than choosing a large penalty solely on development accuracy. |
| Calibration and structured penalties | Future work: §5 | Competing explanations and proposed controls. No result claimed. |
| Individual contribution and completion status | Course requirement: §6 and Table 2 | Original objectives, saved runs and existing demo. Final report and advanced PIs remain open. |

## Compression and repetition audit

Replaced the two older error/example figures with one two-panel diagnostic. Compressed the original benchmark table and window follow-up into one paragraph. Retained a single comparison table for the current representations. Removed detailed harmonic-decay scores, repeated fast-set coverage prose and full genre enumeration; these remain in saved results and README. Moved detailed source checks and editing rationale to these notes. The report's qualifications are attached to the results they constrain.

| Revised results material | Before | After |
| --- | ---: | ---: |
| Original GuitarSet test | 237 | Combined below |
| Window follow-up | 79 | Combined below |
| Root-error follow-up | 331 | Combined below |
| From window fusion to note representations | — | 298 |
| Where the quality errors changed | — | 221 |
| Combined results allocation | 647 | 519 |

Counts are approximate source-word counts after expanding `results.tex` macros and removing LaTeX commands, citations, labels and image paths; they include table and caption text but omit words embedded in figures. Section mappings changed, so only the combined comparison describes compression of the same reporting area. The new Discussion separately develops the explanations and proposed tests.

The abstract repeats only the principal comparison and its local qualification. §4 supplies the measurements. §5 interprets them without repeating the numerical table, and derives the next experiments. Statistical tests or confidence intervals are not implied: recordings repeat pieces, and suitable grouping remains an advanced objective.

## Checks and remaining evidence

`evidence_checks.json` records numeric comparisons, bibliography coverage, artifact hashes and final PDF checks. The new figure is generated from saved predictions and annotation diagnostics; no recognizer training or tuning was performed during this rewrite. Recognition code and original experiment outputs are unchanged. The earlier record of 96 passing tests is historical, not a newly run test result.

Uniform-penalty calibration, controlled same-root changes and evaluation on new pieces are still planned. The progress report is a snapshot of completed comparisons and a research plan, rather than a claim that those proposed studies have already succeeded.
