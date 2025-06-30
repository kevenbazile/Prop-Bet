import sys
import os

print("🔍 DEBUGGING WAGERBRAIN STRUCTURE")
print("=" * 50)

# Check current directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Check if WagerBrain folder exists
wb_folder = os.path.join(current_dir, "WagerBrain")
wb_nested = os.path.join(current_dir, "WagerBrain", "WagerBrain")

print(f"\nFolder checks:")
print(f"WagerBrain folder exists: {os.path.exists(wb_folder)}")
print(f"WagerBrain/WagerBrain folder exists: {os.path.exists(wb_nested)}")

if os.path.exists(wb_folder):
    print(f"\nContents of WagerBrain/:")
    for item in os.listdir(wb_folder):
        print(f"  - {item}")

if os.path.exists(wb_nested):
    print(f"\nContents of WagerBrain/WagerBrain/:")
    for item in os.listdir(wb_nested):
        print(f"  - {item}")
    
    # Check __init__.py specifically
    init_file = os.path.join(wb_nested, "__init__.py")
    print(f"\n__init__.py check:")
    print(f"  Exists: {os.path.exists(init_file)}")
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
        print(f"  Size: {len(content)} characters")
        print(f"  First 200 chars: {content[:200]}")

# Check Python path
print(f"\nPython path (first 5 entries):")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

# Check what happens when we add to path
print(f"\nTrying to add paths...")
if wb_folder not in sys.path:
    sys.path.insert(0, wb_folder)
    print(f"Added WagerBrain folder to path")

if wb_nested not in sys.path:
    sys.path.insert(0, wb_nested)
    print(f"Added WagerBrain/WagerBrain to path")

# Try different import methods
print(f"\nTesting imports:")

# Method 1: Direct WagerBrain import
try:
    import WagerBrain
    print("✅ 1. 'import WagerBrain' worked!")
    print(f"   WagerBrain location: {WagerBrain.__file__}")
    print(f"   WagerBrain contents: {dir(WagerBrain)}")
except Exception as e:
    print(f"❌ 1. 'import WagerBrain' failed: {e}")

# Method 2: From WagerBrain import specific function
try:
    from WagerBrain import implied_probability
    print("✅ 2. 'from WagerBrain import implied_probability' worked!")
    prob = implied_probability('-110')
    print(f"   Test result: {prob}")
except Exception as e:
    print(f"❌ 2. 'from WagerBrain import implied_probability' failed: {e}")

# Method 3: Direct module imports
try:
    import bankroll
    print("✅ 3. 'import bankroll' worked!")
    print(f"   bankroll contents: {[x for x in dir(bankroll) if not x.startswith('_')]}")
except Exception as e:
    print(f"❌ 3. 'import bankroll' failed: {e}")

try:
    import odds
    print("✅ 4. 'import odds' worked!")
    print(f"   odds contents: {[x for x in dir(odds) if not x.startswith('_')]}")
except Exception as e:
    print(f"❌ 4. 'import odds' failed: {e}")

# Method 4: Check what pip thinks is installed
print(f"\nChecking pip installations:")
try:
    import pkg_resources
    installed = list(pkg_resources.working_set)
    wagerbrain_packages = [pkg for pkg in installed if 'wager' in pkg.project_name.lower()]
    print(f"Packages with 'wager': {[pkg.project_name for pkg in wagerbrain_packages]}")
    
    if wagerbrain_packages:
        for pkg in wagerbrain_packages:
            print(f"  {pkg.project_name} {pkg.version} at {pkg.location}")
except Exception as e:
    print(f"Error checking pip packages: {e}")

# Method 5: Manual function test
print(f"\nTrying manual function creation:")
try:
    def test_implied_probability(odds):
        odds_value = int(str(odds).replace('+', ''))
        if odds_value > 0:
            return 100 / (odds_value + 100)
        else:
            return abs(odds_value) / (abs(odds_value) + 100)
    
    test_result = test_implied_probability('-110')
    print(f"✅ Manual function works: {test_result}")
except Exception as e:
    print(f"❌ Manual function failed: {e}")

print("\n" + "=" * 50)
print("DEBUG COMPLETE - Check output above for issues!")