# 第 08 章 · 数据工作流

> PPT 78–85

## 跑

教室没网用预跑样例 CSV：

```powershell
python 08-数据工作流/数据清洗.py --in 08-数据工作流/示例输出/arxiv_10条样例.csv
python 08-数据工作流/出图.py
```

有网试真下载：

```powershell
python 08-数据工作流/下载脚本.py --keyword "large language model" --limit 50
```

## 学完能

从公开数据让 Claude Code 辅助搭可复跑的"获取 → 清洗 → 分析 → 出图"流程。

## 怎么做

1. 固定 `data/raw` `data/processed` `outputs` 目录
2. Agent 写最小可复跑脚本
3. 每步留日志
4. 用验收清单核

## 产出

- [下载脚本.py](./下载脚本.py) — arXiv 公开 API
- [数据清洗.py](./数据清洗.py) — 去重 / 列名规范 / 按日期排序 + 报告
- [出图.py](./出图.py) — 按月发文量 + 分类分布
- [示例输出/arxiv_10条样例.csv](./示例输出/arxiv_10条样例.csv) — 10 篇 LLM 经典论文，离网兜底
- [验收清单.md](./验收清单.md)

> 入门示例；完整科研流水线见 [capstone-科研数据分析](../capstone-科研数据分析/)。
