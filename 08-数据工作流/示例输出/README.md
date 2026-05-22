# `08-数据工作流/示例输出/` —— 离网兜底 + 数据形态参考

教室没网或 arXiv API 抽风时，本目录的 CSV 可以直接喂给后续两个脚本，**跳过下载步骤**继续上课。

## 文件

| 文件 | 行数 | 大小 | 说明 |
| --- | --- | --- | --- |
| `arxiv_10条样例.csv` | 10 篇 | ~5 KB | 2020-2024 年 LLM 方向代表论文，6 列：`arxiv_id, title, summary, published_date, category, authors` |

10 篇都是真实的 LLM 经典 / 关键论文（GPT-3、LoRA、CoT、InstructGPT、ReAct、LLaMA、GPT-4、ToT、Mixtral、DeepSeek-V3），arxiv_id 能在 https://arxiv.org/abs/<id> 直接查到。

## 怎么用

### 场景：网炸了，从清洗步骤继续

```powershell
cd '<repo-root>'

# 1. 把样例 CSV 当成"刚下载"的原始数据
mkdir -p data/raw
copy 08-数据工作流\示例输出\arxiv_10条样例.csv data\raw\arxiv_llm.csv

# 2. 跑清洗（08-数据工作流/数据清洗.py 默认读 data/raw/arxiv_*.csv）
python 08-数据工作流\数据清洗.py

# 3. 出图
python 08-数据工作流\出图.py
```

### 场景：只想看 CSV 长什么样

直接在 VS Code 或 Excel 打开 `arxiv_10条样例.csv`，看 6 列怎么排——
学员第一次写下载脚本时容易把 summary 列里的换行符 / 引号搞坏，
看一遍真实样例 CSV 就知道目标形态了。

### 场景：跟自己跑的结果对比

```powershell
# 在 VS Code 里
code --diff data\raw\arxiv_llm.csv 08-数据工作流\示例输出\arxiv_10条样例.csv
```

## 为什么只放 10 篇？

- 教学场景够用：10 篇能演示去重、字段清洗、按年份 / 类别聚合、最早 / 最新论文等所有清洗模式
- 体积小：~5 KB，git 仓库无压力
- 真实性：每篇都是 LLM 领域**真存在的标志性论文**，学员自己跑 `arxiv` API 也能搜到——可以**对比"我跑出来的"和"参考样例"**

想要更多数据（比如 200 篇）：

```powershell
python 08-数据工作流\下载脚本.py --keyword "large language model" --limit 200
```
