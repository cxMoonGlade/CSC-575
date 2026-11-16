# 一、整体观察

审阅范围为本分支新增 `chordrec/bass.py`、实验 runner、测试文件、README 和初始实验计划的全部说明文字。数值核对来自五个设置在119条开发录音上的原始结果。未使用 test 或 IDMT 结果筛选方法。Nature 写作路径采用 manuscript / methods / experiments / en / generic；课程项目保留简短结论、关键比较及转位限制。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README 第1段 “Adding low-register evidence did not improve development-set chord accuracy.” | 证据边界 | 四个候选的主指标均低于基线；限定 development-set | 低 | 是，直接陈述实验结论 | 保留 | 保留原文 |
| README 表后第1段 “Root accuracy therefore improved while chord accuracy fell.” | 结果一致性 | triad 0.1 的根音准确率增加0.31个百分点，和弦准确率下降0.045个百分点 | 低 | 是，阐明诊断指标与主要任务的差别 | 保留 | 保留原文 |
| bass.py register_scores 说明 “A low-register root contributes a soft preference; inversions can weaken it.” | 方法边界 | 混合分数不强制选择最低音；转位是可能失败情况而非已证实的全部误差来源 | 低 | 是，对公式的简短限定 | 保留 | 保留原文 |
| README 最后一段 “Timings in the shared scorer cover only result lookup and score aggregation here” | 成本定义 | runner 先生成所有预测，共享 scorer 的计时不包含解码；不能当作速度结果 | 中 | 是，应明确测量边界 | 保留 | 保留原文 |

# 三、综合建议

保留全部不利结果以及根音指标与和弦指标的方向差异。结论仅覆盖固定低频带和声明的四个设置，不将其推广为所有低音特征无效。未引入新增文献或未核实机制结论。发现的写作特征不能证明文本由 AI 生成。
