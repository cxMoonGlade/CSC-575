# 一、整体观察

完整审阅 `acquire_fast.py`、prospective selection、acquisition plan 和 `data_notes.md`。Nature 写作路径沿用 manuscript / methods / experiments / en / generic，采用简明数据方法说明。材料明确区分相同曲目的不同速度演奏、全流选择、成员校验及整包校验范围。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| data_notes 第1段 “within this repertoire” | 证据边界 | fast 与 slow 的64个 piece ID 完全重合，不能据此主张新曲泛化 | 中 | 是，限定比较对象 | 保留 | 保留原文 |
| data_notes 第2段 “Selection used archive paths only” | 选择方法 | 冻结选择包含该路径下全部64个 WAV；未按标签或分数筛选 | 中 | 是，准确说明选择规则 | 保留 | 保留原文 |
| data_notes 第3段 “NC remains mapped to N; ambiguous symbols remain X.” | 标注一致性 | 原 load_chords 未修改，保持既定转换和区间范围 | 中 | 是，影响指标分母与解释的必要说明 | 保留 | 保留原文 |
| data_notes 第4段 “The published full-archive checksum is not verified.” | 校验范围 | 只取需要的 HTTP 范围，不能把 ZIP 成员CRC当作整包哈希核验 | 中 | 是，准确界定完成的校验 | 保留 | 保留原文 |

# 三、综合建议

保留全部64条录音，包括无 scoreable 区间的录音；最终清单只记录输入与解析结果。下载完成后添加实际总时长、文件数及网络重试情况，不填入未运行的识别分数。所有识别结果由后续冻结比较生成。发现的写作特征不能证明文本由 AI 生成。

完成后补充检查：新增实际采集统计与 `acquisition_validation.json` 一致。64条录音、1786.16秒总时长、59.56%可评分覆盖以及5条零可评分录音均保留。对所有文件重新读取并核验的结论来自独立验证脚本，而非仅重复下载程序的成功标记。未新增识别效果结论。
