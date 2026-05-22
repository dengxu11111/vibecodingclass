# 第 07 章 · MCP 扩展

> PPT 68–77

## 跑

```powershell
pip install mcp
npx @modelcontextprotocol/inspector python 07-MCP扩展/最小MCP-server.py
# 浏览器开 http://localhost:5173，点 load_annual 输 "北京"
```

4 个 tool 真实 JSON：[客户端测试_完整示例.md](./客户端测试_完整示例.md)。

## 学完能

把跑通的科研动作（OLS 趋势 / 数字回查 csv）包装成 Claude Code 工具，**Agent 调函数取数**而不是**自己读 csv 边读边猜**。

## 怎么做

1. 画工具边界：输入 / 输出 / 权限 / 失败
2. 最小 MCP Server 暴露**只读**工具
3. Agent 调用 + 记返回
4. 加权限和验收规则

## 何时用

边界清晰 / 可验证 / 可授权（算趋势 / 回查 csv）。不适合自由发挥的写作。

## 产出

- [最小MCP-server.py](./最小MCP-server.py) — FastMCP stdio，4 个 tool：
  - `load_annual(city)` — 接 `era5_annual.csv`
  - `compute_ols_trend(years, values)` — OLS + Student-t CI
  - `load_trend_summary()` — 读 `趋势汇总.csv`
  - `verify_number(value, ...)` — 数字回 grep csv（防 AI 编数据）
- [mcp配置样例.json](./mcp配置样例.json) + [说明](./mcp配置说明.md) — 合并到 `~/.claude.json`
- [客户端测试_完整示例.md](./客户端测试_完整示例.md)
- [验收清单.md](./验收清单.md)

## 接到 Claude Code

合并 `mcp配置样例.json` 的 `vibecoding-capstone` 到 `~/.claude.json`，重启。然后：

```
用 vibecoding-capstone 的 load_trend_summary 拿数据，
verify_number 把我稿子里每个数字回 grep csv，列出哪个查不到。
```

把 09 章"批判员" + capstone 05_核验 升级成 MCP 工具调用——可控可审计。

## 另一条路

[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)（Apache-2.0）把 GUI 软件包成 CLI 给 Agent 用。包 GUI 软件 → CLI 更简单；长连接服务 → MCP 对。
