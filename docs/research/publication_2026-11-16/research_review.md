# 研究文档上传前审查 — 2026-11-16

## 一、整体观察

审阅位置：`/home/cx/Documents/csc475/CSC-575/docs/research/`。本轮读取原有 59 份 Markdown 全文，另拟写并复核研究索引；读取 13 个 Python 脚本的文档字符串、注释、提示及图中文字，并读候选引言 TeX 和历史搜索树。正文语言判断以文件内上下文为依据。脚本操作语义沿用已有专项审计，本轮不是完整算法复验。当前项目 README、报告研究问题/方法/讨论及结果表作为事实锚；另读 rock_6 的保存验证记录。

已实际读取用户指定的 `nature-writing/SKILL.md`、manifest、全部 always_load 核心、manuscript/research/method/experiments/discussion/zh-to-en/generic 片段、main-text-discipline 与 discussion-argument-language，以及 `academic-language-audit/SKILL.md`。路由沿用 manuscript / research / method + experiments + discussion / zh-to-en / generic，按研究记录而非投稿主文处理。审计说明留在本文件，不加入报告。

主要问题集中在历史计划的入口：不同日期的方向排序、预期实验及旧报告整合方案，未经说明可能被当成当前承诺。已加短说明及当前入口，保留当时原文。论文记录的六项范围、原文位置、实际阅读深度、作者限制与本项目推断均保留。本轮没有重新阅读外部论文或核验所有外部网页；此前审读记录仍各自承担原文证据，本轮不冒称完成新检索。概括领域背景的来源规则沿用三篇既有综述的审读记录，没有增加需要新综述支持的领域论断。

术语沿用：Long STFT、projection、fundamental-only NNLS、same-root quality error、raw、decoded、source NC、evaluation N。重点保留同根两模板的 7.85 s 与全 24 类正确预测的 5.55 s 区别、−0.00591 的平均分差，以及归一化激活不等于物理音符幅度。没有将校准优先级写成已证实的错误原因。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `root_questions_2026-11-13/README.md`：“最适合继续研究的问题是…不同的时间约束” | 历史建议与当前任务 | 当前报告已采用附加七音和三音强度问题；旧文应保留选题过程但标明时间范围。 | 高 | 是；当时的候选建议有上下文和明确假说，不应改造成已完成结论。 | 改写入口，保留正文 | 首段注明“2026-11-13 的调研与候选方案记录”，链接当前 README，说明后续问题已收窄。 |
| `root_questions_2026-11-13/report_design.md`：“Proposed report text and experiment plan” | 计划状态不明 | 旧 E1/E2 包含不同校准安排和 RMS 措施，不再是当前执行协议。 | 高 | 是；草稿保存合理，但需要版本说明。 | 改写入口 | “Archived draft from 13 November 2026… The current project plan supersedes the research question and experimental controls below.” |
| `research_questions_2026-11-15/research_questions.md`：“当前四页报告仍保留现有研究问题” | 时间指代 | 该句描述第一轮候选时的报告，当前文件已更新；不标记会形成冲突。 | 中 | 是；原句在旧状态下成立。 | 改写 | “这是 2026-11-15 第一轮候选及引言草稿，保留当时的排序”，并链接后续文献重排和当前 README。 |
| `recent_chord_literature_2026-11-15/review.md`：“整体 RMS 匹配另作复核”“增加一个冻结的近期模型” | 后续计划范围 | 当前把整体增益归为实现自检，近期模型是条件性扩展；旧建议不是已承诺的最小实验。 | 高 | 是；作为当时建议可保留。 | 改写入口，保留历史原文 | 顶部明确 RMS 缩放仅作增益不变性自检，近期模型为条件性扩展，执行顺序链接当前 README。 |
| `error_analysis/README.md`：“On IDMT…” | 比较集合未定义 | 这里是 slow 原比较，报告主表是 fast；同名 IDMT 可导致把旧误差分解套到新表。 | 中 | 数据集简称正常，但有多个分支后须说明。 | 改写 | 增加“IDMT subset 4, acoustic_mic/slow”，并链接后续 fast 比较。 |
| `optimization_v2/writeup_portability.md`：“For the four-page report, keep the historical GuitarSet test table.” | 历史排版方案 | 当前报告已按后续研究主线重排；不能作为现在改报告的指令。 | 中 | 旧整合计划本身合理。 | 改写入口，保留正文 | “Archived integration plan for the window-fusion follow-up”，链接当前 PDF。 |
| `root_optimization/bass_branch/README.md`：“Run from the experiment checkout”及绝对路径命令 | 复现位置 | 这是原会话分支命令；项目已有可移植 bundle 重现说明。 | 中 | 历史命令可以作为来源记录保留。 | 改写入口 | “Archived branch summary… use the current reproduction instructions from the project root.” |
| `root_optimization/root_bass_review.md`：“Use…Compare…” | 计划与结果 | 这是原计划，四项候选后来均已跑完；不应看作待做项目。 | 中 | 预先计划的命令语气正常。 | 改写入口 | “Original development plan. The completed branch summary reports all five settings; this plan is retained as written.” |
| `optimization_v2/README_audit.md`：`(results/optimization_v2/README.md)` | 相对链接 | 路径从当前研究目录解析会指向不存在位置。 | 低 | 引用文字合理，仅路径有误。 | 改写 | 改为 `../../../results/optimization_v2/README.md`。 |
| `root_optimization/fast_validation/integration_language_audit.md`：两处 `[search tree](arbor/status.txt)` | 引用的历史 Markdown 被渲染为坏链接 | 表格引用的是修改前/后的原句；当前目录没有该路径。 | 低 | 应保留精确原文，避免重新改写历史引文。 | 改写显示格式 | 将这两段原始链接语法放进代码跨度，保留原字符串而不生成可点击链接。 |
| `rock6_third_diagnostic_2026-11-16/README.md`：“The mean quality margin…was −0.00591” | 必要解释边界 | 正分差时长占多数不等于累计分差为正；同根分差也不等于全部候选的 raw 准确率。 | 高 | 是；它直接决定如何解释 7.85 s，不能因精简删掉。 | 保留 | 保留原文及独立的 24 模板分区、测量单位、事后选择和校准计划。 |
| 文献记录中的 `docs/research/papers/...` 等本地文件名 | 公开阅读入口 | 这些为当时阅读副本，公开仓库不包含 PDF；各篇已给原始来源 URL。 | 中 | 原文阅读来源记录合理，不宜删除版本证据。 | 改写目录入口，保留来源记录 | 新研究索引说明本地名称指当时阅读副本，读者通过各记录给出的原始出版链接访问。 |

## 三、综合建议

本轮仅补当前入口、历史范围和数据分支说明，以及修复相对链接。新研究索引约一屏，带到已有记录；没有重写长期研究笔记或删除不利结果。原有目录中没有必须因内容不相关而排除的文档。旧 `research_questions_2026-11-15/introduction_candidate.tex`、`optimization_v2/writeup_portability.md` 和 `root_optimization/bass_branch/` 应作为历史材料保留，不作为当前方案入口。

修改统计：10 份原 Markdown 有局部入口/链接改动，新增 1 份研究索引。79 个非 Markdown 文件在本分支操作前后逐字节一致，包括 13 个 Python 脚本、候选引言、预测/验证 JSON、CSV/NPZ、图形和历史 bundle。未运行识别、下载或选择参数。修改文档的新链接在去除代码示例后全部解析到仓库现有路径；校验记录见 `/tmp/csc575-publish-research-checks.json`。未改原 Proj、未 commit 或 push。

无正文 Results 重构，故不生成虚假的主文压缩统计；新增短入口的作用是版本与范围定位，原科学段落和测量数值原样保留。论文外部链接的可用性及未来模型实际推理成本没有在本轮重新核验，既有“未知/未运行”均继续保留。

发现的写作特征不能证明文本由 AI 生成。

## 实际审阅清单

下列 Markdown 逐份阅读全文；`README.md` 为本轮新拟索引，其余为原有记录。原有语言审计作为历史说明沿用，不把它们的执行状态改写为本轮复验。

- `docs/research/README.md`
- `docs/research/error_analysis/README.md`
- `docs/research/error_analysis/demo/language_audit.md`
- `docs/research/error_analysis/independent_language_review.md`
- `docs/research/error_analysis/language_audit.md`
- `docs/research/error_analysis/nc_annotation_review.md`
- `docs/research/error_analysis/nc_language_audit.md`
- `docs/research/error_analysis/report_language_audit.md`
- `docs/research/optimization_v2/README_audit.md`
- `docs/research/optimization_v2/idmt_review.md`
- `docs/research/optimization_v2/joint_language_review.md`
- `docs/research/optimization_v2/writeup_language_audit.md`
- `docs/research/optimization_v2/writeup_portability.md`
- `docs/research/optimization_v2/writeup_writing_notes.md`
- `docs/research/progress_2026-11-07/language_audit.md`
- `docs/research/progress_2026-11-07/nature_writing_notes.md`
- `docs/research/publication_2026-11-16/report_review.md`
- `docs/research/recent_chord_literature_2026-11-15/components.md`
- `docs/research/recent_chord_literature_2026-11-15/data.md`
- `docs/research/recent_chord_literature_2026-11-15/guitar_and_systems.md`
- `docs/research/recent_chord_literature_2026-11-15/language_audit.md`
- `docs/research/recent_chord_literature_2026-11-15/review.md`
- `docs/research/recent_chord_literature_2026-11-15/temporal.md`
- `docs/research/recent_chord_literature_2026-11-15/two_stage_2026.md`
- `docs/research/research_questions_2026-11-15/language_audit.md`
- `docs/research/research_questions_2026-11-15/research_questions.md`
- `docs/research/research_questions_2026-11-15/source_audit.md`
- `docs/research/rock6_third_diagnostic_2026-11-16/README.md`
- `docs/research/rock6_third_diagnostic_2026-11-16/language_audit.md`
- `docs/research/root_optimization/README.md`
- `docs/research/root_optimization/bass_branch/README.md`
- `docs/research/root_optimization/bass_branch/initial_plan.md`
- `docs/research/root_optimization/bass_branch/language_audit.md`
- `docs/research/root_optimization/bass_branch/writing_notes.md`
- `docs/research/root_optimization/fast_validation/README.md`
- `docs/research/root_optimization/fast_validation/acquisition_language_audit.md`
- `docs/research/root_optimization/fast_validation/acquisition_writing_notes.md`
- `docs/research/root_optimization/fast_validation/data_notes.md`
- `docs/research/root_optimization/fast_validation/integration_language_audit.md`
- `docs/research/root_optimization/fast_validation/report_language_audit.md`
- `docs/research/root_optimization/fast_validation/report_writing_notes.md`
- `docs/research/root_optimization/fast_validation/reproduction_figure_audit.md`
- `docs/research/root_optimization/fast_validation/runner_language_audit.md`
- `docs/research/root_optimization/fast_validation/source_audit.md`
- `docs/research/root_optimization/fast_validation/source_language_audit.md`
- `docs/research/root_optimization/integration_language_audit.md`
- `docs/research/root_optimization/isolated_compare_review.md`
- `docs/research/root_optimization/isolated_data_review.md`
- `docs/research/root_optimization/isolated_language_audit.md`
- `docs/research/root_optimization/note_cli_language_audit.md`
- `docs/research/root_optimization/note_cli_writing_notes.md`
- `docs/research/root_optimization/report_language_audit.md`
- `docs/research/root_optimization/report_writing_notes.md`
- `docs/research/root_optimization/root_bass_review.md`
- `docs/research/root_optimization/root_harmonic_review.md`
- `docs/research/root_questions_2026-11-13/README.md`
- `docs/research/root_questions_2026-11-13/followup_sources.md`
- `docs/research/root_questions_2026-11-13/language_audit.md`
- `docs/research/root_questions_2026-11-13/literature_audit.md`
- `docs/research/root_questions_2026-11-13/report_design.md`
- `docs/research/root_questions_2026-11-13/report_design_language_audit.md`

脚本文字审阅（13 个文件）：

- `docs/research/error_analysis/demo/check_browser.py`
- `docs/research/rock6_third_diagnostic_2026-11-16/rock6_diagnostic.py`
- `docs/research/root_optimization/bass_branch/run.py`
- `docs/research/root_optimization/fast_validation/acquire_fast.py`
- `docs/research/root_optimization/fast_validation/final_figure_checks.py`
- `docs/research/root_optimization/fast_validation/metadata_preflight.py`
- `docs/research/root_optimization/fast_validation/review_numeric.py`
- `docs/research/root_optimization/fast_validation/verify_acquisition.py`
- `docs/research/root_optimization/review_isolated_numeric.py`
- `docs/research/root_optimization/root_harmonic_extract_check.py`
- `docs/research/root_optimization/root_harmonic_independent_check.py`
- `docs/research/root_questions_2026-11-13/annotation_check.py`
- `docs/research/root_questions_2026-11-13/paired_errors.py`

另读 `docs/research/research_questions_2026-11-15/introduction_candidate.tex` 和 `docs/research/root_optimization/arbor/status.txt`。


## Overview 引用补查

补查范围为 `root_questions_2026-11-13/report_design.md` 的 Introduction draft、同目录 README 的领域做法概述、`research_questions_2026-11-15/research_questions.md` 的背景及候选依据，以及 `introduction_candidate.tex` 的完整引言。用已有 `source_audit.md` 的实际章节阅读记录逐项核对：McVicar §§II–III、Pauwels §§2–4、Müller §4.5 都覆盖频谱/音级证据、和弦模型及时间解码这条共同背景。原始研究的具体算法、单表结果及本项目数值不机械追加综述。

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `report_design.md` Introduction 首段：“Spectral features provide local pitch evidence, while temporal decoding combines that evidence across frames.” | 历史概述缺少就近综述引用 | 这是系统流程背景，原草稿本段无引文；已有三篇审读均直接覆盖此范围。 | 中 | 是正常概述，但用户要求仍适用于公开历史草稿。 | 改写档案说明，保留草稿 | 在 Introduction draft 标题后增加 Archive source note，引用 McVicar、Pauwels、Müller §4.5，并指向记录阅读范围的 source_audit。 |
| `research_questions.md`：“本轮主要阅读：McVicar 2014、Pauwels 2019、Müller 2021 三篇综述” | 引用归属需要明确 | 原文有三篇名称及审读链接；需明确它们共同支持后续表示—模型—解码背景，便于公开阅读。 | 低 | 是，原有近邻来源可以沿用，无须每个候选重复三篇。 | 改写 | 给三篇添加原始出版链接，说明作为以下频谱表示、和弦模型和时间解码讨论的共同背景。 |
| `root_questions_2026-11-13/README.md`“领域已有做法” | 领域框架与具体论文证据 | 表格逐项引用原始方法，流程分类背景未单列综述；不能让旧综述承担 2025–2026 新结果。 | 中 | 具体方法引用原始研究正常；背景来源补一次即可。 | 改写档案说明 | 在表前增加三篇流程背景综述及审读链接，明确各方法和近期结果仍依据相应原始论文。 |
| `introduction_candidate.tex` 首段 `\cite{mcvicar2014,pauwels2019,mueller2021fmp}` | 保留检查 | 已有三篇直接相关综述支持同一连续流程背景；第二段 Cho 和 Humphrey 为具体结论的原始来源。 | 低 | 是，近邻引用足够清楚，不必重复。 | 保留 | TeX 原字节保持不变。 |

本次补查没有重新打开论文全文或扩展既有阅读深度。三篇共同覆盖的是系统流程背景，不为“七音必然造成错误”“校准必然解决问题”等因果结论提供支持；这些仍为未检验假说。近期记录的逐篇结果继续归属原始论文，不用旧综述补数量。此次没有发现上述背景范围之外需要新增综述才能补足的概述段；此结论限于实际指出和阅读的段落，不宣称全仓库每条科学主张都已重新核验。变更仍为此前的 10 份原 Markdown 和 1 份新索引，79 个非 Markdown 文件仍未改。
