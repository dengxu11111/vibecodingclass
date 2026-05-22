# Capstone · 中国主要城市气温趋势小综述

5 步流水线，把第 08 + 09 章合到一个真任务上：30 年（1995-2024）7 城气温趋势 → 600-1000 字综述。

数据：ERA5，经 Open-Meteo 免费代理（无 key、无 VPN）或 Copernicus CDS 官方 API（投稿用）。

> **为什么是 30 年**：WMO climate normal 的标准参考期。本课程把 30 年定为趋势分析的最低教学口径——5 年样本的 CI 会宽到下不了结论。

## 第一次跑

```powershell
cd capstone-科研数据分析
python 01_下载.py   # 联网 1-2 分钟（无 key），7 城 × 30 年
python 02_分析.py   # OLS + Student-t + MK + Sen → 趋势汇总.csv
python 03_出图.py   # outputs/ 下 3 张 PNG
```

看 `outputs/*.png` 就有东西了。想交一份给导师看的稿子 → 跑 04 / 05：

```powershell
# 04: 在 Claude Code 对话里按 04_起草.md 跑三角色
python 05_核验.py   # 把草稿里每个数字回 grep csv，untraced=0 才定稿
```

**没网 / 工具没装齐**？看 `../example/capstone_5y_cds/`：21 KB CDS CSV，直接读。

## 数据流

```text
01_下载.py / 01_下载_cds.py    → data/raw/*.csv
02_分析.py / 02_分析_cds.py    → data/processed/{era5_annual, 趋势汇总, ...}.csv
03_出图.py                      → outputs/*.png
04_起草.md（三角色对话）         → outputs/{资料员_主题表, 起草员_v1, 草稿_v2, 最终稿}.md
05_核验.py                      → outputs/核验报告.md  (每数字 grep csv)
```

> 同样 4 步流水线可原样套到任何领域：换 01_下载 的数据源（生信 / 经济 / 文献元数据 / 实验日志），后 3 步几乎不用改。见 `../pipeline_template/`。

## 两条数据路径

| 路径 | 入口 | 门槛 | 用途 |
| --- | --- | --- | --- |
| **A. Open-Meteo（主线）** | `01_下载.py` | 无 | 30 年免费代理 ERA5 |
| **B. CDS（真投稿）** | `01_下载_cds.py` | CDS 账号 + `~/.cdsapirc` | 官方 ERA5，可投稿引用 |

详细对比：[`../example/capstone_5y_cds/README.md`](../example/capstone_5y_cds/README.md)。

## CDS 路径快跑

```powershell
pip install -r ..
equirements.txt
# 到 https://cds.climate.copernicus.eu 注册账号，把 key 写到 ~/.cdsapirc
python 01_下载_cds.py        # 默认 7 城 × 2020-2024 月均
python 02_分析_cds.py
```

要真做 30 年趋势：`python 01_下载_cds.py --start-year 1995 --end-year 2024`（CDS 排 5-15 分钟）。

## 数据声明

- 底层：ERA5 (Hersbach et al., 2020)，ECMWF 全球再分析。
- Open-Meteo：免费代理，0.25° 分辨率，`temperature_2m_mean`。
- CDS（投稿用）：`reanalysis-era5-single-levels-monthly-means`，DOI 10.24381/cds.f17050d7。
- 7 城：北京 / 上海 / 广州 / 西安 / 武汉 / 哈尔滨 / 乌鲁木齐，覆盖东亚季风 + 西北干旱 + 高纬寒带。

## 验收

```
[ ] data/raw/era5_all.csv 天数 ≥ 70000（7 城 × 30 年）
[ ] data/processed/趋势汇总.csv 含每城 OLS slope + 95% CI + R² + MK + Sen
[ ] outputs/ 下三张 PNG 能打开
[ ] outputs/最终稿.md 每个数字能 grep 到 csv
[ ] python 05_核验.py 通过（untraced=0）
[ ] 草稿里没有"显著"二字
```

## 串起了哪些章节

- 01：用 token 估算选起草员模型
- 03：Vibe Coding 模式跑通 01-03 脚本
- 06：调用「数据清洗」「出图」Skill
- 07：MCP `verify_number` 防 AI 编数字
- 08：抓 → 清 → 画流水线
- 09：三角色对话生成综述
