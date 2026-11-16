# Low-register evidence experiment

Development predictions contain 547.08 seconds of different-root errors, compared with 55.05 seconds of same-root quality errors. A predicted root four semitones above the reference accounts for 153.81 seconds. C:maj→E:min is the largest individual different-root confusion (35.09 seconds). These templates share E and G; emphasizing lower-register evidence may help distinguish them. The confusion pattern motivates this hypothesis but does not establish a spectral cause.

## Candidate and controls

Use the frozen long-window spectrum (8,192 samples), tuning estimate, frame times, RMS threshold and Viterbi penalty. Construct an additional chroma from MIDI 36–59 using the same chroma basis and half-semitone frequency edges. L2-normalize this low-register chroma. No extra STFT is needed.

Let S(c,t) be the current triad cosine score and L(p,t) the low-register chroma. Compare the baseline with four predeclared settings:

- Root evidence: (1−λ)S(c,t)+λL(root(c),t), with λ=0.1 or 0.2.
- Triad-support control: (1−λ)S(c,t)+λ〈template(c),L(:,t)〉, with λ=0.1 or 0.2.

Both score components lie between zero and one. Root evidence is a soft preference. The method does not force the lowest note to equal the root; inversions, absent low fundamentals and harmonics within the low band can still make this preference harmful. The control tests whether any gain requires a root preference or follows from emphasizing low-register chord tones generally.

## Evaluation

Use only the 119 development recordings, grouped by progression families 1 and 2. Select by duration-weighted major/minor accuracy. Report root accuracy on chord-reference time, different-root error duration, same-root quality error duration, chord-to-N duration, and per-family changes. A gain in root accuracy alone is insufficient if major/minor accuracy falls. No extra weight or band-limit search follows these five comparisons in this branch.

Verify that the reconstructed baseline chroma and labels equal the cached frozen baseline. Add numerical checks for all-zero low-register input and synthetic root-position and inverted triads. Save per-recording results, settings and source hashes. Measure complete uncached runtime only if a candidate is selected for further evaluation. Fresh validation material is required before a new generalization claim.

## Writing notes

Scope: local experiment plan; Nature axes manuscript / methods / experiments / en / generic. Canonical terms: low-register chroma, root evidence, triad-support control, duration accuracy. This is an empirical course-project modification, with no novelty or mathematical performance guarantee claimed.

## 一、整体观察

已审阅本文件完整计划和 development-only 混淆统计。文字区分了已观察的误差与待检验的声学解释；参数、成本和转位失败条件均有明确范围。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 开头 “emphasizing lower-register evidence may help distinguish them” | 证据边界 | 混淆统计不能单独证明频谱机制；may 保留假设语气，后一明确限制推断 | 低 | 是，研究计划应区分假设和观察 | 保留 | 保留原文 |
| Candidate “Root evidence is a soft preference” | 方法解释 | 加权发射分数而非强制根音，避免把低音等同根音 | 低 | 是，直接对应数学定义 | 保留 | 保留原文 |

## 三、综合建议

实施时保留所有五个比较及不利结果。若整体准确率下降，不以根音指标改善代替主任务结果。发现的写作特征不能证明文本由 AI 生成。
