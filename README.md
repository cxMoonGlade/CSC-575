# Major/Minor Errors in Guitar Chord Recognition

CSC475/575 progress report  
Christopher Xu | Solo project | November 16, 2026

[Four-page ISMIR report](report/progress_report.pdf) · [Playback notebook](notebooks/listen.ipynb)

## Project description

The program takes guitar audio and produces a playable timeline with twelve major and twelve minor chords, plus a no-chord label (`N`). Comparisons of spectral features and note representations improved root accuracy, but exposed a difference in major/minor errors. Long STFT and projection have nearly equal raw error durations for chords with the correct root but wrong quality; the gap widens after shared decoding and is concentrated in one seventh-chord recording. A shared switch penalty need not have the same effect on different feature scores.

Seventh chords provide a controllable case. Adding B♭ to C major or C minor produces C7 or Cm7 while preserving the major/minor target. The third, E or E♭, distinguishes the two qualities. With our triad templates, adding only a seventh component to ideal pitch-class inputs reduces the magnitude of a nonzero same-root score gap through L2 normalization, without reversing its sign. Varying third amplitude tests the added tone across stronger and weaker evidence for quality.

Our research question is: **How does an added seventh affect major/minor recognition as third strength varies?** Here, *third strength* means amplitude relative to fixed root and fifth components. Comparisons of ideal inputs, paired audio and calibrated decoding will trace how the added tone affects scores and final labels.

## Data and tools

GuitarSet v1.1.0 microphone recordings and performed chord annotations [18] supply development data. After excluding two recordings with known timing errors, progressions 1 and 2 provide 119 recordings. Progression 3 is excluded from parameter selection. All styles, performers, tempi and transpositions of a progression stay together; the [saved split](configs/guitarset_split.json) records these assignments. The annotations retain score-derived boundaries, so boundary scores measure agreement with annotated changes.

Evaluation uses 64 IDMT-SMT-Guitar recordings [19] from subset 4, `acoustic_mic/fast`. Their piece IDs also occur in the earlier `acoustic_mic/slow` comparison. Settings were fixed before fast-set scoring; subsequent error analysis is exploratory.

The code uses Python, NumPy/SciPy, librosa [16], SoundFile, and mir_eval [17]. Dataset and software links are in [docs/resources.md](docs/resources.md).

## Method

Audio is converted to mono at 22,050 Hz. The Long STFT baseline derives chroma from short-time Fourier transform (STFT) magnitudes with an 8,192-sample Hann window and a 512-sample hop. All three representations share a tuning estimate, MIDI range 36–95, C-first pitch-class order and per-frame L2 normalization.

The note-based candidates estimate note strengths from the same magnitude spectrum before octave folding. Their dictionaries contain tuned Hann-windowed sine profiles. Non-negative least squares (NNLS) fits all notes jointly; direct projection fits each note separately. The selected versions use fundamental-only profiles.

The 24 triad templates assign equal weights to their three notes and have unit L2 norm. For a nonzero chroma vector $c$ before normalization, the same-root score difference is

$$
s(C\mathrm{maj})-s(C\mathrm{min})
=\frac{c_E-c_{E^\flat}}{\sqrt{3}\,\lVert c\rVert_2}.
$$

Adding energy only at B♭ shrinks any nonzero score difference without reversing the pair's ordering. Other roots can still compete: for ideal Cm7, C minor and E♭ major have equal scores whenever root and seventh activations match, regardless of third strength. With root, fifth and seventh activations set to 1, they are tied for the highest score at all three planned third amplitudes. This provides a baseline for the audio experiments.

Frames at or below −45 dB relative to the recording's peak root-mean-square (RMS) amplitude receive `N`. Raw predictions select the highest-scoring label; Viterbi decoding adds a common chord-switch penalty of 4, retained from an earlier development search. This compares representations under a shared decoder. L2 normalization does not make their score differences equal, so a separately calibrated comparison is planned. Consecutive identical predictions become timed intervals. The [search record](results/parameter_selection/selection_plan.json) and [frozen configuration](configs/frozen.json) preserve that selection.

## Evaluation and results

Duration-weighted chord accuracy is correctly labelled time divided by scoreable time. Reference labels follow `mir_eval.majmin`; unsupported chords and gaps are excluded and their duration reported. Equivalent labels are merged before one-to-one boundary matching within 100 ms. Gap edges are excluded. A separate diagnostic measures label accuracy within 0.2 s of supported reference changes, clipped to each continuous scoreable span.

### Window and fusion experiments

On the 119 GuitarSet development recordings, short-window STFT, CQT, long-window STFT and adaptive fusion reached 64.56%, 64.95%, 71.97% and 71.66% duration-weighted chord accuracy, respectively, with the shared switch penalty of 4. The original fixed-weight search selected zero short-window weight, matching the long-window baseline. The [selection results](results/parameter_selection/candidate_summary.csv) and [frozen test comparison](results/test_frozen/summary.csv) retain all methods.

A later 4,096/8,192-sample blend with short-window weight 0.2 reached 72.22% on development data. On 64 IDMT `acoustic_mic/slow` recordings, it scored 65.56%, compared with 65.73% for Long STFT. This small development gain did not transfer, prompting the move from window fusion to note representations. The [follow-up record](results/optimization_v2/README.md) includes near-change accuracy and timing.

### Representation comparison

Estimating note strengths before octave folding improved development accuracy. The spectrum, tuning, templates, silence rule and decoder remain fixed.

| Method | Development chord accuracy | Development root accuracy |
|---|---:|---:|
| Long STFT | 71.97% | 74.48% |
| Fundamental-only NNLS | 78.37% | 80.15% |
| Direct projection | 78.02% | 79.54% |

Both candidates improved both development families. Adding modeled harmonic partials performed worse than fundamental-only NNLS; low-register weighting did not improve chord accuracy. Root accuracy ignores major/minor quality, with predicted `N` counted as incorrect on reference chords.

The frozen evaluation used all 64 `acoustic_mic/fast` recordings: 29.77 minutes with 59.56% scoreable coverage. Unannotated prefixes and tails account for 27.07% of total audio time; unsupported reference labels account for 13.37%. Five recordings have no scoreable intervals. These are faster versions of the same pieces used in the earlier slow-tempo comparison, so they test transfer within that repertoire.

| Method | Chord accuracy | Root accuracy | Complete runtime |
|---|---:|---:|---:|
| Long STFT | 64.70% | 73.91% | 9.49 s |
| Direct projection | 67.80% | 78.32% | 10.43 s |
| Fundamental-only NNLS | 66.95% | 78.45% | 44.37 s |

Chord accuracy includes reference `N`; root accuracy excludes it. Runtime covers all 64 files on one CPU thread, without feature caching. Projection gained 3.10 percentage points in chord accuracy and 4.41 points in root accuracy, with about 10% more processing time. NNLS scored slightly higher on roots but made more major/minor errors. Projection improved 30 of the 59 scoreable recordings, tied on 13 and worsened 16; rock/blues accuracy fell by 6.18 points.

Decoded boundary F1 on fast IDMT was 27.27% for Long STFT and 28.90% for projection, using the 100 ms one-to-one matching rule above. These scores measure agreement with annotated changes. The [saved results](results/root_optimization/fast/summary.csv) also report precision, recall and timing error.

Direct projection is the preferred option for the current guitar workflow, available through `chordrec.note_predict`; the original command still reproduces the long-window baseline. New pieces remain a separate evaluation target. [Results, examples and reproduction notes](results/root_optimization/README.md) include the full comparisons.

### Preliminary error analysis and next experiments

Decoding reduces same-root quality-error time for both Long STFT (49.58 → 19.07 s) and projection (49.64 → 27.41 s), but by different amounts. Similar raw totals do not imply errors at the same times. On matched intervals, decoded projection introduces 10.60 s of same-root quality errors where decoded Long STFT is correct, and corrects 2.26 s of long-STFT quality errors. To revisit this difference, each representation's penalty will be selected by duration-weighted chord accuracy on the 119 GuitarSet development recordings and frozen before rescoring fast IDMT. This remains an exploratory comparison; fast IDMT will not be used to choose the penalties.

On references containing only triad pitch classes, decoded quality errors decrease from 0.92% to 0.67% of the group's 612.93 s; on supported references with additional tones, they increase from 4.15% to 7.18% of 324.01 s. These rates use all supported chord time in each group. The net increase is 8.34 s, with `rock_6` contributing 9.89 s and other files partly offsetting it. Its A7, D7 and E7 labels reduce to major triads. This concentration motivates the seventh-tone experiment; third strength has not been measured in these recordings.

A [frame-score diagnostic of `rock_6`](docs/research/rock6_third_diagnostic_2026-11-16/README.md) reproduced all four saved prediction tracks. During 7.85 of projection's 9.89 s of decoded quality errors, the reference major template still outscored its same-root minor counterpart. The mean margin over these errors was negative (−0.00591), so positive-margin duration alone does not determine the preferred sequence. The raw prediction over all 24 templates was correct for 5.55 s within these errors. These checks give calibration priority; they do not identify the source of minor-third activations or measure played-note amplitudes.

The next experiments will proceed in three steps:

1. **Ideal features.** Calculate template margins and competing roots from known pitch-class activations, analysing major and minor conditions separately. Record all templates within an absolute score tolerance of 1e-12 of the maximum. Keep the deterministic single-label error rate, and report ties and reference-label membership in the maximizing set separately, so tie-breaking choices are identifiable.
2. **Paired audio.** Hold root and fifth amplitudes at 1, vary third amplitude over {1, 0.5, 0.25}, and set minor-seventh amplitude to either 0 or 1. Use unit-RMS sinusoids and harmonic complexes with six partials weighted by inverse harmonic number. Within each root, register and timbre condition, pairs will share component waveforms, onsets, duration and envelopes. Whole-clip RMS rescaling will serve only as a gain-invariance check, because frame normalization removes uniform gain in the ideal calculation.
3. **Raw and calibrated decoding.** The synthetic study will use its own development and confirmation sequences with root and same-root quality changes. The GuitarSet development annotations contain no same-root quality changes at contiguous scoreable chord boundaries. Select each representation's penalty by duration-weighted chord accuracy on the synthetic development sequences and freeze it for confirmation. Variants of a source sound will stay in one split. Compare raw, shared-penalty and calibrated predictions to assess false switches and missed changes.

The main result will be curves of the correct-versus-opposite quality score margin at the reference root and chord-error rates against third strength, with and without the seventh. Root errors and same-root quality errors will be reported separately for major and minor references. If GuitarSet calibration removes the observed fast-IDMT gap, follow-up work will focus on score scaling and temporal weighting. In the synthetic study, deviations from ideal margins would motivate inspection of audio features, while persistent root competition would motivate a template revision. Seventh-aware templates and a frozen recent model remain conditional extensions. Confirmation on real guitar will require new pieces.

The [recent literature review](docs/research/recent_chord_literature_2026-11-15/review.md), [paired error analysis](docs/research/root_questions_2026-11-13/report_design.md) and [annotation diagnostics](docs/research/root_questions_2026-11-13/annotation_check.json) document the evidence behind this plan. The four-page report presents the main findings; full recording-level results remain in the repository.

## Running the code

Use Python 3.13; the saved runs used 3.13.13. First follow the [GuitarSet download and extraction steps](docs/resources.md#guitarset), then run these commands from the repository root. `prepare` reads the downloaded files and writes the recording split.

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python -m chordrec prepare
.venv/bin/python -m ipykernel install --sys-prefix --name chordrec --display-name "Chord recognition (.venv)"
.venv/bin/python -m chordrec run --config configs/frozen.json --split development --performer 00 --output results/dev_repeat
.venv/bin/python -m pytest -q
```

GuitarSet audio stays under `docs/datasets/GuitarSet/`. The [IDMT reproduction guide](docs/research/root_optimization/fast_validation/README.md) provides separate download and evaluation commands for the fast-tempo comparison. Open the notebook with the project’s `.venv` Python kernel (registered above as **Chord recognition (.venv)**) for playback, chord plots, and CSV inspection. A [standalone player](results/test_frozen/examples/00_BN3-119-G_comp/playback.html) provides a clickable timeline. The test set has now been used; subsequent method changes need fresh held-out material for a new generalization claim.

The [note-projection player](results/root_optimization/demo_projection/playback.html) compares the baseline and candidate on a development example, where projection corrects an opening C-major interval labelled E minor by Long STFT. Its [preview](results/root_optimization/demo_projection/browser_preview.png) shows the playback controls; the separate [CSV output](results/root_optimization/demo_projection/prediction.csv) records interval starts, ends and labels. Download either player HTML file and open it in a browser; the audio is embedded. GitHub displays the HTML source. To process another file and export its chord intervals:

```bash
.venv/bin/python -m chordrec.note_predict --audio path/to/audio.wav --config configs/note_projection.json --output results/my_audio
```

Use `configs/note_nnls.json` for NNLS. Choose a new output directory; it will contain `prediction.csv`, the configuration, input hashes and timing.

## Related work

Reviews describe chord recognition through spectral features, chord models and temporal context [1, 2, 3]. Vocabulary reduction and annotation differences affect what counts as a correct label [4, 5]. These issues matter here because seventh chords retain additional notes in the audio even when evaluation reduces their labels to major or minor.

Mauch and Dixon [9] estimate note activations with harmonic profiles and NNLS; reassigned spectra [10] and learned chroma [11] offer other pitch representations. Ding et al. [6] revisit a learned two-stage system and compare estimated pitches with score-derived inputs. Their experiments motivate checking both the representation and its interpretation. ChordFormer [7] predicts structured chord components and examines quality confusions with a correct root. Poltronieri et al. [8] use component predictions and consonance-based training-label smoothing; one ablation improves root accuracy while reducing major/minor accuracy. The proposed experiment changes the audio while keeping its reduced target label fixed.

Suitable switching penalties depend on the acoustic model [12]. Duration modelling [13] and event-based prediction [14] address sequence structure more explicitly, motivating comparison of raw predictions and calibrated decoding. Phan et al. [15] release weights for a pseudo-labeling and distillation model, offering a possible later comparison beyond the current templates.

## Christopher Xu

I handle the audio pipeline, fusion and note representations, evaluation, and report. The following objectives and indicators are retained from the original proposal.

- Objective 1: Build a functional multi-resolution chord recognizer.
  - PI1 (basic): Load aligned audio and annotations and produce single-window chord predictions.
  - PI2 (basic): Extract aligned short-window, long-window, and CQT chroma.
  - PI3 (expected): Implement fixed and adaptive fusion with the shared decoder.
  - PI4 (expected): Provide playback, a chord timeline, and timestamped CSV export.
  - PI5 (advanced): Compare reassigned chroma with the main front ends.

- Objective 2: Evaluate the recognition methods and explain their differences.
  - PI1 (basic): Save the recording split, settings, and software versions.
  - PI2 (basic): Calculate duration accuracy, annotation coverage, and boundary metrics.
  - PI3 (expected): Compare test results and full runtime by recording, with examples of improved and worsened predictions.
  - PI4 (expected): Complete the related work, results, and discussion in the README and final report.
  - PI5 (advanced): Estimate uncertainty by bootstrapping whole test songs.

O1 PI1–PI4 and O2 PI1–PI3 are complete. O2 PI4 is complete for the current README and progress report; the final report remains to be written. The [split](configs/guitarset_split.json), [frozen settings](configs/frozen.json) and [software versions](requirements-lock.txt) support O2 PI1. Both advanced indicators remain open. The original song-level bootstrap goal needs a dataset with independent songs; the present test split contains one progression family.

### Completed milestones

| Dates | Work |
|---|---|
| Nov. 7 | Completed the pipeline, development selection, frozen test comparison, and report draft. |
| Nov. 9 | Completed error analysis, note-profile experiments, and the isolated-chord comparison. |
| Nov. 10 | Completed the frozen fast-tempo comparison and updated the report. |
| Nov. 11–13 | Completed the literature follow-up, paired error analysis, annotation checks and revised report. |
| Nov. 15–16 | Updated the recent literature review and focused the research question on seventh tones and third strength. |

## Remaining work

These goals extend the original proposal:

- **Basic:** retain the reproducible recognizer, saved comparisons and playback demonstration.
- **Expected:** complete the paired seventh-tone experiment, decoder calibration and error analysis.
- **Advanced:** investigate seventh-aware templates or a frozen recent model if the results support that direction, with confirmation on new pieces.

| Working dates | Objective |
|---|---|
| Nov. 16–19 | Calibrate the real-recording comparison on GuitarSet; analyse ideal ties and prepare synthetic development and confirmation sequences. |
| Nov. 20–26 | Produce paired margin and error curves, comparing raw predictions with shared-penalty and calibrated decoding. |
| Nov. 27–Dec. 3 | Finish the final report and demonstration. |

## References

Full BibTeX entries are in [references.bib](references.bib).

[1] M. McVicar, R. Santos-Rodríguez, Y. Ni, and T. De Bie. "Automatic Chord Estimation from Audio: A Review of the State of the Art." *IEEE/ACM TASLP* 22(2), 556-575, 2014. [DOI](https://doi.org/10.1109/TASLP.2013.2294580).

[2] J. Pauwels, K. O'Hanlon, E. Gómez, and M. B. Sandler. "20 Years of Automatic Chord Recognition from Audio." *ISMIR*, 54-63, 2019. [DOI](https://doi.org/10.5281/zenodo.3527739).

[3] M. Müller. "An Educational Guide through the FMP Notebooks for Teaching and Learning Fundamentals of Music Processing." *Signals* 2(2), 245–285, 2021. [DOI](https://doi.org/10.3390/signals2020018).

[4] E. J. Humphrey and J. P. Bello. "Four Timely Insights on Automatic Chord Estimation." *ISMIR*, 673-679, 2015. [Paper](https://archives.ismir.net/ismir2015/paper/000294.pdf).

[5] H. V. Koops, W. B. de Haas, J. A. Burgoyne, J. Bransen, A. Kent-Muller, and A. Volk. "Annotator Subjectivity in Harmony Annotations of Popular Music." *Journal of New Music Research* 48(3), 232-252, 2019. [DOI](https://doi.org/10.1080/09298215.2019.1613436).

[6] Y. Ding, Y. Venohr, S. Strahl, M. Müller, and C. Weiß. "Revisiting Two-Stage Audio Chord Recognition in the Deep-Learning Era: Leveraging Multi-Pitch Estimation and Symbolic Pretraining." *ISMIR*, 552–560, 2026. [Paper](https://ismir2026program.ismir.net/poster_266.html).

[7] M. W. Akram, S. Dettori, V. Colla, and G. C. Buttazzo. "ChordFormer: A Conformer-Based Architecture for Large-Vocabulary Audio Chord Recognition." *IEEE Transactions on Audio, Speech and Language Processing* 34, 581–595, 2026. [DOI](https://doi.org/10.1109/TASLPRO.2025.3646468).

[8] A. Poltronieri, X. Serra, and M. Rocamora. "From Discord to Harmony: Decomposed Consonance-Based Training for Improved Audio Chord Estimation." *ISMIR*, 492–500, 2025. [DOI](https://doi.org/10.5281/zenodo.17811559).

[9] M. Mauch and S. Dixon. "Approximate Note Transcription for the Improved Identification of Difficult Chords." *ISMIR*, 135-140, 2010. [Paper](https://webspace.eecs.qmul.ac.uk/s.e.dixon/pub/2010/Mauch-Dixon-ISMIR-2010.pdf).

[10] M. Khadkevich and M. Omologo. "Reassigned Spectrum-Based Feature Extraction for GMM-Based Automatic Chord Recognition." *EURASIP Journal on Audio, Speech, and Music Processing* 2013, article 15, 2013. [DOI](https://doi.org/10.1186/1687-4722-2013-15).

[11] F. Korzeniowski and G. Widmer. "Feature Learning for Chord Recognition: The Deep Chroma Extractor." *ISMIR*, 37-43, 2016. [Paper](https://arxiv.org/abs/1612.05065).

[12] T. Cho, R. J. Weiss, and J. P. Bello. "Exploring Common Variations in State of the Art Chord Recognition Systems." *Sound and Music Computing Conference*, 1–8, 2010. [Paper](https://ronw.net/pubs/smc2010-chordreco.pdf).

[13] F. Korzeniowski and G. Widmer. "Improved Chord Recognition by Combining Duration and Harmonic Language Models." *ISMIR*, 10-17, 2018. [Paper](https://archives.ismir.net/ismir2018/paper/000300.pdf).

[14] L. Kim and J. Park. "An Event-Based Sequence Modeling Approach to Recognizing Non-Triad Chords with Oversegmentation Minimization." *ICASSP*, 2026, accepted paper; author manuscript. [Paper](https://arxiv.org/abs/2604.24386v1).

[15] N. Phan, R. Jin, G. Liu, and X. Dong. "Enhancing Automatic Chord Recognition via Pseudo-Labeling and Knowledge Distillation." *DAFx*, 2026; author manuscript v5. [Paper](https://arxiv.org/abs/2602.19778v5).

[16] B. McFee, C. Raffel, D. Liang, D. P. W. Ellis, M. McVicar, E. Battenberg, and O. Nieto. "librosa: Audio and Music Signal Analysis in Python." *Proceedings of the 14th Python in Science Conference*, 18-24, 2015. [DOI](https://doi.org/10.25080/Majora-7b98e3ed-003).

[17] C. Raffel, B. McFee, E. J. Humphrey, J. Salamon, O. Nieto, D. Liang, and D. P. W. Ellis. "mir_eval: A Transparent Implementation of Common MIR Metrics." *ISMIR*, 367-372, 2014. [Paper](https://www.justinsalamon.com/uploads/4/3/9/4/4394963/raffel_mir_eval_ismir2014.pdf).

[18] Q. Xi, R. M. Bittner, J. Pauwels, X. Ye, and J. P. Bello. "GuitarSet." Version 1.1.0, Zenodo, 2019. [Dataset](https://doi.org/10.5281/zenodo.3371780).

[19] C. Kehling, A. Männchen, and A. Eppler. "IDMT-SMT-Guitar Dataset." Version 1.0.0, Zenodo, 2023. [Dataset](https://doi.org/10.5281/zenodo.7544110).
