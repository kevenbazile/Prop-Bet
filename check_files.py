#!/usr/bin/env python3
"""
check_files.py - Verify all required files exist and have correct content
"""

import os
import sys

def check_file_exists(filename):
    """Check if file exists and show size"""
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"✅ {filename} exists ({size} bytes)")
        return True
    else:
        print(f"❌ {filename} missing")
        return False

def check_file_content(filename, required_text):
    """Check if file contains required text"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if required_text in content:
            print(f"  ✅ Contains required content: {required_text}")
            return True
        else:
            print(f"  ❌ Missing required content: {required_text}")
            return False
    except Exception as e:
        print(f"  ❌ Error reading {filename}: {e}")
        return False

def check_python_syntax(filename):
    """Check if Python file has valid syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, filename, 'exec')
        print(f"  ✅ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"  ❌ Python syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error checking syntax: {e}")
        return False

def main():
    """Check all required files"""
    print("🔍 Multi-Sport Prop Analysis System - File Checker")
    print("=" * 60)
    
    # Required files and their key content
    required_files = {
        'config.py': 'class Config',
        'database_manager.py': 'class DatabaseManager',
        'prop_parser.py': 'class PropParser', 
        'data_fetcher.py': 'class RapidAPIDataFetcher',
        'analysis_engine.py': 'class AnalysisEngine',
        'main.py': 'class PropAnalysisSystem',
        'requirements.txt': 'pandas'
    }
    
    print("\n📁 Checking required files...")
    all_files_good = True
    
    for filename, required_content in required_files.items():
        print(f"\n🔍 Checking {filename}:")
        
        if check_file_exists(filename):
            if filename.endswith('.py'):
                check_python_syntax(filename)
            check_file_content(filename, required_content)
        else:
            all_files_good = False
    
    # Check directories
    print(f"\n📂 Checking directories...")
    required_dirs = ['data', 'tests', 'WagerBrain']
    
    for dirname in required_dirs:
        if os.path.exists(dirname):
            print(f"✅ {dirname}/ directory exists")
            if dirname == 'WagerBrain':
                # Check WagerBrain contents
                contents = os.listdir(dirname)
                print(f"  Contents: {len(contents)} items")
                if any('.py' in item for item in contents):
                    print(f"  ✅ Contains Python files")
                else:
                    print(f"  ⚠️ No Python files found")
        else:
            print(f"⚠️ {dirname}/ directory missing (will be created)")
    
    # Check virtual environment
    print(f"\n🐍 Checking Python environment...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
    else:
        print("⚠️ Virtual environment not detected")
    
    # Check key imports
    print(f"\n📦 Checking key imports...")
    key_imports = ['numpy', 'pandas', 'requests']
    
    for module in key_imports:
        try:
            __import__(module)
            print(f"✅ {module} is available")
        except ImportError:
            print(f"❌ {module} is missing - run: pip install {module}")
            all_files_good = False
    
    # Final summary
    print("\n" + "=" * 60)
    if all_files_good:
        print("🎉 All files look good!")
        print("\n🚀 Try running:")
        print("  python main.py")
        print("  python main.py --mode test")
    else:
        print("❌ Some files are missing or have issues")
        print("\n🔧 Suggested fixes:")
        print("1. Make sure you've copied all the Python files")
        print("2. Check that file names are exactly correct")
        print("3. Run: pip install -r requirements.txt")
        print("4. Make sure you're in the right directory")
    
    print(f"\n📍 Current directory: {os.getcwd()}")
    print(f"📍 Files in directory: {os.listdir('.')}")

if __name__ == "__main__":
    main()