# Overview citation check — 14 November 2026

The report's Introduction and README's Related Work describe spectral features, chord models and temporal context. Three verified reviews support this continuous overview. Specific algorithm descriptions and this project's results retain their own sources; the three-review rule is not applied to individual experimental statements. This is a targeted support check, not a new systematic review or a full re-reading of the other references.

## McVicar et al. (2014)

*Automatic Chord Estimation from Audio: A Review of the State of the Art*. [DOI](https://doi.org/10.1109/TASLP.2013.2294580). Existing local PDF: `docs/papers/McVicar_et_al_2014_Automatic_Chord_Estimation_from_Audio_A_Review.pdf`.

Read for the November 14 review: abstract and Introduction (p. 556), template/HMM discussion (pp. 560–562), higher-order/discriminative models (p. 563), evaluation (pp. 566–567), and conclusion excerpt (p. 572). Other sections were not newly read in full. The abstract and Introduction explicitly organize the review around features, modelling, training and evaluation; pp. 561–562 explain templates and temporal modelling.

- **Input:** recorded music and optional training annotations, depending on the reviewed method.
- **Operations:** chroma extraction, template comparison, probabilistic chord models and temporal decoding. The review does not prescribe a single access model.
- **Output:** frame or interval chord labels from a chosen vocabulary.
- **Error and guarantees:** §§V-B–D distinguish label comparisons, correct overlap and song/corpus averaging. Reviewed finite benchmark results do not establish a guarantee for our recognizer.
- **Total cost:** preprocessing, feature extraction, optional training, scoring and decoding depend on the method. §III-E discusses high memory cost for higher-order models; no common end-to-end cost was established in the inspected passages.
- **Failure conditions:** p. 566 explicitly discusses overfitting in both expert and data-driven systems, including tuning informed by test errors; pp. 566–567 discuss vocabulary-dependent evaluation and annotation disagreement. These are reported issues, not impossibility results.

## Pauwels et al. (2019)

*20 Years of Automatic Chord Recognition from Audio*. [DOI](https://doi.org/10.5281/zenodo.3527739). Existing local PDF: `docs/papers/Pauwels_et_al_2019_20_Years_of_Automatic_Chord_Recognition_from_Audio.pdf`.

Read for the November 14 review: abstract/Introduction, feature and template passages (§§1–3), temporal-context passages (§§4–5), vocabulary and conclusion (§§8–9); other sections were not newly read in full. The Introduction (p. 54) explicitly connects features, chord models and temporal/musical context. §§2–5 provide the support for the report's overview.

- **Input:** music audio; annotations or expert knowledge vary across reviewed systems.
- **Operations:** spectral/chroma construction, template or learned chord models, duration smoothing and harmonic-context modelling.
- **Output:** chord sequences; vocabularies and component targets vary by system.
- **Error and guarantees:** §8 discusses duration-based accuracy and how class imbalance can conceal errors on rarer chords. No recognition or cross-dataset guarantee is inferred from this review.
- **Total cost:** representation, training where used, and decoding costs are system-dependent. §4 notes the lower processing rate of beat-synchronous methods; a comparable total-cost study was not established in the read passages.
- **Failure conditions:** §§4–5 discuss beat-estimation dependence and limited temporal context; §8 discusses overlapping chord categories, imbalance and dataset representativeness; §9 warns that findings may not transfer across integrated architectures. These are the authors' scope cautions, not proof against alternative designs.

## Müller (2021)

*An Educational Guide through the FMP Notebooks for Teaching and Learning Fundamentals of Music Processing*. Signals 2(2), 245–285. [Publisher](https://www.mdpi.com/2624-6120/2/2/18), [author PDF](https://www.audiolabs-erlangen.de/resources/MIR/FMP/data/C0/2021_Mueller_FMP_Signals.pdf), DOI 10.3390/signals2020018.

Verified the publisher's **Review** classification and bibliographic metadata. A parallel source check read all of §4.5 (pp. 263–267) and the conclusion's scope statements (pp. 280–281); the remaining sections were not read in full and notebooks were not executed. This is a broader MIR educational review with a substantial chord-recognition section, not a third dedicated history of ACR. It supports the pipeline description directly: p. 265 covers chroma and templates; p. 266 covers HMM/Viterbi smoothing.

- **Input:** audio and reference annotations; the illustrated study uses four Beatles songs.
- **Operations:** STFT/CQT/IIR chroma, templates, pre-smoothing and HMM/Viterbi decoding with varied self-transition probabilities.
- **Output:** major/minor frame labels and timed segments.
- **Error and guarantees:** precision, recall and F-measure in illustrative finite experiments; no generalization guarantee.
- **Total cost:** annotation conversion, feature precomputation/storage and parameter sweeps are described; complete runtime and complexity are unknown from the inspected sections.
- **Failure conditions:** vocabulary reduction, class imbalance, annotation ambiguity and absent no-chord modelling; numerical underflow in multiplicative Viterbi is addressed by a log-domain implementation.

These sources support the pipeline overview, not an explanation of the observed guitar errors. No additional suitable fourth or fifth review was verified in this targeted search. Crayencour and Cella (2019) was excluded from the count because its publisher classifies it as Methods.
