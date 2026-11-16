# Fast-tempo recording check

The complete `dataset4/acoustic_mic/fast` branch is suitable for a fixed comparison on previously unevaluated tempo versions of the same 64 pieces used in the slow-stream comparison. The repertoire is shared. The dataset authors describe the pieces as performed and recorded at two tempi; the inspected documentation does not independently establish the recordings' complete digital-processing history.

## Sources and reading depth

- Local `SMT_GUITAR_dataset_description.pdf`, dated 2016-01-20: read §1.3.4 (printed p. 5), §2.1 (pp. 5–7), and §2.2.2 (pp. 10–11) through the accompanying text extraction. Section 1.3.4 states that each piece was performed at slow and fast tempi. Section 2.1 describes instruments, recording hardware and audio format. Section 2.2.2 defines per-recording beat timestamps, chord symbols and footer metadata.
- [Fraunhofer dataset page](https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html): re-read the dataset-description and licence sections on 2026-11-10 UTC. It describes recordings of each piece at two tempi. This is the authors' description, not a waveform-based verification of independent takes.
- [Zenodo record](https://zenodo.org/records/7544110): re-read the description, file and version metadata. Version 1.0.0 contains `IDMT-SMT-GUITAR_V2.zip`, with published MD5 `06796e08731bccffaed6ae59361486e4`.
- Read all 64 fast and 64 slow chord CSV files and checked their hashes against the original metadata-download manifest. Inspected the archive inventory, without retrieving or opening any fast WAV. Read selected differing chord-symbol sequences directly after the complete metadata comparison.

No paper was substantively evaluated for this addition. The linked DAFx paper was not read as evidence about recording provenance.

## Task audit

| Field | Source evidence and application |
| --- | --- |
| Input | The archive contains 64 fast microphone WAV members with matching chord CSV files. The guide specifies mono 44.1 kHz, 16-bit audio for subset 4. All 64 piece IDs coincide with the earlier slow subset; all filename tempi are higher. WAV headers and actual waveform contents await acquisition. |
| Allowed operations | Apply the three already frozen audio frontends and common decoder to complete recordings. Use the fast files' own annotations, retaining the original NC-to-N convention and unsupported-label exclusions. The official data licence is CC BY-NC-ND 4.0. No tuning, tempo synthesis, relabelling or audio redistribution is proposed. |
| Output task | Predict timed major/minor chord labels and N on new tempo versions within the same repertoire. This comparison addresses performance on these recordings, with root agreement as a secondary metric. It does not introduce a new-song split. |
| Error definition and guarantees | Primary accuracy is correct duration divided by supported reference duration, including mapped N. Root accuracy uses only supported chord-reference duration, counting predicted N as wrong. The read guide provides no quantitative timing-accuracy guarantee and does not define NC. Finite, increasing CSV times alone do not verify their alignment with the audio. |
| Total cost | Selected WAV members occupy 157,586,402 uncompressed bytes and 101,460,782 compressed bytes, before HTTP-range overhead. Measure complete uncached audio reading, resampling, tuning, spectral/profile construction, fitting or projection, decoding and interval construction. Annotation loading, warm-up and scoring remain separately identified. |
| Failure conditions | Stop on missing pairs, changed hashes, invalid timestamps or reference intervals extending past decoded audio duration. Retain the five zero-scoreable recordings in coverage and runtime totals. Shared pieces, ambiguous symbols and unknown annotation precision limit the interpretation; repeated performances and frames are not independent new songs. |

## Metadata findings

All 64 fast CSVs parse under the unchanged adapter. Their first-to-last-beat spans total 1,302.650181408 s: 936.939999995 s of supported chords, 126.845464861 s of mapped N, and 238.864716552 s of unsupported labels. Five files have no supported reference duration: `country_5`, `metal_1`, `metal_2`, `metal_4` and `rock_5`. This metadata observation does not change the complete-stream selection.

There are 691 supported-label changes, including transitions to or from N; 367 are direct changes between supported chord labels, spread across 43 recordings. Fifty-three recordings have at least one supported-label change. All 24 major/minor labels appear.

Forty-seven fast/slow pairs have identical raw symbol sequences; the remaining pairs differ in symbols or repetition endings. For the 34 pairs with identical beat-key sequences, the best affine mapping of slow to fast timestamps leaves maximum residuals between 0.023 and 0.095 s. These observations show that the CSV annotations are not all literal time-scaled copies. They do not prove that the audio was recorded independently. Use each fast CSV's timestamps directly, and check WAV duration containment after acquisition.

## Wording and pending checks

Preferred scope: “a frozen comparison on the fast-tempo versions of the same 64 pieces.” Attribute the two-tempo performance description to the dataset documentation. Independent recording-process verification, subjective alignment inspection and the exact treatment of NC remain unknown. The already frozen selection does not depend on eventual audio predictions.

Writing guidance reused: academic-language-audit and nature-writing, with manuscript / methods / method + experiments / en / generic. Source evidence, author statements, metadata measurements and the reviewer's inference are kept separate.
