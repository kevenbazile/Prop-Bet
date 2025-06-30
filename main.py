import sys
import argparse
import os
from datetime import datetime
import requests

print("🚀 Starting Multi-Sport Prop Analysis System...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

# Test imports one by one
print("\n📦 Testing imports...")

try:
    print("  Importing database_manager...")
    from database_manager import DatabaseManager
    print("  ✅ DatabaseManager imported")
except Exception as e:
    print(f"  ❌ DatabaseManager import failed: {e}")
    sys.exit(1)

try:
    print("  Importing prop_parser...")
    from prop_parser import PropParser
    print("  ✅ PropParser imported")
except Exception as e:
    print(f"  ❌ PropParser import failed: {e}")
    sys.exit(1)

try:
    print("  Importing data_fetcher...")
    from data_fetcher import RapidAPIDataFetcher
    print("  ✅ RapidAPIDataFetcher imported")
except Exception as e:
    print(f"  ❌ RapidAPIDataFetcher import failed: {e}")
    sys.exit(1)

try:
    print("  Importing analysis_engine...")
    from analysis_engine import WagerBrainAnalysisEngine as AnalysisEngine
    print("  ✅ AnalysisEngine imported")
except Exception as e:
    print(f"  ❌ AnalysisEngine import failed: {e}")
    sys.exit(1)

try:
    print("  Importing config...")
    from config import Config
    print("  ✅ Config imported")
except Exception as e:
    print(f"  ❌ Config import failed: {e}")
    sys.exit(1)

print("\n🏗️ All imports successful! Creating system...")

class PropAnalysisSystem:
    def __init__(self):
        print("🔧 Initializing PropAnalysisSystem...")
        
        try:
            print("  Creating DatabaseManager...")
            self.db = DatabaseManager()
            print("  ✅ DatabaseManager created")
        except Exception as e:
            print(f"  ❌ DatabaseManager creation failed: {e}")
            raise
        
        try:
            print("  Creating PropParser...")
            self.parser = PropParser()
            print("  ✅ PropParser created")
        except Exception as e:
            print(f"  ❌ PropParser creation failed: {e}")
            raise
            
        try:
            print("  Creating RapidAPIDataFetcher...")
            self.fetcher = RapidAPIDataFetcher()
            print("  ✅ RapidAPIDataFetcher created")
        except Exception as e:
            print(f"  ❌ RapidAPIDataFetcher creation failed: {e}")
            raise
            
        try:
            print("  Creating AnalysisEngine...")
            self.analyzer = AnalysisEngine()
            print("  ✅ AnalysisEngine created")
        except Exception as e:
            print(f"  ❌ AnalysisEngine creation failed: {e}")
            raise
        
        print("✅ System initialized successfully!")
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        print("\n🧪 Testing basic functionality...")
        
        try:
            # Test prop parsing
            test_prop = "Mike Trout Over 1.5 Hits +120"
            print(f"  Testing prop: {test_prop}")
            props = self.parser.parse_manual_input(test_prop)
            
            if props:
                prop = props[0]
                print(f"  ✅ Parsed: {prop['player_name']} {prop['prop_type']} {prop['line_value']}")
                
                # Test database
                prop_id = self.db.add_prop(prop)
                print(f"  ✅ Added to database with ID: {prop_id}")
                
                # Test analysis (basic)
                player_stats = {
                    'recent_averages': {
                        'avg_hits': 1.2
                    }
                }
                
                analysis = self.analyzer.analyze_prop(prop, player_stats)
                print(f"  ✅ Analysis complete: {analysis['recommendation']}")
                print(f"  🔎 Analysis details: {analysis}")
                
            else:
                print("  ❌ Prop parsing failed")
                
        except Exception as e:
            print(f"  ❌ Basic functionality test failed: {e}")
            raise
    
    def interactive_mode(self):
        """Interactive CLI mode"""
        print("\n🚀 Starting Interactive Mode")
        print("=" * 60)
        print("Enter props to analyze (or commands):")
        print("💡 Example: 'Mike Trout Over 1.5 Hits +120'")
        print("📋 Commands: 'test', 'help', 'quit'")
        print("-" * 60)
        
        while True:
            try:
                prop_text = input("\n📝 Enter prop or command: ").strip()
                
                if prop_text.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if prop_text.lower() == 'test':
                    self.test_basic_functionality()
                    continue
                
                if prop_text.lower() == 'help':
                    print("\n📚 Available commands:")
                    print("  test - Run basic functionality test")
                    print("  help - Show this help")
                    print("  quit - Exit")
                    print("  Or enter a prop like: 'Mike Trout Over 1.5 Hits +120'")
                    continue
                
                if prop_text:
                    print(f"🔍 Analyzing: {prop_text}")
                    props = self.parser.parse_manual_input(prop_text)
                    if props:
                        prop = props[0]
                        print(f"✅ Parsed successfully: {prop}")
                        # Ask for PrizePicks payout multiplier
                        try:
                            payout_input = input("Enter PrizePicks payout multiplier (e.g., 3 for 2-pick Power Play): ").strip()
                            payout_multiplier = float(payout_input)
                            implied_prob, american_odds = self.payout_to_implied_odds(payout_multiplier)
                            print(f"💰 PrizePicks Implied Probability: {implied_prob:.2%} | Implied Odds: {american_odds:+}")
                        except Exception as e:
                            print(f"⚠️ Could not calculate implied odds: {e}")
                            payout_multiplier = None
                        # Add to database
                        try:
                            prop_id = self.db.add_prop(prop)
                            print(f"  ✅ Added to database with ID: {prop_id}")
                        except Exception as db_e:
                            print(f"  ⚠️ Database add failed: {db_e}")
                        # Fetch player stats from API
                        try:
                            player_stats = self.fetcher.fetch_player_stats(
                                prop['player_name'],
                                prop['sport']
                            )
                            print(f"🌐 API player stats: {player_stats}")  # Show API response
                            if not player_stats:
                                print("❌ No player stats returned from API. Cannot analyze.")
                                continue
                        except Exception as fetch_e:
                            print(f"❌ API fetch failed: {fetch_e}")
                            continue
                        # Analyze
                        try:
                            analysis = self.analyzer.analyze_prop(prop, player_stats)
                            print(f"  ✅ Analysis complete: {analysis['recommendation']}")
                            print(f"  🔎 Analysis details: {analysis}")
                        except Exception as ana_e:
                            print(f"  ❌ Analysis failed: {ana_e}")
                    else:
                        print("❌ Could not parse prop")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def payout_to_implied_odds(self, payout_multiplier):
        implied_prob = 1 / payout_multiplier
        if implied_prob > 0.5:
            american_odds = -100 * (implied_prob / (1 - implied_prob))
        else:
            american_odds = 100 * ((1 - implied_prob) / implied_prob)
        return implied_prob, round(american_odds)

def main():
    """Main entry point with debug output"""
    print("\n🎯 Main function starting...")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Multi-Sport Prop Analysis System (DEBUG)')
    parser.add_argument('--mode', choices=['interactive', 'test'], 
                       default='interactive', help='Run mode')
    parser.add_argument('--prop', help='Analyze a single prop')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    try:
        args = parser.parse_args()
        print(f"  Arguments parsed: mode={args.mode}")
    except Exception as e:
        print(f"❌ Argument parsing failed: {e}")
        return
    
    # Initialize system
    try:
        print("  Creating PropAnalysisSystem...")
        system = PropAnalysisSystem()
        print("  ✅ PropAnalysisSystem created successfully")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return
    
    # Handle different modes
    try:
        if args.prop:
            print(f"  Analyzing single prop: {args.prop}")
            props = system.parser.parse_manual_input(args.prop)
            if props:
                print(f"  ✅ Prop parsed: {props[0]}")
            else:
                print("  ❌ Could not parse prop")
            return
        
        if args.mode == 'test':
            print("  Running test mode...")
            system.test_basic_functionality()
            return
        else:
            print("  Starting interactive mode...")
            system.interactive_mode()
            
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🐛 DEBUG VERSION - Multi-Sport Prop Analysis System")
    print("=" * 60)
    
    try:
        main()
    except Exception as e:
        print(f"\n💥 FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 Program ending...")
