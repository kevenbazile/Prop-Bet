import os

def create_files_now():
    """Create all necessary files in current directory"""
    
    print("🚀 Creating Multi-Sport Prop Analysis files...")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Create subdirectories
    os.makedirs("tests", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 1. config.py
    with open("config.py", "w", encoding="utf-8") as f:
        f.write('''import os

class Config:
    # Database
    DATABASE_PATH = "./data/"
    PROPS_DB = os.path.join(DATABASE_PATH, "props.db")
    STATS_DB = os.path.join(DATABASE_PATH, "player_stats.db")
    
    # API Keys
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE")
    
    # Sports Configuration
    SUPPORTED_SPORTS = {
        "MLB": {
            "name": "Major League Baseball",
            "prop_types": ["hits", "runs", "rbis", "strikeouts", "home_runs"],
        },
        "NFL": {
            "name": "National Football League", 
            "prop_types": ["passing_yards", "rushing_yards", "receiving_yards", "touchdowns"],
        },
        "NBA": {
            "name": "National Basketball Association",
            "prop_types": ["points", "rebounds", "assists", "steals", "blocks"],
        }
    }
''')
    
    # 2. database_manager.py
    with open("database_manager.py", "w", encoding="utf-8") as f:
        f.write('''import sqlite3
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS props (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                player_name TEXT NOT NULL,
                prop_type TEXT NOT NULL,
                line_value REAL NOT NULL,
                odds TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analyzed BOOLEAN DEFAULT FALSE,
                recommended BOOLEAN DEFAULT FALSE,
                confidence_score REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_prop(self, prop_data):
        conn = sqlite3.connect(self.props_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO props (sport, player_name, prop_type, line_value, odds)
            VALUES (?, ?, ?, ?, ?)
        """, (
            prop_data['sport'],
            prop_data['player_name'],
            prop_data['prop_type'],
            prop_data['line_value'],
            prop_data.get('odds')
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
        except:
            df = pd.DataFrame()
        conn.close()
        return df
    
    def update_prop_analysis(self, prop_id, analysis_data):
        conn = sqlite3.connect(self.props_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE props
            SET analyzed = TRUE,
                recommended = ?,
                confidence_score = ?
            WHERE id = ?
        """, (
            analysis_data.get('recommended'),
            analysis_data.get('confidence_score'),
            prop_id
        ))
        
        conn.commit()
        conn.close()
''')
    
    # 3. prop_parser.py
    with open("prop_parser.py", "w", encoding="utf-8") as f:
        f.write('''import re
from datetime import datetime

class PropParser:
    def __init__(self):
        self.sport_keywords = {
            "MLB": ["baseball", "mlb", "runs", "hits", "strikeouts"],
            "NFL": ["football", "nfl", "yards", "touchdowns"],
            "NBA": ["basketball", "nba", "points", "rebounds", "assists"],
        }
    
    def parse_manual_input(self, input_text):
        props = []
        lines = input_text.strip().split('\\n')
        
        for line in lines:
            if not line.strip():
                continue
            prop = self.parse_single_prop(line.strip())
            if prop:
                props.append(prop)
        
        return props
    
    def parse_single_prop(self, line):
        try:
            # Pattern: Player Name Over/Under X.X Stat Type +/-XXX
            pattern = r'(.+?)\\s+(over|under|o|u)\\s+(\\d+\\.?\\d*)\\s+(.+?)\\s*([+-]\\d{3,4})?'
            match = re.search(pattern, line, re.IGNORECASE)
            
            if not match:
                print(f"⚠️ Could not parse: {line}")
                return None
            
            player_name = match.group(1).strip()
            over_under = match.group(2).lower()
            line_value = float(match.group(3))
            prop_type = match.group(4).strip()
            odds = match.group(5)
            
            sport = self.detect_sport(prop_type)
            prop_type = self.normalize_prop_type(prop_type)
            
            prop = {
                'player_name': player_name,
                'sport': sport,
                'prop_type': prop_type,
                'line_value': line_value,
                'bet_type': over_under,
                'odds': odds,
                'raw_input': line,
                'parsed_at': datetime.now().isoformat()
            }
            
            print(f"✅ Parsed: {player_name} {over_under} {line_value} {prop_type}")
            return prop
            
        except Exception as e:
            print(f"❌ Error parsing '{line}': {e}")
            return None
    
    def detect_sport(self, prop_type):
        prop_lower = prop_type.lower()
        for sport, keywords in self.sport_keywords.items():
            for keyword in keywords:
                if keyword in prop_lower:
                    return sport
        return "UNKNOWN"
    
    def normalize_prop_type(self, prop_type):
        prop_lower = prop_type.lower()
        normalizations = {
            "hits": "hits",
            "runs": "runs", 
            "points": "points",
            "rebounds": "rebounds",
            "assists": "assists",
            "passing yards": "passing_yards",
            "rushing yards": "rushing_yards",
        }
        
        for key, value in normalizations.items():
            if key in prop_lower:
                return value
        return prop_type.replace(" ", "_").lower()
''')
    
    # 4. data_fetcher.py
    with open("data_fetcher.py", "w", encoding="utf-8") as f:
        f.write('''class DataFetcher:
    def __init__(self):
        pass
    
    def fetch_player_stats(self, player_name, sport, days=30):
        print(f"🔍 Fetching stats for {player_name} ({sport})")
        return {
            'player_name': player_name,
            'sport': sport,
            'recent_averages': {
                'avg_hits': 1.2,
                'avg_runs': 0.8,
                'avg_points': 25.5,
                'avg_passing_yards': 280.0,
                'avg_rebounds': 8.2,
                'avg_assists': 6.1
            }
        }
''')
    
    # 5. analysis_engine.py
    with open("analysis_engine.py", "w", encoding="utf-8") as f:
        f.write('''from datetime import datetime

class AnalysisEngine:
    def __init__(self):
        self.confidence_thresholds = {
            'high': 0.75,
            'medium': 0.65,
            'low': 0.55
        }
    
    def analyze_prop(self, prop_data, player_stats):
        print(f"🔬 Analyzing {prop_data['player_name']} {prop_data['prop_type']}")
        
        # Simple confidence calculation
        confidence_score = 0.6  # Base confidence
        
        # Adjust based on stats if available
        if player_stats.get('recent_averages'):
            prop_type = prop_data['prop_type']
            line_value = prop_data['line_value']
            avg_key = f"avg_{prop_type}"
            
            if avg_key in player_stats['recent_averages']:
                recent_avg = player_stats['recent_averages'][avg_key]
                if recent_avg > line_value * 1.1:  # 10% above line
                    confidence_score += 0.15
                elif recent_avg > line_value:
                    confidence_score += 0.05
                elif recent_avg < line_value * 0.9:  # 10% below line
                    confidence_score -= 0.15
                else:
                    confidence_score -= 0.05
        
        confidence_score = max(0.0, min(1.0, confidence_score))
        recommendation = self.generate_recommendation(confidence_score)
        
        return {
            'player_name': prop_data['player_name'],
            'prop_type': prop_data['prop_type'],
            'line_value': prop_data['line_value'],
            'confidence_score': confidence_score,
            'recommendation': recommendation,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def generate_recommendation(self, confidence_score):
        if confidence_score >= self.confidence_thresholds['high']:
            return "STRONG_BET"
        elif confidence_score >= self.confidence_thresholds['medium']:
            return "MODERATE_BET"
        elif confidence_score >= self.confidence_thresholds['low']:
            return "WEAK_BET"
        else:
            return "AVOID"
''')
    
    # 6. report_generator.py
    with open("report_generator.py", "w", encoding="utf-8") as f:
        f.write('''from datetime import datetime
from database_manager import DatabaseManager

class ReportGenerator:
    def __init__(self):
        self.db = DatabaseManager()
    
    def generate_daily_report(self):
        today = datetime.now().strftime('%Y-%m-%d')
        props_df = self.db.get_recommended_props()
        
        if props_df.empty:
            return f"📊 Daily Report - {today}\\n\\nNo props analyzed today."
        
        total_props = len(props_df)
        
        report = f"""📊 Daily Prop Analysis Report
📅 Date: {today}

📈 Summary:
• Total Props Analyzed: {total_props}
• System Status: ✅ Operational

🔥 Recent Analysis Available
"""
        return report
''')
    
    # 7. main.py
    with open("main.py", "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Sport Prop Analysis System
"""

import sys
import argparse
from database_manager import DatabaseManager
from prop_parser import PropParser
from data_fetcher import DataFetcher
from analysis_engine import AnalysisEngine
from report_generator import ReportGenerator

class PropAnalysisSystem:
    def __init__(self):
        print("🚀 Initializing Multi-Sport Prop Analysis System...")
        self.db = DatabaseManager()
        self.parser = PropParser()
        self.fetcher = DataFetcher()
        self.analyzer = AnalysisEngine()
        self.reporter = ReportGenerator()
        print("✅ System initialized!")
    
    def analyze_prop_text(self, prop_text):
        print(f"🔍 Analyzing: {prop_text}")
        
        props = self.parser.parse_manual_input(prop_text)
        
        if not props:
            print("❌ Could not parse prop format")
            return
        
        for prop in props:
            prop_id = self.db.add_prop(prop)
            prop['id'] = prop_id
            
            print(f"📊 Fetching stats for {prop['player_name']}...")
            player_stats = self.fetcher.fetch_player_stats(
                prop['player_name'], 
                prop['sport']
            )
            
            analysis = self.analyzer.analyze_prop(prop, player_stats)
            
            self.db.update_prop_analysis(prop_id, {
                'recommended': analysis.get('recommendation') in ['STRONG_BET', 'MODERATE_BET'],
                'confidence_score': analysis.get('confidence_score', 0)
            })
            
            self.display_analysis(analysis)
    
    def display_analysis(self, analysis):
        confidence = analysis.get('confidence_score', 0) * 100
        recommendation = analysis.get('recommendation', 'UNKNOWN')
        
        print(f"\\n✅ Analysis Complete:")
        print(f"   Player: {analysis['player_name']}")
        print(f"   Prop: {analysis['prop_type']} {analysis['line_value']}")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Recommendation: {recommendation}")
        print("-" * 50)
    
    def interactive_mode(self):
        print("🎮 Multi-Sport Prop Analysis System - Interactive Mode")
        print("Enter props to analyze (or 'quit' to exit)")
        print("Example: Mike Trout Over 1.5 Hits +120")
        print("-" * 50)
        
        while True:
            try:
                prop_text = input("\\n📝 Enter prop: ").strip()
                
                if prop_text.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if prop_text.lower() == 'report':
                    report = self.reporter.generate_daily_report()
                    print(f"\\n{report}")
                    continue
                
                if prop_text.lower() == 'help':
                    print("""
📚 Help Commands:
• Enter prop text like: "Mike Trout Over 1.5 Hits +120"
• 'report' - Show daily report
• 'quit' - Exit system
                    """)
                    continue
                
                if prop_text:
                    self.analyze_prop_text(prop_text)
                
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Multi-Sport Prop Analysis System')
    parser.add_argument('--prop', help='Analyze a single prop')
    parser.add_argument('--report', action='store_true', help='Generate daily report')
    parser.add_argument('--mode', choices=['interactive', 'test'], 
                       default='interactive', help='Run mode')
    
    args = parser.parse_args()
    
    system = PropAnalysisSystem()
    
    if args.report:
        report = system.reporter.generate_daily_report()
        print(report)
        return
    
    if args.prop:
        system.analyze_prop_text(args.prop)
        return
    
    if args.mode == 'test':
        test_props = [
            "Mike Trout Over 1.5 Hits +120",
            "Patrick Mahomes Over 275.5 Passing Yards +110",
            "LeBron James Under 25.5 Points -110"
        ]
        
        print("🧪 Running test analysis...")
        for prop in test_props:
            system.analyze_prop_text(prop)
    else:
        system.interactive_mode()

if __name__ == "__main__":
    main()
''')
    
    # 8. quick_test.py
    with open("quick_test.py", "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify the system is working
"""

def test_imports():
    try:
        print("🧪 Testing imports...")
        
        import config
        print("✅ config.py imported")
        
        from database_manager import DatabaseManager
        print("✅ database_manager.py imported")
        
        from prop_parser import PropParser
        print("✅ prop_parser.py imported")
        
        from data_fetcher import DataFetcher
        print("✅ data_fetcher.py imported")
        
        from analysis_engine import AnalysisEngine
        print("✅ analysis_engine.py imported")
        
        print("\\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    try:
        print("\\n🔧 Testing basic functionality...")
        
        from prop_parser import PropParser
        parser = PropParser()
        
        test_prop = "Mike Trout Over 1.5 Hits +120"
        props = parser.parse_manual_input(test_prop)
        
        if props:
            print(f"✅ Prop parsing works: {props[0]['player_name']}")
        else:
            print("❌ Prop parsing failed")
            return False
        
        from database_manager import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialization works")
        
        print("\\n🎉 Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Test for Multi-Sport Prop Analysis System")
    print("=" * 50)
    
    import_success = test_imports()
    
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\\n✅ System is ready to use!")
            print("\\n🎯 Try these commands:")
            print("python main.py")
            print('python main.py --prop "Mike Trout Over 1.5 Hits +120"')
            print("python main.py --report")
            print("python main.py --mode test")
        else:
            print("\\n❌ System has functionality issues")
    else:
        print("\\n❌ Import issues - check that all files are created")
''')
    
    # 9. tests/__init__.py
    with open("tests/__init__.py", "w", encoding="utf-8") as f:
        f.write("# Test package initialization\\n")
    
    # 10. tests/test_prop_parser.py
    with open("tests/test_prop_parser.py", "w", encoding="utf-8") as f:
        f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prop_parser import PropParser

class TestPropParser(unittest.TestCase):
    def setUp(self):
        self.parser = PropParser()
    
    def test_parse_mlb_prop(self):
        input_text = "Mike Trout Over 1.5 Hits +120"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Mike Trout")
        self.assertEqual(prop['sport'], "MLB")
        self.assertEqual(prop['prop_type'], "hits")
        self.assertEqual(prop['line_value'], 1.5)
    
    def test_parse_nfl_prop(self):
        input_text = "Patrick Mahomes Over 275.5 Passing Yards +110"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Patrick Mahomes")
        self.assertEqual(prop['sport'], "NFL")
    
    def test_invalid_prop(self):
        input_text = "Invalid prop format"
        props = self.parser.parse_manual_input(input_text)
        self.assertEqual(len(props), 0)

if __name__ == '__main__':
    unittest.main()
''')
    
    # 11. requirements.txt
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write('''pandas>=1.5.0
numpy>=1.24.0
requests>=2.28.0
python-telegram-bot>=20.0
beautifulsoup4>=4.11.0
selenium>=4.8.0
schedule>=1.2.0
python-dotenv>=1.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
''')
    
    print("\\n✅ All files created successfully!")
    print(f"📁 Files created in: {os.getcwd()}")
    print("\\n🎯 Next steps:")
    print("1. python quick_test.py")
    print("2. python main.py")
    print('3. python main.py --prop "Mike Trout Over 1.5 Hits +120"')
    print("4. python main.py --mode test")
    print("5. python tests/test_prop_parser.py")
    
    # List all created files
    print("\\n📄 Files created:")
    files = [
        "config.py", "database_manager.py", "prop_parser.py", 
        "data_fetcher.py", "analysis_engine.py", "report_generator.py",
        "main.py", "quick_test.py", "requirements.txt",
        "tests/__init__.py", "tests/test_prop_parser.py"
    ]
    for f in files:
        if os.path.exists(f):
            print(f"✅ {f}")
        else:
            print(f"❌ {f}")

if __name__ == "__main__":
    print("🚀 IMMEDIATE FIX - Creating all files now...")
    print("=" * 50)
    create_files_now()
