import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..base_provider import DatabaseProvider


class SQLiteProvider(DatabaseProvider):
    """SQLite database provider for local storage."""
    
    def __init__(self, db_path: str = "dwell.db"):
        self.db_path = db_path
        self.initialize()
    
    @property
    def provider_name(self) -> str:
        return "sqlite"
    
    def initialize(self):
        """Initialize SQLite database and create tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    what_happened TEXT NOT NULL,
                    content_hash TEXT,
                    data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    activity_raw TEXT,
                    emotions TEXT,
                    entry_id INTEGER,
                    data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entry_id) REFERENCES journal_entries (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    data TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS human_values (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS value_comparison_instances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    superior_value_id INTEGER,
                    inferior_value_id INTEGER,
                    reason TEXT,
                    entry_id INTEGER,
                    thread_id INTEGER,
                    data TEXT DEFAULT '{}',
                    user_sentiment TEXT DEFAULT 'undecided',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (superior_value_id) REFERENCES human_values (id),
                    FOREIGN KEY (inferior_value_id) REFERENCES human_values (id),
                    FOREIGN KEY (entry_id) REFERENCES journal_entries (id),
                    FOREIGN KEY (thread_id) REFERENCES threads (id)
                )
            """)
            
            conn.commit()
            self._seed_human_values()
    
    def _seed_human_values(self):
        """Seed the human values table if empty."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM human_values")
            if cursor.fetchone()[0] == 0:
                from values import value_descriptions
                for name, desc in value_descriptions.items():
                    conn.execute("INSERT INTO human_values (name, description) VALUES (?, ?)", (name, desc))
                conn.commit()
    
    def get_entries(self, user_id: str, not_in_timestamps: List = None, not_in_ids: List = None) -> List[Dict]:
        """Get journal entries for a user."""
        not_in_timestamps = not_in_timestamps or []
        not_in_ids = not_in_ids or []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM journal_entries 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,))
            
            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                entry['data'] = json.loads(entry['data'])
                
                if entry["date"] in not_in_timestamps:
                    break
                if entry["id"] in not_in_ids:
                    break
                    
                entries.append(entry)
            
            return entries
    
    def add_entry(self, what_happened: str, user_id: str, date: str) -> Dict:
        """Add a new journal entry."""
        import hashlib
        content_hash = hashlib.sha256(what_happened.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO journal_entries (user_id, date, what_happened, content_hash, data)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, date, what_happened, content_hash, '{}'))
            
            entry_id = cursor.lastrowid
            conn.commit()
            
            return {"id": entry_id, "user_id": user_id, "date": date, "what_happened": what_happened, "content_hash": content_hash, "data": {}}
    
    def edit_entry(self, entry_id: str, what_happened: str) -> Dict:
        """Edit an existing journal entry and invalidate dependent data if content changed."""
        import hashlib
        new_content_hash = hashlib.sha256(what_happened.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get current entry to check if content changed
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
            current_entry = dict(cursor.fetchone())
            
            # If content hash is different, invalidate dependent data
            content_changed = current_entry.get('content_hash') != new_content_hash
            if content_changed:
                print(f"Content changed for entry {entry_id}, invalidating dependent data...")
                self.delete_activities_by_entry(entry_id)
                self.delete_value_comparisons_by_entry(entry_id)
            
            # Update the entry with new content and hash
            conn.execute("""
                UPDATE journal_entries 
                SET what_happened = ?, content_hash = ? 
                WHERE id = ?
            """, (what_happened, new_content_hash, entry_id))
            conn.commit()
            
            # Return updated entry
            cursor = conn.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
            updated_entry = dict(cursor.fetchone())
            updated_entry['data'] = json.loads(updated_entry['data'])
            return updated_entry
    
    def get_activities(self, user_id: str) -> List[Dict]:
        """Get activities for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM activities WHERE user_id = ?", (user_id,))
            activities = []
            for row in cursor.fetchall():
                activity = dict(row)
                activity['data'] = json.loads(activity['data'])
                activities.append(activity)
            return activities
    
    def add_activity(self, activity_data: Any, entry_id: str, user_id: str) -> Optional[Dict]:
        """Add a new activity."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO activities (user_id, activity, activity_raw, emotions, entry_id, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                activity_data.activity,
                activity_data.activity_raw,
                activity_data.emotion.name,
                entry_id,
                json.dumps({"reviewed": False})
            ))
            
            activity_id = cursor.lastrowid
            conn.commit()
            
            return {
                "id": activity_id,
                "user_id": user_id,
                "activity": activity_data.activity,
                "activity_raw": activity_data.activity_raw,
                "emotions": activity_data.emotion.name,
                "entry_id": entry_id,
                "data": {"reviewed": False}
            }
    
    def edit_activity(self, activity_id: str, update_payload: Dict) -> Dict:
        """Edit an existing activity."""
        with sqlite3.connect(self.db_path) as conn:
            set_clause = ", ".join([f"{k} = ?" for k in update_payload.keys()])
            values = list(update_payload.values()) + [activity_id]
            
            conn.execute(f"UPDATE activities SET {set_clause} WHERE id = ?", values)
            conn.commit()
            
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
            return dict(cursor.fetchone())
    
    def delete_activity(self, activity_id: str) -> Dict:
        """Delete an activity."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
            conn.commit()
            return {"deleted": True, "id": activity_id}
    
    def add_chat_message_DB(self, user_id: str, thread_id: str, role: str, content: str) -> Optional[str]:
        """Add a chat message to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO messages (user_id, thread_id, role, message_text)
                VALUES (?, ?, ?, ?)
            """, (user_id, thread_id, role, content))
            
            message_id = cursor.lastrowid
            conn.commit()
            return str(message_id)
    
    def add_thread_DB(self, user_id: str, type: str, thread_data: Dict) -> Optional[str]:
        """Add a thread to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO threads (user_id, type, data)
                VALUES (?, ?, ?)
            """, (user_id, type, json.dumps(thread_data)))
            
            thread_id = cursor.lastrowid
            conn.commit()
            return str(thread_id)
    
    def get_value_comparison_instances(self, user_id: str) -> List[Dict]:
        """Get value comparison instances for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM value_comparison_instances 
                WHERE user_id = ?
            """, (user_id,))
            
            instances = []
            for row in cursor.fetchall():
                instance = dict(row)
                instance['data'] = json.loads(instance['data'])
                instances.append(instance)
            return instances
    
    def get_human_values(self) -> List[Dict]:
        """Get all human values."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM human_values")
            return [dict(row) for row in cursor.fetchall()]
    
    def add_value_comparison_instance(self, value_comp: Any, new_entry: Dict, superior_value_id: str, inferior_value_id: str) -> Optional[Dict]:
        """Add a value comparison instance."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO value_comparison_instances 
                (user_id, type, superior_value_id, inferior_value_id, reason, entry_id, data, user_sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_entry["user_id"],
                "entry",
                superior_value_id,
                inferior_value_id,
                value_comp.reason,
                new_entry["id"],
                json.dumps({"entry_extract": value_comp.ref}),
                'undecided'
            ))
            
            comparison_id = cursor.lastrowid
            conn.commit()
            
            return {
                "id": comparison_id,
                "user_id": new_entry["user_id"],
                "type": "entry",
                "superior_value_id": superior_value_id,
                "inferior_value_id": inferior_value_id,
                "reason": value_comp.reason,
                "entry_id": new_entry["id"],
                "data": {"entry_extract": value_comp.ref},
                "user_sentiment": 'undecided'
            }
    
    def edit_value_comparison_instance(self, value_comparison_id: str, update_payload: Dict) -> Dict:
        """Edit a value comparison instance."""
        with sqlite3.connect(self.db_path) as conn:
            set_clause = ", ".join([f"{k} = ?" for k in update_payload.keys()])
            values = list(update_payload.values()) + [value_comparison_id]
            
            conn.execute(f"UPDATE value_comparison_instances SET {set_clause} WHERE id = ?", values)
            conn.commit()
            
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM value_comparison_instances WHERE id = ?", (value_comparison_id,))
            return dict(cursor.fetchone())
    
    def delete_activities_by_entry(self, entry_id: str) -> int:
        """Delete all activities associated with a journal entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM activities WHERE entry_id = ?", (entry_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"Deleted {deleted_count} activities for entry {entry_id}")
            return deleted_count
    
    def delete_value_comparisons_by_entry(self, entry_id: str) -> int:
        """Delete all value comparisons associated with a journal entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM value_comparison_instances WHERE entry_id = ?", (entry_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"Deleted {deleted_count} value comparisons for entry {entry_id}")
            return deleted_count