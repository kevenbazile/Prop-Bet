#!/usr/bin/env python3
"""
Quick test to verify the system is working
Run this after setting up all the files
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        print("í·ª Testing imports...")
        
        import config
        print("âœ… config.py imported")
        
        from database_manager import DatabaseManager
        print("âœ… database_manager.py imported")
        
        from prop_parser import PropParser
        print("âœ… prop_parser.py imported")
        
        from data_fetcher import DataFetcher
        print("âœ… data_fetcher.py imported")
        
        from analysis_engine import AnalysisEngine
        print("âœ… analysis_engine.py imported")
        
        print("\ní¾‰ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"âŒ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\ní´§ Testing basic functionality...")
        
        # Test prop parser
        from prop_parser import PropParser
        parser = PropParser()
        
        test_prop = "Mike Trout Over 1.5 Hits +120"
        props = parser.parse_manual_input(test_prop)
        
        if props:
            print(f"âœ… Prop parsing works: {props[0]['player_name']}")
        else:
            print("âŒ Prop parsing failed")
            return False
        
        # Test database
        from database_manager import DatabaseManager
        db = DatabaseManager()
        print("âœ… Database initialization works")
        
        print("\ní¾‰ Basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"âŒ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("íº€ Quick Test for Multi-Sport Prop Analysis System")
    print("=" * 50)
    
    import_success = test_imports()
    
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\nâœ… System is ready to use!")
            print("\nRun: python main.py")
        else:
            print("\nâŒ System has functionality issues")
    else:
        print("\nâŒ Import issues - check that all files are created")
