# mcp配置样例.json · 字段说明

[mcp配置样例.json](./mcp配置样例.json) 是 **可直接合并**到你 `~/.claude.json` 或 项目根 `.mcp.json` 的最小配置。每个字段的含义在这里讲，**JSON 自身不带说明字段**（合法 MCP 配置不允许 `_README` / `_说明` 这种自定义键，Claude Code 拒绝加载会让 server 跑不起来）。

## 唯一的 server：vibecoding-capstone

```json
"vibecoding-capstone": {
  "command": "python",
  "args": ["./07-MCP扩展/最小MCP-server.py"],
  "env": {
    "VIBECODING_REPO_ROOT": "${workspaceFolder}"
  }
}
```

- **command + args**：用 Python 跑本仓库的 MCP server，**相对路径**（要求 Claude Code 把 cwd 设到仓库根）。如果合并到全局 `~/.claude.json`、Claude Code 起在其它目录，**把 `args` 改成绝对路径**：
  ```json
  "args": ["e:\\claude—code\\vibecodingclass\\07-MCP扩展\\最小MCP-server.py"]
  ```
- **env.VIBECODING_REPO_ROOT**：让 server 知道 capstone csv 在哪。`${workspaceFolder}` 是 Claude Code / VS Code 自动展开的当前工作区路径变量；非 VS Code 客户端不展开时，**写仓库绝对路径**。
- **server 提供 4 个 tool**：`load_annual` / `compute_ols_trend` / `load_trend_summary` / `verify_number`，详见 [客户端测试_完整示例.md](./客户端测试_完整示例.md)。

## 想加更多 server 怎么写

把它们加到 `mcpServers` 这个 dict 里就行。常用的两个：

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "${workspaceFolder}"
  ]
}
```
官方文件系统 server，给定根目录就让 Agent 在里面读写。**注意**：合到全局 ~/.claude.json 时，`${workspaceFolder}` 不会展开，得换成具体绝对路径。

```json
"fetch": {
  "command": "uvx",
  "args": ["mcp-server-fetch"]
}
```
官方网络抓取 server，capstone 第 01 步备用。**前置**：装 `uv`（<https://docs.astral.sh/uv/getting-started/installation/>），不然 `uvx` 命令找不到。

## 项目内 vs 全局：合并到哪？

| 想要 | 文件 | 优点 | 缺点 |
| --- | --- | --- | --- |
| **只在本仓库用** | `<repo-root>/.mcp.json` | 你 clone 后立即可用；不污染个人配置 | 在其它项目里 Claude Code 不知道 vibecoding-capstone |
| **全局任何项目都用** | `~/.claude.json` 的 `mcpServers` | 一处配好处处用 | 必须用绝对路径，跨机器 / clone 后失效 |

**建议**：先用项目内 `.mcp.json` 跑通；想长期用再迁到全局并把路径写死。

## 合并方法

如果你的 `~/.claude.json` 已经有别的 mcpServers，**不要整段覆盖**——把 `vibecoding-capstone` 这一个键合进去就行。jq 一句话搞定：

```powershell
# Windows PowerShell（先装 jq：scoop install jq）
$existing = Get-Content $env:USERPROFILE\.claude.json | jq '.'
$add = Get-Content 07-MCP扩展\mcp配置样例.json | jq '.mcpServers.["vibecoding-capstone"]'
$merged = $existing | jq --argjson new $add '.mcpServers["vibecoding-capstone"] = $new'
$merged | Out-File $env:USERPROFILE\.claude.json -Encoding utf8
```

或者手工：用 VS Code 打开 `~/.claude.json`，找到 `"mcpServers"`，把 `vibecoding-capstone` 这一行键值粘进去，注意 JSON 的逗号。

## 启动验证

```powershell
# 1. server 本身能跑
pip install mcp
python 07-MCP扩展/最小MCP-server.py

# 2. Claude Code 能识别（重启 Claude Code 后）
# 在对话框输入 / 用 inspector：
npx @modelcontextprotocol/inspector python 07-MCP扩展/最小MCP-server.py
```

跑不通就翻 [客户端测试_完整示例.md](./客户端测试_完整示例.md) 的"常见疑问"表。
