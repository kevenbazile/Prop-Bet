from analysis_engine import WagerBrainAnalysisEngine
from prop_parser import PropParser

picks = [
    'Tarik Skubal Over 4.5 Hits Allowed',
    'Tarik Skubal Over 45.5 Pitcher Fantasy Score',
    'Neptune Over 29 MAP 4 Kills',
    'Dustin Crum Over 231.5 Pass Yards'
]

parser = PropParser()
engine = WagerBrainAnalysisEngine()

print('🎯 DAILY PICKS ANALYSIS')
print('='*40)

for i, pick in enumerate(picks, 1):
    print(f'\n📝 Pick {i}: {pick}')

    prop = parser.parse_single_prop(pick)
    if prop:
        prop['odds'] = '+120'

        prop_type = prop['prop_type']
        line_value = prop['line_value']
        prop_key = 'avg_' + prop_type
        stats = {'recent_averages': {prop_key: line_value + 0.2}}

        result = engine.analyze_prop(prop, stats)
        print(f'   Recommendation: {result["recommendation"]}')
        print(f'   Confidence: {result["confidence_score"]:.1%}')
        print(f'   Hit Probability: {result["wagerbrain_analysis"]["true_probability"]:.1%}') 
    else:
        print('   ❌ Could not parse')

print('\n✅ Analysis complete')