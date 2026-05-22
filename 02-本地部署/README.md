# 第 02 章 · 大模型本地部署

> PPT 17–28

## 跑

```powershell
ollama pull qwen3.5:4b
python 02-本地部署/测试本地模型.py
```

跑通后看 [示例任务/本地模型试金石.md](./示例任务/本地模型试金石.md)：3 个 5 分钟评估。

## 学完能

笔记本上跑起不联网中文 AI；做涉密数据 / 内网知识库都不外泄。

## 怎么做

1. Ollama + 小模型先跑通
2. Docker 起 Open WebUI 连 `localhost:11434`
3. 上传本地资料建知识库
4. 端到端跑"问知识库 → 出答案"

## 底线

本地模型能力**永远不会**超过同等成本的云端模型。本章追求可用 / 隐私 / 自主，不追求最强。

## 产出

- [测试本地模型.py](./测试本地模型.py)
- [docker-compose.yml](./docker-compose.yml) — Open WebUI 一键起
- [ollama安装.md](./ollama安装.md)
- [示例任务/本地模型试金石.md](./示例任务/本地模型试金石.md)
- [验收清单.md](./验收清单.md)

## 起 Open WebUI

```powershell
cd 02-本地部署
docker compose up -d
# 浏览器开 http://localhost:3000
```
