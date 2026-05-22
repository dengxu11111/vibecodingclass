# 第 0 章 · 课前准备

> 在第一节课开课前一周完成。装不上的同学课上直接跟读。

## 这一章要做什么

把后面 9 章会用到的所有软件都装好：

- **Node.js**（Codex / Claude Code 的安装基础）
- **Claude Code**（贯穿 03–09 章的主力 Agent）
- **Codex** / Codex Plus（04 章 Agent 工具对比）
- **OpenClaw**（05 章主角）
- **Ollama**（02 章本地大模型）
- **Docker Desktop**（02 章 Open WebUI）
- **Python 3.10+** & 第三方包（贯穿 01、08、capstone）

## 怎么做

1. 跟着 [软件安装步骤.md](./软件安装步骤.md) 一步步装。
2. 装完每一个软件就去对应章节的 `验收清单.md` 跑一下"是否装好"那一条。
3. 装不上的看 [常见问题.md](./常见问题.md)。

## 验收

打开 PowerShell，下面这些命令都能跑出版本号：

```powershell
node --version          # >= v18
python --version        # >= 3.10
docker --version
ollama --version        # 可选
claude --version        # Claude Code
codex --version         # 可选
```

至少 `node` / `python` 必须装好，其他可以课中再补。
