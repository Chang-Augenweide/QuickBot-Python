"""
QuickBot - Task Scheduler
Cron-like scheduling for reminders and automation.
"""
import uuid
import sqlite3
import logging
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleType(Enum):
    """Schedule types."""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"


class ScheduledTask:
    """Represents a scheduled task."""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        schedule_type: ScheduleType,
        schedule_value: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
        enabled: bool = True
    ):
        self.task_id = task_id
        self.name = name
        self.schedule_type = schedule_type
        self.schedule_value = schedule_value
        self.payload = payload
        self.session_id = session_id
        self.enabled = enabled
        self.status = TaskStatus.PENDING
        self.next_run = self._calculate_next_run()
        self.last_run = None
        self.run_count = 0
    
    def _calculate_next_run(self) -> datetime:
        """Calculate next run time based on schedule."""
        now = datetime.now()
        
        if self.schedule_type == ScheduleType.ONCE:
            try:
                return datetime.fromisoformat(self.schedule_value)
            except ValueError:
                return now + timedelta(hours=1)
        
        elif self.schedule_type == ScheduleType.INTERVAL:
            try:
                minutes = int(self.schedule_value)
                return now + timedelta(minutes=minutes)
            except ValueError:
                return now + timedelta(hours=1)
        
        elif self.schedule_type == ScheduleType.CRON:
            # Simple cron implementation
            # Format: "*/5 * * * *" (every 5 minutes)
            # For now, just default to hourly
            return now + timedelta(hours=1)
        
        return now + timedelta(hours=1)
    
    def update_next_run(self) -> None:
        """Update next run time after execution."""
        if self.schedule_type == ScheduleType.ONCE:
            self.enabled = False
        else:
            self.next_run = self._calculate_next_run()


class Scheduler:
    """Task scheduler with database persistence."""
    
    def __init__(self, db_path: str = "scheduler.db"):
        self.db_path = Path(db_path)
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._task_handler: Optional[Callable] = None
        self._init_db()
        self._load_tasks()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_value TEXT NOT NULL,
                payload TEXT NOT NULL,
                session_id TEXT,
                enabled INTEGER DEFAULT 1,
                next_run TEXT NOT NULL,
                last_run TEXT,
                run_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_tasks(self) -> None:
        """Load tasks from database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE enabled = 1")
        
        for row in cursor.fetchall():
            task = ScheduledTask(
                task_id=row['task_id'],
                name=row['name'],
                schedule_type=ScheduleType(row['schedule_type']),
                schedule_value=row['schedule_value'],
                payload=json.loads(row['payload']),
                session_id=row['session_id'],
                enabled=bool(row['enabled'])
            )
            
            task.next_run = datetime.fromisoformat(row['next_run'])
            task.last_run = datetime.fromisoformat(row['last_run']) if row['last_run'] else None
            task.run_count = row['run_count']
            
            self.tasks[task.task_id] = task
        
        conn.close()
        logger.info(f"Loaded {len(self.tasks)} scheduled tasks")
    
    def _save_task(self, task: ScheduledTask) -> None:
        """Save task to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO tasks
            (task_id, name, schedule_type, schedule_value, payload, session_id,
             enabled, next_run, last_run, run_count, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                task.task_id, task.name, task.schedule_type.value,
                task.schedule_value, json.dumps(task.payload), task.session_id,
                int(task.enabled), task.next_run.isoformat(),
                task.last_run.isoformat() if task.last_run else None,
                task.run_count
            )
        )
        
        conn.commit()
        conn.close()
    
    def set_task_handler(self, handler: Callable) -> None:
        """Set the callback function for executing tasks."""
        self._task_handler = handler
    
    def add_task(
        self,
        name: str,
        schedule_type: ScheduleType,
        schedule_value: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> str:
        """Add a new scheduled task."""
        task_id = str(uuid.uuid4())
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            schedule_type=schedule_type,
            schedule_value=schedule_value,
            payload=payload,
            session_id=session_id,
            enabled=True
        )
        
        self.tasks[task_id] = task
        self._save_task(task)
        
        logger.info(f"Added task: {name} ({schedule_type.value})")
        return task_id
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.enabled = False
        task.status = TaskStatus.CANCELLED
        
        # Delete from database
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        conn.close()
        
        del self.tasks[task_id]
        logger.info(f"Removed task: {task_id}")
        return True
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[ScheduledTask]:
        """Get all tasks."""
        return list(self.tasks.values())
    
    def get_tasks_for_session(self, session_id: str) -> List[ScheduledTask]:
        """Get tasks for a specific session."""
        return [
            task for task in self.tasks.values()
            if task.session_id == session_id
        ]
    
    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a task."""
        task.status = TaskStatus.RUNNING
        logger.info(f"Executing task: {task.name} ({task.task_id})")
        
        try:
            if self._task_handler:
                await self._task_handler(task)
            
            task.status = TaskStatus.COMPLETED
            task.last_run = datetime.now()
            task.run_count += 1
            
            logger.info(f"Task completed: {task.name}")
        
        except Exception as e:
            task.status = TaskStatus.FAILED
            logger.error(f"Task failed: {task.name} - {str(e)}")
        
        finally:
            task.update_next_run()
            self._save_task(task)
    
    async def _check_and_run_tasks(self) -> None:
        """Check for tasks that need to run."""
        now = datetime.now()
        tasks_to_run = [
            task for task in self.tasks.values()
            if task.enabled and task.next_run <= now
        ]
        
        for task in tasks_to_run:
            asyncio.create_task(self._execute_task(task))
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            return
        
        self._running = True
        logger.info("Scheduler started")
        
        while self._running:
            await self._check_and_run_tasks()
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        logger.info("Scheduler stopped")
    
    def parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime."""
        # Support formats like "9:00", "14:30", "2026-02-16 09:00"
        try:
            # Try full datetime
            return datetime.fromisoformat(time_str)
        except ValueError:
            pass
        
        try:
            # Try time only (for today)
            today = datetime.now().date()
            time_part = datetime.strptime(time_str, "%H:%M").time()
            return datetime.combine(today, time_part)
        except ValueError:
            pass
        
        raise ValueError(f"Invalid time format: {time_str}")
    
    def add_reminder(
        self,
        session_id: str,
        message: str,
        remind_at: str,
        description: Optional[str] = None
    ) -> str:
        """Add a reminder task."""
        remind_time = self.parse_time(remind_at)
        
        # If time has passed today, schedule for tomorrow
        now = datetime.now()
        if remind_time <= now:
            remind_time += timedelta(days=1)
        
        payload = {
            'type': 'reminder',
            'message': message
        }
        
        task_id = self.add_task(
            name=description or "Reminder",
            schedule_type=ScheduleType.ONCE,
            schedule_value=remind_time.isoformat(),
            payload=payload,
            session_id=session_id
        )
        
        logger.info(f"Added reminder for {remind_time}: {message}")
        return task_id
    
    def add_recurring_task(
        self,
        session_id: str,
        name: str,
        interval_minutes: int,
        payload: Dict[str, Any]
    ) -> str:
        """Add a recurring task."""
        return self.add_task(
            name=name,
            schedule_type=ScheduleType.INTERVAL,
            schedule_value=str(interval_minutes),
            payload=payload,
            session_id=session_id
        )
