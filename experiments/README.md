# 复现实验：裸问 vs 塑形

用**同一个编程任务**，分别以「裸提示」和「塑形提示」各调用一次 DeepSeek V4，输出两者的思维链（`reasoning_content`）与最终回答（`content`），直观对比思维链结构的差异。

## 依赖

- Python 3（仅用标准库，无需安装第三方包）
- 一个可用的 DeepSeek API key（已配置在 `~/.pi/agent/models.json`）

## 运行

```bash
cd experiments
python run_compare.py     # 裸问 vs 塑形 对比
python demo.py            # 同一任务 × 三种塑形方式 直观演示
python compare-direct.py  # 裸问 vs 直接思考控制（LeetCode 42）
```

脚本会：

1. 从 `~/.pi/agent/models.json` 读取 provider `deepseek` 的 `baseUrl` 和 `apiKey`。
2. 用同一任务各调用一次：
   - **bare**：无 system prompt，直接给需求。
   - **shaped**：system prompt 使用 [`code-build` 模板](../docs/templates/code-build.md)。
3. 在终端打印两者的思维链和回答，并把完整结果存到 `results/compare_<时间戳>.json`。

## 演示脚本 demo.py

对**同一个任务**用三种塑形方式各跑一次，并排对比思维链差异：

- `bare`：无塑形（模型默认思维链）
- `dual-persona`：有结构·双人格辩论（说话人标记）
- `tics`：无结构·口癖引导（第一人称 we need to）

最直观地展示"思维链可塑"：同一个模型，三种完全不同的"大脑"。

## 对比脚本 compare-direct.py

同一道 LeetCode 42 接雨水，对比「裸问」与「直接思考控制（方式二）」：

```bash
COT_EFFORT=max python compare-direct.py   # 高思考挡（默认）
COT_EFFORT=low python compare-direct.py   # 低思考挡
```

实测数据见 [`docs/findings.md`](../docs/findings.md) 第 4.6 节。

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COT_MODEL` | `deepseek-v4-flash` | 模型名 |
| `COT_EFFORT` | `max` | `reasoning_effort`：`low` / `high` / `max`（仅 run_compare.py） |

## 怎么读结果

1. **看 `reasoning_content`**：这是思维链本体。
   - `bare`：通常平铺直叙、无阶段边界。
   - `shaped`：应出现 `<understand>` `<clarify>` `<design>` `<implement>` `<verify>` 阶段标签，并按顺序推进。
2. **看 `content`**：最终回答应只含代码和简要说明，不出现标记。
3. 脚本末尾会自动检测 `shaped` 思维链里出现的关键标记数量，用于判断塑形是否生效。

## 注意事项

- `results/` 已加入 `.gitignore`，实验结果不入库（可复现，需要时重新跑即可）。
- 思维链有随机性，单次结果仅供参考；要下结论建议多次运行观察趋势。
