import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class MultiAPIDataFetcher:
    """Enhanced data fetcher that uses ALL your configured APIs"""
    
    def __init__(self):
        self.config = Config()
        self.rate_limit_delay = self.config.REQUEST_DELAY
        self.last_request_time = {}  # Track last request time per API
        
        # API priority order for each sport (primary, secondary, fallback)
        self.api_priority = {
            'MLB': ['MLB', 'NBASZN'],  # Use MLB API first, NBA season as backup
            'NFL': ['NFL', 'NFLSZN'],
            'NBA': ['NBA', 'NBASZN'], 
            'NHL': ['NHL'],
            'Soccer': ['Soccer'],
            'Tennis': ['Tennis'],
            'MMA': ['MMA'],
            'Boxing': ['Boxing'],
            'PGA': ['PGA'],
            'COD': ['COD'],
            'Darts': ['Darts'],
            'Cricket': ['Cricket'],
            'TableTennis': ['TableTennis'],
            'Nascar': ['Nascar'],
            'F1': ['F1']
        }
        
        # Prop type to sport API mapping
        self.prop_sport_mapping = {
            # MLB Props
            'hits': 'MLB',
            'runs': 'MLB', 
            'rbis': 'MLB',
            'home_runs': 'MLB',
            'strikeouts': 'MLB',
            'runs_allowed': 'MLB',
            'runs_allowed_1st_inning': 'MLB',
            'total_bases': 'MLB',
            'stolen_bases': 'MLB',
            'walks': 'MLB',
            'doubles': 'MLB',
            'singles': 'MLB',
            'triples': 'MLB',
            'earned_runs_allowed': 'MLB',
            
            # NFL Props
            'passing_yards': 'NFL',
            'rushing_yards': 'NFL', 
            'receiving_yards': 'NFL',
            'receptions': 'NFL',
            'touchdowns': 'NFL',
            'passing_touchdowns': 'NFL',
            'rushing_touchdowns': 'NFL',
            'receiving_touchdowns': 'NFL',
            'completions': 'NFL',
            'attempts': 'NFL',
            'interceptions': 'NFL',
            'sacks': 'NFLSZN',
            
            # NBA Props
            'points': 'NBA',
            'rebounds': 'NBA',
            'assists': 'NBA',
            'steals': 'NBA',
            'blocks': 'NBA',
            'three_pointers': 'NBA',
            'field_goals': 'NBA',
            'free_throws': 'NBA',
            'turnovers': 'NBA',
            
            # NHL Props
            'goals': 'NHL',
            'saves': 'NHL',
            'shots': 'NHL',
            'penalty_minutes': 'NHL',
            
            # Soccer Props
            'goals_soccer': 'Soccer',
            'assists_soccer': 'Soccer',
            'shots_soccer': 'Soccer',
            'cards': 'Soccer',
            'saves_soccer': 'Soccer',
            
            # Combat Sports
            'strikes_landed': 'MMA',
            'takedowns': 'MMA',
            'significant_strikes': 'MMA',
            'punches_landed': 'Boxing',
            'knockdowns': 'Boxing',
            
            # Golf
            'birdies': 'PGA',
            'eagles': 'PGA',
            'strokes': 'PGA',
            'greens_in_regulation': 'PGA',
            
            # Esports
            'kills': 'COD',
            'deaths': 'COD',
            'maps_won': 'COD',
            
            # Other Sports
            '180s_thrown': 'Darts',
            'fours': 'Cricket',
            'sixers': 'Cricket',
            'fastest_lap': 'Nascar',
            'laps_led': 'Nascar',
            'points_scored': 'F1'
        }
    
    def fetch_player_stats(self, player_name: str, sport: str, prop_type: str = None, days: int = 30) -> Dict:
        """Fetch player stats using the most appropriate API"""
        print(f"🔍 Fetching stats for {player_name} ({sport})")
        
        # Determine best API to use
        api_sport = self._determine_best_api(sport, prop_type)
        
        # Try APIs in priority order
        apis_to_try = self.api_priority.get(sport.upper(), [sport.upper()])
        
        for api_sport_key in apis_to_try:
            try:
                data = self._fetch_from_api(player_name, api_sport_key, days)
                if data and self._validate_player_data(data):
                    print(f"✅ Got data from {api_sport_key} API")
                    return self._normalize_player_data(data, player_name, sport, api_sport_key)
            except Exception as e:
                print(f"⚠️ {api_sport_key} API failed: {e}")
                continue
        
        # All APIs failed, use enhanced fallback
        print(f"🔄 All APIs failed, using enhanced fallback")
        return self._create_enhanced_fallback_data(player_name, sport, prop_type)
    
    def _determine_best_api(self, sport: str, prop_type: str = None) -> str:
        """Determine the best API to use based on sport and prop type"""
        if prop_type and prop_type in self.prop_sport_mapping:
            return self.prop_sport_mapping[prop_type]
        return sport.upper()
    
    def _fetch_from_api(self, player_name: str, api_sport_key: str, days: int = 30) -> Optional[Dict]:
        """Fetch data from specific API"""
        sport_config = self.config.SUPPORTED_SPORTS.get(api_sport_key)
        if not sport_config:
            print(f"❌ No config found for {api_sport_key}")
            return None
        
        api_key = sport_config.get("api_key")
        api_host = sport_config.get("api_host") 
        endpoint = sport_config.get("endpoint")
        
        if not all([api_key, api_host, endpoint]):
            print(f"❌ Missing API config for {api_sport_key}")
            return None
        
        # Rate limiting
        self._enforce_rate_limit(api_host)
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": api_host,
            "User-Agent": "PropBot/2.0"
        }
        
        # Enhanced parameters based on API
        params = self._build_api_params(player_name, api_sport_key, days)
        
        try:
            print(f"🌐 Making API request to {api_sport_key}: {endpoint}")
            response = requests.get(endpoint, headers=headers, params=params, timeout=15)
            
            # Update rate limit tracking
            self.last_request_time[api_host] = time.time()
            
            print(f"📡 {api_sport_key} API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {api_sport_key} API data received for {player_name}")
                return self._process_api_response(data, api_sport_key)
            elif response.status_code == 429:
                print(f"⚠️ {api_sport_key} API rate limit exceeded")
                time.sleep(5)  # Wait longer for rate limit
                return None
            elif response.status_code == 404:
                print(f"⚠️ Player '{player_name}' not found in {api_sport_key} API")
                return None
            else:
                print(f"❌ {api_sport_key} API error: {response.status_code} - {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"⚠️ {api_sport_key} API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            print(f"⚠️ {api_sport_key} API connection error")
            return None
        except Exception as e:
            print(f"❌ {api_sport_key} API request failed: {e}")
            return None
    
    def _enforce_rate_limit(self, api_host: str):
        """Enforce rate limiting per API host"""
        if api_host in self.last_request_time:
            time_since_last = time.time() - self.last_request_time[api_host]
            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                print(f"⏳ Rate limiting: sleeping {sleep_time:.1f}s for {api_host}")
                time.sleep(sleep_time)
    
    def _build_api_params(self, player_name: str, api_sport_key: str, days: int) -> Dict:
        """Build API parameters based on the specific API"""
        base_params = {
            "name": player_name,
            "search": player_name
        }
        
        # API-specific parameters
        if api_sport_key in ['MLB', 'NFL', 'NBA', 'NHL']:
            base_params.update({
                "season": "2024",
                "league": api_sport_key,
                "days": days
            })
        elif api_sport_key == 'Soccer':
            base_params.update({
                "season": "2024",
                "league": "39"  # Premier League, adjust as needed
            })
        elif api_sport_key in ['MMA', 'Boxing']:
            base_params.update({
                "limit": "20"
            })
        elif api_sport_key == 'PGA':
            base_params.update({
                "tournament": "current",
                "year": "2024"
            })
        elif api_sport_key == 'COD':
            base_params.update({
                "platform": "battle",
                "mode": "mp"
            })
        elif api_sport_key in ['Tennis', 'Darts', 'Cricket']:
            base_params.update({
                "season": "2024"
            })
        elif api_sport_key in ['Nascar', 'F1']:
            base_params.update({
                "season": "2024",
                "round": "current"
            })
        
        return base_params
    
    def _process_api_response(self, data: Dict, api_sport_key: str) -> Dict:
        """Process API response based on the specific API format"""
        # Each API returns data in different formats
        # This method standardizes the response
        
        if api_sport_key == 'MLB':
            return self._process_mlb_response(data)
        elif api_sport_key in ['NFL', 'NFLSZN']:
            return self._process_nfl_response(data)
        elif api_sport_key in ['NBA', 'NBASZN']:
            return self._process_nba_response(data)
        elif api_sport_key == 'NHL':
            return self._process_nhl_response(data)
        elif api_sport_key == 'Soccer':
            return self._process_soccer_response(data)
        elif api_sport_key == 'Tennis':
            return self._process_tennis_response(data)
        elif api_sport_key == 'MMA':
            return self._process_mma_response(data)
        elif api_sport_key == 'Boxing':
            return self._process_boxing_response(data)
        elif api_sport_key == 'PGA':
            return self._process_golf_response(data)
        elif api_sport_key == 'COD':
            return self._process_cod_response(data)
        elif api_sport_key == 'Darts':
            return self._process_darts_response(data)
        elif api_sport_key == 'Cricket':
            return self._process_cricket_response(data)
        elif api_sport_key in ['Nascar', 'F1']:
            return self._process_racing_response(data)
        else:
            # Generic processing
            return data
    
    def _process_mlb_response(self, data: Dict) -> Dict:
        """Process MLB API response"""
        # Extract relevant MLB stats
        if isinstance(data, dict) and 'response' in data:
            players = data['response']
            if players and len(players) > 0:
                player = players[0]
                
                # Extract statistics
                stats = player.get('statistics', [])
                if stats:
                    latest_stats = stats[0] if isinstance(stats, list) else stats
                    
                    return {
                        'player_info': player,
                        'stats': latest_stats,
                        'games': latest_stats.get('games', {}),
                        'batting': latest_stats.get('batting', {}),
                        'pitching': latest_stats.get('pitching', {}),
                        'api_source': 'MLB'
                    }
        
        return data
    
    def _process_nfl_response(self, data: Dict) -> Dict:
        """Process NFL API response"""
        if isinstance(data, dict) and 'response' in data:
            players = data['response']
            if players and len(players) > 0:
                player = players[0]
                
                return {
                    'player_info': player,
                    'stats': player.get('statistics', {}),
                    'passing': player.get('passing', {}),
                    'rushing': player.get('rushing', {}),
                    'receiving': player.get('receiving', {}),
                    'api_source': 'NFL'
                }
        
        return data
    
    def _process_nba_response(self, data: Dict) -> Dict:
        """Process NBA API response"""
        if isinstance(data, dict) and 'response' in data:
            players = data['response']
            if players and len(players) > 0:
                player = players[0]
                
                return {
                    'player_info': player,
                    'stats': player.get('statistics', {}),
                    'games': player.get('games', {}),
                    'api_source': 'NBA'
                }
        
        return data
    
    def _process_nhl_response(self, data: Dict) -> Dict:
        """Process NHL API response"""
        return {'api_source': 'NHL', 'raw_data': data}
    
    def _process_soccer_response(self, data: Dict) -> Dict:
        """Process Soccer API response"""
        return {'api_source': 'Soccer', 'raw_data': data}
    
    def _process_tennis_response(self, data: Dict) -> Dict:
        """Process Tennis API response"""
        return {'api_source': 'Tennis', 'raw_data': data}
    
    def _process_mma_response(self, data: Dict) -> Dict:
        """Process MMA API response"""
        return {'api_source': 'MMA', 'raw_data': data}
    
    def _process_boxing_response(self, data: Dict) -> Dict:
        """Process Boxing API response"""
        return {'api_source': 'Boxing', 'raw_data': data}
    
    def _process_golf_response(self, data: Dict) -> Dict:
        """Process Golf API response"""
        return {'api_source': 'PGA', 'raw_data': data}
    
    def _process_cod_response(self, data: Dict) -> Dict:
        """Process Call of Duty API response"""
        return {'api_source': 'COD', 'raw_data': data}
    
    def _process_darts_response(self, data: Dict) -> Dict:
        """Process Darts API response"""
        return {'api_source': 'Darts', 'raw_data': data}
    
    def _process_cricket_response(self, data: Dict) -> Dict:
        """Process Cricket API response"""
        return {'api_source': 'Cricket', 'raw_data': data}
    
    def _process_racing_response(self, data: Dict) -> Dict:
        """Process Racing (NASCAR/F1) API response"""
        return {'api_source': 'Racing', 'raw_data': data}
    
    def _validate_player_data(self, data: Dict) -> bool:
        """Validate that player data is usable"""
        if not data:
            return False
        
        # Check if we have some kind of player information
        return True  # For now, accept any non-empty response
    
    def _normalize_player_data(self, data: Dict, player_name: str, sport: str, api_source: str) -> Dict:
        """Normalize player data from any API to our standard format"""
        normalized = {
            'player_name': player_name,
            'sport': sport.upper(),
            'recent_averages': {},
            'games_played': 15,
            'total_games': 30,
            'last_updated': datetime.now().isoformat(),
            'data_source': f'api_{api_source}',
            'api_source': api_source,
            'raw_data': data  # Keep raw data for debugging
        }
        
        # Sport-specific normalization
        if sport.upper() == 'MLB':
            normalized['recent_averages'] = self._extract_mlb_averages(data)
        elif sport.upper() == 'NFL':
            normalized['recent_averages'] = self._extract_nfl_averages(data)
        elif sport.upper() == 'NBA':
            normalized['recent_averages'] = self._extract_nba_averages(data)
        elif sport.upper() == 'NHL':
            normalized['recent_averages'] = self._extract_nhl_averages(data)
        else:
            # Generic extraction
            normalized['recent_averages'] = self._extract_generic_averages(data, sport)
        
        return normalized
    
    def _extract_mlb_averages(self, data: Dict) -> Dict:
        """Extract MLB averages from API data"""
        averages = {}
        
        # Try to extract from different possible structures
        if 'batting' in data:
            batting = data['batting']
            averages.update({
                'avg_hits': batting.get('hits_per_game', batting.get('hits', 0)) / max(batting.get('games', 1), 1),
                'avg_runs': batting.get('runs_per_game', batting.get('runs', 0)) / max(batting.get('games', 1), 1),
                'avg_rbis': batting.get('rbi_per_game', batting.get('rbi', 0)) / max(batting.get('games', 1), 1),
                'avg_home_runs': batting.get('home_runs_per_game', batting.get('home_runs', 0)) / max(batting.get('games', 1), 1),
            })
        
        if 'pitching' in data:
            pitching = data['pitching']
            averages.update({
                'avg_runs_allowed': pitching.get('runs_per_game', pitching.get('runs', 0)) / max(pitching.get('games', 1), 1),
                'avg_strikeouts_pitcher': pitching.get('strikeouts_per_game', pitching.get('strikeouts', 0)) / max(pitching.get('games', 1), 1),
                'avg_walks_allowed': pitching.get('walks_per_game', pitching.get('walks', 0)) / max(pitching.get('games', 1), 1),
            })
        
        # Add 1st inning specific stats if available
        if 'innings' in data or 'first_inning' in data:
            averages['avg_runs_allowed_1st_inning'] = 0.5  # Default, would need inning-specific data
        
        return averages
    
    def _extract_nfl_averages(self, data: Dict) -> Dict:
        """Extract NFL averages from API data"""
        averages = {}
        
        if 'passing' in data:
            passing = data['passing']
            games = max(passing.get('games', 1), 1)
            averages.update({
                'avg_passing_yards': passing.get('yards', 0) / games,
                'avg_passing_touchdowns': passing.get('touchdowns', 0) / games,
                'avg_completions': passing.get('completions', 0) / games,
                'avg_attempts': passing.get('attempts', 0) / games,
                'avg_interceptions': passing.get('interceptions', 0) / games,
            })
        
        if 'rushing' in data:
            rushing = data['rushing']
            games = max(rushing.get('games', 1), 1)
            averages.update({
                'avg_rushing_yards': rushing.get('yards', 0) / games,
                'avg_rushing_touchdowns': rushing.get('touchdowns', 0) / games,
            })
        
        if 'receiving' in data:
            receiving = data['receiving']
            games = max(receiving.get('games', 1), 1)
            averages.update({
                'avg_receiving_yards': receiving.get('yards', 0) / games,
                'avg_receiving_touchdowns': receiving.get('touchdowns', 0) / games,
                'avg_receptions': receiving.get('receptions', 0) / games,
            })
        
        return averages
    
    def _extract_nba_averages(self, data: Dict) -> Dict:
        """Extract NBA averages from API data"""
        averages = {}
        
        if 'stats' in data:
            stats = data['stats']
            games = max(stats.get('games', 1), 1)
            averages.update({
                'avg_points': stats.get('points', 0) / games,
                'avg_rebounds': stats.get('totReb', stats.get('rebounds', 0)) / games,
                'avg_assists': stats.get('assists', 0) / games,
                'avg_steals': stats.get('steals', 0) / games,
                'avg_blocks': stats.get('blocks', 0) / games,
                'avg_three_pointers': stats.get('tpm', stats.get('three_pointers', 0)) / games,
            })
        
        return averages
    
    def _extract_nhl_averages(self, data: Dict) -> Dict:
        """Extract NHL averages from API data"""
        return {
            'avg_goals': 0.5,
            'avg_assists': 0.7,
            'avg_shots': 2.5,
            'avg_saves': 25.0
        }
    
    def _extract_generic_averages(self, data: Dict, sport: str) -> Dict:
        """Extract generic averages for other sports"""
        # This would be expanded based on the specific sport and API response format
        return {}
    
    def _create_enhanced_fallback_data(self, player_name: str, sport: str, prop_type: str = None) -> Dict:
        """Create enhanced fallback data when APIs fail"""
        print(f"🔄 Creating enhanced fallback data for {player_name} ({sport})")
        
        # Use the original fallback system but mark it appropriately
        from data_fetcher import DataFetcher
        fallback_fetcher = DataFetcher()
        base_data = fallback_fetcher.fetch_player_stats(player_name, sport)
        
        # Enhance with API-specific context
        base_data.update({
            'data_source': 'fallback_multi_api',
            'attempted_apis': self.api_priority.get(sport.upper(), []),
            'prop_type_context': prop_type,
            'confidence': 'low',
            'last_updated': datetime.now().isoformat()
        })
        
        return base_data
    
    def get_available_apis_for_sport(self, sport: str) -> List[str]:
        """Get list of available APIs for a sport"""
        return self.api_priority.get(sport.upper(), [])
    
    def test_api_connectivity(self) -> Dict:
        """Test connectivity to all configured APIs"""
        results = {}
        
        for sport, config in self.config.SUPPORTED_SPORTS.items():
            try:
                # Make a simple test request
                response = requests.get(
                    config['endpoint'],
                    headers={
                        'X-RapidAPI-Key': config['api_key'],
                        'X-RapidAPI-Host': config['api_host']
                    },
                    timeout=5
                )
                results[sport] = {
                    'status': 'success' if response.status_code == 200 else 'error',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                results[sport] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return results


# Test function
if __name__ == "__main__":
    print("🧪 Testing Multi-API Data Fetcher...")
    
    fetcher = MultiAPIDataFetcher()
    
    # Test API connectivity
    print("\n📡 Testing API connectivity...")
    connectivity = fetcher.test_api_connectivity()
    for sport, result in connectivity.items():
        status = "✅" if result['status'] == 'success' else "❌"
        print(f"   {status} {sport}: {result['status']}")
    
    # Test player data fetching
    test_players = [
        ("Luis Castillo", "MLB", "runs_allowed_1st_inning"),
        ("Patrick Mahomes", "NFL", "passing_yards"),
        ("LeBron James", "NBA", "points")
    ]
    
    for player, sport, prop_type in test_players:
        print(f"\n🔍 Testing {player} ({sport} - {prop_type})")
        data = fetcher.fetch_player_stats(player, sport, prop_type)
        if data:
            print(f"   ✅ Data source: {data.get('data_source')}")
            print(f"   📊 Available stats: {list(data.get('recent_averages', {}).keys())}")
        else:
            print(f"   ❌ No data retrieved")