# IDMT NC annotation review

## 一、整体观察

Reviewed on 2026-11-09. The current adapter follows the documented beat-event format. No parsing or interval-extent error was found that explains the low NC agreement. The remaining uncertainty is the acoustic meaning of NC and the precision of its beat-aligned boundaries.

The guide describes chord symbols as changes that persist until the next explicit symbol (§2.2.2, printed pp. 10–11). It describes a silent opening bar followed by two bars of muted control notes (§1.3.4, printed p. 5). The evaluation begins at the first annotated beat, so this opening material is excluded. Forty-five selected CSVs end with an NC event. The adapter gives these terminal events no duration because no following beat supplies an endpoint; it does not extrapolate them into the recording tail.

Within the scored beat span, NC occupies **151.835147395 s in 32 of 64 recordings**. The 297 beat intervals merge into 207 contiguous NC runs. Thus the reported NC disagreement concerns substantial within-piece material, rather than the unannotated silent opening alone. Genre-folder totals are descriptive groups, not independent statistical samples.

| Genre folder | Recordings with positive NC duration | NC seconds | Contiguous NC runs |
| --- | ---: | ---: | ---: |
| classical | 4 | 11.962313 | 9 |
| country_folk | 4 | 11.448367 | 12 |
| jazz | 7 | 54.004853 | 76 |
| latin | 5 | 10.839683 | 23 |
| metal | 3 | 1.214263 | 3 |
| pop | 2 | 12.386757 | 8 |
| reggae_ska | 5 | 38.698526 | 65 |
| rock_blues | 2 | 11.280385 | 11 |

Examples in `IDMT-SMT-GUITAR_V2/dataset4/acoustic_mic/slow/` make the structure explicit:

- `reggae_ska/annotation/chords/reggae_1_95BPM.csv`, rows 1–32: NC alternates with a chord on successive beats. The other three reggae pieces follow the same NC/chord alternation.
- `jazz/annotation/chords/jazz_1_160BPM.csv`, rows 1–64: NC begins on beat 3 in each of the first 16 bars and persists through beat 4.
- `jazz/annotation/chords/jazz_8_110BPM.csv`, rows 6–64: eight NC runs occupy beats 2–4 of even-numbered bars, totaling 13.130907030 s. The first run is 9.218321995–10.901904761 s. The final event at 42.537437641 s has no scored duration.
- `pop/annotation/chords/pop_4_100BPM.csv`, rows 4–8: NC persists across five beat intervals before the next explicit chord. Treating unlabeled beat rows as a return to the preceding chord would contradict the supplied change notation.

These patterns establish annotation structure. They do not determine whether an individual NC span contains silence, decay, noise, percussion, or pitched notes. No perceptual listening claim is made in this review.

### Sources and reading depth

| Source | Input, operations, and output | Error, total cost, and failure evidence | Reading depth |
| --- | --- | --- | --- |
| Bundled `SMT_GUITAR_dataset_description.pdf`, §§1.3.4 and 2.2.2 | Recorded guitar audio; timestamped beat events, chord changes and optional bass notes; final three rows contain repetition and metre metadata. Supports carry-forward parsing and excluding metadata rows. | No NC vocabulary definition, annotation-generation procedure, timing-error bound, or annotation-cost estimate appears in these sections. The guide states that some onset/texture annotations are missing. | Read both sections in extracted text, checked corresponding local CSV structures. Searched the full extracted guide for NC/no-chord definitions. |
| [Official dataset page](https://www.idmt.fraunhofer.de/en/publications/datasets/guitar.html), Database Content; [Zenodo record](https://zenodo.org/records/7544110), Description | Confirms subset 4 contains 64 pieces repeated across tempi and guitars, with chord and other annotations. | No NC semantics or alignment guarantee supplied. Dataset creation and acoustic inference costs are not quantified there. | Read the dataset descriptions and version information on both primary pages. |
| Local archive inventory and selected annotations | Parsed all 64 selected chord CSVs using the unchanged adapter; merged adjacent N intervals only to count runs. Inspected the four example files above. | Inventory contains no onset/texture files for `acoustic_mic/slow`, so these annotations cannot resolve the acoustic content of this branch's NC spans. No recognition model was trained, tuned, or rerun. | Complete member-name search; all selected CSVs parsed; representative rows directly read. Counts saved in `nc_annotation_stats.json`. |
| [IDMT Transcription API documentation](https://www.idmt.fraunhofer.de/content/dam/idmt/documents/IL/idmt_musicbricks_transcriber_documentation.pdf), 2016, §2.2, Listing 1 line 91, PDF page 6 | A separate audio transcription tool exports beat-aligned chord labels. Its XML comment defines NC as a failure to find a chord owing to silence, noise, or other causes. | No demonstrated link from that output convention to this dataset's annotation process. No performance or end-to-end cost guarantee used. | Read introduction, command-line description and XML example; located NC comment. Context only, not evidence defining the dataset's NC labels. |

Both required writing skills were applied. Nature routing: manuscript / methods / method / en / generic. Terminology is fixed as follows: **NC** is the source symbol; **N** is the experiment's mapped evaluation class; **silence** is an acoustic claim that neither symbol alone establishes.

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| `chordrec/idmt.py`, `convert_chord` docstring: “NC is interpreted as no chord; the dataset guide does not define this abbreviation.” | 证据边界 | 正确区分实验约定与作者定义；本次检索未找到更直接的数据集定义。 | 低 | 是，措辞精确且必要。 | 保留 | 保留原文。 |
| `report/dataset_reading_notes.md`, final paragraph: “They do not establish exact acoustic chord boundaries or a particular cause for model errors.” | 证据边界 | 节拍标注结构并不提供声音边界精度保证。NC 的节拍内周期性不能单独确定声音内容。 | 低 | 是，直接限定所读材料的适用范围。 | 保留 | 保留原文。 |
| `report/dataset_reading_notes.md`, failure row: “The same capture stream and tempo branch do not establish 64 independent progression families.” | 统计单位 | 四个 reggae 文件具有相似节拍级 NC 结构；本次未评估全体和声序列独立性。原文没有将文件数等同独立乐曲数。 | 低 | 是，对当前数据结构的限制准确。 | 保留 | 保留原文。 |

## 三、综合建议

Keep the frozen evaluation labels and comparison unchanged. Combine the annotation counts above with the separately computed energy analysis to describe what the current silence threshold can and cannot represent. Acoustic energy can establish that a span is above that threshold, but cannot distinguish noise from pitched or harmonic content. The original audio with exact NC spans is the appropriate next review aid.

Any claim that NC denotes silence alone, that the source annotations are wrong, or that the separate API generated these annotations would exceed the inspected evidence. The source API convention can remain in research notes; it need not expand the report bibliography.

The new `chordrec/nc_diagnostic.py` was also checked against `audio.extract_features`, `model.decode` and `evaluate._normalize`. Its RMS threshold matches the frozen forced-N rule, and it weights quantiles by exact overlaps with centred prediction cells. Independent overlap computation from the raw annotation beat intervals and saved predictions reproduced 151.835147395 s of NC and 1.994693874254 s of matching N. All exported category totals matched `intervals.csv`; both diagnostic tests passed with `.venv/bin/python -m pytest -q tests/test_nc_diagnostic.py`. The measurements support a statement about the existing energy threshold. They do not establish a new threshold, a perceptual classification, or a generalization improvement.

**发现的写作特征不能证明文本由 AI 生成。**
