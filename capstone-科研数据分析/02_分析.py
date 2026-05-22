"""Capstone · 步骤 2：算月均、年均、OLS 线性趋势 + 95% CI。

读 data/raw/era5_all.csv
→ data/processed/era5_monthly.csv     每城每月均温
→ data/processed/era5_annual.csv      每城每年均温
→ data/processed/趋势汇总.csv          每城 OLS 趋势 (°C/年) + 95% CI + n
→ 打印 Markdown 报告

CI 用 Student-t 临界值（基于 n-2 自由度），不是正态近似。
表格只给「趋势方向」(↑/↓/—)，**不**给「显著」二值判断——n 不大时这是过强结论。

安全闸：年份样本 < 20 直接拒绝跑（避免学生拿 5 年烟测数据继续做 OLS）。
要强行覆盖：`python 02_分析.py --allow-short`（教学讨论小样本时用）。

跑法：
    python 02_分析.py
    python 02_分析.py --allow-short          # 仅用于教学讨论
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date
from math import sqrt
from pathlib import Path

# 趋势分析的教学样本下限（年）。WMO climate normal 是 30 年标准参考期；本仓库以 20 年为脚本保护下限，**不**作为正式结论。
MIN_YEARS_DEFAULT = 20

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw" / "era5_all.csv"
PROC = HERE / "data" / "processed"

# Student-t 双尾 alpha=0.05 临界值表（df → t_{0.025}）。
# 表外采用最接近的较大 df 作为近似；df ≥ 100 退化到正态 1.96。
T_CRIT_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
    16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
    21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
    26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042,
    40: 2.021, 50: 2.009, 60: 2.000, 80: 1.990, 100: 1.984,
}


def t_crit_95(df: int) -> float:
    """返回自由度 df 的 t_{0.025} 临界值。df > 100 退化到正态 1.96。"""
    if df < 1:
        return float("inf")
    if df in T_CRIT_95:
        return T_CRIT_95[df]
    for k in sorted(T_CRIT_95.keys()):
        if df < k:
            return T_CRIT_95[k]
    return 1.96


def mann_kendall(values: list[float]) -> dict:
    """Mann-Kendall 趋势检验（非参数，不要求残差正态）。

    返回 {"S", "Z", "p_two_sided", "trend"}。
    trend ∈ {"↑", "↓", "—"}，按 alpha=0.05 双尾。

    实现仅依赖标准库 math；p 值用正态近似（n>=8 时可用）。
    无打结（ties）调整，对气候年均温这种连续序列足够。
    """
    n = len(values)
    if n < 4:
        return {"S": 0, "Z": 0.0, "p_two_sided": 1.0, "trend": "—"}
    S = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            d = values[j] - values[i]
            if d > 0:
                S += 1
            elif d < 0:
                S -= 1
    var_s = n * (n - 1) * (2 * n + 5) / 18.0
    if S > 0:
        Z = (S - 1) / sqrt(var_s)
    elif S < 0:
        Z = (S + 1) / sqrt(var_s)
    else:
        Z = 0.0
    # 标准正态双尾 p 值近似（Abramowitz & Stegun 26.2.17）
    from math import erf
    p = 2 * (1 - 0.5 * (1 + erf(abs(Z) / sqrt(2))))
    if p < 0.05:
        trend = "↑" if Z > 0 else "↓"
    else:
        trend = "—"
    return {"S": S, "Z": round(Z, 4), "p_two_sided": round(p, 5), "trend": trend}


def sen_slope(years: list[float], values: list[float]) -> dict:
    """Theil-Sen 斜率（非参数）：所有 (i,j) 配对斜率的中位数。

    返回 {"slope", "ci95_low", "ci95_high"}。CI 用 Hollander-Wolfe 的 rank-based 方法。
    """
    n = len(years)
    if n < 4:
        return {"slope": None, "ci95_low": None, "ci95_high": None}
    slopes: list[float] = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            dx = years[j] - years[i]
            if dx != 0:
                slopes.append((values[j] - values[i]) / dx)
    slopes.sort()
    m = len(slopes)
    # 中位数
    if m % 2 == 1:
        med = slopes[m // 2]
    else:
        med = 0.5 * (slopes[m // 2 - 1] + slopes[m // 2])
    # 95% CI rank：c_alpha = 1.96 * sqrt(n(n-1)(2n+5)/18)
    c_alpha = 1.96 * sqrt(n * (n - 1) * (2 * n + 5) / 18.0)
    lo_idx = max(0, int((m - c_alpha) / 2) - 1)
    hi_idx = min(m - 1, int((m + c_alpha) / 2))
    return {"slope": med, "ci95_low": slopes[lo_idx], "ci95_high": slopes[hi_idx]}


def ols_trend(years: list[float], values: list[float]) -> dict:
    """对 (年, 值) 拟合一元线性回归，返回 slope / intercept / 95% CI / R² / n。

    CI 用 Student-t（df = n-2），比正态近似在小样本下更保守。
    """
    n = len(years)
    if n < 3:
        return {"n": n, "slope": None, "ci_low": None, "ci_high": None, "r2": None}

    mean_x = sum(years) / n
    mean_y = sum(values) / n
    sxx = sum((xi - mean_x) ** 2 for xi in years)
    sxy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(years, values))
    syy = sum((yi - mean_y) ** 2 for yi in values)

    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    yhat = [intercept + slope * xi for xi in years]
    ss_res = sum((yi - h) ** 2 for yi, h in zip(values, yhat))
    sigma = sqrt(ss_res / (n - 2)) if n > 2 else 0.0
    se_slope = sigma / sqrt(sxx) if sxx > 0 else 0.0
    # 用 Student-t（df = n-2）做 95% CI
    tc = t_crit_95(n - 2)
    ci = tc * se_slope
    r2 = 1 - ss_res / syy if syy > 0 else 0.0
    return {
        "n": n,
        "slope": slope,
        "ci_low": slope - ci,
        "ci_high": slope + ci,
        "r2": r2,
        "se_slope": se_slope,
        "t_crit": tc,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-short", action="store_true",
                    help="允许 < 20 年的小样本跑 OLS（仅用于教学演示，不要拿结论投稿）")
    ap.add_argument("--min-years", type=int, default=MIN_YEARS_DEFAULT,
                    help=f"年份样本最低要求，默认 {MIN_YEARS_DEFAULT} 年")
    args = ap.parse_args()

    if not RAW.exists():
        print(f"[错误] 找不到 {RAW}。先跑：python 01_下载.py")
        sys.exit(1)

    PROC.mkdir(parents=True, exist_ok=True)
    print(f"→ 读：{RAW}")

    with RAW.open("r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"  共 {len(rows)} 条")

    # 安全闸：先看年份覆盖
    unique_years = set()
    for r in rows:
        try:
            unique_years.add(date.fromisoformat(r["date"]).year)
        except (KeyError, ValueError):
            continue
    n_years = len(unique_years)
    print(f"  覆盖年份：{n_years} 年 ({min(unique_years) if unique_years else '?'}-{max(unique_years) if unique_years else '?'})")
    if n_years < args.min_years and not args.allow_short:
        print(f"\n[安全闸] 年份样本只有 {n_years}，少于 {args.min_years} 年下限。")
        print("  原因：年度 OLS 趋势分析需要至少 20 年（WMO Climate Normal 是 30 年）；")
        print("  小样本下 CI 会宽到没法下任何结论，把结论写进综述会被导师 / 审稿打回。")
        print("")
        print("  解决：重跑下载，用默认 30 年窗口")
        print("    python 01_下载.py                   # 默认 1995-2024")
        print("")
        print("  如果你**就是**想拿小样本做教学演示（讨论 CI 怎么变宽）：")
        print(f"    python 02_分析.py --allow-short")
        sys.exit(2)

    # 聚合：city → month_key → (sum, count)
    monthly: dict = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    annual: dict = defaultdict(lambda: defaultdict(lambda: [0.0, 0]))
    cities_order: list[str] = []

    for r in rows:
        city = r["city"]
        if city not in cities_order:
            cities_order.append(city)
        t = r.get("temp_c", "")
        if not t:
            continue
        try:
            t = float(t)
        except ValueError:
            continue
        d = date.fromisoformat(r["date"])
        mkey = f"{d.year}-{d.month:02d}"
        akey = d.year
        monthly[city][mkey][0] += t; monthly[city][mkey][1] += 1
        annual[city][akey][0] += t; annual[city][akey][1] += 1

    # 写月度
    m_path = PROC / "era5_monthly.csv"
    with m_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "month", "temp_c_mean", "days"])
        for city in cities_order:
            for mkey in sorted(monthly[city].keys()):
                s, n = monthly[city][mkey]
                w.writerow([city, mkey, f"{s / n:.3f}", n])

    # 写年度
    a_path = PROC / "era5_annual.csv"
    with a_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "year", "temp_c_mean", "days"])
        for city in cities_order:
            for y in sorted(annual[city].keys()):
                s, n = annual[city][y]
                w.writerow([city, y, f"{s / n:.3f}", n])

    # 趋势：每城对年度均温做 OLS + Mann-Kendall + Sen 斜率
    # （剔除当年覆盖不足的年份，要求 ≥ 300 天）
    t_path = PROC / "趋势汇总.csv"
    trends: list[dict] = []
    for city in cities_order:
        years_data = sorted(annual[city].items())
        years_used = [(y, s / n) for y, (s, n) in years_data if n >= 300]
        if len(years_used) < 3:
            continue
        ys = [float(y) for y, _ in years_used]
        ts = [t for _, t in years_used]
        r = ols_trend(ys, ts)
        # 加 Mann-Kendall（非参趋势检验）
        mk = mann_kendall(ts)
        # 加 Sen 斜率（非参斜率估计 + rank-based 95% CI）
        sen = sen_slope(ys, ts)
        r.update({
            "mk_S": mk["S"],
            "mk_Z": mk["Z"],
            "mk_p": mk["p_two_sided"],
            "mk_trend": mk["trend"],
            "sen_slope": sen["slope"],
            "sen_ci95_low": sen["ci95_low"],
            "sen_ci95_high": sen["ci95_high"],
        })
        r["city"] = city
        r["mean_temp"] = sum(ts) / len(ts)
        r["years"] = f"{int(min(ys))}-{int(max(ys))}"
        trends.append(r)

    with t_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "city", "years", "n", "mean_temp_c",
            "ols_slope_c_per_year", "ols_ci95_low", "ols_ci95_high", "r2",
            "mk_S", "mk_Z", "mk_p", "mk_trend",
            "sen_slope_c_per_year", "sen_ci95_low", "sen_ci95_high",
        ])
        for r in trends:
            w.writerow([
                r["city"], r["years"], r["n"], f"{r['mean_temp']:.3f}",
                f"{r['slope']:.4f}", f"{r['ci_low']:.4f}", f"{r['ci_high']:.4f}",
                f"{r['r2']:.3f}",
                r["mk_S"], f"{r['mk_Z']:.3f}", f"{r['mk_p']:.4f}", r["mk_trend"],
                f"{r['sen_slope']:.4f}" if r["sen_slope"] is not None else "",
                f"{r['sen_ci95_low']:.4f}" if r["sen_ci95_low"] is not None else "",
                f"{r['sen_ci95_high']:.4f}" if r["sen_ci95_high"] is not None else "",
            ])

    # Markdown 报告
    print("\n## 分析报告（ERA5 / Open-Meteo, 中国城市气温）\n")
    print(f"原始天数：{len(rows)}；输出月份记录：{sum(len(v) for v in monthly.values())}\n")
    years_all = sorted({y for c in cities_order for y, (s, n) in annual[c].items() if n >= 300})
    # 年份多于 12 列时，只展示首年 / 末年 / 均值；完整逐年表请直接看 era5_annual.csv。
    show_yearly = len(years_all) <= 12
    if show_yearly:
        print("### 各城市年均气温（°C）\n")
        header = "| 城市 | " + " | ".join(str(y) for y in years_all) + f" | {len(years_all)} 年均值 |"
        sep = "| --- |" + " --- |" * (len(years_all) + 1)
        print(header); print(sep)
        for city in cities_order:
            row = [city]
            ts: list[float] = []
            for y in years_all:
                ent = annual[city].get(y)
                if ent and ent[1] >= 300:
                    v = ent[0] / ent[1]; ts.append(v); row.append(f"{v:.2f}")
                else:
                    row.append("—")
            row.append(f"{sum(ts) / len(ts):.2f}" if ts else "—")
            print("| " + " | ".join(row) + " |")
    else:
        print(f"### 各城市年均气温摘要（共 {len(years_all)} 年；完整逐年见 era5_annual.csv）\n")
        y_first, y_last = years_all[0], years_all[-1]
        print(f"| 城市 | {y_first} | {y_last} | {len(years_all)} 年均值 |")
        print("| --- | --- | --- | --- |")
        years_set = set(years_all)
        for city in cities_order:
            ent_first = annual[city].get(y_first)
            ent_last = annual[city].get(y_last)
            v_first = (ent_first[0] / ent_first[1]) if ent_first and ent_first[1] >= 300 else None
            v_last = (ent_last[0] / ent_last[1]) if ent_last and ent_last[1] >= 300 else None
            ts = [s / n for y, (s, n) in annual[city].items() if y in years_set and n >= 300]
            cell_first = f"{v_first:.2f}" if v_first is not None else "—"
            cell_last = f"{v_last:.2f}" if v_last is not None else "—"
            cell_mean = f"{sum(ts) / len(ts):.2f}" if ts else "—"
            print(f"| {city} | {cell_first} | {cell_last} | {cell_mean} |")

    print("\n### OLS vs Mann-Kendall + Sen（同一数据，两套方法对比）\n")
    print("| 城市 | n | OLS slope | OLS 95% CI | R2 | Sen slope | Sen 95% CI | MK Z | MK p | MK 方向 |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in trends:
        sen_s = r.get("sen_slope")
        sen_lo = r.get("sen_ci95_low")
        sen_hi = r.get("sen_ci95_high")
        sen_s_str = f"{sen_s:+.4f}" if sen_s is not None else "—"
        sen_ci_str = (f"[{sen_lo:+.4f}, {sen_hi:+.4f}]"
                      if sen_lo is not None and sen_hi is not None else "—")
        print(
            f"| {r['city']} | {r['n']} | {r['slope']:+.4f} | "
            f"[{r['ci_low']:+.4f}, {r['ci_high']:+.4f}] | "
            f"{r['r2']:.2f} | {sen_s_str} | {sen_ci_str} | "
            f"{r['mk_Z']:+.2f} | {r['mk_p']:.3f} | {r['mk_trend']} |"
        )

    # 一致性扫描：OLS 与 MK 结论不一致的城市
    inconsistent = []
    for r in trends:
        ols_dir = "↑" if r["ci_low"] > 0 else ("↓" if r["ci_high"] < 0 else "—")
        if ols_dir != r["mk_trend"]:
            inconsistent.append((r["city"], ols_dir, r["mk_trend"], r["mk_p"]))
    if inconsistent:
        print("\n[一致性扫描] OLS 与 Mann-Kendall 结论**不一致**的城市：")
        for c, od, md, p in inconsistent:
            print(f"  - {c}: OLS={od}  MK={md} (p={p:.3f})")
        print("  → 写稿时应以 MK 为准（非参检验对自相关 / 异常值更稳健）")
    else:
        print("\n[一致性扫描] OLS 与 Mann-Kendall 结论方向一致。")

    print(f"\n[完成] 写入：")
    print(f"  - {m_path}")
    print(f"  - {a_path}")
    print(f"  - {t_path}  （新加 mk_S / mk_Z / mk_p / mk_trend / sen_slope / sen_ci95_low / sen_ci95_high 共 7 列）")
    print("\n方法学说明（写综述时请保留这些 caveat）：")
    print("  - **OLS 列是教学最简版**：假设残差独立同分布，对自相关 / 异常值敏感")
    print("    综述里只说「升温 / 降温 / CI 含 0」，**不要**写「显著」")
    print("  - **MK + Sen 是气候学常规做法**：非参，不要求残差正态，对异常值稳健")
    print("    真做趋势归因，以 MK + Sen 结论为准")
    print("  - 当 OLS 与 MK 结论不一致时（见上方「一致性扫描」），以 MK 为准")
    print("  - 7 城样本不代表全国，更不代表全球；Hurst / 自相关进一步校正可上 pymannkendall.hamed_rao_modification_test")
    print("下一步：python 03_出图.py")


if __name__ == "__main__":
    main()
