# Language audit

## 一、整体观察

审阅范围为新增 `chordrec/error_analysis.py` 的 docstrings、CLI 文案、图例与 JSON 说明，以及本目录分析说明；未修改既有报告。本次按 nature-writing 的 manuscript / research / experiments / en / generic 处理。先核对误差类别和分母，再压缩表述。术语固定为 GuitarSet、IDMT-SMT-Guitar、scoreable duration、near、stable、reference N；near 表示参考边界附近的位置，不解释成错误原因。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `error_analysis.py`, metadata interpretation: “Near-boundary errors are a location category, not a causal attribution to boundary timing.” | 证据边界 | 仅根据时间位置划分，未改变或检验边界机制。 | 高 | 是；防止把位置分类当作原因。 | 保留 | 保留原文 |
| `error_analysis.py`, plot axis: “Error duration / row's scoreable duration (%)” | 分母定义 | near、stable、all 的分母不同，必须明示。 | 中 | 是；图中各行可直接解释。 | 保留 | 保留原文 |
| `error_analysis.py`, example selection: “These post-hoc examples illustrate categories, not population representativeness.” | 证据边界 | 中位错误率录音是确定性示例选择，不构成抽样保证。 | 中 | 是；保留一次即可。 | 保留 | 保留原文 |

## 三、综合建议

保留分类、分母和 NC→N 的既定解释，结果说明仅报告观测量。将文件哈希和逐录音核对保存在 JSON，不加入报告正文。图例优先使用和弦关系，避免把 “other root” 写成已确证的频谱机制。未增加文献主张。**发现的写作特征不能证明文本由 AI 生成。**

Nature-writing allocation: aggregate error composition is the central descriptive result; region detail, confusion cells, deterministic examples, and integrity records remain supporting files. No statistical independence or mechanism claim is inferred from this analysis.
