"""Capstone · 步骤 1（CDS 路径）：直接从 Copernicus Climate Data Store 拉 ERA5。

这是 Open-Meteo 路径（`01_下载.py`）的**真实科研版**。区别：

- 走官方 Copernicus CDS API（不是 Open-Meteo 代理）
- 需要先在 https://cds.climate.copernicus.eu 注册账号，把 key 写进 `~/.cdsapirc`
- 拉的是 ERA5 monthly means（不是日均），单点为最近邻像元
- 数据可以精确说"来自 reanalysis-era5-single-levels-monthly-means dataset"，可投稿

默认下 7 城 × 2020-2024 × 月均 2m 气温（60 个月 × 7 城 = 420 行 CSV，~15 KB）。
**为什么是月均而不是日均**：CDS 拉日均要走 hourly + 时间聚合，请求大、排队久；
课程示例用 monthly_averaged_reanalysis 是最经济、最快出结果的选择。

跑法：
    pip install cdsapi          # 一次性
    python 01_下载_cds.py        # 默认 2020-2024
    python 01_下载_cds.py --start-year 2015 --end-year 2024   # 10 年

产出：
    data/raw/era5_cds_monthly.csv
    （字段：city, year, month, lat, lon, temp_c）

注意：
- 第一次跑某个数据集要先去 CDS 网站接受 Terms of Service（一次性，浏览器点）
- 排队时间不可控；课堂演示前请讲师提前跑过一次，把 CSV 放进 example/
"""

from __future__ import annotations

import argparse
import csv
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
RAW_DIR = HERE / "data" / "raw"

# 经纬度跟 Open-Meteo 路径完全一致
CITIES = [
    ("北京",     39.9042, 116.4074),
    ("上海",     31.2304, 121.4737),
    ("广州",     23.1291, 113.2644),
    ("西安",     34.3416, 108.9398),
    ("武汉",     30.5928, 114.3055),
    ("哈尔滨",   45.8038, 126.5350),
    ("乌鲁木齐", 43.8256,  87.6168),
]


def bounding_box(cities: list[tuple[str, float, float]], pad: float = 0.5) -> tuple[float, float, float, float]:
    """返回覆盖所有城市的 bbox：(N, W, S, E)，含 pad 度的缓冲。"""
    lats = [c[1] for c in cities]
    lons = [c[2] for c in cities]
    return (max(lats) + pad, min(lons) - pad, min(lats) - pad, max(lons) + pad)


def fetch_era5_monthly(start_year: int, end_year: int, out_nc: Path) -> None:
    """调 CDS API 拉 ERA5 monthly means 到 out_nc（NetCDF）。"""
    import cdsapi  # 延迟 import，便于无 cdsapi 环境也能 import 本文件

    north, west, south, east = bounding_box(CITIES)
    years = [str(y) for y in range(start_year, end_year + 1)]
    months = [f"{m:02d}" for m in range(1, 13)]

    print(f"→ 请求 ERA5 monthly means")
    print(f"  年份：{years[0]}-{years[-1]}（{len(years)} 年 × 12 月 = {len(years)*12} 条/像元）")
    print(f"  空间：N={north:.2f} W={west:.2f} S={south:.2f} E={east:.2f}")
    print(f"  变量：2m_temperature")
    print("→ CDS 排队 + 下载中，可能 3-10 分钟...")

    c = cdsapi.Client()
    c.retrieve(
        "reanalysis-era5-single-levels-monthly-means",
        {
            "product_type": "monthly_averaged_reanalysis",
            "variable": "2m_temperature",
            "year": years,
            "month": months,
            "time": "00:00",
            "area": [north, west, south, east],   # N, W, S, E
            "data_format": "netcdf",
            "download_format": "unarchived",
        },
        str(out_nc),
    )
    print(f"[OK] NetCDF 下载到：{out_nc} ({out_nc.stat().st_size / 1024:.1f} KB)")


def extract_city_points(nc_path: Path) -> list[dict]:
    """读 NetCDF，为每个城市抽最近邻像元的逐月气温，返回行列表。"""
    import xarray as xr  # 延迟 import

    ds = xr.open_dataset(nc_path)
    # ERA5 单变量名是 't2m'（开尔文）；月度集合在 valid_time / time 维上
    var_candidates = ["t2m", "2m_temperature"]
    varname = next((v for v in var_candidates if v in ds.data_vars), None)
    if varname is None:
        raise RuntimeError(f"NetCDF 里找不到 2m 气温变量，已有：{list(ds.data_vars)}")

    da = ds[varname]
    # 时间维可能叫 'time' / 'valid_time'
    time_dim = next((d for d in ["valid_time", "time"] if d in da.dims), None)
    lat_dim = "latitude" if "latitude" in da.dims else "lat"
    lon_dim = "longitude" if "longitude" in da.dims else "lon"

    rows: list[dict] = []
    for name, lat, lon in CITIES:
        pt = da.sel({lat_dim: lat, lon_dim: lon}, method="nearest")
        # 取实际像元中心，方便学员看
        actual_lat = float(pt[lat_dim].values)
        actual_lon = float(pt[lon_dim].values)
        times = pt[time_dim].values
        values_k = pt.values  # 开尔文

        for t, v_k in zip(times, values_k):
            # numpy datetime64 → year, month
            import numpy as np
            ts = np.datetime64(t, "M")
            year = int(str(ts)[:4])
            month = int(str(ts)[5:7])
            temp_c = float(v_k) - 273.15  # K → °C
            rows.append({
                "city": name,
                "year": year,
                "month": month,
                "lat_city": lat,
                "lon_city": lon,
                "lat_pixel": round(actual_lat, 4),
                "lon_pixel": round(actual_lon, 4),
                "temp_c": round(temp_c, 3),
            })
    ds.close()
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start-year", type=int, default=2020,
                    help="起始年，默认 2020")
    ap.add_argument("--end-year", type=int, default=2024,
                    help="结束年（含），默认 2024")
    ap.add_argument("--keep-nc", action="store_true",
                    help="保留下载的 NetCDF（默认下载到临时目录后删除）")
    args = ap.parse_args()

    try:
        import cdsapi  # noqa
        import xarray  # noqa
    except ImportError as e:
        print(f"[错误] 缺依赖：{e.name}")
        print("  安装：pip install cdsapi xarray netCDF4")
        return 2

    if not (Path.home() / ".cdsapirc").exists():
        print("[错误] 找不到 ~/.cdsapirc。")
        print("  到 https://cds.climate.copernicus.eu 注册账号，按页面提示")
        print("  把两行 `url:` 和 `key:` 存到 ~/.cdsapirc。")
        return 2

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 下载 NetCDF
    nc_path = (RAW_DIR / "era5_cds_raw.nc") if args.keep_nc \
              else Path(tempfile.gettempdir()) / f"era5_cds_{args.start_year}_{args.end_year}.nc"

    try:
        fetch_era5_monthly(args.start_year, args.end_year, nc_path)
    except Exception as e:
        print(f"[错误] CDS 请求失败：{e}")
        print("  常见原因：")
        print("    - 第一次用 ERA5：先去 https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means")
        print("      浏览器点 'Show Terms of Use' → 'Accept'，回来重跑")
        print("    - key 失效：检查 ~/.cdsapirc 里的 key 是否过期")
        print("    - 排队 / 服务繁忙：稍后重试")
        return 1

    # 2. 抽点 + 写 CSV
    print("\n→ 抽取 7 城最近邻像元 ...")
    try:
        rows = extract_city_points(nc_path)
    except Exception as e:
        print(f"[错误] NetCDF 解析失败：{e}")
        if not args.keep_nc:
            print(f"  原 NetCDF 留在：{nc_path}（用 --keep-nc 让脚本保留它）")
        return 1

    csv_path = RAW_DIR / "era5_cds_monthly.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"[OK] CSV 写入：{csv_path}")
    print(f"  行数：{len(rows)}（= {len(CITIES)} 城 × {(args.end_year - args.start_year + 1) * 12} 月）")
    print(f"  大小：{csv_path.stat().st_size / 1024:.1f} KB")

    if not args.keep_nc:
        try:
            nc_path.unlink()
        except OSError:
            pass

    print("\n下一步：把 CSV 拷到 example/，或自己写分析脚本（数据 schema 见 CSV 列头）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
