# Language and evidence review before integration

## 一、整体观察

审阅对象为 `/tmp/chordrec_candidate/README.md`、`AGENTS.md`、`chordrec/tune.py`、`regions.py`、`report_figures.py`，以及新增的 `notebooks/listen.ipynb` 和 `results/README.md`。README 与说明文字全文审阅；脚本只修改文档字符串、注释和一个图中文字。定位行号采用修改前版本，副本保存在 `/tmp/chordrec_candidate_pre_language_audit/`，前后 SHA-256 见 `language_audit_checks.json`。

使用了指定的 `academic-language-audit` 和 `/home/cx/AI_QEC/AI_QEC/.agents/skills/nature-writing/SKILL.md`。后者加载 manifest 1.6、全部 core、对应方法/实验/英语/generic 片段及 main-text-discipline；目标仍是 ISMIR 课程进度报告。

数字逐项对照冻结测试的 `summary.json`、`per_recording.csv`、`regions/region_summary.json`、`activation.json` 和开发选择记录。59 条录音共 32.37698 分钟；覆盖率 74.0546%；两条录音无可评分区间。表格四类数字均与记录的两位小数一致。12/83,694 帧触发高短窗权重，即 0.0143379%，支持文中的 0.014%。没有修改实验结果或选择规则。

未发现阻止整合的数值或结论错误。主要改动是澄清计时含义、首次出现的缩写、所有前端共有设置，以及常数融合与自适应融合的比较范围。没有重新通读引用论文；本轮文献判断沿用既有审读记录。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README L40：“complete audio-to-label CPU time” | 计时术语不够精确 | 实现用 `time.perf_counter` 测经过时间，包含 I/O；读者可能把 CPU time 理解成进程实际占用 CPU 的时间。 | 中 | “CPU runtime” 常用于说明运行设备，但这里可更精确。 | 改写 | “audio-to-label wall-clock runtime on the CPU” |
| README L22：“They share … CQT chroma provides another representation.” | 共有条件指代不清 | “They” 紧接两个 STFT 前端；实际 CQT 也使用相同调音、音高范围、音级顺序和归一化。 | 中 | 原句是正常技术描述；问题是比较条件没有明确涵盖第三种表示。 | 改写 | 先介绍 STFT 与 CQT，再写 “All three share a tuning estimate, MIDI pitch range 36–95, C-first pitch-class order, and per-frame L2 normalization.” |
| README L34：“A staged search … adaptive threshold/radius.” | 选择目标略简、斜线表达含糊 | 配置记录表明采用有限网格，选择依据为开发集时长正确率。近边界正确率是诊断，不是选参指标。 | 中 | README 可将完整网格留在链接中；仍应说明优化了哪个指标。 | 改写 | “A staged grid search used development-set duration accuracy to select the common switch penalty, a constant fusion weight, and the adaptive threshold and radius.” |
| README L50：“behaving almost like a constant 0.2 mixture. Neither fusion improves …” | 指代与观察层级 | 一共讨论等权、选定常数和自适应三种融合设置。“behaving” 未明确指特征权重还是解码结果。 | 中 | 使用 “almost” 有实际帧比例支持，不属于无证据夸大；应把观察对象说清。 | 改写 | “The selected adaptive rule assigns short-window weight 0.8 to 0.014% of test frames and 0.2 elsewhere. None of the fusion settings improves overall or near-change accuracy over the long window in this comparison.” |
| README L16、40、105：一个测试进行家族、两个零覆盖录音、bootstrap 尚未完成 | 必要证据边界 | 这些信息直接决定录音数量和准确率分母的解释，也决定 advanced PI 的状态。 | 低 | 属于必要研究条件，不能作为“防御性文字”删除。 | 保留 | 保留原意与数字。 |
| README L82：“evaluate revisions on additional held-out material” | 后续资源状态不明确 | 目前已用完预定测试集，额外材料尚未取得。 | 低 | 工作计划可以提出目标，但不宜让读者误以为额外测试材料已经在手。 | 改写 | “Investigate the change detector and obtain new held-out material to evaluate revisions.” |
| AGENTS L3：“Before changing files intended for GitHub, apply both writing skills” | 工作步骤说明可更明确 | 需要把文字审查应用到拟整合变更，同时保留算法开发与语言编辑的区别。 | 低 | 原规则清楚表达用户要求；新句仅明确审阅对象和整合时点。 | 改写 | “Before integrating any file change intended for GitHub, apply both writing skills to its proposed prose, comments, docstrings, and displayed labels:” |
| report_figures.py：图中文字 “24 chord templates + energy N” | 图中文字缩略不自然 | N 是能量规则赋予的标签，不是名为 “energy N” 的技术对象。 | 低 | 图内缩写正常，但应使用已有术语。 | 改写 | “24 triad scores and N rule” |

| listen.ipynb 第 1 格：“largest adaptive improvement … includes all 59 test recordings” | 案例选择和评分范围不够明确 | 两条录音没有可评分时长，案例只从其余 57 条中选择；改善幅度相对开发阶段选定的长窗基线。两个极端案例的覆盖率分别为 37.51% 和 87.50%。 | 中 | 原句没有直接声称 59 条均有准确率，但在演示入口补齐选择范围有助于解释案例。 | 改写 | 指明相对长窗的解码结果差异、57 条可评分录音、事后选择和两个案例的覆盖率；保留总体结果含全部 59 条。 |
| results/README：“Each completed run contains … timestamped predictions” | 文件范围过宽 | 参数选择目录含候选汇总和选择记录，不含与三个识别运行相同的预测文件树。 | 中 | 通常可把 run 当作识别运行；本表同时列出选参过程，应消除歧义。 | 改写 | “The three recognition runs contain …” |
| README 运行说明；notebook 和 results guide：“fixed … weight is zero” | 复现操作与权重指代 | notebook 指定 `chordrec` kernel；新环境需要注册或选择 `.venv`。固定权重指短窗贡献。 | 低 | 原表述技术上可理解，但明确命名降低首次运行的负担。 | 改写 | 增加环境内 kernel 注册命令及选择说明；使用 “fixed short-window weight”。 |

## 三、综合建议

本轮修改以明确比较条件和测量对象为主。README 保留总体/近边界准确率、边界 F1 和运行时间，也保留融合未优于长窗的结果；没有用边界 F1 的微小差异替代原研究问题。性能表仍是数字的主要呈现位置，参数搜索完整记录与逐录音结果继续留在链接文件。

整合前需完成两项文件状态核对：生成并检查最终四页 PDF；确认 README 中报告、图和播放文件的相对链接存在。按任务约定，O2-PI4 的“本次进度报告已完成”将在 PDF 完成后随候选一并整合；它没有把最终报告误报为全部结束。

Python AST 比较确认，除文档字符串及所列图中文字外，脚本语句、计算和数据处理没有改变。README 的数值集合保持不变；仅在权重诊断句中再次明确了方法已定义的 0.8。完整检查结果位于 `language_audit_checks.json`。新增 notebook 的代码格及输出均保持不变；参数选择计数 52 与记录一致。复现指南中的 `--run`、`--output`、`--baseline` 及选参命令参数均已逐项对照代码定义。

**发现的写作特征不能证明文本由 AI 生成。**
