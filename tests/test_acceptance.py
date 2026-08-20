import unittest
from advisor.acceptance import code_top10, compare
from advisor.testsupport import synthetic_models


class AcceptanceTests(unittest.TestCase):
    def test_comparison_returns_real_overlap_shape(self):
        result = compare(synthetic_models(25))
        self.assertIn('overlap', result)
        self.assertEqual(len(result['full_top10']), 10)

    def test_top10_has_one_entry_per_canonical_family(self):
        rows = []
        for i in range(10):
            rows.append({
                'slug': f'vendor/m{i}', 'canonical_slug': f'vendor/family-{i}',
                'price_in': i + 1, 'price_out': i + 1, 'coding': 80 - i,
                'context': 200000, 'has_tools': True, 'uptime_1d': 99,
            })
        duplicate = dict(rows[0])
        duplicate['slug'] = 'vendor/m0:free'
        duplicate['price_in'] = 0
        duplicate['price_out'] = 0
        rows.append(duplicate)

        result = code_top10(rows)

        self.assertEqual(len(result), 10)
        self.assertEqual(len(set(result)), 10)
        self.assertIn('vendor/family-0', result)


if __name__ == '__main__':
    unittest.main()
