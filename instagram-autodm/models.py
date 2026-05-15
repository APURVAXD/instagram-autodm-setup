import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.environ.get('DATABASE_PATH', 'autodm.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instagram_user_id TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            access_token TEXT NOT NULL,
            page_id TEXT,
            reply_message TEXT DEFAULT 'Thanks for your comment! Check your DMs 📩',
            dm_message TEXT DEFAULT 'Hi! Here''s the link you requested: https://example.com',
            cta_button_text TEXT,
            cta_button_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_synced TIMESTAMP
        )
    ''')
    
    # Monitored posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitored_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            post_id TEXT NOT NULL,
            post_caption TEXT,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            UNIQUE(account_id, post_id)
        )
    ''')
    
    # Comments processed table (to avoid duplicate DMs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT UNIQUE NOT NULL,
            account_id INTEGER NOT NULL,
            post_id TEXT NOT NULL,
            commenter_id TEXT NOT NULL,
            commenter_username TEXT,
            comment_text TEXT,
            replied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dm_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

class Account:
    """Instagram account model"""
    
    @staticmethod
    def create(instagram_user_id, username, access_token, page_id=None):
        """Create or update account"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (instagram_user_id, username, access_token, page_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(instagram_user_id) 
            DO UPDATE SET 
                username=excluded.username,
                access_token=excluded.access_token,
                page_id=excluded.page_id,
                last_synced=CURRENT_TIMESTAMP
        ''', (instagram_user_id, username, access_token, page_id))
        conn.commit()
        account_id = cursor.lastrowid
        conn.close()
        return account_id
    
    @staticmethod
    def get_by_id(account_id):
        """Get account by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()
        conn.close()
        return dict(account) if account else None
    
    @staticmethod
    def get_by_instagram_id(instagram_user_id):
        """Get account by Instagram user ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE instagram_user_id = ?', (instagram_user_id,))
        account = cursor.fetchone()
        conn.close()
        return dict(account) if account else None
    
    @staticmethod
    def get_all():
        """Get all accounts"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
        accounts = cursor.fetchall()
        conn.close()
        return [dict(acc) for acc in accounts]
    
    @staticmethod
    def update_messages(account_id, reply_message, dm_message, cta_button_text=None, cta_button_url=None):
        """Update reply and DM messages"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts 
            SET reply_message = ?, dm_message = ?, cta_button_text = ?, cta_button_url = ?
            WHERE id = ?
        ''', (reply_message, dm_message, cta_button_text, cta_button_url, account_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(account_id):
        """Delete account"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()

class MonitoredPost:
    """Monitored Instagram post model"""
    
    @staticmethod
    def add(account_id, post_id, post_caption):
        """Add post to monitoring"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO monitored_posts (account_id, post_id, post_caption)
            VALUES (?, ?, ?)
            ON CONFLICT(account_id, post_id) DO NOTHING
        ''', (account_id, post_id, post_caption))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_by_account(account_id):
        """Get all monitored posts for account"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM monitored_posts 
            WHERE account_id = ? 
            ORDER BY created_at DESC
        ''', (account_id,))
        posts = cursor.fetchall()
        conn.close()
        return [dict(post) for post in posts]
    
    @staticmethod
    def toggle_enabled(post_id, enabled):
        """Enable/disable monitoring for post"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE monitored_posts SET enabled = ? WHERE id = ?', (enabled, post_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(post_id):
        """Remove post from monitoring"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM monitored_posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()

class ProcessedComment:
    """Processed comment model (for deduplication)"""
    
    @staticmethod
    def add(comment_id, account_id, post_id, commenter_id, commenter_username, comment_text, dm_sent=False):
        """Mark comment as processed"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO processed_comments 
                (comment_id, account_id, post_id, commenter_id, commenter_username, comment_text, dm_sent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (comment_id, account_id, post_id, commenter_id, commenter_username, comment_text, dm_sent))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Already processed
            return False
        finally:
            conn.close()
    
    @staticmethod
    def is_processed(comment_id):
        """Check if comment was already processed"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM processed_comments WHERE comment_id = ?', (comment_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    @staticmethod
    def get_by_account(account_id, limit=50):
        """Get processed comments for account"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM processed_comments 
            WHERE account_id = ? 
            ORDER BY replied_at DESC 
            LIMIT ?
        ''', (account_id, limit))
        comments = cursor.fetchall()
        conn.close()
        return [dict(comment) for comment in comments]

# Initialize database on import
init_db()
