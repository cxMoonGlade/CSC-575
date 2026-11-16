# 一、整体观察

完整审阅独立投影模块、测试、runner、计划和 README。Nature 路径沿用 manuscript / methods / experiments / en / generic，固定术语为 independent projection、fundamental-only NNLS、major/minor accuracy。文本直接比较主指标，并保留投影较 NNLS 低0.34个百分点的结果。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README 开头 “Independent projection retained most of the fundamental-only NNLS improvement” | 证据边界 | 投影增益6.06个百分点，NNLS增益6.40个百分点；后句给出全部数值 | 低 | 是，“most”紧邻可核实比较 | 保留 | 保留原文 |
| README 公式段 “under these fixed settings” | 方法结论范围 | 唯一差异是独立投影与联合求解；限定在本组参数和开发数据 | 低 | 是，阻止推广到所有拟合方法 | 保留 | 保留原文 |
| README 计时段 “excludes audio loading, spectrum extraction, tuning and RMS” | 总成本边界 | 保存的 projection_decode_seconds 未涵盖以上步骤 | 中 | 是，不能将局部计时当作端到端优势 | 保留 | 保留原文 |

# 三、综合建议

保留 NNLS 更高准确率及投影计算成本的区别，不将接近的数值写成结果相等。最终运行时间必须使用包含前处理的统一测量。发现的写作特征不能证明文本由 AI 生成。

补充审阅：uncached reader、其两个新增测试及 README 最后一段。说明列出实际执行的预处理与投影步骤，不声称测得完整运行时间。三条开发录音的 parity 结论对应 `extractor_validation.json`，六项针对性测试已通过。原选择阶段模块保存为 `results/source_snapshot/projection.py`，其哈希与 `source_hashes.json` 一致；后加 reader 未改变原投影公式。
