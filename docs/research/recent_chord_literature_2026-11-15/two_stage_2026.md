# Ding et al., ISMIR 2026: two-stage audio chord recognition

Candidate numbers in this source audit refer to the previous six-question list. The revised priority order is in [review.md](review.md).

Audited 2026-11-15. This is directly relevant recent research, not a survey. The paper was found through Christof Weiß's institutional publications page, then retrieved from the official ISMIR 2026 programme. No new experiment was run for this literature review.

## Identity, date and actual reading

**Yiwei Ding, Yannik Venohr, Sebastian Strahl, Meinard Müller and Christof Weiß. “Revisiting Two-Stage Audio Chord Recognition in the Deep-Learning Era: Leveraging Multi-Pitch Estimation and Symbolic Pretraining.” Proceedings of the 27th ISMIR Conference, 2026, pp.552–560.**

The official programme marks it presented remotely as P7-5. The conference occurred **8–12 November 2026**, before the review cutoff of 15 November. The linked camera-ready PDF has nine pages with printed proceedings numbers 552–560. No DOI was found in this check, so none is invented.

- Official paper/programme and authors' post-review update: https://ismir2026program.ismir.net/poster_266.html
- Official linked PDF: https://drive.google.com/file/d/1ROT53YqkYdCGWM8uKe_rMFWe0RadHj--/view
- Local retrieved PDF: `docs/research/papers/Ding_et_al_2026_Two_Stage_ACR_ISMIR.pdf`
- Official conference dates: https://ismir2026.ismir.net/
- Institutional author record: https://www.caidas.uni-wuerzburg.de/ch/team/christof-weiss/
- Author code named in paper: https://github.com/suncerock/two-stage-acr

**Reading depth:** read camera-ready Introduction, §§2.1–2.3, §§3.1–3.4 and §4, including Tables 1–4 and footnotes 3,5,6. Read the official programme's author post-review update, and consulted the meta-review to distinguish external criticism from authors' conclusions. No training/code execution, checkpoint audit or independent replication. References were used to locate context, not all individually read.

## Six-field audit

| Field | Verified account |
|---|---|
| Input | Real audio is transformed into harmonic CQT (HCQT), then ClassicPitch predicts frame-wise pitch-presence probabilities. MPE pretraining uses **17 transcription datasets, 152 h**, including **GuitarSet**, GAPS, MAESTRO, MusicNet and ensembles (Table1, §3.1). Symbolic chord pretraining uses DCML: after excluding two Beethoven corpora overlapping the later chord data, **12 corpora, 392 movements, 46,264 measures**. Fine-tuning/evaluation classical audio comprises SWD/BPSD/BSQD, **126 movements and 114 h** with multiple performances; separate pop experiments use Isophonics and Billboard. |
| Allowed operations | Supervised independent pretraining of MPE and symbolic chord recognition; soft MPE outputs downsampled to **10 Hz**; a CRNN or four-layer Conformer predicts structured chord information. Backend-only fine-tuning freezes/caches MPE; optional joint fine-tuning unfreezes both. Comparisons include end-to-end training from scratch, pretrained/fine-tuned combinations, ClassicPitch versus BasicPitch, binarized versus continuous intermediate representations, and score-derived “oracle” pitches (§§2–3). Joint training also lowers HCQT temporal resolution to10Hz for tractability (§2.3), so it changes more than gradient flow. |
| Output task | Time-varying chord labels, with internal root, bass and constituent pitch-class predictions. CRNN additionally has a learned label head, but the reported comparisons decode its structured outputs by the same style of symbolic rule used for the Conformer (§3.1 footnote5). The task is richer than the project's major/minor/N vocabulary. **No-chord frames are masked in training and evaluation**; results do not validate silence/no-chord recognition. |
| Error definition and guarantees | Duration-weighted mir_eval **MajMin and Tetrads WCSR**, plus average precision of predicted constituent pitch-class activities (**PC/AP**, threshold-independent); five-fold evaluation. No theoretical recognition/generalization guarantee, no proven universal upper bound. Score-derived input is called an “upper bound” by authors, but operationally it is an oracle-input result for the tested backend/configuration; it is not a bound over all possible chord systems. No separate root accuracy or same-root major/minor error analysis was found in the tables. |
| Total cost | Audio/score alignment and transcription labels; HCQT; 60,000 MPE pretraining steps, batch128 of~2.3s; 50 symbolic pretraining epochs, batch64 of8measures; 30 audio fine-tuning epochs, batch64 of10s; folds, additional configurations, frontend inference, downsampling/caching, backend prediction and label decoding all contribute (§3.1). Authors report ClassicPitch has **44× the CRNN FLOPs** and unfreezing it slows training **6×**, with little extra improvement (§3.2,p556). Caching removes repeated frontend work during backend fine-tuning but not its acquisition or final inference cost. Absolute training wall time, hardware, end-to-end inference speed and memory were not found in the read paper. |
| Failures and limitations | Author-observed distribution mismatch: binary symbolic pitches versus imperfect continuous MPE, and musical-time score frames versus physical-time audio (§2.3). Unadapted BasicPitch representations sharply reduce scores; backend fine-tuning recovers much of that gap (§3.3). Classical-only training transfers imperfectly to pop (§3.4). Authors explicitly note possible annotation-style specificity (§3.2), omit N, and acknowledge no comparison against off-the-shelf published ACR systems in post-review update. Effects of training data availability and architectural decomposition are not fully separated (meta-review; supported by dataset/training design), so the result does not establish intrinsic superiority at equal data/cost. |

## Results that materially change our project framing

**1. Acoustic representation quality is not the whole chord-recognition problem.** In Table3 (aggregate of the three classical sets), the fine-tuned CRNN backend with ClassicPitch gets MajMin/Tetrads/PC-AP **80.85/69.91/92.92**. Replacing its input with score-derived pitches yields **81.88/71.07/93.21**. Tetrads increases only **1.16 percentage points** under this particular comparison. The authors infer a stronger harmonic-modeling bottleneck than acoustic bottleneck in their setting (§3.3,p557). Our appropriate inference is narrower: it motivates stage-specific error attribution; it does **not** show that our projection frontend is adequate, or that every audio chord system should stop improving pitch estimation.

**2. Representation distribution and backend adaptation have large effects.** With two pretrained stages simply concatenated, changing ClassicPitch to BasicPitch drops Tetrads **64.15→34.98**. With backend fine-tuning, the corresponding gap is **69.91→65.17**. These are results under different training conditions, not a calibrated causal estimate that all lost accuracy is due to score scale. Authors suggest BasicPitch's softer output contributes to the mismatch. This is a contemporary precedent for testing whether a backend calibrated for one representation interprets another representation fairly.

**3. Soft evidence can help, but this is a small measured effect here.** Binarizing ClassicPitch predictions changes fine-tuned Tetrads **69.91→69.59**, MajMin **80.85→80.61**, PC/AP **92.92→92.78** (Table3). The paper's interpretation is that probabilities retain useful information. It does not establish that arbitrary score rescaling improves a template matcher, or that thresholding is always harmful.

**4. Richer features or jointly trained models need not win.** Footnote6 reports that their direct chord model overfit when given HCQT instead of CQT. Joint fine-tuning offers little further benefit with substantially higher training cost, and removes the guarantee that the intermediate variables remain semantically interpretable (§3.2). “Not guaranteed” here describes missing supervision/constraints, not proof that representations actually became meaningless.

**5. Important project overlap if reusing a checkpoint.** GuitarSet belongs to MPE pretraining. Using the released frontend on our GuitarSet examples could therefore yield a trained-on input-domain comparison; it must not be advertised as an untouched held-out benchmark. IDMT is not listed in Table1, but absence from that list alone is not a complete checkpoint contamination audit. Verify actual training manifests before making independence claims.

## Direct relevance to the proposed research questions

This paper makes the earlier emphasis on old chroma/HMM reviews inadequate for positioning our project. Two-stage recognition and separating audio evidence from harmonic interpretation are **active 2026 research directions**. The literature motivation should connect the project to these current studies while preserving the project's smaller experimental scale.

- **Candidate1 (calibration):** Keep as a necessary control. Ding et al. already show large frontend/backend adaptation effects. Simply retuning our penalty would be a much smaller version of an established issue; the interesting part is explaining *which error patterns remain* after adaptation.
- **Candidate2 (seventh-tone intervention):** Remains useful as a focused causal test not performed here. A manageable study can hold the root/third/fifth constant, vary seventh and third strengths, then inspect acoustic evidence, raw template competition and decoded labels. The new paper supplies the stage-attribution motivation, while not answering this specific mechanism.
- **Candidate3 (modeling sevenths internally):** Becomes a natural alternative explanation/control, because better pitch evidence can leave harmonic-model errors. Existing rich-label models mean template vocabulary expansion is not a new principle.
- **Candidate6 (NNLS versus projection):** Broad method ranking is less valuable than measuring which pitch-estimation differences actually matter for root and quality. A near-oracle experiment using known synthetic pitch activations can separate frontend errors from downstream chord interpretation, analogous to Ding et al.'s score-input experiment, but in our guitar/major-minor task.

**A sharper umbrella question worth considering:**

> Which pitch-estimation errors cause same-root major/minor errors in a two-stage guitar chord recognizer?

For a four-page course report, narrow this further to one controllable mechanism:

> Does added seventh-tone energy change major/minor evidence before decoding, or are the errors introduced by chord modeling and temporal decoding?

The study would compare the same audio and intermediate activations at each stage, including a known-pitch control, and report both persistent and new errors after calibrated decoding. This is a research question about failure conditions, rather than a claim that two-stage architectures, components, calibration or richer dictionaries are new. No assertion of field-wide originality follows from reading this paper alone.

## Author limitations versus review comments

The official programme includes an author statement that a **MajMin evaluation bug was corrected in the camera-ready version**. Use the downloaded camera-ready tables, not figures quoted from earlier review text. The author update acknowledges absent off-the-shelf comparisons, notes training-data overlap complicates comparison with popular-music checkpoints, and proposes independent RWC-Pop evaluation as future work. It also promises a checkpoint predicting N, but the paper's reported results continue to mask N; availability and behavior of such a checkpoint were not checked here.

The meta-review's concern that pretraining-data and architectural effects remain entangled is an external review assessment, not an authors' theorem or a demonstrated methodological impossibility. The experiments do support comparisons of the actual trained systems. They do not establish same-data, same-cost dominance over contemporary recognizers.

## Search/retrieval trail

Queries: `"Revisiting Two-Stage Audio Chord Recognition"`; `"Yiwei Ding" "Symbolic Pretraining" chord`. Author publication listing and official programme matched all five authors. Programme Paper iframe points to Drive id `1ROT53YqkYdCGWM8uKe_rMFWe0RadHj--`; downloaded public PDF via `https://drive.google.com/uc?export=download&id=1ROT53YqkYdCGWM8uKe_rMFWe0RadHj--`. PDF extraction and printed page numbers verified. DOI unknown.
