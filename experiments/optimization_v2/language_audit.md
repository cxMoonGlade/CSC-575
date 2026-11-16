## 一、整体观察

审阅范围：本目录 README、全部 Python 文件的说明文字、注释与显示标签，以及两个保留的实验计划；未改动报告正文。核对了四个原始结果文件与三条开发录音的移植检查。原稿通过 `original_sources.json` 中的路径和 SHA256 定位，修改稿使用当前行号。

已使用 academic-language-audit 和 Nature writing 1.6.0。README 按“比较什么—观察到什么—如何运行”组织，保留学生项目所需的信息。数字、选择标准、数值计算与研究范围不因润色而改变。未见集中出现的套话、创新性夸大或机械重复。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| 原 `acquire_idmt.py` 第 1 行：“using verified HTTP byte ranges” | 核验对象含糊 | 实现检查响应状态、Content-Range 和长度；整个压缩包的哈希并未验证。 | 中 | 可以，但“verified”未说明检查对象。 | 改写，已应用 | “using checked HTTP range responses” |
| 原 `idmt_metadata_acquire.py` 的 `scope`：“All64selectedregardlessscoreablelabelcoverage; acoustic_mic/acoustic_pickup arecapturestreams ofoneacousticguitar, notindependentguitars.” | 局部表达不自然 | 连写妨碍阅读；麦克风与拾音器的区别应明确保留。 | 低 | 否，缺少空格不是学术惯例。 | 改写，已应用 | “Include all 64 selected recordings regardless of scoreable-label coverage. acoustic_mic and acoustic_pickup capture the same acoustic guitar.” |
| README 第 5 行：“The four branches evaluated 30 settings, including repeated controls.” | 样本与比较数量核对 | 四个固定网格为 9、9、7、5；明确重复基线不算独立新方法。 | 低 | 是，属于必要的比较范围说明。 | 保留 | 保留原文。 |
| README 第 15 行：“The small development gain does not establish a new validated default.” | 证据边界 | 最佳开发增益未达到预设标准；该句解释默认方法的选择，没有把开发结果写成泛化优势。 | 低 | 是，限定条件直接影响读者使用代码。 | 保留 | 保留原文。 |
| `resolution/run.py` 的 `cost_note`：“Cached prediction timings and the extra extraction time are not complete audio-to-label inference comparisons.” | 成本范围 | 特征缓存与单独提取时间不能合成原始录音到输出的公平速度结论。 | 低 | 是，避免把组件耗时当成总成本。 | 保留 | 保留原文。 |

## 三、综合建议

已修改下载来源说明中的含糊措辞和连写文本；保留准确的数值、变量名与技术注释。运行说明使用统一的 development recordings、duration-weighted chord accuracy、percentage points 和 baseline。四个分支的全部参数保留在源文件及计划中，README 只列关键比较和执行命令。

本次不重新评价文献或外部数据上的算法表现。移植检查仅覆盖三个开发录音和五个配置；完整网格结果来自原始实验。数据获取脚本的完整重下载未重跑，缓存中的 ZIP 目录读取通过检查。以上范围在交付说明中保留。发现的写作特征不能证明文本由 AI 生成。
