import unittest
from advisor.config import PROFILE_BY_KEY
from advisor.recommend import recommend


def row(slug, intelligence=70, coding=70, price_in=1, price_out=1, discount=0, mandatory=False, overpay=1):
    return {'slug': slug, 'name': slug, 'price_in': price_in, 'price_out': price_out, 'intelligence': intelligence, 'coding': coding, 'agentic': 60, 'context': 300000, 'has_tools': True, 'uptime_1d': 99.5, 'discount_max': discount, 'best_provider': 'P', 'provider_count': 2, 'overpay_ratio': overpay, 'reasoning_default_effort': 'medium', 'reasoning_mandatory': mandatory, 'has_tiered_pricing': False, 'base_price': 1}


class RecommendTests(unittest.TestCase):
    def test_bulk_rejects_mandatory_reasoning(self):
        result = recommend([row('bad', mandatory=True), row('good')], PROFILE_BY_KEY['bulk'])
        self.assertTrue(result['picks'])
        self.assertNotIn('bad', {p['slug'] for p in result['picks']})

    def test_every_card_has_one_sentence_reason(self):
        result = recommend([row('a'), row('b', price_in=0.2, price_out=0.2, discount=.5)], PROFILE_BY_KEY['chat'])
        self.assertTrue(result['picks'])
        self.assertTrue(all(p['reason'].endswith('.') for p in result['picks']))

if __name__ == '__main__':
    unittest.main()
