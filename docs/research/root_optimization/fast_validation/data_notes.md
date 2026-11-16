# Fast-tempo validation data

The selection contains all 64 WAV files under `dataset4/acoustic_mic/fast`, with their matching fast-tempo chord CSVs. It uses the same 64 piece identifiers as the earlier slow-stream comparison. The intended comparison tests transfer between tempo performances within this repertoire.

The selection and acquisition plans were written before audio download. Selection used archive paths only; no recording was removed for unsupported labels, annotation coverage or recognizer results. All 64 annotations were copied from the previously downloaded metadata after their size, ZIP CRC32 and SHA256 were checked. Audio acquisition uses two workers, checked HTTP byte ranges, ZIP member CRC32 and per-file SHA256. A partial `.wav.part` file becomes a final WAV only after validation.

Reference parsing uses the existing `chordrec.idmt.load_chords` implementation without changes. NC remains mapped to N; ambiguous symbols remain X. Labels span the first through last annotated beat, without filling the initial control signal or trailing audio. The final manifest checks finite, increasing intervals against each WAV's duration and retains recordings with no scoreable chord intervals.

The archive is retrieved by selected byte ranges. The published full-archive checksum is not verified. This acquisition reads archive metadata, WAV headers and chord CSVs; it does not run recognition or assess annotation accuracy by listening. The dataset-guide interpretation is documented in the parent task's source preflight.

Files: `prospective_selection.json` fixes the audio paths; `metadata_sources.json` records copied annotations; `audio_sources.json` records member verification and transfer counts; `validation_manifest.json` binds audio and annotations to parsed references. All four are under `docs/datasets/IDMT-SMT-Guitar-fast/`. The parent evaluation plan remains `/tmp/chordrec_root_fast/plan.json`.

Source archive: https://zenodo.org/records/7544110/files/IDMT-SMT-GUITAR_V2.zip?download=1
Dataset page: https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html
License: CC BY-NC-ND 4.0. Audio and annotation files are copied unchanged.

Acquisition completed with 64 checked WAV files, totalling 1,786.16 seconds (29.77 minutes). Supported chord and N labels cover 59.56% of the audio. Five pieces have no scoreable intervals and remain in the manifest: country_5, metal_1, metal_2, metal_4 and rock_5. The transfer used 105,655,086 HTTP-range bytes and required no retry. A separate verification pass re-read every saved WAV and annotation, checked CRC/SHA values, and confirmed all parsed intervals lie within their audio duration. No predictions were generated.
