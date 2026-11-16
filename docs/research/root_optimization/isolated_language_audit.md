## 一、整体观察

完整审阅本轮新增的 `chordrec/isolated.py` 草稿、适配器测试草稿和 `isolated_data_review.md`。已使用用户指定的 academic-language-audit 与 nature-writing 两项技能；Nature 路由为 manuscript / methods / method + experiments / en / generic。核对范围为源注释、文件名、选择规则、评价区间、官方数据说明及公开来源元数据，没有读取预测或评价结果。

主要写作要求是把新录音、孤立和弦任务与独立歌曲数量区分清楚。保留首次选取时间、文件校验和数据来源于单独清单；报告正文只需交代任务和区间。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| `isolated_data_review.md` 第一段：“They form 44 matched fingering, quality and shift groups, each recorded on two electric guitars.” | 样本单位 | 88 文件包含相同指型、质量和移调的成对演奏，不能作为 88 个新和弦进程解释。 | 高 | 是必要的样本结构说明。 | 保留 | 保留原文。 |
| 同文件第二段：“The reference spans the earliest note onset through the latest note offset” | 评价范围 | 该规则包含扫弦起始和衰减，且不把开头静音强行标成 N。 | 中 | 是复现指标分母所必需的表达。 | 保留 | 保留原文。 |
| 适配器 docstring：“All annotated pitch classes must equal that triad before it is accepted.” | 输入验证边界 | 实现检查整段注释音的音级集合，不证明所有时刻均同时奏出完整三和弦。 | 中 | 作为集合一致性检查可保留，配合阅读笔记说明时间边界。 | 保留 | 保留原文；数据说明已明确初始扫弦并非所有音同时起始。 |
| 数据说明“Sources and reading depth”中的编号差异 | 来源一致性 | 网页的 first/second 与档案目录及 PDF 相反；直接写 dataset1 而不注明来源会让读者选错材料。 | 中 | 说明一次即可，不必在主报告反复出现。 | 保留 | “Paths and guide section numbers identify the material here.” |

## 三、综合建议

只在孤立和弦范围内解释后续效果，并同时呈现两乐器和 44 个配对组。标注创建方法与边界精度未从所读指南找到，不补造保证；参考标签与音符集合一致只是静态核对。适配器测试验证时间范围、标签冲突和非法时间，不以测试通过代替识别性能。没有新增性能主张。

**发现的写作特征不能证明文本由 AI 生成。**
