# 对比示例：裸问 vs 塑形

> 以下思维链为**示意**（展示两种模式的典型形态差异），不是真实模型输出。要获得真实对比，请运行 [`experiments/run_compare.py`](../experiments/run_compare.py)。

---

## 任务

> 写一个 Python 函数 `group_mean(rows, key_col, value_col)`：`rows` 是字典列表（每行一条记录），按 `key_col` 分组，对 `value_col` 求均值。值缺失或无法转为数字的跳过；某组无有效值时该组均值记为空。

---

## 裸问：散乱的思维链（示意）

```text
嗯，需要按 key 分组，用字典吧，defaultdict 应该可以。
然后对每个组的值求和再除以个数。要注意 value 可能是字符串，得转 float。
缺失值要跳过……那就用 try 跳过好了。
还有除以零的情况，先不管了，应该不会出现。
直接写：

def group_mean(rows, key_col, value_col):
    from collections import defaultdict
    sums = defaultdict(float)
    counts = defaultdict(int)
    for row in rows:
        k = row.get(key_col)
        v = row.get(value_col)
        try:
            sums[k] += float(v)
            counts[k] += 1
        except (TypeError, ValueError):
            pass
    return {k: (sums[k] / counts[k] if counts[k] else None) for k in sums}
```

**特征**：没有阶段边界，想到哪写到哪；边界情况（除零、空输入）顺带处理；没有方案权衡，也没有事后验证。

---

## 塑形：说话人标记的思维链（示意）

```text
[判断] 写函数，难点是缺失值、空组和边界处理。
[第1轮] 各自提出方案
[稳] 逐项检查输入，空组返回None。
[快] 用defaultdict一行搞定。
[第2轮] 互相质疑
[稳] 键缺失会KeyError，值可能非数字。
[快] 加try跳过非数字，够用。
[第3轮] 修正立场、给出结论
[稳] 坚持显式记录空组，避免遗漏。
[快] 接受，语义确实更清楚。
[裁定] 采用稳派：显式处理边界，空组返回None。
```

**特征**：说话人标记可解析；两人格交锋暴露边界；裁定直接决定最终实现。

---

## 差异分析

| 维度 | 裸问 | 塑形 |
|------|------|------|
| 结构 | 平铺直叙，无边界 | 分阶段、有说话人标记 |
| 澄清 | 隐式假设，事后才发现 | 假设显式列出 |
| 设计 | 直接写，无方案权衡 | 至少两方案 + 权衡理由 |
| 验证 | 缺失或顺带 | 显式逐项检查 |
| 可检查性 | 只能读全文 | 可按标记定位每一步 |
| 可复现性 | 每次路径可能不同 | 路径稳定 |

**核心结论**：塑形不改变模型能力，只改变思考方式——同样的模型，思考被框定后，输出更完整、更可检查、更可复现。
