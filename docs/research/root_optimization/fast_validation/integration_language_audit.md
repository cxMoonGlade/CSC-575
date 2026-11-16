# 快节奏验证整合：语言审查

## 一、整体观察

审阅范围为主 README 的根音实验与排期修改、results 两级索引、研究索引、评估脚本 README、六项测试的导入修改，以及独立数值检查脚本的说明和输出字段。旧文取自 November 9 项目文件；新稿位于本次 `integration_draft/`。报告与图形另有专门审查。数值依据为完整 384 行结果及独立重算，不涉及重新运行或挑选模型。

使用 academic-language-audit 与用户指定的 nature-writing。沿用 manuscript / research / experiments and discussion / en / generic 路由及已读取的核心指导。按“方法—结果—适用范围”组织，保留精度和完整处理时间；哈希、运行顺序和下载细节放在复现记录。课程格式优先，不套用 Nature 的篇幅或投稿规则。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 旧主 README，Root-error experiments：“This ceiling leaves improvement on new chord progressions unresolved.” | 新旧结果关系 | 孤立片段仍为天花板，但已完成相同曲目的快速版本验证；不能把它写成新曲目。 | 高 | 是，原句对旧实验成立；当前应补新证据。 | 改写 | “These are faster versions of the same pieces used in the earlier slow-tempo comparison, so they test transfer within that repertoire.” |
| 新主 README，结果表后：“Chord accuracy includes reference `N`; root accuracy excludes it.” | 指标分母 | 主指标为 1,063.79 秒，根音为 936.94 秒；59 段有主指标，58 段有根音指标。 | 高 | 是，防止把无和弦识别当成根音改善。 | 保留 | 保留原文，完整样本数在结果摘要说明。 |
| 新结果摘要，Fast-tempo recordings：“NNLS has a slightly better root score, but more same-root major/minor errors: 37.67 seconds versus projection's 27.41 seconds.” | 结果解释 | 依据同一批已保存区间的误差分解；不推断具体声学原因。 | 高 | 是，解释根音与完整标签的不同排序。 | 保留 | 保留原文。 |
| 新主 README：“Direct projection is the preferred option for the current guitar workflow” | 推广范围 | 主指标 +3.10 点，根音 +4.41 点，完整成本约 +10%；同时明确原命令默认值和新曲目未测试。 | 中 | 是，限定工作流的工程选择，不称为普遍最优。 | 保留 | 保留原文。 |
| 新结果摘要：“Projection improves 30 scoreable recordings, ties on 13 and worsens 16.” | 分布和不利结果 | 对全部 59 段有定义的主指标比较；没有仅报告正例。 | 中 | 是，简短说明平均改善的非均匀性。 | 保留 | 保留原文。 |
| 旧研究索引：“The `[search tree](arbor/status.txt)` ends with the original baseline” | 不同实验混淆 | 该树只含 11 月 9 日孤立片段，不能以新快速片段 67.80% 与原 100% 比较。 | 中 | 是，需增加历史范围。 | 改写 | “The November 9 `[search tree](arbor/status.txt)` ends with the original baseline” |
| 评估 README：“Six focused checks cover N-aware root scoring...” | 复现定位 | 六项合成测试保持原逻辑，导入改为项目内命名空间；命令改为根目录执行。 | 低 | 是，具体说明测试覆盖而非空泛可靠性承诺。 | 保留 | 保留原文；使用 `.venv/bin/python -m pytest tests/test_root_validation.py -q`。 |

## 三、综合建议

正文保留三方法的主要指标、根音指标和完整处理时间，错误细分与选例放在结果说明。元数据验证、下载策略及逐项数值检查不扩入四页报告。快慢数据使用相同曲目 ID，不声称独立新曲目或未见和弦进行的泛化。图形为事后最大增益和最大损失选例，须同时标注低覆盖率。

比较脚本的原注释、协议及测试说明已经单独审查；整合只改变测试导入和文档中的复现路径。独立检查脚本保持为原会话快照，绝对路径不伪装为通用命令。没有新增论文结论，也未新增机制归因。

发现的写作特征不能证明文本由 AI 生成。

排期一致性补充：README 的 11 月 15–26 日工作改为错误分析和寻找新曲目；未见进行的验证列入 advanced，与报告的目标层级一致。没有把新曲目实验写成已完成结果。

复现说明补充：图形命令使用项目模块路径，从已保存区间重新绘图；无需运行模型。研究目录的会话检查脚本保留原绝对路径，与通用评估命令区分。
