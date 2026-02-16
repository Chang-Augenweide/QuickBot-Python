"""
QuickBot - Memory Management Module
Implements long-term conversation memory with semantic search.
"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class Memory:
    """Conversation memory manager."""
    
    def __init__(self, db_path: str = "memory.db", max_messages: int = 1000):
        self.db_path = Path(db_path)
        self.max_messages = max_messages
        self._conn = None
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection (lazy initialization)."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for messages
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session_timestamp
            ON messages(session_id, timestamp)
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                platform TEXT,
                user_id TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Long-term memory table (for important information)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                importance INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add a message to memory."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO messages (session_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, json.dumps(metadata or {}))
        )
        
        message_id = cursor.lastrowid
        
        # Update session timestamp
        cursor.execute(
            """
            UPDATE sessions SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (session_id,)
        )
        
        # Prune old messages if over limit
        self._prune_messages(session_id)
        
        conn.commit()
        return message_id
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get messages for a session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if limit:
            cursor.execute(
                """
                SELECT id, role, content, metadata, timestamp
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                (session_id, limit, offset)
            )
        else:
            cursor.execute(
                """
                SELECT id, role, content, metadata, timestamp
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                """,
                (session_id,)
            )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row['id'],
                'role': row['role'],
                'content': row['content'],
                'metadata': json.loads(row['metadata']),
                'timestamp': row['timestamp']
            })
        
        return messages
    
    def _prune_messages(self, session_id: str) -> None:
        """Remove old messages if over limit."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Count messages
        cursor.execute(
            "SELECT COUNT(*) as count FROM messages WHERE session_id = ?",
            (session_id,)
        )
        count = cursor.fetchone()['count']
        
        if count > self.max_messages:
            # Keep only the most recent messages
            cursor.execute(
                """
                DELETE FROM messages
                WHERE session_id = ? AND id NOT IN (
                    SELECT id FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                )
                """,
                (session_id, session_id, self.max_messages)
            )
            conn.commit()
    
    def set_long_term(self, key: str, value: str, importance: int = 1) -> None:
        """Store information in long-term memory."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO long_term_memory (key, value, importance, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (key, value, importance)
        )
        
        conn.commit()
    
    def get_long_term(self, key: str) -> Optional[str]:
        """Retrieve information from long-term memory."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT value FROM long_term_memory WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        
        return row['value'] if row else None
    
    def search_long_term(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search long-term memory (simple keyword search)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Simple LIKE search (for more advanced, use embeddings)
        cursor.execute(
            """
            SELECT key, value, importance, created_at
            FROM long_term_memory
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
            """,
            (f"%{query}%", f"%{query}%", limit)
        )
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'key': row['key'],
                'value': row['value'],
                'importance': row['importance'],
                'created_at': row['created_at']
            })
        
        return results
    
    def create_session(
        self,
        session_id: str,
        name: Optional[str] = None,
        platform: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create or update a session."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO sessions (id, name, platform, user_id, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, name, platform, user_id, json.dumps(metadata or {}))
        )
        
        conn.commit()
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, name, platform, user_id, metadata, created_at, updated_at
            FROM sessions
            WHERE id = ?
            """,
            (session_id,)
        )
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'name': row['name'],
                'platform': row['platform'],
                'user_id': row['user_id'],
                'metadata': json.loads(row['metadata']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, name, platform, user_id, created_at, updated_at
            FROM sessions
            ORDER BY updated_at DESC
            """
        )
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row['id'],
                'name': row['name'],
                'platform': row['platform'],
                'user_id': row['user_id'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return sessions
    
    def get_context(
        self,
        session_id: str,
        limit: Optional[int] = None,
        include_long_term: bool = True
    ) -> List[Dict[str, str]]:
        """Get conversation context for AI."""
        messages = self.get_messages(session_id, limit)
        messages.reverse()  # Chronological order
        
        context = []
        for msg in messages:
            context.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Add long-term memory as system message
        if include_long_term:
            important_memories = self.search_long_term("", limit=5)
            if important_memories:
                memory_text = "\n".join([
                    f"- {m['key']}: {m['value']}"
                    for m in important_memories
                    if m['importance'] >= 2
                ])
                if memory_text:
                    context.insert(0, {
                        'role': 'system',
                        'content': f"Key information about the user:\n{memory_text}"
                    })
        
        return context
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
