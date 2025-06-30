import os
import sqlite3
from config import Config

def fix_database():
    """Delete old database and recreate with proper schema"""
    
    # Delete old database files
    if os.path.exists(Config.PROPS_DB):
        os.remove(Config.PROPS_DB)
        print("🗑️ Deleted old props database")
    
    # Create new database with proper schema
    conn = sqlite3.connect(Config.PROPS_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE props (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT NOT NULL,
            player_name TEXT NOT NULL,
            prop_type TEXT NOT NULL,
            line_value REAL NOT NULL,
            bet_type TEXT,
            odds TEXT,
            raw_input TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analyzed BOOLEAN DEFAULT FALSE,
            recommended BOOLEAN DEFAULT FALSE,
            confidence_score REAL
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Created new database with proper schema")

if __name__ == "__main__":
    fix_database()