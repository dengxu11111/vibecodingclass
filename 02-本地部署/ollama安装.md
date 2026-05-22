# Ollama 安装

## Windows

下载安装包：<https://ollama.com/download/windows>

装完打开 PowerShell：

```powershell
ollama --version
ollama pull qwen3.5:4b        # 中文好、6G 内存就能跑
ollama pull qwen3.5:0.6b      # 显存小的同学先试这个
ollama run qwen3.5:4b "用一句话介绍你自己"
```

## macOS

```bash
brew install ollama
brew services start ollama   # 后台跑
ollama pull qwen3.5:4b
```

## Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
ollama pull qwen3.5:4b
```

## 常用命令

```powershell
ollama list                  # 已下载的模型
ollama ps                    # 正在跑的模型
ollama rm qwen3.5:4b         # 删除模型
ollama show qwen3.5:4b       # 看模型详情
```

## 推荐模型清单

| 模型 | 大小 | 适合 |
| --- | --- | --- |
| `qwen3.5:0.6b` | < 1 GB | 极低资源，跑通流程用 |
| `qwen3.5:4b` | 2.5 GB | 中文问答主力 |
| `qwen3-coder:30b-a3b` | 2.5 GB | 写代码 |
| `qwen3.5:30b-a3b` | 9 GB | 显存 ≥ 16G，效果显著上升 |
| `llama3.1:8b` | 4.9 GB | 英文场景 |
| `deepseek-r1:7b` | 4.7 GB | 本地推理模型 |

## 默认端口

`http://localhost:11434`，所有 HTTP API 都打这个端口。
