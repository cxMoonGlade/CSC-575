# IDMT dataset reading notes

This is the metadata review for the earlier slow-tempo fusion comparison. The current report's fast-tempo comparison uses the same dataset; its selection and reproduction details are in the [fast-set notes](../docs/research/root_optimization/fast_validation/README.md).

The added reference is the dataset record, not the linked DAFx paper. Read sources: [official dataset page](https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html), [Zenodo version 1.0.0](https://zenodo.org/records/7544110), and the supplied description's sections 1.3.4 and 2.2.2 (printed pages 10–11 for the annotation format). The archive is named `IDMT-SMT-GUITAR_V2.zip`; that filename is distinct from the Zenodo record's version number.

| Item | Evidence and scope |
| --- | --- |
| Input | Dataset subset 4 contains 64 short pieces with repeated recordings across instruments/setups and tempi. This experiment selected all 64 IDs in one `acoustic_mic/slow` branch, using archive metadata before scoring. The checked files are 44.1 kHz mono 16-bit PCM. |
| Operations | Convert recognized source symbols to the evaluation syntax; assign successive beat spans using the last explicit chord; retain only the first-to-last annotated span. `NC` is interpreted as `N` by the experiment, not asserted as a definition explicitly supplied by the inspected guide. Unrecognized forms remain excluded. |
| Output task | Major/minor/no-chord interval agreement with the supplied annotations. A separate chord-only diagnostic omits reference `N`. This is a chord-recognition evaluation of the chosen branch. |
| Error and guarantee | Duration agreement and boundary matching use the existing project metrics. The guide defines beat timestamps and chord-change notation. It does not report a quantified annotation-timing guarantee or the annotation-creation process in the inspected sections. |
| Total cost | The report will use the actual uncached file-to-label runtime for each fixed method. Cache construction and development-selection timings are separate. No external runtime is inferred from the development cache. |
| Failure conditions and limits | Unknown source symbols reduce coverage; unlabelled intros/tails are excluded rather than guessed. The same capture stream and tempo branch do not establish 64 independent progression families. Chord-only and overall accuracy have different denominators. |

The description explicitly says recordings begin with silence and muted control notes. It also identifies repetition metadata in the last three CSV rows. These observations support excluding unannotated control material and avoiding an independence claim. They do not establish exact acoustic chord boundaries or a particular cause for model errors.

Local provenance: `/tmp/chordrec_opt2/idmt_data/prospective_selection.json`, `validation_manifest.json`, `annotation_inventory.json`, and `dataset_description.txt`. Audio/model results were not part of the metadata selection review.
