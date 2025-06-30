#!/bin/bash

echo "ÌæÆ Multi-Sport Prop Analysis System - Usage Examples"
echo "=================================================="
echo ""

echo "Ì≥ä 1. INTERACTIVE MODE (Default)"
echo "   python main.py"
echo "   # Enter props manually, type 'help' for commands"
echo ""

echo "ÌæØ 2. ANALYZE SINGLE PROP"
echo "   python main.py --prop \"Mike Trout Over 1.5 Hits +120\""
echo "   python main.py --prop \"Patrick Mahomes Over 275.5 Passing Yards +110\""
echo "   python main.py --prop \"LeBron James Under 25.5 Points -110\""
echo ""

echo "Ì¥ñ 3. RUN TELEGRAM BOT"
echo "   python main.py --mode telegram"
echo "   # Requires TELEGRAM_BOT_TOKEN in .env"
echo ""

echo "Ì≥à 4. GENERATE DAILY REPORT"
echo "   python main.py --report"
echo ""

echo "Ì∑™ 5. RUN TEST MODE"
echo "   python main.py --mode test"
echo "   # Runs with sample test data"
echo ""

echo "Ì¥¨ 6. RUN TESTS"
echo "   python tests/test_prop_parser.py"
echo "   python -m pytest tests/"
echo "   python -m pytest tests/ --cov=."
echo ""

echo "Ì≤° INTERACTIVE MODE COMMANDS:"
echo "   - Enter any prop text to analyze"
echo "   - 'report' - Show daily report"
echo "   - 'help' - Show help"
echo "   - 'quit' - Exit"
echo ""

echo "Ì≥ù PROP FORMAT EXAMPLES:"
echo "   \"Mike Trout Over 1.5 Hits +120\""
echo "   \"Patrick Mahomes Over 275.5 Passing Yards +110\""
echo "   \"LeBron James Under 25.5 Points -110\""
echo "   \"Connor McDavid Over 0.5 Goals -150\""
echo ""
