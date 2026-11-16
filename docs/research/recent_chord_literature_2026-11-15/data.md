# Recent audio chord recognition: data and pretrained representations

Candidate numbers in this source audit refer to the previous six-question list. The revised priority order is in [review.md](review.md).

Scope: selective primary-source check through 2026-11-15; not an exhaustive review. No model inference was executed. The three works below are original studies/system submissions, not overview papers. The six-field records distinguish reported methods/results from our proposed implications.

## 1. Phan et al., Enhancing Automatic Chord Recognition via Pseudo-Labeling and Knowledge Distillation (2026)

Primary metadata: https://arxiv.org/abs/2602.19778 . Submitted 23 February 2026; v5 dated 3 July 2026; arXiv explicitly says accepted to DAFx26. Local PDF has DAFx26 proceedings header. Read v5 §§3–6, equations 1–10 and Tables 1–4, including noise ablation and conclusion. This is research, not a survey.

- Input: CQT features from FMA/DALI/MAESTRO (over 1,000 hours), pretrained BTC teacher; later 600 labelled songs split 420/60/120 (§4.1).
- Operations: teacher pseudo-labels all frames, student pretraining, then labelled fine-tuning with confidence-weighted distillation (§3.2).
- Output: framewise 170-class chord recognition; 2E1D additionally uses Gaussian smoothing and overlapping windows (§3.2.5).
- Error/guarantees: mir_eval chord and segmentation metrics, quality-balanced accuracy; empirical comparisons, no accuracy/generalization guarantee. Best BTC MajMin is 80.24 against teacher 79.00 (Tables 1–2), on their split.
- Total cost: CQT extraction, teacher inference, student training, teacher targets during distillation, fine-tuning and output smoothing. Stage-one convergence: 30–40 epochs with KD versus 50–70 without. GPU-hours, hardware, end-to-end latency and preprocessing time are not reported in the read text.
- Failure conditions: authors identify teacher bias/weak generalization transfer (§6); noisy-label adaptation degrades without regularization (Table 4). Guitar-domain transfer remains untested here.

Additional independent implementation inspection: GitHub connector read https://github.com/ptnghia-j/ChordMini README and checkpoints directory. Actual files exist: `btc_model_best.pth` 35,942,692 bytes, `2e1d_model_best.pth` 27,523,646 bytes, teacher checkpoint 12,229,576 bytes. README gives single-audio-to-`.lab` invocation; dependencies and code have not been installed/tested. Example inference uses Gaussian kernel 9, 0.5-second minimum segment, overlap voting, and smoothing. These settings need separate recording or ablation in a short-event study; the checkpoint alone does not define the evaluated pipeline. Labelled audio is not distributed. MIT source-code license does not supply dataset rights.

Our assessment: a feasible recent pretrained comparator without reproducing the thousand-hour training recipe. Do not call its lower parameter count proof of lower total cost. Its article does not establish which specific sound perturbations create same-root quality confusions, nor whether our shared switching penalty is calibrated. Teacher-quality dependence motivates comparisons of error *patterns*, not a promise that a deep baseline solves our guitar cases.

## 2. Majchrzak and Mańdziuk, Training chord recognition models on artificially generated audio

Primary publication update: https://link.springer.com/article/10.1007/s00521-026-12069-0 verifies an **Original Article published 30 March 2026**, Neural Computing and Applications 38, article 240. It is inaccurate to describe the work only as a 2025 preprint. Publisher full text was subscription restricted. Actual substantive reading used https://arxiv.org/abs/2508.05878 v1 (7 August 2025), local PDF §§3–6 and Tables 1–4. Journal text changes have not been compared.

- Input: synthetic AAM, real Billboard and Winterreise; BTC uses CQT, HT uses NNLS treble/bass chroma (§3).
- Operations: train/fine-tune on dataset combinations, transpose training examples through twelve roots, six-fold evaluation; paired Winterreise performances stay together (§§3.4,4).
- Output: 25-class major/minor/N sequences.
- Error/guarantees: Root/MajMin WCSR and CCM, fold means/deviations; finite evidence, no transfer guarantee. Adding AAM to Winterreise for BTC changes MajMin 77.02 to 77.15; authors report no significant difference (§5.3, Table3).
- Total cost: audio/CQT/NNLS construction, twelvefold augmentation, 13 training conditions × six folds. Manual NNLS preparation restricted HT to 192/3,000 AAM tracks. A single GPU was used; some full-AAM experiments took up to ten days. GPU model, inference and feature-extraction times remain unknown (§5.4, Table4).
- Failure conditions: synthetic-only BTC performs much worse on Winterreise than AAM; gains depend on architecture and evaluation corpus. AAM supplies only major/minor labels; richer vocabularies are future work (§§5–6).

Our assessment: this directly weakens any proposed novelty claim that “synthetic audio can help chord recognition.” It supports a narrower, feasible study of which controlled changes preserve or destroy a model's chord decision, followed by a real-guitar check. Synthetic chord sequences are useful experimental controls, but their success does not establish real-audio generalization. Important distinction for candidate 2: this study changes training distributions; our intervention would hold individual chord tones fixed while varying a seventh, voicing or third strength. That difference in experimental task is concrete, but does not by itself prove novelty. Candidate 3 still needs care: an internally larger vocabulary tested under the same reduced output task is not equivalent to training on synthetic major/minor songs.

## 3. Viviani et al., MuQ-BTC (MIREX 2026 system submission)

Primary author system abstract: https://futuremirex.com/portal/wp-content/uploads/2026/audio-chord-estimation/MuQ-BTC.pdf . Linked from the MIREX results mirror, snapshot 15 November 2026: https://futuremirex.com/mirex/wiki/2026:Audio_Chord_Estimation_Results . Original wiki link is https://www.music-ir.org/mirex/wiki/2026:Audio_Chord_Estimation_Results . Original direct access failed due to TLS/timeout; official mirror supplies the submission. Saved `docs/research/papers/Viviani_et_al_2026_MuQ_BTC_MIREX.pdf`. Read all three pages, §§2–6 and Tables1–2. Treat as a **MIREX system report**, not a verified peer-reviewed ISMIR research paper; template proceedings footer does not establish peer review.

- Input: music mixes and labelled recordings, including 88-hour SheetSage-Chord.
- Operations: six-stem BS-RoFormer separation; retain bass/guitar/piano/other; frozen MuQ embeddings; enlarged BTC classifier; twelve-root augmentation; five training folds (§§2–4).
- Output: 170 reported classes, no bass/inversions; 25-Hz frame predictions.
- Error/guarantees: WCSR across mir_eval vocabularies, component additions (Table2); empirical only. Separation raises IRRI MajMin 84.79→85.43 but lowers SheetSage-Chord 77.03→76.21.
- Total cost: separation plus foundation-encoder inference, augmentation, feature storage/normalization and BTC training up to 100 epochs. Hardware, latency, memory and upstream pretraining costs are unreported.
- Failure conditions: unsupported inversions are explicit (§2.4). Separation benefit depends on corpus (Table2); no isolated causal explanation is supplied. Song-overlap and clip-group split guarantees cannot be established from the report alone.

Our assessment: important recent context: current feature research includes learned representations and source separation, not only chroma redesign. However, the method is a larger input-processing pipeline; its score cannot identify the contribution of spectral representation alone. A straightforward coursework comparison should not attempt to retrain this entire system. Its Table2 motivates checking *which inputs* a preprocessing step helps or harms, but provides no evidence that removing vocals/drums is appropriate for our solo-guitar audio. Root, quality and segmentation errors remain useful dimensions, not obsolete questions. The report's broad SOTA claim should not be repeated: its own ablation compares selected baselines, and the external MIREX table does not show universal dominance.

## Implications for the six previous candidates

These judgments are our study-design assessment, not claims made by the papers above.

1. **Decoder calibration** remains a necessary diagnostic control. As the sole main research question it risks being too local: a different best penalty does not establish a novel general mechanism. Use it within a comparison of observed error conditions, not as the main reason the project matters.
2. **Seventh-tone interference** remains a clear intervention, but broaden selection only as evidence warrants: seventh strength, third strength and voicing are alternatives, not all mandatory dimensions. Add a recent frozen neural baseline (ChordMini is presently verified as available) to test whether the effect is particular to templates/projection or shared more widely. New precise RQ: *When does adding a seventh change a recognizer's inferred major/minor quality?* Outcome must be conditional on acoustic rendering and recognizer, not a universal claim about seventh chords.
3. **Internal seventh-chord modelling** is a plausible competing explanation experiment, especially once recent methods with extended vocabularies are compared under a common reduced evaluation. Do not infer that extended internal vocabulary causes any advantage without an ablation.
4. **Short events** gains a practical modern comparator because ChordMini's default postprocessing includes smoothing and minimum segment duration. A stronger RQ is *Which short chord changes are lost by the acoustic model, and which by postprocessing?* Need controls for window centering, lookahead and frame rate.
5. **Separate root/quality penalties** remains a candidate modification, contingent on sufficient genuine transitions and independently selected parameters; no extra novelty follows from mentioning modern neural methods.
6. **NNLS versus projection** becomes a classical-method comparison unless tied to an interpretable condition and a current reference method. Full costs must include feature construction and model inference.

Recommended course-scale direction from this subreview: **controlled error analysis across interpretable and pretrained recognizers**, anchored in the existing guitar root/quality anomaly. Keep a narrow primary intervention (e.g. third strength × added seventh), raw-versus-postprocessed results, and a real-audio check. Compare no more than the current baseline/projection pair plus one frozen modern baseline initially. This is feasible because the baseline inference assets are available, not because model execution or domain validity has already been demonstrated. Novelty remains to be checked against targeted intervention/robustness literature before claiming an unstudied phenomenon.
