# Root-error hypothesis: harmonic note fitting

Read 2026-11-09. Evidence is restricted to the 119 development recordings and Mauch and Dixon (2010). Neither previously evaluated test set was used to select this method.

## Paper audit

Source: *Approximate Note Transcription for the Improved Identification of Difficult Chords*, ISMIR 2010, pp. 135–140. Local PDF and its extracted text were read through §§1–5, Table 1, Figure 3, and methodological footnotes. The reference list was inspected. The original implementation and thesis were not read or reproduced in this pass.

- **Input:** audio, evaluated on 210 MIREX 2009 songs with chord references (§3, p. 138).
- **Allowed operations:** downsampling to 11025 Hz; 4096-sample Hamming DFT; mapping to 256 bins spaced at one third of a semitone; global tuning estimation and interpolation; local spectrum subtraction/standardization; NNLS fitting with 84 idealized harmonic note profiles; separate bass/treble chroma folding; automatic beat tracking and median aggregation; Viterbi inference in a dynamic Bayesian network (§§2.1–2.5, pp. 136–138). The extracted hop statement “2048 frames (approximately .05 s)” is internally inconsistent and was not adopted for this implementation.
- **Output task:** a 121-state chord sequence including inversions and N. Evaluation also reduces to 24 major/minor chords plus N (§2.1 and §3.1).
- **Error and guarantee:** duration-weighted correct overlap. Full-column-rank E gives uniqueness of the NNLS solution (§2.4); this is not a recognition guarantee. Under the same standardized spectrum, Table 1 reports 79.0% without NNLS versus 80.0% with s=.6. The comparison to a 74% earlier complete system does not isolate NNLS. Table 1 and Figure 3 provide finite-corpus evidence.
- **Total cost:** DFT, log-frequency mapping, tuning, standardization, dictionary construction, framewise constrained least squares, beat tracking, aggregation, and DBN decoding. End-to-end runtime and memory were not reported in the sections read. Dictionary compression to 256 rows reduces the fitting dimension. The paper provides no matching-accuracy end-to-end speed advantage.
- **Failure conditions and scope:** the authors explicitly assume no sinusoidal cancellation (footnote 1). Geometric harmonic envelopes and common tuning are modeling choices, not necessary properties of chord recognition. Figure 3 shows decreases for maj7 and N; §4 proposes, but does not verify, a beneficial-harmonics explanation for maj7. Beat synchronization and the DBN differ from this project's framewise triad system. Their gains do not guarantee gains for GuitarSet or establish the cause of its errors.

## Development diagnosis

The saved long8192 predictions contain 1577.840597 correct seconds out of 2192.498948 scoreable seconds. Wrong-root predictions occupy 547.081291 seconds; same-root quality errors 55.046177 seconds; chord-to-N errors 12.530883 seconds. Wrong-root errors make up 89.006% of all errors. Prediction roots four semitones above the reference account for 153.814408 seconds, followed by seven semitones at 118.185979 seconds. C:maj to E:min contributes 35.085117 seconds.

An illustrative, deliberately selected long error is `01_Funk1-97-C_comp`, 0–9.896907 seconds. Its performed label is C:maj/3, and its note annotations contain E, G and C, with 4.950877, 3.992714 and 3.704982 note-seconds respectively. No B note is annotated in this interval. The long-window mean chroma over .2–9.69 seconds assigns B=.305938 and C=.277654; the decoder predicts E:min throughout. These observations motivate separating note fundamentals from their partials before octave folding. They do not identify the acoustic origin of B energy, and the note annotations are another estimated representation rather than independent manual verification of every note.

## Proposed comparison

Fit idealized harmonic note profiles to the same 8192-sample Hann magnitude spectrum and observed frequency range as the baseline. Use MIDI 36–95 and the existing tuning estimate. Each partial has a Hann-windowed sine response, with amplitude decay s^(k-1). Evaluate s=0, .6 and .9. The s=0 model controls for note fitting without harmonic modeling. Sum the nonnegative fitted activations by pitch class, normalize, and retain the existing triad templates, RMS rule and Viterbi penalty 4. This is a simplified experiment inspired by Mauch and Dixon, with no spectral standardization, bass model, beat aggregation or DBN.

The primary outcome remains duration-weighted major/minor accuracy. Root accuracy and wrong-root seconds diagnose whether any gain addresses the proposed problem. Require overall improvement without a decline in either development progression family before considering a candidate. Record the cost of fitting and measure uncached full inference separately if a candidate advances.

## Writing review

Nature-writing route: manuscript / research / method and related work / English / generic. Terms remain `harmonic note fitting`, `NNLS`, `root accuracy`, and `duration-weighted major/minor accuracy`.

### 一、整体观察

已审读本文笔记与实验计划。表述区分了历史方法、开发集观察和待检验解释；结果尚未产生，因此未写入性能提升结论。

### 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| Diagnosis: “These observations motivate separating note fundamentals from their partials before octave folding.” | 证据边界 | 根音混淆与缺失 B 标注不能单独证明所有额外 B 能量来自泛音。下一句说明此范围。 | 中 | 是，作为实验动机而非机制结论。 | 保留 | 保留原文及下一句限定。 |
| Paper audit: “79.0% without NNLS versus 80.0% with s=.6.” | 比较条件 | 保留相同标准化下的直接对照，避免把完整系统对比归给 NNLS。 | 高 | 是，Table 1 支持。 | 保留 | 保留原文。 |

### 三、综合建议

后续结果应报告开发集及分组差异，不能将根音指标改善替代原定和弦准确率。保存失败候选和运行成本。上述语言特征不能证明文本由 AI 生成。

## Result-language audit

The result paragraph reports all settings, including the adverse harmonic comparisons. The phrase “fundamental-only NNLS” identifies the winning control. “Harmonic removal improves accuracy” was rejected because the harmonic models underperform that control. Chord accuracy remains the primary metric; root accuracy uses all chord-scoreable duration. Development fitting times are separated from uncached inference costs. The final extractor adds uncached audio processing and removes dictionary caching; the initial source snapshot remains in the result directory. Three numerical/temporal tests passed.

## Portability review

The runner now accepts `--project-root`, `--cache-dir`, and `--output`. Argument parsing and expensive imports occur inside a guarded `main`; imports and help perform no experiment. The original result snapshots remain unchanged. The candidate loop and metric aggregation have identical abstract syntax to the archived runner, so this packaging edit does not require another full development search.

Nature-writing retained the established manuscript/research/method/English/generic route. Reproduction instructions state the required cache and distinguish stage timings from full inference. The added wording introduces no new performance claim.

### 一、整体观察

本次只审读运行参数帮助、复现说明和成本标签。原始结果与来源快照保留，未重新解释实验结论。

### 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README, final paragraph: “the baseline chroma and all tuning estimates come from the cache” | 成本边界 | 准确说明已复用的计算，防止把阶段计时读成完整推断成本。 | 高 | 是，直接对应运行代码。 | 保留 | 保留原文。 |
| README, final paragraph: “each NNLS call constructs its dictionary” | 版本一致性 | 新运行器使用无字典缓存的模块；前文单独说明历史结果复用了字典。 | 中 | 是，区分历史计时和复现实验。 | 保留 | 保留原文。 |

### 三、综合建议

完整文件推断成本继续由独立运行器测量，避免使用此处缓存实验的计时进行系统速度比较。发现的写作特征不能证明文本由 AI 生成。
