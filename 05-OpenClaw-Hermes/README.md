# 第 05 章 · OpenClaw / Hermes Agent

> 对应 PPT 第 46–56 页

## WHAT —— 学什么

- **核心对象**：OpenClaw（国产 Claude Code 兼容客户端）、Hermes（开源 Agent 框架）、API Key、Workflow、Tool Use
- **真实场景**：你需要一个**国内能稳定用 + 中文友好 + 能连本地项目**的 Agent 工作台
- **学习结果**：在 OpenClaw 里配好模型 / Key / 项目路径，跑通一次"自然语言 → Agent 操作本地文件 → 输出结果"

## WHY —— 为什么学

- **痛点**：直连 Claude Code 要 VPN + Anthropic 账号；OpenClaw 直接接 DeepSeek / OpenRouter，国内零门槛
- **边界**：本章不是 OpenClaw 完整说明书；只解决从零到跑通第一个任务

## HOW —— 怎么做（4 步）

1. 配模型接口和 API Key（DeepSeek 或 OpenRouter）—— 见 [API-Key配置.md](./API-Key配置.md)
2. 连接本地项目路径（让 Agent 能读写你的代码 / 数据目录）
3. 跑一个文件级小任务——见 [Hermes任务样例.md](./Hermes任务样例.md)
4. 给 Agent 一个明确的权限边界——见 [权限边界清单.md](./权限边界清单.md)

## 本章产出

- [API-Key配置.md](./API-Key配置.md)：三家模型 Key 的申请与填法
- [Hermes任务样例.md](./Hermes任务样例.md)：3 个真实任务示例
- [权限边界清单.md](./权限边界清单.md)
- [验收清单.md](./验收清单.md)

## OpenClaw + Agent 跑起来什么样

[Hermes任务样例.md](./Hermes任务样例.md) 给的是空 prompt 模板。
看 [Hermes实战_完整示例.md](./Hermes实战_完整示例.md) —— 任务 1 「读 README 写课程导读」**完整对话回放**：
学员发的 prompt、Hermes 调用 `read_file` / `write_file` 的过程、生成的 `outputs/课程导读.md` 真实内容、4 类常见翻车。
学员第一次跑前看一遍这个回放，心里就有数了。

## 验收 → 见 [验收清单.md](./验收清单.md)
