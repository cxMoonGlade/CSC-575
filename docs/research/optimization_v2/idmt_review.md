## 一、整体观察

审阅 `chordrec/idmt.py`、`tests/test_idmt.py`、`chordrec/external_compare.py` 全文，以及冻结配置和前瞻性选取计划。核对官方说明 §1.3.4（印刷第 5 页）与 §2.2.2（第 10–11 页），并解析所选 64 份 CSV、读取 WAV 文件头。未读取音频样本、提取特征或计算任何外部预测、分数。

已应用 `academic-language-audit` 和用户指定的 `/home/cx/AI_QEC/AI_QEC/.agents/skills/nature-writing/SKILL.md`，沿用 manifest 1.6 核心及方法/实验片段。Nature 路由为 manuscript / methods / method + experiments / en / generic。说明文字直接交代观测格式、转换规则和测量范围，没有增加文学化背景或机制解释。

解析结果与计划一致：157 个原始符号中 29 个明确映射为 X；支持的 slash bass 先验证音名语法，再在 majmin 任务中忽略转位。NC→N 是明确约定，所读官方说明没有定义该缩写。未知、拼写异常或未定义的组合后缀不自动修复。首拍到末拍之外不延伸标签，末三行不参与评分。官方说明将重复位置写作点分形式，但实际所选 64 个文件均使用逗号整数对，当前检查针对实际文件格式。

**就绪结论：可执行冻结的两方法外部比较。** 56 个现有核心及 IDMT 测试通过；三个新测试覆盖异常符号、合法转位、首尾范围/元数据和重复时间。全部 64 份标注通过区间及范围检查，运行器语法检查通过。无需更改预测算法或参数。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| idmt.py 原说明：“NC is interpreted as no chord.” | 约定与来源的区分 | 官方所读两节说明了时间和符号位置，没有解释 NC；保留这项约定但不将其归于数据集作者。 | 中 | “interpreted” 已体现解释性质；增加一句即可明确来源范围。 | 改写 | “NC is interpreted as no chord; the dataset guide does not define this abbreviation.” |
| idmt.py 原注释：“Compound numeric suffixes are not defined in the dataset guide.” | 术语范围 | 13 等常规符号与 79、713 等组合后缀需要区分；官方说明未给和弦词表。 | 低 | 原句可理解，但举出具体后缀更易核对转换表。 | 改写 | “The guide does not define the chord vocabulary. Map the conventional spellings below; combined suffixes such as 79 remain X.” |
| external_compare.py 原检查：“Both configurations must be frozen before evaluation” | 复现条件不完整 | status=frozen 本身不能保证输入仍是约定的 8192 基线和 4096/8192、w=0.2 候选。 | 中 | 提示文字正常，但需要相应实现检查支撑精确比较范围。 | 改写 | 增加共享参数、候选窗口/权重、调音政策、64 个唯一 piece ID 和指定 capture stream 检查。 |
| external_compare.py 原 `sources.json` 仅保存代码哈希 | 复现证据不完整 | 哈希能辨认版本，但不能独立恢复源码和软件环境；推断前还需保留实际标注范围。 | 中 | 哈希记录是正确做法；补齐源快照和环境，而不是将其误称为完整复现包。 | 改写 | 增加 source_snapshot、environment.json、输入验证副本，以及包含 N/支持和弦/不支持标签时长的 annotation_audit.json。 |
| external_compare.py 的 chord-only 诊断 | 评价含义 | 主指标继续包含 N；诊断通过把参考 N 改为 X 排除该时长，不改变预测结果。 | 低 | 这是清楚、可核验的分母说明，应保留。 | 保留 | 保留主指标与 chord-only 诊断的区别。 |

## 三、综合建议

改动均已保存于隔离草稿：补充 NC 的来源限定、冻结协议检查、代码/环境快照和推断前标注审计，并核对解码音频时长与文件头一致。原始识别、Viterbi、总体/区域评分和两种配置的数值设置没有改变。测试文件未修改。

推断前元数据核对结果保存在 `idmt_preflight.json`：首末拍范围总计 1627.939297058 秒，其中支持和弦 1180.545555553 秒、N 151.835147395 秒、不支持参考 295.558594110 秒。该统计只解释参考分母，不含任何模型效果信息。论文中无需搬入完整审查日志；说明映射规则、覆盖率、NC 约定和 chord-only 诊断即可。实际阅读深度仅为上述指南章节和所选文件格式，未声称主观听验对齐或已获边界精度保证。

**发现的写作特征不能证明文本由 AI 生成。**
