# Guitar-specific research and a current system submission

Checked 15 November 2026. These records distinguish the actual task and evaluation from general audio chord recognition. The two PDFs were read directly; neither implementation was run.

## Murgul, Schimper and Heizmann — ISMIR 2025

*Joint Transcription of Acoustic Guitar Strumming Directions and Chords*, pp.477–483. [Official proceedings record](https://zenodo.org/records/17811416); [PDF](https://zenodo.org/records/17811416/files/000055.pdf). The conference was in September 2025; subsequent repository creation/modification dates do not change the publication year.

Reading depth: full main text §§1–6, including data construction, architecture, evaluation protocol and Tables 1–6; references used only as pointers. The text says 229 input frequency bins in §4.1 while Figure 4 labels 512; this inconsistency requires code inspection for reproduction.

| Field | Verified account |
| --- | --- |
| Input | Microphone audio at inference. Training data include 90 minutes of recordings from three guitarists and four hours of synthetic strumming. Pickup audio and hand-motion sensors assist annotation; these are not required inputs to the microphone recognizer. |
| Allowed operations | Semi-automatic annotation with manual correction; guitar tablature synthesis and virtual-instrument rendering; pitch shifting and acoustic effects; log-Mel features; convolutional and bidirectional recurrent networks for onset/direction and chord prediction (§§2–4). |
| Output | Up/down strumming events and 24 major/minor chord labels. Chord evaluation samples predictions at **reference strumming times**, not automatically recovered chord segments (§5.4). |
| Error and guarantee | Event precision/recall/F1 with 50-ms tolerance, plus event-sampled chord accuracy. Table 6 reports 90.06% for combined training and 89.21% for BTC. These are finite empirical results; no statistical significance or general error guarantee is established for that difference. They cannot be compared directly with our duration-weighted sequence scores. |
| Total cost | Sensors, recording, manual correction, virtual-instrument rendering/augmentation, 10-s overlapping crops, log-Mel extraction, 20,000 training steps and inference. §4.3 reports about two hours on a Tesla V100, batch six. Data preparation and full inference time are unreported. Commercial rendering tools are part of the original synthesis recipe. |
| Failure conditions | Authors identify muted strums and seventh/suspended chords as extensions (§6). Evaluation uses three guitarists, with two training and one testing in §5.1. Event-time chord evaluation does not test boundary recovery. Synthetic-only training is less effective for direction classification than combining real data (§5.2). |

Implication for our study: guitar-specific joint models and controlled strum synthesis have recent precedent. The paper does not isolate third-arrival timing or the effect of adding a seventh at fixed triad strength. A new onset experiment should target recognition after quality evidence becomes available, rather than repeat event detection or claim that missing evidence can always be recovered.

## Vardar — SLASH, MIREX 2026 system description

*SLASH: Audio Chord Estimation with Harmonic Features and Structured Decoding*. [Author-hosted submission PDF](https://chordict.com/labs/slash-mirex-2026.pdf), linked from the [author's October 2026 results account](https://chordict.com/labs/mirex-2026-audio-chord-estimation). This is a challenge system description, not established here as a peer-reviewed research paper. The official MIREX wiki could not be retrieved reliably in this branch; no claimed external ranking is used.

Reading depth: all main text §§1–7, Tables 1–2 and Figure 1; reference list inspected for source attribution. This record uses the submitted system description, not the author's blog as evidence for comparative performance.

| Field | Verified account |
| --- | --- |
| Input | Mono audio at 22,050 Hz; three harmonic CQT channels, 144 bins each and 92.88-ms hop (§3.1). Training uses 728 recordings/47.11 hours (§4, Table 1). |
| Allowed operations | Six Conformer blocks and ten component heads; weighted focal training loss; global key prior; Viterbi base-chord decoding; thresholded extensions/bass and short-run cleanup (§3). The system uses the complete recording and operates offline. |
| Output | Harte chord intervals with selected extensions and bass. Thirteenth targets are trained but never emitted. The evaluator workaround maps thirdless power chords to sus4 (§6); this affects emitted labels even if the selected metrics treat both as mismatches. |
| Error and guarantee | Local duration-weighted mir_eval metrics and local runs of MIREX evaluation code. §5 explicitly calls Table 2 post-selection results. No universal recognition or deployment guarantee follows. |
| Total cost | HCQT, augmentation, 12.61M-parameter model, 50 epochs/187,850 optimizer steps, overlapping-window inference, global key scoring and structured decoding. §6 reports a 15-recording check taking 3.7% of audio duration on an RTX 3050 Laptop GPU, including per-file startup. The feature-preparation share and total training wall time are not separately stated; the ratio is not a streaming-latency measurement. |
| Failure conditions | Authors disclose inherited decoder constants from an earlier system that had seen most nominal held-out recordings (§4), and selection between two trained variants using scored sets (§5). Adding Billboard training data improves Western-pop sets but not the J-pop set. Same-corpus/partly same-artist evaluation does not establish other-genre transfer (§7). |

Implication for our study: structured output, key priors and minimum-duration cleanup remain active system choices in 2026. Their presence does not establish which stage causes our observed errors. It also demonstrates why a downloaded model comparison must include its decoding and preprocessing, and why development overlap matters even when model weights were not trained on a test recording.

## Additional screening

- IEEE *Real-Time Guitar Chord Recognition via FPGA-accelerated Wavelet Analysis*, DOI 10.1109/ICCC71363.2026.11593367: publisher metadata/abstract only; no six-field performance comparison performed.
- IEEE *Automatic Chord Recognition Using CNN-LSTM Based on Mel Spectrogram*, DOI 10.1109/IncoSST69426.2026.11709510: metadata/abstract only. Isolated segment classification does not establish continuous segmentation performance.
- *Towards Interpreting and Improving the Latent Space for Musical Chord Recognition*: repository metadata appeared recent, but first publication is ICMC 2022. Not counted as a new 2026 study.
- BACHI, arXiv:2510.06528: symbolic input; not treated as an audio recognizer without an additional transcription stage.
- *Large-Vocabulary Chord Recognition Based on Contrastive Learning and Noisy Student*, DOI 10.1109/TCE.2024.3425718: candidate identified through metadata; full text and exact publisher version pending, so it does not support substantive conclusions here.

Searches also included `audio chord recognition seventh interference`, `chord recognition third onset guitar`, `chord recognition asynchrony`, and `ISMIR 2026 chord recognition`. Absence of an exact match in these searches is not evidence of an unstudied problem.
