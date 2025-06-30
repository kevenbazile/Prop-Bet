import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prop_parser import PropParser
from config import Config

class TestPropParser(unittest.TestCase):
    def setUp(self):
        self.parser = PropParser()
    
    def test_parse_mlb_prop(self):
        """Test parsing MLB prop"""
        input_text = "Mike Trout Over 1.5 Hits +120"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Mike Trout")
        self.assertEqual(prop['sport'], "MLB")
        self.assertEqual(prop['prop_type'], "hits")
        self.assertEqual(prop['line_value'], 1.5)
        self.assertEqual(prop['bet_type'], "over")
    
    def test_parse_nfl_prop(self):
        """Test parsing NFL prop"""
        input_text = "Patrick Mahomes Over 275.5 Passing Yards +110"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Patrick Mahomes")
        self.assertEqual(prop['sport'], "NFL")
        self.assertEqual(prop['prop_type'], "passing_yards")
        self.assertEqual(prop['line_value'], 275.5)
    
    def test_parse_nba_prop(self):
        """Test parsing NBA prop"""
        input_text = "LeBron James Under 25.5 Points -110"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "LeBron James")
        self.assertEqual(prop['sport'], "NBA")
        self.assertEqual(prop['prop_type'], "points")
        self.assertEqual(prop['line_value'], 25.5)
        self.assertEqual(prop['bet_type'], "under")
    
    def test_parse_nhl_prop(self):
        """Test parsing NHL prop"""
        input_text = "Connor McDavid Over 0.5 Goals +150"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Connor McDavid")
        self.assertEqual(prop['sport'], "NHL")
        self.assertEqual(prop['prop_type'], "goals")
        self.assertEqual(prop['line_value'], 0.5)
    
    def test_parse_mma_prop(self):
        """Test parsing MMA prop"""
        input_text = "Jon Jones Over 2.5 Takedowns +200"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Jon Jones")
        self.assertEqual(prop['sport'], "MMA")
        self.assertEqual(prop['prop_type'], "takedowns")
        self.assertEqual(prop['line_value'], 2.5)
    
    def test_parse_golf_prop(self):
        """Test parsing Golf prop"""
        input_text = "Tiger Woods Over 3.5 Birdies -120"
        props = self.parser.parse_manual_input(input_text)
        
        self.assertEqual(len(props), 1)
        prop = props[0]
        self.assertEqual(prop['player_name'], "Tiger Woods")
        self.assertEqual(prop['sport'], "GOLF")
        self.assertEqual(prop['prop_type'], "birdies")
        self.assertEqual(prop['line_value'], 3.5)
    
    def test_parse_multiple_props(self):
        """Test parsing multiple props"""
        input_text = """Mike Trout Over 1.5 Hits +120
Patrick Mahomes Over 275.5 Passing Yards +110
LeBron James Under 25.5 Points -110"""
        
        props = self.parser.parse_manual_input(input_text)
        self.assertEqual(len(props), 3)
        
        # Check each sport was detected correctly
        sports = [prop['sport'] for prop in props]
        self.assertIn('MLB', sports)
        self.assertIn('NFL', sports)
        self.assertIn('NBA', sports)
    
    def test_invalid_prop(self):
        """Test handling invalid prop format"""
        input_text = "Invalid prop format"
        props = self.parser.parse_manual_input(input_text)
        self.assertEqual(len(props), 0)
    
    def test_sport_detection(self):
        """Test sport detection logic"""
        self.assertEqual(self.parser.detect_sport("hits"), "MLB")
        self.assertEqual(self.parser.detect_sport("passing yards"), "NFL") 
        self.assertEqual(self.parser.detect_sport("points"), "NBA")
        self.assertEqual(self.parser.detect_sport("goals"), "NHL")
        self.assertEqual(self.parser.detect_sport("takedowns"), "MMA")
        self.assertEqual(self.parser.detect_sport("birdies"), "GOLF")
        self.assertEqual(self.parser.detect_sport("unknown stat"), "UNKNOWN")
    
    def test_prop_validation(self):
        """Test prop validation"""
        valid_prop = {
            'player_name': 'Test Player',
            'sport': 'MLB',
            'prop_type': 'hits',
            'line_value': 1.5
        }
        self.assertTrue(self.parser.validate_prop(valid_prop))
        
        # Test invalid prop - missing player name
        invalid_prop = {
            'sport': 'MLB',
            'prop_type': 'hits',
            'line_value': 1.5
        }
        self.assertFalse(self.parser.validate_prop(invalid_prop))
        
        # Test invalid prop - zero line value
        invalid_prop2 = {
            'player_name': 'Test Player',
            'sport': 'MLB', 
            'prop_type': 'hits',
            'line_value': 0
        }
        self.assertFalse(self.parser.validate_prop(invalid_prop2))
    
    def test_csv_parsing(self):
        """Test CSV format parsing"""
        csv_text = """Player,Sport,PropType,Line,OverOdds,UnderOdds
Mike Trout,MLB,hits,1.5,+120,-140
Patrick Mahomes,NFL,passing_yards,275.5,+110,-110"""
        
        props = self.parser.parse_csv_format(csv_text)
        self.assertEqual(len(props), 2)
        
        self.assertEqual(props[0]['player_name'], 'Mike Trout')
        self.assertEqual(props[0]['sport'], 'MLB')
        self.assertEqual(props[1]['player_name'], 'Patrick Mahomes')
        self.assertEqual(props[1]['sport'], 'NFL')

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPropParser)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\\n{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if not result.failures and not result.errors:
        print("\\n✅ All tests passed!")
    else:
        print(f"\\n❌ {len(result.failures + result.errors)} tests failed")
