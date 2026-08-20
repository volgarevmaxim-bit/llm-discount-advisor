import unittest
from advisor.normalize import normalize_model


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.meta = {
            'canonical_slug': 'vendor/model', 'id': 'vendor/model', 'name': 'Model',
            'pricing': {'prompt': '0.000002', 'completion': '0.000004'},
            'context_length': 200000, 'supported_parameters': ['tools'],
            'architecture': {'input_modalities': ['text'], 'output_modalities': ['text']},
            'benchmarks': {'artificial_analysis': {'intelligence_index': 60, 'coding_index': 70, 'agentic_index': 50}},
            'reasoning': {'default_effort': 'high', 'mandatory': True, 'supported_efforts': ['low', 'high']},
        }

    def test_endpoint_price_discount_base_and_provider(self):
        result = normalize_model(self.meta, [
            {'provider_name': 'Expensive', 'uptime_last_1d': 99, 'pricing': {'prompt': '0.000002', 'completion': '0.000004'}},
            {'provider_name': 'Cheap', 'uptime_last_1d': 99.5, 'pricing': {'prompt': '0.000001', 'completion': '0.000002', 'discount': 0.5}},
        ])
        self.assertEqual(result['best_provider'], 'Cheap')
        self.assertAlmostEqual(result['price_in'], 1.0)
        self.assertAlmostEqual(result['base_price'], 2.5)
        self.assertEqual(result['reasoning_default_effort'], 'high')
        self.assertTrue(result['reasoning_mandatory'])

    def test_overrides_are_not_dropped(self):
        result = normalize_model(self.meta, [
            {'provider_name': 'P', 'uptime_last_1d': 100, 'pricing': {'prompt': '0.000002', 'completion': '0.000004', 'overrides': [{'min_prompt_tokens': 128000}]}}
        ])
        self.assertTrue(result['has_tiered_pricing'])
        self.assertEqual(len(result['pricing_overrides']), 1)


if __name__ == '__main__':
    unittest.main()
