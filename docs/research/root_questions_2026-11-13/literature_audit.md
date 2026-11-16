# Source audit, 13 November 2026

Focused search on root/quality errors, representations and temporal decoding. Discovery used web search, arXiv, author PDFs and conference archives; no academic-search MCP was available. This is a targeted review, not an exhaustive ranking. Author statements, finite experimental evidence and project hypotheses are distinguished below. No recognition model was trained in this review.

## 1. Mauch and Dixon, 2010

*Approximate Note Transcription for the Improved Identification of Difficult Chords*, ISMIR, 135–140. [Author PDF](https://webspace.eecs.qmul.ac.uk/s.e.dixon/pub/2010/Mauch-Dixon-ISMIR-2010.pdf).

- **Read:** selected passages in local PDF text, §§1–5, especially §§2.1–2.5, Table 1 and discussion. References not independently audited. PDF hop-size/sample-time inconsistency remains unresolved.
- **Input/operations:** audio → tuned log-frequency spectrum, local standardization, 84-note harmonic dictionary and framewise NNLS; separate bass/general chroma, beat aggregation, DBN.
- **Output:** 121 chord states including N; bass is distinct from chord root.
- **Error/guarantee:** overlap under reduced/full vocabularies. Standardized control 79.0% versus NNLS decay .6 at 80.0% (Table 1). Dictionary full rank supports solution uniqueness, not recognition correctness.
- **Total cost:** resampling, spectral conversion, tuning, standardization, iterative fitting, beat tracking and DBN; complete runtime/hardware unknown.
- **Limits:** no sinusoidal cancellation is an explicit assumption. Shared geometric profiles are a modeling choice. Maj7/N worsen (Fig. 3); discussion offers an unconfirmed harmonics explanation. Our fundamental-only linear-spectrum implementation differs substantially.

## 2. Korzeniowski and Widmer, 2016

*Feature Learning for Chord Recognition: The Deep Chroma Extractor*, ISMIR, 37–43. [Author PDF](https://www.cp.jku.at/research/papers/Korzeniowski_ISMIR_2016.pdf).

- **Read:** selected passages in §§2, 4–7, Table 1 and context/saliency discussion; no code execution.
- **Input/operations:** magnitude STFT → log quarter-tone features; ±0.7-second context → supervised neural pitch-class features; linear chord classifier.
- **Output:** learned 12-D chroma, then major/minor/N labels. Targets derive from chord annotations, not performed-note transcription.
- **Error/guarantee:** majmin duration WCSR, 8-fold validation on 383 recordings; learned features outperform tested hand-crafted features. No chord-accuracy guarantee.
- **Total cost:** feature extraction, context construction, network and classifier training/inference; complete time and hardware unknown. Future context prevents zero-lookahead streaming.
- **Limits:** chroma discards register; 25-class experiments do not establish inversion performance. Post-filtering interaction is future work (§7). Saliency is observational evidence, not a controlled proof of third-note causation. Useful precedent for task-relevant context, not evidence that our errors require neural training.

## 3. Korzeniowski and Widmer, 2018

*Automatic Chord Recognition with Higher-Order Harmonic Language Modelling*, EUSIPCO, 1914–1918. [Proceedings PDF](https://new.eurasip.org/Proceedings/Eusipco/Eusipco2018/papers/1570432212.pdf).

- **Read:** all five pages, §§I–IV, Table I and figure captions; fine graphical coordinates were not extracted from garbled PDF glyphs.
- **Input/operations:** 1.5-second log-spectral CNN evidence; separate N-gram chord-change and negative-binomial duration models; exact flattened-HMM decoding. Temperature and training-target smoothing tested.
- **Output:** timed 24 major/minor chords plus N.
- **Error/guarantee:** duration WCSR on 1,125 songs, four folds; exact inference concerns the chosen model, not ground-truth correctness. Table I: raw 78.51, duration 79.33, 2-gram 79.59, 5-gram 79.88.
- **Total cost:** acoustic training/extraction, language estimation, state construction and decoding. State count grows as K|Y|(|Y|−1)^(N−1); full wall time unknown.
- **Limits:** temperature is not a universal remedy; authors find overconfidence minor here. Simple duration model underestimates long segments (§III-A). Relevant precedent for score/temporal interaction; our cosine scores are not calibrated neural probabilities.

## 4. Poltronieri, Serra and Rocamora, 2025

*From Discord to Harmony: Decomposed Consonance-based Training for Improved Audio Chord Estimation*, ISMIR; [arXiv v1](https://arxiv.org/abs/2509.01588v1).

- **Read:** introduction/related work, §§3–5, Tables 1–3; no repository execution or appendix found in this version.
- **Input/operations:** CQT → Conformer → chord-tone probabilities conditioning root/bass heads; weighted losses, optional consonance smoothing; root argmax and pitch threshold reconstruct labels.
- **Output:** root, bass, pitch classes and Harte chords beyond a fixed output vocabulary.
- **Error/guarantee:** mir_eval, tone overlap and mechanical distances on RWC Pop/USPop after Isophonics/Billboard training. Table 2 shows root improvement need not improve majmin. No recognition guarantee.
- **Total cost:** CQT, transposition augmentation, 20-second overlapping chunks, training, inference and symbolic conversion. Complete runtime/hardware unknown.
- **Limits:** fixed threshold and root commitment are design choices. Aggregate comparisons do not identify mechanisms; consonance metrics do not establish perceptual validation. Our N-excluding root score has a different declared denominator. Direct precedent for the observed metric disagreement, not proof of its cause.

## 5. Akram, Dettori, Colla and Buttazzo, ChordFormer

*ChordFormer: A Conformer-Based Architecture for Large-Vocabulary Audio Chord Recognition*. [arXiv record](https://arxiv.org/abs/2502.11840); local accepted author copy bears [DOI 10.1109/TASLPRO.2025.3646468](https://doi.org/10.1109/TASLPRO.2025.3646468).

- **Read:** accepted-copy §§III-A/B/F, IV-A/B, root-conditioned discussion in V, VII; other architecture/ablation material only searched. arXiv metadata checked separately; versions are not assumed identical.
- **Input/operations:** CQT, Conformer, class-reweighted training; joint root+triad output, separate bass/extensions; CRF/Viterbi vocabulary decoding.
- **Output:** structured large-vocabulary chord sequences. This is not independent root and triad classification.
- **Error/guarantee:** WCSR and component/class analyses; experiments use 1,217 recordings and five folds. No recognition guarantee.
- **Total cost:** preprocessing, augmentation, training, component scores, vocabulary construction and temporal decoding; complete time/hardware unknown in inspected sections.
- **Limits:** authors discuss weaker results when root must also be correct; root-excluded evaluation does not solve root estimation. Reweighting and a fixed transition penalty are design choices, not necessary task restrictions. Useful structural precedent; current review does not establish its CPU cost relative to our system.

## 6. Phan, Jin, Liu and Dong, 2026

*Enhancing Automatic Chord Recognition via Pseudo-Labeling and Knowledge Distillation*, DAFx26; [arXiv v5](https://arxiv.org/abs/2602.19778v5).

- **Read:** selected passages in §§3.1–3.2.5, 4–6 and Tables 1–4, with abstract metadata; some figure layout text illegible, not used.
- **Input/operations:** unlabeled music, pretrained BTC teacher and aligned labels; CQT, pseudo-labeling, student training, then supervised adaptation with selective distillation.
- **Output:** 170-class chord sequences; BTC and 2E1D students.
- **Error/guarantee:** mir_eval, segmentation and class metrics on 120 held-out songs from a 600-song selection. No accuracy guarantee.
- **Total cost:** over 1,000 hours of audio preprocessing and teacher inference, two-stage training, student inference; 3.03M/2.2M parameters. Epoch comparisons are reported; complete wall-time/hardware costs remain unknown.
- **Limits:** authors explicitly identify teacher bias/weak generalization as transferable failures. Teacher-label agreement and ground-truth accuracy differ. Student parameter count alone does not establish end-to-end efficiency. Provides a data-coverage route, with substantially more data preparation than our proposed controlled study.

## Public product disclosures

Chordify, [19 August 2020](https://chordify.net/pages/algorithm-summer-bootcamp/) and [24 August 2021](https://chordify.net/pages/chordify-algorithm-learns/), relevant article bodies read in full. Audio is processed by chord and beat networks; users/editors supply corrections. Outputs are timed chord displays. Public error definitions, guarantees, current architecture and complete costs are unknown. The later post explicitly describes spurious chords on bass-only/vocal-only passages. These posts describe their publication-time system, not a verified 2026 implementation.

## Screening only

Mackenzie, *Chord Recognition with Deep Learning*, arXiv:2512.22621: abstract/metadata only, not used for method evaluation. BACHI, arXiv:2510.06528: discovered as a symbolic-input candidate; not substantively evaluated. The existing ISMIR 2018 duration/language paper was partially reread; the EUSIPCO paper above supplies the directly checked temperature comparison. Chordino code was not newly inspected.

## Interpretive rules

None of these papers establishes that the present root/quality trade-off is unavoidable. Separate bass and root, acoustic pitch presence and harmonic annotation, and residual minimization and label correctness. Existing decompositions provide comparison methods; they do not establish optimality. No first-in-field novelty claim follows from this targeted search.
