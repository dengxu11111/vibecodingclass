# Third-Party Notices

本仓库重新分发了若干第三方内容。**根 `LICENSE` 不取代任何第三方协议**——下面每一项以其原始许可证为准。

## 1. Copernicus / ECMWF ERA5 reanalysis 数据样本

**范围**：`example/capstone_5y_cds/data/` 下的 3 个 CSV（合计约 22 KB），由 capstone 的 `01_下载_cds.py` 从 Copernicus CDS API 抓取。

**底层数据**：ERA5 reanalysis (Hersbach et al., 2020, 2023)，欧洲中期天气预报中心 (ECMWF) 出品的全球大气再分析。

**许可证**：[Licence to use Copernicus Products v1.2](./licenses/COPERNICUS-LICENSE-v1.2.txt)（License agreement for the use of Copernicus Products by Copernicus contributors and other users）。要点：

- ✓ 免费使用（含商业）
- ✓ 可以再分发（含派生品）
- ✓ **必须引用**数据生产者 (ECMWF) 与 Copernicus Climate Change Service
- ✗ 不得隐藏 / 删除归属
- ✗ 数据本身无保修，使用者自担风险

**必须引用**（写综述 / 论文 / 任何对外发布时）：

> Hersbach, H., Bell, B., Berrisford, P., et al. (2023): ERA5 monthly averaged data on single levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI: <https://doi.org/10.24381/cds.f17050d7>

Open-Meteo 路径（`capstone-科研数据分析/01_下载.py` 拉到的数据）属于"通过 Open-Meteo 代理访问的 ERA5"，应在致谢部分写明 Open-Meteo + 上面这条 Hersbach 引用。

许可证全文：[licenses/COPERNICUS-LICENSE-v1.2.txt](./licenses/COPERNICUS-LICENSE-v1.2.txt)

---

## 2. K-Dense scientific-agent-skills

**范围**：`06-Skill封装/.claude/skills/` 与 `.claude/skills/` 下的 4 个 Skill 目录：

- `literature-review/`
- `scientific-writing/`
- `peer-review/`
- `scientific-critical-thinking/`

**版权**：K-Dense Inc. © 2025

**许可证**：MIT License

**上游**：<https://github.com/K-Dense-AI/scientific-agent-skills>

**修改说明**：仅复制 SKILL.md（去 emoji），未改其它内容。完整归属 / LICENSE 全文 / 同步命令见 [`06-Skill封装/.claude/skills/CREDITS.md`](./06-Skill封装/.claude/skills/CREDITS.md)。

---

## 3. Open-Meteo Historical Weather API

**范围**：`capstone-科研数据分析/01_下载.py` 调用此 API 抓数据。本仓库**不分发** Open-Meteo 数据本身（你自己跑）。

**API**：<https://open-meteo.com/en/docs/historical-weather-api>

**许可证**：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)（attribution required）

**底层数据**：仍是 ERA5——见上方 §1 的 Copernicus 引用要求。引用 Open-Meteo 时按其[官方建议](https://open-meteo.com/en/license)：

> Weather data by [Open-Meteo](https://open-meteo.com/)

---

## 4. HKUDS/CLI-Anything（仅文档参考）

**范围**：第 07 章 README 与 资源/参考链接.md 引用了该项目，**没有 vendor 其代码**。

**版权**：HKUDS · Apache-2.0 License

**上游**：<https://github.com/HKUDS/CLI-Anything>

---

## 关于本仓库自身

根 [LICENSE](./LICENSE) 给课程代码 (MIT) 和教学内容 (CC BY 4.0) 分别授权。**第三方组件按本文件中各自的协议处理**——不被根 LICENSE 覆盖。

如果你 fork 本仓库并新增 vendor 自第三方的内容，请追加到本文件。
