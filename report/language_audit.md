# Academic language audit — Introduction argument, 2026-11-16

## 一、整体观察

实际阅读当前报告全文、README 项目描述及方法/计划，并对照上一版 Introduction。修改范围为 Introduction 和 README 的 Project description；其余章节用于上下文核对。先按 nature-writing 重组推理，再检查措辞。原稿的问题是变量选择的理由缺失：raw/decoded 差异支持检查表示与解码，却未直接说明为何改变三音幅度。新版保留研究问题，补充保持目标标签的七音干预、三音作为大小调线索，以及理想模板分差预期。

背景沿用三篇 overview 及 overview_sources.md 的既有核对范围，本轮未重新阅读全文或核验所有外部引文。新增桥梁依据报告式 (2) 和既定实验参数，不引入新的文献机制结论。

## 二、逐条定位

位置按上一版 Introduction 自编号段落；暂存稿注明为本轮候选文本。

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
|---|---|---|---|---|---|---|
| P2：“Vocabulary reduction and annotation ambiguity therefore affect error interpretation.” | 缺少实验选择依据 | 概括没有说明标签归约如何帮助控制实验；annotation ambiguity 也不是当前操控因素 | 中 | 是，概括正常，但没有推进当前问题 | 改写 | “Seventh chords provide a controllable case: adding B♭ to C major or C minor produces C7 or Cm7 while preserving the target label under major/minor evaluation.” |
| P3：“The added decoded errors were concentrated in a seventh-chord recording, motivating a closer look at feature evidence and temporal decisions.” | 观察到问题之间的跳跃 | 该观察支持检查分数与解码，不能独立推出七音或弱三音是原因 | 高 | 是，谨慎措辞合理，但不足以补齐理由 | 改写 | 先给出 raw/decoded 对比和共享惩罚的解释，再用下一段介绍控制变量及式 (2) 的预期。 |
| P4：“Here, third strength means amplitude relative to fixed root and fifth components; pitch remains unchanged.” | 定义没有解释变量作用 | 定义准确，但读者仍不知道为何改变此幅度 | 中 | 是，定义应保留 | 改写 | 保留相对幅度定义；提前说明：“Varying the third's amplitude lets us test the added tone across stronger and weaker evidence for quality.” |
| 暂存 P3：“shrinks a nonzero same-root score gap” | 数学范围与有符号量的表述 | 公式适用于当前评分规则；应明确减小的是分差绝对值 | 低 | 是，通常可理解，但可更精确 | 改写 | “With our triad templates, adding only a seventh component to ideal pitch-class inputs reduces the magnitude of a nonzero same-root score gap through L2 normalization, without reversing its sign…” |
| 新版 P4：“Comparisons of ideal inputs, paired audio and calibrated decoding will trace…” | 已完成与计划工作的边界 | 使用未来时；未把真实录音中的三音幅度当作已测量事实 | 低 | 是，适合进度报告 | 保留 | 保留原文。 |

## 三、综合建议

推理顺序为系统任务、实际观察、控制变量的理由、研究问题及比较路线。四个原始/解码时长和单曲范围保留；公式只用一句说明，不在引言重复推导或 Cm7 并列例子。独立审阅认可该推理，并建议明确数学范围与分差绝对值，已采纳。README 同步该结构。

报告仍为四页，所有页已经渲染检查；其余正文和结果未改。本轮没有新增实验或外部文献核验。上述写作特征不能证明文本由 AI 生成。

---

# Publication pass — 2026-11-16

报告正文沿用本文件下方的完整审查版本。上传前新增的仓库入口、历史范围及复现说明已分别经过 nature-writing 与 academic-language-audit，记录在 [publication_2026-11-16](../docs/research/publication_2026-11-16/report_review.md)。没有改动已测结果、源码快照或当前研究问题。

---

# Academic language audit — progress evidence and diagnostic, 2026-11-16

## 一、整体观察

本轮实际审阅暂存报告全文、results.tex、README、原始 PI、保存的开发/外部结果，以及 rock_6 诊断的 summary.json、validation.json 和播放器图的来源记录。先用 nature-writing 调整论证和证据分配，再用 academic-language-audit 检查含义、范围和自然度。正文以课程进度为主：先交代已实现的系统和原目标完成证据，再从错误分析引出剩余实验。没有采用其他模型给出的分数预测。

文献论述沿用现有19条参考文献及三篇综述的背景引文；未声称本轮重新阅读全文或核验全部文献。新增内容来自项目保存结果和冻结配置下的诊断，不新增文献机制主张。独立检查确认两套校准、理想输入并列处理及原始/解码后的区别仍可辨认。

## 二、逐条定位

位置以本轮最终暂存章节及 results.tex 为准；“前稿”指整合前文本，“中间稿”指本轮压缩过程中已修正的表述。

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
|---|---|---|---|---|---|---|
| 前稿摘要：“This report examines major/minor errors in a guitar chord recognizer.” | 系统与进度背景不足 | 读者先接触错误，尚不知道原项目交付什么 | 中 | 是，研究摘要中正常；本课程报告需要先交代已实现系统 | 改写 | “A working guitar chord recognizer converts audio into timed major/minor labels, with interval playback and CSV export for inspection.” |
| 前稿融合概述：“small development gains that did not persist” | PI证据和转向理由过薄 | 未显示短窗、CQT及自适应融合结果；固定权重搜索与后续融合实验易混淆 | 中 | 是，通常可作概括，但不足以承载原PI完成说明 | 改写 | §4.1提供119条开发集的四种结果，说明原fixed选到零权重，再给出后续blend的独立slow比较 |
| 中间稿§3.1：“Fixed fusion averages short/long chroma” | 方法含义含混 | 可能读成等权，与零权重及0.2权重不一致 | 中 | “average”可包括加权，但此处应明确 | 改写 | “Fixed fusion takes a weighted average of short/long chroma…” |
| 中间稿§3.3：“Of 29.77 minutes…” | 数据范围遗漏 | 前文同时介绍slow64和fast64，读者可能把统计量归给两者合并 | 高 | 数字本身正确，压缩后指代不充分 | 改写 | “The fast set totals 29.77 minutes…” |
| 前稿边界指标仅指向仓库 | 完成证据不足 | O2.2包含boundary metrics；原报告未显示其结果 | 中 | 将次要分析放仓库正常，但课程PI需要具体证据 | 改写 | §3.3定义100ms一对一匹配；§4.2给出27.27%与28.90%的F1 |
| 中间稿：“its fixed slow-IDMT comparison fell to 65.56%” | 比较条件及表达 | “fell to”混合开发集与外部集，仿佛同一评测发生下降 | 中 | 常见口语概括，不适合这里的跨数据比较 | 改写 | “…on slow IDMT the frozen blend scored 65.56%, versus 65.73% for Long STFT.” |
| Figure 1：“Compact player view…” | 展示来源与功能范围 | 使用真实播放器与保存预测，仅调整显示；CSV属于另存文件，非图中按钮 | 中 | 是，名称准确说明展示方式 | 保留 | 保留compact、具体录音名和“rounded for display”；不称未修改全屏截图，不虚构CSV控件 |
| §4.3：“the correct major template outscored its minor counterpart during 7.85…” | 新诊断的证据边界 | 这是参考根音下的两个模板比较，不是24类raw预测正确时长；后者为5.552177s | 高 | 是，当前表述已经正确限定对象 | 保留 | 保留原文；不改写成“raw predictions were correct for 7.85s” |
| §4.3：“The mean margin over these errors was nevertheless negative…” | 结论校准 | 正分差时间更长，但完整9.893311s的时长加权均值为−0.00590777；不能仅据多数正分差认定解码器是唯一原因 | 高 | 是，解释了数值看似矛盾之处 | 保留 | 保留负均值及“Physical third strength remains unmeasured.” |
| §6，两次penalty selection | 数据与用途 | 真实录音复查用GuitarSet开发集；合成confirmation使用自己的development序列 | 高 | 是，必要的平行结构，不属于机械重复 | 保留 | 分别写出选择数据、chord accuracy目标和冻结后的比较对象；保留raw/shared-penalty/calibrated三组 |
| §3.2 Cm7 equality与§6 tied maximizers | 数学和统计范围 | root与seventh等强时三个alpha档位均可打平；argmax顺序不能解释为声学效应 | 高 | 是，简短条件和统计规则具有直接作用 | 保留 | 保留理想并列与单标签错误分别记录；README保持固定容差及并列集合说明 |
| Table 2，O2.4 | 完成状态 | 已完成本次README与progress report，不代表最终报告已交付 | 中 | 是，限定是必要事实而非自我贬低 | 改写 | “Done for this report; final version remains…”；表注明确final report pending |
| 压缩稿§3.2的N及Table 1标题 | 定义与原始/解码区别 | 只写N不定义、只写accuracy不注明decoded，会增加阅读歧义 | 中 | 可从上下文推测，但恢复几个词更清楚 | 改写 | 恢复“the no-chord label N”与“Decoded duration-weighted accuracies” |

## 三、综合建议

八项basic/expected指标已有正文、表或示例对应，具体映射见本轮writing_notes.md。Table 2的作用是指向证据，新增内容没有把正文变成逐项验收记录。原始PI文字保留在README，最终报告仍为待完成工作。

本轮最重要的边界是：7.85/9.89描述同根major/minor分差，而非全24类原始预测正确率；均值负，声学第三音幅度未测量。该结果支持优先校准和检查序列决策，未证明音频特征无误、七音有确定因果作用或解码是唯一原因。新的分数由验证过的冻结代码重算，已有预测标签和边界完全复现；原档案并不含分数数组。

保留原有19条文献、关键数值、共享lambda条件、校准选择准则、并列处理、事后选例范围和正负示例。删除重复铺垫与一般性项目辩护，把详细声源构造、完整诊断和显示调整说明放到README或来源记录。字数算法、变化及证据分配见writing_notes.md；版面和最终文件一致性由整合检查记录。

这些写作特征不能证明文本由AI生成，也不能用于推断作者身份或AI生成概率。下方为历史审查；旧的“没有运行新分析”仅指当时的措辞修改。

---

# Academic language audit — tie handling and calibration, 2026-11-16

## 一、整体观察

本轮使用 nature-writing 与 academic-language-audit，核对报告和 README 的局部改写及上下文。修改集中在并列得分的适用范围、校准数据与比较对象，不扩展研究主张。另由独立审阅者检查数学含义、计划时态和表达。正文仍为四页，原有结果和引用保留。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级 | 是否可能属于正常学术表达及原因 | 建议 | 建议修改版本 |
|---|---|---|---|---|---|---|
| §3.2：“equal pitch-class activations for Cm7 give equal scores…” | 数学条件表述偏窄 | 在计划参数下，三个三音幅度均出现并列；等幅只是其中一例 | 高 | 是，原例正确，但未覆盖后续实验 | 改写 | “…equal scores whenever the root and seventh activations match, regardless of third strength.” |
| §5，理想特征段 | 统计规则遗漏 | 单标签 argmax 可由模板顺序决定；并列诊断需与通常错误率分开 | 高 | 原文是正常概述，但此处补充会影响结果解释 | 补充 | “I will record tied maximizers within a fixed numerical tolerance and flag predictions determined by tie-breaking.” README 保留单标签错误率并单列并列统计。 |
| §5：“by development chord accuracy, using sequences…” | 数据来源含混 | 读者无法判断指 GuitarSet 还是合成序列，也无法判断校准用于哪项比较 | 高 | 是，简写自然但不够明确 | 改写 | GuitarSet 开发集校准后复查 fast IDMT；合成开发序列另行校准后用于 confirmation。 |
| §5：“If calibration removes the decoded gap…” | 比较对象不明 | 需要区分既有真实录音差距与尚未运行的控制实验 | 高 | 条件句正常，指代仍需补足 | 改写 | “If the fast-IDMT gap disappears after GuitarSet calibration…” |
| 暂存 README：“no same-root quality changes” | 统计范围不足 | 既有诊断计数限于相邻且可评分的标注边界 | 中 | 数值依据存在，但不可省去统计范围 | 限定 | “…at contiguous scoreable chord boundaries.” |
| Introduction，研究问题后的通用过渡句 | 重复铺垫 | 工作基础和后续实验已由前文及 §5 说明 | 低 | 正常学术过渡，在四页报告中可省 | 删除 | 保留用户指定的 “Our research question is:” 及问题本身。 |

## 三、综合建议

两处必要说明已融入原段落，不另加解释性小节。校准和并列分析保持未来时；尚未实施的规则未写成已验证结果。保留原始单标签评价，另用并列统计说明选择规则的影响，避免将参考标签位于并列集合中直接算作正确。引用与既有来源审查沿用前次记录，本轮没有重新声称完成文献全文核验。

这些语言检查不能用于判断作者身份或推断 AI 生成概率。以下为历史审查记录，旧的校准表述以本轮修订为准。

---

# Academic language audit — feedback revision, 2026-11-16

## 一、整体观察

审阅完整暂存报告、README、结果表说明与图形标签，并对照原稿、模板实现和保存的数值记录。本轮采用 nature-writing 与 academic-language-audit，重点补足“观察—数学预期—判别实验”的推理链。正文保持四页课程进度报告的体量；计划实验使用未来时，既有结果保持原指标和比较条件。三篇已核验 overview 的背景引用保留，19 篇引用顺序不变。本轮没有重新阅读全文核验所有旧论文；阅读深度及六项来源审查沿用 research 目录的既有记录。

## 二、逐条定位

位置按修订前章节和原文定位；“暂存”表示本轮草稿中已修正的措辞。

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级 | 是否可能属于正常学术表达及原因 | 建议 | 建议修改版本 |
|---|---|---|---|---|---|---|
| Introduction：“My initial guitar experiments also reveal different changes in root and quality errors” | 证据与动机连接偏弱 | 最直接的观察是 raw 总量接近而 decoded 总量不同，应先给出此依据 | 高 | 是，概括准确但不足以承担动机 | 改写 | 给出 49.58/49.64 s 与 19.07/27.41 s，说明差距在解码后扩大 |
| §3.2：“Unit-length templates score twelve major and twelve minor chords by cosine similarity.” | 方法细节与数学预期不足 | 单位长度未说明非零权重相等；权重决定七音干预的基线 | 高 | 是，常见简写，但此处需补充 | 改写 | 每个三和弦位置为 1/√3；增加 Eq. 2 与固定根音排序说明 |
| §3.2，新增 Cm7 例子 | 必要的适用范围 | 同根排序不变不保证全 24 类预测不变 | 高 | 是，简短反例直接限定数学结论 | 保留 | 等激活 Cm7 对 C minor 与 E♭ major 给出相同分数 |
| §5：“A separate equal-RMS comparison will check the effect of changing total energy.” | 实验控制解释不当 | 若只做整体增益缩放，当前归一化流程通常抵消变化 | 高 | 表达自然，但实验角色不正确 | 改写 | “Whole-clip gain rescaling will serve only as an implementation check…” |
| §5，原连续列举多类实验 | 实验优先级和判别标准不足 | 未明确本轮最低主要输出及结果如何决定后续工作 | 高 | 正常计划，但取舍不清 | 改写 | 理想模板→配对音频→raw/校准解码；明确分差和错误曲线及后续分支 |
| 暂存 Abstract：“the shared decoder corrected more of these errors” | 计量含义过宽 | 总量能证明净减少更多，不直接等于只统计纠正区间 | 中 | 合理概括，仍可更精确 | 改写 | “decoding reduced this duration more for spectral chroma” |
| 暂存 §5：“correct-versus-opposite quality score margin” | 指标限定不足 | 需与全类别最高分差区分 | 中 | 术语正常，少一个条件 | 改写 | “…at the reference root” |
| 暂存 §5：“select a separate switching penalty … on development sequences” | 选择规则不明确 | 校准需固定优化指标，不能事后只优化质量错误 | 中 | 计划中可略细节，此处补充成本低 | 改写 | 按 development chord accuracy 选择，各类原始音源变体保持同组 |
| 暂存 §5：“without requiring an improved model in advance” | 冗余及防御性解释 | 已有明确输出；此句主要解释项目为何成立 | 低 | 可用于规划沟通，不需放正文 | 精简 | 删除该句 |
| Figure 1(a)：“Quality-error time (s)” | 统计单位与比较目的 | 组时长不同；百分比更适合比较组内错误比例 | 中 | 原秒数适合总量贡献，不能据此认定原图错误 | 改写 | “Quality-error time (%)”；图注明确全部受支持参考和弦时长分母 |
| §3.3：“59.56% scoreable coverage” | 范围说明不足 | 剩余时间既有未标注首尾，也有不支持的类别 | 中 | 数字准确，但读者需知道排除原因 | 改写 | 补充总时长 27.07% 未标注首尾、13.37% 不支持类别 |
| §6：“Basic final goals… Expected goals…” | 原计划与后续目标容易混淆 | 表中已完成原 proposal 指标，后续实验仍未运行 | 中 | 单独读正常，需标明阶段 | 改写 | Table 2 标记 original proposal；正文标记 remaining stage |
| Introduction：“Our research question is” | 人称风格 | 用户此前明确指定该引导语 | 低 | 可理解，保留用户要求 | 保留 | 保留原文 |

## 三、综合建议

已优先修正动机、数学基线和实验决策，其余修改用于减少重复、解释覆盖率及保持图文一致。保留共享解码器条件下的观察，未将校准假说写成已证实的因果解释；保留 rock_6 事后选例和真实录音三音强度未测量的事实。未采用外部反馈中的指标混比、NNLS 稀疏约束或特定失真归因。

新增实验的根音/音区范围、序列时长和音源分组将于执行前写入配置；这些不是已完成结果。英文全文编译和视觉检查另记于 evidence_checks.json。

发现的写作特征不能证明文本由 AI 生成。
