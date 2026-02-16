# 贡献指南

感谢你对 QuickBot 项目的兴趣！我们非常欢迎社区贡献本文档将帮助你快速开始。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试指南](#测试指南)
- [文档贡献](#文档贡献)

---

## 🌟 行为准则

在参与本项目时，请遵守以下行为准则：

- **尊重和包容** - 尊重不同的观点和经验
- **建设性反馈** - 提供建设性的反馈建议
- **专注于项目** - 贡献应与项目目标一致
- **接受批评** - 以开放的心态接受对自己工作的批评

---

## 🚀 如何贡献

### 报告 Bug

如果你发现了 bug，请：

1. 检查 [Issues](https://github.com/Chang-Augenweide/QuickBot/issues) 确保问题尚未被报告
2. 创建一个新的 Issue，使用清晰的标题
3. 在 Issue 中提供：
   - 详细的复现步骤
   - 预期行为 vs 实际行为
   - 环境信息（操作系统、Python 版本、QuickBot 版本）
   - 错误日志或截图
   - 相关配置（脱敏后）

### 功能请求

如果你想添加新功能：

1. 先在 [Discussions](https://github.com/Chang-Augenweide/QuickBot/discussions) 中讨论
2. 确认功能符合项目目标
3. 创建 Issue 描述功能需求和用例
4. 等待维护者反馈

---

## 🔄 开发流程

### 1. Fork 项目

1. 点击 GitHub 页面右上角的 "Fork" 按钮
2. 克隆你的 fork 仓库到本地：
   ```bash
   git clone https://github.com/YOUR_USERNAME/QuickBot.git
   cd QuickBot
   ```

### 2. 设置上游仓库

```bash
git remote add upstream https://github.com/Chang-Augenweide/QuickBot.git
```

### 3. 创建特性分支

```bash
git checkout -b feature/your-feature-name
# 或者
git checkout -b fix/your-bug-fix
```

分支命名约定：
- `feature/xxx` - 新功能
- `fix/xxx` - bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

### 4. 开发和测试

- 进行代码开发
- 确保代码遵循规范（见下文）
- 编写测试用例
- 运行测试验证功能

### 5. 提交更改

详见 [提交规范](#提交规范)

### 6. 推送到你的fork

```bash
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 访问你的 fork 仓库页面
2. 点击 "New Pull Request"
3. 选择你的特性分支
4. 填写 PR 描述：
   - 清晰的标题
   - 描述所做的更改
   - 关联相关的 Issue
   - 添加截图或演示（如果适用）

### 8. 代码审查和修改

维护者可能会要求你：
- 修改代码
- 添加测试
- 更新文档
- 回答问题

请友好地配合这些要求。

---

## 📐 代码规范

### Python 代码

遵循 [PEP 8](https://pep8.org/) 风格指南：

- 使用 4 空格缩进
- 行长度不超过 79 字符
- 使用有意义的变量名和函数名
- 添加文档字符串
- 导入顺序：标准库 → 第三方库 → 本地导入

示例：
```python
"""QuickBot 模块文档字符串."""

import os
import sys
from typing import Dict, List, Optional

import requests

from internal.config import Config


def process_message(message: str) -> Dict:
    """
    处理消息的函数.

    Args:
        message: 输入消息

    Returns:
        处理后的结果字典
    """
    # 实现代码
    pass
```

### Go 代码

遵循 [Effective Go](https://go.dev/doc/effective_go) 和 Go 社区约定：

- 使用 `gofmt` 格式化代码
- 导出标识符使用 PascalCase，非导出使用 camelCase
- 错误处理不应被忽略
- 添加必要的注释

示例：
```go
// Package internal implements core QuickBot functionality.
package internal

import (
    "context"
    "log"
)

// Message represents a chat message.
type Message struct {
    ID      string
    Content string
    Time    time.Time
}

// ProcessMessage processes an incoming message.
func ProcessMessage(ctx context.Context, msg *Message) error {
    log.Printf("Processing message: %s", msg.ID)
    // 实现代码
    return nil
}
```

---

## 📝 提交规范

使用清晰的提交信息格式：

```
<类型>(<范围>): <描述>

[可选的详细描述]

[可选的关联 Issue]
```

### 类型

- `feat`: 新功能
- `fix`: bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

### 示例

```
feat(ai): 支持新的 AI 提供商接口

添加了新的 AI provider 抽象接口，支持更多的 AI 服务提供商。

Closes #123
```

```
fix(memory): 修复内存泄漏问题

修复了内存管理模块中的一个内存泄漏问题，该问题导致长时间运行后内存占用过高。

Fixes #456
```

```
docs(README): 更新安装说明

更新了 README 中的快速开始部分，添加了依赖安装的详细步骤。
```

---

## 🧪 测试指南

### 运行测试

```bash
# Python 测试
python -m pytest tests/ -v

# Go 测试
go test ./...

# 运行所有测试
make test
```

### 编写测试

为你的新代码编写测试：

**Python 测试：**
```python
import pytest

from internal.memory import Memory


def test_memory_creation():
    """测试内存创建."""
    memory = Memory(db_path=":memory:")
    assert memory is not None


def test_add_message():
    """测试添加消息."""
    memory = Memory(db_path=":memory:")
    session_id = "test_session"
    memory.create_session(session_id=session_id)

    memory.add_message(
        session_id=session_id,
        role="user",
        content="Hello"
    )

    messages = memory.get_messages(session_id, limit=10)
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello"
```

**Go 测试：**
```go
package memory

import "testing"

func TestMemoryCreation(t *testing.T) {
    mem := NewMemory(":memory:")
    if mem == nil {
        t.Fatal("Failed to create memory")
    }
}

func TestAddMessage(t *testing.T) {
    mem := NewMemory(":memory:")
    sessionID := "test_session"

    mem.CreateSession(sessionID, "test_platform", "test_user", nil)
    mem.AddMessage(sessionID, "user", "Hello", nil)

    msgs := mem.GetMessages(sessionID, 10)
    if len(msgs) != 1 {
        t.Errorf("Expected 1 message, got %d", len(msgs))
    }
}
```

---

## 📚 文档贡献

文档是项目的重要组成部分，欢迎改进文档！

### 可以改进的文档

- README.md - 主要文档
- docs/README.md - 详细文档
- docs/DEPLOYMENT.md - 部署指南
- docs/CHANGELOG.md - 更新日志
- 代码注释

### 文档规范

- 使用清晰的语言
- 提供代码示例
- 保持文档更新
- 遵循项目的文档格式

### 文档 PR 流程

与代码 PR 相同：
1. Fork 项目
2. 创建 `docs/xxx` 分支
3. 修改文档
4. 提交更改
5. 创建 Pull Request

---

## 🔧 开发环境设置

### Python 环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Go 环境

```bash
# 下载依赖
go mod download

# 安装开发工具
go install golang.org/x/tools/cmd/goimports@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

---

## 💬 获取帮助

如果你在贡献过程中遇到问题：

1. 查阅 [现有文档](https://github.com/Chang-Augenweide/QuickBot/tree/main/docs)
2. 搜索 [Issues](https://github.com/Chang-Augenweide/QuickBot/issues)
3. 在 [Discussions](https://github.com/Chang-Augenweide/QuickBot/discussions) 中提问
4. 加入我们的 [Discord 社区](https://discord.com/invite/clawd)

---

## 🏆 贡献者

感谢所有贡献者的辛勤付出！

<!-- 贡献者列表会自动更新 -->

---

再次感谢你的贡献！🙏
