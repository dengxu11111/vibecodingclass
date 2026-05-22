# 第三方 Skill 来源与归属

本目录下大部分 Skill 是**老师自己写的**（中文名），少数 Skill 是从社区精选 vendor 而来（英文名）。

## 来自 K-Dense Inc. — 科研 Agent Skills

| Skill 目录 | 用途 | 上游 |
| --- | --- | --- |
| `scientific-writing/` | 科研稿件正文写作（IMRAD、引用风格、CONSORT/STROBE） | <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/scientific-skills/scientific-writing> |
| `peer-review/` | 结构化同行评议、稿件批评、清单式打分 | <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/scientific-skills/peer-review> |
| `scientific-critical-thinking/` | 批判性思考：证据评估、逻辑陷阱识别 | <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/scientific-skills/scientific-critical-thinking> |
| `literature-review/` | 文献综述：检索、聚类、缺口识别、综述结构 | <https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/scientific-skills/literature-review> |

**版权**：K-Dense Inc. © 2025，MIT License。
**LICENSE 全文**：<https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/LICENSE.md>

按 MIT 协议要求，下列声明随同 Skill 一起分发：

```
MIT License

Copyright (c) 2025 K-Dense Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 修改说明

本仓库**只 vendor 了上游每个 Skill 的 SKILL.md 部分**（提示词 / 验收规则 / 工作流程），**没有**复制：

- 上游 `references/`（Skill 引用的详细文档，30–200 KB 一份）
- 上游 `scripts/`（Skill 调用的辅助 Python 脚本，部分有外部依赖）
- 上游 `assets/`（Skill 配套素材，多为图片）

需要完整版的同学，照上表里的链接 `git clone` 上游仓库即可（仓库整体 ~50 MB）。

唯一的修改：**移除了 emoji**（Windows GBK 控制台对 emoji 不友好），其余内容、frontmatter、license 字段保持原样。

## 同步原则

K-Dense 升级了上游 SKILL.md 后想同步本课程内的副本：

```powershell
# 例：同步 peer-review
gh api "repos/K-Dense-AI/scientific-agent-skills/contents/scientific-skills/peer-review/SKILL.md" `
  | python -c "import json,sys,base64,re; d=json.load(sys.stdin); t=base64.b64decode(d['content']).decode('utf-8'); t=re.sub(r'[\U0001F300-\U0001FAFF\U00002600-\U000027BF]','',t); open(r'06-Skill封装\.claude\skills\peer-review\SKILL.md','w',encoding='utf-8').write(t)"

# 同时同步 active 副本
copy "06-Skill封装\.claude\skills\peer-review\SKILL.md" ".claude\skills\peer-review\SKILL.md"
```

## 课程自写 Skill

`数据清洗/` 和 `出图/` 是老师自己写的，**不属于** K-Dense 上游。它们的归属与课程整体一致（见仓库根 LICENSE）。

根 `.claude/skills/` 下还有一个 `数字核验/`（capstone 第 5 步专用），同样是老师自写。
