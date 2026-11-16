# Recent component and vocabulary research: targeted source audit

Candidate numbers in this source audit refer to the previous six-question list. The revised priority order is in [review.md](review.md).

Checked 2026-11-15. Scope: 2023–2026 audio chord recognition, focusing on root/quality/component models. This note audits two directly relevant papers; it is not a systematic review or a claim of exhaustive coverage. No project report, bibliography, or experimental result was changed.

## 1. Akram et al., ChordFormer

**Publication and version verification.** The journal article is **2026**, IEEE Transactions on Audio, Speech and Language Processing **34:581–595**, DOI **10.1109/TASLPRO.2025.3646468**. Publisher-deposited Crossref metadata confirms these fields (`chordformer_crossref.json` in this directory). The DOI's embedded 2025 is not the journal publication year. The official author repository gives the same journal citation. The IEEE landing page was blocked by a JavaScript check, so the publisher's final formatted PDF was not read. The locally available institutional accepted manuscript is headed December 2025, and explicitly says accepted, author version, not fully edited. The arXiv record has only v1, submitted 17 February 2025. These are **versions of one paper**, not separate studies.

Primary sources:

- Journal DOI: https://doi.org/10.1109/TASLPRO.2025.3646468
- Publisher-deposited metadata: https://api.crossref.org/works/10.1109/TASLPRO.2025.3646468
- Accepted manuscript: https://www.iris.sssup.it/retrieve/485be142-ac71-4f4b-92fe-624d1e8ac756/ChordFormer_A_Conformer-Based_Architecture_for_Large-Vocabulary_Audio_Chord_Recognition.pdf
- Preprint/version record: https://arxiv.org/abs/2502.11840
- Author code/citation: https://github.com/mwaseemrandhawa/ChordFormer

**Reading depth.** Targeted reading of accepted manuscript §§III-A–F, IV-A–D, V-B/C, VI-D/E, VII; inspected Tables I–V and IX, Fig. 4 discussion, with keyword checks for computational costs and failure statements. Compared arXiv v1 Table II/III and decoding equation against accepted version. Not a line-by-line audit of the complete code, all architectural ablations, or final publisher proofs.

| Required field | What the paper actually establishes |
|---|---|
| Input | Audio from 1,217 songs spanning Isophonics, Billboard and MARL; 5 folds, with 60/20/20 train/validation/test proportions per fold. CQT at 22,050 Hz, hop 512, 36 bins/octave across C1–C8 (252 bins); dB conversion and normalization (§IV-A, p.7–8). |
| Allowed operations | Supervised learning from aligned component labels; CQT pitch shifts −5…+6 semitones; four Conformer layers; class-reweighted loss; component activations combined by a linear-chain CRF (§III, IV). A scalar penalty applies to every whole-chord state change, Eq.12. Accepted manuscript explicitly reports trying λ=2…35 and choosing 30 (§III-F, p.7); this is not a new operation for our project. |
| Output task | Six component variables: **root+triad jointly**, bass, seventh, ninth, eleventh, thirteenth. Thus this is not precisely “independent root and quality heads.” Decoding is vocabulary-constrained; large-vocabulary evaluation uses 301 chord labels including N (§III-A, IV-D). |
| Errors and guarantees | mir_eval Root, MajMin, Thirds, Triads, Sevenths, Tetrads, inversion metrics and MIREX; 301-class frame accuracy and macro class accuracy; a root-ignored aggregate ARWCSR. These are finite empirical comparisons, no theorem bounding recognition error or out-of-distribution guarantees. Root-ignored scoring does **not** remove a physical root tone from audio. Fig.4's quality confusion conditions on a correctly predicted root, so this analysis already has a recent precedent. |
| Total cost | Costs include labeled-audio acquisition/alignment, CQT/dB conversion, augmentation, five-fold training and hyperparameter searches, Conformer inference, component recombination, vocabulary-constrained CRF, and scoring. Table I gives architectural sizes (4 layers, 16 heads, 1024 FFN; 100 output activations); §IV-B samples 1,000-frame (~23.2 s) segments, batch 24, AdamW with validation-controlled schedule. **No total training time, inference wall time, hardware, full parameter count, end-to-end scaling or memory measurements were found in the read text.** Therefore neither an efficiency advantage nor RTX5090 reproduction time is established. |
| Failure conditions and limitations | Author-observed class-frequency tradeoff: higher rare-class weights can lower overall frame accuracy; confusion remains among harmonically related qualities and extensions (§V-C, p.11). Table III shows frame/class accuracy 79.08/39.34 without weighting versus 74.16/44.71 at (γ=.7,wmax=20). Author conclusion identifies combined root-and-quality recognition as an improvement direction. Our inference: findings from these pooled popular-music corpora do not establish behavior for isolated guitar, controlled added sevenths, different note balance, or latency-limited streaming. These are untested conditions, not impossibility results. |

**Version-sensitive numbers.** Do not mix arXiv v1's Root 84.69/MajMin 84.09 and no-weighting frame/class 78.77/38.84 with accepted version's Root 84.60/MajMin 84.35 and 79.08/39.34. Accepted Table IX compares structured versus flat 301-class output, with MajMin 84.35 versus 83.32 on that experiment. It does not isolate a seven-tone acoustic intervention or prove that bigger template dictionaries always improve a fixed 25-label task.

**Implication for our candidate questions.** Candidate 1 (decoder calibration) needs a mechanistic or condition-specific comparison beyond tuning λ. Candidate 3 (richer internal representation with reduced evaluation) and root/quality decomposition have close existing methodological precedents. Candidate 5 (separate transition costs) is not identical to this paper's uniform CRF penalty, but cannot be framed as the first use of chord structure or the first temporal model. The useful bounded question is what happens to **the same paired guitar evidence** before and after calibrated decoding, not whether component recognition has been invented.

## 2. Poltronieri, Serra and Rocamora, From Discord to Harmony

**Publication and version verification.** ISMIR **2025**, actual proceedings PDF pp.**492–500**, title **“From Discord to Harmony: Decomposed Consonance-based Training for Improved Audio Chord Estimation.”** arXiv:2509.01588 v1 was submitted 1 September 2025 and gives ISMIR 2025 as journal reference. The ISMIR conference index currently uses a shorter title (“Consonance-Based Smoothing…”) and pages 492–502; the PDF actually linked by that index is nine pages, with printed page numbers 492–500 and the longer title. This is a metadata inconsistency, not evidence for a second study. The actual proceedings PDF and arXiv tables agree for the inspected results.

Primary sources:

- Conference index: https://ismir.net/conferences/ismir-2025/
- Actual proceedings PDF, archived in `docs/research/papers`: https://zenodo.org/record/17706494/files/000057.pdf
- Subsequent proceedings record / DOI: https://doi.org/10.5281/zenodo.17811559
- arXiv metadata: https://arxiv.org/abs/2509.01588
- Official author code: https://github.com/andreamust/consonance-ACE

**Reading depth.** Read proceedings §§3.1, 3.2, 3.2.1, 3.2.2, 4, 4.1, 5 and Tables 1–3; checked title, page numbers and selected methods/results against local arXiv v1. Read related-work context around chord decomposition. Did not independently reproduce the metrics or run the training/decoding code. No supplement was located/read.

| Required field | What the paper actually establishes |
|---|---|
| Input | Two distinct experiments: (a) CASD's multiple symbolic annotations, with a random-sequence control matching its 50 tracks/4 annotations structure and vocabulary/length distributions (§3.1, pp.494–495); (b) audio with Isophonics+Billboard annotations for training/validation and RWC Pop+USPop as test corpora (§4, p.496). The latter uses 22,050 Hz CQT, hop 2048, 144 bins over six octaves from C1 (§3.2). |
| Allowed operations | Supervised Conformer; pitch-class multi-hot chord-tone predictions condition additional root and bass heads; composite cross-entropy/BCE and cardinality loss; perceptually weighted **training-label smoothing**, and symbolic reconstruction from component predictions (§3.2.1–2, pp.495–496). Training uses 20 s excerpts with 50% overlap, transpositions −5…+6, AdamW/cosine schedule, mixed precision and patience 10 (§4, p.497). Label smoothing here is **not temporal smoothing** and should not be cited as proof that a transition penalty works. |
| Output task | Frame-wise root, bass and chord pitch classes, reconstructed into symbolic chord labels without a fixed enumerated chord vocabulary. Root/bass use argmax; chord tones use threshold .5 and intervals relative to predicted root, then Harte shorthand conversion (§3.2.1). Comparisons include a fixed 170-class output and decomposed versions of both their Conformer and BTC. |
| Errors and guarantees | Binary duration-based mir_eval metrics plus Tone-by-Tone similarity and Mechanical/Mechanical-Consonance distances; inverted-chord scores. CASD agreement is compared with random labels; model table reports corpus-level outcomes. No guaranteed accuracy, universal perceptual-validity theorem, or reported statistical uncertainty establishes that every small numerical gap is meaningful. |
| Total cost | Includes obtaining audio and aligned annotations, CQT, overlapping crops, pitch-shift augmentation, repeated baseline and variant training, encoder inference, root/bass/tone decoding, symbolic conversion and multiple metrics. Consonance distances and target construction are additional operations. No training wall time, hardware, parameter count, real-time factor or full end-to-end cost was found in the read paper; “decomposed” does not mean negligible overall cost. |
| Failure conditions and limitations | Authors note small differences in standard vocabulary metrics (§4.1); Table2 shows decomposition alone raises Conformer Root 81.4→83.4 but **MajMin falls 77.5→77.2**; BTC Root 81.6→82.9 but MajMin 77.3→76.0. Their consonance label smoothing changes the Conformer pair to 84.0/77.8. These are empirical table differences, not proof of a causal root/quality tradeoff or a statistically significant reduction. Author-defined consonance vector is grounded in Western tonal harmony; generalization to other harmonic traditions is not shown. Authors explicitly exclude Spectral Pitch Similarity from their study (§3.1). Our inference: thresholds, root errors and pitch-class predictions may affect label reconstruction, but the paper does not isolate which mechanism explains our guitar errors. |

**Most directly useful finding.** This is a recent example in which improving root accuracy does not automatically improve complete major/minor recognition. It strengthens the motivation to inspect error types, while not establishing that our projection-vs-chroma phenomenon has the same cause. Root accuracy and MajMin also have different metric rules; do **not** subtract their percentages and call the difference same-root quality error. Our same-root error duration must continue to be computed on explicitly matched supported intervals.

**Implication for our candidates.** Candidate 3 should acknowledge this direct fixed-vocabulary versus decomposed-output comparison. Candidate 2 (paired addition/removal of seventh tones at controlled third strength), and interaction with a separately calibrated decoder, remains a distinct experiment absent from the sections read. A bounded question could be: **Does seventh-chord content reduce major/minor discrimination before decoding, or does temporal decoding amplify the resulting ambiguity?** The proposed evidence would be paired audio interventions and margins/errors, not a new component model or a universal explanation.

## Consequences for the six earlier candidates

1. **Decoder calibration:** retain as a required baseline/control; a standalone claim of newness is weak given ChordFormer §III-F and older CRF/HMM literature.
2. **Added seventh tones:** comparatively useful controlled question, if note balance and register are explicit factors and real-audio validation is kept distinct. Neither audited paper directly answers it.
3. **Model sevenths before reducing output:** clear existing large-vocabulary/decomposed precedent. Useful baseline or mechanism comparison; smaller template implementation is not by itself a new idea.
4. **Window/decoder short-event interaction:** neither audited paper directly isolates it. This pair cannot establish novelty or exhaustive absence; temporal methods are audited in `temporal.md`.
5. **Separate root/quality penalties:** distinct from uniform whole-label CRF, but structural component modeling already exists. Requires data containing actual same-root quality changes, as already noted in the project.
6. **NNLS versus independent projection:** not directly addressed by these learned models. Could remain a signal-processing project, but this audit does not supply recent direct evidence for it.

Recommendation after these two recent papers: do not discard the project for a larger neural system; tighten its claim to a controlled failure mechanism. Use decoder calibration as a control, and choose **one** principal acoustic or model-vocabulary intervention. A current learned-model checkpoint can be an external comparator if its license, inputs, output mapping, training overlap and runtime are verified; benchmarking a downloaded model does not require retraining every state-of-the-art system.

## Search log and candidate-only exclusions

Queries used through web search: `ChordFormer comprehensive chord recognition conformer bi-directional transformer decoder 2026 3646468`; `"From Discord to Harmony" chord recognition 2025 ISMIR`; `automatic chord recognition root quality component 2024 2025 2026`; `"10.1109/TASLPRO.2025.3646468"`; `"ChordFormer" "2026" pages`; `chord recognition 2024 2025 "contrastive" "noisy"`; `audio chord recognition 2024 2025 "root" "quality" decomposition`.

Additional search leads, **metadata-only, not substantive evaluations here**:

- Murgul et al., *Joint Transcription of Acoustic Guitar Strumming Directions and Chords*, ISMIR2025, https://zenodo.org/records/17811416; audited in `guitar_and_systems.md`.
- Yao et al., *BACHI*, https://arxiv.org/abs/2510.06528. Its stated input is **symbolic music**, so cannot be treated as an audio recognizer replacement without a transcription stage and its cost/errors.
- Chordict's October2026 MIREX system account: https://chordict.com/labs/mirex-2026-audio-chord-estimation. This is an author's system report, not a peer-reviewed paper. Must verify official MIREX tables and splits before using numerical comparisons; audited in `guitar_and_systems.md`.
- Li et al., *Large-Vocabulary Chord Recognition Based on Contrastive Learning and Noisy Student*, DOI10.1109/TCE.2024.3425718. Search metadata suggest online2024/journal2025; **not** yet publisher-verified/full-text-read in this branch, so no method-performance conclusion used.

