## 一、整体观察

读取当前项目 README 全文；本轮修改范围为一段后续实验说明、两行外部结果、数据相关工作一句话和第 16 条数据集引用。原 GuitarSet 测试表、个人目标/PI 和前 15 条参考文献保持原样；仅删除早期结果段中已经过时的下一步句子。另审阅 `.gitignore` 新增的 `experiments/optimization_v2/cache/`：只排除可重建的特征缓存，不排除计划、结果或负面证据。

使用 `academic-language-audit` 和用户指定的 `/home/cx/AI_QEC/AI_QEC/.agents/skills/nature-writing/SKILL.md`，沿用已读 manifest 1.6 核心、main-text-discipline 及方法/实验/英语片段；本轮另读 Related Work 片段。Nature 路由：manuscript / methods / experiments + related-work / en / generic。采用“有限开发改善 → 冻结外部比较 → 参考标签诊断 → 保留基线”的四句顺序；完整实验记录继续留在链接中。

独立核验见 `../external_review.json`：256 行包含 long/fixed × raw/viterbi 各 64 条记录；总体、区域和 chord-only 汇总重算一致。将参考中非 N 标签设为 X 后重新计算区间分数，得到两种解码方法相同的 N-only 正确时长 1.994693874253926 秒、N 参考时长 151.835147395 秒，即 1.3137234089%。14 个源码文件、3 个配置/选取输入、64 个音频及 64 个标注哈希均匹配；最短音频 17.5 秒。四条录音没有可评分参考区间，仍计入覆盖率及运行时间。

第 16 条引用依据已取得的官方 Zenodo 元数据：Kehling、Männchen、Eppler，2023，版本 1.0.0，DOI 10.5281/zenodo.7544110。实际内容核对限于数据说明 §1.3.4、§2.2.2 和所选标注格式，不声称完整阅读其关联算法论文。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 初稿 Follow-up 第 1 句：“below the 0.5-point adoption threshold”（副本见 `../README_before_final_polish.md`） | 实验流程占据结果叙述 | 用户要求避免把项目写成认证流程；实际增量 0.2584434103587996 个百分点与外部下降已足以说明保留基线，内部阈值可留在实验计划。 | 中 | 阈值属于正常实验记录，但不必放在这段简短结果摘要中。 | 精简 | “gained 0.26 percentage points over the long window in [development experiments](../../../results/optimization_v2/README.md).” |
| 原 README Evaluation 末段：“The next method question is whether a change detector can distinguish sustained harmonic changes from shorter performance variations.” | 后续计划已过时 | 新增开发及外部比较后，这个下一步描述不能反映当前的 NC 标注/音频检查重点；初始实验链接和结果仍然有效。 | 中 | 原句在早期报告中是合理计划，但当前版本应更新。 | 精简 | 删除这一个句子，保留初始运行链接、触发比例和其余结果链接。 |
| Follow-up 第 2 句：“64 … four recordings have no scoreable intervals” | 样本与分母 | 64 条全部处理，但只有 60 条具有定义的逐录音准确率；覆盖率按所有音频计为 61.6564397350%。 | 中 | 用短括号交代必要分母信息，不扩大样本独立性主张。 | 保留 | 保留原文。 |
| Follow-up 第 3 句：“NC→N is our convention” | 来源与解释边界 | 所读指南未定义 NC；目前仅观察到该约定下 N 时段的低正确率，没有听验来确定这些声音的性质。 | 中 | 该限定直接影响指标含义，不能改成作者明示定义或将 NC 写成已知静音/旋律。 | 保留 | 保留原文。 |
| Follow-up 第 4 句：“improves neither overall nor near-change accuracy” | 结论范围 | 外部总体、近变化和 chord-only 准确率均下降；边界 F1 有微小上升，因此不泛称所有指标都下降。 | 中 | 限定到研究问题对应的准确率，表述充分且准确。 | 保留 | 保留原文。 |
| 新增 [16] 与 Related Work 数据说明 | 引用身份与阅读深度 | 名称、作者顺序、年份、版本、DOI 来自官方数据记录；只陈述已核对的数据类型。 | 低 | 数据集可以作为正式参考文献，不必虚构关联算法优势。 | 保留 | 保留原文。 |

## 三、综合建议

无需追加长篇讨论。两行表格显示外部结果，四句话解释实测变化、评分分母和结论；完整网格、失败分支、运行时间和逐录音分析由 `results/optimization_v2/README.md` 引导。新链接随最终整合落盘即可；BibTeX 第 16 项由报告代理同步添加。

本轮没有修改模型参数或再次运行推断。原始表格与 PI 文本的字面一致性检查保存在 `README_checks.json`。N 诊断明确写成 “label 1.31% of reference N duration as N”，只表示与参考标签的时长一致率。NC 的实际声音内容仍待听验；该未知没有被填成解释。缓存忽略规则无科学文字需要润色，路径准确且作用范围符合实验组织。

**发现的写作特征不能证明文本由 AI 生成。**
