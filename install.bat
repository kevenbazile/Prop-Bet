install_bat = '''@echo off
echo 🚀 Installing Multi-Sport Prop Analysis System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\\Scripts\\activate

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing requirements...
pip install -r requirements.txt

echo.
echo 🎉 Installation complete!
echo.
echo 📋 Next steps:
echo 1. Copy your .env file or edit .env.template
echo 2. Run: python main.py
echo 3. Or run tests: python tests\\test_prop_parser.py
echo.
pause
'''

