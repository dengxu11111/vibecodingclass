"""03_plot.template.py · 跨学科可移植的可视化骨架

读 data/processed/<domain>_summary.csv → 出 outputs/<domain>_*.png

最少出 2 张图：
- 主图（趋势 / 排序 / 分布——按你领域定）
- 概览图（多维度的总览）

跑法：
    python 03_<你的领域>.py
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")              # 没有 GUI 也能跑
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
PROC = HERE / "data" / "processed"
OUT = HERE / "outputs"

# ============================================================
# 中文字体兜底（PPT 第 80 页：中文不行就英文）
# ============================================================
USE_CN_FONT = False
for f in ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "PingFang SC"]:
    if any(f.lower() in n.name.lower()
           for n in matplotlib.font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = f
        plt.rcParams["axes.unicode_minus"] = False
        USE_CN_FONT = True
        break


# ============================================================
# TODO-1：跟 02 step 对齐
# ============================================================
DOMAIN_NAME = "domain"
GROUP_KEY = "category"     # 02 里聚合的维度（跟 02 的 summary csv 第一列对齐）

# 如果你领域的分组名是中文且字体兜不住，给一份英文映射
LABEL_EN: dict[str, str] = {
    # "北京": "Beijing",
    # "上海": "Shanghai",
    # TODO: 填你领域里需要英文化的分组名
}


def label(cn: str) -> str:
    """根据字体是否支持中文，返回中文或英文标签。"""
    if USE_CN_FONT:
        return cn
    return LABEL_EN.get(cn, cn)


# ============================================================
# TODO-2：你领域的"主图"是什么
# ============================================================
def plot_main(summary_rows: list[dict]) -> None:
    """主图——根据你领域定。

    capstone：按 OLS slope 排序的趋势条形图（误差棒 = 95% CI）
    arXiv：按月发文量柱状图
    生信：火山图
    临床：KM 生存曲线
    经济：时间序列折线
    """
    # 默认：mean 排序条形图
    rows = sorted(summary_rows, key=lambda r: float(r["mean"]), reverse=True)
    labels = [label(r[GROUP_KEY]) for r in rows]
    means = [float(r["mean"]) for r in rows]

    fig, ax = plt.subplots(figsize=(9, max(4, len(rows) * 0.4)))
    ax.barh(labels[::-1], means[::-1])
    ax.set_xlabel("mean" if not USE_CN_FONT else "均值")
    title = f"{DOMAIN_NAME}: mean by {GROUP_KEY}"
    ax.set_title(title)
    plt.tight_layout()
    p = OUT / f"{DOMAIN_NAME}_main.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    print(f"  [OK] {p.name}")


# ============================================================
# TODO-3：你领域的"概览图"是什么
# ============================================================
def plot_overview(summary_rows: list[dict]) -> None:
    """概览图——给读者一个 5 秒能看明白的总览。

    capstone：城市 × 月份的气候态热图
    arXiv：分类 Top-N
    生信：PCA 前两个主成分散点 / 样本聚类树
    临床：基线特征对比表
    """
    # 默认：每组样本量 n 的条形图
    rows = sorted(summary_rows, key=lambda r: int(r["n"]), reverse=True)[:10]
    labels = [label(r[GROUP_KEY]) for r in rows]
    counts = [int(r["n"]) for r in rows]

    fig, ax = plt.subplots(figsize=(9, max(3, len(rows) * 0.4)))
    ax.barh(labels[::-1], counts[::-1])
    ax.set_xlabel("n" if not USE_CN_FONT else "样本量")
    ax.set_title(f"{DOMAIN_NAME}: sample size by {GROUP_KEY}")
    plt.tight_layout()
    p = OUT / f"{DOMAIN_NAME}_overview.png"
    fig.savefig(p, dpi=120)
    plt.close(fig)
    print(f"  [OK] {p.name}")


# ============================================================
# 通用部分（一般不需要改）
# ============================================================
def main():
    in_path = PROC / f"{DOMAIN_NAME}_summary.csv"
    if not in_path.exists():
        print(f"[错误] 找不到 {in_path}。先跑 python 02_<你的领域>.py")
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)

    with in_path.open("r", encoding="utf-8-sig") as f:
        summary_rows = list(csv.DictReader(f))
    if not summary_rows:
        print(f"[错误] {in_path} 是空的。")
        sys.exit(1)
    print(f"→ 读 {len(summary_rows)} 行 from {in_path.name}")

    plot_main(summary_rows)
    plot_overview(summary_rows)

    print(f"\n[完成] 出图都在 {OUT}/")
    print(f"下一步：照 04_draft.template.md 跑多模型起草流程")


if __name__ == "__main__":
    main()
