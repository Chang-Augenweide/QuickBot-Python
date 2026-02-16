"""
QuickBot - Tool System
Allows the AI to execute external tools and commands safely.
"""
import os
import subprocess
import json
import logging
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class ToolPermission(Enum):
    """Tool permission levels."""
    ALLOW_ALL = "allow_all"
    ALLOW_WHITELIST = "allow_whitelist"
    DENY_ALL = "deny_all"


class Tool:
    """Base class for tools."""
    
    def __init__(self, name: str, description: str, permission: ToolPermission = ToolPermission.ALLOW_WHITELIST):
        self.name = name
        self.description = description
        self.permission = permission
    
    async def execute(self, **kwargs) -> str:
        """Execute the tool."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for AI."""
        return {
            'name': self.name,
            'description': self.description,
            'permission': self.permission.value
        }


class ShellTool(Tool):
    """Execute shell commands safely."""
    
    def __init__(self, allowed_commands: Optional[List[str]] = None):
        super().__init__(
            name="shell",
            description="Execute shell commands (allowed: " + (", ".join(allowed_commands) if allowed_commands else "none") + ")",
            permission=ToolPermission.ALLOW_WHITELIST
        )
        self.allowed_commands = allowed_commands or []
    
    async def execute(self, command: str, timeout: int = 30) -> str:
        """Execute shell command."""
        if not command.strip():
            return "Error: Empty command"
        
        # Check if command is allowed
        if self.allowed_commands:
            cmd_parts = command.split()
            base_cmd = cmd_parts[0]
            if base_cmd not in self.allowed_commands:
                return f"Error: Command '{base_cmd}' is not allowed"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                return f"Command failed (exit {result.returncode}):\n{result.stderr}"
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"


class FileTool(Tool):
    """File operations tool."""
    
    def __init__(self, base_dir: str = "."):
        super().__init__(
            name="file",
            description="Read, write, and list files",
            permission=ToolPermission.ALLOW_WHITELIST
        )
        self.base_dir = Path(base_dir).resolve()
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve and validate path."""
        resolved = (self.base_dir / path).resolve()
        
        # Ensure path is within base directory
        try:
            resolved.relative_to(self.base_dir)
        except ValueError:
            raise PermissionError(f"Access denied: {path}")
        
        return resolved
    
    async def execute(self, operation: str, path: str, content: Optional[str] = None) -> str:
        """Execute file operation."""
        try:
            resolved_path = self._resolve_path(path)
            
            if operation == "read":
                if not resolved_path.exists():
                    return f"Error: File not found: {path}"
                return resolved_path.read_text(encoding='utf-8')
            
            elif operation == "write":
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                resolved_path.write_text(content or "", encoding='utf-8')
                return f"Success: Written to {path}"
            
            elif operation == "list":
                if not resolved_path.exists():
                    return f"Error: Path not found: {path}"
                
                if resolved_path.is_file():
                    items = [str(resolved_path.name)]
                else:
                    items = sorted([
                        p.name + ("/" if p.is_dir() else "")
                        for p in resolved_path.iterdir()
                    ])
                return "\n".join(items) if items else "(empty)"
            
            elif operation == "delete":
                if not resolved_path.exists():
                    return f"Error: File not found: {path}"
                
                if resolved_path.is_dir():
                    import shutil
                    shutil.rmtree(resolved_path)
                else:
                    resolved_path.unlink()
                
                return f"Success: Deleted {path}"
            
            else:
                return f"Error: Unknown operation '{operation}'"
        
        except PermissionError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema with operations."""
        schema = super().get_schema()
        schema['operations'] = ['read', 'write', 'list', 'delete']
        return schema


class MemoryTool(Tool):
    """Memory operations tool."""
    
    def __init__(self, memory):
        super().__init__(
            name="memory",
            description="Store and retrieve long-term information",
            permission=ToolPermission.ALLOW_ALL
        )
        self.memory = memory
    
    async def execute(self, operation: str, key: Optional[str] = None, value: Optional[str] = None) -> str:
        """Execute memory operation."""
        try:
            if operation == "set" and key and value:
                self.memory.set_long_term(key, value, importance=2)
                return f"Success: Remembered '{key}'"
            
            elif operation == "get" and key:
                stored = self.memory.get_long_term(key)
                return stored if stored else f"Info: No memory for '{key}'"
            
            elif operation == "search":
                results = self.memory.search_long_term(key or "", limit=10)
                if not results:
                    return "Info: No memories found"
                
                return "\n".join([
                    f"- {r['key']}: {r['value'][:100]}..."
                    for r in results
                ])
            
            else:
                return "Error: Invalid operation. Use: set/get/search"
        
        except Exception as e:
            return f"Error: {str(e)}"


class WebSearchTool(Tool):
    """Web search tool."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="web_search",
            description="Search the web for information",
            permission=ToolPermission.ALLOW_WHITELIST
        )
        self.api_key = api_key  # Could be for Google, Bing, Brave, etc.
    
    async def execute(self, query: str, num_results: int = 5) -> str:
        """Execute web search."""
        # Placeholder - implement based on search API
        # For now, return a message about needing API key
        if not self.api_key:
            return "Info: Web search requires an API key (configure in settings)"
        
        # This would call the actual search API
        return f"Search results for '{query}' (requires API implementation)"


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.permission = ToolPermission.ALLOW_WHITELIST
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_all(self) -> Dict[str, Tool]:
        """Get all tools."""
        return self.tools.copy()
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all available tools."""
        return [
            tool.get_schema()
            for tool in self.tools.values()
            if tool.permission != ToolPermission.DENY_ALL
        ]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool."""
        tool = self.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"
        
        if tool.permission == ToolPermission.DENY_ALL:
            return f"Error: Tool '{tool_name}' is disabled"
        
        if self.permission == ToolPermission.DENY_ALL:
            return "Error: All tools are disabled"
        
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    def set_permission(self, permission: ToolPermission) -> None:
        """Set global permission level."""
        self.permission = permission
        logger.info(f"Tool permission set to: {permission.value}")


async def execute_code_safely(code: str, allowed_imports: Optional[List[str]] = None) -> str:
    """Safely execute Python code."""
    allowed_imports = allowed_imports or []
    
    try:
        # Parse and analyze code
        tree = ast.parse(code)
        
        # Check for dangerous operations
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in allowed_imports:
                        return f"Error: Import '{alias.name}' is not allowed"
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module not in allowed_imports:
                    return f"Error: Import from '{node.module}' is not allowed"
        
        # Execute in restricted environment
        result = {}
        exec(code, {'__builtins__': {}}, result)
        
        # Return result
        output = []
        for key, value in result.items():
            if not key.startswith('_'):
                output.append(f"{key} = {value}")
        
        return "\n".join(output) if output else "Code executed successfully (no output)"
    
    except SyntaxError as e:
        return f"Syntax Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
