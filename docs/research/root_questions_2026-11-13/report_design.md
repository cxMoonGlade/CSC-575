# Report framing and preliminary study

Archived draft from 13 November 2026. The annotation audit and saved-prediction analysis were complete when this plan was written; the decoder experiments were proposed. The [current project plan](../../../README.md#preliminary-error-analysis-and-next-experiments) supersedes the research question and experimental controls below.

## Proposed title

**Root and Chord-Quality Errors in Template-Based Audio Chord Recognition**

## Introduction draft

Archive source note: [McVicar et al. (2014)](https://doi.org/10.1109/TASLP.2013.2294580), [Pauwels et al. (2019)](https://archives.ismir.net/ismir2019/paper/000004.pdf) and [Müller (2021), §4.5](https://doi.org/10.3390/signals2020018) cover the task and spectral-feature, chord-model and temporal-decoding background below. The [source audit](../research_questions_2026-11-15/source_audit.md) records the sections read.

Automatic chord recognition assigns harmonic labels to intervals of audio. A major/minor recognizer must identify both the chord root and its quality. Spectral features provide local pitch evidence, while temporal decoding combines that evidence across frames. The interaction matters: a representation that improves root estimates may still introduce quality errors in some passages.

This project asks: **How do spectral representation and temporal decoding affect root and chord-quality errors in a lightweight guitar chord recognizer?** Initial multi-resolution experiments did not improve the held-out comparison. Their error analysis motivated a comparison of note projection and non-negative least squares before octave folding. This report presents those comparisons and a subsequent analysis of error changes. The next experiments will test whether a common switching penalty explains the remaining quality errors, and whether distinguishing root changes from quality changes adds useful information.

## Preliminary-results draft

Direct projection improved duration accuracy from 64.70% to 67.80% on the frozen fast-tempo comparison. Same-root quality errors nevertheless increased from 19.07 to 27.41 s. A subsequent annotation audit found that these errors decreased from 5.64 to 4.14 s on references containing only triad pitch classes, but increased from 13.43 to 23.28 s on references with additional chord tones. The largest deterioration occurred in `rock_6`, whose A7, D7 and E7 annotations reduce to major triads under the evaluation vocabulary. This concentration motivates examining the representation, decoder and vocabulary reduction together; it does not identify which one explains the errors.

Among contiguous, scoreable chord-to-chord boundaries, the 119 development recordings contain 410 root changes and no same-root major/minor changes. The fast recordings contain 363 root changes and four same-root quality changes. These data can reveal spurious quality changes, but development accuracy alone cannot establish whether stronger quality smoothing preserves real quality changes. Controlled examples containing both kinds of transition are therefore needed.

## 报告主线

主问题研究“表示和解码如何影响两类错误”。“弱三音”“两种时间尺度”和“七和弦约简影响识别”是解释候选。问题来自已经观察到的结果；引言可以先提出问题，但不能把本轮诊断写成原先预设的实验。

已完成的多分辨率比较保留为起点，并用简短结果解释为何继续研究音符表示。保持原有个人 PI 编号及完成状态。后续解码和可控样例列入剩余工作，不标为完成。

分层依据 `mir_eval.chord.encode` 返回的参考和弦音级集合，忽略低音字段：与大／小三和弦集合完全一致归为 triad，其余可约简参考归为 extended。转移统计不跨越间隙、N 或不可评分区间；它统计标注中的转移，不是实际演奏音符变化。

## 初步实验与竞争解释

| 实验 | 对照与测量 | 能回答什么 |
| --- | --- | --- |
| E0，已完成 | 对齐保存的逐帧和解码输出；按原始参考音级集合分层；统计真实参考转移。 | 错误是否集中、数据能否评价真实性质变化。分层与曲目和演奏混杂，不是约简的因果效应。 |
| E1，待做 | Long STFT 与 projection，各用 λ=0、原 λ=4、在开发集选择的统一 λ；候选固定为 {0,1,2,4,8,16}。在 progression 1 上选择、2 上观察，再交换；同一录音供所有条件使用。 | 单一平滑强度能解释多少差异。两个家族均已用于开发，这只是开发稳定性检查。若最优值在边缘，先报告边缘结果；后续扩展另记。 |
| E2，待做 | 可控和弦序列包含同根 major↔minor、换根、保持不变三种情况；交叉改变三音幅度、额外七音及和弦时长，使用相同包络和边界处理。 | 区分频谱证据、额外音和持续时间的影响；同时检查误报、真实变化漏检和延迟。 |
| E3，取决于 E1/E2 | 与已调好的统一惩罚比较：换根用 λr，同根性质变化用 λq；保持声学分数、状态和 N 规则。 | 额外结构能否在减少虚假切换的同时保留真实变化。当前开发集不足以单独选择 λq。 |

E2 的具体幅度、时长、样例数和随机种子将在生成前固定，当前尚未采集或分析这些样例。先固定生成方案，再分开用于开发和诊断的音色与随机种子；真实新曲目用于后续确认。所有变体与转调属于同一基础序列组。三音幅度取非零值，避免没有三音却强行认定大小调；保持不变的对照采用相同重起音包络，避免边界声音只出现在发生变化的条件中。控制总 RMS，并记录各音幅度。合成样例检验指定条件下的行为，不代表真实吉他泛化。

对大小调切换既统计错误跳变，也统计漏检；只减少跳变不算充分改善。主指标仍为完整和弦时长准确率，附根音准确率、按固定参考时间统计的性质错误、边界表现和端到端运行时间。双方根音都正确的区间只作配对诊断，它是由输出定义的子集。

统一分数缩放不是独立方法。现有解码目标为 `sum(e_t(s_t)) − λ × switches`；把所有有限声学分数乘以 α>0，等价于把 λ 改为 λ/α。因此不把全局温度和统一惩罚当作两项独立改进。局部或分量相关调整才可能改变这一等价关系。

## 四页内的安排

| 内容 | 预计篇幅 | 作用 |
| --- | ---: | --- |
| Abstract、Introduction、Related Work | 0.8 页 | 提出问题，交代表示与时间模型的先例。 |
| Method、Data、Evaluation | 0.8 页 | 用一条识别流程、一个拟合公式和明确的评分范围说明比较。 |
| Preliminary Results、Discussion | 1.2 页 | 压缩保留原窗口比较；展示三方法主结果、一次错误分解和一个时间轴案例。 |
| Individual Progress、Remaining Work | 0.4 页 | 保留个人 PI；列基本、预期和进阶目标。 |
| References | 0.8 页 | 现有 16 篇加 Cho et al. 2010、EUSIPCO 2018 和 Discord 2025，共 19 篇；正文分别承担对照依据、解码交互和组成指标差异的论证。 |

篇幅是排版目标。总体结果、关键失败条件及个人状态优先；完整参数表、逐录音结果和原文审读记录放在仓库笔记。实验比较包括特征与字典构造、参数选择、解码和输出成本；缓存仅供开发重算，完整推理耗时另测。已有 fast/slow 与 GuitarSet 测试结果用于诊断，新方法的确认需另取曲目。

## 本次核对材料

- [annotation_check.json](annotation_check.json)：442 个输入文件的摘要、逐录音统计和原汇总一致性检查。
- [annotation_check.py](annotation_check.py)：只分析标注及保存的预测，不运行识别器。
- [followup_sources.md](followup_sources.md)：新增来源的任务、成本、失败条件及阅读深度。
- [report_design_language_audit.md](report_design_language_audit.md)：两项指定写作技能的处理记录。

复核命令（项目根目录运行）：

```bash
.venv/bin/python docs/research/root_questions_2026-11-13/annotation_check.py \
  . /tmp/chord-annotation-check.json
```
