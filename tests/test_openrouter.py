import unittest

from advisor.openrouter import endpoint_slug


class EndpointIdentityTests(unittest.TestCase):
    def test_endpoint_slug_prefers_unique_id_over_family_canonical_slug(self):
        model = {'id': 'vendor/model:free', 'canonical_slug': 'vendor/model-20260820'}
        self.assertEqual(endpoint_slug(model), 'vendor/model:free')


if __name__ == '__main__':
    unittest.main()