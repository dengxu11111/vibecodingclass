"""Capstone · 步骤 3：出图。

读 data/processed/*
→ outputs/年均气温_折线.png       7 城市逐年折线（主线 30 年，烟测时 5 年）
→ outputs/趋势_条形图.png         OLS slope ± 95% Student-t CI
→ outputs/月气候态_热图.png       city × month 长期均温

输入兼容两种 schema：
- 02_分析.py 加 MK+Sen 后写出的 15 列版（含 ols_* / sen_* / mk_* 前缀）
- 旧版 8 列（slope_c_per_year / ci95_low / ci95_high）

跑法：
    python 03_出图.py
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 中文字体兜底（PPT 第 80 页讲：中文不行就用英文标签避坑）
USE_CN_FONT = False
for f in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "PingFang SC"]:
    if any(f.lower() in n.name.lower() for n in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = f
        plt.rcParams["axes.unicode_minus"] = False
        USE_CN_FONT = True
        break

HERE = Path(__file__).parent
PROC = HERE / "data" / "processed"
OUT = HERE / "outputs"
ANNUAL = PROC / "era5_annual.csv"
MONTHLY = PROC / "era5_monthly.csv"
TREND = PROC / "趋势汇总.csv"

CITY_EN = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou",
    "西安": "Xi'an", "武汉": "Wuhan", "哈尔滨": "Harbin", "乌鲁木齐": "Urumqi",
}


def label(cn: str) -> str:
    return cn if USE_CN_FONT else CITY_EN.get(cn, cn)


def main():
    if not ANNUAL.exists():
        print(f"[错误] 找不到 {ANNUAL}。先跑：python 02_分析.py")
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)

    # ============ 图 1：年均气温折线 ============
    annual_by_city: dict = defaultdict(dict)
    with ANNUAL.open("r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if int(r["days"]) >= 300:
                annual_by_city[r["city"]][int(r["year"])] = float(r["temp_c_mean"])

    fig, ax = plt.subplots(figsize=(11, 5))
    for city, ydata in annual_by_city.items():
        years = sorted(ydata.keys())
        vals = [ydata[y] for y in years]
        ax.plot(years, vals, marker="o", linewidth=1.6, label=label(city))
    ax.set_title("Annual mean 2m temperature, China (ERA5 via Open-Meteo)"
                 if not USE_CN_FONT else "中国主要城市年均气温（ERA5 / Open-Meteo）")
    ax.set_xlabel("Year" if not USE_CN_FONT else "年份")
    ax.set_ylabel("Temperature (°C)" if not USE_CN_FONT else "气温 (°C)")
    ax.legend(loc="best", fontsize=9, ncol=2)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    p1 = OUT / "年均气温_折线.png"
    fig.savefig(p1, dpi=120); plt.close(fig)
    print(f"  [OK] {p1.name}")

    # ============ 图 2：趋势条形图（slope ± 95% CI） ============
    if TREND.exists():
        trends: list[dict] = []
        with TREND.open("r", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                # 兼容 02_分析.py 加 MK + Sen 前后两种 schema：
                #   旧（≤ 8 列）：slope_c_per_year / ci95_low / ci95_high
                #   新（15 列）：ols_slope_c_per_year / ols_ci95_low / ols_ci95_high
                #             另含 sen_slope_c_per_year / sen_ci95_* / mk_*
                slope_key = "ols_slope_c_per_year" if "ols_slope_c_per_year" in r else "slope_c_per_year"
                lo_key = "ols_ci95_low" if "ols_ci95_low" in r else "ci95_low"
                hi_key = "ols_ci95_high" if "ols_ci95_high" in r else "ci95_high"
                trends.append({
                    "city": r["city"],
                    "slope": float(r[slope_key]),
                    "lo": float(r[lo_key]),
                    "hi": float(r[hi_key]),
                    "r2": float(r["r2"]),
                })
        trends.sort(key=lambda x: x["slope"])

        labels = [label(t["city"]) for t in trends]
        slopes = [t["slope"] for t in trends]
        errs_low = [t["slope"] - t["lo"] for t in trends]
        errs_high = [t["hi"] - t["slope"] for t in trends]

        colors = ["#D62728" if s > 0 else "#1F77B4" for s in slopes]
        fig, ax = plt.subplots(figsize=(8, 5))
        y_pos = range(len(labels))
        ax.barh(list(y_pos), slopes, color=colors,
                xerr=[errs_low, errs_high], capsize=4)
        ax.axvline(0, color="black", linewidth=0.6)
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(labels)
        ax.set_title("OLS slope of annual temperature (°C / year, error bars = 95% CI)"
                     if not USE_CN_FONT else "年均气温 OLS 趋势（°C / 年，误差棒 = 95% CI）")
        ax.set_xlabel("°C / year")
        plt.tight_layout()
        p2 = OUT / "趋势_条形图.png"
        fig.savefig(p2, dpi=120); plt.close(fig)
        print(f"  [OK] {p2.name}")

    # ============ 图 3：city × month 气候态热图 ============
    monthly_by_city: dict = defaultdict(lambda: defaultdict(list))
    with MONTHLY.open("r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            mon = int(r["month"].split("-")[1])
            monthly_by_city[r["city"]][mon].append(float(r["temp_c_mean"]))

    cities = list(monthly_by_city.keys())
    months_idx = list(range(1, 13))
    matrix = []
    for c in cities:
        row = []
        for m in months_idx:
            vs = monthly_by_city[c].get(m, [])
            row.append(sum(vs) / len(vs) if vs else float("nan"))
        matrix.append(row)

    fig, ax = plt.subplots(figsize=(11, 4))
    im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r")
    ax.set_yticks(range(len(cities)))
    ax.set_yticklabels([label(c) for c in cities])
    ax.set_xticks(range(12))
    ax.set_xticklabels([f"{m}" for m in months_idx])
    ax.set_xlabel("Month" if not USE_CN_FONT else "月份")
    ax.set_title("Monthly climatology (mean 2m temperature, °C)"
                 if not USE_CN_FONT else "月度气候态（平均 2m 气温，°C）")
    fig.colorbar(im, ax=ax, label="°C")
    for i in range(len(cities)):
        for j in range(12):
            v = matrix[i][j]
            if v == v:  # not NaN
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        color="white" if abs(v) > 15 else "black", fontsize=7)
    plt.tight_layout()
    p3 = OUT / "月气候态_热图.png"
    fig.savefig(p3, dpi=120); plt.close(fig)
    print(f"  [OK] {p3.name}")

    print(f"\n[完成] 三张图都在 {OUT}")
    print("下一步：照 04_起草.md 跑多模型流程")


if __name__ == "__main__":
    main()
