"""最小 MCP server——包装 capstone 的科研分析能力。

为什么这么写：
- 学生在 capstone 已经跑过 01_下载.py / 02_分析.py / 05_核验.py
- 把这些能力做成 MCP tool 之后，**在 Claude Code 对话框里一句话就能调**
  比如："读北京的年度气温序列，做 OLS 趋势，把所有数字回 grep csv 确认没编造"
- 同样一份逻辑，CLI 跑 vs MCP 跑，体会两种连接方式的差异（见 README）

依赖：pip install mcp     —— **只依赖标准库 + mcp**，不引 pandas / numpy
工作目录：默认从仓库根算（自动往上找 capstone-科研数据分析/）；可用 VIBECODING_REPO_ROOT 环境变量覆盖

跑法：
    pip install mcp
    python 最小MCP-server.py            # stdio，等 client 连
    # 调试：
    # npx @modelcontextprotocol/inspector python 最小MCP-server.py

接到 Claude Code：把 mcp配置样例.json 合并到 ~/.claude.json，重启 Claude Code 即可。
"""

import csv
import os
from math import sqrt
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("[错误] 没装 mcp。请先：pip install mcp")
    raise SystemExit(1)


# ----- 路径解析：定位 capstone 的 data/processed/ -----

def _repo_root() -> Path:
    """优先用 VIBECODING_REPO_ROOT，否则从本脚本所在目录向上找 capstone-* 目录。"""
    env = os.environ.get("VIBECODING_REPO_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve().parent
    for p in [here, *here.parents]:
        if (p / "capstone-科研数据分析").is_dir():
            return p
    return here.parent  # 退而求其次


REPO = _repo_root()
PROC = REPO / "capstone-科研数据分析" / "data" / "processed"

mcp = FastMCP("vibecoding-capstone-server")


# ===================== Tool 1：取某城市年度气温 =====================

@mcp.tool()
def load_annual(city: str) -> dict:
    """读 era5_annual.csv，返回某城市的逐年均温序列。

    Args:
        city: 城市中文名，如 "北京"、"上海"、"哈尔滨"。

    Returns:
        {"city": ..., "years": [..], "temps_c": [..], "n": N, "source": "..."}
        找不到 csv 或城市时，返回带 error 字段的字典。
    """
    f = PROC / "era5_annual.csv"
    if not f.exists():
        return {"error": f"找不到 {f}。先到 capstone 目录跑 python 02_分析.py。"}
    years: list[int] = []
    temps: list[float] = []
    with f.open("r", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            if r["city"] != city:
                continue
            if int(r["days"]) < 300:  # 覆盖不足的年份剔除
                continue
            years.append(int(r["year"]))
            temps.append(float(r["temp_c_mean"]))
    if not years:
        return {"error": f"era5_annual.csv 里没有城市 {city!r}。已知城市见 trend_summary。"}
    return {
        "city": city,
        "years": years,
        "temps_c": temps,
        "n": len(years),
        "source": str(f.relative_to(REPO)),
    }


# ===================== Tool 2：纯计算的 OLS 趋势 =====================

@mcp.tool()
def compute_ols_trend(years: list[float], values: list[float]) -> dict:
    """对 (年, 值) 做一元线性回归，返回 slope / 95% CI / R² / n。

    与 capstone/02_分析.py 同源——95% CI 用 Student-t（df = n-2）近似。
    纯函数，不读文件，便于跨城市 / 跨变量复用。

    Args:
        years:  年份序列（数值化的）
        values: 同长度的值序列

    Returns:
        {"n", "slope", "intercept", "ci95_low", "ci95_high", "r2", "se_slope"}
    """
    n = len(years)
    if n != len(values) or n < 3:
        return {"error": f"输入长度异常：len(years)={n}, len(values)={len(values)}，且要求 n>=3"}

    mean_x = sum(years) / n
    mean_y = sum(values) / n
    sxx = sum((xi - mean_x) ** 2 for xi in years)
    sxy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(years, values))
    syy = sum((yi - mean_y) ** 2 for yi in values)

    if sxx == 0:
        return {"error": "年份没有方差（sxx=0），无法回归"}

    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    yhat = [intercept + slope * xi for xi in years]
    ss_res = sum((yi - h) ** 2 for yi, h in zip(values, yhat))
    sigma = sqrt(ss_res / (n - 2))
    se_slope = sigma / sqrt(sxx)

    # Student-t 95% 双尾临界值表（df→t），df>30 退化到 1.96
    T = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
        8: 2.306, 9: 2.262, 10: 2.228, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042,
    }
    df = n - 2
    tc = T.get(df) or next((T[k] for k in sorted(T) if df < k), 1.96)
    ci = tc * se_slope
    r2 = 1 - ss_res / syy if syy > 0 else 0.0

    return {
        "n": n,
        "slope": round(slope, 6),
        "intercept": round(intercept, 6),
        "ci95_low": round(slope - ci, 6),
        "ci95_high": round(slope + ci, 6),
        "r2": round(r2, 4),
        "se_slope": round(se_slope, 6),
        "t_crit_95": round(tc, 4),
    }


# ===================== Tool 3：取趋势汇总（多城对比） =====================

@mcp.tool()
def load_trend_summary() -> dict:
    """读 趋势汇总.csv，返回所有城市的 slope / CI / R² 列表。

    Returns:
        {"rows": [{"city", "years", "n", "mean_temp_c", "slope_c_per_year",
                   "ci95_low", "ci95_high", "r2"}, ...], "source": "..."}
    """
    f = PROC / "趋势汇总.csv"
    if not f.exists():
        return {"error": f"找不到 {f}。先到 capstone 目录跑 python 02_分析.py。"}
    rows = []
    with f.open("r", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            row = {"city": r["city"], "years": r["years"], "n": int(r["n"])}
            # 02_分析.py 加 MK + Sen 后有 15 列；旧版本只有 8 列。两套都兼容。
            float_cols = (
                "mean_temp_c",
                "ols_slope_c_per_year", "ols_ci95_low", "ols_ci95_high",
                "slope_c_per_year", "ci95_low", "ci95_high",
                "r2",
                "mk_Z", "mk_p",
                "sen_slope_c_per_year", "sen_ci95_low", "sen_ci95_high",
            )
            for k in float_cols:
                if k in r and r[k] != "":
                    try:
                        row[k] = float(r[k])
                    except ValueError:
                        row[k] = r[k]
            for k in ("mk_S", "mk_trend"):
                if k in r:
                    row[k] = r[k]
            rows.append(row)
    return {"rows": rows, "source": str(f.relative_to(REPO))}


# ===================== Tool 4：数字回查 csv（防 AI 编数据） =====================

@mcp.tool()
def verify_number(
    value: str,
    file: str = "趋势汇总.csv",
    tol: float = 0.001,
    column: str | None = None,
    city: str | None = None,
) -> dict:
    """数值容差匹配：把一个数字在 capstone 的 csv 里**按数值**回查，确认它是真数据。

    与子串匹配（`grep`）不同——这个工具把数字解析成 float，按 ±tol 容差找匹配。
    `tol` 默认 **0.001**——slope 级精度。**只想验整数 / 整百分位**用 `tol=0.5`；
    **想确认整数小数后第 3 位都对**用 `tol=0.0001`。

    **重要警告**：tol 是数值容差，不是子串。所以 `value="0.45"` 与 csv 里 `0.4519`
    的差 = 0.0019，**默认 tol=0.001 下**会判定 found=False；**但若你手贱调到 tol=0.01**，
    它就会假命中——这时记得用 `column=` 钉到具体字段。

    用法场景：起草员稿子里写 "北京升温 +0.0258 °C/年"
        → verify_number("0.0258")                            # 全表搜
        → verify_number("0.0258", column="ols_slope_c_per_year")  # 限定列（推荐）
        → verify_number("0.0258", city="北京")               # 限定城市
        → verify_number("0.0258", city="北京", column="ols_slope_c_per_year")  # 同行同列（最严）

    Args:
        value:   要查的数字字符串（如 "0.0258"、"22.472"、"+0.0382"）。
        file:    在 capstone/data/processed/ 下要搜的 csv，默认 趋势汇总.csv。
        tol:     绝对容差，默认 0.001（slope 精度）。整数列用 0.5，p 值用 0.0001。
        column:  可选——限定只在该列里找（用 csv 的列名）。**slope 验证强烈建议带 column**。
        city:    可选——限定只在该城市的行里找。

    Returns:
        {"found", "match_count", "value_searched", "tol", "hits": [...],
         "file": "...", "available_columns": [...], "available_cities": [...]}
        hits 里每条 = {"city": ..., "column": ..., "csv_value": ..., "diff": ...}
        最多返回 10 条命中。
    """
    f = PROC / file
    if not f.exists():
        return {"error": f"找不到 {f}"}
    try:
        target = float(value.strip().lstrip("+"))
    except ValueError:
        return {"error": f"无法把 {value!r} 解析成 float。要数字，不要字符串。"}

    hits: list[dict] = []
    available_cols: list[str] = []
    available_cities: set[str] = set()

    with f.open("r", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        available_cols = list(reader.fieldnames or [])
        for row in reader:
            row_city = row.get("city") or row.get("year") or row.get("arxiv_id") or "?"
            available_cities.add(row_city)
            if city and city != row_city:
                continue
            for col, cell in row.items():
                if column and col != column:
                    continue
                # 只对能解析成 float 的 cell 做数值比较
                try:
                    cell_val = float(str(cell).strip().lstrip("+"))
                except (ValueError, AttributeError):
                    continue
                diff = abs(cell_val - target)
                if diff <= tol:
                    hits.append({
                        "city": row_city,
                        "column": col,
                        "csv_value": cell_val,
                        "diff": round(diff, 6),
                    })
                    if len(hits) >= 10:
                        break
            if len(hits) >= 10:
                break

    return {
        "found": bool(hits),
        "match_count": len(hits),
        "value_searched": target,
        "tol": tol,
        "filter": {"column": column, "city": city},
        "hits": hits,
        "file": str(f.relative_to(REPO)),
        "available_columns": available_cols,
        "available_cities": sorted(available_cities),
    }


# ===================== 启动 =====================

if __name__ == "__main__":
    # FastMCP 默认走 stdio，Claude Code 这种 MCP 客户端用 stdio 调
    mcp.run()
