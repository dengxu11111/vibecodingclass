# Vibe Coding 课程配套仓库

> 配套 96 页《Vibe Coding 课件 PPT》。课件讲 WHAT / WHY，本仓库给"打开终端就能跑"的 HOW。

## 谁该看这个仓库

- 想把 Claude Code / Codex / OpenClaw / Ollama / MCP / Skill 用进日常科研的人（本科 → 博后 → 工程师 / 独立研究者，方向不限）
- 已经看过课件 PPT、需要照着敲的实操清单

> capstone 用气候数据做演示，**4 步流水线（下载 → 分析 → 出图 → 多模型撰稿）可原样套到任何领域**——换数据源即可。`pipeline_template/` 就是为这件事准备的。

## 课程目录

| 章节 | 主题 | PPT 页 | 关键词 |
| --- | --- | --- | --- |
| [00](./00-课前准备/) | 课前准备 | —— | Node.js / Docker / Ollama / Claude Code |
| [01](./01-模型选型/) | 模型选型 | 1–16 | Token / Context / API / 国产模型 |
| [02](./02-本地部署/) | 大模型本地部署 | 17–28 | Ollama / Open WebUI / Docker |
| [03](./03-Vibe-Coding/) | Vibe Coding | 29–38 | Notebook / Script / Skill / Debug |
| [04](./04-Agent工具对比/) | Agent 工具对比 | 39–45 | VS Code / Codex / Claude Code |
| [05](./05-OpenClaw-Hermes/) | OpenClaw / Hermes | 46–56 | API Key / Workflow / Tool Use |
| [06](./06-Skill封装/) | Skill 封装 | 57–67 | SKILL.md / Prompt / Validation |
| [07](./07-MCP扩展/) | MCP 扩展 | 68–77 | Server / Tool / Resource |
| [08](./08-数据工作流/) | 数据工作流 | 78–85 | Cloud / Dataset / API / Chart |
| [09](./09-论文自动化/) | 论文自动化 | 86–96 | Multi-model / Reviewer / Evidence Chain |
| [capstone](./capstone-科研数据分析/) | 综合实操 | —— | 5 步流水线 / OLS+MK+Sen / 数字核验 |
| [pipeline_template](./pipeline_template/) | 跨学科骨架 | —— | 4 步空模板，套你自己方向 |
| [资源](./资源/) | 公共资源 | —— | prompt / 参考链接 |

> PPT 不随仓库发布，页码仅用于课堂对齐；公开读者按各章 README 独立学习即可。

## 快速开始

```powershell
# 1. 装依赖
pip install -r requirements.txt
# 国内：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 2. 跑 capstone（无 key，30 年 ERA5）
cd capstone-科研数据分析
python 01_下载.py
python 02_分析.py
python 03_出图.py
# 04 在 Claude Code / OpenClaw 对话里跑，见 04_起草.md（三角色）
python 05_核验.py
```

## 课程专用 slash command

git clone 之后 Claude Code 自动认出根 `.claude/`：

| 命令 | 作用 |
| --- | --- |
| `/setup-check` | 检查 Node / Python / Ollama / Claude / Codex；英文报错翻译成中文 |
| `/explain-error` | 粘报错 → 原因 / 下一步 / 是否可跳过 |
| `/capstone-run` | 顺序跑 01_下载 → 02_分析 → 03_出图，失败停下 |
| `/capstone-draft` | 三角色对话生成综述 |
| `/capstone-validate` | 跑 05_核验.py，按 untraced 报告给修改建议 |

## 没网怎么办

```powershell
# 把 example 的 CDS 数据拷到 capstone 工作目录
xcopy /E /I example\capstone_5y_cds\data capstone-科研数据分析\data
python capstone-科研数据分析_分析_cds.py
```

完整离网方案见 [example/EXAMPLE-README.md](./example/EXAMPLE-README.md)。

## 路径 / 编码提示

- 本地仓库路径含中文 / 空格 / 破折号时绝对路径加引号：`cd '<repo-root>'`
- Python `print` 不要打 `²` / `✓` / `—`（Windows GBK 控制台炸），matplotlib 标签没事

## 反馈

讲到哪一章发现 README 不对劲，欢迎改 Markdown 提 PR。
