# 一、整体观察

审阅新增 `chordrec/note_predict.py`、`tests/test_note_predict.py` 及生成播放器中的新增标题与说明。已按 academic-language-audit 和 nature-writing 两项技能检查；Nature 路径沿用 manuscript / methods / experiments / en / generic。界面仅说明预测方法、开发集示例和参考标签，研究结论留在报告。原 `run.py` 与默认配置未修改。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 模块说明 “Recognize chords in one audio file with a frozen note-profile front end.” | 范围 | CLI 接受冻结的投影或 NNLS 配置，不修改原批处理流程 | 低 | 是，直接说明用途 | 保留 | 保留原文 |
| 播放器说明 “Development example with performed reference labels.” | 证据边界 | 播放器只能加载保存划分中的 GuitarSet 开发录音；本次示例预先指定 | 中 | 是，防止把示例当作新测试结果 | 保留 | 保留原文 |
| summary.runtime_definition “Imports, the separate warm-up pass, raw diagnostics, hashing, file output and playback generation are excluded.” | 成本定义 | 使用已有 predict 函数的音频到区间计时，单独记录完整预热开销 | 中 | 是，明确计算时间包含与排除项 | 保留 | 保留原文 |
| JAMS 处理注释 “JAMS endpoints may be rounded beyond the final audio sample.” | 复现说明 | 实际示例末端标签超出音频约10微秒；播放器按音频长度截断，保留原标签 | 低 | 是，解释必要的边界处理 | 保留 | 保留原文 |

# 三、综合建议

保留方法名、开发集标记和计时边界。示例准确率只解释该录音；不代替整个开发集或冻结测试的结果。独立子进程验证投影与 NNLS 的 CSV 与共享推理函数完全一致；浏览器验证播放、停止和定位。发现的写作特征不能证明文本由 AI 生成。

界面补充审阅：轨道名由 “Fundamental projection” / “Fundamental NNLS” 精简为 “Note projection” / “Note NNLS”，避免图形左侧文字被截断。只修改显示文字，方法标识和配置不变。示例 HTML 从保存区间重绘，未重复推理或改动成绩。
