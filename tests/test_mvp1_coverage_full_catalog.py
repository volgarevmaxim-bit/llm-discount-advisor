import unittest

from advisor.mvp1 import build_mvp1_artifacts


class Mvp1FullCatalogCoverageTests(unittest.TestCase):
    def test_coverage_uses_all_catalog_families_and_quality_signals(self):
        models = [
            {
                "id": "vendor/gated",
                "canonical_slug": "vendor/gated-family",
                "name": "Gated",
                "pricing": {"prompt": "0.000001", "completion": "0.000002"},
                "context_length": 300000,
                "supported_parameters": ["tools"],
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
                "benchmarks": {"artificial_analysis": {"intelligence_index": 70, "coding_index": 75, "agentic_index": 65}, "design_arena": []},
                "reasoning": {"mandatory": False},
            },
            {
                "id": "vendor/uncovered",
                "canonical_slug": "vendor/uncovered-family",
                "name": "Uncovered Strong",
                "pricing": {"prompt": "0.000001", "completion": "0.000002"},
                "context_length": 300000,
                "supported_parameters": ["tools"],
                "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
                "benchmarks": {"artificial_analysis": {"intelligence_index": 60, "coding_index": 62, "agentic_index": 58}, "design_arena": []},
                "reasoning": {"mandatory": False},
            },
        ]
        rankings = {
            "data": {
                "aaData": {
                    "intelligence": [{"uid": "vendor/gated-family", "permaslug": "vendor/gated-family", "score": 70}],
                    "coding": [{"uid": "vendor/gated-family", "permaslug": "vendor/gated-family", "score": 75}],
                    "agentic": [{"uid": "vendor/gated-family", "permaslug": "vendor/gated-family", "score": 65}],
                },
                "costPerRequest": {"vendor/gated-family": 1.0},
                "weightedInputPrices": {"vendor/gated-family": 0.5},
                "daData": {},
            }
        }
        endpoints = {
            "vendor/gated": [{
                "provider_name": "Provider",
                "uptime_last_1d": 99.0,
                "pricing": {"prompt": "0.000001", "completion": "0.000002", "discount": 0.0},
            }]
        }

        result = build_mvp1_artifacts(
            models,
            endpoints,
            rankings,
            "2026-08-20T00:00:00Z",
        )

        counts = result["task_cost_coverage"]["counts"]
        self.assertEqual(counts["families_total"], 2)
        uncovered = [
            row for row in result["task_cost_coverage"]["families"]
            if row["canonical_family"] == "vendor/uncovered-family"
        ]
        self.assertEqual(uncovered[0]["classification"], "worthy_candidate")


if __name__ == "__main__":
    unittest.main()
