from analysis_engine import WagerBrainAnalysisEngine
from prop_parser import PropParser

# Simple test
parser = PropParser()
engine = WagerBrainAnalysisEngine()

prop = parser.parse_single_prop('Luis Castillo + Jack Leiter Over 0.5 1st Inning Runs Allowed')
prop['odds'] = '+120'

stats = {
    'recent_averages': {
        'avg_runs_allowed_1st_inning': 0.8
    }
}

result = engine.analyze_prop(prop, stats)

print(f'Recommendation: {result["recommendation"]}')
print(f'Confidence: {result["confidence_score"]:.1%}')
print(f'Expected Value: {result["wagerbrain_analysis"]["expected_value"]:.4f}')