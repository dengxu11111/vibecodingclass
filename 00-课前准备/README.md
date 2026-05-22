# 第 0 章 · 课前准备

开始学课程之前装完。**全部都装**——每一章都会用到。

## 必装清单

| # | 软件 | 用在哪 |
| --- | --- | --- |
| 1 | **Python 3.10+** + pip | capstone / 01 / 08 |
| 2 | **Node.js LTS** | 装 Claude Code / Codex 的基础 |
| 3 | **Claude Code** | 03 / 04 / 06 / 07 / 09 主力 Agent |
| 4 | **Codex** | 04 章 Agent 对比 |
| 5 | **OpenClaw** + DeepSeek API key | 05 章；Claude Code 不可用时的国内备用 |
| 6 | **Ollama** + `qwen3.5:4b` | 02 章本地大模型 |
| 7 | **Docker Desktop** | 02 章 Open WebUI |
| 8 | **VS Code** | 主编辑器 |

## 步骤

1. 跟 [软件安装步骤.md](./软件安装步骤.md) 一项一项装。
2. 每装完一个跑 `--version` 命令验证。
3. 卡住看 [常见问题.md](./常见问题.md)。

## 验收

```powershell
node --version          # >= v18
python --version        # >= 3.10
claude --version
codex --version
ollama --version
docker --version
```

8 个全部跑得出版本号才算过。装不上的项目**今天**就解决。
