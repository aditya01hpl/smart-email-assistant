import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class EmailDatabase:
    """SQLite database for storing processed emails"""
    
    def __init__(self, db_path: str = "emails.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables with migration support"""
        try:
            # First, let's check if database exists and backup if needed
            if os.path.exists(self.db_path):
                print(f"[DEBUG] Database exists at {self.db_path}")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Check if emails table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
                emails_table_exists = cursor.fetchone()
                
                # Check if sync_metadata table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_metadata'")
                sync_table_exists = cursor.fetchone()
                
                if not emails_table_exists or not sync_table_exists:
                    print("[DEBUG] Creating missing database tables...")
                    self._create_fresh_tables(cursor)
                else:
                    print("[DEBUG] Database tables exist, checking for migrations...")
                    self._migrate_database(cursor)
                
                conn.commit()
                print("[DEBUG] Database initialization completed successfully")
                
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {str(e)}")
            # Try to create fresh database
            try:
                if os.path.exists(self.db_path):
                    backup_path = f"{self.db_path}.backup_{int(datetime.now().timestamp())}"
                    os.rename(self.db_path, backup_path)
                    print(f"[DEBUG] Backed up corrupted database to {backup_path}")
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    self._create_fresh_tables(cursor)
                    conn.commit()
                    print("[DEBUG] Created fresh database successfully")
            except Exception as e2:
                print(f"[ERROR] Failed to create fresh database: {str(e2)}")
                raise
    
    def _create_fresh_tables(self, cursor):
        """Create fresh database tables with all columns"""
        print("[DEBUG] Creating emails table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                sender_name TEXT DEFAULT '',
                subject TEXT NOT NULL,
                body TEXT DEFAULT '',
                timestamp TEXT NOT NULL,
                summary TEXT DEFAULT '',
                has_reply BOOLEAN DEFAULT FALSE,
                draft_reply TEXT DEFAULT '',
                is_relevant BOOLEAN DEFAULT TRUE,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                conversation_id TEXT DEFAULT '',
                priority TEXT DEFAULT 'medium'
            )
        ''')
        
        print("[DEBUG] Creating sync_metadata table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                key TEXT PRIMARY KEY,
                value TEXT DEFAULT '',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self._create_indexes(cursor)
        print("[DEBUG] Tables and indexes created successfully")
    
    def _migrate_database(self, cursor):
        """Migrate existing database to new schema"""
        try:
            # Check if priority column exists
            cursor.execute("PRAGMA table_info(emails)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'priority' not in columns:
                print("[MIGRATION] Adding priority column to emails table")
                cursor.execute('ALTER TABLE emails ADD COLUMN priority TEXT DEFAULT "medium"')
            
            if 'sender_name' not in columns:
                print("[MIGRATION] Adding sender_name column to emails table")
                cursor.execute('ALTER TABLE emails ADD COLUMN sender_name TEXT DEFAULT ""')
            
            if 'conversation_id' not in columns:
                print("[MIGRATION] Adding conversation_id column to emails table")
                cursor.execute('ALTER TABLE emails ADD COLUMN conversation_id TEXT DEFAULT ""')
            
            # Create any missing indexes
            self._create_indexes(cursor)
            print("[DEBUG] Database migration completed")
            
        except Exception as e:
            print(f"[ERROR] Database migration failed: {str(e)}")
            raise
    
    def _create_indexes(self, cursor):
        """Create necessary indexes"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_emails_timestamp ON emails(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_emails_has_reply ON emails(has_reply)",
            "CREATE INDEX IF NOT EXISTS idx_emails_relevant ON emails(is_relevant)",
            "CREATE INDEX IF NOT EXISTS idx_emails_priority ON emails(priority)",
            "CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                print(f"[WARNING] Failed to create index: {str(e)}")
    
    def save_email(self, email_data: Dict) -> bool:
        """Save or update email in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO emails 
                    (id, sender, sender_name, subject, body, timestamp, summary, 
                     has_reply, draft_reply, is_relevant, conversation_id, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email_data['id'],
                    email_data['sender'],
                    email_data.get('sender_name', ''),
                    email_data['subject'],
                    email_data['body'],
                    email_data['timestamp'],
                    email_data.get('summary', ''),
                    email_data.get('has_reply', False),
                    email_data.get('draft_reply', ''),
                    email_data.get('is_relevant', True),
                    email_data.get('conversation_id', ''),
                    email_data.get('priority', 'medium')
                ))
                
                conn.commit()
                print(f"[DEBUG] Successfully saved email: {email_data['subject'][:30]}...")
                return True
        except Exception as e:
            print(f"[ERROR] Error saving email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_email_by_id(self, email_id: str) -> Optional[Dict]:
        """Get email by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM emails WHERE id = ? AND is_relevant = TRUE
                ''', (email_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            print(f"[ERROR] Error getting email by ID: {str(e)}")
        
        return None
    
    def get_all_emails(self, limit: int = 50) -> List[Dict]:
        """Get all relevant emails ordered by timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM emails 
                    WHERE is_relevant = TRUE
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] Error getting all emails: {str(e)}")
            return []
    
    def get_emails_by_priority(self, priority: str) -> List[Dict]:
        """Get emails filtered by priority"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM emails 
                    WHERE is_relevant = TRUE AND priority = ?
                    ORDER BY timestamp DESC
                ''', (priority.lower(),))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] Error getting emails by priority: {str(e)}")
            return []
    
    def get_unreplied_emails(self) -> List[Dict]:
        """Get emails that haven't been replied to"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM emails 
                    WHERE has_reply = FALSE AND is_relevant = TRUE
                    ORDER BY timestamp DESC
                ''')
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] Error getting unreplied emails: {str(e)}")
            return []
    
    def mark_as_replied(self, email_id: str) -> bool:
        """Mark email as replied"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE emails 
                    SET has_reply = TRUE 
                    WHERE id = ?
                ''', (email_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[ERROR] Error marking email as replied: {str(e)}")
            return False
    
    def update_draft_reply(self, email_id: str, draft_reply: str) -> bool:
        """Update draft reply for an email"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE emails 
                    SET draft_reply = ? 
                    WHERE id = ?
                ''', (draft_reply, email_id))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[ERROR] Error updating draft reply: {str(e)}")
            return False
    
    def get_email_stats(self) -> Dict:
        """Get email statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total emails
                cursor.execute('SELECT COUNT(*) FROM emails WHERE is_relevant = TRUE')
                total_emails = cursor.fetchone()[0]
                
                # Unreplied emails
                cursor.execute('SELECT COUNT(*) FROM emails WHERE has_reply = FALSE AND is_relevant = TRUE')
                unreplied_emails = cursor.fetchone()[0]
                
                # Replied emails
                cursor.execute('SELECT COUNT(*) FROM emails WHERE has_reply = TRUE AND is_relevant = TRUE')
                replied_emails = cursor.fetchone()[0]
                
                # Recent emails (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM emails 
                    WHERE datetime(timestamp) > datetime('now', '-1 day') 
                    AND is_relevant = TRUE
                ''')
                recent_emails = cursor.fetchone()[0]
                
                # Priority breakdown
                cursor.execute('''
                    SELECT priority, COUNT(*) as count 
                    FROM emails 
                    WHERE is_relevant = TRUE
                    GROUP BY priority
                ''')
                priority_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Top senders
                cursor.execute('''
                    SELECT sender, COUNT(*) as count 
                    FROM emails 
                    WHERE is_relevant = TRUE
                    GROUP BY sender 
                    ORDER BY count DESC 
                    LIMIT 5
                ''')
                top_senders = [{'sender': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                return {
                    'total_emails': total_emails,
                    'unreplied_emails': unreplied_emails,
                    'replied_emails': replied_emails,
                    'recent_emails': recent_emails,
                    'reply_rate': round((replied_emails / total_emails * 100) if total_emails > 0 else 0, 1),
                    'priority_stats': priority_stats,
                    'top_senders': top_senders
                }
        except Exception as e:
            print(f"[ERROR] Error getting email stats: {str(e)}")
            return {
                'total_emails': 0,
                'unreplied_emails': 0,
                'replied_emails': 0,
                'recent_emails': 0,
                'reply_rate': 0,
                'priority_stats': {},
                'top_senders': []
            }
    
    def update_last_sync(self):
        """Update last sync timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO sync_metadata (key, value, updated_at)
                    VALUES ('last_sync', ?, CURRENT_TIMESTAMP)
                ''', (datetime.now().isoformat(),))
                
                conn.commit()
        except Exception as e:
            print(f"[ERROR] Error updating last sync: {str(e)}")
    
    def get_last_sync_time(self) -> Optional[str]:
        """Get last sync timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT value FROM sync_metadata WHERE key = 'last_sync'
                ''')
                
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"[ERROR] Error getting last sync time: {str(e)}")
            return None
    
    def search_emails(self, query: str, limit: int = 20) -> List[Dict]:
        """Search emails by subject, sender, or body content"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                search_pattern = f"%{query}%"
                cursor.execute('''
                    SELECT * FROM emails 
                    WHERE (subject LIKE ? OR sender LIKE ? OR body LIKE ?)
                    AND is_relevant = TRUE
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (search_pattern, search_pattern, search_pattern, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] Error searching emails: {str(e)}")
            return []
    
    def cleanup_old_emails(self, days: int = 30):
        """Remove emails older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM emails 
                    WHERE datetime(timestamp) < datetime('now', '-{} days')
                '''.format(days))
                
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"[ERROR] Error cleaning up old emails: {str(e)}")
            return 0