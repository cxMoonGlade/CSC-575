# NC diagnostic writing review — 2026-11-09

## 一、整体观察

审阅范围：新 `chordrec/nc_diagnostic.py` 的说明、注释、图表标签及 `results/nc_diagnostic/README.md`；对照冻结解码器、逐区间 CSV、汇总 JSON 和标注审查。使用 academic-language-audit 与 nature-writing，沿用 manuscript / research / experiments、discussion / en / generic。核心判断限于已测能量与现有门限，不把 NC 当作已确认的静音。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| README 第 2 段：“Just 1.31% of reference `NC` duration meets this rule.” | 数值与定义 | 1.994693874 / 151.835147395 秒；分母是时长，非区间数量。 | 低 | 是，直接描述已有结果。 | 保留 | 保留原文。 |
| README 第 3 段：“These distributions overlap.” | 证据边界 | NC 与支持和弦的时长加权 RMS 分布相交；该观察未给出最优分类器或泛化结论。 | 低 | 是，随后的声学解释限制清晰。 | 保留 | 保留原文。 |
| README 播放说明：“This is an inspection aid; no listening judgements have yet been recorded.” | 证据边界 | 浏览器播放检查不等同于听觉分类；不得将波形或 RMS 判断写成亲耳观察。 | 低 | 是，区分交付工具与待做的主观判断。 | 保留 | 保留原文。 |
| `weighted_quantiles`：“Return inverse empirical-CDF quantiles with duration weights.” | 方法说明 | 排序后取累计权重达到目标分位数的第一个值；与实现一致。 | 低 | 是，定义了分位数约定。 | 保留 | 保留原文。 |

## 三、综合建议

主文只保留 NC 检测不足及下一步检查所需的事实；完整分位数、源码校验和源文件哈希留在诊断目录。保持 NC（原标签）、N（评分类）、RMS（能量）三者的区别。已记录分布不能证明 NC 是静音、标注错误，或某个新门限有效。未新增论文主张。发现的写作特征不能证明文本由 AI 生成。

Nature 写作记录：本次沿用既有术语表。诊断方法与分位数表置于结果附件，报告只需一句解释；播放器说明只介绍操作与样本选择。未改变识别参数、输出标签或评估分母。
