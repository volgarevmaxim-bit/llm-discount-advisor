import unittest

from advisor.changes import compare_decisions, decision_snapshot_compatible, hysteresis_default_change


class ChangeTests(unittest.TestCase):
    def test_legacy_snapshot_skips_market_comparison(self):
        old = {"generated_at": "2026-08-19T00:00:00Z", "models": [{"slug": "vendor/model"}]}
        new = {"schema_version": "1.0", "generated_at": "2026-08-20T00:00:00Z", "profiles": []}
        result = compare_decisions(old, new)
        self.assertEqual(result["status"], "comparison_skipped")
        self.assertEqual(result["reason"], "schema_migration")

    def test_same_day_decision_comparison_is_idempotent(self):
        surface = {"schema_version": "1.0", "generated_at": "2026-08-20T01:00:00Z", "profiles": [{"profile": "code", "roles": {"balanced_default": {"ranking_key": "vendor/model", "provider": "P"}}}]}
        self.assertEqual(compare_decisions(surface, surface)["events"], [])

    def test_default_change_requires_two_confirmations(self):
        before = "vendor/old"
        after = "vendor/new"
        self.assertFalse(hysteresis_default_change(before, after, [after]))
        self.assertTrue(hysteresis_default_change(before, after, [after, after]))


if __name__ == "__main__":
    unittest.main()
