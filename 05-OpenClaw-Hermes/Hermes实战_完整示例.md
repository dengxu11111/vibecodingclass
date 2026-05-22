# Hermes 实战 · 一次任务的完整 trace

> 第一次跑前看完这个 trace，知道 Agent 工作流长什么样，自己上手就不慌。
> 任务来自 [Hermes任务样例.md](./Hermes任务样例.md) 任务 1：「读 README 写课程导读」。

## 前置

- OpenClaw 接好 DeepSeek-V3
- 工作目录在仓库根 `<repo-root>`

## 你 prompt

```
你是【Hermes 任务执行 Agent】，按 4 步顺序执行：

步骤 1：读取仓库根 README.md
步骤 2：读取 capstone-科研数据分析/README.md
步骤 3：综合两份文件，写一份 300 字「课程导读」，结构：给谁的（30 字）/ 学了能干什么（100 字）/ 怎么上手（170 字）
步骤 4：把导读保存到 outputs/课程导读.md

约束：不允许编造仓库里没有的章节 / 文件；不许写"显著"等无支撑程度词。
```

## Hermes 工作 trace（示意）

> ⚠ 工具名 `read_file / write_file` 是**示意**——真实工具名以你装的 OpenClaw 版本为准。

```
[步骤 1] read_file("README.md")          → 5621 字符
[步骤 2] read_file("capstone-科研数据分析/README.md")  → 4892 字符
[步骤 3] (内部生成草稿，按 3 段结构)
[步骤 4] write_file("outputs/课程导读.md", content=<导读正文>)
         → 写入成功，约 300 字

完成。已生成 outputs/课程导读.md。只引用了两份 README 出现过的章节编号，无编造。
```

## 验证

```powershell
(Get-Content outputs/课程导读.md -Raw).Length  # ≈ 300
# 检查文中引用的章节编号是否真存在
ls 00-课前准备, 01-模型选型, ..., capstone-科研数据分析
```

## 这次教会了什么

1. Agent 的工具调用**显式可见**——出问题直接看哪一步崩
2. 在 prompt 第一段写硬约束（不许编造）真的能管住模型
3. 每一步给具体动作（"步骤 1：读取..."）比 "帮我搞定" 成功率高 5×
4. 保存路径要明确——别让 Agent 自己决定

## 不顺利的几种 case

| 现象 | 原因 | 怎么办 |
| --- | --- | --- |
| 直接给导读不调 `read_file` | DeepSeek 工具调用走神 | prompt 强调"**必须**先 read_file 才能写" |
| 引用了 "第 10 章"（不存在） | hallucination | 加 "输出前自己 grep 仓库目录确认" |
| `write_file` 路径错 | outputs 不存在 / 权限边界 | 先 `mkdir outputs`，或 prompt 要求自动创建 |
| 429 | DeepSeek 限流 | 等几分钟 / 升付费层 |
