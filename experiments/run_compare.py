#!/usr/bin/env python
"""
对比实验：裸问 vs 塑形（思维链工程）

对同一个编程任务，分别用两种提示词调用 DeepSeek V4：
  - 裸问（bare）：无 system prompt，直接给需求
  - 塑形（shaped）：system prompt 使用 code-build 模板（受控思考架构）

输出两者的 reasoning_content（思维链）与 content（最终回答），
用于对比思维链结构的差异。

用法：
    python run_compare.py

配置：
    - 自动从 ~/.pi/agent/models.json 读取 provider "deepseek" 的 baseUrl/apiKey
    - 环境变量 COT_MODEL 可覆盖模型名（默认 deepseek-v4-flash）
    - 环境变量 COT_EFFORT 可覆盖 reasoning_effort（默认 max）
"""

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODEL = os.environ.get("COT_MODEL", "deepseek-v4-flash")
EFFORT = os.environ.get("COT_EFFORT", "max")
CONFIG_PATH = Path(os.environ["USERPROFILE"]) / ".pi" / "agent" / "models.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "results"

# 同一个编程任务
TASK = """写一个 Python 函数 group_mean(rows, key_col, value_col)：
rows 是字典列表（每行一条记录），按 key_col 分组，对 value_col 求均值。
值缺失或无法转为数字的跳过；某组无有效值时该组均值记为 None。"""

# 塑形 system prompt（与 docs/templates/code-build.md 保持一致）
SHAPED_SYSTEM = """你是一名资深软件工程师。在动手前，请在思考中严格按以下阶段推进，每个阶段用对应标签开头：

<understand> 理解需求：明确要做什么、边界和约束。
<clarify> 澄清：找出歧义和缺失信息。能合理假设的就假设并记录；遇到无法合理假设的关键歧义，停止并直接向用户提问。
<design> 设计：给出至少两个可行方案，从正确性、简洁性、可维护性角度权衡，选定一个并说明理由。
<implement> 实现：按选定方案写出完整、最小、清晰的代码。
<verify> 验证：检查代码正确性、边界情况和是否满足需求；发现问题就回到 <implement> 修正。

规则：
1. 严格按顺序推进，不跳步、不混步。
2. 这些阶段标签只用于组织你的思考过程，最终回答中不要输出任何阶段标签。
3. 最终回答只包含代码和必要的简要说明。"""


def load_api_config():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    provider = config["providers"].get("deepseek")
    if not provider:
        provider = next(iter(config["providers"].values()))
    base_url = provider["baseUrl"].rstrip("/")
    api_key = provider.get("apiKey", "")
    return base_url, api_key


def request_once(base_url, api_key, system, user):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,
        "thinking": {"type": "enabled"},
        "reasoning_effort": EFFORT,
    }
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            body = json.loads(response.read().decode("utf-8", errors="replace"))
            choice = body.get("choices", [{}])[0]
            message = choice.get("message", {})
            return {
                "ok": True,
                "reasoning_content": message.get("reasoning_content") or "",
                "content": message.get("content") or "",
                "finish_reason": choice.get("finish_reason"),
                "usage": body.get("usage"),
                "latency_seconds": round(time.perf_counter() - started, 3),
            }
    except urllib.error.HTTPError as error:
        return {
            "ok": False,
            "http_status": error.code,
            "error": error.read().decode("utf-8", errors="replace"),
        }
    except Exception as error:
        return {"ok": False, "error": f"{type(error).__name__}: {error}"}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    base_url, api_key = load_api_config()
    print(f"model={MODEL}  effort={EFFORT}  base_url={base_url}", flush=True)

    results = {}
    for name, system in (("bare", ""), ("shaped", SHAPED_SYSTEM)):
        print(f"\n=== {name} ===", flush=True)
        record = request_once(base_url, api_key, system, TASK)
        results[name] = record
        if record["ok"]:
            print(f"latency={record['latency_seconds']}s", flush=True)
            print("--- reasoning_content ---", flush=True)
            print(record["reasoning_content"][:2000], flush=True)
            print("--- content ---", flush=True)
            print(record["content"][:2000], flush=True)
        else:
            print(f"FAILED: {record.get('error') or record.get('http_status')}", flush=True)

    report = {
        "model": MODEL,
        "task": TASK,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "bare": results["bare"],
        "shaped": results["shaped"],
    }
    out_path = OUTPUT_DIR / f"compare_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nsaved: {out_path}", flush=True)

    shaped_reasoning = results["shaped"].get("reasoning_content") or ""
    tags = ["<understand>", "<clarify>", "<design>", "<implement>", "<verify>"]
    found = [t for t in tags if t in shaped_reasoning]
    print(f"\nshaped 思维链中出现的阶段标签: {found}", flush=True)
    if len(found) >= 4:
        print("塑形生效：思维链按阶段标签推进。", flush=True)
    else:
        print("提示：塑形效果不明显，可尝试调整 temperature 或 COT_EFFORT。", flush=True)


if __name__ == "__main__":
    main()
