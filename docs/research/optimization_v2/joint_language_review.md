## 一、整体观察

实际审阅 `joint_review.json` 的范围、结论和说明字段，以及 `review_joint.py` 的文档字符串和注释。数字经脚本逐项重算四条开发分支的 30 个设置，并以三个开发录音、两种方法核对完整区间评分。使用 `academic-language-audit` 与用户指定的 `/home/cx/AI_QEC/AI_QEC/.agents/skills/nature-writing/SKILL.md`；沿用已读核心和方法/实验片段。未读取旧测试集或 IDMT 数据、预测、得分。

## 二、逐条定位

| 具体位置及原文 | 问题类型 | 具体依据及对理解或论证的影响 | 修改优先级：高／中／低 | 是否可能属于正常学术表达及原因 | 建议：保留／核实／精简／改写 | 建议修改版本 |
| --- | --- | --- | --- | --- | --- | --- |
| joint_review.json conclusions：“All 30 saved setting summaries, including repeated baselines, reconcile …” | 核对范围 | 共 9+9+7+5 行，含重复控制；每行已核对总体、家族、演奏者的时长总和。 | 低 | 明确限定为记录一致性，没有声称 30 个独立方法或独立实验。 | 保留 | 保留原文。 |
| joint_review.json conclusions：“on the six checked recording/method pairs” | 验证强度 | 完整区间评价器与缓存评分仅在三个开发录音乘两种方法上独立交叉核对，最大差异 3.55e−15 秒。 | 低 | 保留抽查范围是必要而具体的证据边界。 | 保留 | 保留原文。 |
| 早期叙述字段：“+0.258444” | 末位舍入 | 精确差值为 +0.2584434103587996 个百分点，六位小数应为 +0.258443；不影响结果或门槛。 | 低 | 可以使用较少有效位，但应正确舍入；预先保存的计划应保留历史原样。 | 改写 | 后续报告使用 “+0.26 percentage points”；精确记录保留实际浮点值。 |

## 三、综合建议

Nature writing 路由为 manuscript / methods / method + experiments / en / generic。结论保持“分支数值重算 → 有限交叉核对 → 未通过门槛”的顺序；不把一致性检查写成一般正确性证明，也不把用于比较的真实标签上界写成可运行方法。旧 candidate 配置中的评价计划文字已由主代理修正；当前数字配置与 n1 一致。计时仍限于缓存实验，不产生端到端加速结论。

**发现的写作特征不能证明文本由 AI 生成。**
