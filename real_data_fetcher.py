import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from config import Config

class RealDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # API endpoints
        self.apis = {
            'mlb': 'https://statsapi.mlb.com/api/v1',
            'nba': 'https://stats.nba.com/stats',
            'nfl': 'https://api.sportsdata.io/v3/nfl',
            'nhl': 'https://statsapi.web.nhl.com/api/v1'
        }
    
    def get_real_player_stats(self, player_name, sport, days=30):
        """Get real player statistics from APIs"""
        print(f"📊 Fetching real stats for {player_name} ({sport})")
        
        try:
            if sport.upper() == 'MLB':
                return self.get_mlb_stats_real(player_name, days)
            elif sport.upper() == 'NBA':
                return self.get_nba_stats_real(player_name, days)
            elif sport.upper() == 'NFL':
                return self.get_nfl_stats_real(player_name, days)
            elif sport.upper() == 'NHL':
                return self.get_nhl_stats_real(player_name, days)
            else:
                print(f"❌ Unsupported sport: {sport}")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching real stats: {e}")
            return {}
    
    def get_mlb_stats_real(self, player_name, days):
        """Get real MLB stats from MLB API"""
        try:
            # Search for player
            search_url = f"{self.apis['mlb']}/sports/1/players"
            params = {'season': datetime.now().year}
            
            response = self.session.get(search_url, params=params)
            time.sleep(0.5)  # Rate limiting
            
            if response.status_code != 200:
                print(f"❌ MLB API error: {response.status_code}")
                return {}
            
            data = response.json()
            player_id = None
            
            # Find player by name
            for player in data.get('people', []):
                full_name = f"{player.get('firstName', '')} {player.get('lastName', '')}"
                if player_name.lower() in full_name.lower():
                    player_id = player['id']
                    break
            
            if not player_id:
                print(f"❌ Player {player_name} not found in MLB API")
                return {}
            
            # Get game logs
            stats_url = f"{self.apis['mlb']}/people/{player_id}/stats"
            params = {
                'stats': 'gameLog',
                'season': datetime.now().year,
                'gameType': 'R'
            }
            
            response = self.session.get(stats_url, params=params)
            time.sleep(0.5)
            
            if response.status_code == 200:
                stats_data = response.json()
                return self.parse_mlb_stats_real(stats_data, player_name)
            
            return {}
            
        except Exception as e:
            print(f"❌ MLB stats error: {e}")
            return {}
    
    def parse_mlb_stats_real(self, data, player_name):
        """Parse real MLB statistics"""
        try:
            games = []
            
            if 'stats' in data and data['stats']:
                for stat_group in data['stats']:
                    if stat_group['type']['displayName'] == 'gameLog':
                        for split in stat_group.get('splits', []):
                            game_stats = split.get('stat', {})
                            game_date = split.get('date')
                            
                            game = {
                                'date': game_date,
                                'hits': game_stats.get('hits', 0),
                                'runs': game_stats.get('runs', 0),
                                'rbis': game_stats.get('rbi', 0),
                                'home_runs': game_stats.get('homeRuns', 0),
                                'strikeouts': game_stats.get('strikeOuts', 0),
                                'at_bats': game_stats.get('atBats', 0)
                            }
                            games.append(game)
            
            # Calculate averages
            if games:
                recent_games = games[-15:]  # Last 15 games
                
                averages = {
                    'avg_hits': np.mean([g['hits'] for g in recent_games]),
                    'avg_runs': np.mean([g['runs'] for g in recent_games]),
                    'avg_rbis': np.mean([g['rbis'] for g in recent_games]),
                    'avg_home_runs': np.mean([g['home_runs'] for g in recent_games]),
                    'avg_strikeouts': np.mean([g['strikeouts'] for g in recent_games]),
                    'games_played': len(recent_games)
                }
                
                return {
                    'player_name': player_name,
                    'sport': 'MLB',
                    'games': recent_games,
                    'recent_averages': averages,
                    'data_source': 'MLB_API_REAL'
                }
            
            return {}
            
        except Exception as e:
            print(f"❌ MLB parsing error: {e}")
            return {}
    
    def get_nba_stats_real(self, player_name, days):
        """Get real NBA stats - placeholder for NBA API integration"""
        # NBA API requires more complex authentication
        # For now, return mock data based on known players
        
        mock_data = {
            'lebron james': {'avg_points': 25.8, 'avg_rebounds': 7.2, 'avg_assists': 7.8},
            'stephen curry': {'avg_points': 29.5, 'avg_rebounds': 4.5, 'avg_assists': 6.1},
            'kevin durant': {'avg_points': 28.2, 'avg_rebounds': 6.8, 'avg_assists': 5.0},
        }
        
        player_lower = player_name.lower()
        for name, stats in mock_data.items():
            if name in player_lower:
                return {
                    'player_name': player_name,
                    'sport': 'NBA',
                    'recent_averages': stats,
                    'data_source': 'MOCK_DATA'
                }
        
        # Default NBA averages
        return {
            'player_name': player_name,
            'sport': 'NBA',
            'recent_averages': {
                'avg_points': 18.5,
                'avg_rebounds': 5.2,
                'avg_assists': 4.1
            },
            'data_source': 'DEFAULT_NBA'
        }
    
    def get_nfl_stats_real(self, player_name, days):
        """Get real NFL stats - placeholder"""
        return {
            'player_name': player_name,
            'sport': 'NFL',
            'recent_averages': {
                'avg_passing_yards': 250.0,
                'avg_rushing_yards': 75.0,
                'avg_receiving_yards': 65.0,
                'avg_touchdowns': 1.2
            },
            'data_source': 'DEFAULT_NFL'
        }
    
    def get_nhl_stats_real(self, player_name, days):
        """Get real NHL stats - placeholder"""
        return {
            'player_name': player_name,
            'sport': 'NHL',
            'recent_averages': {
                'avg_goals': 0.6,
                'avg_assists': 0.8,
                'avg_points': 1.4,
                'avg_shots': 3.2
            },
            'data_source': 'DEFAULT_NHL'
        }
    
    def get_team_defensive_stats(self, team, sport):
        """Get real team defensive statistics"""
        # This would fetch real defensive stats against specific stat types
        return {
            'team': team,
            'sport': sport,
            'defensive_rating': 'AVERAGE',  # ELITE, GOOD, AVERAGE, POOR
            'stats_allowed': {}
        }
