#!/usr/bin/env python
"""
思维链塑形演示：同一个任务 × 三种塑形方式，直观对比思维链差异。

  - bare         ：无塑形（模型默认思维链）
  - dual-persona ：有结构·双人格辩论（说话人标记）
  - tics         ：无结构·口癖引导（第一人称 we need to）

用法：python demo.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

MODEL = os.environ.get("COT_MODEL", "deepseek-v4-flash")
CONFIG_PATH = Path(os.environ["USERPROFILE"]) / ".pi" / "agent" / "models.json"

# 同一个任务：一个天然有"拉扯"的决策问题
TASK = "我现在有 10 万存款，工作稳定但不喜欢。我该不该辞职去做独立游戏？给我一个建议。"

MODES = {
    "bare": "",
    "dual-persona": """你是"双顾问"，体内有两位立场对立的顾问：
"稳"——保守，重视风险和长期稳定。
"快"——激进，重视梦想和行动。

回复前必须在 think 标签内辩论，固定结构如下，必须遵守，不得省略：

[判断] 用户决策的核心矛盾。
[稳] 提出稳妥建议。
[快] 反驳并提出激进建议。
[争执] 双方交锋一轮。
[裁定] 谁赢及原因。

示例（任务为"要不要养猫"时）：
[判断] 想养又怕麻烦，矛盾在陪伴需求 vs 时间成本。
[稳] 先算时间经济账，养猫是十年责任。
[快] 别想太多，养了才有动力，快乐最重要。
[争执] 稳：冲动养了又弃养更糟。快：顾虑太多会错过美好。
[裁定] 稳胜出，先试养验证意愿再决定。

规则：
1. 上述 [判断][稳][快][争执][裁定] 只出现在思维链（think 标签）中，必须完整出现，不得省略。
2. 整个辩论在 think 标签内完成，最终回答里不得出现任何 [方括号] 标记，也不得复述辩论过程。
3. [裁定] 确定后，最终回答按胜者立场、用自然段落给出建议。
4. 最终回答是给用户看的正文，用自然语言写，不掺杂思考内容。""",
    "tics": """你在思考时，请用第一人称、可执行的句式展开推理：
- 用 "we need to ..." 描述每一个具体动作，一句说清一个动作。
- 穿插 I'll（下一步）、I can（可行方案）、I need（必须做的）、I should（应做的）。
- 短句、口语化，一步一句。
- 不要用 "let me ..." 开头，用 "we need to ..." 代替。""",
}


def load_api_config():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    provider = config["providers"].get("deepseek") or next(iter(config["providers"].values()))
    return provider["baseUrl"].rstrip("/"), provider.get("apiKey", "")


def run(base_url, api_key, system):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": TASK})
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "thinking": {"type": "enabled"},
        "reasoning_effort": "max",
    }
    req = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(req, timeout=600) as resp:
        body = json.loads(resp.read().decode("utf-8", errors="replace"))
        msg = body["choices"][0]["message"]
        return {
            "reasoning": msg.get("reasoning_content") or "",
            "content": msg.get("content") or "",
            "latency": round(time.perf_counter() - started, 1),
        }


def main():
    base_url, api_key = load_api_config()
    print(f"任务：{TASK}\n模型：{MODEL}  reasoning_effort=max\n")
    for name, system in MODES.items():
        r = run(base_url, api_key, system)
        reasoning, content = r["reasoning"], r["content"]
        bar = "=" * 66
        print(f"\n{bar}\n【{name}】  {r['latency']}s  思维链 {len(reasoning)} 字\n{bar}")
        print("— 思维链（前 700 字）—")
        print(reasoning[:700])
        if len(reasoning) > 700:
            print(f"...（共 {len(reasoning)} 字，截断）")
        print("\n— 最终回答（前 300 字）—")
        print(content[:300])


if __name__ == "__main__":
    main()
