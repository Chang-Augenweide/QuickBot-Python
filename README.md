# QuickBot-Python 🐍

> **轻量级个人 AI 助手框架** | [Go 版本](https://github.com/Chang-Augenweide/QuickBot-Go)

<div align="center">

**一个轻量级、模块化、可扩展的个人 AI 助理框架**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open Issues](https://img.shields.io/github/issues-raw/Chang-Augenweide/QuickBot-Python)](https://github.com/Chang-Augenweide/QuickBot-Python/issues)
[![Repository Size](https://img.shields.io/github/repo-size/Chang-Augenweide/QuickBot-Python)](https://github.com/Chang-Augenweide/QuickBot-Python)

</div>

---

## ✨ 特性

QuickBot-Python 是一个功能完整的 AI 助手框架，让你轻松构建自己的智能助手。

### 🎯 核心功能

- **🤖 多 AI 提供商** - 支持 OpenAI、Anthropic、Ollama（本地模型）
- **📱 多平台支持** - Telegram、Discord、Slack
- **💾 智能内存管理** - 会话记忆 + 长期记忆（SQLite）
- **⏰ 任务调度系统** - 支持一次性任务和周期性任务（Cron 表达式）
- **🔧 可扩展工具系统** - 内置文件、Shell、计算工具，支持自定义扩展
- **🛡️ 安全特性** - API 密钥加密、用户验证、日志审计

---

## 🏗️ 系统架构

```
QuickBot 生态系统
        │
        ├─ 核心层
        │   ├─ Agent (AI 代理)
        │   ├─ Memory (内存管理)
        │   ├─ Scheduler (任务调度)
        │   └─ Tools (工具系统)
        │
        ├─ AI 层
        │   ├─ OpenAI Provider
        │   ├─ Anthropic Provider
        │   └─ Ollama Provider
        │
        └─ 平台层
            ├─ Telegram
            ├─ Discord
            └─ Slack
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- SQLite 3

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Chang-Augenweide/QuickBot-Python.git
cd QuickBot-Python

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化配置
cp config.example.yaml config.yaml
nano config.yaml

# 4. 运行 QuickBot
python cmd/quickbot/main.py
```

### 配置示例

```yaml
# Bot 基本信息
bot:
  name: QuickBot
  debug: false
  timezone: Asia/Shanghai

# AI 提供商配置
ai:
  provider: openai  # openai, anthropic, ollama
  api_key: your_api_key_here
  model: gpt-4o
  temperature: 0.7

# 平台配置
platforms:
  telegram:
    enabled: true
    token: your_telegram_bot_token
    allowed_users: []  # 空数组允许所有用户

# 内存管理
memory:
  enabled: true
  max_messages: 1000
  storage: memory.db

# 任务调度
scheduler:
  enabled: true
  storage: scheduler.db
```

---

## 📚 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/help` | 显示帮助信息 | `/help` |
| `/status` | 查看系统状态 | `/status` |
| `/remind` | 设置提醒 | `/remind 14:30 下午开会` |
| `/memory` | 存储或检索信息 | `/memory set name 张三` |
| `/tasks` | 查看任务列表 | `/tasks` |

---

## 🛠️ 自定义工具

创建自定义工具非常简单：

```python
from internal.tools.tools import ToolBase

class MyCustomTool(ToolBase):
    """自定义工具示例"""

    def get_schema(self):
        return {
            'name': 'my_tool',
            'description': '我的自定义工具',
            'parameters': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string', 'description': '输入文本'}
                },
                'required': ['text']
            }
        }

    async def execute(self, text: str) -> str:
        # 实现你的逻辑
        result = f"处理结果: {text}"
        return result
```

将工具文件保存到 `tools/` 目录，QuickBot 会自动加载。

### 内置工具

QuickBot-Python 提供以下内置工具：

| 工具名 | 功能 | 权限 |
|--------|------|------|
| `file_read` | 读取文件内容 | owner |
| `file_write` | 写入文件 | owner |
| `shell_exec` | 执行 shell 命令 | owner |
| `calculator` | 数学计算 | allow_all |
| `weather` | 查询天气 | allow_all |
| `translator` | 文本翻译 | allow_all |

---

## 📊 性能优化

QuickBot-Python 经过优化，可支持：

- **100+** 同时在线用户
- **1000+** 每分钟消息处理
- **<500ms** 平均响应时间

### 优化建议

1. 使用本地 AI 模型（Ollama）降低延迟
2. 配置合理的内存过期时间
3. 定期清理 SQLite 数据库

---

## 🔧 故障排除

### 问题：Python 版本不兼容

```bash
# 检查 Python 版本
python --version

# 如果版本低于 3.8，使用 pyenv 安装
pyenv install 3.11.0
pyenv global 3.11.0
```

### 问题：依赖安装失败

```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 问题：数据库文件损坏

```bash
# 删除损坏的数据库文件
rm memory.db scheduler.db

# 重启 QuickBot，会自动创建新数据库
python cmd/quickbot/main.py
```

---

## 📖 文档

- **[API 文档](docs/API.md)** - 详细的 API 参考
- **[部署指南](docs/DEPLOYMENT.md)** - 生产环境部署
- **[贡献指南](CONTRIBUTING.md)** - 如何贡献代码

---

## 🤝 贡献

欢迎贡献代码！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新。

---

## 🔗 相关项目

- **[QuickBot-Go](https://github.com/Chang-Augenweide/QuickBot-Go)** - Go 语言版本实现
- **QuickBot 原版](https://github.com/Chang-Augenweide/QuickBot)** - 已归档，请使用新仓库

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

感谢以下开源项目：

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [discord.py](https://github.com/Rapptz/discord.py)
- [slack-sdk](https://github.com/slackapi/python-slack-sdk)
- [APScheduler](https://github.com/agronholm/apscheduler)
- [PyYAML](https://github.com/yaml/pyyaml)

---

<div align="center">

**⚡ 开始你的 AI 助手之旅！**

如果这个项目对你有帮助，请给个 ⭐ Star！

Made with ❤️ by [Chang-Augenweide](https://github.com/Chang-Augenweide)

</div>
