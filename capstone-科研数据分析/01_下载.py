"""Capstone · 步骤 1：抓 Open-Meteo ERA5 archive 上中国主要城市的日均气温。

Open-Meteo 是 ERA5 reanalysis 的免费代理 API：
- 不需要 key、不需要 Copernicus 账号、不需要 VPN
- 数据底层就是 ECMWF ERA5（学术界标准气候再分析数据集）
- API 文档：https://open-meteo.com/en/docs/historical-weather-api

默认抓 7 个中国城市 × 近 30 年 × 日均 2m 气温（1995-2024，共 30 个完整年）。

30 年是趋势分析的下限（WMO Climate Normal 也是 30 年）。课堂演示时如果想跑快一点，
用 `--start 2020-01-01 --end 2024-12-31` 跑 5 年烟测，但 5 年的样本 **不能** 接 02 / 03 步
做趋势结论——只能验证下载链路通。

产出：
    data/raw/era5_<city>.csv     每个城市一份
    data/raw/era5_all.csv        合并版

跑法：
    python 01_下载.py                                  # 默认 30 年，约 1-2 分钟
    python 01_下载.py --start 2020-01-01 --end 2024-12-31  # 5 年烟测，不接 02 步
"""

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
API = "https://archive-api.open-meteo.com/v1/archive"

# 经纬度取自国家统计局 / 维基百科官方坐标
CITIES = [
    ("北京",     39.9042, 116.4074),
    ("上海",     31.2304, 121.4737),
    ("广州",     23.1291, 113.2644),
    ("西安",     34.3416, 108.9398),
    ("武汉",     30.5928, 114.3055),
    ("哈尔滨",   45.8038, 126.5350),
    ("乌鲁木齐", 43.8256,  87.6168),
]


def fetch_city(name: str, lat: float, lon: float, start: str, end: str) -> list[dict]:
    """抓某个城市某段时间的日均气温。"""
    qs = (
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start}&end_date={end}"
        f"&daily=temperature_2m_mean"
        f"&timezone=Asia%2FShanghai"
    )
    url = f"{API}?{qs}"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"[错误] {name} 抓取失败：{e.reason}")
        return []

    daily = data.get("daily") or {}
    dates = daily.get("time", [])
    temps = daily.get("temperature_2m_mean", [])
    if not dates:
        print(f"[警告] {name} 返回为空：{data.get('reason', '未知原因')}")
        return []

    return [
        {
            "city": name,
            "date": d,
            "lat": lat,
            "lon": lon,
            "temp_c": "" if t is None else f"{t:.2f}",
        }
        for d, t in zip(dates, temps)
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="1995-01-01",
                    help="起始日期，默认 1995-01-01（30 年窗口）")
    ap.add_argument("--end",   default="2024-12-31",
                    help="结束日期，默认 2024-12-31（30 个完整年）")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"→ 数据源：Open-Meteo (ERA5)，{args.start} → {args.end}")
    print(f"→ 城市：{len(CITIES)} 座")

    all_rows: list[dict] = []
    for name, lat, lon in CITIES:
        print(f"  抓 {name} ({lat:.2f}, {lon:.2f}) ...", end=" ", flush=True)
        rows = fetch_city(name, lat, lon, args.start, args.end)
        print(f"得 {len(rows)} 天")
        if not rows:
            continue

        # 单城市一份
        p = RAW_DIR / f"era5_{name}.csv"
        with p.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        all_rows.extend(rows)
        time.sleep(1.0)  # Open-Meteo 限流很宽松，sleep 1 秒以示尊重

    if not all_rows:
        print("[错误] 一个城市也没抓到。检查网络或 Open-Meteo 服务。")
        sys.exit(1)

    # 合并
    combined = RAW_DIR / "era5_all.csv"
    with combined.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader(); w.writerows(all_rows)

    print(f"\n[完成] 共 {len(all_rows)} 条 → {combined}")
    print("下一步：python 02_分析.py")


if __name__ == "__main__":
    main()
