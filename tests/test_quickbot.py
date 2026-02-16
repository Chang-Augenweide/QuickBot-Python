#!/usr/bin/python3
"""
QuickBot Test Suite

Tests all QuickBot modules:
- Configuration
- Memory
- Scheduler
- Tools
- Agent
- Platform adapters

Run: python test_quickbot.py
"""

import unittest
import os
import sys

# Add QuickBot directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""

    def test_config_load(self):
        """Test configuration loading"""
        from config import Config

        config = Config('config.yaml')
        self.assertIsNotNone(config)
        self.assertEqual(config.get('bot.name', 'QuickBot'), 'QuickBot')

    def test_config_set(self):
        """Test configuration setting"""
        from config import Config

        config = Config('config.yaml')
        config.set('bot.debug', True)
        self.assertTrue(config.get('bot.debug', False))


class TestMemory(unittest.TestCase):
    """Test memory management"""

    def setUp(self):
        """Setup test database"""
        from memory import Memory

        self.test_db = 'test_memory_temp.db'
        self.memory = Memory(self.test_db, max_messages=100)

    def tearDown(self):
        """Cleanup test database"""
        self.memory.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_session_creation(self):
        """Test session creation"""
        session_id = self.memory.create_session('test_user', 'telegram', 'user123')
        self.assertIsNotNone(session_id)

    def test_message_storage(self):
        """Test message storage"""
        session_id = self.memory.create_session('test_user', 'telegram', 'user123')
        msg_id = self.memory.add_message(session_id, 'user', 'Hello!')
        self.assertIsNotNone(msg_id)

    def test_message_retrieval(self):
        """Test message retrieval"""
        session_id = self.memory.create_session('test_user', 'telegram', 'user123')
        self.memory.add_message(session_id, 'user', 'Hello!')
        self.memory.add_message(session_id, 'assistant', 'Hi!')

        messages = self.memory.get_messages(session_id, limit=10)
        self.assertEqual(len(messages), 2)

    def test_long_term_memory(self):
        """Test long-term memory"""
        self.memory.set_long_term('test_key', 'test_value', importance=2)
        value = self.memory.get_long_term('test_key')
        self.assertEqual(value, 'test_value')

    def test_context_generation(self):
        """Test context generation"""
        session_id = self.memory.create_session('test_user', 'telegram', 'user123')
        self.memory.add_message(session_id, 'user', 'Hello!')
        self.memory.add_message(session_id, 'assistant', 'Hi!')

        context = self.memory.get_context(session_id)
        self.assertIn('Hello!', context)
        self.assertIn('Hi!', context)


class TestScheduler(unittest.TestCase):
    """Test task scheduler"""

    def setUp(self):
        """Setup test database"""
        from scheduler import Scheduler

        self.test_db = 'test_scheduler_temp.db'
        self.scheduler = Scheduler(self.test_db)

    def tearDown(self):
        """Cleanup test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_task_creation(self):
        """Test task creation"""
        task_id = self.scheduler.add_task(
            name='Test Task',
            schedule_type='interval',
            schedule_value='1h',
            payload={'type': 'test'},
            session_id='test_session'
        )
        self.assertIsNotNone(task_id)

    def test_task_retrieval(self):
        """Test task retrieval"""
        task_id = self.scheduler.add_task(
            name='Test Task 2',
            schedule_type='interval',
            schedule_value='30m',
            payload={'type': 'test2'},
            session_id='test_session'
        )
        task = self.scheduler.get_task(task_id)
        self.assertEqual(task.name, 'Test Task 2')

    def test_reminder_creation(self):
        """Test reminder creation"""
        reminder_id = self.scheduler.add_reminder(
            session_id='user123',
            message='Test reminder',
            remind_at='test_time'
        )
        self.assertIsNotNone(reminder_id)

    def test_task_removal(self):
        """Test task removal"""
        task_id = self.scheduler.add_task(
            name='Task to Remove',
            schedule_type='interval',
            schedule_value='1h',
            payload={'type': 'test'},
            session_id='test_session'
        )
        result = self.scheduler.remove_task(task_id)
        self.assertTrue(result)


class TestTools(unittest.TestCase):
    """Test tool system"""

    def setUp(self):
        """Setup tool registry"""
        from tools import ToolRegistry

        self.registry = ToolRegistry()

    def test_tool_registration(self):
        """Test tool registration"""
        # Mock tool
        class MockTool:
            def __init__(self):
                self.name = 'mock_tool'
                self.description = 'Mock tool'

            def execute(self, args):
                return 'success'

        tool = MockTool()
        self.registry.register(tool)
        self.registry.register(tool)
        retrieved = self.registry.get('mock_tool')
        self.assertIsNotNone(retrieved)

    def test_tool_execution(self):
        """Test tool execution"""
        from tools import FileTool, ShellTool

        temp_dir = os.path.join(os.path.dirname(__file__), 'test_temp')
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Test file tool
            file_tool = FileTool(base_dir=temp_dir)
            result = file_tool.execute('write', {
                'path': 'test.txt',
                'content': 'Hello QuickBot!'
            })
            self.assertIn('success', result.lower())

            # Test shell tool
            shell_tool = ShellTool(allowed_commands=['echo'])
            result = shell_tool.execute({
                'command': 'echo "test"'
            })
            self.assertIn('test', result)
        finally:
            # Cleanup
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


class TestAIProviders(unittest.TestCase):
    """Test AI providers"""

    def test_openai_provider_init(self):
        """Test OpenAI provider initialization"""
        from ai_providers import OpenAIProvider

        provider = OpenAIProvider(
            api_key='test_key',
            base_url='https://api.openai.com/v1',
            model='gpt-4o'
        )
        self.assertEqual(provider.provider_name, 'openai')
        self.assertEqual(provider.model, 'gpt-4o')

    def test_anthropic_provider_init(self):
        """Test Anthropic provider initialization"""
        from ai_providers import AnthropicProvider

        provider = AnthropicProvider(
            api_key='test_key',
            model='claude-3-sonnet'
        )
        self.assertEqual(provider.provider_name, 'anthropic')
        self.assertEqual(provider.model, 'claude-3-sonnet')


class TestAgent(unittest.TestCase):
    """Test main agent"""

    def setUp(self):
        """Setup test environment"""
        from agent import Agent
        from config import Config
        from memory import Memory
        from scheduler import Scheduler

        self.test_memory_db = 'test_agent_memory.db'
        self.test_scheduler_db = 'test_agent_scheduler.db'

        config = Config('config.yaml')
        memory = Memory(self.test_memory_db, max_messages=100)
        scheduler = Scheduler(self.test_scheduler_db)

        self.agent = Agent(config, memory, scheduler)

    def tearDown(self):
        """Cleanup test databases"""
        self.agent.stop()
        for db_file in [self.test_memory_db, self.test_scheduler_db]:
            if os.path.exists(db_file):
                os.remove(db_file)

    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent)

    def test_memory_operations(self):
        """Test memory operations"""
        self.agent.set_memory('test', 'value')
        result = self.agent.get_memory('test')
        self.assertEqual(result, 'value')


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestTools))
    suite.addTests(loader.loadTestsFromTestCase(TestAIProviders))
    suite.addTests(loader.loadTestsFromTestCase(TestAgent))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    print("=" * 50)
    print("    QuickBot Test Suite")
    print("=" * 50)
    print()

    exit_code = run_tests()

    print()
    print("=" * 50)
    if exit_code == 0:
        print("    All tests PASSED ✓")
    else:
        print("    Some tests FAILED ✗")
    print("=" * 50)

    sys.exit(exit_code)
