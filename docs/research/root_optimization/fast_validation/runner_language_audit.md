# Fast-comparison runner: writing and evidence review

## 一、整体观察

审读本目录 `compare.py` 的文档字符串、帮助、运行协议与 `README.md`。沿用 academic-language-audit 和 nature-writing；后者的路由为 manuscript / methods / method and experiments / English / generic。本轮是已冻结模型的评估工具，没有新的文献结论。数据来源的六项审读由 `/tmp/chordrec_root_fast/source_audit.md` 记录。

本工具将新节奏版本与新曲目区分，将包括参考 N 的主指标与仅限参考和弦的根音指标区分。未写入尚未运行的模型结果。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README opening: “Each piece ID matches a previously evaluated slow recording, so this tests transfer within the same repertoire.” | 推广范围 | 快慢两组使用相同 64 个曲目 ID。匹配规则与元数据已核对。 | 高 | 是，明确测量范围。 | 保留 | 保留原文。 |
| README metrics: “Root accuracy and chord-only accuracy exclude reference N” | 误差定义 | 孤立和弦实验没有参考 N；此处有 N，不能直接沿用总 scoreable duration 作为根音分母。 | 高 | 是，代码通过合成区间测试。 | 保留 | 保留原文。 |
| README timing: “Each timed method loads and processes the full audio independently.” | 成本边界 | 调用完整 uncached extractor，单独 warm-up；说明所包含和排除的步骤。 | 高 | 是，与现有 predict 计时范围一致。 | 保留 | 保留原文。 |
| Protocol: “Recordings are new tempo renditions, not independent new compositions or unseen progressions.” | 证据范围 | 数据文档描述不同速度的演奏；未从波形独立核实完整录制或处理历史。 | 中 | 是，限定为数据集记录的节奏版本，不声称已证明独立录音。 | 保留 | 保留原文。 |

## 三、综合建议

按预定指标完整记录三种方法。N 错误单列；零 scoreable 文件继续计入音频、覆盖率与耗时。结果只能评价这些新节奏版本，不能写成独立新曲目的泛化。上述写作特征不能证明文本由 AI 生成。

Nature-writing checks: one experiment, one frozen comparison, explicit denominators and full cost. Source and validation logs stay outside the report. The API labels remain `long`, `projection`, and `harmonic`; the last denotes the already frozen fundamental-only NNLS configuration.
