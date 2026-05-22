# 第 03 章 · Vibe Coding

> 对应 PPT 第 29–38 页

## WHAT —— 学什么

- **核心对象**：Vibe Coding（自然语言驱动编程）、Debug、Notebook、Script、Skill
- **真实场景**：你不再"写代码"，而是"和 AI 一起 vibe 一段代码"——开 Notebook，描述你想要什么，AI 给草稿，你跑、你改、你记
- **学习结果**：能在一节课内用 Vibe Coding 模式跑一个完整的"数据 → 调试 → 出图 → Skill"小流程

## WHY —— 为什么学

- **痛点**：科研代码最怕"跑了一遍出了结果就丢了"——下次想复现要重写
- **边界**：Vibe Coding 不是"让 AI 全自动"，而是"AI 负责草稿、人负责验收和记录"

## HOW —— 怎么做（4 步）

1. **一句话说明数据、目标、输出、限制**——给 AI 写最简明的 prompt
2. **让 Agent 先写最小可运行版本**——能跑通比好看更重要
3. **每一步都留证据**：保留输入、保留中间结果、保留代码 diff
4. **高频代码动作封装 Skill**——见 [第 06 章](../06-Skill封装/)

## 本章产出

- [demo.ipynb](./demo.ipynb)：一个真实可跑的 Vibe Coding Notebook（基于公开 arXiv 数据）
- [调试记录模板.md](./调试记录模板.md)
- [验收清单.md](./验收清单.md)

## 怎么用

```powershell
cd 03-Vibe-Coding
pip install jupyter requests pandas matplotlib
jupyter notebook demo.ipynb
```

Notebook 里每一步都有 Markdown 解说 + 可跑代码 + 可改 prompt 的位置。

## 第一次写完调试记录长什么样

新人填 [调试记录模板.md](./调试记录模板.md) 经常不知道从哪起笔。
看 [调试记录_完整示例.md](./调试记录_完整示例.md) —— 一份"capstone 第 1 步从崩到稳"的完整 4 轮 prompt 迭代记录，
含 v1 → v4 的真错 / 真改 / 真沉淀，照着写自己第一份记录就有谱了。

## 验收 → 见 [验收清单.md](./验收清单.md)
