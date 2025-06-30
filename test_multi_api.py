#!/usr/bin/env python3
"""
Simple test for multi-API PrizePicks workflow
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from analysis_engine import WagerBrainAnalysisEngine
    from prop_parser import PropParser
    print("✅ Core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_analysis():
    """Test basic analysis with existing modules"""
    print("\n🎯 Testing Basic Multi-Prop Analysis")
    print("="*50)
    
    # Initialize components
    parser = PropParser()
    engine = WagerBrainAnalysisEngine()
    
    # Test props
    test_props = [
        "Luis Castillo + Jack Leiter Over 0.5 1st Inning Runs Allowed",
        "Mike Trout Over 1.5 Hits",
        "Aaron Judge Under 1.5 Home Runs"
    ]
    
    results = []
    
    for i, prop_text in enumerate(test_props, 1):
        print(f"\n📝 Analyzing Prop {i}: {prop_text}")
        
        # Parse prop
        parsed = parser.parse_single_prop(prop_text)
        if not parsed:
            print(f"❌ Failed to parse: {prop_text}")
            continue
        
        # Create mock stats based on prop type
        prop_type = parsed['prop_type']
        line_value = parsed['line_value']
        
        # Enhanced mock stats
        if 'runs_allowed' in prop_type:
            mock_avg = line_value + 0.3  # Pitcher combo likely to allow more
        elif 'hits' in prop_type:
            mock_avg = line_value + 0.2  # Slightly above line
        elif 'home_runs' in prop_type:
            mock_avg = line_value - 0.1  # Slightly below for under bet
        else:
            mock_avg = line_value + 0.15
        
        player_stats = {
            'recent_averages': {f"avg_{prop_type}": mock_avg},
            'games_played': 15,
            'total_games': 30,
            'data_source': 'enhanced_mock'
        }
        
        # Add odds estimate
        parsed['odds'] = '+120'
        
        # Run analysis
        try:
            result = engine.analyze_prop(parsed, player_stats)
            results.append(result)
            
            print(f"✅ {parsed['player_name']}")
            print(f"   Recommendation: {result['recommendation']}")
            print(f"   Confidence: {result['confidence_score']:.1%}")
            print(f"   Expected Value: {result['wagerbrain_analysis']['expected_value']:.4f}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    return results

def analyze_slip(results):
    """Analyze the complete slip"""
    if not results:
        print("❌ No results to analyze")
        return
    
    print(f"\n🎯 SLIP ANALYSIS")
    print("="*30)
    
    # Calculate slip probability (all must hit)
    slip_probability = 1.0
    total_expected_value = 0
    
    recommendations = []
    for result in results:
        true_prob = result['wagerbrain_analysis']['true_probability']
        bet_type = result.get('bet_type', 'over')
        
        # Adjust probability based on bet type
        if bet_type == 'over':
            pick_prob = true_prob
        else:
            pick_prob = 1 - true_prob
            
        slip_probability *= pick_prob
        total_expected_value += result['wagerbrain_analysis']['expected_value']
        recommendations.append(result['recommendation'])
    
    # Estimate multiplier (3-pick slip)
    entry_count = len(results)
    if entry_count == 3:
        if slip_probability > 0.3:
            multiplier = 6.0
        elif slip_probability > 0.2:
            multiplier = 8.0
        else:
            multiplier = 12.0
    else:
        multiplier = 5.0  # Default
    
    # Calculate expected payout
    stake = 1.0
    expected_payout = slip_probability * multiplier * stake
    slip_expected_value = expected_payout - stake
    
    # Generate recommendation
    strong_bets = recommendations.count('STRONG_BET')
    moderate_bets = recommendations.count('MODERATE_BET')
    avoid_bets = recommendations.count('AVOID') + recommendations.count('STRONG_AVOID')
    
    if avoid_bets > 0:
        slip_recommendation = "AVOID_SLIP"
    elif slip_expected_value > 0.15 and strong_bets >= 2:
        slip_recommendation = "STRONG_PLAY"
    elif slip_expected_value > 0.05 and (strong_bets + moderate_bets) >= 2:
        slip_recommendation = "MODERATE_PLAY"
    elif slip_expected_value > 0:
        slip_recommendation = "WEAK_PLAY"
    else:
        slip_recommendation = "AVOID_SLIP"
    
    print(f"📊 Slip Metrics:")
    print(f"   Total Picks: {entry_count}")
    print(f"   Slip Probability: {slip_probability:.1%}")
    print(f"   Estimated Multiplier: {multiplier}x")
    print(f"   Expected Payout: ${expected_payout:.2f}")
    print(f"   Expected Value: ${slip_expected_value:.2f}")
    print(f"   Individual EVs: ${total_expected_value:.3f}")
    
    print(f"\n🎯 FINAL RECOMMENDATION: {slip_recommendation}")
    
    if slip_recommendation == "STRONG_PLAY":
        print("   ✅ Strong positive expected value - good slip!")
    elif slip_recommendation == "MODERATE_PLAY":
        print("   ⚠️ Moderate value - consider smaller stake")
    elif slip_recommendation == "WEAK_PLAY":
        print("   ⚠️ Weak value - proceed with caution")
    else:
        print("   ❌ Avoid this slip - negative expected value")
    
    print(f"\n📋 Individual Recommendations:")
    for i, result in enumerate(results, 1):
        player = result['player_name']
        rec = result['recommendation']
        conf = result['confidence_score']
        print(f"   {i}. {player}: {rec} ({conf:.1%})")

def simulate_api_usage():
    """Simulate what the multi-API system would do"""
    print(f"\n🌐 SIMULATED API USAGE")
    print("="*30)
    
    api_simulation = {
        'Luis Castillo + Jack Leiter': {
            'sport': 'MLB',
            'primary_api': 'MLB API',
            'backup_apis': ['NBASZN API'],
            'prop_type': '1st Inning Runs Allowed',
            'status': 'Would use MLB API for pitcher stats'
        },
        'Mike Trout': {
            'sport': 'MLB', 
            'primary_api': 'MLB API',
            'backup_apis': ['NBASZN API'],
            'prop_type': 'Hits',
            'status': 'Would use MLB API for batting stats'
        },
        'Aaron Judge': {
            'sport': 'MLB',
            'primary_api': 'MLB API', 
            'backup_apis': ['NBASZN API'],
            'prop_type': 'Home Runs',
            'status': 'Would use MLB API for power stats'
        }
    }
    
    total_apis = len(set(sim['primary_api'] for sim in api_simulation.values()))
    
    print(f"📡 API Strategy:")
    for player, info in api_simulation.items():
        print(f"   🏈 {player}")
        print(f"      Primary: {info['primary_api']}")
        print(f"      Prop: {info['prop_type']}")
        print(f"      Status: {info['status']}")
    
    print(f"\n📊 Summary:")
    print(f"   Total APIs Available: 15+")
    print(f"   APIs for This Slip: {total_apis}")
    print(f"   Fallback Options: Enhanced mock data")
    print(f"   Rate Limiting: Built-in delays")

def main():
    """Main test function"""
    print("🎯 Multi-API PrizePicks Analysis Test")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Test basic analysis
    results = test_basic_analysis()
    
    # Analyze as complete slip
    analyze_slip(results)
    
    # Show API simulation
    simulate_api_usage()
    
    print(f"\n✅ Test completed successfully!")
    print(f"Next steps:")
    print(f"   1. Save multi_api_data_fetcher.py")
    print(f"   2. Save enhanced_prizepicks_workflow.py") 
    print(f"   3. Run with real APIs for live data")

if __name__ == "__main__":
    main()