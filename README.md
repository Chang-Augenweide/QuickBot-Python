<div align="center">

# QuickBot 🚀

**一个轻量级、模块化、可扩展的个人 AI 助理框架**

[Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
[Go](https://img.shields.io/badge/Go-1.22+-cyan.svg)
[License](https://img.shields.io/badge/License-MIT-green.svg)

[📚 完整文档](docs/README.md) | [🚀 快速开始](#快速开始) | [📖 部署指南](docs/DEPLOYMENT.md) | [💬 社区](https://github.com/Chang-Augenweide/QuickBot/discussions)

</div>

---

## ✨ 特性

QuickBot 是一个功能完备的个人 AI 助理框架，支持多平台、多云 AI 提供商、内存管理、任务调度和强大的工具系统。

### 🎯 核心功能

- **🤖 多 AI 提供商** - 支持 OpenAI、Anthropic、Ollama 及其他 OpenAI 兼容 API
- **📱 多平台支持** - Telegram、Discord、Slack（微信规划中）
- **💾 内存管理** - 会话记忆 + 长期记忆，智能上下文检索
- **⏰ 任务调度** - 一次性任务、周期性任务、提醒事项，支持 Cron 表达式
- **🔧 工具系统** - 文件操作、Shell 命令、计算功能，支持自定义工具扩展
- **🔒 安全可靠** - API 密钥加密、用户验证、命令白名单、日志审计
- **🐳 Docker 支持** - 开箱即用的容器化部署
- **☸️ Kubernetes 就绪** - 支持云原生部署

### 🏗️ 技术栈

| 组件 | Python | Go |
|------|--------|-----|
| **核心逻辑** | ✅ 完整实现 | ✅ 高性能版本 |
| **内存管理** | ✅ SQLite | ✅ 优化实现 |
| **任务调度** | ✅ Cron 支持 | 🔜 开发中 |
| **平台适配** | ✅ Telegram/Discord/Slack | 🔜 开发中 |

---

## 📊 项目架构

```
QuickBot/
├── cmd/                   # 命令行工具
│   └── quickbot/
│       └── main.py       # 主入口
├── internal/              # 内部模块
│   ├── agent/            # 核心 Agent 逻辑
│   ├── ai/               # AI 提供商集成
│   ├── config/           # 配置管理
│   ├── memory/           # 内存管理
│   ├── scheduler/        # 任务调度
│   ├── tools/            # 工具系统
│   └── security/         # 安全模块
├── platforms/             # 平台适配器
│   ├── telegram.py       # Telegram 平台
│   └── ...
├── configs/               # 配置文件
├── docs/                  # 完整文档
├── tests/                 # 测试套件
├── examples/              # 示例代码
└── scripts/               # 工具脚本
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装与运行

#### 1. 克隆仓库

```bash
git clone https://github.com/Chang-Augenweide/QuickBot.git
cd QuickBot
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置启动

```bash
# 复制配置模板
cp config.example.yaml config.yaml

# 编辑配置文件，填写你的 API 密钥
nano config.yaml

# 启动 QuickBot
python cmd/quickbot/main.py
```

### 🎉 验证安装

运行 `python cmd/quickbot/main.py --init` 来验证环境和配置。

---

## 📖 使用指南

### 基本命令

QuickBot 支持内置命令和自然语言交互：

| 命令 | 说明 | 示例 |
|------|------|------|
| `/help` | 显示帮助信息 | `/help` |
| `/status` | 查看系统状态 | `/status` |
| `/remind` | 设置提醒 | `/remind 09:00 开会` |
| `/memory` | 存储/检索信息 | `/memory set 姓名 张三` |
| `/tasks` | 列出计划任务 | `/tasks` |

### 配置示例

在 `config.yaml` 中配置你的 AI 提供商：

```yaml
ai:
  provider: openai  # 可选: openai, anthropic, ollama
  api_key: your_api_key_here
  model: gpt-4o
  base_url: https://api.openai.com/v1
  max_tokens: 2000
  temperature: 0.7

platforms:
  telegram:
    enabled: true
    token: your_telegram_bot_token
    allowed_users:
      - user1@example.com

memory:
  enabled: true
  max_messages: 1000
  storage: memory.db

scheduler:
  enabled: true
  storage: scheduler.db
```

### 自定义工具

在 `examples/` 目录下有示例代码，展示如何创建和使用自定义工具：

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
                    'input': {'type': 'string', 'description': '输入参数'}
                }
            }
        }

    async def execute(self, input: str) -> str:
        # 实现你的逻辑
        return f"处理结果: {input}"
```

---

## 📚 文档

- **[完整文档](docs/README.md)** - 详细的功能说明和 API 参考
- **[部署指南](docs/DEPLOYMENT.md)** - Docker、Kubernetes、systemd 等生产环境部署
- **[更新日志](docs/CHANGELOG.md)** - 版本更新内容

---

## 🐳 Docker 部署

### 快速启动

```bash
# 构建镜像
docker build -t quickbot:latest .

# 运行容器
docker run -d \
  --name quickbot \
  -p 8080:8080 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v quickbot_data:/app/data \
  quickbot:latest
```

### Docker Compose

```bash
# 一键启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f quickbot
```

---

## 📈 性能指标

| 指标 | Python 版本 | Go 版本 |
|------|------------|---------|
| 内存占用 | < 50 MB | < 20 MB |
| 平均响应时间 | < 1s | < 0.5s |
| 并发会话 | 100+ | 500+ |
| 内存容量 | > 10,000 条消息 | > 20,000 条消息 |

---

## 🛠️ 开发路线图

### ✅ 已完成

- [x] AI 集成（OpenAI、Anthropic、Ollama）
- [x] 多平台框架（Telegram、Discord、Slack）
- [x] 内存管理（会话 + 长期）
- [x] 任务调度（Cron、提醒）
- [x] 工具系统（文件、Shell、计算）
- [x] 配置管理（YAML、环境变量）
- [x] 安全模块（加密、验证、审计）
- [x] Docker 支持

### 🔜 进行中

- [ ] Go 模块优化
- [ ] Web 管理界面
- [ ] 插件系统完善

### 🗓️ 计划中

- [ ] 向量数据库集成（语义搜索）
- [ ] 多模态支持（图像、语音）
- [ ] 工作流编排
- [ ] 微信平台支持

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- Python 遵循 [PEP 8](https://pep8.org/)
- Go 遵循 [Effective Go](https://go.dev/doc/effective_go)
- 添加适当的文档字符串和注释
- 编写单元测试

---

## 🔒 安全特性

- API 密钥加密存储
- 用户验证和授权（allowed_users）
- 命令白名单机制（仅调试模式）
- 路径访问限制（沙盒环境）
- 完整的日志审计追踪

---

## 📄 许可证

本项目采用 [MIT License](docs/LICENSE) 开源。

---

## 🙏 致谢

感谢所有贡献者和开源项目的支持！

---

## 📧 联系方式

- **项目主页**: [GitHub](https://github.com/Chang-Augenweide/QuickBot)
- **问题反馈**: [Issues](https://github.com/Chang-Augenweide/QuickBot/issues)
- **讨论区**: [Discussions](https://github.com/Chang-Augenweide/QuickBot/discussions)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个 Star！**

Made with ❤️ by [Chang-Augenweide](https://github.com/Chang-Augenweide)

</div>
