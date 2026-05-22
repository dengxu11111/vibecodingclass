# 第 07 章 · MCP 扩展

> 对应 PPT 第 68–77 页

## 学完这章你能

**给 Agent 装一套"科研工具盒"**——让它**调函数取数**而不是**自己 read_file 边读边猜**。capstone 第 5 步的"数字回链 csv"就是用 MCP 工具做的。

## 5 分钟先跑通这个

```powershell
pip install mcp
npx @modelcontextprotocol/inspector python 07-MCP扩展/最小MCP-server.py
# 浏览器会自动开 http://localhost:5173，左边面板点 load_annual，输入 "北京"
```

看 4 个 tool 真实返回的 JSON 是什么样：[客户端测试_完整示例.md](./客户端测试_完整示例.md)。

## WHAT

- 核心对象：MCP Server / Tool / Resource / Connector
- 真实场景：把跑通的科研动作（OLS 趋势、数字回查 csv）**包装成 Agent 工具**，让 Claude Code / OpenClaw 一句话调到
- 学完能干什么：判断一个能力该做成 prompt、脚本、Skill，还是 MCP 工具

## WHY

Agent 没有稳定工具时，"知道怎么做"和"真的做到了"会混在一起；起草员还可能编数字。MCP 适合**边界清晰、可验证、可授权**的能力——"算趋势"、"回查 csv"。不适合"自由发挥的写作"。

## HOW（4 步）

1. 画工具边界：输入 / 输出 / 权限 / 失败情况
2. 用最小 MCP Server 暴露**只读**工具
3. Agent 调用，记录返回值——尤其用 `verify_number` 去 grep csv
4. 加权限和验收规则，再考虑写入操作

## 本章产出

- [最小MCP-server.py](./最小MCP-server.py)：FastMCP server（stdio），4 个 tool：
  - `load_annual(city)` → 接 `era5_annual.csv`
  - `compute_ols_trend(years, values)` → OLS + Student-t CI
  - `load_trend_summary()` → 读 `趋势汇总.csv`
  - `verify_number(value, ...)` → 数字回 grep csv（防 AI 编数据）
- [mcp配置样例.json](./mcp配置样例.json)：可直接合并的最小配置（合法 MCP，无说明字段）
- [mcp配置说明.md](./mcp配置说明.md)：上面 JSON 每个字段的解释 + 全局 vs 项目内的取舍 + jq 合并命令
- [验收清单.md](./验收清单.md)

## 跑

```powershell
pip install mcp
python 07-MCP扩展/最小MCP-server.py    # stdio 模式，静默等 client（**正常**）

# 单测 4 个 tool（不需要 Claude Code）：
npx @modelcontextprotocol/inspector python 07-MCP扩展/最小MCP-server.py
```

详细 schema + 真实 JSON 调用样例：[客户端测试_完整示例.md](./客户端测试_完整示例.md)。

接到 Claude Code：把 `mcp配置样例.json` 的 `mcpServers.vibecoding-capstone` 合并到 `~/.claude.json`，重启。然后在 capstone 工作流里说：

```
用 vibecoding-capstone 的 load_trend_summary 拿数据，
verify_number 把我稿子里每个数字回 grep csv，列出哪个查不到。
```

这就把第 09 章的"批判员" + capstone 05_核验 升级成 MCP 工具调用——可控可审计。

## MCP 不是唯一答案：CLI plugin 流派

社区另一个声音：**CLI 才是 Agent 的最佳通用接口**。代表项目 [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)（Apache-2.0），把 60+ 款 GUI 软件包成 Click-based CLI 给 Agent 用。

| 维度 | MCP | CLI plugin |
| --- | --- | --- |
| 协议 | stdio/SSE/HTTP + JSON-RPC | bash 调用 + JSON stdout |
| 跨 Agent | 任何支持 MCP 的客户端 | 任何能 bash 的 Agent |
| 状态保持 | server 持有 | CLI / 进程 / 文件级 |
| 写一个新工具 | Python/TS SDK，懂协议 | 写 CLI 即可（Click + JSON） |
| 适合什么 | 长连接 / 有状态 / 事件推送（DB、IDE 嵌入） | 一次性命令、批处理、文件型工作流 |

CLI-Anything 把 MCP 当兜底（[mcp-backend.md](https://github.com/HKUDS/CLI-Anything/blob/main/cli-anything-plugin/guides/mcp-backend.md)）。怎么选：

- 包装 GUI 软件给 Agent 用 → CLI 包装更简单
- 接长连接服务（数据库 / 浏览器自动化 / IDE 状态）→ MCP 对
- 让多家 Agent 都能用 → 两条路都跨 Agent，看数据流向

> 课堂演示：本章先跑通 [最小MCP-server.py](./最小MCP-server.py)（理解协议），课后浏览 CLI-Anything 60+ skill 目录（理解另一种范式）。两套都见过，下次包装新工具就知道怎么选。

## 验收 → 见 [验收清单.md](./验收清单.md)
