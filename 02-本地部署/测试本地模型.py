"""调本地 Ollama 的最小脚本——验证模型确实跑起来了。

用法：
    python 测试本地模型.py                          # 用默认提问
    python 测试本地模型.py "你的问题"
    python 测试本地模型.py --model qwen3.5:0.6b "你好"

Ollama 未启动时给出友好提示，而不是 traceback。
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:4b"
DEFAULT_PROMPT = "用一句话介绍你自己。"


def call_ollama(host: str, model: str, prompt: str, timeout: int = 60) -> str:
    """调 Ollama 的 /api/generate 接口（非流式，简单看输出）。"""
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("response", "<空响应>")


def list_models(host: str) -> list[str]:
    with urllib.request.urlopen(f"{host}/api/tags", timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [m["name"] for m in data.get("models", [])]


def main():
    ap = argparse.ArgumentParser(description="测试本地 Ollama 模型")
    ap.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--host", default=DEFAULT_HOST)
    args = ap.parse_args()

    print(f"→ 连接 {args.host} ...")
    try:
        models = list_models(args.host)
    except urllib.error.URLError as e:
        print(f"\n[错误] 连不上 Ollama：{e.reason}")
        print("请先：")
        print("  1. 装 Ollama https://ollama.com/download")
        print("  2. 拉一个模型：ollama pull qwen3.5:4b")
        print("  3. 确认 Ollama 服务在跑：ollama list")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] 通信异常：{e}")
        sys.exit(1)

    if not models:
        print("[提示] Ollama 起来了但没有装任何模型。先跑：")
        print("  ollama pull qwen3.5:4b")
        sys.exit(1)

    print(f"  已装模型：{', '.join(models)}")
    if args.model not in models:
        print(f"[提示] {args.model} 没装，自动改用 {models[0]}")
        args.model = models[0]

    print(f"→ 用 {args.model} 回答：{args.prompt!r}")
    print("-" * 60)
    try:
        answer = call_ollama(args.host, args.model, args.prompt)
        print(answer.strip())
    except Exception as e:
        print(f"[错误] 推理失败：{e}")
        sys.exit(1)
    print("-" * 60)
    print("[完成] 本地模型可用。下一步：打开 http://localhost:3000 用 Open WebUI 聊。")


if __name__ == "__main__":
    main()
