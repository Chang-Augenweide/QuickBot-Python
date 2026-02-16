# QuickBot Documentation

## Overview

QuickBot is a lightweight, efficient personal AI assistant framework written in Python 3, designed to be simple, modular, and extensible.

## Architecture

QuickBot is built around several core components:

- **Agent**: Main agent logic for processing messages and coordinating components
- **Memory**: Long-term conversation memory with semantic search
- **AI Providers**: Pluggable AI model integrations (OpenAI, Anthropic, Ollama)
- **Scheduler**: Cron-like task scheduling for reminders and automation
- **Tools**: Extensible system for executing safe operations
- **Platforms**: Multi-platform support (Telegram, Discord, Slack, etc.)

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create configuration:

```bash
python main.py --init
```

4. Edit `config.yaml` with your API keys and settings

5. Run the bot:

```bash
python main.py
```

## Configuration

See `config.example.yaml` for all available options.

### AI Providers

**OpenAI:**
```yaml
ai:
  provider: "openai"
  api_key: "sk-..."
  model: "gpt-4o"
```

**Anthropic (Claude):**
```yaml
ai:
  provider: "anthropic"
  api_key: "sk-ant-..."
  model: "claude-3-5-sonnet-20241022"
```

**Local Ollama:**
```yaml
ai:
  provider: "ollama"
  model: "llama3.2"
```

### Platform Setup

**Telegram:**
1. Create a bot via @BotFather
2. Get the token
3. Add to config.yaml
4. Start the bot

## Commands

- `/help` - Show help message
- `/status` - Show system status
- `/remind HH:MM message` - Set a reminder
- `/memory set|get key [value]` - Store/retrieve information
- `/tasks` - List scheduled tasks

## Memory Management

QuickBot automatically manages conversation memory:

- Short-term: Recent messages in SQLite database
- Long-term: Important information stored with semantic search
- Automatic pruning: Old messages are removed when over limit

## Creating Custom Tools

See `example_tools.py` for examples. Basic structure:

```python
from tools import Tool, ToolPermission

class MyTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Does something useful",
            permission=ToolPermission.ALLOW_WHITELIST
        )
    
    async def execute(self, **kwargs) -> str:
        # Tool logic here
        return "Result"
```

## Scheduler Tasks

Reminders:
```python
scheduler.add_reminder(
    session_id="user123",
    message="Check emails",
    remind_at="09:00"
)
```

Recurring tasks:
```python
scheduler.add_recurring_task(
    session_id="user123",
    name="Daily report",
    interval_minutes=1440,
    payload={"type": "message", "text": "Daily report time!"}
)
```

## Platform Development

To add a new platform, create a class with the following methods:

```python
class MyPlatform:
    def __init__(self, bot, token, **kwargs):
        self.bot = bot
        self.token = token
    
    async def start(self):
        # Initialize platform
        pass
    
    async def stop(self):
        # Cleanup
        pass
    
    async def send_message(self, session_id, message):
        # Send message to platform
        pass
```

## Development

Running with debug mode:
```yaml
bot:
  debug: true
```

This enables shell tool and additional logging.

## License

MIT
