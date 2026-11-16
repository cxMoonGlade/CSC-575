# Repository entry-point review, 2026-11-16

## 一、整体观察

本轮只修改独立检出 `/home/cx/Documents/csc475/CSC-575` 内的 `README.md`、`docs/resources.md`、`.gitignore`。原项目 `Proj` 保持不动；未提交、未推送。重点是首次克隆后的数据准备、播放器使用和提交范围，没有改写研究主张或重排报告。

执行技能：`nature-writing` 与 `academic-language-audit`。Nature 路由为 `manuscript / research / method（局部复现说明） / zh-to-en / generic`。这是课程项目仓库说明，采用清楚的步骤和证据归属，不套用期刊投稿材料格式。

术语沿用原稿：GuitarSet v1.1.0 为开发数据；IDMT-SMT-Guitar 为外部比较数据；`prepare` 表示读取已下载文件并生成划分；Long STFT、direct projection、NNLS 的命名不变。正文和参考文献保持原有表达，不添加新的领域综述主张。原有综述引文组 [1–3] 保留，本轮没有重新审读这些论文，亦不声称完成新的引文内容核验。

实际读取范围：

- 当前 `README.md` 全文、`docs/resources.md` 全文、`.gitignore` 全文、`AGENTS.md` 全文。
- `chordrec/run.py` 的 CLI/prepare 实现，`chordrec/data.py` 的标注、划分和路径规则；`chordrec/note_predict.py` 的输出及播放器条件。
- `chordrec/diagnostic_player.py` 的播放器音频内嵌和归属信息；两个 README 链接的 HTML 检查了音频 data URI，未重新进行视觉播放测试。
- `results/dev_frozen/environment.json` 全文；`requirements.txt` 全文和 `requirements-lock.txt` 中 Python 相关条目；不以包的新旧推测 Python 版本。
- `docs/research/root_optimization/fast_validation/README.md`、`results/root_optimization/README.md` 全文，用于确认 IDMT 来源、子集、数量及复现入口。
- 原项目本地 `docs/datasets/GuitarSet/sources.json`、该目录 README 全文及 `inventory.json` 的 summary 和若干记录；旧 inventory 的“尚未实验”等历史描述没有带入当前资源说明。
- 两个原始 GuitarSet ZIP 的完整成员列表与实际文件 MD5。各含 360 个顶层文件，MD5 与本地已核验来源记录一致；没有重新下载归档或重新核验官方网页的实时状态。
- `report/BUILD.md`，用于确认当前 PDF、构建资源和归档截图脚本的用途。

技能读取包括两个 SKILL.md、nature-writing manifest、全部 always_load 文件，以及 manuscript/research/method/zh-to-en/generic 对应片段。

## 二、逐条定位

位置使用修改前 `Proj` 的行号；新行号可由独立检出的 diff 核对。

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| README:95–100，安装后直接运行 `.venv/bin/python -m chordrec prepare` | 复现前提缺失 | `prepare` 只读取本地文件；新克隆没有被忽略的数据目录。没有下载、解压步骤会直接失败。 | 高 | 命令本身正确，但对新读者缺少前提。 | 改写 | “First follow the GuitarSet download and extraction steps … `prepare` reads the downloaded files and writes the recording split.” 下载细节集中到 resources，避免首页堆砌。 |
| README:96，`python -m venv .venv` | 环境说明不明确 | 保存的 environment.json 明确 Python 3.13.13；原命令取决于用户默认 Python。 | 中 | 通用项目中很常见，本项目已有冻结环境可直接说明。 | 核实后改写 | “Use Python 3.13; the saved runs used 3.13.13.” 命令采用 `python3.13`。 |
| README:104/106，链接 “standalone player” 和 “note-projection player” | 使用步骤缺失 | HTML 含内嵌音频，但 GitHub 文件页显示源码；链接本身不是可执行网页入口。 | 中 | 文件链接正确，缺少首次使用说明。 | 改写 | “Download either player HTML file and open it in a browser; the audio is embedded. GitHub displays the HTML source.” |
| resources:5，`as agreed on November 7`；resources:15，`Both GuitarSet archives were downloaded and verified on November 7` | 会话遗留、信息组织 | 旧下载过程无法帮助新克隆者；现有实验还使用 IDMT。 | 中 | 适合作为原始日志，不适合当前资源入口。 | 改写 | “The current experiments use GuitarSet for development and IDMT-SMT-Guitar for external comparisons.” 随后给 GuitarSet 下载命令及 IDMT 复现链接。 |
| resources:17，`Downloaded archives and audio are kept locally rather than uploaded to the source repository.` | 内容一致性 | 完整数据目录被忽略，但保存的 HTML 明确内嵌个别录音；原文容易使读者以为所有仓库文件均不含音频。 | 中 | 其归档意图正常，但范围过宽。 | 改写 | “Dataset archives remain local. The saved HTML players embed individual recordings with source attribution.” |
| resources:32，`The course progress report is due November 14` | 已过期安排 | 当前任务为进度版发布，沿用旧日期作为当前安排会误导；本轮不推测新的截止日期。 | 中 | 曾是历史安排，现应改成当前文档指引。 | 改写 | “The course requires submission as a single 3–4 page PDF; the remaining project schedule is in the README.” |
| .gitignore:6–20，数据目录排除规则 | 发布范围 | IDMT 复现说明下载 ZIP 到根目录；原规则未排 ZIP。report 目录已有编译日志。 | 中 | 原规则有用，但覆盖范围不足。 | 改写 | 增加 `*.zip` 及 report 的日志/辅助文件规则，保留 PDF、TeX、bbl、bib 和图。 |
| README 的研究问题、结果、原始 PI、剩余目标和 19 条参考文献 | 必要保留 | 本轮任务是发布入口；不存在需要更改数据或研究叙事的新证据。 | 高 | 属于正常、必要的研究表述。 | 保留 | 保留原文；逐节字节比较通过。 |

## 三、综合建议与验证

已将新克隆者需要的下载细节放入 resources，并让 README 只保留入口和下一步命令。修改后的资源说明依次解释数据用途、获取方式、复现入口和报告文件；不再复述会话决定和旧截止日期。播放器说明对应实际内嵌音频，不添加不存在的托管演示服务。

完成的检查：

- 两个原始 ZIP 的 MD5 分别为 `b39b78e63d3446f2e54ddb7a54df9b10` 与 `275966d6610ac34999b58426beb119c3`，匹配本地来源记录；每包 360 个文件且无额外目录层。
- 新增 shell 代码块通过 `bash -n`；README 与 resources 的相对文件链接均存在。
- 使用独立检出的 `make_manifest` 和现有本地数据，输出到临时目录，得到 119 条 development、59 条 test、2 条排除记录。未修改原始数据或原保存划分。
- `git check-ignore --no-index` 验证根 ZIP 和编译日志会被排除，PDF、TeX、bbl、bib 及图保留。
- README 的 Project description、Data and tools、Method、Evaluation and results、Related work、Christopher Xu、Remaining work、References 与原项目逐节一致；仅 Running the code 改动。
- 未重新执行依赖安装、全量网络下载或大型识别实验；这是入口文案和已有本地材料的验证，不应称为一次全新机器的端到端复现。

无需追加新文献；本轮没有增加需要 overview 支撑的领域论述。发现的写作特征不能证明文本由 AI 生成。
