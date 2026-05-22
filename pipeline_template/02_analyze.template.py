"""02_analyze.template.py · 跨学科可移植的分析步骤骨架

读 data/raw/<domain>.csv
→ 清洗（去重 / 缺失值处理 / 列名规范化）
→ 聚合（按你领域的分组维度）
→ 计算（你领域的关键统计）
→ 写 data/processed/<domain>_*.csv
→ 打印 Markdown 报告

跑法：
    python 02_<你的领域>.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from math import sqrt
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
PROC = HERE / "data" / "processed"

# ============================================================
# TODO-1：对齐 01 step 的产出名 + 你的字段语义
# ============================================================
DOMAIN_NAME = "domain"          # 跟 01 step 一致
GROUP_KEY = "category"           # 聚合维度（如 city / gene / region / arm）
VALUE_KEY = "value"              # 主测量值
TIME_KEY = "date"                # 时间维度（如果有）
ID_KEY = "id"                    # 主键，去重用


# ============================================================
# TODO-2：你领域的"清洗"是什么
# ============================================================
def clean(rows: list[dict]) -> list[dict]:
    """举几条最朴素的清洗动作；按你领域加。

    capstone 这一步：按 arxiv_id / city 去重 + 关键列缺失就删
    arXiv 示例：列名规范化 + 按 arxiv_id 去重 + 按 published_date 升序
    生信场景：可能需要去除 outlier （3 sigma）+ 去除低 read count 样本
    """
    # 去重（按主键）
    seen = set()
    deduped = []
    for r in rows:
        k = r.get(ID_KEY, "")
        if k and k in seen:
            continue
        seen.add(k)
        deduped.append(r)

    # 关键列缺失就删
    before = len(deduped)
    deduped = [r for r in deduped if r.get(ID_KEY) and r.get(VALUE_KEY) not in (None, "")]
    dropped = before - len(deduped)
    if dropped:
        print(f"  [清洗] 删 {dropped} 行（{ID_KEY} 或 {VALUE_KEY} 缺失）")

    # TODO: 加你领域特有的清洗（异常值、单位换算、字段规范化）

    return deduped


# ============================================================
# TODO-3：你领域的"关键聚合"是什么
# ============================================================
def aggregate(rows: list[dict]) -> dict[str, list[float]]:
    """把 row 列表按 GROUP_KEY 分组，每组得到一串 VALUE_KEY 的数值。

    capstone：按 city 分组得到 30 个年均温
    arXiv：按 category 分组得到论文数
    生信：按 gene 分组得到不同样本的表达量
    """
    groups: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        g = r.get(GROUP_KEY, "?")
        try:
            v = float(r[VALUE_KEY])
        except (ValueError, KeyError, TypeError):
            continue
        groups[g].append(v)
    return dict(groups)


# ============================================================
# TODO-4：你领域的"关键统计"是什么
# ============================================================
def compute_summary(values: list[float]) -> dict:
    """对一组数值算汇总统计。

    capstone 这一步：mean / OLS slope / Mann-Kendall / Sen
    arXiv：count（已经在 aggregate 完成）
    生信：mean / std / t 统计量 / p 值
    """
    n = len(values)
    if n == 0:
        return {"n": 0}

    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    sd = sqrt(var)

    return {
        "n": n,
        "mean": round(mean, 4),
        "sd": round(sd, 4),
        "min": min(values),
        "max": max(values),
        # TODO: 加你领域的统计 —— 趋势 / 检验 / 效应量等
    }


# ============================================================
# 通用部分（一般不需要改）
# ============================================================
def main():
    in_path = RAW / f"{DOMAIN_NAME}.csv"
    if not in_path.exists():
        print(f"[错误] 找不到 {in_path}。先跑 python 01_<你的领域>.py")
        sys.exit(1)

    print(f"→ 读：{in_path}")
    with in_path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        cols = reader.fieldnames or []
    print(f"  原始 {len(rows)} 行 / {len(cols)} 列")

    rows = clean(rows)
    groups = aggregate(rows)

    # 写出聚合结果
    PROC.mkdir(parents=True, exist_ok=True)
    summary_path = PROC / f"{DOMAIN_NAME}_summary.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([GROUP_KEY, "n", "mean", "sd", "min", "max"])
        for g in sorted(groups.keys()):
            s = compute_summary(groups[g])
            w.writerow([g, s["n"], s.get("mean", ""), s.get("sd", ""),
                        s.get("min", ""), s.get("max", "")])

    # 写出清洗后全量数据
    clean_path = PROC / f"{DOMAIN_NAME}_clean.csv"
    if rows:
        with clean_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # Markdown 报告
    print(f"\n## {DOMAIN_NAME} 分析报告\n")
    print(f"清洗后 {len(rows)} 行 / 分组数 {len(groups)}\n")
    print(f"### Top 10 分组（按 n 降序）\n")
    print(f"| {GROUP_KEY} | n | mean | sd | min | max |")
    print(f"| --- | --- | --- | --- | --- | --- |")
    top = sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True)[:10]
    for g, vals in top:
        s = compute_summary(vals)
        print(f"| {g} | {s['n']} | {s.get('mean', ''):.3f} | "
              f"{s.get('sd', ''):.3f} | {s.get('min', '')} | {s.get('max', '')} |")

    print(f"\n[完成] 写入：")
    print(f"  - {clean_path}")
    print(f"  - {summary_path}")
    print(f"下一步：python 03_<你的领域>.py")


if __name__ == "__main__":
    main()
