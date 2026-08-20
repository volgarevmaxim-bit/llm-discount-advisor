import unittest
from datetime import datetime, timezone
from advisor.gate import gate


def model(slug, quality=70, coding=70, da=None, price='0.000001', created=None, alias=None):
    return {'id': slug, 'canonical_slug': slug, 'name': slug, 'created': created or datetime.now(timezone.utc).timestamp(), 'pricing': {'prompt': price, 'completion': price}, 'benchmarks': {'artificial_analysis': {'intelligence_index': quality, 'coding_index': coding, 'agentic_index': quality}, 'design_arena': da or []}, 'architecture': {'output_modalities': ['text']}, 'alias_target': alias}


class GateTests(unittest.TestCase):
    def test_gate_uses_canonical_slug_and_records_reject(self):
        strong = model('vendor/strong')
        weak = model('vendor/weak', quality=None, coding=None, da=[])
        passed, rejected = gate([strong, weak], now=datetime.now(timezone.utc))
        self.assertEqual([m['canonical_slug'] for m in passed], ['vendor/strong'])
        self.assertEqual(rejected[-1]['slug'], 'vendor/weak')
        self.assertEqual(rejected[-1]['reason'], 'below_all_thresholds')

    def test_free_model_passes_g4(self):
        free = model('vendor/free', quality=None, coding=None, price='0')
        passed, rejected = gate([free])
        self.assertEqual(passed[0]['gate_reason'], ['G4:free'])
        self.assertFalse(rejected)

    def test_alias_rejected_before_gate(self):
        passed, rejected = gate([model('vendor/alias', alias='vendor/real')])
        self.assertFalse(passed)
        self.assertEqual(rejected[0]['reason'], 'alias')

    def test_recent_participation_passes_g6(self):
        da = [{'rank': 42, 'elo': 1227, 'category': str(i)} for i in range(6)]
        item = model('vendor/hy3', quality=None, coding=None, da=da, price='0.000001')
        passed, rejected = gate([item])
        self.assertEqual(passed[0]['gate_reason'], ['G6:participation'])
        self.assertFalse(rejected)

    def test_canonical_slug_is_not_replaced_by_id(self):
        item = model('vendor/canonical', quality=70)
        item['id'] = 'vendor/variant-id'
        passed, _ = gate([item])
        self.assertEqual(passed[0]['canonical_slug'], 'vendor/canonical')

if __name__ == '__main__':
    unittest.main()


class CanonicalKeyTests(unittest.TestCase):
    def test_suffix_remains_explicit(self):
        item = model('vendor/model:free', quality=70)
        passed, _ = gate([item])
        self.assertEqual(passed[0]['canonical_slug'], 'vendor/model:free')


    def test_variants_share_one_gate_family_and_free_variant_is_visible(self):
        base = model('vendor/model-family', quality=None, coding=None, price='0.000001')
        free = dict(base)
        free['id'] = 'vendor/model-family:free'
        free['pricing'] = {'prompt': '0', 'completion': '0'}

        passed, rejected = gate([base, free])

        self.assertEqual(len(passed), 2)
        self.assertEqual({item['canonical_slug'] for item in passed}, {'vendor/model-family'})
        self.assertTrue(all('G4:free' in item['gate_reason'] for item in passed))
        self.assertFalse(rejected)