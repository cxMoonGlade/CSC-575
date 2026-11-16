# 文献范围与证据核对 — 2026-11-15

本轮用于重构课程项目的研究问题，不是系统性综述，也不声称证明截至 2026 年尚无先例。核对当前 `report/references.bib` 和 README：可确认三篇综述——McVicar 2014、Pauwels 2019、Müller 2021。Humphrey–Bello 2015 是包含原创实验的批判性分析，作为第四篇主要阅读材料，不计为第四篇独立综述。

按输入、允许操作、输出任务、误差/保证、总成本和失败条件记录；以下阅读由主分支与两个并行阅读分支完成。未运行被引论文的代码。作者明示的模型选择、有限实验和本项目推断分别记录。

检索渠道：本地原文、ISMIR 档案、作者机构网页、出版社网页和通用网页搜索。搜索包括 `automatic chord recognition acoustic model temporal smoothing switching penalty Cho Weiss Bello 2010`、`automatic chord recognition higher order harmonic language modelling temperature acoustic model 2018`、`From Discord to Harmony chord root bass pitch class 2025`、`chord recognition 2024 2025 major minor errors chroma temporal smoothing review`。非原始博客和商业评论未作为技术依据；近期搜索结果的元数据不构成全文审读或新颖性证明。

# Foundations audit for the chord-recognition research question

Read on 2026-11-15. No report edits. This is a mechanism-oriented reading of two historical surveys, not proof of an unfilled 2026 literature gap. Current experiment observations motivate candidate explanations; the papers do not establish their cause.

## McVicar et al. (2014)

Primary metadata: https://biblio.ugent.be/publication/6936363 ; DOI https://doi.org/10.1109/TASLP.2013.2294580 . Local full text: `docs/papers/McVicar_et_al_2014_Automatic_Chord_Estimation_from_Audio_A_Review.pdf`.

**Actual depth:** substantive reading of §§II-A/F/G, III-A/B/E/F, IV-E, V-A–D, VIII (journal pp.558–563, 565–567, 572–573); selected surrounding material, not a complete reread of all cited studies, tables, or references.

| Audit field | What the paper establishes and boundary |
|---|---|
| Input | Polyphonic Western popular-music audio; annotations provide training/evaluation targets. Spectrum/chroma are intermediate representations, not the original task input. |
| Allowed operations | Reviews STFT/CQT, tuning/weighting/harmonic processing, octave folding, feature smoothing, templates, HMM/DBN/CRF inference, expert parameterization and learning. Particular methods make their own assumptions; there is no universal restricted-operation model. |
| Output | A timed chord-label sequence from a chosen vocabulary, sometimes including inversions, bass or key. |
| Error and guarantees | §V distinguishes exact chord-label agreement, pitch-set agreement, root/third reductions, per-song overlap and corpus weighting. It gives no universal accuracy, robustness or generalization guarantee. HMM conditional-independence and first-order assumptions (§III-B, p.562) describe a model, not a theorem that musical data satisfy them. |
| Total cost | Review has no uniform end-to-end timing/precision benchmark. §II-F notes frame-count savings from beat synchronization; §III-E reports high memory costs for higher-order models. This cannot establish that a frontend is cheaper after feature construction, tuning, decoding and evaluation. Unknown unless measured in our pipeline. |
| Failures and limitations | Explicit: fixed STFT window trades frequency against temporal resolution (§II-A, p.558); octave folding loses register/inversion distinctions (§II-E/G, p.560); expert and learned systems can both overfit, including through inspecting test errors (§IV-E, p.566); a reduced vocabulary and different scoring rules change the task (§V-A/B). These are distinct representation, modelling and evaluation issues. |

**Useful implication (ours):** an apparent representation improvement under one decoder penalty is not sufficient to attribute the change to acoustic evidence alone. A factorial feature × decoder comparison can separate those effects locally, without claiming a novel general-purpose recognizer.

## Pauwels et al. (2019)

Primary full text: https://archives.ismir.net/ismir2019/paper/000004.pdf ; archival record https://zenodo.org/records/3527739 . Local copy: `docs/papers/Pauwels_et_al_2019_20_Years_of_Automatic_Chord_Recognition_from_Audio.pdf`.

**Actual depth:** read main text pp.54–59, §§1–9, with emphasis on §§2–4 and 7–8. Did not independently reread the complete underlying bibliography.

| Audit field | What the paper establishes and boundary |
|---|---|
| Input | Audio plus, depending on the reviewed system, training annotations and auxiliary beat/key/bass information. |
| Allowed operations | Pitch/chroma construction, harmonic/template modelling, neural features/classifiers, temporal smoothing or sequence models, beat synchronization, auxiliary target prediction and vocabulary construction. |
| Output | Timed harmonic labels; alternate formulations can predict pitch sets or component labels. Explicit vocabulary is a consequence of a classification design, not inherently required by the musical task (§8, p.59). |
| Error and guarantees | Discusses label ambiguity, annotation disagreement, class imbalance and duration-weighted evaluation. No new common numerical experiment or error/generalization guarantee is supplied by this review. Claims about particular methods are summaries of cited studies, not transferable guarantees. |
| Total cost | No end-to-end comparative runtime budget. §2 notes dimensionality reduction/computation tradeoffs; §4 notes fewer frames after beat synchronization; §7 describes the poor scalability of repeated human judging. Feature construction, training, upstream beat errors and decoding still count. |
| Failures and limitations | Explicit: harmonic energy can map to other pitch classes (§2, p.55); ideal binary templates can mismatch measured chroma (§3, pp.55–56); blind smoothing can smear boundaries and remove short chords (§4, p.56); beat synchronization relies on correct beat estimation (§4, p.57); triad/tetrad classes overlap and rare-class improvements may vanish in aggregate accuracy (§8, p.59); limited stylistic coverage does not establish general applicability. |

**Useful implication (ours):** seventh-chord references, a triad-only prediction model and a smoothing decoder are three separable possible explanations for the present quality errors. Current `rock_6` evidence is diagnostic, not proof that any one explains the effect.


---

# Source audit and research-question candidates — 2026-11-15

Read-only project inspection; no repository files changed. Read current `report/progress_report.tex` and reference entries, full relevant Humphrey & Bello pp. 673–678, and Müller front matter, §2 and complete §4.5. Original sources verified through official author/publisher or ISMIR links.

## Source types and evidence

### Müller (2021), *An Educational Guide through the FMP Notebooks for Teaching and Learning Fundamentals of Music Processing*

Source: https://www.audiolabs-erlangen.de/resources/MIR/FMP/data/C0/2021_Mueller_FMP_Signals.pdf ; DOI 10.3390/signals2020018. Printed pp.245–285. Publisher labels it **Review** on p.245. It is an educational MIR review; §4.5 (pp.263–266) directly covers chord recognition. Do not present it as an exhaustive review of contemporary ACR systems.

- **Input:** audio recordings; real-valued twelve-dimensional chroma (§4.5, pp.263–266).
- **Operations:** construct major/minor templates, framewise similarities and argmax; continuous-feature HMM with normalized similarity emissions; uniform non-self transitions, one self-transition parameter; log-domain Viterbi (pp.265–266).
- **Output:** chord-labelled time intervals in a simplified major/minor task.
- **Error/guarantee:** discusses reference-based precision/recall/F-measure and visual inspection; no claim that decoding guarantees better perceptual chord accuracy. Viterbi optimizes its stated model, not agreement with musical truth.
- **Total cost:** feature computation, label conversion, templates, decoding and evaluation are needed. No comparable end-to-end runtime claim is supplied in the inspected chord section. §2 explicitly prioritizes teaching over compact/efficient implementation.
- **Failure conditions:** model and annotation mismatch; chord and segmentation ambiguity; underflow in multiplicative Viterbi (remedied by log domain). Parameters are fixed using musical knowledge, not estimated in this demonstration.
- **Evidence boundary:** these are author-described properties/limitations. Inferring that our projection scores require a differently calibrated penalty is a hypothesis, not a finding of this review.

### Humphrey & Bello (2015), *Four Timely Insights on Automatic Chord Estimation*

Source: https://archives.ismir.net/ismir2015/paper/000294.pdf ; local PDF `docs/research/papers/Humphrey_Bello_2015_Four_Timely_Insights.pdf`. Printed pp.673–679. This is **original comparative/qualitative analysis with a critical perspective**, not a fourth independent survey. Four insights are not four overview articles.

- **Input:** music recordings plus chord references from merged datasets (1217 unique tracks) and separately analysed Rock Corpus; two existing large-vocabulary models (§§2–3, pp.674–675).
- **Operations:** beat-synchronous multiband chroma/GMM-HMM versus CQT-patch CNN plus Viterbi; fivefold training/evaluation; compare model–reference, model–model and annotator agreement.
- **Output:** time-aligned sequences from 157 classes, with trackwise diagnostic examples.
- **Error/guarantee:** duration-weighted chord-symbol recall over metric-supported time; different comparison functions. No theorem or universal accuracy guarantee. Empirical model/sample scope only.
- **Total cost:** acoustic extraction, model training repeated across five folds, decoding, reference conversion and qualitative review. Comparable wall-clock total is unreported in the inspected paper.
- **Failure conditions:** tuning assumptions; music poorly described by chord labels; vocabulary reductions and related-but-nonidentical labels; segmentation/recognition versus transcription ambiguity; annotator disagreement (§§4.1–4.4, pp.676–678).
- **Evidence boundary:** the paper motivates inspecting source labels and individual tracks. It does not prove that our seventh-chord example is wrongly annotated or that label reduction causes our false-minor predictions. Mapping a dominant seventh to its major triad is consistent with the chosen scoring convention; a wrong minor can still be a genuine recognition error under that convention.


## Cho, Weiss and Bello (2010)：补充原始实验

[作者全文](https://ronw.net/pubs/smc2010-chordreco.pdf)，*Exploring Common Variations in State of the Art Chord Recognition Systems*。

本轮重读 §3.3、Table 2、Figure 8 的正文解释（PDF 第 6 页），结合已有 `root_questions_2026-11-13/followup_sources.md` 对 §§2–4 的记录；未重新阅读全部八页。此文为原始实验，不计入综述数量。

- 输入：音频及 Beatles 和弦标注，模型训练和评价依赖所比较的设置。
- 允许操作：CQT/chroma、特征平滑、二值模板或 Gaussian/GMM/HMM 声学模型、转移矩阵及 Viterbi 参数扫描。
- 输出：major/minor/N 和弦序列。
- 误差与保证：13 个唱片分组、180 首歌曲上的正确时长比例及最优设置表；有限数据结果，不保证新数据或其他声学模型的准确率。
- 总成本：特征提取、模型训练、参数组合搜索和解码；所读部分没有可比较的完整端到端计时。
- 失败条件：作者将模板模型对转移惩罚的敏感性与候选分数接近联系起来；这是其模型和实验的解释。我们的余弦分数不是该文的倒数距离伪概率，不能照搬参数值。论文早已研究模型依赖的平滑，因此“分别调参”本身不构成新方法。

本项目推断：需要检查声学分数间隔和错误连续段，才能区分相同惩罚下的行为差异。校准后差距缩小支持该局部解释，但不证明全部错误由一个参数造成。

## 当前实现与观测核对

读取 `chordrec/model.py`、当前报告、配置及现有预测汇总。解码目标是逐帧余弦分数之和减去每次标签变化的统一惩罚。单纯将全部有限声学分数乘以正数 c，等价于将惩罚换成 λ/c；不能将全局温度与统一惩罚包装为两个独立机制。

原始同根音性质错误时长：long STFT 49.582448998 s，projection 49.643469402 s；统一解码后分别为 19.073605447 s 和 27.414784586 s。它们是对固定参考支持区间统计的错误类别时长，总量接近不代表错误位置或声学证据相同。开发集同根音大小调变化为 0，fast IDMT 为 4；不能仅凭这批数据验证专门的性质平滑能保留真实变化。

对固定两端 A 的简化两路径比较，A–B–A 相对全 A 的目标差是 Σ[e_t(B)−e_t(A)]−2λ。因此累计声学优势大于 2λ 才使前一条路径更优。这是从当前目标直接推出的两路径比较，不是完整 25 状态 Viterbi 的识别保证；其他路径、边界及 N 状态会改变比较。

已有音频与预测可支持探索性诊断。新的参数或方法可以在开发材料上选择，旧测试集继续用于描述；独立泛化结论需要新曲目。oracle-root 分数只作诊断，不作为实际识别器输出。主要指标使用预先固定的参考支持区间，不能只选择两个系统都预测对根音的帧。
