# `example/capstone_5y_cds/` —— CDS / Copernicus 路径参考产物

这一份是 **capstone 的"真实科研版"**：直接走 Copernicus Climate Data Store (CDS) 拉 ERA5 monthly means，没有经过 Open-Meteo 代理。

跟 `Open-Meteo 路径` 的区别：

| 维度 | `01_下载.py` (Open-Meteo) | `capstone_5y_cds/` (本目录, CDS) |
| --- | --- | --- |
| **数据源** | Open-Meteo Historical Weather API（ERA5 代理） | Copernicus CDS API（官方 ERA5） |
| **门槛** | 零 key、零 VPN、零账号 | 需要 [CDS 账号](https://cds.climate.copernicus.eu) + `~/.cdsapirc` |
| **时间粒度** | 日均 → 聚合月 / 年 | 月均（直接拉 `monthly_averaged_reanalysis`） |
| **时间跨度** | 30 年（1995-2024） | 5 年（2020-2024，作教学示例） |
| **可投稿** | 一般不行（要写明 Open-Meteo 代理） | 可以（数据集名 + DOI 都能给） |
| **课程定位** | 主线：零门槛入门 | 进阶：真实工作流 |

## 文件清单

```
capstone_5y_cds/
├── README.md                              ← 这个文件
└── data/
    ├── raw/
    │   └── era5_cds_monthly.csv           7 城 × 60 月 × 月均 2m 气温（21 KB，420 行）
    └── processed/
        ├── era5_cds_annual.csv            7 城 × 5 年 × 年均（873 字节）
        └── era5_cds_summary.csv           7 城 × （5 年均 / 最冷年 / 最暖年 / 年差）
```

## raw CSV 字段

| 字段 | 含义 |
| --- | --- |
| `city` | 城市名 |
| `year` | 年（2020-2024） |
| `month` | 月（1-12） |
| `lat_city` / `lon_city` | 城市的真实经纬度（用来查最近邻像元的输入） |
| `lat_pixel` / `lon_pixel` | ERA5 0.25° 网格上的最近邻像元中心，**实际取数位置** |
| `temp_c` | 该像元该月平均 2m 气温（°C，已从开尔文转） |

## 复现这份数据

```powershell
# 1. 一次性环境
pip install cdsapi xarray netCDF4

# 2. 注册 CDS 账号 → 把 key 写到 ~/.cdsapirc
#    格式：
#      url: https://cds.climate.copernicus.eu/api
#      key: <你的 UID>:<API key>
#    第一次拉 ERA5 还要去 dataset 页面接受 Terms of Use

# 3. 跑下载（约 1-2 分钟，看 CDS 队列）
python capstone-科研数据分析/01_下载_cds.py

# 4. 跑年均聚合 + 概要
python capstone-科研数据分析/02_分析_cds.py
```

跑完会在 `capstone-科研数据分析/data/` 下生成本目录里同名的 3 个 CSV。

## 跟 Open-Meteo 路径数据对比

两份 5 年窗口**不完全重合**——Open-Meteo 是 2021-2025（旧主线），CDS 是 2020-2024（教学小请求）。
取重合的 2021-2024 四年看：

| 北京年均 (°C) | 2021 | 2022 | 2023 | 2024 | 4 年均 |
| --- | --- | --- | --- | --- | --- |
| Open-Meteo（日均→年均） | 12.70 | 12.64 | 13.44 | 13.75 | 13.13 |
| CDS（月均→年均，本目录） | 13.08 | 13.08 | 13.71 | 13.84 | 13.43 |
| 差 | +0.38 | +0.44 | +0.27 | +0.09 | **+0.30** |

> 两条路径系统性差 ~0.3 °C。原因：Open-Meteo 用日均聚合到年均，每天的日均又是 24 小时插值；
> CDS monthly_averaged_reanalysis 是官方按月聚合的产品，方法更标准。差值是符合预期的**算法差**，
> 不是"数据错"。同样的城市排序、同样的相对趋势——这两路都能讲清"近年升温"故事，
> 但发论文用 CDS，是因为它能直接给 DOI 和聚合定义。

## 为什么只有 5 年？

CDS API 的请求**排队 + 处理时间**不可控（3-30 分钟），5 年 × 月均的请求是 60 个时间步，
属于"小请求"——通常 1-2 分钟出结果。课程示例选这个量级是为了：

1. 学员第一次跑 CDS 不至于等到崩溃
2. CSV 小，方便 git 仓库直接带
3. 演示 cdsapi → NetCDF → CSV 的方法链跑通就够了

**真想做趋势研究**：把 `01_下载_cds.py --start-year 1995 --end-year 2024` 跑一次，CDS 大概排 5-15 分钟，
然后用月均自己写一个简单的 OLS 即可。**不要**用 `02_分析.py` 直接接 CDS 数据——
那个脚本是为日数据写的，schema 不一样。

## 数据使用声明 / 引用

CDS 拉到的 ERA5 数据，按 Copernicus License v1.2 引用：

> Hersbach, H., Bell, B., Berrisford, P., et al. (2023): ERA5 monthly averaged data on single levels
> from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS).
> DOI: 10.24381/cds.f17050d7

写综述 / 论文时**必须**引用这一条。Open-Meteo 路径属于"间接使用"，要写明"通过 Open-Meteo 历史天气 API 访问的 ERA5"。
