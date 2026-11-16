# Report update — 2026-11-09

## 一、整体观察

审阅范围：README 新增误差分析段落和时间表；报告 Discussion、Individual Progress、Remaining Work、误差图及测试数量。逐项对照 `results/error_analysis/` 和 `results/nc_diagnostic/`，未重新评价原有文献。已应用 academic-language-audit 和 nature-writing（manuscript / research / experiments、discussion / en / generic）。报告继续以多分辨率比较为主，新增分析解释现有系统错在哪里，不宣称准确率提高。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| 修改前 Remaining Work：“separating chord-identity, boundary and no-chord errors” | 证据边界 | 新分析划分参考变化附近与其他区域，不能证明错误由边界偏移造成。 | 高 | 原文作为计划合理，但不适合作为已完成分析的描述。 | 改写 | “inspect the measured error categories by listening and complete their analysis in the final report” |
| 修改前 ExternalDiscussion：“listening and annotation review should establish what those passages represent” | 进度一致性 | 标注格式和能量分析已完成，主观声学判断尚未完成。 | 中 | 原计划合理，需要随进度更新。 | 改写 | “The annotation guide leaves NC undefined; interval playback now supports checking its meaning before revising no-chord detection.” |
| 修改后 Discussion：“Stable regions occupy most scored time and account for 76.5% and 68.8% of total error duration, respectively.” | 分母与解释 | 该区域占总可评分时长约 85% 和 79%。前句同时说明 near 的错误率更高。 | 中 | 是，明确区分错误时长占比与错误率；不把位置解释为声学原因。 | 保留 | 保留原文。 |
| 修改后 Discussion：“Different-root predictions account for 89.3% ... and 61.2%” | 定义一致性 | 分母是全部错误时长；图中分母则是可评分时长，轴标题和图注已另行注明。 | 低 | 是，两种分母各有用途且可核算。 | 保留 | 保留原文。 |
| 修改后 Discussion：“Their energy distribution overlaps that of chord-labelled intervals.” | 证据边界 | 时长加权 RMS 累积分布支持重叠；未据此选取新门限或推断声音内容。 | 低 | 是，保留声学含义待听验这一直接限制。 | 保留 | 保留原文。 |

## 三、综合建议

保留原比较分数和有限域已放弃后的当前项目范围。将完整混淆矩阵、分位数、源文件哈希和逐条标注审查留在研究与结果目录。报告使用一张误差构成图替换方法流程图；流程已在方法文字与公式中说明，原图仍保留在仓库。两项写作技能均未改变模型或评分。发现的写作特征不能证明文本由 AI 生成。

Nature 写作记录：术语沿用既有 ledger，新增 other root（支持和弦之间根音不匹配）及 stable（可评分时长中，去除参考变化 ±0.2 s 邻域后的部分）。证据链为：融合未改善冻结比较 → 根音与 N 错误占比 → 能量与 NC 含义待核对 → 用区间播放进行下一步检查。原流程图转为仓库材料；误差构成图进入正文，RMS 图与分位数表留在诊断说明。未重复追加原有实验分数。
