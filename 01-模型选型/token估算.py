"""估算一段文本的 token 数 + 各家模型的预估调用价格。

用法：
    python token估算.py "你要估算的中文/英文文本"
    python token估算.py --file 某段文本.txt

仓库里准备了 3 段不同形态的示例文本，可以直接试：
    python token估算.py --file 示例文本/中文摘要.txt          # ~505 token
    python token估算.py --file 示例文本/英文段落.txt          # ~193 token
    python token估算.py --file 示例文本/长输入_论文章节.txt   # ~1542 token

不装 tiktoken 也能跑——会退化到"字符数 / 1.5"的粗略估算。
"""

import argparse
import sys
from pathlib import Path

# 价格表 —— **教学估算，以官网为准**（API 价格随时变，用之前过一遍 模型对比表.md 里的官方链接）
# DeepSeek / Qwen / Gemini 等供应商有分段计费 / 缓存命中折扣，这里取的是最常见档位
PRICING = {
    "DeepSeek-V3":      {"input": 0.27, "output": 1.10, "context": 64_000,  "中文": "强"},
    "DeepSeek-R1":      {"input": 0.55, "output": 2.19, "context": 64_000,  "中文": "强（推理）"},
    "智谱 GLM-4.5":      {"input": 0.50, "output": 1.50, "context": 128_000, "中文": "强"},  # 官方 ¥ 计价，这里按汇率约估
    "Qwen3-Max (≤32K)": {"input": 1.20, "output": 6.00, "context": 32_000,  "中文": "强"},  # 长上下文档位另算
    "Claude Sonnet 4.6":{"input": 3.00, "output": 15.00, "context": 200_000, "中文": "好"},
    "Claude Opus 4.7":  {"input": 5.00, "output": 25.00, "context": 200_000, "中文": "好"},
    "Claude Haiku 4.5": {"input": 1.00, "output": 5.00,  "context": 200_000, "中文": "好"},
    "GPT-4.1":          {"input": 2.00, "output": 8.00,  "context": 1_000_000, "中文": "中"},
    "Gemini 2.5 Pro":   {"input": 1.25, "output": 10.00, "context": 200_000, "中文": "中"},  # >200K 加价
}


def count_tokens(text: str) -> tuple[int, str]:
    """估算 token 数。优先用 tiktoken，没有就退化到粗估。"""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")  # GPT-4 系编码，跨家粗估够用
        return len(enc.encode(text)), "tiktoken (cl100k_base)"
    except ImportError:
        # 粗估：中文每字约 1 token，英文每 1.5 字符约 1 token
        chinese = sum(1 for c in text if "一" <= c <= "鿿")
        other = len(text) - chinese
        return chinese + max(1, other // 2), "粗估（未安装 tiktoken）"


def estimate_cost(input_tokens: int, output_tokens: int) -> None:
    print(f"\n按【输入 {input_tokens:,} tok / 输出 {output_tokens:,} tok】计费的 API 成本：\n")
    print(f"  {'模型':<22}{'输入费':>10}{'输出费':>10}{'合计':>10}   上下文       中文")
    print("  " + "-" * 78)
    for name, p in PRICING.items():
        in_cost = input_tokens / 1_000_000 * p["input"]
        out_cost = output_tokens / 1_000_000 * p["output"]
        total = in_cost + out_cost
        print(
            f"  {name:<22}"
            f"${in_cost:>9.4f}"
            f"${out_cost:>9.4f}"
            f"${total:>9.4f}"
            f"   {p['context']:>7,}    {p['中文']}"
        )
    print()


def main():
    ap = argparse.ArgumentParser(description="估算文本 token 数 + 各家模型 API 价格")
    ap.add_argument("text", nargs="?", default=None, help="要估算的文本（也可用 --file）")
    ap.add_argument("--file", type=Path, help="从文件读取文本")
    ap.add_argument("--output", type=int, default=500, help="预估输出 token 数（默认 500）")
    args = ap.parse_args()

    if args.file:
        text = args.file.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        ap.print_help()
        sys.exit(1)

    n, method = count_tokens(text)
    print(f"文本长度：{len(text)} 字符")
    print(f"Token 数：{n:,}   （方法：{method}）")
    estimate_cost(n, args.output)

    print("提示：")
    print("  - 这只是单次调用的成本。Agent 流程通常会反复调多次，要乘以预期轮数。")
    print("  - 推理模型（R1 / o-series）的实际输出 token 包含思考链，会更贵。")
    print("  - 中文一个字平均 ≈ 1.3 token；英文一个 word ≈ 1.3 token。")


if __name__ == "__main__":
    main()
