# 第 06 章 · Skill 封装

> PPT 57–67

## 读

```powershell
code 06-Skill封装/对比示例_有无Skill.md
```

同一任务开/不开 Skill 的 5 项打分。30 秒知道值不值得封。

## 学完能

把高频动作封成 SKILL.md，下次一句 `Use the X skill` 调出来。

## 怎么做

1. 挑用过 2 次以上的动作
2. 写 SKILL.md：触发 + 步骤 + 输出格式
3. 加验收规则
4. 真任务跑 3 次都顺即可

## 何时不封

只做一次的任务 / 规则经常变 / 团队就你一个人。

## 产出

**课程自写**（中文，贴近 capstone）：

- [`.claude/skills/数据清洗/SKILL.md`](./.claude/skills/数据清洗/SKILL.md)
- [`.claude/skills/出图/SKILL.md`](./.claude/skills/出图/SKILL.md)
- [`对比示例_有无Skill.md`](./对比示例_有无Skill.md)

**K-Dense vendor 4 个**（在仓库根 `.claude/skills/`，不在本章重复）：

| Skill | 对应 |
| --- | --- |
| `scientific-writing/` | 09 章「起草员」 |
| `peer-review/` | 09 章「审稿员」 |
| `scientific-critical-thinking/` | 09 章「批判员」 |
| `literature-review/` | 09 章「资料员」 |

上游 <https://github.com/K-Dense-AI/scientific-agent-skills>（MIT）。License [`.claude/skills/CREDITS.md`](./.claude/skills/CREDITS.md)。

## 怎么用

仓库根 `.claude/skills/` clone 后 Claude Code 自动识别。全局可用：

```powershell
xcopy /E /I "06-Skill封装\.claude\skills" "$env:USERPROFILE\.claude\skills"   # Windows
cp -r 06-Skill封装/.claude/skills/* ~/.claude/skills/                              # macOS/Linux
```

Claude Code 对话里 `用「数据清洗」Skill ...` 或 `Use the scientific-writing skill ...` 即可触发。

**判断流程**：新需求 → 先查 K-Dense 上游有没有现成的 → 没有再用本章 4 步法自写。

## 验收 → [验收清单.md](./验收清单.md)
