# Project resources

## Data

The current experiments use GuitarSet for development and IDMT-SMT-Guitar for external comparisons. Dataset archives remain local. The saved HTML players embed individual recordings with source attribution.

### GuitarSet

[GuitarSet v1.1.0](https://zenodo.org/records/3371780) supplies microphone recordings and chord annotations under CC BY 4.0. The required archives are `audio_mono-mic.zip` (656.9 MB) and `annotation.zip` (39.1 MB). Both contain files directly at their top level; extract them into separate directories as below.

From the repository root, using `curl`, `md5sum` and `unzip`:

```bash
mkdir -p docs/archives docs/datasets/GuitarSet/annotations docs/datasets/GuitarSet/audio_mono-mic
curl --fail --location --retry 4 \
  'https://zenodo.org/records/3371780/files/annotation.zip?download=1' \
  --output docs/archives/annotation.zip
curl --fail --location --retry 4 \
  'https://zenodo.org/records/3371780/files/audio_mono-mic.zip?download=1' \
  --output docs/archives/audio_mono-mic.zip
md5sum --check <<'MD5'
b39b78e63d3446f2e54ddb7a54df9b10  docs/archives/annotation.zip
275966d6610ac34999b58426beb119c3  docs/archives/audio_mono-mic.zip
MD5
```

Check that both MD5 results say `OK`, then extract:

```bash
unzip -n docs/archives/annotation.zip -d docs/datasets/GuitarSet/annotations
unzip -n docs/archives/audio_mono-mic.zip -d docs/datasets/GuitarSet/audio_mono-mic
```

The result is 360 WAV/JAMS pairs. `chordrec prepare` selects accompaniment recordings and excludes `04_BN3-154-E_comp` and `04_Jazz1-200-B_comp` because of [reported annotation timing errors](https://github.com/marl/GuitarSet/issues/5). Progressions 1 and 2 provide 119 development recordings; progression 3 provides 59 previously evaluated test recordings. Chord intervals follow score-derived segmentation.

### IDMT-SMT-Guitar

[IDMT-SMT-Guitar](https://zenodo.org/records/7544110) supplies the 88 isolated chords from `dataset1` and the slow- and fast-tempo progression recordings from `dataset4/acoustic_mic`. The latest comparison uses all 64 fast recordings. The [fast-tempo reproduction guide](research/root_optimization/fast_validation/README.md) gives the archive URL, checksum, extraction and evaluation commands. Its audio and annotations use CC BY-NC-ND 4.0.

### Background resources

The original project materials include [Isophonics chord annotations](https://isophonics.net/content/reference-annotations-beatles); Beatles audio is not needed for the current experiments. Other collected resources are:

- [Chordify CASD](https://github.com/chordify/CASD): multiple expert chord annotations and YouTube reference URLs, without an audio archive.
- [ChoCo](https://github.com/smashub/choco): harmony annotations in JAMS format.
- [Jazz Audio Aligned Harmony Dataset](https://github.com/MTG/JAAH): jazz harmony annotations and precomputed chroma, without original recordings.

## Software and examples

- [librosa chroma example](https://librosa.org/doc/0.11.0/auto_examples/plot_chroma.html): a starting point for feature extraction and plots.
- [mir_eval](https://github.com/mir-evaluation/mir_eval): music information retrieval evaluation routines.
- [Pitch Class CNN](https://github.com/christofw/pitchclass_cnn): reference implementation for learned pitch-class features.
- [Chord recognition system](https://github.com/krist311/chords-recognition): another implementation for background reading.

## Literature

The [project README](../README.md) contains the related work and bibliography. [references.bib](../references.bib) contains the corresponding BibTeX entries for the final report.

## Report template

The report uses the [official ISMIR 2024 LaTeX template](https://github.com/ismir/paper_templates/tree/master/2024/latex). The [four-page PDF](../report/progress_report.pdf) and [build instructions](../report/BUILD.md) are in `report/`. The course requires submission as a single 3–4 page PDF; the remaining project schedule is in the [README](../README.md#remaining-work).
