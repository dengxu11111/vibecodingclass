# CLAUDE.md

教学仓库，配 96 页《Vibe Coding》课件 PPT。目标读者：想把 AI Coding 用进日常科研的研究者（方向不限）。

PPT 不进仓库。各章 README 顶部的"PPT 页码"只用于对齐课件。

## 结构

```
00-课前准备/ + 01-模型选型/ ... 09-论文自动化/   九章 + 验收清单
capstone-科研数据分析/                            5 步流水线（ERA5 气温趋势），双数据路径
pipeline_template/                                跨学科 4 步骨架（你套自己方向）
example/capstone_5y_cds/                          CDS 路径预跑产物，离网兜底
.claude/                                          课程出厂配置（5 cmd / 7 skill / 1 agent / settings）
资源/                                            公共 prompt + 链接
```

每章三件套：`README.md`（WHAT / WHY / HOW）+ 教学产物 + `验收清单.md`。三方对齐是契约——改一个要同步另两个。

## 常用命令

PowerShell。仓库路径含非 ASCII 字符的话绝对路径加引号。

```powershell
# 装依赖
pip install -r requirements.txt
# 国内：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# capstone Open-Meteo 路径（无 key，30 年）
cd '<repo-root>\capstone-科研数据分析'
python 01_下载.py     # 7 城 × 30 年，1-2 分钟
python 02_分析.py     # OLS + Student-t CI（< 20 年拒跑）
python 03_出图.py
python 05_核验.py     # 草稿数字回链 CSV

# capstone CDS 路径（需 ~/.cdsapirc，5 年月均）
python 01_下载_cds.py
python 02_分析_cds.py

# 第 4 步多模型起草在 Claude Code / OpenClaw 对话里跑，见 04_起草.md
```

## 不变量

**Capstone 数据流**（不要改回旧 30y 单路径或 Open-Meteo 5 年）：

```
01_下载.py / 01_下载_cds.py  →  data/raw/*.csv
02_分析.py / 02_分析_cds.py  →  data/processed/{era5_annual,趋势汇总,...}.csv
03_出图.py                    →  outputs/*.png
04_起草.md（三角色对话）       →  outputs/{资料员_主题表,起草员_v1,草稿_v2,最终稿}.md
05_核验.py                    →  outputs/核验报告.md  (每数字 grep csv，untraced=0 才定稿)
```

`data/` 和 `outputs/` 全 gitignore，只留 `.gitkeep`。

**Skill 位置**：根 `.claude/skills/` 是 Claude Code 自动发现的激活副本（7 个）。`06-Skill封装/.claude/skills/` 只留课程自写的「数据清洗 / 出图」作为教学讲解；K-Dense 四 Skill 不在 06 章重复。改 Skill 必须保住 frontmatter `name + description`。

**多模型流程**：

- 主线 = 三角色（资料员 → 起草员 → 审稿员合并 critic + polish）→ `capstone/04_起草.md`
- 高阶班 = 五角色 → `09-论文自动化/多模型角色分工.md`

硬约束（两个版本共用）：不许编数据、不许编引用、每个数字回链 CSV。

## 编辑规范

- 面向用户的文本是中文。代码注释中文，变量英文 / 拼音。
- 章节文件名用中文（`下载脚本.py` / `出图.py`），不要英化。
- 改章节产出时同步改：根 README、当章 README、本文件、当章验收清单。
- `print` 不要用 `²` / `✓` / `—`（Windows GBK 控制台炸），用 `R2` / `[OK]` / `--`。Matplotlib 通过字体渲染 OK。
- `03_出图.py` 中文字体兜底链 YaHei → SimHei → Noto Sans CJK → 英文 fallback，**别删**。
- 依赖故意小：`requests / pandas / matplotlib / tiktoken / jupyter / mcp` + 可选 `cdsapi / xarray / netCDF4`。`02_分析.py` 手写 OLS / MK / Sen 以避免 scipy。

## 故意做成这样

- `08-数据工作流` 用 arXiv，`capstone` 用 ERA5——故意两个领域，平缓入门 vs 真科研
- 没有 test / lint / build / pyproject.toml / CI。
- 文档里**统一**写 `<repo-root>`，不要硬编码本机绝对路径。
- `07-MCP扩展/mcp配置样例.json` 里 `_README` / `_说明` 字段不是合法 MCP 字段，是行内教学注释——你拷到自己 `~/.claude.json` 时要去掉。
- 价格表只作教学估算，每个供应商带官网链接，**用前去官网核一遍**。
