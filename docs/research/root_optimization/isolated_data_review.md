# Isolated-chord evaluation material

The new check uses all 88 isolated chord recordings in the official ZIP's two `dataset1/* Chords` directories. They form 44 matched fingering, quality and shift groups, each recorded on two electric guitars. These are separate recordings from the previously evaluated dataset-4 acoustic pieces. The task measures transfer to isolated chords.

The selection was saved before audio download and prediction. Each filename gives an E or A fingering, major or minor quality, and a shift from 0 to 10 semitones. The derived triad was checked against every annotated MIDI pitch class. All 88 annotations agreed. The reference spans the earliest note onset through the latest note offset, totalling 202.725 seconds. Leading silence remains unlabelled. All 24 major/minor labels occur; D-sharp and G-sharp have fewer examples than the other roots.

Use one frozen candidate and the existing baseline with their usual decoding. Report duration-weighted major/minor accuracy, root errors, and the two instrument results. The 44 paired groups describe repeated voicings across instruments; the 88 files are not 88 independent musical progressions. No parameters are selected using this material.

## Sources and reading depth

- [Official dataset page](https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html): read the complete dataset description, reference, download and licence sections on 2026-11-09. The licence is CC BY-NC-ND 4.0.
- [Zenodo record](https://zenodo.org/records/7544110): read the description, file information and version metadata. The repository version is 1.0.0, published in 2023; the ZIP is named `IDMT-SMT-GUITAR_V2.zip`.
- Archive guide, `SMT_GUITAR_dataset_description.pdf`, dated 2016-01-20: read §§1.2–1.3, 2.1 and 2.2, printed pages 2–11, using its local text extraction. Section 1.3.1, page 4, describes the isolated chords. Section 2.1, pages 5–7, documents recording sessions, guitars and audio format. Section 2.2.1, pages 8–10, defines the note annotations.
- Read all 88 selected XML files programmatically and inspected examples directly. Only file metadata and note annotations were used in this review; no recognition output was read.

The webpage and Zenodo description reverse the first/second subset order relative to the ZIP directories and attached guide. Paths and guide section numbers identify the material here. The guide states that four independent recording sessions produced the four subsets. It does not establish independence among the 88 isolated chords.

## Task and evidence boundaries

| Item | Verified scope |
| --- | --- |
| Input | Mono 44.1 kHz guitar WAV recordings and XML note pitch/onset/offset annotations. |
| Operations | Local non-commercial evaluation under the linked dataset licence; no audio redistribution is proposed. Recognition uses the existing audio preprocessing and a frozen candidate. |
| Output | Predicted major/minor chord and root over the annotated strum-and-decay span. The reference chord is derived from the documented fingering and checked against the note labels. |
| Error and guarantees | Duration-weighted exact major/minor and root agreement. No numerical annotation-accuracy guarantee was found in the read guide sections. Initial strum notes need not yet contain the full triad, although the full span receives its intended chord label. |
| Cost | 88 XML files and approximately 15.41 MB of compressed WAV members; decoding, resampling, feature extraction and sequence decoding must remain in end-to-end timing. Actual network transfer also includes ZIP range overhead. |
| Failure conditions | Filename/XML pitch-class disagreement, malformed events or out-of-file intervals stop evaluation. A benefit on isolated strums supports that task; it does not measure new progression or full-mixture performance. |

These are data-source and evaluation notes, not a review of the linked DAFx paper. That paper was not read for this addition. Annotation creation details and boundary precision remain unknown from the sections inspected.

## Writing checks

Nature route: manuscript / methods / method + experiments / en / generic. Terms retained consistently: *isolated chord*, *root*, *major/minor*, *annotated span*, and *paired group*. The prose leads with the material and measurement; acquisition logs remain in the manifests.
