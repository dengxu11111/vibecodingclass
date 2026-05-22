# `example/` —— 参考产物 / 离线兜底

教室网炸了 / 工具没装好 / 想跟标准答案对比，看这里。

## 目录

```
example/
├── EXAMPLE-README.md
└── capstone_5y_cds/           CDS · Copernicus 路径（真实科研流，5 年月均）
    ├── README.md              详细说明 + 跟 Open-Meteo 路径的差异对比
    └── data/
        ├── raw/era5_cds_monthly.csv         7 城 × 60 月 = 420 行（21 KB）
        └── processed/
            ├── era5_cds_annual.csv          7 城 × 5 年（年均）
            └── era5_cds_summary.csv         5 年均 / 最冷年 / 最暖年 / 年差
```

## 怎么用

```powershell
# 跳过下载，从分析步骤继续
xcopy /E /I example\capstone_5y_cds\data capstone-科研数据分析\data
python capstone-科研数据分析\02_分析_cds.py
```

```powershell
# 跟自己的结果 diff
code --diff capstone-科研数据分析\data\processed\era5_cds_annual.csv example\capstone_5y_cds\data\processed\era5_cds_annual.csv
```

## Open-Meteo 30 年没有 example，故意的

Open-Meteo 路径**无 key、无 VPN、无账号**就能跑，课堂主线设定：**每位学员自己跑一次**比看现成答案学得扎实。

讲师想准备 Open-Meteo 现成产物（应对无网）→ 自己跑 `python 01_下载.py && python 02_分析.py && python 03_出图.py`，把产出复制到 `example/capstone_30y/`，写对应 README。本仓库**故意不预装**。

## 这里不能放

- `.env` / API Key / cookie / token
- 个人路径 / 本机用户名 / 邮箱
- `.claude/settings.local.json`
- 真实学生 / 受访者数据
- 未授权论文 PDF
- > 10 MB 的二进制 / NetCDF

看见这些泄漏到 example/，**第一时间 issue**，不要 push。
