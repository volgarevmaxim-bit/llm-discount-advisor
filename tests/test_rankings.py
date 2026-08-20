import unittest

from advisor.rankings import normalize_rankings_payload, raw_pareto, stable_pareto


class RankingsNormalizationTests(unittest.TestCase):
    def test_normalizes_frontend_categories_and_preserves_permaslug(self):
        payload = {
            "data": {
                "aaData": {
                    "intelligence": [
                        {
                            "uid": "vendor/model-20260820",
                            "permaslug": "vendor/model-20260820",
                            "openrouter_slug": None,
                            "heuristic_openrouter_slug": "vendor/model",
                            "aa_name": "Model",
                            "score": 60.0,
                        }
                    ],
                    "coding": [],
                    "agentic": [],
                },
                "costPerRequest": {"vendor/model-20260820": 0.5},
                "weightedInputPrices": {"vendor/model-20260820": 0.1},
                "daData": {},
            }
        }

        result = normalize_rankings_payload(payload, generated_at="2026-08-20T00:00:00Z")

        self.assertEqual(result["schema_version"], "1.0")
        self.assertEqual(result["categories"]["intelligence"]["rows"], 1)
        self.assertEqual(result["quality_rows"][0]["ranking_key"], "vendor/model-20260820")
        self.assertEqual(result["quality_rows"][0]["permaslug"], "vendor/model-20260820")
        self.assertEqual(result["cost_per_request"]["vendor/model-20260820"], 0.5)
        self.assertEqual(result["weighted_input_prices"]["vendor/model-20260820"], 0.1)

    def test_missing_frontend_category_fails_loudly(self):
        payload = {
            "data": {
                "aaData": {"intelligence": [], "coding": []},
                "costPerRequest": {},
                "weightedInputPrices": {},
                "daData": {},
            }
        }
        with self.assertRaisesRegex(ValueError, "agentic"):
            normalize_rankings_payload(payload)

    def test_raw_pareto_is_deterministic_and_price_first(self):
        points = [
            {"ranking_key": "expensive", "price": 3.0, "score": 90.0},
            {"ranking_key": "cheap", "price": 1.0, "score": 70.0},
            {"ranking_key": "middle", "price": 2.0, "score": 80.0},
            {"ranking_key": "dominated", "price": 2.5, "score": 75.0},
        ]
        self.assertEqual([p["ranking_key"] for p in raw_pareto(points)], ["cheap", "middle", "expensive"])

    def test_stable_pareto_returns_points_not_margin_dominated(self):
        points = [
            {"ranking_key": "cheap", "price": 1.0, "score": 70.0},
            {"ranking_key": "slightly-better", "price": 0.95, "score": 71.0},
            {"ranking_key": "clearly-better", "price": 0.8, "score": 73.0},
        ]
        result = stable_pareto(points)
        self.assertEqual({p["ranking_key"] for p in result}, {"clearly-better"})


if __name__ == "__main__":
    unittest.main()
