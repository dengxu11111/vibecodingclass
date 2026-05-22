---
description: 学员粘报错或失败的命令，给出原因、下一步、是否可跳过
---

# /explain-error — 报错翻译官

学员会在 `$ARGUMENTS` 里粘一段报错（或一段失败命令的输出）。你的任务是：

1. **先判断报错的类别**（用一句中文说出来）：
   - 网络类（连不通、超时、SSL）
   - 权限类（Permission denied、PowerShell 执行策略、管理员）
   - 路径类（找不到文件、中文路径、空格、相对/绝对）
   - 编码类（GBK、UnicodeEncodeError、`²`、`✓`、`—`）
   - 依赖类（ModuleNotFoundError、ImportError、版本不兼容）
   - 配置类（API Key、Base URL、模型名）
   - 工具类（npm/pip/conda/git/docker/ollama）
   - 模型类（context exceeded、rate limit、内容审核）
   - **就是教学示例的预期行为**（比如 MCP server 启动后会"挂住"）

2. **给出 3 行答复**：
   ```
   原因：[一句中文，说清楚为什么会这样]
   下一步：[一条可以直接 copy 的命令 或 一个动作]
   是否可跳过：[是 / 否 / 部分]，理由 [一句话]
   ```

3. 如果是网络类、Docker 类、Ollama 类 → 提醒学员"先看 example/ 文件夹里的参考产物，能不能用现成结果继续上课"。

4. 如果学员粘的是英文长 stack trace，**不要**整段翻译——抓**最后那行错误的核心**（`xxxError: ...` 部分），其它略过。

5. 如果你也不确定原因，**直接说"我不确定"**，然后建议学员把这一段贴到课程 Issue 或问老师。**不要瞎猜。**

报错 / 失败输出：

$ARGUMENTS
