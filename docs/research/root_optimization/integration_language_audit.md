# 一、整体观察

审阅范围：新增 harmonic、projection、isolated_compare 模块的注释、文档字符串和提示，以及 README 的根音实验段、实验摘要、结果索引和复现说明。结果依据保存的开发集输出、独立孤立和弦比较及数值复核。沿用 Nature 路由 manuscript / research / method, experiments, discussion / en / generic；课程作业格式优先。

主结论是开发集上的音符表示改进。两种候选尚未获得新和弦进行上的优势证据。代码说明直接描述计算步骤；冻结配置与原始结果保留原字节以便核对来源。报告正文的单独审阅另存。

# 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| root_harmonic/README.md: “The narrower-dictionary interpretation remains to be tested against direct projection before external evaluation.” | 状态过时 | 投影对照与 88 条新录音比较现已完成。 | 中 | 作为先前计划合理，当前说明应更新。 | 改写 | “The completed projection control and isolated-chord comparison are summarized in results/root_optimization/README.md.” |
| harmonic.py: “Each profile sums the magnitudes of separately windowed sine partials.” | 方法范围 | 准确描述字典；它不是声源分离保证。 | 低 | 是，具体且与实现一致。 | 保留 | 保留原文。 |
| projection.py: “Fit each nonnegative profile separately, ignoring profile overlap.” | 方法区别 | 独立投影与联合 NNLS 的区别明确。 | 低 | 是，解释算法而不夸大效果。 | 保留 | 保留原文。 |
| 新 README 表格标题 “Development recordings (119)” | 证据范围 | 候选在此数据上选择；不能写成独立泛化结果。 | 高 | 是，必要的比较条件。 | 保留 | 保留表格样本量并在后文单列孤立和弦结果。 |
| 新结果摘要 “All three decoded methods reached 100%” | 结论范围 | 88 条孤立片段存在天花板，不能据此认为三种方法等效。 | 高 | 是，数值正确，但须解释其判别能力。 | 保留 | “This comparison cannot establish an improvement on chord progressions.” |
| root_optimization/README.md 原复现命令直接使用本地数据目录 | 复现输入缺失 | 新 88 条录音未随源码发布，原文没有从公开来源构造目录和必要清单的步骤。 | 中 | 已有数据的本机运行可用，但不满足新环境复现。 | 改写 | 新增官方 ZIP 下载、MD5 核验、精确目录匹配提取及冻结清单复制；说明运行器会先检查全部 176 个源文件哈希。 |
| 同文件原文：“Use the instructions in that branch's ... README.md with this project's data and development cache.” | 路径指代不明确 | 历史分支不包含 optimization_v2 helpers，且其原 README 使用本机绝对路径；从克隆目录直接照搬会找不到辅助文件。 | 中 | 文字意图合理，但缺少明确工作目录。 | 改写 | 从主项目目录调用克隆目录内的绝对 runner 路径，并指定 `--project-root .` 和上文建立的 cache。 |

# 三、综合建议

保留完整和弦准确率作为主指标，同时报告根音准确率；低音加权的失败结果留在实验记录。开发阶段缓存计时不用于完整速度比较。直接投影和 NNLS 都作为可运行候选保留，原基线仍为默认方法。后续需要尚未评估过的和弦进行，才能判断开发集增益是否转移。

Nature 主文分配：README 保留一张开发集表和一段外部比较；四页报告保留方法公式、结果表及结论边界。参数枚举、读取深度、源码快照、数值核验及搜索树放在实验记录中。发现的写作特征不能证明文本由 AI 生成。

单文件命令与试听链接已加入 README，注释和界面文字另经 `note_cli_language_audit.md` 审阅。示例说明仅指出保存 CSV 中开头的 E:min→C:maj 变化，并标为预先选定的开发集诊断例。结果索引的“All runs use GuitarSet”已限定为原始实验，避免遗漏新增 IDMT 数据。

数据获取说明补审：沿用两项写作技能，仅修改上述实验记录 README 的数据获取与 bass 复现命令。ZIP 大小和 MD5 来自已核对的官方档案元数据；提取通配符与冻结成员表逐项比较，恰好覆盖 88 WAV 和 88 XML。该说明提供完整 ZIP 的复现路径，不把原先的范围下载写成已验证完整 ZIP。没有重新下载音频或执行推断。
