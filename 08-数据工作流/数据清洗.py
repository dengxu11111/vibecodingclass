"""第 08 章 · 数据清洗脚本：对照「数据清洗 Skill」的实现。

读 data/raw/<file>.csv，
→ 列名规范化（小写下划线）
→ 按 arxiv_id 去重
→ 按 published_date 升序
→ 写 data/processed/<file>_clean.csv
→ 打印清洗报告

用法：
    python 数据清洗.py                                 # 自动找最新 raw csv
    python 数据清洗.py data/raw/arxiv_xxx.csv
"""

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


def normalize_col(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def find_latest_raw(base: Path) -> Path | None:
    raws = sorted((base / "data" / "raw").glob("arxiv_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return raws[0] if raws else None


def main():
    ap = argparse.ArgumentParser(description="清洗 arXiv 抓回来的 CSV")
    ap.add_argument("input", nargs="?", help="原始 csv 路径；不给就自动找最新一份")
    ap.add_argument("--key", default="arxiv_id", help="去重主键列名")
    ap.add_argument("--date-col", default="published_date", help="时间列名")
    args = ap.parse_args()

    base = Path(__file__).parent.parent
    in_path = Path(args.input) if args.input else find_latest_raw(base)
    if not in_path or not in_path.exists():
        print("[错误] 找不到原始 csv。先跑：python 下载脚本.py")
        sys.exit(1)

    print(f"→ 读：{in_path}")
    with in_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        orig_fieldnames = reader.fieldnames or []

    orig_count = len(rows)
    if orig_count == 0:
        print("[错误] 空文件")
        sys.exit(1)

    # 1. 列名规范化
    name_map = {n: normalize_col(n) for n in orig_fieldnames}
    rows = [{name_map[k]: v for k, v in r.items()} for r in rows]
    fieldnames = [name_map[n] for n in orig_fieldnames]

    # 2. 去重
    seen: set[str] = set()
    deduped = []
    for r in rows:
        k = r.get(args.key, "")
        if k and k in seen:
            continue
        seen.add(k)
        deduped.append(r)
    dup_removed = orig_count - len(deduped)

    # 3. 关键列缺失 → 删
    before_na = len(deduped)
    deduped = [r for r in deduped if r.get(args.key) and r.get(args.date_col)]
    na_removed = before_na - len(deduped)

    # 4. 时间升序
    deduped.sort(key=lambda r: r.get(args.date_col, ""))

    # 5. 写出
    out_dir = base / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (in_path.stem + "_clean.csv")
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    # 6. 报告
    print()
    print("## 清洗报告")
    print()
    print("| 项 | 数量 |")
    print("| --- | --- |")
    print(f"| 原始行数 | {orig_count} |")
    print(f"| 重复删除 | {dup_removed} |")
    print(f"| 关键列缺失删除 | {na_removed} |")
    print(f"| 清洗后行数 | {len(deduped)} |")
    print()

    if "category" in fieldnames:
        cats = Counter(r.get("category", "") for r in deduped)
        print("### Top 5 category")
        for c, n in cats.most_common(5):
            print(f"  - {c}: {n}")

    if "published_date" in fieldnames and deduped:
        print()
        print(f"### 日期跨度：{deduped[0].get('published_date')} → {deduped[-1].get('published_date')}")

    print()
    print(f"[完成] 写入 {out_path}")
    print("下一步：python 出图.py")


if __name__ == "__main__":
    main()
