import unittest

from advisor.config import PROFILE_BY_KEY
from advisor.decision import build_profile_decision


class DecisionSurfaceTests(unittest.TestCase):
    def test_profile_contract_and_three_roles_are_deterministic(self):
        ranking = {
            "quality_rows": [
                {"category": "coding", "ranking_key": "vendor/cheap-20260820", "permaslug": "vendor/cheap-20260820", "score": 68.0},
                {"category": "coding", "ranking_key": "vendor/best-20260820", "permaslug": "vendor/best-20260820", "score": 80.0},
                {"category": "coding", "ranking_key": "vendor/middle-20260820", "permaslug": "vendor/middle-20260820", "score": 78.0},
            ],
            "cost_per_request": {
                "vendor/cheap-20260820": 0.5,
                "vendor/best-20260820": 3.0,
                "vendor/middle-20260820": 1.0,
            },
        }
        catalog = [
            {"id": "vendor/cheap", "canonical_slug": "vendor/cheap-20260820", "best_provider": "CheapP", "discount_max": 0.0, "uptime_1d": 99.0, "has_tools": True},
            {"id": "vendor/best", "canonical_slug": "vendor/best-20260820", "best_provider": "BestP", "discount_max": 0.1, "uptime_1d": 99.0, "has_tools": True},
            {"id": "vendor/middle", "canonical_slug": "vendor/middle-20260820", "best_provider": "MiddleP", "discount_max": 0.2, "uptime_1d": 99.0, "has_tools": True},
        ]

        result = build_profile_decision(ranking, catalog, PROFILE_BY_KEY["code"])

        self.assertEqual(result["quality_metric"], "coding")
        self.assertEqual(result["price_unit"], "usd_per_100_requests")
        self.assertEqual(result["roles"]["cost_option"]["ranking_key"], "vendor/cheap-20260820")
        self.assertEqual(result["roles"]["quality_option"]["ranking_key"], "vendor/best-20260820")
        self.assertIn("balanced_default", result["roles"])
        self.assertEqual(result["candidate_count"], 3)

    def test_unmatched_or_unpriced_rows_are_not_recommendations(self):
        ranking = {
            "quality_rows": [
                {"category": "intelligence", "ranking_key": "vendor/matched-20260820", "permaslug": "vendor/matched-20260820", "score": 60.0},
                {"category": "intelligence", "ranking_key": "vendor/unmatched-20260820", "permaslug": "vendor/unmatched-20260820", "score": 99.0},
            ],
            "cost_per_request": {"vendor/matched-20260820": 1.0},
        }
        catalog = [{"id": "vendor/matched", "canonical_slug": "vendor/matched-20260820", "best_provider": "P"}]

        result = build_profile_decision(ranking, catalog, PROFILE_BY_KEY["chat"])

        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["unmatched_quality_rows"], 1)
        self.assertEqual(result["unpriced_rows"], 0)
        self.assertNotIn("vendor/unmatched-20260820", result["raw_pareto"])


if __name__ == "__main__":
    unittest.main()
