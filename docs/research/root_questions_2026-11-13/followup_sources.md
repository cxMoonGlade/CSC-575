# Follow-up source check

13 November 2026. Queries: `chord recognition root chord type transition probabilities temporal model major minor smoothing`; `"Automatic Chord Recognition with Higher-Order" temperature smoothing`. Primary research and the textbook author's implementation were inspected. Search results alone were not used to evaluate other methods.

## Cho, Weiss and Bello (2010)

*Exploring Common Variations in State of the Art Chord Recognition Systems*. [Author PDF](https://ronw.net/pubs/smc2010-chordreco.pdf).

- **Read:** abstract, selected §§2.1–2.4, §§3.1–3.5, §4; Tables 1–4 and Figure 8 discussion. Embedded Figure 3 text is corrupted; its details were not relied on. References not independently audited.
- **Input/operations:** audio, CQT chroma, optional prefilter; binary templates or trained Gaussian/GMM/three-state chord HMMs; Viterbi and alternative transition matrices. Uniform penalties and smoothing lengths are varied.
- **Output:** major/minor/N chord sequences.
- **Error/guarantee:** correct-duration fraction, averaged over 13 Beatles disc folds (180 songs); finite experiments, no recognition guarantee.
- **Total cost:** features, filtering, model fitting per condition/fold, parameter sweeps, emission scores and decoding. Complete timing/hardware unknown.
- **Limits:** §3.3 links model sensitivity to score separation. §4 restricts conclusions to fast fixed-rate features and warns about homogeneous-data overfitting. Reported table optima do not establish independent selection performance. Small gains from complex transitions in this setting do not rule out other structures. The relevant precedent is model-specific smoothing calibration, not proof of our error mechanism.

## Müller, FMP notebook: Experiments—Beatles Collection

[Author-maintained notebook](https://www.audiolabs-erlangen.de/resources/MIR/FMP/C5/C5S3_ChordRec_Beatles.html).

- **Read:** dataset/reduction, song selection, prefiltering interpretation, self-transition section and associated code excerpts; no local execution.
- **Input/operations/output:** four Beatles excerpts, STFT/CQT/IIR chroma, templates/HMM, parameter sweeps → timed major/minor labels.
- **Error/guarantee:** reported F-measure examples; not a population guarantee. Its label reduction differs from our mir_eval policy, so numerical results are not directly comparable.
- **Total cost:** audio/features, smoothing, classification and decoding for each setting; complete measured wall time unknown in inspected material.
- **Limits:** states that smoothing depends on chord-change rate and can remove short chords. Four examples illustrate behaviour; they do not establish our guitar results. Supports a course-level controlled study; the present audit does not newly review the linked 2014 article.

## Existing 2018 source revisited

Korzeniowski and Widmer, EUSIPCO 2018: [proceedings](https://new.eurasip.org/Proceedings/Eusipco/Eusipco2018/papers/1570432212.pdf). Rechecked §§I–II-A and the temperature/smoothing findings; six-field audit remains in [literature_audit.md](literature_audit.md). Training-target smoothing is not the same operation as our inference switching cost. Temperature on neural probabilities is not assumed to be calibrated cosine evidence.

## What changes in our framing

The prior recommendation made separate root/quality time constraints the main question. The new annotation audit places this below a broader representation/decoding question: zero eligible same-root quality changes in development means reduced false switching cannot establish preservation of real quality changes. `rock_6` contains only A7/D7/E7 references, and error increases are concentrated in the additional-tone stratum. This motivates vocabulary-sensitive controls, without diagnosing bad annotations or missing performed thirds.
