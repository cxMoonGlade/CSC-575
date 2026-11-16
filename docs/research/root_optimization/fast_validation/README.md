# Reproduce the fast-tempo comparison

This comparison uses all 64 recordings in IDMT-SMT-Guitar's `dataset4/acoustic_mic/fast` stream and their matching chord CSVs. They share the 64 piece identifiers of the earlier slow-tempo comparison. The frozen selection includes all recordings, including five with no scoreable intervals.

The [official archive](https://zenodo.org/records/7544110/files/IDMT-SMT-GUITAR_V2.zip?download=1) contains 1,329,918,978 bytes. Its published MD5 is `06796e08731bccffaed6ae59361486e4`. Audio and annotations use [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/); retain the source files unchanged. See the [dataset page](https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html).

Run these commands from the repository root. Downloading the complete archive avoids dependence on the original session's range cache:

```bash
curl --fail --location --retry 4 \
  'https://zenodo.org/records/7544110/files/IDMT-SMT-GUITAR_V2.zip?download=1' \
  --output IDMT-SMT-GUITAR_V2.zip
md5sum --check <<'MD5'
06796e08731bccffaed6ae59361486e4  IDMT-SMT-GUITAR_V2.zip
MD5
```

The following extracts exactly 64 WAV files and 64 matching chord CSVs across all genre directories. It checks each file against the saved manifest and restores the selection files required by the comparison runner:

```bash
.venv/bin/python - <<'PY'
from pathlib import Path, PurePosixPath
import hashlib, json, shutil, stat, zipfile
saved = Path('results/root_optimization/fast')
data_root = Path('docs/datasets/IDMT-SMT-Guitar-fast')
selection = json.loads((saved / 'selection.json').read_text())
validation = json.loads((saved / 'input_validation.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha((saved / 'selection.json').read_bytes()) == validation['source_selection_sha256']
assert len(selection['recordings']) == len(validation['recordings']) == 64
prefix = 'IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/fast/'
expected = {r[k]: r[k + '_sha256'] for r in validation['recordings'] for k in ('audio', 'annotation')}
assert len(expected) == 128
with zipfile.ZipFile('IDMT-SMT-GUITAR_V2.zip') as archive:
    actual_audio = {n for n in archive.namelist() if n.startswith(prefix) and n.endswith('.wav')}
    assert actual_audio == {r['archive_path'] for r in selection['recordings']}
    assert len(actual_audio) == 64
    for name, fingerprint in expected.items():
        path = PurePosixPath(name)
        assert name.startswith(prefix) and not path.is_absolute() and '..' not in path.parts
        assert not stat.S_ISLNK(archive.getinfo(name).external_attr >> 16)
        payload = archive.read(name)  # ZIP also checks the member CRC32.
        assert sha(payload) == fingerprint
        target = data_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == payload
        else:
            target.write_bytes(payload)
for source, target in [('selection.json', 'prospective_selection.json'),
                       ('input_validation.json', 'validation_manifest.json'),
                       ('previous_selection.json', 'previous_selection.json')]:
    destination = data_root / target
    if destination.exists():
        assert destination.read_bytes() == (saved / source).read_bytes()
    else:
        shutil.copyfile(saved / source, destination)
print('Restored 64 WAV files, 64 chord CSVs and the frozen manifests.')
PY
```

Repeat the fixed comparison with a new output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
.venv/bin/python experiments/root_validation/compare.py \
  --project-root . \
  --plan results/root_optimization/fast/evaluation_plan.json \
  --data-root docs/datasets/IDMT-SMT-Guitar-fast \
  --baseline configs/frozen.json \
  --projection configs/note_projection.json \
  --nnls configs/note_nnls.json \
  --previous-selection docs/datasets/IDMT-SMT-Guitar-fast/previous_selection.json \
  --output results/fast_repeat --run
```

The original `acquire_fast.py` is retained as a session snapshot under `docs/research/root_optimization/fast_validation/`. It contains absolute local paths and requires the cached ZIP directory; use the full-archive route above on a new machine. The original acquisition verified selected members and their SHA256 values, without downloading or verifying the complete archive.

The acquisition and review scripts in this research directory preserve their original session paths. Use the commands above to reproduce the comparison on another machine.
