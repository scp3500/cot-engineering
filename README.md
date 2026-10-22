# CoT Engineering（思维链工程）

> **Chain-of-Thought Engineering** — a branch of prompt engineering that treats the reasoning chain as a designable object, not a black box.

**CoT Engineering** 是提示词工程的一个分支：DeepSeek V4 的思考过程可约束、可设计。我们给模型一套**受控的思考架构**——用多说话人标记把思考组织成可解析的结构，让思考**直接决定输出**。

---

## 一句话理解

- 普通提示词：告诉模型「做什么」。
- 思维链工程：再告诉模型「**怎么想**」——谁在思考、按什么顺序、谁拍板，且拍板结果直接决定最终输出。

## 为什么可行

DeepSeek V4（V4-Pro / V4-Flash）在 Thinking 模式下，用 `<think>` 标签隔开推理过程与最终回答。思考是自回归生成的文本，前面写出的内容会引导后续思考，所以能被提示词**框定和塑形**。

## 核心发现（实验验证）

**思维链标记的命中率，取决于「思考是否直接决定输出」。**

| 场景 | 标记命中率 | 原因 |
|------|-----------|------|
| 角色扮演 / 对话（谁赢谁说话） | **100%（25/25）** | 不走到裁定就无法输出 |
| 代码 / 产出（辩完还是要写代码） | 17%~100% 飘忽 | 辩论是"过场"，可跳过 |

完整实验数据与机理见 [`docs/findings.md`](docs/findings.md)。

## 快速开始

思维链塑形分三种方式，按需选择：

**方式一：有结构（显式标记，可解析）**
1. 角色扮演 / 决策 → [`docs/templates/roleplay-dual-persona.md`](docs/templates/roleplay-dual-persona.md)（25/25 验证）
2. 写代码 → [`docs/templates/code-build.md`](docs/templates/code-build.md)；修 bug → [`docs/templates/code-fix.md`](docs/templates/code-fix.md)
3. 复制 system prompt 粘贴到 DeepSeek V4 Thinking 模式，**代码类务必开深度思考（`reasoning_effort=max`）**

**方式二 / 三：无标记（直接控制思考 / 口癖引导）**
- [`docs/templates/style-tics.md`](docs/templates/style-tics.md)

## 目录结构

```
cot-engineering/
├── README.md
├── LICENSE
├── docs/
│   ├── overview.md                    # 总纲 / 元方法论
│   ├── design-principles.md           # 设计原则
│   ├── findings.md                    # 实验数据与核心规律（重要）
│   ├── templates/
│   │   ├── roleplay-dual-persona.md   # 有结构·说话人标记（100% 验证）
│   │   ├── code-build.md              # 有结构·写新功能（build 100% 验证）
│   │   ├── code-fix.md                # 有结构·修 bug
│   │   └── style-tics.md              # 无标记·直接控制 + 口癖
│   └── examples.md                    # 裸问 vs 塑形对比
└── experiments/
    ├── run_compare.py                 # 复现实验：裸问 vs 塑形
    └── README.md
```

## 复现实验

```bash
cd experiments
python run_compare.py
```

脚本从 `~/.pi/agent/models.json` 读取 DeepSeek API 配置，对同一任务跑「裸问 vs 塑形」，输出两者思维链对比。详见 [`experiments/README.md`](experiments/README.md)。

## 阅读顺序

1. [`docs/findings.md`](docs/findings.md) — 先看实验结论，知道什么有效、什么无效。
2. [`docs/templates/`](docs/templates/) — 直接抄模板用。
3. [`docs/overview.md`](docs/overview.md) + [`docs/design-principles.md`](docs/design-principles.md) — 再补原理。

## 元能力

本项目文档本身是**元指令**：把 [`docs/overview.md`](docs/overview.md) 喂给任意支持思考的模型，它就能据此为**新领域**（法律、医学、写作、数学……）生成结构合理的新模板。

## 相关工作

- [scp3500/oh-we-need](https://github.com/scp3500/oh-we-need) — DeepSeek V4 思维链引导（`we need to` 口癖路线，与本项目结构化标记路线互补）
- [yjh051108/dsh-routing-suite](https://github.com/yjh051108/dsh-routing-suite) — 运行时注入 × 思维模式路由

## License

[MIT](LICENSE)
