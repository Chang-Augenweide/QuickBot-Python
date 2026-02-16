"""
QuickBot - Basic Tests
"""
import asyncio
import unittest
from pathlib import Path
import tempfile
import os

from config import Config
from memory import Memory
from scheduler import Scheduler, ScheduleType
from tools import ToolRegistry, FileTool


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration loading."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_file = f.name
            f.write("bot:\n  name: TestBot\n")
        
        try:
            config = Config(config_file)
            self.assertEqual(config.get('bot.name'), 'TestBot')
            
            config.set('bot.debug', True)
            self.assertTrue(config.get('bot.debug'))
        
        finally:
            os.unlink(config_file)


class TestMemory(unittest.TestCase):
    """Test memory management."""
    
    def setUp(self):
        """Set up test database."""
        self.db_file = tempfile.mktemp(suffix='.db')
        self.memory = Memory(db_path=self.db_file)
        self.session_id = "test_session"
    
    def tearDown(self):
        """Clean up."""
        self.memory.close()
        if os.path.exists(self.db_file):
            os.unlink(self.db_file)
    
    def test_add_get_message(self):
        """Test adding and retrieving messages."""
        self.memory.add_message(
            session_id=self.session_id,
            role='user',
            content='Hello world'
        )
        
        messages = self.memory.get_messages(self.session_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['content'], 'Hello world')
    
    def test_long_term_memory(self):
        """Test long-term memory operations."""
        self.memory.set_long_term('test_key', 'test_value')
        value = self.memory.get_long_term('test_key')
        
        self.assertEqual(value, 'test_value')
    
    def test_context_generation(self):
        """Test context generation."""
        self.memory.add_message(
            session_id=self.session_id,
            role='user',
            content='First message'
        )
        
        context = self.memory.get_context(self.session_id)
        self.assertGreater(len(context), 0)


class TestScheduler(unittest.TestCase):
    """Test scheduler."""
    
    def setUp(self):
        """Set up test database."""
        self.db_file = tempfile.mktemp(suffix='.db')
        self.scheduler = Scheduler(db_path=self.db_file)
    
    def tearDown(self):
        """Clean up."""
        scheduler_tasks = self.scheduler.get_all_tasks()
        for task in scheduler_tasks:
            self.scheduler.remove_task(task.task_id)
        
        if os.path.exists(self.db_file):
            os.unlink(self.db_file)
    
    def test_add_task(self):
        """Test adding a task."""
        task_id = self.scheduler.add_task(
            name='Test Task',
            schedule_type=ScheduleType.INTERVAL,
            schedule_value='60',
            payload={'type': 'message', 'text': 'Hello'}
        )
        
        task = self.scheduler.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.name, 'Test Task')
    
    def test_add_reminder(self):
        """Test adding a reminder."""
        task_id = self.scheduler.add_reminder(
            session_id='user123',
            message='Test reminder',
            remind_at='10:00'
        )
        
        task = self.scheduler.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task.payload['type'], 'reminder')


class TestTools(unittest.TestCase):
    """Test tool system."""
    
    def setUp(self):
        """Set up tool registry."""
        self.registry = ToolRegistry()
        self.temp_dir = tempfile.mkdtemp()
        self.file_tool = FileTool(base_dir=self.temp_dir)
        self.registry.register(self.file_tool)
    
    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_file_tool_write_read(self):
        """Test file write and read."""
        # Write
        result = await self.file_tool.execute(
            operation='write',
            path='test.txt',
            content='Hello world'
        )
        self.assertIn('Success', result)
        
        # Read
        result = await self.file_tool.execute(
            operation='read',
            path='test.txt'
        )
        self.assertEqual(result, 'Hello world')
    
    async def test_file_tool_list(self):
        """Test file listing."""
        result = await self.file_tool.execute(
            operation='list',
            path='.'
        )
        self.assertIsNotNone(result)


if __name__ == '__main__':
    # Run async tests with event loop
    def run_async_test(test_func):
        def wrapper(self):
            asyncio.run(test_func(self))
        wrapper.__name__ = test_func.__name__
        return wrapper
    
    # Wrap async tests
    TestTools.test_file_tool_write_read = run_async_test(TestTools.test_file_tool_write_read)
    TestTools.test_file_tool_list = run_async_test(TestTools.test_file_tool_list)
    
    unittest.main()
