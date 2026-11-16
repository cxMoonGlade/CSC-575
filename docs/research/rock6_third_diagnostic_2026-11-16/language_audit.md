# Writing check — rock_6 diagnostic

## 一、整体观察

审阅范围为本目录 `README.md`、`rock6_diagnostic.py` 的说明文字和图中标签，以及供报告采用的短段落；已核对 `run/summary.json`、`run/validation.json` 和图像。采用 nature-writing 的 manuscript / research / experiments / zh-to-en / generic 路由，并执行 academic-language-audit。新文字仅解释本项目的诊断，不新增文献综述或外部方法主张。

写作以观测到的局部分差和解码标签不一致为主线，区分同根二选一和全部24模板的预测。诊断保留现有模型及参数，不将归一化 chroma 称作物理能量，也不将它解释为实际演奏音符的证据。数据与实现校验留在研究记录中，报告只保留直接推进研究问题的一项结果。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README 首段：“During 7.85 s of these errors (79.36%), its correct major template still scored above the minor template at the reference root.” | 证据边界核对 | 明确限定同根二选一；不等同于24模板中正确预测。与精确时长分区一致。 | 高 | 是；这是诊断直接测量的现象。 | 保留 | 保留原文。 |
| README 第三段：“These are separate partitions: a positive same-root margin does not ensure that the reference chord beats every competing root.” | 推理衔接 | 7.85 s 与5.55 s分别来自同根分差和全类别raw预测，须说明分母与事件不同。 | 高 | 是；此处解释不同统计量，避免虚假矛盾。 | 保留 | 保留原文。 |
| README 第四段：“The mean quality margin over the decoded quality errors was −0.00591.” | 证据解释 | 正分差时长占多数，但负分差可幅度更大；均值防止将持续时长直接当成解码目标。 | 高 | 是；该数值改变如何理解前面的时长比例。 | 保留 | 保留原文。 |
| README 方法段：“Chroma values are feature activations, not acoustic energy or measured note amplitudes.” | 术语准确性 | 两条前端输出都经L2归一化；不能用它们判定实际演奏中的三音幅度。 | 高 | 是；限定测量量的含义。 | 保留 | 保留原文。 |
| 图(a,b)纵轴：“Normalized activation”；图(c)：“Major − minor score” | 图文一致性 | 标签对应单位长度chroma和参考根音的模板分差。所有该曲参考标签均归约为major。 | 中 | 是；术语简短并与实现一致。 | 保留 | 保留原文。 |
| 验证记录：“Archived artifacts contain labels and grid/RMS metadata, but not score arrays.” | 核查范围 | 原结果没有可比较的分数数组；实际验证是冻结源码、环境、预测区间和解析公式。 | 高 | 是；防止夸大复现范围。 | 保留 | 保留原文。 |

## 三、综合建议

报告采用一个短段落即可。不要把79.36%的正分差时长写成“声学证据正确率”，也不要据此认定切换惩罚一定是错误根因。正文保留实际测得的7.85/9.89 s及后续校准的优先级；完整24模板输出、局部均值、复现日志和大图放在本研究记录。

图像已检查，坐标、图例和时间线完整，无文字重叠。脚本的注释和说明只解释数据处理、验证与输出，不加入结果推测。发现的写作特征不能证明文本由 AI 生成。
