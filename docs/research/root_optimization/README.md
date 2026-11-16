# Root-error study

The [result summary](../../../results/root_optimization/README.md) compares low-register weighting, note-profile NNLS and direct projection. The [prospective plan](plan.json) records development selection and the new isolated-chord comparison. The November 9 [search tree](arbor/status.txt) ends with the original baseline: both candidates tied its 100% decoded score on isolated chords. A subsequent [frozen fast-tempo comparison](fast_validation/README.md) found a projection gain on new tempo versions of previously evaluated pieces. These are separate comparisons with different reference distributions; their absolute scores should not be compared as one search objective.

The main package includes both note frontends as optional methods. Their code and frozen settings match both the isolated-chord and fast-tempo runs; the original baseline files and configuration are unchanged. [Integration checks](integration_checks.json) and the [independent numeric review](isolated_numeric_review.json) record these facts.

## Isolated-chord data

From the project root, download the [official ZIP](https://zenodo.org/records/7544110) (1,329,918,978 bytes) and extract the 88 WAV/XML pairs. The data use [CC BY-NC-ND 4.0](https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html).

```bash
curl --fail --location --retry 3 'https://zenodo.org/records/7544110/files/IDMT-SMT-GUITAR_V2.zip?download=1' --output /tmp/IDMT-SMT-GUITAR_V2.zip
printf '%s  %s\n' '06796e08731bccffaed6ae59361486e4' '/tmp/IDMT-SMT-GUITAR_V2.zip' | md5sum --check -
chord_data_dir=docs/datasets/IDMT-SMT-Guitar-isolated
mkdir -p "$chord_data_dir"
unzip -n /tmp/IDMT-SMT-GUITAR_V2.zip \
  'IDMT-SMT-GUITAR_V2/dataset1/* Chords/audio/*.wav' \
  'IDMT-SMT-GUITAR_V2/dataset1/* Chords/annotation/*.xml' -d "$chord_data_dir"
cp docs/research/root_optimization/isolated_prospective_selection.json "$chord_data_dir/prospective_selection.json"
cp docs/research/root_optimization/isolated_validation_manifest.json "$chord_data_dir/validation_manifest.json"
```

Continue only if the archive checksum passes. Keep the archive directory structure: `isolated_compare` expects `IDMT-SMT-GUITAR_V2/dataset1/` inside the data directory. Before inference, it checks all 176 source-file SHA256 hashes, references and durations against the saved validation manifest. Existing extracted files are not overwritten by `unzip -n`; a differing file causes validation to fail. This full-ZIP route reproduces the selected files; the original run downloaded selected byte ranges.

## Reproduction

From the project root, prepare a fresh development cache if needed, then run the saved comparisons:

```bash
.venv/bin/python experiments/optimization_v2/common.py --project-root . --work-dir /tmp/chord-dev-repeat --cache-dir /tmp/chord-dev-repeat/cache
.venv/bin/python experiments/root_harmonic/run.py --project-root . --cache-dir /tmp/chord-dev-repeat/cache --output /tmp/chord-nnls-repeat
.venv/bin/python experiments/root_projection/run.py --project-root . --cache-dir /tmp/chord-dev-repeat/cache --output /tmp/chord-projection-repeat
.venv/bin/python -m chordrec.isolated_compare --data-root docs/datasets/IDMT-SMT-Guitar-isolated --baseline configs/frozen.json --candidate configs/note_nnls.json --projection configs/note_projection.json --output /tmp/chord-isolated-repeat
```

Choose unused output paths. Development runs reuse spectra or tuning and do not measure complete inference time. The isolated comparison performs complete inference, but reproducing its fixed result does not create a new held-out test.

The [Git bundle](experiments.bundle) preserves the initial snapshot and all experimental branches, including rejected bass code:

```bash
git clone -b experiment/bass docs/research/root_optimization/experiments.bundle /tmp/chord-root-history
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python /tmp/chord-root-history/experiments/root_optimization/bass/run.py \
  --project-root . --cache-dir /tmp/chord-dev-repeat/cache --output /tmp/chord-bass-repeat
```

Run these commands from this project's root, after preparing the development cache above. The absolute runner path selects the rejected bass implementation; `--project-root .` supplies this project's data, split and cache helpers. Branch `experiment/harmonic` contains the NNLS study, `experiment/projection` the projection control, and `evaluation/isolated` the frozen comparison. The bundle contains code and plans; audio remains in this project's dataset directories.

## Reading and checks

[Mauch–Dixon reading notes](root_harmonic_review.md) record the paper's input, operations, output, error definition, guarantees, total cost and limitations. The [experiment review](../../../experiments/root_harmonic/review.md) distinguishes the simplified implementation from the published system. [Data notes](isolated_data_review.md) describe label construction, archive selection and reading depth. The [integration language audit](integration_language_audit.md) applies the two requested writing skills; report and CLI audits are saved separately here.
