# pipeline_template · 跨学科 4 步骨架

不是 demo，是把第 08 章和 capstone 的公共骨架抽出来的脚手架，让任何方向的研究者 30 分钟套到自己数据。

## 4 步模式

```
01_download  →  data/raw/*.csv              抓数据
02_analyze   →  data/processed/*.csv         清洗 + 聚合 + 计算
03_plot      →  outputs/*.png                可视化
04_draft.md  →  outputs/*.md                 多模型协作写稿
```

模式不变，每步 80% 代码（路径处理、CSV、sleep、错误兜底）也不变。**变的是 20%**——数据源 / 聚合维度 / 检验方法 / 主图。

## 跨学科映射

| 方向 | 数据源 | 关键聚合 | 检验 / 计算 | 主图 |
| --- | --- | --- | --- | --- |
| 气候 / 遥感 (capstone) | Open-Meteo / cdsapi | 年均 / 月均 | OLS + MK + Sen | 趋势线 + 趋势条形 |
| 文献计量 (08 章) | arXiv / OpenAlex API | 按类目 / 时间 | 频次 + 增长率 | 月度柱状 + Top-N |
| 生信 | NCBI / GEO / UniProt | 按基因 / 通路 | t-test / DESeq2 | 火山 / 富集气泡 |
| 经济 / 金融 | FRED / Yahoo / Wind | 同比 / 环比 | OLS + ADF + 协整 | 时序 + 滚动相关 |
| 社科 / 调查 | 问卷 / 公开微观 | 分组均值 | 卡方 / ANOVA | 分组柱状 + 残差 |
| 临床 / 流行病 | 实验室 / RCT 元数据 | 按 arm / 时间到事件 | log-rank + Cox | KM 曲线 + 森林 |
| 化学 / 材料 | PubChem / Materials Project | 指纹 / 属性聚类 | RDKit + RF | 散点 + Tanimoto 热图 |

方向不在上面也照填，模式一样。

## 用法

```powershell
# 1. 拷到你自己的项目根（不要在本课程仓库里跑，会污染示例）
cp -r pipeline_template ~/your-project-root/my_pipeline

# 2. 按文件头 TODO 改 4 个模板
cd ~/your-project-root/my_pipeline
# 编辑 01_download.template.py / 02_analyze.template.py / 03_plot.template.py / 04_draft.template.md

# 3. 跑通——有 1 行真数据就算过第一关
python 01_<你的领域>.py && python 02_<...>.py && python 03_<...>.py
```

## 与 08 章 / capstone 的关系

| | 08 章 | capstone | pipeline_template |
| --- | --- | --- | --- |
| 目的 | 教模式（arXiv 友好示例） | 跑真科研（ERA5 完整） | 空脚手架，套自己方向 |
| 可跑 | ✓ | ✓ | ✗（含 TODO） |
| 领域 | 论文 metadata | 气候网格 | **由你填** |

## 故意没写进模板

- 不绑定 pandas / scipy / sklearn——你领域要用就自己 `pip install`
- 不绑定 csv schema——02 读 csv 的部分是 TODO
- 不绑定模型 / API key——04 prompt 是模型无关
- 不绑定 MCP server——MCP 抽象比 Skill 难泛化，先跑通 4 步再决定要不要包装

## 验收

跑完一次自己领域的 4 步，能回答：

- [ ] 我领域的最小数据样本是什么？
- [ ] 01 需要 API key / sleep / 版权许可吗？
- [ ] 02 关键聚合维度（时间 / 类目 / 个体）？
- [ ] 03 有学科约定俗成的"必出图"吗？
- [ ] 04 多模型 3 角色在我领域是否合理？要不要合并 / 砍？
