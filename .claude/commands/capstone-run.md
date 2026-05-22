---
description: 按顺序跑 capstone 的 01_下载 → 02_分析 → 03_出图，失败就停下并解释
---

# /capstone-run — 跑 capstone 数据流水线

依次执行 capstone 的三个数据脚本。**一步失败立刻停**，并用中文解释失败原因 + 下一步。

## 流程

1. **预检**（无 Bash 调用，先看文件）：
   - 当前目录是否在仓库根（看 `CLAUDE.md` 是否存在）
   - `capstone-科研数据分析/01_下载.py` 是否存在
   - 如果 `capstone-科研数据分析/data/raw/era5_all.csv` 已存在且 ≥ 70000 行，告诉用户"已有 30 年数据，是否复用？跳过 01 直接跑 02？"

2. **第 1 步：下载**
   - 跑 `python capstone-科研数据分析/01_下载.py`
   - 默认 30 年，约 1-2 分钟
   - **失败常见原因**：
     - 网络超时 → 提示用户切换 CDS 路径（`01_下载_cds.py`），或直接看 `example/capstone_5y_cds/data/` 里的 CDS 参考 CSV
     - 单城市失败 → 脚本本身会跳过，最后看 `era5_all.csv` 行数是否合理
   - 成功标志：stdout 打印 `[完成] 共 NNNNN 条`

3. **第 2 步：分析**
   - 跑 `python capstone-科研数据分析/02_分析.py`
   - 这步纯本地计算，几秒内
   - **失败常见原因**：
     - `[错误] 找不到 era5_all.csv` → 先跑第 1 步
     - `[安全闸] 年份样本太少` → 用户可能用了 5 年烟测数据，提示重跑第 1 步默认参数
   - 成功标志：写入 `era5_monthly.csv` / `era5_annual.csv` / `趋势汇总.csv`

4. **第 3 步：出图**
   - 跑 `python capstone-科研数据分析/03_出图.py`
   - **失败常见原因**：
     - 中文字体缺失 → 脚本有兜底，会用英文城市名，告诉用户可以忽略警告
   - 成功标志：`outputs/` 下出现 3 张 PNG

5. **总结**：跑完后用中文报告：
   - `data/raw/era5_all.csv` 多少行（应 ≥ 70000）
   - `data/processed/趋势汇总.csv` 多少行（应 = 7）
   - `outputs/` 下三张图是否都生成
   - **下一步建议**：跑 `/capstone-draft` 进入多角色起草

**不要**自己改脚本——只跑、只解释。
**不要**重复跑——除非用户明确要求。
**遇到 7 城都连不上**：告诉用户切到 CDS 路径（`01_下载_cds.py`），或从 `example/capstone_5y_cds/data/` 拷 CDS 参考 CSV 当输入跳过下载（注意 CDS 是月数据，要跑 `02_分析_cds.py` 不是 `02_分析.py`）。
