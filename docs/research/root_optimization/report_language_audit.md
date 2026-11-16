# 根音实验报告更新：语言与证据审查

## 一、整体观察

审阅范围为本目录的 `progress_report.tex`、`results.tex`、编译后的四页 PDF，以及用于核对数值的开发集和孤立和弦结果 JSON。保留了原 GuitarSet 结果宏及全部 16 条参考文献。Mauch–Dixon 的输入、操作、输出、误差/保证、成本与失败条件沿用已读全文的 `experiments/root_harmonic/review.md`；本次未增加论文或扩展其结论。

Nature-writing 路由为 manuscript / research / method、experiments、discussion / English / generic。核心结果是开发集上音符谱表示改善根音预测；直接投影接近 NNLS，而新采集的孤立和弦评估对三种方法都达到满分，因此没有确立新和弦进行上的优势。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| §4.4: “Fundamental-only NNLS reduced their duration from 547.08 to 422.78 s.” | 证据范围 | 前句明确是开发集；数值与原结果相符，没有推广到测试集。 | 高 | 是，直接陈述当前数据。 | 保留 | 保留原文。 |
| §4.4: “Harmonic decays 0.6 and 0.9 scored 73.07% and 63.20% chord accuracy.” | 不利证据 | 两个泛音字典都低于 fundamental-only，对解释改进来源至关重要。 | 高 | 是，防止把提升归因于泛音去除。 | 保留 | 保留原文。 |
| §4.4: “All three decoded methods reached 100% chord and root accuracy, leaving no improvement to measure on these clips.” | 天花板效应 | 新测试支持正确运行和成本比较，但不能区分识别精度。 | 高 | 是，与表 2 的三个满分一致。 | 保留 | 保留原文。 |
| 原 §4.1: “Feature caching is disabled” | 成本边界 | 开发阶段复用了调律和谱缓存，原句可能被理解为所有实验都无缓存。 | 高 | 原句对旧完整推断计时成立，新增实验后需限定。 | 改写 | “Feature caching is disabled for these measurements; the OS file cache is retained.” |
| Discussion draft: “whereas harmonic profiles reduced accuracy” | 比较对象 | 衰减 0.6 的得分仍高于原 STFT 基线，降低是相对 fundamental-only NNLS 而言。 | 高 | 不完整，比较对象必须明确。 | 改写 | “Both harmonic variants scored below fundamental-only fitting.” |
| 原图 2 说明: “each dataset's scoreable duration” | 数据范围 | 同一个 IDMT 数据集现在包含两次不同子集评估。 | 中 | 原说明在旧版本可理解，新版本需标清。 | 改写 | “Long-window errors in the original GuitarSet and IDMT subset-4 comparisons, divided by scoreable duration.” |

## 三、综合建议

保留三个证据层次：原窗口比较、新开发集消融、新孤立和弦比较。正文只给出影响结论的数值，完整运行记录留在仓库。新表的耗时来自独立、无特征缓存的完整推断；开发实验的阶段计时没有进入表中。发现的写作特征不能证明文本由 AI 生成。
