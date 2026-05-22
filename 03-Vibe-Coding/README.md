# 第 03 章 · Vibe Coding

> PPT 29–38

## 跑

打开 **Claude Code**，贴这句话，把生成脚本另存为 `demo.py` 跑：

```
写一个 Python 脚本，用 urllib 抓 arXiv 最新 50 篇 'large language model' 论文，
按月份统计发表数，画 PNG 到本目录。只用标准库，不要 requests。
```

跑通后看 [调试记录_完整示例.md](./调试记录_完整示例.md)：capstone 第 1 步 v1→v4 真实 prompt 迭代。

## 学完能

一节课内用 Vibe Coding 模式跑完"数据 → 调试 → 出图 → 沉淀 Skill"小流程。

## 怎么做

1. 一句话写清数据 / 目标 / 输出 / 限制
2. Agent 给最小可跑草稿，跑通比好看重要
3. 每步留证据（输入 / 中间结果 / diff）
4. 高频动作封 Skill（[第 06 章](../06-Skill封装/)）

## 底线

不是"AI 全自动"。AI 负责草稿，人负责验收和记录。

## 产出

- [demo.ipynb](./demo.ipynb) — 真实可跑 Notebook（公开 arXiv 数据）
- [调试记录模板.md](./调试记录模板.md) + [完整示例](./调试记录_完整示例.md)
- [验收清单.md](./验收清单.md)

## 跑 Notebook

```powershell
cd 03-Vibe-Coding
pip install jupyter requests pandas matplotlib
jupyter notebook demo.ipynb
```
