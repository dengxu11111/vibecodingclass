# Vibe Coding 课程仓库

配套 96 页《Vibe Coding》课件 PPT 的实操材料。课件讲 WHAT / WHY，本仓库讲 HOW——打开终端就能跑。

**核心工具 = Claude Code + Codex**。其它都是为这两个服务。

## 课程目录

| 章节 | 主题 | PPT |
| --- | --- | --- |
| [00 课前准备](./00-课前准备/) | 装齐 8 件软件 | —— |
| [01 模型选型](./01-模型选型/) | Token / 上下文 / 价格 / 国产 vs 国外 | 1–16 |
| [02 本地部署](./02-本地部署/) | Ollama / Open WebUI / 私有 AI | 17–28 |
| [03 Vibe Coding](./03-Vibe-Coding/) | 自然语言驱动编程 + 调试记录 | 29–38 |
| [04 Agent 对比](./04-Agent工具对比/) | **Claude Code vs Codex 决策** | 39–45 |
| [05 OpenClaw](./05-OpenClaw-Hermes/) | 国内备用 Agent（DeepSeek API） | 46–56 |
| [06 Skill 封装](./06-Skill封装/) | 把高频动作沉淀给 Claude Code | 57–67 |
| [07 MCP 扩展](./07-MCP扩展/) | 给 Agent 装科研工具盒 | 68–77 |
| [08 数据工作流](./08-数据工作流/) | 从 API 抓数据到出图 | 78–85 |
| [09 论文自动化](./09-论文自动化/) | 多模型协作 + 数字回链核验 | 86–96 |
| [capstone](./capstone-科研数据分析/) | 5 步综合（ERA5 气温趋势） | —— |
| [pipeline_template](./pipeline_template/) | 跨学科 4 步骨架 | —— |
| [资源](./资源/) | prompt + 参考链接 | —— |

> PPT 不随仓库发布。

## 刚 clone 完？三步

```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
code example/capstone_5y_cds/data/raw/era5_cds_monthly.csv
python capstone-科研数据分析/01_下载.py
```

## Slash command

git clone 后 Claude Code 自动认出根 `.claude/`：

| 命令 | 作用 |
| --- | --- |
| `/setup-check` | 验环境，英文报错翻译成中文 |
| `/explain-error` | 粘报错 → 原因 / 下一步 / 可否跳过 |
| `/capstone-run` | 顺序跑 01-03，失败停下 |
| `/capstone-draft` | 三角色对话生成综述 |
| `/capstone-validate` | 跑 05_核验.py，按 untraced 给建议 |

## 没网

```powershell
xcopy /E /I example\capstone_5y_cds\data capstone-科研数据分析\data
python capstone-科研数据分析_分析_cds.py
```

详见 [example/EXAMPLE-README.md](./example/EXAMPLE-README.md)。

## 注意

- 仓库路径含中文 / 空格 / 破折号时绝对路径加引号：`cd '<repo-root>'`
- Python `print` 不要打 `²` / `✓` / `—`（Windows GBK 炸），matplotlib 标签没事

## 反馈

发现 README 不对劲，欢迎改 Markdown 提 PR。
