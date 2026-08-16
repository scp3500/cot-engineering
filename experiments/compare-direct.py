#!/usr/bin/env python
"""
对比：裸问 vs 直接思考控制（方式二）
题目：LeetCode 42 接雨水（Trapping Rain Water）

  - bare   ：无 system prompt，直接给题
  - direct ：方式二，命令模型"怎么想"（顺序/多解法/权衡/验证），不要求标记

用法：python compare-direct.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

MODEL = os.environ.get("COT_MODEL", "deepseek-v4-flash")
CONFIG_PATH = Path(os.environ["USERPROFILE"]) / ".pi" / "agent" / "models.json"

TASK = """给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。

示例 1：
输入：height = [0,1,0,2,1,0,1,3,2,1,2,1]
输出：6

示例 2：
输入：height = [4,2,0,3,2,5]
输出：9

请实现函数 trap(height)，返回能接的雨水总量。"""

DIRECT_SYSTEM = """思考时必须按以下方式：

1. 先分析问题：明确输入、输出、边界条件（空数组、单元素、单调递增/递减）。
2. 再列举至少 2 种解法，分析各自的时间复杂度和空间复杂度。
3. 权衡后选定一种，说明理由。
4. 实现代码，并验证示例和边界情况。

用自然语言思考，不要写任何标记。"""


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
        "reasoning_effort": os.environ.get("COT_EFFORT", "max"),
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
    print(f"题目：LeetCode 42 接雨水\n模型：{MODEL}  reasoning_effort=max  temperature=0\n")
    for name, system in (("bare", ""), ("direct", DIRECT_SYSTEM)):
        r = run(base_url, api_key, system)
        reasoning, content = r["reasoning"], r["content"]
        bar = "=" * 66
        print(f"\n{bar}\n【{name}】  {r['latency']}s  思维链 {len(reasoning)} 字\n{bar}")
        print("— 思维链（前 900 字）—")
        print(reasoning[:900])
        if len(reasoning) > 900:
            print(f"...（共 {len(reasoning)} 字，截断）")
        print("\n— 最终代码（前 800 字）—")
        print(content[:800])


if __name__ == "__main__":
    main()
