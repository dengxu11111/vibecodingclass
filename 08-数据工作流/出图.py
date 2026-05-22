"""第 08 章 · 出图脚本：对照「出图 Skill」的实现。

读 data/processed/<file>_clean.csv，
→ 按月统计发文量（柱状图）
→ Top 5 category 分布（条形图）
→ 保存到 outputs/

用法：
    python 出图.py
    python 出图.py data/processed/arxiv_xxx_clean.csv
"""

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # 没有 GUI 也能跑
import matplotlib.pyplot as plt


def find_latest_clean(base: Path) -> Path | None:
    files = sorted(
        (base / "data" / "processed").glob("*_clean.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def main():
    ap = argparse.ArgumentParser(description="给清洗后的 arXiv 数据画图")
    ap.add_argument("input", nargs="?", help="清洗后 csv 路径；不给就自动找最新")
    args = ap.parse_args()

    base = Path(__file__).parent.parent
    in_path = Path(args.input) if args.input else find_latest_clean(base)
    if not in_path or not in_path.exists():
        print("[错误] 找不到清洗后 csv。先跑 数据清洗.py")
        sys.exit(1)

    print(f"→ 读：{in_path}")
    with in_path.open("r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("[错误] 空文件")
        sys.exit(1)

    out_dir = base / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. 按月柱状图
    months: Counter = Counter()
    for r in rows:
        d = r.get("published_date", "")
        if len(d) >= 7:
            months[d[:7]] += 1

    keys = sorted(months.keys())
    values = [months[k] for k in keys]

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(keys, values, color="#4C78A8")
    ax.set_title(f"arXiv submissions by month  (n={len(rows)})")
    ax.set_xlabel("month")
    ax.set_ylabel("paper count")
    ax.tick_params(axis="x", rotation=70, labelsize=7)
    plt.tight_layout()
    p1 = out_dir / "趋势_按月发文量.png"
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    print(f"  写 {p1}")

    # 2. Top 5 分类
    if "category" in rows[0]:
        cats = Counter(r.get("category", "?") for r in rows).most_common(8)
        labels = [c for c, _ in cats]
        counts = [n for _, n in cats]

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(labels[::-1], counts[::-1], color="#F58518")
        ax.set_title("Top categories")
        ax.set_xlabel("paper count")
        plt.tight_layout()
        p2 = out_dir / "分类_Top8.png"
        fig.savefig(p2, dpi=120)
        plt.close(fig)
        print(f"  写 {p2}")

    # 3. 一句话解读
    if keys:
        peak_month = max(months.items(), key=lambda x: x[1])
        print()
        print(f"[解读] 峰值月份：{peak_month[0]}（{peak_month[1]} 篇）；"
              f"日期跨度：{keys[0]} → {keys[-1]}")


if __name__ == "__main__":
    main()
