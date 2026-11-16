# 边界细化实验：语言检查

## 一、整体观察

按 `academic-language-audit` 和用户指定的 `nature-writing` 1.6.0 检查了新增代码中的注释、docstring、实验计划、结果说明与输出字段。沿用此前已读取的技能指导；这里的产物是一个课程项目实验分支，不套用 Nature 期刊叙事或创新要求。

实际阅读范围为本分支 `boundary.py`、`test_boundary.py`、`experiment/run.py`、`plan.json`、`RESULTS.md` 和保存的结果摘要。数字直接取自本轮开发集输出。没有新增或评价论文，没有把先前测试集表现作为本轮选择依据。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `boundary.py` docstring: "Move existing chord boundaries using local template scores." | 方法作用范围 | 只陈述现有边界移动，不预先声称识别准确率提高；与实现输入和输出一致。 | 低 | 是，属于清晰的代码说明。 | 保留 | 保留原文。 |
| `RESULTS.md` 首段: "The best setting improved pooled duration accuracy by **0.038 percentage points**, below the required 0.5 points." | 结果与接受条件 | 最佳值增加 0.037613891 个百分点，低于事先约定门槛；不能用边界 F1 增加改写为通过主要目标。 | 高 | 是，准确交代主要比较及其判断条件。 | 保留 | 保留原文。 |
| `RESULTS.md` 边界解释: "this is not deletion from the decoded sequence" | 不同统计范围 | 全部 1,226 个预测边界保持，但可评价参考区间内的边界数为 716→712。该句解释两个计数为什么不同，避免错误推断。 | 中 | 是，属于对可见数值差异的必要解释。 | 保留 | 保留原文。 |
| `RESULTS.md` 计时段: "These figures include decoding and refinement, but exclude audio loading and feature extraction." | 总成本边界 | 使用的是缓存特征，不能将约 0.35 秒写成完整音频识别耗时。 | 高 | 是，计时条件直接决定数值含义。 | 保留 | 保留原文。 |

## 三、综合建议

结果说明以未达到预定门槛为主结论，同时保留近边界指标的小幅变化。没有把开发集改善写成对新歌曲的优势，没有宣称统计显著性或将候选升级为验证过的默认方法。所有六个候选均保留，且实验已按计划停止。

五项新测试检查已知转移位置、搜索半径、平分处理，以及随机输入下的序列和静音约束；全套测试为 58 项。代码行为未因语言修改而改变。

发现的写作特征不能证明文本由 AI 生成。
