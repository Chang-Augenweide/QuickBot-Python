"""
QuickBot - Core Agent
Main agent logic for processing messages and coordinating components.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime

from config import Config
from ai_providers import get_provider, AIProvider
from memory import Memory
from scheduler import Scheduler
from tools import ToolRegistry, ShellTool, FileTool, MemoryTool

logger = logging.getLogger(__name__)


class QuickBot:
    """Main QuickBot agent."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = Config(config_path)
        self.memory = None
        self.ai_provider: Optional[AIProvider] = None
        self.scheduler: Optional[Scheduler] = None
        self.tool_registry: Optional[ToolRegistry] = None
        self._running = False
        
        self._setup_logging()
        self._init_components()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get('logging.file', 'quickbot.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger.info(f"QuickBot initialized")
        logger.info(f"Debug mode: {self.config.get('bot.debug', False)}")
    
    def _init_components(self) -> None:
        """Initialize all components."""
        # Memory
        if self.config.get('memory.enabled', True):
            self.memory = Memory(
                db_path=self.config.get('memory.storage', 'memory.db'),
                max_messages=self.config.get('memory.max_messages', 1000)
            )
            logger.info("Memory component initialized")
        
        # AI Provider
        ai_config = self.config.get('ai', {})
        provider_type = ai_config.get('provider', 'openai')
        api_key = ai_config.get('api_key', '')
        model = ai_config.get('model', 'gpt-4o')
        
        if api_key or provider_type == 'ollama':
            self.ai_provider = get_provider(
                provider_type=provider_type,
                api_key=api_key,
                model=model,
                max_tokens=ai_config.get('max_tokens', 2000),
                temperature=ai_config.get('temperature', 0.7),
                base_url=ai_config.get('base_url', '')
            )
            logger.info(f"AI provider initialized: {provider_type} ({model})")
        else:
            logger.warning("No AI API key configured")
        
        # Scheduler
        if self.config.get('scheduler.enabled', True):
            self.scheduler = Scheduler(
                db_path=self.config.get('scheduler.storage', 'scheduler.db')
            )
            
            # Set up task handler
            async def task_handler(task):
                await self._handle_scheduled_task(task)
            
            self.scheduler.set_task_handler(task_handler)
            logger.info("Scheduler component initialized")
        
        # Tool Registry
        if self.config.get('tools.enabled', True):
            self.tool_registry = ToolRegistry()
            self._register_default_tools()
            logger.info("Tool registry initialized")
    
    def _register_default_tools(self) -> None:
        """Register default tools."""
        if not self.tool_registry:
            return
        
        # File tool
        if self.memory:
            base_dir = self.config.get('tools.directory', '.')
            if base_dir:
                self.tool_registry.register(FileTool(base_dir=base_dir))
        
        # Memory tool
        if self.memory:
            self.tool_registry.register(MemoryTool(self.memory))
        
        # Shell tool (only if debug mode)
        if self.config.get('bot.debug', False):
            allowed_commands = ['ls', 'pwd', 'cat', 'echo', 'date']
            self.tool_registry.register(ShellTool(allowed_commands=allowed_commands))
    
    async def _handle_scheduled_task(self, task) -> None:
        """Handle a scheduled task."""
        logger.info(f"Executing scheduled task: {task.name}")
        
        # Handle different task types
        payload = task.payload
        
        if payload.get('type') == 'reminder':
            # Send reminder message
            if task.session_id and 'message' in payload:
                await self.send_message(
                    session_id=task.session_id,
                    message=f"⏰ Reminder: {payload['message']}"
                )
        
        # Additional task types can be added here
        elif payload.get('type') == 'message':
            if task.session_id:
                await self.send_message(
                    session_id=task.session_id,
                    message=payload.get('text', '')
                )
        
        elif payload.get('type') == 'system_event':
            # Handle system events
            await self._handle_system_event(payload)
    
    async def _handle_system_event(self, payload: Dict[str, Any]) -> None:
        """Handle system events."""
        event_type = payload.get('event_type')
        
        if event_type == 'heartbeat':
            # Heartbeat task - check for reminders, etc.
            logger.debug("Heartbeat received")
        
        elif event_type == 'backup':
            # Backup task
            logger.info("Running backup...")
            # Implement backup logic
    
    async def send_message(self, session_id: str, message: str, **kwargs) -> None:
        """Send a message to a platform. Override in platform integrations."""
        # This is a placeholder - actual sending is handled by platform modules
        logger.info(f"[{session_id}] Sending: {message[:50]}...")
    
    async def process_message(
        self,
        session_id: str,
        message: str,
        platform: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process an incoming message."""
        logger.info(f"[{session_id}] Received from {platform}: {message[:50]}...")
        
        metadata = metadata or {}
        
        # Check for special commands
        if message.startswith('/'):
            return await self._handle_command(
                session_id, message, platform, user_id, metadata
            )
        
        # Store user message in memory
        if self.memory:
            self.memory.create_session(
                session_id=session_id,
                platform=platform,
                user_id=user_id,
                metadata=metadata
            )
            self.memory.add_message(
                session_id=session_id,
                role='user',
                content=message,
                metadata=metadata
            )
        
        # Get conversation context
        context = []
        system_prompt = self._get_system_prompt()
        
        if system_prompt:
            context.append({'role': 'system', 'content': system_prompt})
        
        if self.memory:
            memory_context = self.memory.get_context(
                session_id=session_id,
                limit=self.config.get('memory.max_messages', 100) // 2
            )
            context.extend(memory_context)
        
        # Add available tools to system prompt
        if self.tool_registry and self.tool_registry.get_all():
            tools_info = self._get_tools_info()
            if tools_info:
                context[0]['content'] += f"\n\nAvailable tools:\n{tools_info}"
        
        # Call AI
        try:
            if not self.ai_provider:
                return "AI provider not configured. Please set an API key in the configuration."
            
            response = await self.ai_provider.chat(
                messages=context,
                max_tokens=self.config.get('ai.max_tokens', 2000),
                temperature=self.config.get('ai.temperature', 0.7)
            )
            
            # Store AI response in memory
            if self.memory:
                self.memory.add_message(
                    session_id=session_id,
                    role='assistant',
                    content=response,
                    metadata={'platform': platform}
                )
            
            # Check if AI wants to use a tool
            if response.startswith('TOOL:'):
                return await self._handle_tool_call(session_id, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI."""
        bot_name = self.config.get('bot.name', 'QuickBot')

        prompt = f"""You are {bot_name}, a helpful AI assistant.

Your role is to assist users in a friendly and efficient manner.

Guidelines:
- Be concise, clear, and helpful
- Avoid filler phrases like "I'd be happy to help" or "Great question"
- Remember important information in long-term memory when asked
- If you need to use a tool, start with response with "TOOL: tool_name:parameters"
- The user prefers direct, actionable responses
- Be helpful but don't be overly verbose

Example:
User: "What's 2+2?"
You: "4" (not "I'd be happy to help you calculate that. 2+2 equals 4.")
"""

        # Add tools information if available
        if self.tool_registry and self.tool_registry.get_all():
            tools_info = self._get_tools_info()
            if tools_info:
                prompt += f"\n\nAvailable tools:\n{tools_info}\n"
            prompt += "\nTo use a tool, respond with: TOOL: tool_name:arg1=value1,arg2=value2"

        return prompt
    
    def _get_tools_info(self) -> str:
        """Get information about available tools."""
        if not self.tool_registry:
            return ""
        
        tools = self.tool_registry.get_all()
        info = []
        for tool in tools.values():
            schema = tool.get_schema()
            info.append(f"- {tool.name}: {schema['description']}")
        
        return "\n".join(info)
    
    async def _handle_tool_call(self, session_id: str, response: str) -> str:
        """Handle a tool call from AI."""
        try:
            # Parse: TOOL: tool_name:arg1=value1,arg2=value2
            parts = response[len('TOOL:'):].strip().split(':', 1)
            tool_name = parts[0].strip()
            
            kwargs = {}
            if len(parts) > 1:
                for arg in parts[1].split(','):
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        kwargs[key.strip()] = value.strip()
            
            if self.tool_registry:
                result = await self.tool_registry.execute_tool(tool_name, **kwargs)
                return result
            
            return "Tool system not available"
        
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            return f"Error executing tool: {str(e)}"
    
    async def _handle_command(
        self,
        session_id: str,
        command: str,
        platform: str,
        user_id: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Handle special commands."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == '/help':
            return self._get_help_message()
        
        elif cmd == '/status':
            return self._get_status_message()
        
        elif cmd == '/remind':
            # Usage: /remind HH:MM message
            if len(args) >= 2 and self.scheduler:
                time_str = args[0]
                message = ' '.join(args[1:])
                
                try:
                    task_id = self.scheduler.add_reminder(
                        session_id=session_id,
                        message=message,
                        remind_at=time_str
                    )
                    return f"✅ Reminder set for {time_str}: {message}"
                except ValueError as e:
                    return f"⚠️ Invalid time format: {str(e)}"
            else:
                return "Usage: /remind HH:MM message\nExample: /remind 09:00 Check emails"
        
        elif cmd == '/memory':
            if len(args) >= 2 and self.memory:
                action = args[0].lower()
                key = args[1]
                value = ' '.join(args[2:]) if len(args) > 2 else None
                
                if action == 'set' and value:
                    self.memory.set_long_term(key, value, importance=2)
                    return f"✅ Remembered: {key}"
                elif action == 'get':
                    stored = self.memory.get_long_term(key)
                    return stored if stored else f"ℹ️ No memory for '{key}'"
            else:
                return "Usage: /memory set|get key [value]"
        
        elif cmd == '/tasks':
            if self.scheduler:
                tasks = self.scheduler.get_tasks_for_session(session_id)
                if tasks:
                    task_list = "\n".join([
                        f"- {t.name} at {t.next_run.strftime('%H:%M')}"
                        for t in tasks
                    ])
                    return f"📋 Your tasks:\n{task_list}"
                else:
                    return "ℹ️ No scheduled tasks"
            else:
                return "Scheduler not available"
        
        else:
            return f"Unknown command: {cmd}. Use /help for available commands."
    
    def _get_help_message(self) -> str:
        """Get help message."""
        return f"""📖 {self.config.get('bot.name', 'QuickBot')} Commands:

/help - Show this help message
/status - Show system status
/remind HH:MM message - Set a reminder
/memory set|get key [value] - Store/retrieve information
/tasks - List your scheduled tasks

Just chat with me naturally! I can help with various tasks."""
    
    def _get_status_message(self) -> str:
        """Get status message."""
        status_parts = [
            f"🤖 {self.config.get('bot.name', 'QuickBot')} Status",
            f"📊 Messages in memory: {len(self.memory.get_messages('', limit=1000)) if self.memory else 0}",
            f"⏰ Scheduled tasks: {len(self.scheduler.get_all_tasks()) if self.scheduler else 0}",
            f"🔧 Available tools: {len(self.tool_registry.get_all()) if self.tool_registry else 0}",
            f"🧠 AI Provider: {self.config.get('ai.provider', 'None')}"
        ]
        
        return "\n".join(status_parts)
    
    async def start(self) -> None:
        """Start the bot."""
        if self._running:
            return
        
        self._running = True
        logger.info("QuickBot started")
        
        # Start scheduler
        if self.scheduler:
            asyncio.create_task(self.scheduler.start())
    
    async def stop(self) -> None:
        """Stop the bot."""
        self._running = False
        logger.info("QuickBot stopping...")
        
        # Stop scheduler
        if self.scheduler:
            await self.scheduler.stop()
        
        # Close memory
        if self.memory:
            self.memory.close()
        
        logger.info("QuickBot stopped")
    
    async def stream_response(
        self,
        session_id: str,
        message: str,
        platform: str,
        user_id: str
    ) -> AsyncIterator[str]:
        """Stream a response from the AI."""
        context = []
        system_prompt = self._get_system_prompt()
        
        if system_prompt:
            context.append({'role': 'system', 'content': system_prompt})
        
        if self.memory:
            memory_context = self.memory.get_context(
                session_id=session_id,
                limit=50
            )
            context.extend(memory_context)
        
        if self.ai_provider:
            async for chunk in self.ai_provider.chat_stream(
                messages=context,
                max_tokens=self.config.get('ai.max_tokens', 2000),
                temperature=self.config.get('ai.temperature', 0.7)
            ):
                yield chunk
        else:
            yield "AI provider not configured."
