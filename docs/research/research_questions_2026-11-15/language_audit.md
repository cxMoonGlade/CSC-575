# 候选研究问题与引言草稿审查 — 2026-11-15

## 一、整体观察

审阅 `research_questions.md`、`source_audit.md` 与 `introduction_candidate.tex`。本次使用 creative-thinking-for-research 的问题重构、约束检查，结合 hypothesis-generation 的竞争解释与可反驳预测；按用户要求给出有理由的优先级，不使用自动评分。写作以 nature-writing 为核心，按 academic-language-audit 检查范围和数据一致性。引言沿用 manuscript / research / intro / zh-to-en / generic 的课程论文设置。

本轮主要问题是统计量名称可能混淆完整和弦错误与同根音性质错误；另一处需区分内部类别预测和最终任务表现。独立复核后已改。原四页报告尚未将任何候选写作确定的新方向；本次交付为候选和引言草稿。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 草稿候选 1：“Does projection's increase in major/minor errors persist after decoder calibration?” | 指标范围不准确 | 完整 major/minor 标签准确率改善；增加的是根音正确但性质错误的时长。笼统说 major/minor errors 容易与已报结果冲突。 | 高 | 上下文可以限定，但独立研究问题必须明确。 | 改写 | “Does projection's increase in same-root quality errors persist after decoder calibration?” |
| 候选 3：“若只是多报七和弦或仅在看过的一个案例有效，则不支持。” | 失败条件不准确 | 内部七和弦预测增加仍可能改善归约后的最终结果。 | 中 | 值得检查额外类别，但类别数量本身不是任务失败。 | 改写 | “若只是增加七和弦预测而没有降低最终 major/minor 错误，或收益仅在看过的一个案例出现，则不支持其一般有效性。” |
| 引言末句：“…test whether calibration accounts for the difference while preserving genuine changes.” | 因果归因可能过强 | 重新优化后差距变化不能单独证明原错误的完整机制。 | 中 | accounts for 可作弱解释，但在本设计中用测量陈述更准确。 | 改写 | “Paired error analysis and controlled transitions will measure the remaining quality-error gap and the detection of genuine changes.” |
| 引言：“The corresponding raw error totals were similar, but this does not establish that their locations or score margins were alike.” | 必要比较条件 | raw 错误总时长接近不表示逐帧证据或错误连续结构相同。 | 高 | 是，直接阻止从总体数值跳到单一机制。 | 保留 | 保留原文。 |
| 候选顺序与范围 | 新颖性边界 | 综述与 Cho 2010 已明确讨论相关问题；本项目能研究具体条件下的机制和表现，但不能据此声称填补无人研究的领域空白。 | 高 | 是，课程研究可以有清晰的有限范围。 | 保留 | 保留“排序是建议，不是新颖性评分”和具体前例说明。 |

## 三、综合建议

选一个主问题及一个竞争解释实验，避免同时承诺六个方向。候选 1 最适合承接已有进度；候选 2 的声学干预更直接，但需新增配对声音；候选 5 必须补足真实转换条件。三篇综述共同支撑连续的流程背景，具体实验论断保留原始论文引用。源文献的六项范围与阅读深度单独记录。没有新增实验结果或将探索性发现改写成预设假说。

发现的写作特征不能证明文本由 AI 生成。
