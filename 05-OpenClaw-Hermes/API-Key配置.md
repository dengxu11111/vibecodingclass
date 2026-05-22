# API Key 配置

> OpenClaw 不自带模型，需要你接一家模型 API。下面三家任选一家。

## 选项 1：DeepSeek（首推，国产、便宜）

1. 浏览器打开 <https://platform.deepseek.com/api_keys>
2. 注册账号 → 实名认证 → 充值（10 元够用很久）
3. 点「创建 API Key」，复制以 `sk-` 开头的字符串
4. 打开 OpenClaw → 设置 → 模型 → 选择 DeepSeek → 粘贴 Key → 保存

测试：在 OpenClaw 的对话窗口里发"你好"，看到回复就配好了。

## 选项 2：OpenRouter（聚合多家、有免费额度）

1. 浏览器打开 <https://openrouter.ai/keys>（需要科学上网）
2. 注册账号（不用充值也有少量免费额度）
3. 创建 Key，复制 `sk-or-v1-...`
4. OpenClaw → 设置 → 模型 → OpenRouter → 粘贴 Key

OpenRouter 上的免费模型可在 <https://openrouter.ai/models?max_price=0> 查看，名字末尾会有 `:free`。

## 选项 3：智谱 GLM

1. 浏览器打开 <https://bigmodel.cn/glm-coding>
2. 注册 → 进入控制台 → API Keys → 创建
3. OpenClaw → 设置 → 模型 → 智谱 / 自定义 OpenAI 兼容 → 填 Key 和 Base URL

智谱的 Base URL：`https://open.bigmodel.cn/api/paas/v4`

## 通用建议

- **Key 不要进 git**：放在 OpenClaw 配置里就好，不要写进项目代码
- **学生账号 / 助教账号分开**：避免大家共享 Key 跑爆额度
- **跑批之前先看余额**：DeepSeek 的 usage 页面会告诉你今天烧了多少

## 模型推荐

| Provider | 推荐模型 ID | 适合 |
| --- | --- | --- |
| DeepSeek | `deepseek-chat` | 日常任务（V3） |
| DeepSeek | `deepseek-reasoner` | 推理 / 思辨（R1） |
| OpenRouter | `meta-llama/llama-3.1-8b-instruct:free` | 免费、体验 Agent 流程 |
| 智谱 | `glm-4.5` | 中文写作 |
