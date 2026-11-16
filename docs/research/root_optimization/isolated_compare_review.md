## 一、整体观察

完整审阅 `/tmp/chordrec_root_v1/isolated_compare.py` 草稿及其调用的 `recognize`、`decompose`、`prediction_intervals` 和 harmonic 特征提取代码；同时核对 88 份 XML、音频文件头、全部 176 个输入哈希和冻结选择。没有运行音频特征或识别模型。复用 academic-language-audit 与 nature-writing 的既定指导，Nature 路由仍为 manuscript / methods / method + experiments / en / generic。

主指标按参考区间精确累计 major/minor 正确时长。根音正确时长为完整和弦正确时长加“同根音、错误质量”时长；预测 N 算错误。手工构造的 2.3 秒参考区间验证了 1.0 秒完整正确、1.5 秒根音正确、0.3 秒其他根音及 0.5 秒 N 错误。两种方法均从加载音频计时到解码区间完成，NNLS 字典构造与求解包含在候选成本中。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| runner 的 `inputs.json` 保存当前文件哈希 | 冻结输入验证不足 | 保存当前哈希可以追溯一次运行，但不会发现冻结后、运行前的文件漂移。当前全部文件与冻结清单一致。 | 中 | 哈希记录本身合理；还需与冻结清单比较。 | 改写 | 推断前对照 `validation_manifest.json` 中的选择和 176 个输入哈希。 |
| runner：“Each of the 44 chord groups must contain two instruments” | 检查与表述不完全一致 | 代码只检查每组有两条记录，没有检查两种指定乐器各一条。当前数据实际满足两乐器配对。 | 中 | 这是合理约束，但实现需支持提示所说的条件。 | 改写 | 对每个 group_id 检查两种预期 instrument 各出现一次。 |
| runner 的 `Path(__file__).parent.glob("*.py")` | 源码快照范围 | 在 chordrec 目录执行可覆盖实际本地依赖；直接执行临时草稿只保存临时目录的 Python 文件。 | 中 | 集成后的写法合理。 | 保留 | 先集成到 chordrec，再运行；保存准备好的音频、标注和编号映射。 |
| isolated.py 原文：“Return the triad over the union of annotated note durations.” | 数学范围不准确 | 实现返回最早 onset 到最晚 offset 的一个连续区间；一般情况下不等于多个音符区间的集合并。 | 中 | 在本数据可能近似同义，但应直接描述实现。 | 改写 | “Return the triad from the first note onset to the last note offset.” |

## 三、综合建议

推断前补齐冻结文件验证和指定乐器配对检查。根音与 major/minor 指标、raw/Viterbi 分离、完整方法计时、44 配对组及孤立和弦范围都与既定计划一致。根音指标在本数据的分母为支持的和弦时长；适配器不会引入参考 N。

适配器只改了一句 docstring，已验证移除 docstring 后的 AST 完全相同；旧冻结清单保持不变，新旧源码哈希保存在 `isolated_adapter_provenance.json`。进一步用当前适配器重读全部 88 份 XML，参考区间和标签与旧冻结清单完全一致。相关数值检查保存在 `isolated_compare_review.json`。

**发现的写作特征不能证明文本由 AI 生成。**
