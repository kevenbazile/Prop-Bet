import os
from datetime import datetime

class Config:
    """Centralized configuration"""
    
    # API Keys (from your prompt)
    TELEGRAM_BOT_TOKEN = "7633034225:AAGHyorIbrr_SSs1pPNWIF_bJ9sId-5q4Sc"
    X_RAPID_API_KEY = "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20"
    ODDS_API_KEY = "3e336de9c572638d36a0c91a03958337"
    TWOCAPTCHA_API_KEY = "YOUR_2CAPTCHA_KEY"
    FLARESOLVERR_URL = "http://localhost:8191/v1"
    WEATHER_API_KEY = "abab613657b5bd8e3f0d028d187ed97e"

    # Database
    DATABASE_PATH = "./database/"
    PROPS_DB = os.path.join(DATABASE_PATH, "props.db")
    STATS_DB = os.path.join(DATABASE_PATH, "player_stats.db")
    
    # Rate Limiting
    API_RATE_LIMIT = 60  # requests per minute
    REQUEST_DELAY = 1.5  # seconds between requests
    
    # Supported Sports and API Key Mapping
    SUPPORTED_SPORTS = {
        # X_RAPID_API_KEY
        "MLB": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "all-sport-live-stream.p.rapidapi.com",
            "endpoint": "https://all-sport-live-stream.p.rapidapi.com/api/v1/all-live-stream",
            "prop_tabs": [
                "Popular", "Pitcher Strikeouts", "Total Bases", "Hits+Runs+RBIs", "1st Inning Runs Allowed",
                "Hitter Fantasy Score", "Home Runs", "Pitcher Fantasy Score", "Hits Allowed", "Stolen Bases",
                "Doubles", "Walk Allowed", "1st inning walks Allowed", "Singles", "Pitch Outs", "Walk", "Hits",
                "Earned Runs Allowed", "RBIs", "Runs", "Hitter Strikeouts", "Triples"
            ]
        },
        "NFL": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-american-football.p.rapidapi.com",
            "endpoint": "https://api-american-football.p.rapidapi.com/players",
            "prop_tabs": [
                "Pass Yards", "Rush Yards", "Rush+Rec+TDs", "Recieving Yards"
            ]
        },
        "NBA": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-nba-v1.p.rapidapi.com",
            "endpoint": "https://api-nba-v1.p.rapidapi.com/players",
            "prop_tabs": [
                "Points", "Rebounds", "Assists", "Steals", "Blocks", "Three Pointers"
            ]
        },
        "NHL": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-hockey.p.rapidapi.com",
            "endpoint": "https://api-hockey.p.rapidapi.com/players",
            "prop_tabs": []
        },
        "NFLSZN": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-american-football.p.rapidapi.com",
            "endpoint": "https://api-american-football.p.rapidapi.com/players",
            "prop_tabs": [
                "Recieveing Yards", "Pass TDs", "Rec TDs", "Rush TDs", "Sacks", "INT", "100 Rush Yard Games"
            ]
        },
        "NBASZN": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-nba-v1.p.rapidapi.com",
            "endpoint": "https://api-nba-v1.p.rapidapi.com/players",
            "prop_tabs": [
                "Points Per Game AVG", "Rebounds Per Game AVG", "Assists Per Game AVG", "3pt Made Per Game AVG"
            ]
        },

        # X_RAPID_API_KEY_8
        "Soccer": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-football-v1.p.rapidapi.com",
            "endpoint": "https://api-football-v1.p.rapidapi.com/players",
            "prop_tabs": [
                "Popular", "Goalie Saves", "Shots", "Goals", "Shots on Target", "Assist", "Cards", "Passes Attempted",
                "Goalie Saves (Combo)", "Goals Allowed", "Goals Allowed in first 30 Minutes", "Goal + Assist", "Shot Assisted",
                "Clearances", "Tackles", "Attempted Dribbles", "Fouls", "Offsides"
            ]
        },
        "Tennis": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "api-tennis.p.rapidapi.com",
            "endpoint": "https://api-tennis.p.rapidapi.com/players",
            "prop_tabs": [
                "Popular", "Total Games", "Aces", "Total Games Won", "Fantasy Score", "Break points Won", "Double Faults"
            ]
        },
        "MMA": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "mma-data.p.rapidapi.com",
            "endpoint": "https://mma-data.p.rapidapi.com/players",
            "prop_tabs": [
                "Popular", "Significant strikes", "Fight time(Mins)", "Significant Strikes(Combo)", "Fantasy score", "Takedowns", "RD 1 Significant Takedown"
            ]
        },
        "Boxing": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "boxing-data.p.rapidapi.com",
            "endpoint": "https://boxing-data.p.rapidapi.com/players",
            "prop_tabs": [
                "Popular", "Total punches Landed", "Fight Time(Mins)", "Fantasy Score"
            ]
        },
        "PGA": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "golf-leaderboard.p.rapidapi.com",
            "endpoint": "https://golf-leaderboard.p.rapidapi.com/players",
            "prop_tabs": [
                "Popular", "Strokes", "Birdies or better", "Birdies or better matchup", "Greens in regulation", "Par"
            ]
        },
        "COD": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "call-of-duty.p.rapidapi.com",
            "endpoint": "https://call-of-duty.p.rapidapi.com/players",
            "prop_tabs": [
                "Popular", "MAPS 1-3 Kills(Combos)", "Maps 1-3", "Series K/D", "Map 1 Kills", "Map 2 Kills", "Map2 first Blood (combo)", "Map 3 Kills"
            ]
        },
        # ...continue for all other sports, using the correct api_key and endpoint...

        # Example for Darts, Cricket, Table Tennis (X_RAPID_API_KEY_3)
        "Darts": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "darts.p.rapidapi.com",
            "endpoint": "https://darts.p.rapidapi.com/players",
            "prop_tabs": [
                "180's Thrown", "Total Logs", "1st Leg Checkout Total", "180's Thrown(combo)"
            ]
        },
        "Cricket": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "cricket-live.p.rapidapi.com",
            "endpoint": "https://cricket-live.p.rapidapi.com/players",
            "prop_tabs": [
                "Fours", "Sixers", "1st inning runs"
            ]
        },
        "TableTennis": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "table-tennis.p.rapidapi.com",
            "endpoint": "https://table-tennis.p.rapidapi.com/players",
            "prop_tabs": []
        },
      "Nascar": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "nascar.p.rapidapi.com",
            "endpoint": "https://nascar.p.rapidapi.com/players",
            "prop_tabs": [
                "Fastest Lap", "Laps Led", "Top 5 Finish", "Top 10 Finish"
            ]
        },
        "F1": {
            "api_key": "9c0527d0e4mshbaaddd42aa7047dp174106jsn0cadf9a24b20",
            "api_host": "formula-1.p.rapidapi.com",
            "endpoint": "https://formula-1.p.rapidapi.com/players",
            "prop_tabs": [
                "Fastest Lap", "Laps Led", "Podium Finish", "Points Scored"
            ]
        }
    }
    
    # Telegram Bot Commands
    BOT_COMMANDS = {
        "/start": "Welcome to Multi-Sport Prop Bot",
        "/help": "Show available commands", 
        "/sports": "List supported sports",
        "/props": "Get today's best props",
        "/analyze": "Analyze specific player prop",
    }
