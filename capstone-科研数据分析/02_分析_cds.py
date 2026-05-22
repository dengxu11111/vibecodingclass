"""Capstone · 步骤 2（CDS 路径）：把月均 CSV 聚合成年均 + 5 年均值表。

读 data/raw/era5_cds_monthly.csv（01_下载_cds.py 产）
→ data/processed/era5_cds_annual.csv     每城每年均温（12 月简单平均）
→ data/processed/era5_cds_summary.csv    每城 5 年均温 / 最低年 / 最高年
→ 打印 Markdown 概要

为什么不直接接 02_分析.py？
- 02_分析.py 处理的是日数据，要算月均再算年均；CDS 路径直接拿月均，跳过中间一步
- 5 年样本不够做 OLS 趋势（02_分析.py 有 ≥ 20 年安全闸），所以这里只出"年均 + 概要"
- 真要做趋势，把 01_下载_cds.py 的 --end-year 拉到 1995 或更早（CDS 排队会更久）

跑法：
    python 02_分析_cds.py
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
RAW_CSV = HERE / "data" / "raw" / "era5_cds_monthly.csv"
PROC_DIR = HERE / "data" / "processed"


def main() -> int:
    if not RAW_CSV.exists():
        print(f"[错误] 找不到 {RAW_CSV}。先跑：python 01_下载_cds.py")
        return 1

    PROC_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 读月均
    with RAW_CSV.open("r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"→ 读月均：{len(rows)} 行")

    # 2. 聚合到年均：city → year → [sum, count]
    annual: dict = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    cities_order: list[str] = []
    for r in rows:
        city = r["city"]
        if city not in cities_order:
            cities_order.append(city)
        try:
            year = int(r["year"])
            t = float(r["temp_c"])
        except (KeyError, ValueError):
            continue
        annual[city][year][0] += t
        annual[city][year][1] += 1

    # 3. 写年均 CSV
    annual_path = PROC_DIR / "era5_cds_annual.csv"
    with annual_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "year", "temp_c_mean", "months"])
        for city in cities_order:
            for y in sorted(annual[city].keys()):
                s, n = annual[city][y]
                w.writerow([city, y, f"{s / n:.3f}", n])

    # 4. 概要表：5 年均 + 最低 / 最高年
    summary_path = PROC_DIR / "era5_cds_summary.csv"
    summary_rows: list[dict] = []
    for city in cities_order:
        ys = sorted(annual[city].keys())
        means = [annual[city][y][0] / annual[city][y][1] for y in ys]
        mean_all = sum(means) / len(means)
        i_min = means.index(min(means))
        i_max = means.index(max(means))
        summary_rows.append({
            "city": city,
            "years": f"{ys[0]}-{ys[-1]}",
            "n_years": len(ys),
            "mean_temp_c": f"{mean_all:.3f}",
            "min_year": ys[i_min],
            "min_temp_c": f"{means[i_min]:.3f}",
            "max_year": ys[i_max],
            "max_temp_c": f"{means[i_max]:.3f}",
            "max_minus_min_c": f"{means[i_max] - means[i_min]:.3f}",
        })
    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)

    # 5. Markdown 概要
    print(f"\n## CDS · ERA5 monthly means 2020-2024 概要（7 城）\n")
    print("| 城市 | 窗口 | n | 均温 (°C) | 最冷年 / 温度 | 最暖年 / 温度 | 年差 (°C) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for r in summary_rows:
        print(f"| {r['city']} | {r['years']} | {r['n_years']} | "
              f"{r['mean_temp_c']} | {r['min_year']} / {r['min_temp_c']} | "
              f"{r['max_year']} / {r['max_temp_c']} | {r['max_minus_min_c']} |")

    print(f"\n[完成] 写入：")
    print(f"  - {annual_path}")
    print(f"  - {summary_path}")
    print(f"\n说明：")
    print(f"  - 数据来自 CDS API 的 ERA5 monthly means (单位 K，已转 °C)")
    print(f"  - 像元为城市最近邻（0.25° 分辨率），非站点观测")
    print(f"  - 5 年样本只能看年际波动，**不能**下趋势结论；要做 OLS 请重跑 01_下载_cds.py 拉 ≥ 20 年")
    return 0


if __name__ == "__main__":
    sys.exit(main())
