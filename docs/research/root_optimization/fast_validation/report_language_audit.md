# Fast-recording report update: language audit

## 一、整体观察

审阅对象为本目录的 `progress_report.tex`、`results.tex`、两张图及编译后的四页 PDF；实际阅读全文，并复核新表格、摘要、讨论和图注。数字来自 `/tmp/chordrec_root_fast/results/summary.json`、逐录音结果和 `figures_final/error_case_selection.json`。本轮没有重读全部 16 篇参考文献，也没有增加文献主张；Mauch and Dixon 的方法解释沿用此前全文审读记录。

本轮将单和弦测试的满分结果压缩为一句，用含和弦变化的快速度版本检验已冻结的方法。正文保留投影法的整体收益、根音与质量错误的取舍，以及逐录音和流派上的退步。定位使用章节名、宏名和原文片段。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `RootResults` 图注：“root accuracy excludes reference $N$ and ignores major/minor quality” | 指标定义与内容一致性 | 主指标含 N，根音指标排除 N；59 条可计分录音中仅58条有可计分和弦时长，不能混用分母。 | 高 | 是；这是理解指标必要的定义。 | 保留 | 保留原文。 |
| Root-error follow-up：“Across the 59 scoreable files, projection improved 30, tied 13 and worsened 16.” | 证据边界 | 总体提升不是每条录音均有提升；此句保留可复核的负面分布，后一句报告 rock/blues 下降6.18个百分点。 | 高 | 是；直接描述观察结果，没有推断显著性。 | 保留 | 保留原文。 |
| `AbstractResults`：“These recordings are new tempo versions within the previously evaluated repertoire.” | 泛化范围 | 64条快版本与此前慢版本共享piece ID，不能写成未见曲目的外部泛化。 | 高 | 是；这一区分决定结论适用范围。 | 保留 | 保留原文。 |
| `ExampleCaption`：“Cases were selected after evaluation for inspection.” | 案例选择 | 图1选59条可计分录音中提升和下降最大的两条，覆盖率分别34.29%和86.55%，不是随机代表样本。 | 高 | 是；图注明确选取规则，避免以极值案例替代总体结果。 | 保留 | 保留原文。 |
| Root-error follow-up：“NNLS identified slightly more roots but made more quality errors and took over four times as long as projection.” | 主指标与成本 | NNLS根音准确率78.45%略高于78.32%，但完整标签准确率66.95%低于67.80%；44.37秒对10.43秒。仅报根音将改变方法排序。 | 高 | 是；这是与主指标及完整推断成本一致的结果比较。 | 保留 | 保留原文。 |
| Root-error follow-up：“Long STFT, fundamental-only NNLS and projection all reached 100\% on the scoreable intervals of 88 isolated IDMT chords” | 指代与信息密度 | 明确列出三种方法并限制到可计分区间，避免将前述两个谐波衰减设置误算为这三种方法；单和弦结果不再占一个表格。 | 中 | 是；必要的对照和边界合并到一句。 | 保留 | 保留原文。 |
| Discussion：“The guide leaves \\texttt{NC} undefined, so its meaning needs checking before revising the energy rule.” | 观察与推测 | 未声称已有试听证明NC的语义。正文保留慢版本1.31%匹配和能量重叠，后续解释留待检查。 | 中 | 是；措辞保持未解决事实的不确定性。 | 保留 | 保留原文。 |

## 三、综合建议

本稿已将主张限定为这些快速度版本上的提升，区分根音准确率与完整标签准确率，并保留质量错误增加和部分录音退步。原 GuitarSet 表格及其 `FinalResults` 宏逐字保留；图2明确属于原 GuitarSet 和 IDMT 慢版本结果。新增图1使用最终案例文件，未复用旧测试案例。

后续需要的数据是未见曲目的评估和对NC区间的试听核查；当前资料不能证明跨曲目泛化或谐波去除机制。本轮未新增这类结论。四页布局、16条参考文献、数字和图注已核对；没有未解析引文或越界文本框。

发现的写作特征不能证明文本由 AI 生成。

整合补充：图注增加 “Blank spans are unannotated.”，与已检查的图形约定一致。新图另存为 `root_fast_cases.pdf`，保留旧 GuitarSet 图供历史结果链接使用。此路径修改不改变图内容。

最终图注将空白限定为 reference 轨道：“Blank reference spans are unannotated.”；预测 N 使用浅灰矩形，不混淆标注缺失和预测类别。
