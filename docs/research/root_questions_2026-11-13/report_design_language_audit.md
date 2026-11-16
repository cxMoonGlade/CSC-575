# 一、整体观察

审阅材料：report_design.md、followup_sources.md 全文和 annotation_check.py 的说明文字。按 academic-language-audit 与 nature-writing 处理；Nature 路由为 manuscript / research / intro、experiments、discussion、title / zh-to-en / generic，目标仍为四页课程报告。引言采用“具体任务—观察—问题—实验”顺序，英文草稿在前，中文设计说明在后。

本轮主问题从“是否需要不同时间约束”调整为“表示与解码如何影响两类错误”。新标注核对显示开发数据没有符合当前计分规则的同根性质变化，因此需要给结构化惩罚增加保留真实变化的检验。定位以文件名、章节和完整原句为准。原文审读深度在 followup_sources.md；模型训练及 E1–E3 未执行。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| report_design，Introduction：“The interaction matters: a representation that improves root estimates may still introduce quality errors in some passages.” | 保留判断 | 保存的同区间预测显示这一局部现象；句子没有把它推广为所有录音的规律。 | — | 限定 some passages 与已检查范围一致。 | 保留 | 保留原文。 |
| report_design，Preliminary-results：“Among contiguous, scoreable chord-to-chord boundaries, the 119 development recordings contain 410 root changes and no same-root major/minor changes.” | 计数范围 | 必须保留 contiguous、scoreable；否则读者可能误认为完整原始音乐中没有任何性质变化。 | 高 | 精确限定是必要的统计定义。 | 保留 | 保留原文；在中文说明中补充分层定义和断点处理。 |
| report_design，Preliminary-results：“This concentration motivates examining the representation, decoder and vocabulary reduction together; it does not identify which one explains the errors.” | 保留判断 | 额外音分层与曲目混杂，增加主要来自 rock_6。 | — | 明确相关观察与机制之间的距离，影响下一步实验选择。 | 保留 | 保留原文。 |
| report_design，E1：“在 progression 1 上选择、2 上观察，再交换” | 泛化范围 | 两个家族过去都用于开发；交换不是新的独立测试。 | 高 | 作为开发稳定性检查合理。 | 保留 | 保留相邻解释“两个家族均已用于开发，这只是开发稳定性检查”。 |
| report_design，E2：“交叉改变三音幅度、额外七音及和弦时长” | 未完成的方法细节 | 方向已确定，但幅度、时长、样本数与种子尚未固定；不能称为完整预注册方案。 | 中 | 在进度报告中列下一步实验是正常写法。 | 改写 | 保留计划表，补充“具体幅度、时长、样例数和随机种子将在生成前固定，当前尚未采集或分析这些样例”。 |
| followup_sources，Cho 2010：“Small gains from complex transitions in this setting do not rule out other structures.” | 保留判断 | 作者实验适用范围有限，已有先例不等于所有结构无用。 | — | 保留开放问题，同时没有否认原结果。 | 保留 | 保留原文。 |

# 三、综合建议

将完整和弦准确率作为主要效果，局部性质错误用于解释。保留原多分辨率实验及个人 PI，明确新问题由后续分析形成。下一步先做统一惩罚对照和真实变化检验；结果若不支持增加结构，也应成为研究答案。

本轮没有听音确认 rock_6 的实际三音，也没有证明约简产生了错误。原标签、四种输出和原汇总已程序核对；音频解释仍待结合可控实验和听音。脚本只读已有资料；新文件经过两步语言检查后归档。现有 PDF 的版式和正文未在本轮重新编译。

发现的写作特征不能证明文本由 AI 生成。
