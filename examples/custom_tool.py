"""
QuickBot 自定义工具示例

本文件展示如何创建和使用自定义工具来扩展 QuickBot 的功能。
"""

from typing import Dict, Any
from internal.tools.tools import ToolBase


class CalculatorTool(ToolBase):
    """计算器工具示例 - 支持基本数学运算"""

    def get_schema(self) -> Dict[str, Any]:
        """返回工具的 JSON Schema"""
        return {
            'name': 'calculator',
            'description': '执行基本数学运算（加、减、乘、除）',
            'parameters': {
                'type': 'object',
                'properties': {
                    'expression': {
                        'type': 'string',
                        'description': '数学表达式，例如: 2 + 3 * 4'
                    }
                },
                'required': ['expression']
            }
        }

    async def execute(self, expression: str) -> str:
        """
        执行计算

        Args:
            expression: 数学表达式

        Returns:
            计算结果字符串
        """
        try:
            # 简单的计算实现（注意：生产环境中应使用更安全的方式）
            result = eval(expression)
            return f"计算结果: {expression} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"


class WeatherTool(ToolBase):
    """天气查询工具示例"""

    def __init__(self, api_key: str = None):
        """
        初始化天气工具

        Args:
            api_key: 天气 API 密钥（可选）
        """
        self.api_key = api_key
        self.base_url = "https://api.weather.com/v1"

    def get_schema(self) -> Dict[str, Any]:
        """返回工具的 JSON Schema"""
        return {
            'name': 'weather',
            'description': '查询指定城市的天气预报',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {
                        'type': 'string',
                        'description': '城市名称，例如: 北京, 上海, 广州'
                    },
                    'days': {
                        'type': 'integer',
                        'description': '预报天数 (1-7)',
                        'default': 1
                    }
                },
                'required': ['city']
            }
        }

    async def execute(self, city: str, days: int = 1) -> str:
        """
        查询天气

        Args:
            city: 城市名称
            days: 预报天数

        Returns:
            天气信息字符串
        """
        # 这里应该是实际的 API 调用
        # 示例实现
        if not self.api_key:
            return f"天气查询需要 API 密钥。当前配置未提供密钥。"

        # 模拟返回
        return f"""
🌤️ {city}天气预报：

今天: 晴转多云，气温 20-28°C
明天: 小雨，气温 18-25°C
后天: 晴转阴，气温 19-27°C

提示：出门记得带伞！
"""


class TranslationTool(ToolBase):
    """翻译工具示例"""

    def __init__(self, source_lang: str = 'auto', target_lang: str = 'zh'):
        """
        初始化翻译工具

        Args:
            source_lang: 源语言代码
            target_lang: 目标语言代码
        """
        self.source_lang = source_lang
        self.target_lang = target_lang

    def get_schema(self) -> Dict[str, Any]:
        """返回工具的 JSON Schema"""
        return {
            'name': 'translate',
            'description': f'翻译文本（默认: {self.source_lang} → {self.target_lang}）',
            'parameters': {
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': '需要翻译的文本'
                    }
                },
                'required': ['text']
            }
        }

    async def execute(self, text: str) -> str:
        """
        执行翻译

        Args:
            text: 需要翻译的文本

        Returns:
            翻译结果
        """
        # 这里应该是实际的翻译 API 调用
        # 示例实现
        return f"翻译结果（{self.target_lang}）: {text}"


class UrlSummarizerTool(ToolBase):
    """URL 摘要工具示例"""

    def get_schema(self) -> Dict[str, Any]:
        """返回工具的 JSON Schema"""
        return {
            'name': 'url_summarizer',
            'description': '获取并总结网页内容',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': '网页 URL'
                    }
                },
                'required': ['url']
            }
        }

    async def execute(self, url: str) -> str:
        """
        获取并总结网页内容

        Args:
            url: 网页 URL

        Returns:
            网页摘要
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题和主要文本
            title = soup.title.string if soup.title else "无标题"
            paragraphs = [p.get_text() for p in soup.find_all('p')]

            # 简单摘要（取前几段）
            summary = '\n'.join(paragraphs[:3])

            return f"""
📄 网页摘要
标题: {title}
链接: {url}

内容概述:
{summary[:500]}...
"""
        except Exception as e:
            return f"获取网页内容失败: {str(e)}"


class NoteTakingTool(ToolBase):
    """笔记工具示例 - 存储和检索笔记"""

    def __init__(self, storage_file: str = "notes.json"):
        """
        初始化笔记工具

        Args:
            storage_file: 笔记存储文件
        """
        self.storage_file = storage_file
        self.notes = {}
        self._load_notes()

    def _load_notes(self) -> None:
        """加载笔记"""
        try:
            import json
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
        except FileNotFoundError:
            self.notes = {}

    def _save_notes(self) -> None:
        """保存笔记"""
        import json
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def get_schema(self) -> Dict[str, Any]:
        """返回工具的 JSON Schema"""
        return {
            'name': 'note',
            'description': '管理笔记（添加、获取、删除）',
            'parameters': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'description': '操作类型: add, get, delete, list',
                        'enum': ['add', 'get', 'delete', 'list']
                    },
                    'key': {
                        'type': 'string',
                        'description': '笔记键名（用于 get, delete）'
                    },
                    'content': {
                        'type': 'string',
                        'description': '笔记内容（用于 add）'
                    }
                },
                'required': ['action']
            }
        }

    async def execute(self, action: str, key: str = None, content: str = None) -> str:
        """
        执行笔记操作

        Args:
            action: 操作类型
            key: 键名
            content: 内容

        Returns:
            操作结果
        """
        if action == 'add':
            if not key:
                return "错误: 添加笔记需要提供键名（key 参数）"
            if not content:
                return "错误: 添加笔记需要提供内容（content 参数）"

            self.notes[key] = {
                'content': content,
                'created_at': str(pd.Timestamp.now()) if 'pd' in globals() else 'unknown'
            }
            self._save_notes()
            return f"✅ 笔记已保存: {key}"

        elif action == 'get':
            if not key:
                return "错误: 获取笔记需要提供键名（key 参数）"

            if key not in self.notes:
                return f"ℹ️ 未找到笔记: {key}"

            note = self.notes[key]
            return f"""📝 {key}
{note['content']}
创建时间: {note.get('created_at', 'unknown')}"""

        elif action == 'delete':
            if not key:
                return "错误: 删除笔记需要提供键名（key 参数）"

            if key not in self.notes:
                return f"ℹ️ 未找到笔记: {key}"

            del self.notes[key]
            self._save_notes()
            return f"🗑️ 笔记已删除: {key}"

        elif action == 'list':
            if not self.notes:
                return "📋 暂无笔记"

            note_list = '\n'.join([f"- {key}" for key in self.notes.keys()])
            return f"📋 笔记列表:\n{note_list}"

        else:
            return f"❌ 未知操作: {action}"


# ================================
# 如何在 QuickBot 中使用自定义工具
# ================================

"""
在你的 agent.py 或初始化代码中注册自定义工具:

from examples.custom_tool import (
    CalculatorTool,
    WeatherTool,
    TranslationTool,
    UrlSummarizerTool,
    NoteTakingTool
)

# 创建工具实例
calculator = CalculatorTool()
weather = WeatherTool(api_key="your_weather_api_key")
translator = TranslationTool(source_lang='en', target_lang='zh')
summarizer = UrlSummarizerTool()
note_taker = NoteTakingTool(storage_file="notes.json")

# 注册工具到工具注册表
if self.tool_registry:
    self.tool_registry.register(calculator)
    self.tool_registry.register(weather)
    self.tool_registry.register(translator)
    self.tool_registry.register(summarizer)
    self.tool_registry.register(note_taker)

# 现在你可以通过 AI 使用这些工具了！
# 例如，用户问 "计算 2 + 3 * 4"，AI 会调用 calculator 工具
# 用户问 "北京今天天气怎么样"，AI 会调用 weather 工具
# 用户说 "帮我记住会议时间"，AI 会调用 note_taker 工具
"""

if __name__ == '__main__':
    """测试自定义工具"""

    import asyncio

    async def test_tools():
        """测试所有自定义工具"""

        print("🧪 测试自定义工具\n")
        print("=" * 50)

        # 测试计算器
        print("\n📊 测试计算器工具:")
        calc = CalculatorTool()
        result = await calc.execute(expression="2 + 3 * 4")
        print(f"结果: {result}")

        # 测试天气（无 API 密钥）
        print("\n🌤️ 测试天气工具:")
        weather = WeatherTool()
        result = await weather.execute(city="北京", days=3)
        print(f"结果: \n{result}")

        # 测试翻译
        print("\n🌐 测试翻译工具:")
        translator = TranslationTool()
        result = await translator.execute(text="Hello, World!")
        print(f"结果: {result}")

        # 测试 URL 摘要
        print("\n📄 测试 URL 摘要工具:")
        summarizer = UrlSummarizerTool()
        result = await summarizer.execute(url="https://example.com")
        print(f"结果: \n{result[:200]}...")

        # 测试笔记工具
        print("\n📝 测试笔记工具:")
        note_taker = NoteTakingTool()

        result = await note_taker.execute(action="add", key="会议", content="下午3点，会议室A")
        print(f"结果: {result}")

        result = await note_taker.execute(action="get", key="会议")
        print(f"结果: \n{result}")

        result = await note_taker.execute(action="list")
        print(f"结果: \n{result}")

        # 清理
        result = await note_taker.execute(action="delete", key="会议")
        print(f"结果: {result}")

        print("\n" + "=" * 50)
        print("✅ 所有工具测试完成！")

    asyncio.run(test_tools())
