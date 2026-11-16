# 优化结果草稿语言审查

## 一、整体观察

按 `/home/cx/.codex/skills/academic-language-audit/SKILL.md` 及用户指定的 `/home/cx/AI_QEC/AI_QEC/.agents/skills/nature-writing/SKILL.md`（1.6.0）检查了 `optimization.md`、`portability.md` 和 `verify_portability.py`。本轮沿用已读取的技能核心与适用章节指导；以课程报告的简洁英文为目标。

实际核对了三个完成方向及一次后续试验的结果 JSON、窗口比较脚本、白化计划、生产特征提取代码和三条开发录音的移植检查。随后读取了 `/tmp/chordrec_opt2/external_results/summary.json`、`run.json` 和 `annotation_audit.json`，将外部比较的占位说明替换为真实数值；没有新增参数选择。数据集官方网页、Zenodo 记录和说明文档的 1.3.4、2.2.2 节已核对，未新增论文评价。

草稿以开发改善幅度及其没有在固定外部比较中重现为主线；选择门槛保留在实验计划中。长窗基线保持默认。开发数值核对记录位于 `numeric_checks.json`，外部结果核对还记录在 `../report_final/evidence_checks.json`。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 修订前 `optimization.md`，表后首段："None met the gate." | 叙事重心 | 计划中已记录门槛；结果摘要应以实际分数及外部变化为中心，避免反复使用通过／失败措辞。 | 中 | 单独看属于正常协议说明；在这份简短摘要中移到实验计划更合适。 | 精简，已完成 | 删除该句，保留完整分数和比较结果。 |
| `optimization.md`："Window length changes both frequency resolution and temporal averaging; these scores do not isolate either effect." | 机制推断 | 较长窗同时改变两种性质；汇总准确率本身不能证明改善来自频率分辨率。该句避免把试验动机写成已证实机制。 | 高 | 是，直接限定所支持的解释。 | 保留 | 保留原文。 |
| 修订前 `optimization.md`："Results are pending." | 外部验证状态 | 真实外部结果已齐备，此句不再符合进度；最终文本采用两方法的总体、近边界及 chord-only 数值。原稿保存在 `../report_review/optimization_before_external.md`。 | 高 | 是，作为此前状态正确，当前需要更新。 | 核实后改写，已完成 | "Its fixed comparison on 64 IDMT acoustic-microphone recordings did not reproduce that gain: accuracy was **65.558%**, against **65.732%** for the baseline." |
| 最终 `optimization.md`："it does not establish that `NC` means silence" | 标注语义与模型原因 | 1.31% 是在显式 NC→N 映射下的时长符合率；所读说明没有定义 NC，不能用低能量规则的分数倒推其真实含义。 | 高 | 是，直接限制一个容易出现的错误机制解释。 | 保留 | 保留原文。 |
| `portability.md`："The selected development candidate needs no new production feature option." | 实现与实验一致性 | 最佳候选仍用 8,192 样本长窗；现有代码的调音估计也用该窗。三条开发录音的特征与预测完全一致，因此不需为未选中的 16,384 窗增加配置项。 | 中 | 是，陈述具体实现判断，证据范围为此配置及三条检查。 | 保留 | 保留原文。 |

## 三、综合建议

正文不使用 29 或 30 这一容易混淆的设置总数；移植说明注明 30 行分数中含重复控制，排除边界分支额外基线才得到 29。三个方法方向和四个后续新设置已经足以说明范围。

更新四页报告时保留旧 GuitarSet 测试表，把新的开发选择与已经完成的 IDMT 比较分开。外部任务、标注口径、覆盖率、总耗时和结果已依据真实输出填写。移植检查是三个独立的配置一致性检查，不追加到 pytest 数量中。最终优化摘要采用目标仓库的相对证据链接，不保留临时目录路径。

发现的写作特征不能证明文本由 AI 生成。

结果摘要中的复现命令使用已集成 runner 的参数和仓库相对路径，固定三个线程环境变量为 1，并指定新输出目录。本报告代理没有为核对文字而再次运行外部评估。
