# Recent temporal literature audit — 2026-11-15

Candidate numbers in this source audit refer to the previous six-question list. The revised priority order is in [review.md](review.md).

Scope: focused primary-source search for audio chord temporal segmentation, bounded context, short events and score calibration, published 2023–2026 and available by 2026-11-15. This is a targeted update, not an exhaustive systematic review. Queries included `Kim Park Event-Based Chord 2026`, `Yuan Devaney BMACE 2024 2026`, `chord recognition uncertainty calibration segmentation 2024 2025`, `chord recognition temporal smoothing short chords 2024 2025 2026`, and `automatic chord recognition calibration 2023 2024 2025 2026`. Search discovery used web search; substantive conclusions below use authors' papers and official proceedings records. No report files changed.

## 1. Kim and Park — event-level sequence modelling (ICASSP 2026)

Primary record: https://arxiv.org/abs/2604.24386 ; PDF: https://arxiv.org/pdf/2604.24386 . Submitted 27 April 2026; authors' arXiv record explicitly says accepted to ICASSP 2026. Cite as 2026 conference work, noting that the text read is arXiv v1. Local PDF: `docs/research/papers/Kim_Park_2026_Event_Based_Seq2Seq_arxiv_v1.pdf`. Read full methodological and experimental text §§1–4, Tables 1–2, and captions/discussion of Figures 1–4. Figure 3 cells were not independently transcribed.

**Six-field paper audit (source-supported facts).**

- **Input:** Audio, converted to log-CQT; 25.6-second segments, 100-ms hop, six octaves, 24 bins/octave (§3.1). Dataset: 471 pop songs; five folds.
- **Operations:** Autoregressive Transformer encoder–decoder. MERGE tokens encode time and whole chord; SPLIT encodes time/root/quality. Optional encoder pretraining fits embedding similarities to labelled chord-sequence similarity (§§2.1–2.3). Inference masks invalid token types.
- **Output:** Time-aligned segments from 168 chord combinations plus no/unknown chord; time tokens quantized to 100 ms.
- **Errors/guarantees:** WCSR under seven vocabularies plus directional-Hamming-derived under/over/mean segmentation scores (§3.1). Table 2 reports pTE-DS maj/min 86.7 versus BTC 82.3; oversegmentation score 92.9 versus 85.9. These are empirical results, not guarantees.
- **Total cost:** CQT, augmentation, optional pretraining, supervised training and autoregressive decoding. Parameter count, measured training/inference time and hardware were not reported in the read text.
- **Failure conditions:** §3.3 explicitly reports complex chords simplified to frequent qualities, including maj6→maj. Figure 3 conditions quality confusion on correct root. §4 names vocabulary expansion and annotation subjectivity as future work.

**Our interpretation and applicability.** This paper directly rules out presenting event-level modelling, separate root/quality representations, or same-root quality confusion as untouched territory. It does not isolate guitar strumming, delayed thirds, or the current projection/decoder interaction. Five-fold averaged validation evidence does not establish arbitrary-corpus generalization. The protocol calls the held-out fold validation and uses validation-based stopping; an independent final holdout is not described. The 100-ms token grid limits output timing resolution, but does not prove a specific minimum detectable chord duration. No demonstrated end-to-end latency comparison is available. Reimplementing the whole model is unnecessary for this course; retain the methodological lesson to assess both oversegmentation and deletion of true short segments.

## 2. Yuan and Devaney — BMACE (ISMIR 2024 late-breaking/demo; arXiv 2026)

Primary record: https://arxiv.org/abs/2601.02101 ; PDF: https://arxiv.org/pdf/2601.02101 . The 5 January 2026 upload explicitly identifies the work as ISMIR Late-Breaking Demo **2024**. The PDF's venue statement agrees. Do not count it as a new 2026 full conference paper. Local PDF/text: `docs/research/papers/Yuan_Devaney_BMACE_2024_arxiv2026.{pdf,txt}`. Read complete three-page extended abstract including §§1–3, Figure 1 and Table 1.

**Six-field paper audit (source-supported facts).**

- **Input:** USPOP2002 audio with MARL annotations; 10-second windows overlapping by five seconds. Log-CQT at 22,050 Hz, hop 2,048, six octaves, 24 bins/octave; training-statistics normalization (§3.1).
- **Operations:** Bidirectional Mamba blocks, concatenation and fully connected layers; compare two unidirectional arrangements, BTC and CRNN (§2).
- **Output:** Framewise probabilities for 25-label or 170-label vocabularies.
- **Errors/guarantees:** Table 1 gives WCSR, model GFLOPs and parameters. Maj/min BMACE 0.7678, BTC 0.7628, CRNN 0.7796. Authors explicitly caution that small recognition differences are unlikely statistically significant (§3.2); no guarantee.
- **Total cost:** Training/inference include CQT and normalization. Reported model cost: 0.0261 GFLOPs and 114,361 parameters for maj/min, versus BTC 0.6282 and 2,910,361. GPU configuration stated; end-to-end time, memory and preprocessing cost not quantified.
- **Failure conditions:** Evaluation on one corpus; rare labels and annotator disagreement motivated the work (§1). No failure-specific experiment or confidence calibration reported.

**Our interpretation and applicability.** Efficiency is a legitimate recent research axis, but this limited evidence supports model-size/operation reduction, not a proved low-latency or end-to-end advantage. Bidirectional access and ten-second input windows cannot be equated with causal real-time operation. Comparisons are validation results; split details and uncertainty estimates are insufficient for a broad superiority claim. This does not motivate adopting Mamba merely because it is recent. It weakens any claim that our tiny template computation needs an accelerator, while reinforcing the need to report full costs when comparing NNLS and projection.

## 3. Chang and Su — latency-controlled ACR (SMC 2025)

Primary official proceedings record: https://zenodo.org/records/15838757 ; PDF: https://zenodo.org/records/15838757/files/185_SMC25_proceedings_with_concerts.pdf . DOI 10.5281/zenodo.15838757. Conference paper in SMC2025 proceedings, pp.176–182; published 8 July 2025, conference 10–12 July. Downloaded `docs/research/papers/Chang_Su_2025_Latency_Controlled_ACR.pdf` and extracted adjacent `.txt`. Read §§1–5 in full (pp.176–180), model formulas and Tables 1–2; references inspected only as pointers.

**Six-field paper audit (source-supported facts).**

- **Input:** Log-CQT from pop recordings, 93-ms hop; Isophonics, Robbie Williams and USPOP2002; five-fold cross-validation (§§3.3,4.1). Authors manually correct global annotation offsets.
- **Operations:** CNN front end, contextual-block Transformer with limited look-ahead and inherited context; Tonnetz-derived soft training targets (§3).
- **Output:** Per-frame major/minor/no-chord labels, 25 classes.
- **Errors/guarantees:** WCSR root/maj-min plus directional-Hamming segmentation quality. Table 1: CBP-1 maj/min 80.26 versus offline BTC 81.36; reported architecture latency 186 ms. Empirical results; no error guarantee.
- **Total cost:** 7.54M parameters, about 20 training epochs per fold, pitch-shift augmentation (§§4.1–4.2). Latency is explicitly `(current block + look-ahead) × hop` (§4.3), not measured full audio-to-output runtime. CQT/compute latency and hardware timing are not provided.
- **Failure conditions:** Lower context degrades maj/min more than root scores (§4.4, p.180). Authors explain this through early roots and later thirds; they do not experimentally isolate note-arrival order. Vocabulary and data restrict evaluation to pop major/minor recognition.

**Our interpretation and applicability.** This is particularly relevant to our root-versus-quality narrative. An explicit recent mechanistic explanation exists, but its causal test is missing from this paper. It supports investigating note-onset order, not asserting it causes our current `rock_6` failure. Do not reproduce their 186-ms number as system latency. A course adaptation could retain existing STFT/projection methods, vary note-onset asynchrony, and examine which stage delays quality evidence. Mere demonstration that an absent third provides no major/minor evidence is trivial; test persistent error after the third arrives and whether an onset-aware aggregation method improves that error without deleting genuine short changes.

## Consequences for the previous six questions

1. **Decoder calibration:** retain as a necessary experimental control, not the strongest main novelty claim. Recent event-level and block-context models show that temporal structure is being actively redesigned. A λ sweep alone answers only our implementation question.
2. **Adding seventh tones:** remains a plausible controlled mechanism experiment. Kim–Park directly shows complex-to-common quality confusions, but does not test addition of one tone with all else fixed. It cannot validate the current dominant-seventh explanation by itself.
3. **Modelling sevenths then reducing outputs:** already close to the established large-vocabulary/structured-output agenda. Course comparison is valid; broad novelty requires much more evidence than these sources.
4. **Window × decoding effects on short chords:** remains interpretable and affordable if sharpened to where evidence disappears and paired with short-event recall. Recent segment modelling confirms relevance but also prevents claiming segmentation itself is new.
5. **Separate root/quality transition penalties:** Kim–Park's split tokens are a nearby precedent, not the same algorithm. Consider only after identifying actual failure conditions and building real positive transitions. Current lack of same-root transitions still matters.
6. **Joint fitting versus independent projection:** BMACE does not answer this acoustic question. Cost-versus-error conditioning remains a useful course study; do not turn operation counts alone into a superiority claim.

A stronger alternative to propose, if the user wants a mechanism-centered question:

> How does note-onset asynchrony affect root and quality errors in guitar chord recognition?

A method-oriented extension:

> Can onset-aware evidence aggregation reduce quality errors in arpeggiated guitar chords without suppressing genuine chord changes?

Test identical note sets, strengths and decay envelopes with controlled onset order/delay; compare existing front ends and calibrated decoding. Evaluate recognition lag from both intended chord onset and arrival of the quality-defining third; measure false changes and missed changes separately. Use natural GuitarSet excerpts for an external plausibility check, not as a randomized causal experiment. Define incomplete-chord scoring carefully: a third that has not sounded yet may be irrecoverable from current acoustics; persistent mistakes after it appears are more informative. This is an adaptation and a testable candidate, not a verified worldwide research gap.

## Screened leads not substantively included

- BACHI (arXiv:2510.06528, 2025) is explicitly **symbolic** chord recognition. Metadata/abstract only in this branch; no claim it solves audio errors.
- ChordSync (SMC2024 paper205) uses chord-annotation alignment; candidate for separate audit, not yet read here.
- MCCN (ECNCT2026, DOI10.1109/ECNCT70535.2026.11661549) appeared in third-party metadata with “channel calibration.” No primary full text obtained; not evidence of probabilistic score calibration.
- Research on Self-Training in Automatic Chord Recognition (EEI2026, DOI10.1109/EEI70303.2026.11640529) appeared in third-party metadata mentioning confidence thresholding/temporal smoothing. Primary text not checked; pending.
- No directly matching 2023–2026 paper on *calibrating the existing STFT-versus-projection transition penalty* was verified in this focused search. This does not establish absence or novelty.
