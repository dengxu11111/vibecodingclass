"""第 08 章 · 数据下载脚本：从 arXiv 公开 API 抓取论文 metadata。

为什么用 arXiv：
- 公开、不需要 API Key、对中国用户友好
- 返回 Atom XML，标准库 xml.etree 就能解
- 限速：每 3 秒 1 次请求，本脚本默认 sleep(3)

用法：
    python 下载脚本.py                              # 默认抓 "large language model" 50 篇
    python 下载脚本.py --keyword "graph neural network" --limit 200
    python 下载脚本.py --keyword "transformer" --limit 1000 --batch 200

产出：
    data/raw/arxiv_<keyword>.csv     原始数据，只读保存
"""

import argparse
import csv
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"a": "http://www.w3.org/2005/Atom"}
ARXIV_URL = "http://export.arxiv.org/api/query"
SLEEP_BETWEEN_BATCH = 3.0


def fetch_batch(keyword: str, start: int, batch_size: int) -> list[dict]:
    """抓一批论文 metadata。"""
    params = {
        "search_query": f'all:"{keyword}"',
        "start": start,
        "max_results": batch_size,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        print(f"[错误] 抓取失败：{e.reason}")
        return []

    root = ET.fromstring(raw)
    rows = []
    for entry in root.findall("a:entry", NS):
        rows.append({
            "arxiv_id": entry.findtext("a:id", "", NS).rsplit("/", 1)[-1],
            "title": entry.findtext("a:title", "", NS).strip().replace("\n", " "),
            "summary": entry.findtext("a:summary", "", NS).strip().replace("\n", " ")[:500],
            "published_date": entry.findtext("a:published", "", NS)[:10],
            "category": (entry.find("{http://arxiv.org/schemas/atom}primary_category") or ET.Element("x")).get("term", ""),
            "authors": " | ".join(
                a.findtext("a:name", "", NS)
                for a in entry.findall("a:author", NS)
            ),
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="抓 arXiv 论文 metadata")
    ap.add_argument("--keyword", default="large language model", help="搜索关键词")
    ap.add_argument("--limit", type=int, default=50, help="总抓取上限（默认 50）")
    ap.add_argument("--batch", type=int, default=100, help="每批多少条（≤ 2000，默认 100）")
    ap.add_argument("--out", default=None, help="输出 csv 路径")
    args = ap.parse_args()

    out_path = Path(args.out) if args.out else (
        Path(__file__).parent.parent / "data" / "raw" /
        f"arxiv_{args.keyword.replace(' ', '_')}.csv"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ 关键词：{args.keyword!r}")
    print(f"→ 目标：{args.limit} 篇，每批 {args.batch}")
    print(f"→ 输出：{out_path}")

    all_rows: list[dict] = []
    start = 0
    while len(all_rows) < args.limit:
        need = min(args.batch, args.limit - len(all_rows))
        print(f"  抓 start={start} size={need} ...", end=" ", flush=True)
        batch = fetch_batch(args.keyword, start, need)
        print(f"得 {len(batch)} 条")
        if not batch:
            print("[警告] 这一批返回空，提前结束")
            break
        all_rows.extend(batch)
        start += need
        if len(all_rows) < args.limit:
            time.sleep(SLEEP_BETWEEN_BATCH)

    if not all_rows:
        print("[错误] 一条都没抓到，请检查网络。")
        sys.exit(1)

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n[完成] 抓了 {len(all_rows)} 篇，写入 {out_path}")
    print("下一步：python 数据清洗.py")


if __name__ == "__main__":
    main()
