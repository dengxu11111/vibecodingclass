"""01_download.template.py · 跨学科可移植的下载步骤骨架

把这个文件 cp 到你自己项目的根，重命名为 `01_<你的领域>.py`，然后改 TODO 块。
什么都不改也能跑（会下载 1 条占位记录），跑通就开始按 TODO 改。

为什么这么写：
- 路径处理、CSV 写入、sleep 礼貌、错误兜底——这些 80% 的部分**不变**
- 数据源 URL、请求参数、字段名——这些 20% 的部分**由你填**
- 只依赖 Python 标准库，跑前不用装包

跑法：
    python 01_<你的领域>.py
    python 01_<你的领域>.py --limit 50

产出：
    data/raw/<你的领域>.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW_DIR = HERE / "data" / "raw"

# ============================================================
# TODO-1：填你的数据源
# ============================================================
# 选一个你能拿到的公开 API 或文件源。建议先选**零账号 / 零 key** 的：
#   - arXiv:       http://export.arxiv.org/api/query
#   - OpenAlex:    https://api.openalex.org/works
#   - Open-Meteo:  https://archive-api.open-meteo.com/v1/archive
#   - NASA POWER:  https://power.larc.nasa.gov/api/temporal/daily/point
#   - FRED:        https://api.stlouisfed.org/fred/series/observations  (需 key)
# 如果你的数据**已经在本地 CSV / NetCDF**，直接 read_csv 跳过 HTTP 部分

DATA_SOURCE_URL = "https://example.com/api/replace-me"
DOMAIN_NAME = "domain"   # 用在输出文件名，如 "arxiv" / "era5" / "deseq2"


# ============================================================
# TODO-2：定义"一条记录"长什么样
# ============================================================
# 这是你 CSV 每一行将有的字段。**保持小**——你能查回原始 API 的最少字段。
# 后面 02_analyze 也按这些字段名走。

FIELDNAMES = [
    "id",          # 主键，去重用
    "date",        # 时间维度（如果有的话）
    "value",       # 主测量值
    "category",    # 分组维度（可选）
    # TODO: 加你自己领域的字段
]


# ============================================================
# TODO-3：写抓取函数
# ============================================================
def fetch(limit: int) -> list[dict]:
    """抓 limit 条记录，返回符合 FIELDNAMES schema 的 dict 列表。

    至少要做到的事：
    1. 处理 HTTP 错误（urllib.error.URLError）—— 返回 [] 而不是崩
    2. 处理 API 速率限制 —— sleep N 秒，N 按对方文档来（arXiv 3s / Open-Meteo 1s）
    3. 处理 API 返回的字段名 ≠ 你的 FIELDNAMES —— 在这里映射
    4. 不许编数据：API 返回为空就返回 []，不要在这里造假记录
    """
    # ====== TODO: 改成你的真实抓取 ======
    # 例 1：HTTP API
    # url = f"{DATA_SOURCE_URL}?limit={limit}"
    # try:
    #     with urllib.request.urlopen(url, timeout=30) as resp:
    #         data = json.loads(resp.read().decode("utf-8"))
    # except urllib.error.URLError as e:
    #     print(f"[错误] 网络问题：{e.reason}")
    #     return []
    # # 字段名映射
    # rows = []
    # for it in data.get("results", []):
    #     rows.append({
    #         "id": it["id"],
    #         "date": it.get("publication_date", ""),
    #         "value": it.get("score", 0.0),
    #         "category": it.get("subject", ""),
    #     })
    # return rows

    # 例 2：本地 CSV / Excel
    # 直接 csv.DictReader，跳过 fetch，把 read_local() 当 fetch 用

    # 默认占位：返回一条假数据让脚手架跑得通——**真用时务必删掉**
    print("[警告] 你还没改 fetch()。返回一条占位记录。请尽快填 TODO。")
    return [{
        "id": "REPLACE-ME-1",
        "date": "2026-01-01",
        "value": 0.0,
        "category": "placeholder",
    }]


# ============================================================
# 通用部分（理论上不需要改）
# ============================================================
def main():
    ap = argparse.ArgumentParser(description=f"抓 {DOMAIN_NAME} 数据")
    ap.add_argument("--limit", type=int, default=20, help="抓取上限")
    ap.add_argument("--out", default=None, help="输出 csv 路径；不给就走默认 data/raw/")
    args = ap.parse_args()

    out_path = Path(args.out) if args.out else (RAW_DIR / f"{DOMAIN_NAME}.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ 数据源：{DATA_SOURCE_URL}")
    print(f"→ 输出：{out_path}")
    print(f"→ 目标：{args.limit} 条")

    t0 = time.time()
    rows = fetch(args.limit)
    elapsed = time.time() - t0

    if not rows:
        print("[错误] 没抓到任何记录。检查网络 / API / TODO 是否填好。")
        sys.exit(1)

    # 检查字段一致性
    expected = set(FIELDNAMES)
    actual = set(rows[0].keys())
    if expected != actual:
        print(f"[警告] FIELDNAMES 与 fetch() 返回字段不一致：")
        print(f"  FIELDNAMES = {sorted(expected)}")
        print(f"  fetch keys = {sorted(actual)}")

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\n[完成] 抓了 {len(rows)} 条 ({elapsed:.1f}s) → {out_path}")
    print(f"下一步：python 02_analyze.py")


if __name__ == "__main__":
    main()
