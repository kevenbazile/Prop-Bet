import re
from datetime import datetime
from typing import Dict, List, Optional
from config import Config

class PropParser:
    def __init__(self):
        self.sport_keywords = {
            "MLB": ["baseball", "mlb", "runs", "hits", "strikeouts", "home runs", "rbis", "stolen bases", 
                   "innings", "inning", "era", "whip", "allowed", "walks", "saves", "holds"],
            "NFL": ["football", "nfl", "yards", "touchdowns", "passing", "rushing", "receiving", "receptions",
                   "completions", "attempts", "interceptions", "fumbles", "sacks"],
            "NBA": ["basketball", "nba", "points", "rebounds", "assists", "steals", "blocks", "three pointers",
                   "field goals", "free throws", "turnovers", "minutes"],
            "NHL": ["hockey", "nhl", "goals", "assists", "saves", "shots", "penalty minutes", "hits",
                   "faceoff", "plus minus", "time on ice"],
            "MMA": ["mma", "ufc", "strikes", "takedowns", "submission", "knockdowns", "significant strikes"],
            "BOXING": ["boxing", "punches", "knockdowns", "rounds", "jabs", "power punches"],
            "GOLF": ["golf", "birdies", "eagles", "pars", "bogeys", "driving distance", "fairways",
                    "greens in regulation", "putts"],
            # Esports
            "COD": ["cod", "call of duty", "map", "kills", "deaths", "assists", "kd ratio"],
            "CS2": ["cs2", "counter-strike", "maps", "kills", "deaths", "assists", "adr"],
            "LOL": ["lol", "league of legends", "assists", "kills", "deaths", "cs", "gold"],
            "VAL": ["val", "valorant", "kills", "deaths", "assists", "rounds"],
            "R6": ["r6", "rainbow six", "kills", "deaths", "assists"],
            "DOTA2": ["dota2", "dota", "kills", "deaths", "assists", "last hits"],
            "RL": ["rl", "rocket league", "goals", "saves", "demos", "shots"],
        }

        # Enhanced regex patterns for different prop formats
        self.patterns = [
            # Pattern 1: Standard format - "Mike Trout Over 1.5 Hits +120"
            re.compile(
                r"^(?P<player_name>[A-Za-z .'-]+)\s+"
                r"(?P<bet_type>Over|Under|More|Less|O|U)\s+"
                r"(?P<line_value>\d+(\.\d+)?)\s+"
                r"(?P<prop_type>.+?)"
                r"(?:\s+(?P<odds>[+-]\d+))?$",
                re.IGNORECASE
            ),
            
            # Pattern 2: Complex prop format - "Luis Castillo + Jack Leiter Over 0.5 1st Inning Runs Allowed"
            re.compile(
                r"^(?P<player_name>[A-Za-z .'+&-]+)\s+"
                r"(?P<bet_type>Over|Under|More|Less|O|U)\s+"
                r"(?P<line_value>\d+(\.\d+)?)\s+"
                r"(?P<prop_type>.+?)$",
                re.IGNORECASE
            ),
            
            # Pattern 3: PrizePicks style - "Player Name Prop Type More/Less Line"
            re.compile(
                r"^(?P<player_name>[A-Za-z .'+&-]+)\s+"
                r"(?P<prop_type>(?:1st\s+)?(?:\w+\s+)*\w+)\s+"
                r"(?P<bet_type>More|Less|Over|Under)\s+"
                r"(?P<line_value>\d+(\.\d+)?)$",
                re.IGNORECASE
            ),
            
            # Pattern 4: Reverse order - "Over 1.5 Hits Mike Trout"
            re.compile(
                r"^(?P<bet_type>Over|Under|More|Less|O|U)\s+"
                r"(?P<line_value>\d+(\.\d+)?)\s+"
                r"(?P<prop_type>[A-Za-z0-9 _-]+?)\s+"
                r"(?P<player_name>[A-Za-z .'+&-]+)$",
                re.IGNORECASE
            )
        ]

    def parse_manual_input(self, input_text: str) -> List[Dict]:
        """Parse manually copied prop data"""
        props = []
        lines = input_text.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue
            prop = self.parse_single_prop(line.strip())
            if prop:
                props.append(prop)
        return props

    def parse_single_prop(self, line: str) -> Optional[Dict]:
        """Parse a single prop line using multiple patterns"""
        # Clean up the input
        line = line.strip()
        
        # Try each pattern
        for i, pattern in enumerate(self.patterns):
            match = pattern.match(line)
            if match:
                print(f"✅ Matched pattern {i+1}: {line}")
                return self.extract_prop_data(match, line)
        
        # If no patterns match, try manual parsing for special cases
        return self.manual_parse_fallback(line)

    def manual_parse_fallback(self, line: str) -> Optional[Dict]:
        """Fallback manual parsing for edge cases"""
        # Handle cases like "Luis Castillo + Jack Leiter Over 0.5 1st Inning Runs Allowed"
        parts = line.split()
        
        # Look for Over/Under/More/Less
        direction_words = ['over', 'under', 'more', 'less', 'o', 'u']
        direction_idx = None
        direction = None
        
        for i, part in enumerate(parts):
            if part.lower() in direction_words:
                direction_idx = i
                direction = part.lower()
                break
        
        if direction_idx is None:
            print(f"⚠️ Could not find direction (Over/Under) in: {line}")
            return None
        
        # Look for line value (number after direction)
        line_value = None
        line_value_idx = None
        
        for i in range(direction_idx + 1, len(parts)):
            try:
                line_value = float(parts[i])
                line_value_idx = i
                break
            except ValueError:
                continue
        
        if line_value is None:
            print(f"⚠️ Could not find line value in: {line}")
            return None
        
        # Player name is everything before direction
        player_name = ' '.join(parts[:direction_idx]).strip()
        
        # Prop type is everything after line value
        prop_type = ' '.join(parts[line_value_idx + 1:]).strip() if line_value_idx + 1 < len(parts) else 'unknown'
        
        if not player_name:
            print(f"⚠️ Could not extract player name from: {line}")
            return None
        
        # Create the prop data
        return self.create_prop_dict(player_name, direction, line_value, prop_type, None, line)

    def extract_prop_data(self, match, line: str) -> Dict:
        """Extract prop data from regex match"""
        data = match.groupdict()
        
        player_name = data['player_name'].strip()
        direction = data['bet_type'].lower()
        line_value = float(data['line_value'])
        prop_type = data['prop_type'].strip()
        odds = data.get('odds') if data.get('odds') else None
        
        return self.create_prop_dict(player_name, direction, line_value, prop_type, odds, line)

    def create_prop_dict(self, player_name: str, direction: str, line_value: float, 
                        prop_type: str, odds: Optional[str], raw_input: str) -> Dict:
        """Create standardized prop dictionary"""
        
        # Normalize direction
        if direction in ['more', 'o']:
            direction = 'over'
        elif direction in ['less', 'u']:
            direction = 'under'

        # Detect sport and normalize prop type
        sport = self.detect_sport(prop_type, player_name)
        normalized_prop_type = self.normalize_prop_type(prop_type, sport)

        prop = {
            'player_name': player_name,
            'sport': sport,
            'prop_type': normalized_prop_type,
            'line_value': line_value,
            'bet_type': direction,
            'odds': odds,
            'raw_input': raw_input,
            'original_prop_type': prop_type,  # Keep original for reference
            'parsed_at': datetime.now().isoformat()
        }

        print(f"✅ Parsed: {player_name} {direction} {line_value} {prop_type} ({sport})")
        return prop

    def detect_sport(self, prop_type: str, player_name: str = "") -> str:
        """Detect sport based on prop type and player name"""
        prop_lower = prop_type.lower()
        name_lower = player_name.lower()
        
        # Check for sport-specific keywords in prop type
        for sport, keywords in self.sport_keywords.items():
            for keyword in keywords:
                if keyword in prop_lower:
                    return sport
        
        # Check for known player patterns (you could expand this with a player database)
        # For now, we'll make educated guesses based on common patterns
        if any(word in prop_lower for word in ['inning', 'runs', 'hits', 'strikeouts', 'era']):
            return "MLB"
        elif any(word in prop_lower for word in ['yards', 'touchdowns', 'receptions', 'completions']):
            return "NFL"
        elif any(word in prop_lower for word in ['points', 'rebounds', 'assists', 'field goals']):
            return "NBA"
        elif any(word in prop_lower for word in ['goals', 'saves', 'shots', 'assists']) and 'field goals' not in prop_lower:
            return "NHL"
        
        return "MLB"  # Default to MLB if uncertain

    def normalize_prop_type(self, prop_type: str, sport: str) -> str:
        """Normalize prop type to standard format"""
        prop_lower = prop_type.lower().strip()
        
        # Enhanced normalizations with more specific patterns
        normalizations = {
            # MLB - Enhanced with inning-specific props
            "hits": "hits",
            "runs": "runs",
            "runs allowed": "runs_allowed",
            "1st inning runs allowed": "runs_allowed_1st_inning",
            "first inning runs allowed": "runs_allowed_1st_inning",
            "1st inning runs": "runs_1st_inning",
            "rbis": "rbis", 
            "rbi": "rbis",
            "home runs": "home_runs",
            "home run": "home_runs",
            "hr": "home_runs",
            "strikeouts": "strikeouts",
            "k": "strikeouts",
            "ks": "strikeouts",
            "stolen bases": "stolen_bases",
            "sb": "stolen_bases",
            "walks": "walks",
            "bb": "walks",
            "total bases": "total_bases",
            "tb": "total_bases",
            "era": "era",
            "earned run average": "era",
            "whip": "whip",
            "innings pitched": "innings_pitched",
            "ip": "innings_pitched",
            
            # NFL
            "passing yards": "passing_yards",
            "rushing yards": "rushing_yards", 
            "receiving yards": "receiving_yards",
            "receptions": "receptions",
            "rec": "receptions",
            "touchdowns": "touchdowns",
            "touchdown": "touchdowns",
            "td": "touchdowns",
            "passing touchdowns": "passing_touchdowns",
            "rushing touchdowns": "rushing_touchdowns",
            "receiving touchdowns": "receiving_touchdowns",
            "completions": "completions",
            "comp": "completions",
            "attempts": "attempts",
            "att": "attempts",
            "interceptions": "interceptions",
            "int": "interceptions",
            
            # NBA
            "points": "points",
            "pts": "points",
            "rebounds": "rebounds",
            "reb": "rebounds",
            "assists": "assists",
            "ast": "assists",
            "steals": "steals",
            "stl": "steals",
            "blocks": "blocks",
            "blk": "blocks",
            "three pointers": "three_pointers",
            "threes": "three_pointers",
            "3pm": "three_pointers",
            "field goals": "field_goals",
            "fg": "field_goals",
            "free throws": "free_throws",
            "ft": "free_throws",
            "turnovers": "turnovers",
            "to": "turnovers",
            "double double": "double_double",
            "triple double": "triple_double",
            
            # NHL
            "goals": "goals",
            "assists": "assists",
            "points": "points" if sport != "NBA" else "points",
            "shots": "shots",
            "sog": "shots",
            "saves": "saves",
            "sv": "saves",
            "penalty minutes": "penalty_minutes",
            "pim": "penalty_minutes",
            "hits": "hits" if sport == "NHL" else "hits",
            "blocked shots": "blocked_shots",
            "faceoff wins": "faceoff_wins",
            "fow": "faceoff_wins",
            
            # MMA/Boxing
            "strikes landed": "strikes_landed",
            "significant strikes": "significant_strikes",
            "takedowns": "takedowns",
            "td": "takedowns",
            "submission attempts": "submission_attempts",
            "knockdowns": "knockdowns",
            "punches landed": "punches_landed",
            "rounds won": "rounds_won",
            
            # Golf
            "birdies": "birdies",
            "eagles": "eagles",
            "pars": "pars",
            "bogeys": "bogeys",
            "driving distance": "driving_distance",
            "fairways hit": "fairways_hit",
            "greens in regulation": "greens_in_regulation",
            "gir": "greens_in_regulation",
            "putts": "putts",
            
            # Esports
            "kills": "kills",
            "deaths": "deaths",
            "assists": "assists",
            "maps won": "maps_won",
            "rounds won": "rounds_won",
            "damage": "damage",
            "adr": "adr",
            "kd ratio": "kd_ratio",
            "kda": "kda"
        }
        
        # Direct match first
        if prop_lower in normalizations:
            return normalizations[prop_lower]
        
        # Partial matches for complex props
        for key, value in normalizations.items():
            if key in prop_lower:
                return value
        
        # If no match found, create a normalized version
        normalized = prop_lower.replace(" ", "_").replace("-", "_").replace("'", "").replace("+", "_plus_")
        
        # Clean up multiple underscores
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        
        return normalized.strip("_")

    def parse_csv_format(self, csv_text: str) -> List[Dict]:
        """Parse CSV format props"""
        props = []
        lines = csv_text.strip().split('\n')
        # Skip header if present
        if lines and any(header in lines[0].lower() for header in ['player', 'sport', 'prop']):
            lines = lines[1:]
        for line in lines:
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split(',')]
            if len(parts) >= 4:
                prop = {
                    'player_name': parts[0],
                    'sport': parts[1].upper() if len(parts) > 1 else 'UNKNOWN',
                    'prop_type': parts[2] if len(parts) > 2 else '',
                    'line_value': float(parts[3]) if len(parts) > 3 else 0,
                    'odds_over': parts[4] if len(parts) > 4 else None,
                    'odds_under': parts[5] if len(parts) > 5 else None,
                    'opponent': parts[6] if len(parts) > 6 else None,
                    'game_date': parts[7] if len(parts) > 7 else None,
                    'parsed_at': datetime.now().isoformat()
                }
                props.append(prop)
                print(f"✅ CSV: {prop['player_name']} {prop['prop_type']} {prop['line_value']}")
        return props

    def validate_prop(self, prop: Dict) -> bool:
        """Validate parsed prop data"""
        required_fields = ['player_name', 'sport', 'prop_type', 'line_value']
        for field in required_fields:
            if not prop.get(field):
                print(f"❌ Missing required field: {field}")
                return False
        
        if prop['line_value'] <= 0:
            print(f"❌ Invalid line value: {prop['line_value']}")
            return False
            
        return True

    def batch_parse(self, input_text: str, format_type: str = "auto") -> List[Dict]:
        """Parse multiple props with format detection"""
        if format_type == "auto":
            format_type = self.detect_format(input_text)
        if format_type == "csv":
            return self.parse_csv_format(input_text)
        else:
            return self.parse_manual_input(input_text)

    def detect_format(self, input_text: str) -> str:
        """Auto-detect input format"""
        if "," in input_text and input_text.count(",") > input_text.count(" "):
            return "csv"
        else:
            return "standard"

    def analyze_bet(self, prop: Dict, payout_multiplier: float, book_odds: float) -> Dict:
        """Analyze bet for +EV opportunities"""
        implied_prob = self.calculate_implied_probability(book_odds)
        edge = None
        if payout_multiplier:
            edge = prop.get('confidence_score', 0) - implied_prob
            if edge > 0:
                print(f"🟢 +EV Bet! Your edge: {edge:.2%}")
            else:
                print(f"🔴 No edge. Your edge: {edge:.2%}")
        return {
            'implied_probability': implied_prob,
            'edge': edge
        }

    def calculate_implied_probability(self, odds: float) -> float:
        """Calculate implied probability from odds"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return -odds / (-odds + 100)

    def debug_parse(self, line: str) -> Dict:
        """Debug parsing - shows detailed breakdown"""
        print(f"\n🔍 DEBUG PARSING: '{line}'")
        print(f"Length: {len(line)} characters")
        
        # Test each pattern
        for i, pattern in enumerate(self.patterns):
            match = pattern.match(line)
            if match:
                print(f"✅ Pattern {i+1} matched!")
                groups = match.groupdict()
                for key, value in groups.items():
                    print(f"   {key}: '{value}'")
                return self.extract_prop_data(match, line)
            else:
                print(f"❌ Pattern {i+1} no match")
        
        # Try fallback
        print("🔄 Trying fallback parser...")
        result = self.manual_parse_fallback(line)
        if result:
            print("✅ Fallback parser succeeded!")
        else:
            print("❌ Fallback parser failed")
        
        return result

# Test the updated parser
if __name__ == "__main__":
    parser = PropParser()
    
    # Test cases
    test_props = [
        "Luis Castillo + Jack Leiter Over 0.5 1st Inning Runs Allowed",
        "Mike Trout Over 1.5 Hits +120",
        "Patrick Mahomes More 2.5 Passing Touchdowns",
        "LeBron James Under 25.5 Points -110",
        "Connor McDavid Over 0.5 Goals +150"
    ]
    
    print("🧪 Testing Updated PropParser...")
    for prop_text in test_props:
        print(f"\n📝 Testing: {prop_text}")
        result = parser.parse_single_prop(prop_text)
        if result:
            print(f"   ✅ Success: {result['player_name']} {result['bet_type']} {result['line_value']} {result['prop_type']}")
        else:
            print("   ❌ Failed to parse")
            # Run debug if it fails
            parser.debug_parse(prop_text)