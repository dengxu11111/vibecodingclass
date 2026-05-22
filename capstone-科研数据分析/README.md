# Capstone · 中国主要城市气温趋势小综述

> 把第 08 + 09 章串起来的一个完整故事。
> **目标**：用 5 个脚本 + 一份 600–1000 字综述，做出"近 30 年（1995–2024）中国主要城市气温趋势"的小研究。
> **数据**：ERA5 reanalysis，经 Open-Meteo Historical Weather API 免费代理（零 key、零 VPN）。
> **为什么是 30 年**：30 年是 WMO climate normal 的标准参考期；本课程把它定为教学趋势分析的最低口径。5 年样本的 CI 会宽到没法下任何结论。

## 故事

设定：你需要在半天内回答"近 30 年中国主要城市的气温到底变了多少"，并交出一两张图、一段综述。

> 这是一个**示例任务**——选气候是因为数据零门槛拿（无 key、无 VPN、无账号）。**同样的 4 步流水线可以套到任何领域**：把 `01_下载.py` 换成你的数据源（生物数据库 / 经济指标 / 实验日志 / 文献元数据 …），后面 3 步几乎不用改。

正常做法要 1–2 天：装 cdsapi → 申账号 → 拉数据 → 切片 → 趋势检验 → 出图 → 写稿。

Vibe Coding 模式下 30 分钟：

```text
01_下载.py   →   data/raw/era5_<city>.csv  +  era5_all.csv
                       ↓
02_分析.py   →   data/processed/era5_monthly.csv
                  data/processed/era5_annual.csv
                  data/processed/趋势汇总.csv（OLS slope ± 95% Student-t CI）
                       ↓
03_出图.py   →   outputs/年均气温_折线.png
                  outputs/趋势_条形图.png
                  outputs/月气候态_热图.png
                       ↓
04_起草.md   →   outputs/资料员_主题表.md / 起草员_v1.md / 草稿_v2.md / 最终稿.md
                       ↓
05_核验.py   →   outputs/核验报告.md（每个数字必须能在 csv 里找到）
```

## 两条数据路径

| 路径 | 入口脚本 | 数据源 | 门槛 | 适用 |
| --- | --- | --- | --- | --- |
| **A. Open-Meteo（主线，零门槛）** | `01_下载.py` | Open-Meteo Historical Weather API（ERA5 代理） | 无 key、无账号、无 VPN | 课堂主线、学员第一次跑 |
| **B. CDS（真实科研，进阶）** | `01_下载_cds.py` | Copernicus CDS API（官方 ERA5） | CDS 账号 + `~/.cdsapirc` + `pip install cdsapi xarray netCDF4` | 想拿数据投稿 / 做正经研究 |

两条路径用同样的 7 城坐标、同样的 0.25° 网格、同样的 2m 气温变量；区别只在"代理 vs 官方"和"日 vs 月"。详细对比见 [`../example/capstone_5y_cds/README.md`](../example/capstone_5y_cds/README.md)。

## 一键跑（路径 A · Open-Meteo）

```powershell
cd '<repo-root>\capstone-科研数据分析'
python 01_下载.py                    # 默认 7 城 × 1995-2024，30 年，约 1-2 分钟
python 02_分析.py
python 03_出图.py
# 然后在 Claude Code / OpenClaw 里按 04_起草.md 的 prompt 跑多模型流程
python 05_核验.py                    # 把草稿里每个数字回链到 csv，不通过就重写
```

只想验证下载链路通（**不接** 02 / 03 步，5 年样本做不出趋势）：

```powershell
python 01_下载.py --start 2020-01-01 --end 2024-12-31
```

## 一键跑（路径 B · CDS / Copernicus）

```powershell
# 一次性环境（默认 requirements.txt 已含 cdsapi / xarray / netCDF4）
pip install -r ..\requirements.txt

# 一次性凭据：到 https://cds.climate.copernicus.eu 注册账号
# 拿到 key 后写 ~/.cdsapirc（两行 url + key）
# 第一次拉 ERA5 还要去 dataset 页面点 Accept Terms

cd '<repo-root>\capstone-科研数据分析'
python 01_下载_cds.py                # 默认 7 城 × 2020-2024 月均，约 1-2 分钟（含 CDS 排队）
python 02_分析_cds.py                # 出年均 + 概要 CSV
```

CDS 路径的 5 年样本不足以做 OLS 趋势（02_分析.py 安全闸 ≥ 20 年），但**已经能拿来讲清"用真实 ERA5 数据流"这件事**；产物预跑结果在 `../example/capstone_5y_cds/`，**离网也可以直接看**。
要真做趋势：`python 01_下载_cds.py --start-year 1995 --end-year 2024`（CDS 排队会更久，5-15 分钟）。

## 数据来源声明

- **底层数据**：ERA5 reanalysis (Hersbach et al., 2020)，欧洲中期天气预报中心 (ECMWF) 出品的全球大气再分析。
- **取数方式**：通过 Open-Meteo Historical Weather API（<https://open-meteo.com/en/docs/historical-weather-api>）。Open-Meteo 是 ERA5 的免费代理，**坐标分辨率 0.25°**，**变量 `temperature_2m_mean`**（日均 2 米气温）。
- **城市**：北京 / 上海 / 广州 / 西安 / 武汉 / 哈尔滨 / 乌鲁木齐，覆盖东亚季风区 + 西北干旱区 + 高纬寒带。
- **真做投稿**：投学术期刊请用官方 cdsapi 直接拉 Copernicus 原始 NetCDF，记录版本号 + DOI；Open-Meteo 是教学 / 快速调研用的便利层。

## 这一节验证了什么

- 第 01 章：用 token 估算选了**便宜 + 中文好**的 DeepSeek-V3 起草
- 第 02 章：本地 Ollama 可以做对涉密 / 内网数据敏感的稿件润色
- 第 03 章：Vibe Coding 模式跑通"下载 → 分析 → 出图"
- 第 05 章：OpenClaw + DeepSeek 跑全流程
- 第 06 章：调用「数据清洗」「出图」两个 Skill
- 第 08 章：抓 → 清 → 画完整流水线（这次是真实气候数据）
- 第 09 章：资料员 → 起草员 → 审稿员 → 批判员 → 润色员 五角色

## 不要忘记验收

```
[ ] data/raw/era5_all.csv 天数 ≥ 70000（7 城 × 30 年 × ~365 天的下限）
[ ] data/processed/趋势汇总.csv 含每城 slope + 95% Student-t CI + R²
[ ] outputs/ 下三张 PNG 能打开，标注完整
[ ] outputs/草稿_v2.md 或 outputs/最终稿.md 每个数字都能追溯到 csv 行
[ ] python 05_核验.py 通过（核验报告里 untraced = 0）
[ ] 草稿里没有"显著"二字（用"升温/降温/CI 含 0"代替）
[ ] 9 章的验收清单全部勾完
```
