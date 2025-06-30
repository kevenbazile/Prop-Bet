#!/usr/bin/env python3
"""
Quick test to verify the system is working
Run this after setting up all the files
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("� Testing imports...")
        
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
        
        print("\n� All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\n� Testing basic functionality...")
        
        # Test prop parser
        from prop_parser import PropParser
        parser = PropParser()
        
        test_prop = "Mike Trout Over 1.5 Hits +120"
        props = parser.parse_manual_input(test_prop)
        
        if props:
            print(f"✅ Prop parsing works: {props[0]['player_name']}")
        else:
            print("❌ Prop parsing failed")
            return False
        
        # Test database
        from database_manager import DatabaseManager
        db = DatabaseManager()
        print("✅ Database initialization works")
        
        print("\n� Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("� Quick Test for Multi-Sport Prop Analysis System")
    print("=" * 50)
    
    import_success = test_imports()
    
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\n✅ System is ready to use!")
            print("\nRun: python main.py")
        else:
            print("\n❌ System has functionality issues")
    else:
        print("\n❌ Import issues - check that all files are created")
