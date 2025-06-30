import sqlite3
import pandas as pd
import os
from config import Config

class DatabaseManager:
    def __init__(self):
        self.props_db = Config.PROPS_DB
        self.stats_db = Config.STATS_DB
        self.init_databases()
    
    def init_databases(self):
        os.makedirs(Config.DATABASE_PATH, exist_ok=True)
        self.create_props_tables()
        print("✅ Database initialized")
    
    def create_props_tables(self):
        conn = sqlite3.connect(self.props_db)
        cursor = conn.cursor()
        
        # Check if odds column exists, if not add it
        cursor.execute("PRAGMA table_info(props)")
        columns = [column[1] for column in cursor.fetchall()]
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS props (
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
        
        # Add missing columns if they don't exist
        if 'odds' not in columns:
            try:
                cursor.execute("ALTER TABLE props ADD COLUMN odds TEXT")
                print("✅ Added odds column to database")
            except:
                pass
        
        if 'bet_type' not in columns:
            try:
                cursor.execute("ALTER TABLE props ADD COLUMN bet_type TEXT")
                print("✅ Added bet_type column to database")
            except:
                pass
        
        if 'raw_input' not in columns:
            try:
                cursor.execute("ALTER TABLE props ADD COLUMN raw_input TEXT")
                print("✅ Added raw_input column to database")
            except:
                pass
        
        conn.commit()
        conn.close()
    
    def add_prop(self, prop_data):
        conn = sqlite3.connect(self.props_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO props (sport, player_name, prop_type, line_value, bet_type, odds, raw_input)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            prop_data['sport'],
            prop_data['player_name'],
            prop_data['prop_type'],
            prop_data['line_value'],
            prop_data.get('bet_type'),
            prop_data.get('odds'),
            prop_data.get('raw_input')
        ))
        
        prop_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return prop_id
    
    def get_recommended_props(self):
        conn = sqlite3.connect(self.props_db)
        try:
            df = pd.read_sql_query("""
                SELECT * FROM props
                WHERE recommended = TRUE
                ORDER BY confidence_score DESC
            """, conn)
        except Exception as e:
            print(f"⚠️ Database query error: {e}")
            df = pd.DataFrame()
        conn.close()
        return df
    
    def update_prop_analysis(self, prop_id, analysis_data):
        """Update prop with analysis results"""
        conn = sqlite3.connect(self.props_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE props
            SET analyzed = TRUE,
                recommended = ?,
                confidence_score = ?
            WHERE id = ?
        """, (
            analysis_data.get('recommended', False),
            analysis_data.get('confidence_score', 0),
            prop_id
        ))
        
        conn.commit()
        conn.close()
        print("✅ Updated database with analysis results")
    
    def get_unanalyzed_props(self):
        """Get props that haven't been analyzed yet"""
        conn = sqlite3.connect(self.props_db)
        try:
            df = pd.read_sql_query("""
                SELECT * FROM props
                WHERE analyzed = FALSE
                ORDER BY created_at DESC
            """, conn)
        except:
            df = pd.DataFrame()
        conn.close()
        return df
    
    def get_all_props(self):
        """Get all props for reporting"""
        conn = sqlite3.connect(self.props_db)
        try:
            df = pd.read_sql_query("""
                SELECT * FROM props
                ORDER BY created_at DESC
            """, conn)
        except Exception as e:
            print(f"⚠️ Database query error: {e}")
            df = pd.DataFrame()
        conn.close()
        return df
'''

# =============================================================================
# ALTERNATIVE QUICK FIX - Delete and recreate database
# =============================================================================

quick_fix_script = '''
import os
import sqlite3
from config import Config

def fix_database():
    """Delete old database and recreate with proper schema"""
    
    # Delete old database files
    if os.path.exists(Config.PROPS_DB):
        os.remove(Config.PROPS_DB)
        print("🗑️ Deleted old props database")
    
    if os.path.exists(Config.STATS_DB):
        os.remove(Config.STATS_DB)
        print("🗑️ Deleted old stats database")
    
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

print("🔧 DATABASE FIX NEEDED")
print("=" * 50)
print()
print("🚨 Issue: Database table missing 'odds' column")
print()
print("💡 OPTION 1 (Recommended): Replace database_manager.py")
print("   Copy the 'database_manager_fixed' code above into your database_manager.py")
print()
print("💡 OPTION 2 (Quick Fix): Reset database")
print("   Create a file called 'fix_database.py' with the 'quick_fix_script' code")
print("   Then run: python fix_database.py")
print()
print("🚀 After applying either fix:")
print("   python main.py")
print()
print("🎯 The fixed version will:")
print("   ✅ Add missing database columns automatically")
print("   ✅ Handle the odds data properly") 
print("   ✅ Store complete prop information")
print("   ✅ Enable proper analysis and reporting")