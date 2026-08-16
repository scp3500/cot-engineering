#!/usr/bin/env python
"""
思维链塑形演示（代码版）：同一个编程任务 × 三种塑形方式，直观对比思维链差异。

  - bare         ：无塑形（模型默认思维链）
  - dual-persona ：有结构·双工程师辩论（说话人标记 + 轮数）
  - tics         ：无结构·口癖引导（第一人称 we need to）

用法：python code-demo.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

MODEL = os.environ.get("COT_MODEL", "deepseek-v4-flash")
CONFIG_PATH = Path(os.environ["USERPROFILE"]) / ".pi" / "agent" / "models.json"

# 同一个代码任务：IPv4 校验，有"前导零/边界/格式"的真实分歧可辩
TASK = """写一个 Python 函数 is_valid_ipv4(s)，判断字符串是否是合法 IPv4 地址。
要求处理边界：前导零（如 01.2.3.4）、每段范围 0-255、必须恰好四段、非数字字符。"""

MODES = {
    "bare": "",
    "dual-persona": """你是"双工程师"，体内有两位立场对立的工程师：
"稳"——保守，重视代码正确性、边界处理和可维护性。
"快"——激进，重视简洁实现和快速交付。

回复前必须在 think 标签内辩论。固定结构如下，必须遵守，不得省略：

[判断] 任务类型与核心难点。

[第1轮] 各自提出方案
[稳] 提出稳妥方案。
[快] 反驳并提出更简洁的方案。

[第2轮] 互相质疑
[稳] 质疑对方方案的漏洞。
[快] 回应并反质疑。

[第3轮] 修正立场、给出结论
[稳] 修正或坚持自己的方案。
[快] 修正或坚持自己的方案。

[裁定] 采用谁的方案及原因。

示例（任务为"写一个求平均值的函数"时）：
[判断] 写函数，难点是空列表与非法输入。
[第1轮] 各自提出方案
[稳] 逐项检查输入，空列表返回None。
[快] 一行三元表达式，空列表返回0。
[第2轮] 互相质疑
[稳] 返回0会掩盖"无数据"的事实。
[快] 需求只说别报错，0更简单。
[第3轮] 修正立场、给出结论
[稳] 同意加判断，但坚持None语义。
[快] 接受None，语义确实更清楚。
[裁定] 采用返回None，加空列表判断。

规则：
1. 上述标记只出现在思维链（think 标签）中，必须完整出现，不得省略。
2. 整个辩论在 think 标签内完成，最终回答里不得出现任何 [方括号] 标记，也不得复述辩论过程。
3. [裁定] 确定后，最终代码必须严格按该方案实现，不得混合或折中。
4. 最终回答只输出代码和必要说明，用自然语言写。""",
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
    print(f"任务：{TASK}\n模型：{MODEL}  reasoning_effort=max  temperature=0\n")
    for name, system in MODES.items():
        r = run(base_url, api_key, system)
        reasoning, content = r["reasoning"], r["content"]
        bar = "=" * 66
        print(f"\n{bar}\n【{name}】  {r['latency']}s  思维链 {len(reasoning)} 字\n{bar}")
        print("— 思维链（前 800 字）—")
        print(reasoning[:800])
        if len(reasoning) > 800:
            print(f"...（共 {len(reasoning)} 字，截断）")
        print("\n— 最终代码（前 600 字）—")
        print(content[:600])


if __name__ == "__main__":
    main()
