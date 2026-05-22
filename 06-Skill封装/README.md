# 第 06 章 · Skill 封装

> 对应 PPT 第 57–67 页

## WHAT

- 核心对象：Skill / SKILL.md / Workflow / Validation
- 真实场景：vibe 出一个有用的工作流，第二次不想重写
- 学完能干什么：把高频动作沉淀成 Claude Code Skill，下次一句话调出来

## WHY

每次都从零跟 Agent 解释一遍同样的需求——又慢、又容易遗漏关键约束。Skill ≠ Python 包；它是**给 Agent 看的说明书**，告诉它"什么时候用、怎么用、怎么验收"。

## HOW（4 步）

1. **挑高频动作**：一周用过 2 次以上的工作流
2. **写 SKILL.md**：触发条件 + 步骤 + 输出格式
3. **加验收规则**：避免"看似完整但空泛"的结果
4. **真任务反复迭代**：跑 → 改 → 跑，三次都顺即可

## 本章产出

**课程自写 Skill**（中文化、贴近 capstone）：

- [`.claude/skills/数据清洗/SKILL.md`](./.claude/skills/数据清洗/SKILL.md)
- [`.claude/skills/出图/SKILL.md`](./.claude/skills/出图/SKILL.md)

**从 K-Dense 社区 vendor 的 4 个生产级科研 Skill**（在仓库根 `.claude/skills/`，不在本章重复）：

| Skill | 用途 | 对应课程角色 |
| --- | --- | --- |
| `scientific-writing/` | IMRAD、APA/AMA、CONSORT/STROBE | 第 09 章「起草员」 |
| `peer-review/` | 结构化同行评议、清单式打分 | 第 09 章「审稿员」 |
| `scientific-critical-thinking/` | 证据评估、逻辑陷阱识别 | 第 09 章「批判员」 |
| `literature-review/` | 综述：检索、聚类、缺口识别 | 第 09 章「资料员」 |

License 与归属：[`.claude/skills/CREDITS.md`](./.claude/skills/CREDITS.md)。

## 生态：K-Dense scientific-agent-skills

社区已经把很多科研动作封成了 Skill——**别什么都自己写**。

上游：<https://github.com/K-Dense-AI/scientific-agent-skills>（MIT；具体 Skill 数以上游为准）

覆盖：数据 / 统计、生命科学、化学量子、可视化、写作评审、AI/ML。判断流程：

```
拿到新需求 → 先查上游有没有现成的
  → 有：vendor 到 .claude/skills/<name>/，按 MIT 注明出处
  → 没有 / 不合用：用本章 4 步法自己写
```

## 怎么用

```powershell
# 仓库根 .claude/skills/ 已经放好，clone 之后 Claude Code 直接识别。
# 想在所有项目里全局可用，复制到用户目录：
# Windows:
xcopy /E /I "06-Skill封装\.claude\skills" "$env:USERPROFILE\.claude\skills"
# macOS / Linux:
cp -r 06-Skill封装/.claude/skills/* ~/.claude/skills/

# 在 Claude Code 对话里直接触发：
# "用「数据清洗」Skill 把 data/qml.csv 去重并按日期排序"
# "Use the scientific-writing skill to draft a Methods section based on 02_分析.py"
```

## A/B 对比示例

[对比示例_有无Skill.md](./对比示例_有无Skill.md) —— 同一个数据清洗任务，启不启用 Skill 的 5 项打分对比。看完知道什么时候**值得**封。

## 验收 → 见 [验收清单.md](./验收清单.md)
