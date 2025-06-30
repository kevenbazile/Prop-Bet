import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from prop_parser import PropParser
from analysis_engine import WagerBrainAnalysisEngine
from multi_api_data_fetcher import MultiAPIDataFetcher

@dataclass
class PrizePicksEntry:
    """Single PrizePicks entry"""
    player_name: str
    prop_type: str
    line_value: float
    bet_type: str  # 'over' or 'under'
    sport: str
    confidence_score: float = 0.0
    true_probability: float = 0.0
    expected_value: float = 0.0
    recommendation: str = "PENDING"
    data_source: str = "unknown"
    api_source: str = "unknown"

@dataclass
class PrizePicksSlip:
    """Complete PrizePicks slip with multiplier"""
    entries: List[PrizePicksEntry]
    entry_count: int
    multiplier: float
    estimated_payout: float
    slip_probability: float
    slip_expected_value: float
    kelly_fraction: float
    recommendation: str
    total_apis_used: int
    api_success_rate: float

class EnhancedPrizePicksWorkflow:
    """Enhanced PrizePicks analysis workflow with multi-API support"""
    
    def __init__(self, use_real_apis: bool = True):
        self.parser = PropParser()
        self.engine = WagerBrainAnalysisEngine()
        self.data_fetcher = MultiAPIDataFetcher() if use_real_apis else None
        self.use_real_apis = use_real_apis
        
        # Track API usage statistics
        self.api_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'apis_used': set(),
            'sports_covered': set()
        }
        
        # PrizePicks multiplier table (updated with more accurate data)
        self.multiplier_table = {
            2: {2: 3.0, 3: 5.5, 4: 10.0, 5: 20.0, 6: 50.0},
            3: {3: 6.0, 4: 12.0, 5: 25.0, 6: 100.0},
            4: {4: 15.0, 5: 35.0, 6: 150.0},
            5: {5: 40.0, 6: 250.0},
            6: {6: 300.0}
        }
    
    def analyze_single_pick(self, prop_text: str, fetch_real_data: bool = None) -> Optional[PrizePicksEntry]:
        """Analyze a single PrizePicks entry with enhanced API support"""
        if fetch_real_data is None:
            fetch_real_data = self.use_real_apis
            
        print(f"\n🔍 Analyzing: {prop_text}")
        
        # Parse the prop
        parsed_prop = self.parser.parse_single_prop(prop_text)
        if not parsed_prop:
            print(f"❌ Could not parse: {prop_text}")
            return None
        
        # Update stats
        self.api_stats['sports_covered'].add(parsed_prop['sport'])
        
        # Fetch player data with enhanced API selection
        data_source = "unknown"
        api_source = "unknown"
        
        if fetch_real_data and self.data_fetcher:
            self.api_stats['total_requests'] += 1
            
            try:
                player_stats = self.data_fetcher.fetch_player_stats(
                    parsed_prop['player_name'], 
                    parsed_prop['sport'],
                    parsed_prop['prop_type']
                )
                
                if player_stats and player_stats.get('recent_averages'):
                    self.api_stats['successful_requests'] += 1
                    data_source = player_stats.get('data_source', 'api')
                    api_source = player_stats.get('api_source', 'unknown')
                    self.api_stats['apis_used'].add(api_source)
                    print(f"✅ Data fetched from {api_source} API")
                else:
                    raise Exception("No valid data returned from API")
                    
            except Exception as e:
                print(f"⚠️ API fetch failed: {e}")
                self.api_stats['failed_requests'] += 1
                player_stats = self._create_enhanced_mock_stats(parsed_prop)
                data_source = "fallback"
                api_source = "fallback"
        else:
            # Use mock data for testing
            player_stats = self._create_enhanced_mock_stats(parsed_prop)
            data_source = "mock"
            api_source = "mock"
        
        # Run analysis
        try:
            result = self.engine.analyze_prop(parsed_prop, player_stats)
            
            entry = PrizePicksEntry(
                player_name=parsed_prop['player_name'],
                prop_type=parsed_prop['original_prop_type'],
                line_value=parsed_prop['line_value'],
                bet_type=parsed_prop['bet_type'],
                sport=parsed_prop['sport'],
                confidence_score=result['confidence_score'],
                true_probability=result['wagerbrain_analysis']['true_probability'],
                expected_value=result['wagerbrain_analysis']['expected_value'],
                recommendation=result['recommendation'],
                data_source=data_source,
                api_source=api_source
            )
            
            print(f"✅ {entry.player_name}: {entry.recommendation} ({entry.confidence_score:.1%}) [{api_source}]")
            return entry
            
        except Exception as e:
            print(f"❌ Analysis failed for {prop_text}: {e}")
            return None
    
    def analyze_slip(self, prop_texts: List[str], target_multiplier: float = None, 
                    fetch_real_data: bool = None) -> Optional[PrizePicksSlip]:
        """Analyze complete PrizePicks slip with enhanced API tracking"""
        print(f"\n🎯 ANALYZING PRIZEPICKS SLIP WITH MULTI-API SUPPORT")
        print(f"{'='*60}")
        
        if fetch_real_data is None:
            fetch_real_data = self.use_real_apis
        
        # Test API connectivity first if using real APIs
        if fetch_real_data:
            print("🔗 Testing API connectivity...")
            connectivity = self.data_fetcher.test_api_connectivity()
            available_apis = [sport for sport, result in connectivity.items() if result['status'] == 'success']
            print(f"✅ Available APIs: {len(available_apis)}/{len(connectivity)}")
        
        # Analyze each pick
        entries = []
        for prop_text in prop_texts:
            entry = self.analyze_single_pick(prop_text, fetch_real_data)
            if entry:
                entries.append(entry)
        
        if not entries:
            print("❌ No valid entries to analyze")
            return None
        
        entry_count = len(entries)
        print(f"\n📊 SLIP SUMMARY: {entry_count} entries")
        
        # Calculate API usage stats
        apis_used = len(self.api_stats['apis_used'])
        success_rate = (self.api_stats['successful_requests'] / max(self.api_stats['total_requests'], 1)) * 100
        
        print(f"🌐 API Usage: {apis_used} different APIs, {success_rate:.1f}% success rate")
        
        # Calculate slip probability (all picks must hit)
        slip_probability = 1.0
        for entry in entries:
            if entry.bet_type == 'over':
                pick_prob = entry.true_probability
            else:  # under
                pick_prob = 1 - entry.true_probability
            slip_probability *= pick_prob
        
        # Get multiplier
        if target_multiplier:
            multiplier = target_multiplier
            print(f"🎲 Using provided multiplier: {multiplier}x")
        else:
            multiplier = self._estimate_multiplier(entry_count, slip_probability)
            print(f"🎲 Estimated multiplier: {multiplier}x")
        
        # Calculate expected value
        stake = 1.0  # $1 stake
        expected_payout = slip_probability * multiplier * stake
        expected_value = expected_payout - stake
        
        # Calculate Kelly fraction
        kelly_fraction = self._calculate_kelly_for_slip(slip_probability, multiplier)
        
        # Generate recommendation
        recommendation = self._generate_slip_recommendation(
            entries, slip_probability, expected_value, kelly_fraction
        )
        
        slip = PrizePicksSlip(
            entries=entries,
            entry_count=entry_count,
            multiplier=multiplier,
            estimated_payout=expected_payout,
            slip_probability=slip_probability,
            slip_expected_value=expected_value,
            kelly_fraction=kelly_fraction,
            recommendation=recommendation,
            total_apis_used=apis_used,
            api_success_rate=success_rate
        )
        
        self._print_enhanced_slip_analysis(slip)
        return slip
    
    def compare_with_sportsbooks(self, entries: List[PrizePicksEntry]) -> Dict:
        """Enhanced sportsbook comparison with API data"""
        print(f"\n📈 ENHANCED SPORTSBOOK COMPARISON")
        print(f"{'='*50}")
        
        comparisons = []
        
        # If we have real API access, try to get actual sportsbook data
        if self.use_real_apis and hasattr(self.data_fetcher, 'fetch_sportsbook_odds'):
            for entry in entries:
                try:
                    sportsbook_data = self.data_fetcher.fetch_sportsbook_odds(
                        entry.sport, entry.player_name
                    )
                    
                    if sportsbook_data:
                        comparison = self._analyze_real_sportsbook_data(entry, sportsbook_data)
                    else:
                        comparison = self._create_mock_sportsbook_comparison(entry)
                        
                except Exception as e:
                    print(f"⚠️ Sportsbook data fetch failed for {entry.player_name}: {e}")
                    comparison = self._create_mock_sportsbook_comparison(entry)
                
                comparisons.append(comparison)
                self._print_sportsbook_comparison(comparison)
        else:
            # Use mock sportsbook data
            for entry in entries:
                comparison = self._create_mock_sportsbook_comparison(entry)
                comparisons.append(comparison)
                self._print_sportsbook_comparison(comparison)
        
        return {
            'comparisons': comparisons,
            'total_entries': len(entries),
            'data_source': 'real_apis' if self.use_real_apis else 'mock',
            'generated_at': datetime.now().isoformat()
        }
    
    def _create_enhanced_mock_stats(self, parsed_prop: Dict) -> Dict:
        """Create enhanced mock stats with more realistic data"""
        prop_type = parsed_prop['prop_type']
        line_value = parsed_prop['line_value']
        sport = parsed_prop['sport']
        player_name = parsed_prop['player_name']
        
        # Enhanced mock data based on prop type and player
        base_multipliers = {
            'runs_allowed_1st_inning': 1.2,
            'hits': 1.15,
            'runs': 1.1,
            'home_runs': 0.8,
            'strikeouts': 1.3,
            'passing_yards': 1.05,
            'rushing_yards': 1.1,
            'receiving_yards': 1.08,
            'points': 1.12,
            'rebounds': 1.15,
            'assists': 1.18
        }
        
        multiplier = base_multipliers.get(prop_type, 1.1)
        mock_avg = line_value * multiplier
        
        # Create sport-specific mock averages
        mock_averages = {f"avg_{prop_type}": mock_avg}
        
        # Add related stats for more realistic analysis
        if sport == 'MLB':
            if 'runs_allowed' in prop_type:
                mock_averages.update({
                    'avg_era': 3.8,
                    'avg_whip': 1.2,
                    'avg_strikeouts_pitcher': 6.5,
                    'avg_walks_allowed': 2.8
                })
            else:
                mock_averages.update({
                    'avg_hits': mock_avg if 'hits' in prop_type else 1.3,
                    'avg_runs': mock_avg if 'runs' in prop_type else 0.9,
                    'avg_rbis': 1.1,
                    'avg_home_runs': mock_avg if 'home_runs' in prop_type else 0.35
                })
        
        return {
            'player_name': player_name,
            'sport': sport,
            'recent_averages': mock_averages,
            'games_played': 15,
            'total_games': 30,
            'data_source': 'enhanced_mock',
            'confidence': 'medium',
            'last_updated': datetime.now().isoformat()
        }
    
    def _analyze_real_sportsbook_data(self, entry: PrizePicksEntry, sportsbook_data: Dict) -> Dict:
        """Analyze real sportsbook data against PrizePicks"""
        # Process actual sportsbook API response
        comparison = {
            'player': entry.player_name,
            'prop': entry.prop_type,
            'prizepicks_line': entry.line_value,
            'sportsbooks': {},
            'line_advantage': 0,
            'value_rating': 'neutral',
            'data_source': 'real_api'
        }
        
        # Extract sportsbook lines and odds from real data
        # This would depend on the actual API response format
        if 'bookmakers' in sportsbook_data:
            for bookmaker in sportsbook_data['bookmakers']:
                book_name = bookmaker.get('title', 'unknown')
                markets = bookmaker.get('markets', [])
                
                # Find the relevant market for this prop
                for market in markets:
                    if self._matches_prop_type(market.get('key'), entry.prop_type):
                        outcomes = market.get('outcomes', [])
                        if len(outcomes) >= 2:
                            comparison['sportsbooks'][book_name] = {
                                'line': outcomes[0].get('point', entry.line_value),
                                'over_odds': outcomes[0].get('price', -110),
                                'under_odds': outcomes[1].get('price', -110)
                            }
        
        # Calculate line advantage
        if comparison['sportsbooks']:
            avg_line = sum(book['line'] for book in comparison['sportsbooks'].values()) / len(comparison['sportsbooks'])
            comparison['line_advantage'] = self._calculate_line_advantage(entry, avg_line)
            comparison['value_rating'] = self._rate_line_value(comparison['line_advantage'])
        
        return comparison
    
    def _create_mock_sportsbook_comparison(self, entry: PrizePicksEntry) -> Dict:
        """Create realistic mock sportsbook comparison"""
        import random
        
        # Create realistic variations around the PrizePicks line
        base_line = entry.line_value
        
        mock_sportsbook_data = {
            'draftkings': {
                'line': base_line + random.uniform(-0.2, 0.2),
                'over_odds': random.randint(-125, -105),
                'under_odds': random.randint(-125, -105)
            },
            'fanduel': {
                'line': base_line + random.uniform(-0.15, 0.15),
                'over_odds': random.randint(-120, -100),
                'under_odds': random.randint(-120, -100)
            },
            'betmgm': {
                'line': base_line + random.uniform(-0.1, 0.3),
                'over_odds': random.randint(-118, -108),
                'under_odds': random.randint(-118, -108)
            },
            'caesars': {
                'line': base_line + random.uniform(-0.25, 0.1),
                'over_odds': random.randint(-115, -110),
                'under_odds': random.randint(-115, -110)
            }
        }
        
        # Calculate line advantage
        avg_line = sum(book['line'] for book in mock_sportsbook_data.values()) / len(mock_sportsbook_data)
        line_advantage = self._calculate_line_advantage(entry, avg_line)
        
        return {
            'player': entry.player_name,
            'prop': entry.prop_type,
            'prizepicks_line': entry.line_value,
            'sportsbooks': mock_sportsbook_data,
            'line_advantage': line_advantage,
            'value_rating': self._rate_line_value(line_advantage),
            'data_source': 'mock'
        }
    
    def _matches_prop_type(self, market_key: str, prop_type: str) -> bool:
        """Check if sportsbook market matches our prop type"""
        market_mappings = {
            'player_hits': 'hits',
            'player_runs': 'runs',
            'player_rbis': 'rbis',
            'player_home_runs': 'home_runs',
            'player_strikeouts': 'strikeouts',
            'player_passing_yards': 'passing_yards',
            'player_rushing_yards': 'rushing_yards',
            'player_receiving_yards': 'receiving_yards',
            'player_points': 'points',
            'player_rebounds': 'rebounds',
            'player_assists': 'assists'
        }
        
        return market_mappings.get(market_key) == prop_type
    
    def _calculate_line_advantage(self, entry: PrizePicksEntry, avg_sportsbook_line: float) -> float:
        """Calculate line advantage for PrizePicks vs sportsbooks"""
        if entry.bet_type == 'over':
            # For overs, lower lines are better
            return avg_sportsbook_line - entry.line_value
        else:
            # For unders, higher lines are better
            return entry.line_value - avg_sportsbook_line
    
    def _rate_line_value(self, line_advantage: float) -> str:
        """Rate the line value advantage"""
        if line_advantage > 0.2:
            return 'very_favorable'
        elif line_advantage > 0.1:
            return 'favorable'
        elif line_advantage > -0.1:
            return 'neutral'
        elif line_advantage > -0.2:
            return 'unfavorable'
        else:
            return 'very_unfavorable'
    
    def _print_sportsbook_comparison(self, comparison: Dict):
        """Print individual sportsbook comparison"""
        player = comparison['player']
        prop = comparison['prop']
        pp_line = comparison['prizepicks_line']
        advantage = comparison['line_advantage']
        rating = comparison['value_rating']
        
        rating_emoji = {
            'very_favorable': '🟢',
            'favorable': '🟡', 
            'neutral': '⚪',
            'unfavorable': '🟠',
            'very_unfavorable': '🔴'
        }
        
        print(f"\n{rating_emoji.get(rating, '⚪')} {player} {prop}")
        print(f"   PrizePicks: {pp_line} | Advantage: {advantage:+.2f} | Rating: {rating}")
        
        for book, data in comparison['sportsbooks'].items():
            print(f"   {book.title()}: {data['line']} (O: {data['over_odds']:+d}, U: {data['under_odds']:+d})")
    
    def _estimate_multiplier(self, entry_count: int, slip_probability: float) -> float:
        """Enhanced multiplier estimation"""
        if entry_count < 2 or entry_count > 6:
            return 2.0
        
        # More sophisticated multiplier estimation
        base_multipliers = self.multiplier_table.get(entry_count, {})
        
        if slip_probability > 0.4:
            return base_multipliers.get(entry_count, 2.0)
        elif slip_probability > 0.25:
            return base_multipliers.get(entry_count + 1, 3.0)
        elif slip_probability > 0.15:
            return base_multipliers.get(entry_count + 2, 5.0)
        else:
            return base_multipliers.get(entry_count + 3, 10.0)
    
    def _calculate_kelly_for_slip(self, win_probability: float, multiplier: float) -> float:
        """Calculate Kelly criterion for the entire slip"""
        if win_probability <= 0 or multiplier <= 1:
            return 0.0
        
        b = multiplier - 1
        p = win_probability
        q = 1 - win_probability
        
        kelly = (b * p - q) / b
        return max(0, min(0.25, kelly))
    
    def _generate_slip_recommendation(self, entries: List[PrizePicksEntry], 
                                    slip_probability: float, expected_value: float, 
                                    kelly_fraction: float) -> str:
        """Enhanced slip recommendation with API data quality consideration"""
        
        # Count recommendation types
        strong_picks = sum(1 for e in entries if e.recommendation == 'STRONG_BET')
        moderate_picks = sum(1 for e in entries if e.recommendation == 'MODERATE_BET')
        weak_picks = sum(1 for e in entries if e.recommendation == 'WEAK_BET')
        avoid_picks = sum(1 for e in entries if e.recommendation in ['AVOID', 'STRONG_AVOID'])
        
        # Check data quality
        api_picks = sum(1 for e in entries if e.data_source.startswith('api'))
        data_quality_multiplier = 1.0 + (api_picks / len(entries) * 0.2)  # Boost for real API data
        
        # Enhanced recommendation logic
        if avoid_picks > 0:
            return "AVOID_SLIP"
        elif (expected_value * data_quality_multiplier > 0.20 and 
              slip_probability > 0.35 and 
              strong_picks >= len(entries) // 2):
            return "STRONG_PLAY"
        elif (expected_value * data_quality_multiplier > 0.10 and 
              slip_probability > 0.25 and 
              (strong_picks + moderate_picks) >= len(entries) * 0.6):
            return "MODERATE_PLAY"
        elif (expected_value > 0 and 
              weak_picks < len(entries) // 2 and
              slip_probability > 0.15):
            return "WEAK_PLAY"
        else:
            return "AVOID_SLIP"
    
    def _print_enhanced_slip_analysis(self, slip: PrizePicksSlip):
        """Print enhanced slip analysis with API information"""
        print(f"\n🎯 ENHANCED SLIP ANALYSIS")
        print(f"{'='*60}")
        
        print(f"📋 INDIVIDUAL PICKS:")
        for i, entry in enumerate(slip.entries, 1):
            api_indicator = "🌐" if entry.data_source.startswith('api') else "📝"
            print(f"   {i}. {api_indicator} {entry.player_name} [{entry.api_source}]")
            print(f"      {entry.bet_type.title()} {entry.line_value} {entry.prop_type}")
            print(f"      Confidence: {entry.confidence_score:.1%} | Rec: {entry.recommendation}")
        
        print(f"\n🌐 API USAGE SUMMARY:")
        print(f"   APIs Used: {slip.total_apis_used}")
        print(f"   Success Rate: {slip.api_success_rate:.1f}%")
        print(f"   Sports Covered: {len(self.api_stats['sports_covered'])}")
        
        print(f"\n📊 SLIP METRICS:")
        print(f"   Total Picks: {slip.entry_count}")
        print(f"   Slip Probability: {slip.slip_probability:.1%}")
        print(f"   Multiplier: {slip.multiplier}x")
        print(f"   Expected Payout: ${slip.estimated_payout:.2f}")
        print(f"   Expected Value: ${slip.slip_expected_value:.2f}")
        print(f"   Kelly Fraction: {slip.kelly_fraction:.1%}")
        
        print(f"\n🎯 FINAL RECOMMENDATION: {slip.recommendation}")
        
        # Enhanced recommendation explanation
        if slip.recommendation == "STRONG_PLAY":
            print("   ✅ Strong positive EV with high-quality data!")
        elif slip.recommendation == "MODERATE_PLAY":
            print("   ⚠️ Moderate value - consider smaller stake")
        elif slip.recommendation == "WEAK_PLAY":
            print("   ⚠️ Weak value - proceed with caution")
        else:
            print("   ❌ Avoid this slip - negative expected value")
    
    def get_api_usage_report(self) -> Dict:
        """Get detailed API usage report"""
        return {
            'total_requests': self.api_stats['total_requests'],
            'successful_requests': self.api_stats['successful_requests'],
            'failed_requests': self.api_stats['failed_requests'],
            'success_rate': (self.api_stats['successful_requests'] / 
                           max(self.api_stats['total_requests'], 1)) * 100,
            'unique_apis_used': len(self.api_stats['apis_used']),
            'apis_used': list(self.api_stats['apis_used']),
            'sports_covered': list(self.api_stats['sports_covered']),
            'generated_at': datetime.now().isoformat()
        }


# Enhanced test function
def enhanced_test():
    """Enhanced test with real API integration"""
    print("🎯 Enhanced PrizePicks Workflow Test with Multi-API Support")
    print("="*70)
    
    # Test with real APIs (set to False for mock data)
    USE_REAL_APIS = True
    
    workflow = EnhancedPrizePicksWorkflow(use_real_apis=USE_REAL_APIS)
    
    # Test props covering multiple sports and APIs
    test_props = [
        "Luis Castillo + Jack Leiter Over 0.5 1st Inning Runs Allowed",  # MLB API
        "Patrick Mahomes Over 275.5 Passing Yards",                      # NFL API
        "LeBron James Under 25.5 Points"                                 # NBA API
    ]
    
    # Analyze the slip
    slip = workflow.analyze_slip(test_props, target_multiplier=6.0, fetch_real_data=USE_REAL_APIS)
    
    # Enhanced sportsbook comparison
    if slip:
        sportsbook_analysis = workflow.compare_with_sportsbooks(slip.entries)
        
        # Print API usage report
        print(f"\n📊 API USAGE REPORT:")
        api_report = workflow.get_api_usage_report()
        print(f"   Total API Calls: {api_report['total_requests']}")
        print(f"   Success Rate: {api_report['success_rate']:.1f}%")
        print(f"   APIs Used: {', '.join(api_report['apis_used'])}")
        print(f"   Sports Covered: {', '.join(api_report['sports_covered'])}")
    
    return slip

if __name__ == "__main__":
    enhanced_test()