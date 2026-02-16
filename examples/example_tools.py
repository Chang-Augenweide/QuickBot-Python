"""
QuickBot - Example Custom Tool
Shows how to create custom tools for QuickBot.
"""
import asyncio
from tools import Tool


class WeatherTool(Tool):
    """Weather information tool (example)."""
    
    def __init__(self, api_key: str = ""):
        super().__init__(
            name="weather",
            description="Get weather information for a location",
            permission=ToolPermission.ALLOW_WHITELIST
        )
        self.api_key = api_key
    
    async def execute(self, location: str = "") -> str:
        """Get weather for location."""
        if not location:
            return "Error: Please provide a location"
        
        # This is a placeholder - you would call a real weather API here
        # For example: OpenWeatherMap, WeatherAPI, etc.
        
        # Simulated response
        return f"Weather for {location}:\n🌤️ Partly Cloudy\n🌡️ 22°C\n💧 45% humidity\n🌬️ Light breeze"


class CalculatorTool(Tool):
    """Calculator tool."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic and advanced calculations",
            permission=ToolPermission.ALLOW_ALL
        )
    
    async def execute(self, expression: str) -> str:
        """Calculate expression."""
        try:
            # Safe evaluation of mathematical expressions
            allowed_names = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'sqrt': lambda x: x ** 0.5,
            }
            
            # Basic math operators are allowed
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return f"Result: {result}"
        
        except Exception as e:
            return f"Error: Invalid expression - {str(e)}"


# Example of how to register custom tools
def register_custom_tools(tool_registry):
    """Register custom tools with the tool registry."""
    
    # Weather tool (requires API key in production)
    # tool_registry.register(WeatherTool(api_key="your-api-key"))
    
    # Calculator tool
    tool_registry.register(CalculatorTool())


# When your custom tool file is imported, QuickBot can automatically load it
# by adding it to the config or by importing it in your initialization code.
