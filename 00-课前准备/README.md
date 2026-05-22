# 第 0 章 · 课前准备

> 在第一节课开课前一周完成。装不上的同学课上直接跟读。

## 最少装啥（最快上手）

**只想跑 capstone + 第 01 / 08 章**（最便宜的路径）：

| 装什么 | 用在哪 | 装不上能跳过吗 |
| --- | --- | --- |
| **Python 3.10+** + pip | capstone 全部脚本、token 估算、数据下载 / 清洗 / 出图 | ❌ 必装 |
| **DeepSeek API key**（免费额度） | 04 / 05 / 09 章里的"找 Agent 对话"步骤 | ✓ 没有也能读 Markdown 学 |
| **OpenClaw** | 05 章主角 / 用 DeepSeek API 的客户端 | ✓ 没装的话课程里 Agent 对话先看示例就行 |
| Ollama | 02 章本地大模型 | ✓ 整章可跳，capstone 不依赖 |
| Docker | 02 章 Open WebUI / 知识库 | ✓ 整段教学演示，capstone 不依赖 |
| Claude Code / Codex | 03 / 04 / 06 / 07 章 Agent 实操 | ✓ 装不上可以用 OpenClaw 平替 |

**最低需求**：装 Python 3.10+ 就够看 + 跑 70% 内容。其它工具按章节展开再装。

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
