import numpy as np
import pandas as pd
import sys
import os
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Current working directory:", os.getcwd())
print("analysis_engine.py __file__:", __file__ if '__file__' in globals() else 'Not available')

# **FIXED WAGERBRAIN IMPORTS**
# Add WagerBrain to Python path
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
wagerbrain_path = os.path.join(current_dir, 'WagerBrain')
if wagerbrain_path not in sys.path:
    sys.path.insert(0, wagerbrain_path)
    print(f"Added WagerBrain to path: {wagerbrain_path}")

# Import WagerBrain functions
WAGERBRAIN_AVAILABLE = False
try:
    from WagerBrain import (
        kelly_criterion, basic_kelly_criterion,
        implied_probability, true_odds_ev, stated_odds_ev,
        PropModel, BettingModel,
        odds_converter, probability_calculator
    )
    WAGERBRAIN_AVAILABLE = True
    logger.info("✅ WagerBrain imported successfully!")
    print("✅ WagerBrain models initialized")
    
except ImportError as e:
    logger.warning(f"⚠️ WagerBrain import failed: {e}")
    logger.info("🔄 Using fallback functions...")
    
    # Fallback functions
    def implied_probability(odds):
        """Fallback implied probability calculation"""
        try:
            if isinstance(odds, str) and (odds.startswith('+') or odds.startswith('-')):
                odds_value = int(odds)
            else:
                odds_value = -110
            
            if odds_value > 0:
                return 100 / (odds_value + 100)
            else:
                return abs(odds_value) / (abs(odds_value) + 100)
        except:
            return 0.5263  # -110 implied probability
    
    def kelly_criterion(prob, odds):
        """Fallback Kelly criterion calculation"""
        try:
            if isinstance(odds, str) and (odds.startswith('+') or odds.startswith('-')):
                odds_value = int(odds)
            else:
                odds_value = -110
            
            if odds_value > 0:
                decimal_odds = (odds_value / 100) + 1
            else:
                decimal_odds = (100 / abs(odds_value)) + 1
            
            kelly = (prob * decimal_odds - 1) / (decimal_odds - 1)
            return max(0, min(0.25, kelly))  # Cap at 25% of bankroll
        except:
            return 0.0
    
    basic_kelly_criterion = kelly_criterion
    
    def true_odds_ev(stake, profit, prob):
        """Fallback expected value calculation"""
        return (prob * profit) - ((1 - prob) * stake)
    
    def stated_odds_ev(stake, odds, prob):
        """Fallback stated odds EV calculation"""
        try:
            if isinstance(odds, str) and (odds.startswith('+') or odds.startswith('-')):
                odds_value = int(odds)
            else:
                odds_value = -110
            
            if odds_value > 0:
                profit = stake * (odds_value / 100)
            else:
                profit = stake * (100 / abs(odds_value))
            return true_odds_ev(stake, profit, prob)
        except:
            return 0.0
    
    def odds_converter(odds, to_format='decimal'):
        """Fallback odds converter"""
        return 2.0
    
    def probability_calculator(data):
        """Fallback probability calculator"""
        return 0.5
    
    class PropModel:
        def __init__(self):
            self.name = "FallbackPropModel"
        def predict(self, data):
            return 0.5
        def analyze(self, data):
            return {"probability": 0.5, "confidence": 0.5}
    
    class BettingModel:
        def __init__(self):
            self.name = "FallbackBettingModel"
        def analyze(self, data):
            return {"expected_value": 0.0, "kelly_size": 0.0}
    
    WAGERBRAIN_AVAILABLE = False

# Try to import scipy for advanced statistics
try:
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("⚠️ SciPy not available. Some statistical features will be limited.")

# Try to import config
try:
    from config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("⚠️ Config module not available. Using default settings.")


@dataclass
class AnalysisConfig:
    """Configuration class for analysis parameters"""
    confidence_thresholds: Dict[str, float] = None
    factor_weights: Dict[str, float] = None
    kelly_max_fraction: float = 0.25
    min_edge_threshold: float = 0.01
    monte_carlo_simulations: int = 10000
    risk_free_rate: float = 0.02
    
    def __post_init__(self):
        if self.confidence_thresholds is None:
            self.confidence_thresholds = {
                'high': 0.75,
                'medium': 0.65,
                'low': 0.55
            }
        
        if self.factor_weights is None:
            self.factor_weights = {
                'recent_form': 0.40,
                'opponent_strength': 0.25,
                'home_away': 0.15,
                'weather': 0.10,
                'rest_days': 0.05,
                'historical': 0.05
            }


class WagerBrainAnalysisEngine:
    """Enhanced Analysis Engine with WagerBrain Mathematical Integration"""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        
        # Use config for thresholds and factors
        self.confidence_thresholds = self.config.confidence_thresholds
        self.factors = self.config.factor_weights

        # Initialize WagerBrain models
        try:
            self.prop_model = PropModel()
            self.betting_model = BettingModel()
            logger.info("✅ WagerBrain models initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize WagerBrain models: {e}")
            self.prop_model = None
            self.betting_model = None

    def analyze_prop(self, prop_data: Dict, player_stats: Dict, opponent_data: Optional[Dict] = None) -> Dict:
        """Comprehensive prop analysis with WagerBrain integration"""
        try:
            logger.info(f"🔬 Analyzing {prop_data['player_name']} {prop_data['prop_type']} {prop_data['line_value']}")

            # Core analysis components
            recent_analysis = self.analyze_recent_performance(player_stats, prop_data)
            historical_analysis = self.analyze_historical_trends(player_stats, prop_data)
            opponent_analysis = self.analyze_opponent_matchup(opponent_data, prop_data)
            situational_analysis = self.analyze_situational_factors(prop_data, player_stats)

            # Calculate weighted confidence score
            confidence_score = self.calculate_confidence_score(
                recent_analysis,
                historical_analysis,
                opponent_analysis,
                situational_analysis
            )

            # WagerBrain Mathematical Analysis
            wagerbrain_analysis = self.wagerbrain_mathematical_analysis(prop_data, confidence_score, player_stats)

            # Generate recommendation using WagerBrain
            recommendation = self.generate_wagerbrain_recommendation(
                confidence_score,
                wagerbrain_analysis
            )

            analysis_result = {
                'prop_id': prop_data.get('id'),
                'player_name': prop_data['player_name'],
                'prop_type': prop_data['prop_type'],
                'line_value': prop_data['line_value'],
                'sport': prop_data['sport'],
                'confidence_score': round(confidence_score, 3),
                'recommendation': recommendation,
                'analysis_components': {
                    'recent_performance': recent_analysis,
                    'historical_trends': historical_analysis,
                    'opponent_matchup': opponent_analysis,
                    'situational_factors': situational_analysis
                },
                'wagerbrain_analysis': wagerbrain_analysis,
                'analyzed_at': datetime.now().isoformat()
            }

            logger.info(f"✅ Analysis complete - Confidence: {confidence_score:.1%}, Recommendation: {recommendation}")
            return analysis_result

        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return self.create_error_analysis(prop_data, str(e))

    def wagerbrain_mathematical_analysis(self, prop_data: Dict, confidence_score: float, player_stats: Dict) -> Dict:
        """Advanced mathematical analysis using WagerBrain"""
        try:
            # Extract odds
            odds = prop_data.get('odds', '-110')
            line_value = prop_data['line_value']

            # Convert odds to probability using WagerBrain
            implied_prob = implied_probability(odds)

            # Calculate our true probability (confidence score)
            true_probability = confidence_score

            # Calculate profit for a $1 stake based on American odds
            try:
                odds_value = int(str(odds).replace('+', ''))
                if odds_value > 0:
                    profit = odds_value / 100
                else:
                    profit = 100 / abs(odds_value)
            except (ValueError, TypeError):
                profit = 100 / 110  # Default for -110 odds

            # Calculate Expected Value using WagerBrain
            expected_value = true_odds_ev(1, profit, true_probability)

            # Calculate Kelly Criterion using WagerBrain
            kelly_bet_size = kelly_criterion(true_probability, odds)

            # Advanced statistical analysis
            statistical_analysis = self.wagerbrain_statistical_analysis(player_stats, prop_data)

            # Sharpe ratio calculation for risk assessment
            sharpe_ratio = self.calculate_sharpe_ratio(expected_value, statistical_analysis.get('volatility', 0.1))

            # Monte Carlo simulation
            monte_carlo_results = self.run_monte_carlo_simulation(prop_data, player_stats)

            return {
                'expected_value': round(expected_value, 4),
                'kelly_criterion': round(kelly_bet_size, 4),
                'implied_probability': round(implied_prob, 4),
                'true_probability': round(true_probability, 4),
                'edge': round(true_probability - implied_prob, 4),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'statistical_analysis': statistical_analysis,
                'monte_carlo': monte_carlo_results,
                'wagerbrain_engine': 'active' if WAGERBRAIN_AVAILABLE else 'fallback'
            }

        except Exception as e:
            logger.error(f"❌ Mathematical analysis error: {e}")
            return self.fallback_mathematical_analysis(prop_data, confidence_score)

    def wagerbrain_statistical_analysis(self, player_stats: Dict, prop_data: Dict) -> Dict:
        """Advanced statistical analysis using WagerBrain"""
        try:
            if not player_stats.get('recent_averages'):
                return {'volatility': 0.1, 'confidence_interval': [0, 0], 'note': 'insufficient_data'}
            
            prop_type = prop_data['prop_type']
            line_value = prop_data['line_value']
            
            # Get recent average
            avg_key = f"avg_{prop_type}"
            recent_avg = player_stats['recent_averages'].get(avg_key, line_value)
            
            # Calculate volatility (standard deviation estimation)
            volatility = abs(recent_avg - line_value) / line_value if line_value > 0 else 0.1
            volatility = max(0.05, min(0.5, volatility))  # Reasonable bounds
            
            # Calculate confidence intervals
            std_dev = recent_avg * volatility
            confidence_interval_95 = [
                max(0, recent_avg - 1.96 * std_dev),
                recent_avg + 1.96 * std_dev
            ]
            
            # Z-score calculation
            z_score = (line_value - recent_avg) / std_dev if std_dev > 0 else 0
            
            # Probability of hitting the over based on normal distribution
            if SCIPY_AVAILABLE:
                prob_over = 1 - norm.cdf(line_value, recent_avg, std_dev)
            else:
                # Simple approximation without scipy
                if z_score > 2:
                    prob_over = 0.025
                elif z_score > 1:
                    prob_over = 0.16
                elif z_score > 0:
                    prob_over = 0.5 - (z_score * 0.34)
                elif z_score > -1:
                    prob_over = 0.5 + (abs(z_score) * 0.34)
                elif z_score > -2:
                    prob_over = 0.84
                else:
                    prob_over = 0.975
            
            return {
                'volatility': round(volatility, 3),
                'confidence_interval': [round(ci, 2) for ci in confidence_interval_95],
                'z_score': round(z_score, 3),
                'probability_over': round(prob_over, 4),
                'probability_under': round(1 - prob_over, 4),
                'standard_deviation': round(std_dev, 3),
                'recent_average': round(recent_avg, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Statistical analysis error: {e}")
            return {'volatility': 0.1, 'error': str(e)}
    
    def run_monte_carlo_simulation(self, prop_data: Dict, player_stats: Dict, simulations: int = None) -> Dict:
        """Run Monte Carlo simulation for prop outcome"""
        try:
            if simulations is None:
                simulations = self.config.monte_carlo_simulations
                
            if not player_stats.get('recent_averages'):
                return {'hit_rate_over': 0.5, 'simulations': 0, 'note': 'insufficient_data'}
            
            prop_type = prop_data['prop_type']
            line_value = prop_data['line_value']
            
            avg_key = f"avg_{prop_type}"
            recent_avg = player_stats['recent_averages'].get(avg_key, line_value)
            
            # Estimate standard deviation
            std_dev = recent_avg * 0.2  # Assume 20% coefficient of variation
            
            # Run Monte Carlo simulation
            np.random.seed(42)  # For reproducible results
            simulated_values = np.random.normal(recent_avg, std_dev, simulations)
            
            # Calculate hit rate
            hits_over = np.sum(simulated_values > line_value)
            hit_rate_over = hits_over / simulations
            
            # Calculate percentiles
            percentiles = np.percentile(simulated_values, [5, 25, 50, 75, 95])
            
            return {
                'hit_rate_over': round(hit_rate_over, 4),
                'hit_rate_under': round(1 - hit_rate_over, 4),
                'simulations': simulations,
                'percentiles': {
                    '5th': round(percentiles[0], 2),
                    '25th': round(percentiles[1], 2),
                    '50th': round(percentiles[2], 2),
                    '75th': round(percentiles[3], 2),
                    '95th': round(percentiles[4], 2)
                },
                'expected_outcome': round(recent_avg, 2),
                'simulation_std': round(np.std(simulated_values), 3)
            }
            
        except Exception as e:
            logger.error(f"❌ Monte Carlo simulation error: {e}")
            return {'hit_rate_over': 0.5, 'error': str(e)}
    
    def calculate_sharpe_ratio(self, expected_return: float, volatility: float) -> float:
        """Calculate Sharpe ratio for risk-adjusted returns"""
        try:
            if volatility == 0:
                return 0
            return (expected_return - self.config.risk_free_rate) / volatility
        except:
            return 0
    
    def generate_wagerbrain_recommendation(self, confidence_score: float, wagerbrain_analysis: Dict) -> str:
        """Generate recommendation using WagerBrain analysis"""
        try:
            expected_value = wagerbrain_analysis.get('expected_value', 0)
            kelly_size = wagerbrain_analysis.get('kelly_criterion', 0)
            edge = wagerbrain_analysis.get('edge', 0)
            
            # Enhanced recommendation logic using config thresholds
            if expected_value > 0.05 and edge > 0.03 and kelly_size > 0.01:
                if confidence_score >= self.confidence_thresholds['high']:
                    return "STRONG_BET"
                elif confidence_score >= self.confidence_thresholds['medium']:
                    return "MODERATE_BET"
                else:
                    return "WEAK_BET"
            elif expected_value > 0.02 and edge > self.config.min_edge_threshold:
                return "WEAK_BET"
            elif expected_value < -0.03 or edge < -0.05:
                return "STRONG_AVOID"
            else:
                return "AVOID"
                
        except Exception as e:
            logger.error(f"❌ Recommendation error: {e}")
            return self.generate_basic_recommendation(confidence_score)
    
    def generate_basic_recommendation(self, confidence_score: float) -> str:
        """Fallback recommendation logic"""
        if confidence_score >= self.confidence_thresholds['high']:
            return "STRONG_BET"
        elif confidence_score >= self.confidence_thresholds['medium']:
            return "MODERATE_BET"
        elif confidence_score >= self.confidence_thresholds['low']:
            return "WEAK_BET"
        else:
            return "AVOID"
    
    def fallback_mathematical_analysis(self, prop_data: Dict, confidence_score: float) -> Dict:
        """Fallback mathematical analysis when WagerBrain is unavailable"""
        odds = prop_data.get('odds', '-110')
        
        implied_prob = self.fallback_implied_probability(odds)
        expected_value = self.fallback_expected_value(confidence_score, odds)
        kelly_size = self.fallback_kelly_criterion(confidence_score, odds)
        
        return {
            'expected_value': round(expected_value, 4),
            'kelly_criterion': round(kelly_size, 4),
            'implied_probability': round(implied_prob, 4),
            'true_probability': round(confidence_score, 4),
            'edge': round(confidence_score - implied_prob, 4),
            'sharpe_ratio': 0.0,
            'statistical_analysis': {'volatility': 0.1},
            'monte_carlo': {'hit_rate_over': confidence_score},
            'wagerbrain_engine': 'fallback'
        }

    # Fallback mathematical functions
    def fallback_implied_probability(self, odds: str) -> float:
        """Fallback implied probability calculation"""
        try:
            if isinstance(odds, str) and (odds.startswith('+') or odds.startswith('-')):
                odds_value = int(odds)
            else:
                odds_value = -110
            
            if odds_value > 0:
                return 100 / (odds_value + 100)
            else:
                return abs(odds_value) / (abs(odds_value) + 100)
        except:
            return 0.5263  # -110 implied probability
    
    def fallback_expected_value(self, true_prob: float, odds: str) -> float:
        """Fallback expected value calculation"""
        try:
            implied_prob = self.fallback_implied_probability(odds)
            return true_prob - implied_prob
        except:
            return 0.0
    
    def fallback_kelly_criterion(self, true_prob: float, odds: str) -> float:
        """Fallback Kelly criterion calculation"""
        try:
            if isinstance(odds, str) and (odds.startswith('+') or odds.startswith('-')):
                odds_value = int(odds)
            else:
                odds_value = -110
            
            if odds_value > 0:
                decimal_odds = (odds_value / 100) + 1
            else:
                decimal_odds = (100 / abs(odds_value)) + 1
            
            kelly = (true_prob * decimal_odds - 1) / (decimal_odds - 1)
            return max(0, min(self.config.kelly_max_fraction, kelly))
        except:
            return 0.0

    # Analysis methods
    def analyze_recent_performance(self, player_stats: Dict, prop_data: Dict) -> Dict:
        """Analyze recent performance trends"""
        try:
            if not player_stats.get('recent_averages'):
                return {'score': 0.5, 'trend': 'insufficient_data', 'note': 'No recent averages available'}
            
            prop_type = prop_data['prop_type']
            line_value = prop_data['line_value']
            recent_averages = player_stats['recent_averages']
            
            avg_key = f"avg_{prop_type}"
            if avg_key not in recent_averages:
                return {'score': 0.5, 'trend': 'no_matching_stat', 'note': f'No {prop_type} average found'}
            
            recent_avg = recent_averages[avg_key]
            
            # Enhanced hit rate calculation
            ratio = recent_avg / line_value if line_value > 0 else 0
            
            if ratio >= 1.20:
                hit_rate = 0.80
            elif ratio >= 1.15:
                hit_rate = 0.75
            elif ratio >= 1.10:
                hit_rate = 0.70
            elif ratio >= 1.05:
                hit_rate = 0.65
            elif ratio >= 1.02:
                hit_rate = 0.58
            elif ratio >= 0.98:
                hit_rate = 0.52
            elif ratio >= 0.95:
                hit_rate = 0.45
            elif ratio >= 0.90:
                hit_rate = 0.38
            elif ratio >= 0.85:
                hit_rate = 0.30
            else:
                hit_rate = 0.25
            
            # Determine trend
            if ratio >= 1.15:
                trend = "strongly_positive"
            elif ratio >= 1.05:
                trend = "positive"
            elif ratio >= 0.95:
                trend = "stable"
            elif ratio >= 0.85:
                trend = "negative"
            else:
                trend = "strongly_negative"
            
            return {
                'score': hit_rate,
                'hit_rate': hit_rate,
                'recent_average': recent_avg,
                'line_value': line_value,
                'trend': trend,
                'avg_vs_line_ratio': ratio,
                'games_analyzed': player_stats.get('games_played', 'unknown'),
                'note': f'Average {recent_avg:.2f} vs Line {line_value} (ratio: {ratio:.3f})'
            }
            
        except Exception as e:
            logger.error(f"❌ Recent performance analysis error: {e}")
            return {'score': 0.5, 'error': str(e)}
    
    def analyze_historical_trends(self, player_stats: Dict, prop_data: Dict) -> Dict:
        """Analyze long-term historical trends"""
        try:
            if not player_stats.get('recent_averages'):
                return {'score': 0.5, 'trend': 'insufficient_data'}
            
            prop_type = prop_data['prop_type']
            line_value = prop_data['line_value']
            
            consistency_score = 0.7
            recent_averages = player_stats['recent_averages']
            avg_key = f"avg_{prop_type}"
            
            if avg_key in recent_averages:
                season_avg = recent_averages[avg_key]
                historical_ratio = season_avg / line_value if line_value > 0 else 0
                historical_score = min(max(historical_ratio * 0.5, 0.2), 0.8)
            else:
                historical_score = 0.5
                season_avg = None
            
            final_score = (historical_score * 0.7) + (consistency_score * 0.3)
            
            return {
                'score': final_score,
                'season_average': season_avg,
                'line_value': line_value,
                'historical_ratio': historical_ratio if season_avg else None,
                'consistency': consistency_score,
                'sample_size': player_stats.get('total_games', 'unknown'),
                'note': 'Based on available season averages'
            }
            
        except Exception as e:
            logger.error(f"❌ Historical analysis error: {e}")
            return {'score': 0.5, 'error': str(e)}
    
    def analyze_opponent_matchup(self, opponent_data: Optional[Dict], prop_data: Dict) -> Dict:
        """Analyze opponent defensive strength"""
        try:
            if not opponent_data:
                return {'score': 0.5, 'note': 'no_opponent_data'}
            
            sport = prop_data['sport']
            
            if sport == "MLB":
                return self.analyze_mlb_pitching_matchup(opponent_data, prop_data)
            else:
                return {'score': 0.5, 'note': f'{sport}_analysis_placeholder'}
                
        except Exception as e:
            return {'score': 0.5, 'error': str(e)}
    
    def analyze_mlb_pitching_matchup(self, pitching_data: Dict, prop_data: Dict) -> Dict:
        """Analyze MLB pitching matchup"""
        try:
            prop_type = prop_data['prop_type']
            
            # Enhanced matchup analysis
            matchup_scores = {
                'hits': 0.55,
                'runs': 0.52,
                'rbis': 0.50,
                'strikeouts': 0.48,
                'home_runs': 0.45
            }
            
            opponent_score = matchup_scores.get(prop_type, 0.50)
            difficulty = 'moderate'
            
            # Adjust based on opponent data if available
            if 'era' in pitching_data:
                era = pitching_data['era']
                if era > 4.5:
                    opponent_score += 0.1
                    difficulty = 'favorable'
                elif era < 3.5:
                    opponent_score -= 0.1
                    difficulty = 'difficult'
            
            return {
                'score': max(0.2, min(0.8, opponent_score)),
                'note': f'MLB {prop_type} matchup analysis',
                'difficulty': difficulty,
                'opponent_stats': pitching_data
            }
            
        except Exception as e:
            return {'score': 0.5, 'error': str(e)}
    
    def analyze_situational_factors(self, prop_data: Dict, player_stats: Dict) -> Dict:
        """Analyze situational factors"""
        try:
            sport = prop_data['sport']
            
            # Enhanced situational analysis
            home_away_score = 0.5  # Would need actual home/away data
            
            # Weather factor (relevant for outdoor sports)
            weather_score = 0.5
            if sport in ['MLB', 'NFL', 'GOLF']:
                weather_score = 0.55  # Slightly favorable assumption
            
            rest_score = 0.5  # Would need actual rest data
            form_score = 0.5   # Would need recent form data
            
            # Weighted situational score
            situational_score = (
                home_away_score * 0.3 +
                weather_score * 0.25 +
                rest_score * 0.25 +
                form_score * 0.2
            )
            
            return {
                'score': max(0.2, min(0.8, situational_score)),
                'components': {
                    'home_away': home_away_score,
                    'weather': weather_score,
                    'rest': rest_score,
                    'form': form_score
                },
                'note': f'{sport} situational analysis'
            }
            
        except Exception as e:
            return {'score': 0.5, 'error': str(e)}
    
    def calculate_confidence_score(self, recent_analysis: Dict, historical_analysis: Dict, 
                                 opponent_analysis: Dict, situational_analysis: Dict) -> float:
        """Calculate weighted confidence score"""
        try:
            recent_score = recent_analysis.get('score', 0.5)
            historical_score = historical_analysis.get('score', 0.5)
            opponent_score = opponent_analysis.get('score', 0.5)
            situational_score = situational_analysis.get('score', 0.5)
            
            weighted_score = (
                recent_score * self.factors['recent_form'] +
                historical_score * self.factors['historical'] +
                opponent_score * self.factors['opponent_strength'] +
                situational_score * (self.factors['home_away'] + self.factors['weather'] + self.factors['rest_days'])
            )
            
            return max(0.0, min(1.0, weighted_score))
            
        except Exception as e:
            logger.error(f"❌ Confidence calculation error: {e}")
            return 0.5
    
    def create_error_analysis(self, prop_data: Dict, error_msg: str) -> Dict:
        """Create error analysis result"""
        return {
            'prop_id': prop_data.get('id'),
            'player_name': prop_data.get('player_name', 'Unknown'),
            'prop_type': prop_data.get('prop_type', 'Unknown'),
            'line_value': prop_data.get('line_value', 0),
            'sport': prop_data.get('sport', 'Unknown'),
            'confidence_score': 0.0,
            'recommendation': 'ERROR',
            'analysis_components': {
                'recent_performance': {'score': 0.0, 'error': error_msg},
                'historical_trends': {'score': 0.0, 'error': error_msg},
                'opponent_matchup': {'score': 0.0, 'error': error_msg},
                'situational_factors': {'score': 0.0, 'error': error_msg}
            },
            'wagerbrain_analysis': {'error': error_msg, 'wagerbrain_engine': 'error'},
            'error': error_msg,
            'analyzed_at': datetime.now().isoformat()
        }

    # Additional utility methods for enhanced functionality
    def batch_analyze_props(self, props_list: List[Dict], 
                           player_stats_dict: Dict[str, Dict],
                           opponent_data_dict: Optional[Dict[str, Dict]] = None) -> List[Dict]:
        """Analyze multiple props in batch"""
        results = []
        total_props = len(props_list)
        
        logger.info(f"🔄 Starting batch analysis of {total_props} props")
        
        for i, prop_data in enumerate(props_list, 1):
            try:
                player_name = prop_data.get('player_name')
                player_stats = player_stats_dict.get(player_name, {})
                opponent_data = opponent_data_dict.get(player_name) if opponent_data_dict else None
                
                result = self.analyze_prop(prop_data, player_stats, opponent_data)
                results.append(result)
                
                if i % 10 == 0:
                    logger.info(f"📊 Processed {i}/{total_props} props")
                    
            except Exception as e:
                logger.error(f"❌ Error analyzing prop {i}: {e}")
                error_result = self.create_error_analysis(prop_data, str(e))
                results.append(error_result)
        
        logger.info(f"✅ Batch analysis complete. Processed {len(results)} props")
        return results

    def get_analysis_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics from analysis results"""
        if not results:
            return {'error': 'No results to summarize'}
        
        # Filter out error results
        valid_results = [r for r in results if r.get('error') is None]
        
        if not valid_results:
            return {'error': 'No valid results to summarize'}
        
        recommendations = [r['recommendation'] for r in valid_results]
        confidence_scores = [r['confidence_score'] for r in valid_results]
        
        # Extract WagerBrain metrics
        expected_values = []
        kelly_fractions = []
        edges = []
        
        for r in valid_results:
            wb_analysis = r.get('wagerbrain_analysis', {})
            expected_values.append(wb_analysis.get('expected_value', 0))
            kelly_fractions.append(wb_analysis.get('kelly_criterion', 0))
            edges.append(wb_analysis.get('edge', 0))
        
        summary = {
            'total_props_analyzed': len(results),
            'valid_analyses': len(valid_results),
            'error_count': len(results) - len(valid_results),
            'recommendations': {
                'STRONG_BET': recommendations.count('STRONG_BET'),
                'MODERATE_BET': recommendations.count('MODERATE_BET'),
                'WEAK_BET': recommendations.count('WEAK_BET'),
                'AVOID': recommendations.count('AVOID'),
                'STRONG_AVOID': recommendations.count('STRONG_AVOID'),
                'ERROR': recommendations.count('ERROR')
            },
            'confidence_stats': {
                'mean': round(np.mean(confidence_scores), 3),
                'median': round(np.median(confidence_scores), 3),
                'std': round(np.std(confidence_scores), 3),
                'min': round(min(confidence_scores), 3),
                'max': round(max(confidence_scores), 3)
            },
            'expected_value_stats': {
                'mean': round(np.mean(expected_values), 4),
                'median': round(np.median(expected_values), 4),
                'positive_ev_count': sum(1 for ev in expected_values if ev > 0),
                'total_expected_return': round(sum(expected_values), 4)
            },
            'kelly_stats': {
                'mean': round(np.mean(kelly_fractions), 4),
                'median': round(np.median(kelly_fractions), 4),
                'max_recommended_bet': round(max(kelly_fractions), 4),
                'total_bankroll_allocation': round(sum(kelly_fractions), 4)
            },
            'edge_stats': {
                'mean': round(np.mean(edges), 4),
                'positive_edge_count': sum(1 for edge in edges if edge > 0),
                'best_edge': round(max(edges), 4),
                'worst_edge': round(min(edges), 4)
            },
            'sports_breakdown': self._get_sports_breakdown(valid_results),
            'wagerbrain_status': 'active' if WAGERBRAIN_AVAILABLE else 'fallback',
            'generated_at': datetime.now().isoformat()
        }
        
        return summary

    def _get_sports_breakdown(self, results: List[Dict]) -> Dict:
        """Get breakdown of results by sport"""
        sports_data = {}
        
        for result in results:
            sport = result.get('sport', 'Unknown')
            if sport not in sports_data:
                sports_data[sport] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'avg_expected_value': 0,
                    'recommendations': {}
                }
            
            sports_data[sport]['count'] += 1
            sports_data[sport]['avg_confidence'] += result.get('confidence_score', 0)
            
            wb_analysis = result.get('wagerbrain_analysis', {})
            sports_data[sport]['avg_expected_value'] += wb_analysis.get('expected_value', 0)
            
            rec = result.get('recommendation', 'UNKNOWN')
            if rec not in sports_data[sport]['recommendations']:
                sports_data[sport]['recommendations'][rec] = 0
            sports_data[sport]['recommendations'][rec] += 1
        
        # Calculate averages
        for sport, data in sports_data.items():
            if data['count'] > 0:
                data['avg_confidence'] = round(data['avg_confidence'] / data['count'], 3)
                data['avg_expected_value'] = round(data['avg_expected_value'] / data['count'], 4)
        
        return sports_data

    def export_results_to_csv(self, results: List[Dict], filename: str = None) -> str:
        """Export analysis results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prop_analysis_results_{timestamp}.csv"
        
        # Convert results to DataFrame
        data = []
        for result in results:
            row = {
                'prop_id': result.get('prop_id'),
                'player_name': result.get('player_name'),
                'prop_type': result.get('prop_type'),
                'line_value': result.get('line_value'),
                'sport': result.get('sport'),
                'confidence_score': result.get('confidence_score'),
                'recommendation': result.get('recommendation'),
                'analyzed_at': result.get('analyzed_at'),
                'error': result.get('error')
            }
            
            # Add WagerBrain metrics
            wb_analysis = result.get('wagerbrain_analysis', {})
            row.update({
                'expected_value': wb_analysis.get('expected_value'),
                'kelly_fraction': wb_analysis.get('kelly_criterion'),
                'implied_probability': wb_analysis.get('implied_probability'),
                'true_probability': wb_analysis.get('true_probability'),
                'edge': wb_analysis.get('edge'),
                'sharpe_ratio': wb_analysis.get('sharpe_ratio'),
                'wagerbrain_engine': wb_analysis.get('wagerbrain_engine')
            })
            
            # Add component scores
            components = result.get('analysis_components', {})
            row.update({
                'recent_performance_score': components.get('recent_performance', {}).get('score'),
                'historical_trends_score': components.get('historical_trends', {}).get('score'),
                'opponent_matchup_score': components.get('opponent_matchup', {}).get('score'),
                'situational_factors_score': components.get('situational_factors', {}).get('score')
            })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"📄 Results exported to {filename}")
        return filename

    def get_top_recommendations(self, results: List[Dict], 
                               recommendation_type: str = "STRONG_BET", 
                               limit: int = 10) -> List[Dict]:
        """Get top recommendations of a specific type"""
        filtered_results = [r for r in results 
                          if r.get('recommendation') == recommendation_type and r.get('error') is None]
        
        # Sort by expected value for bets, by confidence for avoids
        if recommendation_type in ["STRONG_BET", "MODERATE_BET", "WEAK_BET"]:
            filtered_results.sort(
                key=lambda x: x.get('wagerbrain_analysis', {}).get('expected_value', 0), 
                reverse=True
            )
        else:
            filtered_results.sort(
                key=lambda x: x.get('confidence_score', 0), 
                reverse=False
            )
        
        return filtered_results[:limit]

    def validate_analysis_quality(self, results: List[Dict]) -> Dict:
        """Validate the quality and consistency of analysis results"""
        if not results:
            return {'status': 'error', 'message': 'No results to validate'}
        
        valid_results = [r for r in results if r.get('error') is None]
        
        if not valid_results:
            return {'status': 'error', 'message': 'No valid results to validate'}
        
        # Calculate quality metrics
        completion_rate = len(valid_results) / len(results)
        error_rate = (len(results) - len(valid_results)) / len(results)
        
        # Check recommendation diversity
        recommendations = [r.get('recommendation') for r in valid_results]
        unique_recommendations = set(recommendations)
        diversity_score = len(unique_recommendations) / 5  # 5 possible recommendation types
        
        # Check mathematical consistency
        consistency_checks = []
        for result in valid_results:
            wb_analysis = result.get('wagerbrain_analysis', {})
            edge = wb_analysis.get('edge', 0)
            expected_value = wb_analysis.get('expected_value', 0)
            kelly_fraction = wb_analysis.get('kelly_criterion', 0)
            
            # Check if edge and expected value have consistent signs
            if edge * expected_value >= 0:
                consistency_checks.append(1)
            else:
                consistency_checks.append(0)
            
            # Check if kelly fraction is reasonable given expected value
            if expected_value > 0 and kelly_fraction > 0:
                consistency_checks.append(1)
            elif expected_value <= 0 and kelly_fraction <= 0.01:
                consistency_checks.append(1)
            else:
                consistency_checks.append(0)
        
        mathematical_consistency = np.mean(consistency_checks) if consistency_checks else 0.0
        
        # Overall quality score
        quality_score = (
            completion_rate * 0.3 +
            (1 - error_rate) * 0.3 +
            diversity_score * 0.2 +
            mathematical_consistency * 0.2
        )
        
        quality_metrics = {
            'completion_rate': round(completion_rate, 3),
            'error_rate': round(error_rate, 3),
            'recommendation_diversity': round(diversity_score, 3),
            'mathematical_consistency': round(mathematical_consistency, 3),
            'overall_quality_score': round(quality_score, 3),
            'status': 'excellent' if quality_score > 0.9 else 'good' if quality_score > 0.8 else 'acceptable' if quality_score > 0.6 else 'poor',
            'total_results': len(results),
            'valid_results': len(valid_results),
            'unique_recommendations': len(unique_recommendations),
            'wagerbrain_available': WAGERBRAIN_AVAILABLE
        }
        
        return quality_metrics


# Legacy compatibility and convenience functions
AnalysisEngine = WagerBrainAnalysisEngine

def create_analysis_engine(config: Optional[AnalysisConfig] = None) -> WagerBrainAnalysisEngine:
    """Factory function to create analysis engine instance"""
    return WagerBrainAnalysisEngine(config)


# Test and example usage
if __name__ == "__main__":
    print("🚀 Starting WagerBrain Analysis Engine Test...")
    
    # Test configuration
    test_config = AnalysisConfig(
        confidence_thresholds={
            'high': 0.80,
            'medium': 0.70,
            'low': 0.60
        },
        kelly_max_fraction=0.20,
        monte_carlo_simulations=5000
    )
    
    # Create engine
    try:
        engine = WagerBrainAnalysisEngine(test_config)
        
        # Example prop data
        sample_prop = {
            'id': 'prop_001',
            'player_name': 'Mike Trout',
            'prop_type': 'hits',
            'line_value': 1.5,
            'odds': '+110',
            'sport': 'MLB'
        }
        
        # Example player stats
        sample_stats = {
            'recent_averages': {
                'avg_hits': 1.8,
                'avg_runs': 1.2,
                'avg_rbis': 1.5
            },
            'games_played': 15,
            'total_games': 140
        }
        
        # Example opponent data
        sample_opponent = {
            'era': 4.2,
            'whip': 1.3,
            'k_9': 8.5
        }
        
        # Run analysis
        print("🔬 Running sample analysis...")
        result = engine.analyze_prop(sample_prop, sample_stats, sample_opponent)
        
        print(f"\n✅ Analysis Results:")
        print(f"   Player: {result['player_name']}")
        print(f"   Prop: {result['prop_type']} {result['line_value']}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence_score']:.1%}")
        
        wb_analysis = result['wagerbrain_analysis']
        print(f"   Expected Value: {wb_analysis.get('expected_value', 0):.4f}")
        print(f"   Kelly Fraction: {wb_analysis.get('kelly_criterion', 0):.4f}")
        print(f"   Edge: {wb_analysis.get('edge', 0):.4f}")
        print(f"   Engine: {wb_analysis.get('wagerbrain_engine', 'unknown')}")
        
        # Test batch analysis
        print(f"\n🔄 Testing batch analysis...")
        props_list = [sample_prop] * 3  # Analyze same prop 3 times for demo
        player_stats_dict = {sample_prop['player_name']: sample_stats}
        opponent_dict = {sample_prop['player_name']: sample_opponent}
        
        batch_results = engine.batch_analyze_props(props_list, player_stats_dict, opponent_dict)
        summary = engine.get_analysis_summary(batch_results)
        
        print(f"   Batch Results: {len(batch_results)} props analyzed")
        print(f"   Valid Analyses: {summary['valid_analyses']}")
        print(f"   Strong Bets: {summary['recommendations']['STRONG_BET']}")
        print(f"   Average Confidence: {summary['confidence_stats']['mean']:.3f}")
        print(f"   Average Expected Value: {summary['expected_value_stats']['mean']:.4f}")
        
        # Test quality validation
        quality = engine.validate_analysis_quality(batch_results)
        print(f"   Quality Score: {quality['overall_quality_score']:.3f} ({quality['status']})")
        
        print(f"\n🎯 WagerBrain Analysis Engine test complete!")
        print(f"   WagerBrain Status: {'✅ Active' if WAGERBRAIN_AVAILABLE else '⚠️ Fallback'}")
        print(f"   SciPy Status: {'✅ Available' if SCIPY_AVAILABLE else '⚠️ Limited'}")
        
    except Exception as e:
        print(f"❌ Analysis Engine test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("🏁 Analysis Engine initialization complete!")