#!/usr/bin/env python3
"""
Quick test to verify the system is working
Run this after setting up all the files
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("ν·ͺ Testing imports...")
        
        import config
        print("β config.py imported")
        
        from database_manager import DatabaseManager
        print("β database_manager.py imported")
        
        from prop_parser import PropParser
        print("β prop_parser.py imported")
        
        from data_fetcher import DataFetcher
        print("β data_fetcher.py imported")
        
        from analysis_engine import AnalysisEngine
        print("β analysis_engine.py imported")
        
        print("\nνΎ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"β Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\nν΄§ Testing basic functionality...")
        
        # Test prop parser
        from prop_parser import PropParser
        parser = PropParser()
        
        test_prop = "Mike Trout Over 1.5 Hits +120"
        props = parser.parse_manual_input(test_prop)
        
        if props:
            print(f"β Prop parsing works: {props[0]['player_name']}")
        else:
            print("β Prop parsing failed")
            return False
        
        # Test database
        from database_manager import DatabaseManager
        db = DatabaseManager()
        print("β Database initialization works")
        
        print("\nνΎ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"β Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("νΊ Quick Test for Multi-Sport Prop Analysis System")
    print("=" * 50)
    
    import_success = test_imports()
    
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\nβ System is ready to use!")
            print("\nRun: python main.py")
        else:
            print("\nβ System has functionality issues")
    else:
        print("\nβ Import issues - check that all files are created")
