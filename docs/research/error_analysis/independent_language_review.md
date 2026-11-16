# Final progress-report language and evidence review

## 一、整体观察

审阅范围：当前 `README.md` 全文、`report/progress_report.tex` 和 `report/results.tex`，重点核对本轮新增的误差分解、NC 能量诊断、讨论和后续计划。数据依据为 `results/error_analysis/{guitarset,idmt}/summary.json`、逐录音结果、混淆矩阵，以及 `results/nc_diagnostic/summary.json`。此前已逐行核对 738 条区域记录，最大数值差异为 7.11×10⁻¹⁵ 秒。本轮未重新审读原有 Related Work 的各篇论文，也未重复全套测试。

已应用 `academic-language-audit` 和指定的 `nature-writing`，沿用 manuscript / methods / en / generic，并补读 Discussion、讨论语言校准和正文压缩指导。新增内容以结果为中心，没有将分析过程、审查清单或失败尝试展开成长篇说明。未发现阻碍交付的科学问题；建议修正两处轻微歧义。

数字核对结果：

| 指标 | GuitarSet | IDMT |
| --- | ---: | ---: |
| Different-root 占总错误时长 | 89.3368% → 89.3% | 61.1655% → 61.2% |
| Reference N error 占总错误时长 | 0% | 32.8176% → 32.8% |
| Stable 占总错误时长 | 76.4656% → 76.5% | 68.7837% → 68.8% |
| Near 区域错误率 | 41.0190% | 51.3416% |
| Stable 区域错误率 | 23.5973% | 29.7748% |
| Stable 占评分时长 | 84.9576% | 79.1644% |

NC 的 207 段、32 个录音、151.84 秒、中位相对 RMS −28.09 dB 和 1.31% 阈值命中率均与输出一致。NC 与和弦区间的能量分布重叠是当前描述性结果，没有被写成声音类别判断或阈值优化结果。PDF 文件头确认四页 A4。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| `report/results.tex`，`DiscussionResults` 首句：“but neither fixed comparison favours it overall” | 含义轻微歧义 | 本文同时使用 fixed fusion 作为方法名，fixed comparison 容易被读成只讨论这一方法；实际指冻结设置下的比较。 | 低 | 可以理解，但本项目术语环境使其有歧义。 | 改写 | “Fusion can help or hurt locally (Figure~\ref{fig:example}), but it improves neither dataset's overall accuracy under the frozen settings.” |
| `report/results.tex`，`DiscussionResults` 第二段：“Errors are more frequent near reference changes, yet stable regions contribute 76.5\% and 68.8\% of total error duration because they occupy most scored time.” | 统计量与解释措辞 | 测量的是错误时长比例，而非错误事件频次。两类区域的时长与错误率共同决定错误总量；直接列出量的关系更清楚。 | 低 | 原句并未断言声学因果，但可以更准确。 | 改写 | “Error rates are higher near reference changes. Stable regions occupy most scored time and account for 76.5\% and 68.8\% of total error duration, respectively.” |
| 同段：“This temporal breakdown does not identify an acoustic cause.” | 证据边界 | near/stable 仅依据参考标签边界定义；不能将 near 错误直接归因于估计边界偏移。 | 低 | 是，直接防止对本项统计的误读。 | 保留 | 保留原文。 |
| `report/results.tex`，`ExternalDiscussion`：“Their energy distribution overlaps that of chord-labelled intervals.” | 描述性结论 | 与时长加权 RMS 分布和分位数一致；后句仍明确 NC 未定义，未声称噪声、余音或旋律已被听辨。 | 低 | 是，当前证据足以支持分布描述。 | 保留 | 保留原文。 |
| `README.md`，Follow-up experiments：“different-root predictions account for 89.3% ... and 61.2% ... reference N errors ... 32.8%” | 指标分母 | 文中明确以 baseline error duration 为分母；图中以 scoreable duration 为分母，并在图注中说明，两者没有混用。 | 低 | 是，正文比例和图形比例回答不同的简洁问题。 | 保留 | 保留原文。 |

## 三、综合建议

只需处理表中两处歧义，无需扩大正文。保留当前讨论顺序：冻结比较未见收益 → 不同根音及 N 错误的构成 → 区域差异 → NC 声学含义尚待回放检查。听验被明确列为后续工作，未冒充已完成的主观判断。

Related Work、本轮未改动的旧实验数字和 70 项测试状态不在此次独立复验范围；它们沿用项目原记录。新增分析不构成新的泛化改善，也未改变原模型分数。四页报告结构保持简练，没有新增文献来装饰诊断结果。

**发现的写作特征不能证明文本由 AI 生成。**
