# Repository publication: code, experiments and results language audit

审阅日期：2026-11-16。工作副本：`/home/cx/Documents/csc475/CSC-575`。未修改原始 `Proj`，未提交或推送。

## 一、整体观察

实际审阅范围为 `chordrec/`、`tests/`、`experiments/`、`results/` 和 `notebooks/`。已读取两个指定技能及 Nature writing 的 manifest、全部 always-load 核心文件，以及 manuscript、research、method、experiments、English、generic 片段；另使用 shared main-text-discipline 与 discussion-argument-language 检查证据位置、重复与解释范围。沿用已确定的项目范围，不重新构造论文论点。路由为 manuscript / research / method + experiments / en / generic，按仓库说明文字的规模应用，未套用期刊投稿要求。

完整阅读了 18 个 Markdown 文件（16 个不同内容）、141 个 Python 文件经 SHA256 去重后的 56 个版本中的 docstrings、注释、帮助信息及显示文字；另补读了短字符串中的图例与标签。重复源码仅在字节哈希一致时复用审阅。完整阅读了 1 个 notebook 的 Markdown、代码和原有输出说明，以及 5 个 HTML 页面的可见文字、无障碍标签和生成器中的动态提示。HTML 内嵌音频和数据载荷未作为语言材料读取或改写。

493 个 JSON 文件均解析并提取字符串，得到 561 个不同的含空格文本，其中 352 个为路径，209 个为非路径说明、计划、标签、运行条件及解释文字，已阅读其上下文字段。计划中明确标为 hypothesis 的陈述保留为实验前假设。3990 个 CSV 为机器生成的数值或时间标签记录，本轮未逐行重验；没有修改其内容。10 个 PNG 和 7 个 PDF 的可见标签通过生成器阅读，本轮没有逐一进行视觉复核。唯一 TXT 是历史搜索树的终端摘要，已阅读并保留。

主要问题是当前入口仍将旧 GuitarSet 测试视为本版报告内容，以及已评估材料的标题和使用范围可能让读者误解。技术说明总体具体，成本条件、数据分组和探索性范围较清楚，没有为润色而改变模型、算法或测量结果。

术语沿用项目约定：Long STFT、fundamental-only NNLS、projection、duration-weighted chord accuracy、root accuracy；源代码标识符、历史方法键和冻结计划中的原用语保留。当前报告使用的方案名称不通过批量替换改写原始结果。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `results/README.md` 原第 14 行：“The test comparison is reported in [the progress report]…” | 版本一致性 | 当前报告已不再展示原 GuitarSet 测试比较。该入口会将读者引向不含该表的 PDF。 | 中 | 句式正常，但指向的报告内容已变化。 | 改写，已应用 | “The original GuitarSet test comparison remains here as a historical experiment. The current … progress report … focuses on the development comparisons and the fast-tempo IDMT results.” |
| `results/README.md` 保存实验说明后的新增定位句 | 历史记录与当前命令的区分 | 冻结计划和快照保留当时的路径、解释与前瞻性措辞；可运行入口另在实验 README。 | 中 | 是，说明不同版本文件的用途。 | 改写，已应用 | “Archived plans and source snapshots describe the experiments as run. The linked experiment READMEs give current reproduction commands.” |
| `results/root_optimization/README.md` 原小节标题：“Fresh isolated chords (88)” | 时间与状态含糊 | 比较已完成；fresh 在脱离历史语境后可能读成尚未评估。 | 低 | 可以作为当时的新材料描述，但不适合作为当前状态标题。 | 改写，已应用 | “Isolated-chord comparison (88)” |
| 同文件 fast-tempo 节末：“This evaluated set is now reserved for fixed-result reproduction; later changes need separate validation.” | 使用范围与计划一致性 | 当前方案允许在独立开发材料上校准后，明确标注为探索性的重评；原句容易被读成连这种重评也不允许。 | 中 | 禁止用测试结果调参的原则合理；绝对限定为复现过窄。 | 改写，已应用 | “The evaluated set must not be used to select parameters. Reassessment after calibration on separate development data remains exploratory; claims about new repertoire require separate held-out recordings.” |
| `notebooks/listen.ipynb` Markdown cell 0：“For the two cases discussed in the report…” | 版本一致性 | 指的是旧自适应融合案例，不是当前报告的 projection 示例。 | 中 | 原版本下正常；当前关联已过期。 | 改写，已应用 | 标题改为 “Original GuitarSet test: listen and inspect”；开头说明这是历史测试，案例写为 “Two selected cases are …”。保留 ID、数量、覆盖率及事后选择说明。 |
| 同 notebook，code cells 1、3、4 的已执行输出 | 发布材料冗余 | 包含内嵌音频、旧图及本地绝对路径；静态图与保存文件逐字节相同，预测与汇总仍在结果目录。 | 低 | 执行输出是正常 notebook 用法，但这里没有唯一证据。 | 精简，已应用 | 清空 outputs 和 execution_count，保留全部代码与 Markdown（仅 cell 0 更新）。 |
| `experiments/root_projection/README.md`：“The 0.34-percentage-point gap therefore measures the additional benefit of joint fitting under these fixed settings.” | 条件与证据范围 | 紧邻独立拟合与共同字典的定义，并限定相同设置；没有推成普遍优势。 | 低 | 是，属于条件明确的开发比较。 | 保留 | 保留原文。 |
| `experiments/root_harmonic/README.md`：“This comparison supports testing the note representation further; it does not support attributing the improvement to harmonic removal.” | 机制边界 | 基频控制优于带泛音模型；原句防止将模型名解释成已证实原因。 | 低 | 是，限定直接影响研究解释。 | 保留 | 保留原文。 |
| `chordrec/diagnostic_player.py` 与 5 个 HTML 的播放、参考类别及来源标签 | 显示文字 | 标签明确区分 scoreable chord、N、unsupported 和 unannotated；区间播放文案对应现有功能，没有 CSV 导出按钮的虚构说法。 | 低 | 是，简短功能说明适合演示。 | 保留 | 保留原文及全部 HTML 字节。 |
| 冻结 `results/optimization_v2/hypothesis_tree/tree.json` 的 n2 insight：“The fixed local-median whitening suppresses useful spectral balance in this setup…” | 历史解释的证据边界 | 保存结果只直接显示准确率下降，不能独立确定被抑制成分的声学作用。这是历史搜索记录中的推断，并非当前报告结论。 | 中 | 作为当时解释可以记录，但不应当作已证实机制引用。 | 保留历史记录；后续引用时核实 | 冻结记录保留原文；当前 README 仅报告 whitening 的准确率变化，未采用此机制解释。 |
| 冻结配置及旧 JSON 计划中的 “selected64”、 “on119development recordings” 等 | 局部可读性 | 缺少空格；改写受哈希约束的配置或计划会破坏原比较的来源验证。 | 低 | 否，是历史记录中的排版问题。 | 保留历史字节；当前说明使用正常间距 | 本轮不改冻结记录；入口已解释其历史性质，准确的当前说明见对应 README。 |

## 三、综合建议

本轮只修改 `results/README.md`、`results/root_optimization/README.md` 和 `notebooks/listen.ipynb`。历史结果数值、原始配置、计划、源码快照以及所有当前 Python 代码保持不变。对 141 个 Python 文件和 493 个 JSON 文件重新计算哈希，均与审阅开始时一致。两个 README 的数字序列不变；notebook 的全部代码单元与原文件一致，保留了原案例数据与选择范围。原 notebook PNG 输出与 `results/test_frozen/examples/00_BN3-119-G_comp/timeline.png` 逐字节相同，因此清除输出未删除唯一图像证据。

这轮没有搬移或新增数值结果：结果表保留，历史计划仍在原目录，当前入口只修正其定位。按空白分词，`results/README.md` 从 282 词变为 316 词，`results/root_optimization/README.md` 从 891 词变为 903 词。新增文字用于说明版本和使用范围，不将完整审计过程放入项目说明。

当前入口应继续区分原测试、开发比较和探索性诊断。新增解释不能把单曲或开发集观察写成已证实机制；计时继续标明是否含音频加载、特征构造与解码。已评估数据不用于选择参数，独立校准后的重评需明确其探索性质。

本轮未重新运行音频识别、联网核验文献或重新确认原审读笔记的论文内容。已存在的 Mauch and Dixon 阅读审计保留为历史记录；不能将其写成这轮独立审读结果。这些目录主要记载项目方法和运行结果，没有新增需 overview 支撑的领域综述。仓库全文的综述引用检查由报告审查负责。

未完成或不在本轮范围：逐一检查 10 个 PNG、7 个 PDF 的最终显示；历史冻结 JSON 的排版与个别推断措辞仍按原始记录保留，不能声称全部原始文件已被改写。正式发布前，主代理需完成全局文件集、数据许可、链接和 PDF 检查。本代理不修改或推送冻结记录来消除这些历史差异。

清单及哈希保存在 `/tmp/csc575-code-audit-inventory.json`；实际阅读提取保存在 `/tmp/csc575-code-prose.txt`、`/tmp/csc575-json-prose.txt` 和 `/tmp/csc575-json-narrative-prose.txt`。这些是本轮审查工作文件，不要求发布。

发现的写作特征不能证明文本由 AI 生成。
