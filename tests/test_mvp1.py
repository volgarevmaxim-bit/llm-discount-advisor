import unittest

from advisor.mvp1 import build_mvp1_artifacts


class Mvp1IntegrationTests(unittest.TestCase):
    def test_builds_all_profiles_and_preview_artifacts_without_applying_config(self):
        model = {
            "id": "vendor/model",
            "canonical_slug": "vendor/model-20260820",
            "name": "Vendor Model",
            "pricing": {"prompt": "0.000001", "completion": "0.000002"},
            "context_length": 300000,
            "supported_parameters": ["tools"],
            "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            "benchmarks": {"artificial_analysis": {"intelligence_index": 70, "coding_index": 75, "agentic_index": 65}, "design_arena": []},
            "reasoning": {"mandatory": False, "default_effort": "medium"},
        }
        rankings = {
            "data": {
                "aaData": {
                    "intelligence": [{"uid": "vendor/model-20260820", "permaslug": "vendor/model-20260820", "score": 70}],
                    "coding": [{"uid": "vendor/model-20260820", "permaslug": "vendor/model-20260820", "score": 75}],
                    "agentic": [{"uid": "vendor/model-20260820", "permaslug": "vendor/model-20260820", "score": 65}],
                },
                "costPerRequest": {"vendor/model-20260820": 1.0},
                "weightedInputPrices": {"vendor/model-20260820": 0.5},
                "daData": {},
            }
        }
        endpoints = {"vendor/model": [{"provider_name": "Provider", "uptime_last_1d": 99.0, "pricing": {"prompt": "0.000001", "completion": "0.000002", "discount": 0.0}}]}

        result = build_mvp1_artifacts([model], endpoints, rankings, generated_at="2026-08-20T00:00:00Z")

        self.assertEqual(result["decision_surface"]["ranking_mode"], "rankings_cost_per_request")
        self.assertEqual({item["profile"] for item in result["decision_surface"]["profiles"]}, {"chat", "code", "agentic", "longdoc", "bulk"})
        self.assertEqual(result["config_patch"]["status"], "not_applied")
        self.assertTrue(result["config_patch"]["requires_confirmation"])
        self.assertEqual(result["changes"]["status"], "baseline")


if __name__ == "__main__":
    unittest.main()
