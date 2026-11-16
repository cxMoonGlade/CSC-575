# 一、整体观察

审阅范围：`README_draft.md` 的全部重现步骤、更新后的 `/tmp/chordrec_root_fast/figures.py` 全部源代码，以及 `figures_final/error_cases.png`、PDF 和案例选择记录。PNG 已实际目视检查。Nature 路径采用 manuscript / methods / experiments / en / generic，固定术语为 fast-tempo comparison、frozen selection、saved interval predictions。README 区分完整 ZIP 重现路径与原会话的局部范围下载记录；未执行新下载。

图形脚本只读取已保存的逐录音结果和区间 CSV，并用既有 `reduce_label` 映射展示标签。没有音频读取、特征提取、识别器调用或模型修改。它在可评分且有两种方法结果的录音中，选择 projection 减 long 的准确率差值最高和最低的两例；零可评分录音只排除于例图选择，保存排除理由。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README 首段 “They share the 64 piece identifiers of the earlier slow-tempo comparison.” | 证据边界 | 输入清单的两个64元素集合完全相同；新速度演奏不等于新曲目 | 中 | 是，解释验证范围所必需 | 保留 | 保留原文 |
| README 最段 “It contains absolute local paths and requires the cached ZIP directory” | 可重现性 | 原脚本固定 ROOT/WORK/CACHE；没有伪装成通用安装入口 | 中 | 是，准确区分归档和可移植步骤 | 保留 | 保留原文 |
| figures.py 保存规则 “Post-hoc illustrations: largest and smallest ... differences” | 选择透明性 | `pairs.sort` 后取最后和第一项，确为结果出来后的极端差值选择 | 中 | 是，避免将极端案例当随机代表 | 保留 | 保留原文；正文图注也应写 post-hoc largest/smallest gains |
| figures.py `selected=[('Largest increase',pairs[-1]),('Largest decrease',pairs[0])]` | 显示一致性 | 实际最高差值 jazz_5 为 +47.37065 个百分点，最低 rock_6 为 −22.53056 个百分点；当前标题方向正确 | 低 | 是，清楚标记事后极值案例 | 保留 | 保留原文；若以后用于全零差值数据，应改用 “No change” |
| figures.py 区间标签 `None`→X、`N`→N，minor用斜线 | 图形解释 | 保留不支持标签与 N 的区别，空白区间对应无标注；主图注应给出必要图例 | 低 | 是，适合简洁示例图 | 保留 | 建议图注短句：“Cross-hatching marks unsupported reference chords; diagonal hatching marks minor chords.” |

# 三、综合建议

README 中的 full-ZIP 路径依赖保存的 selection/input_validation/previous_selection 三份文件；已确认它们位于正式结果目录并与原始记录逐字节一致。提取步骤应验证完整归档 MD5、成员 CRC 与保存的每文件 SHA256；不会重新选择录音或标签。

例图应注明根据已保存结果事后选择最高和最低差值，不能据此说明典型表现。图形记录已经保留案例覆盖率和所有零覆盖排除原因。非阻断性健壮性备注：当前脚本假定 runner 的逐录音结果无重复且配对完整；若以后用于其他 CSV，可另加配对和分母一致性检查。当前主方法与参数不受图形脚本影响。

最终核对读入64条录音的192份区间 CSV（reference、long、projection）。逐文件总时长和逐标签时长在显示合并前后最大差值均为 **0.0秒**，源 CSV 哈希未改变。jazz_5 的参考区间由32段合并为8段，总时长保持19.214013605秒；rock_6 由96段合并为11段，总时长保持48.033015873秒。两例的预测区间数不变。

例图选择与保存结果的最高、最低差值完全一致。jazz_5 覆盖率34.2930%，rock_6 覆盖率86.5460%，应在图注或紧邻的说明中保留，以便理解按可评分时长计算的变化。图中标题、坐标轴和三个轨道标签完整可读，合并后的参考区间减少了无信息分界；交叉线与斜线分别区分不支持标签和小和弦。

总准确率有59条录音可评分，根音/和弦诊断只有58条；jazz_3 只有 N 参考时间。例图使用总体准确率，正确地在59条中选择，且保留5条无总体可评分时长录音的排除记录。

代码与资产哈希、六条实际绘图轨道的合并前后数量和时长、以及正式目录核对均记录于 `final_figure_checks.json`。正式目录复制后，已再次运行 `final_figure_checks.py`：selection、input_validation、previous_selection、evaluation_plan 四份文件哈希一致，runner 与审阅源码一致。完整 ZIP 提取块已通过语法检查，其128个预期文件名来自冻结清单。

本次只审阅和读取保存结果，未重新推理、未修改主方法或图形脚本。发现的写作特征不能证明文本由 AI 生成。

正式目录最终核对：128个音频/标注源文件 SHA256 全部匹配冻结验证清单；192个保存区间 CSV 与原运行结果一致；三个图形资产（PNG、PDF、选择 JSON）与 `figures_final` 完全相同。正式图形脚本与审阅版本相同，重现 README 与草稿逐字节一致，原会话采集脚本存在于声明的归档路径。已检查正式 runner 的 `--help`，所列参数与 README 命令一致。没有执行下载、提取、评分或重新推理。
