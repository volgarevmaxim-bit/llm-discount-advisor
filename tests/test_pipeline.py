import unittest
from advisor.pipeline import build


class PipelineTests(unittest.TestCase):
    def test_model_with_empty_endpoint_list_is_reported_not_fatal(self):
        model = {
            "id": "dots-studio/dots-3-note-preview-20260813",
            "canonical_slug": "dots-studio/dots-3-note-preview-20260813",
            "name": "Dots Studio: Dots3-Note Preview",
            "pricing": {"prompt": "0.000001", "completion": "0.000001"},
            "context_length": 128000,
            "architecture": {"output_modalities": ["text"]},
            "benchmarks": {
                "artificial_analysis": {
                    "intelligence_index": 99,
                    "coding_index": 99,
                    "agentic_index": 99,
                },
                "design_arena": [],
            },
            "created": 0,
        }
        artifacts = build([model], {model["canonical_slug"]: []}, "2026-08-20T00:00:00Z")
        self.assertEqual(artifacts["snapshot"]["models"], [])
        self.assertEqual(artifacts["shortlist"]["gate"]["endpoint_errors"], 1)
        self.assertEqual(artifacts["gate_rejected"]["rejected"][0]["slug"], model["canonical_slug"])
        self.assertIn("endpoint_unusable", artifacts["gate_rejected"]["rejected"][0]["reason"])

    def test_variants_are_normalized_as_one_family_after_fetching_each_id(self):
        base = {
            "id": "vendor/model",
            "canonical_slug": "vendor/model-20260820",
            "name": "Vendor Model",
            "pricing": {"prompt": "0.000001", "completion": "0.000001"},
            "context_length": 128000,
            "architecture": {"output_modalities": ["text"]},
            "benchmarks": {"artificial_analysis": {"intelligence_index": 90, "coding_index": 90, "agentic_index": 90}, "design_arena": []},
            "created": 0,
        }
        free = dict(base)
        free["id"] = "vendor/model:free"
        free["pricing"] = {"prompt": "0", "completion": "0"}
        endpoints = {
            "vendor/model": [{"provider_name": "Paid", "uptime_last_1d": 99, "pricing": {"prompt": "0.000001", "completion": "0.000001"}}],
            "vendor/model:free": [{"provider_name": "Free", "uptime_last_1d": 99, "pricing": {"prompt": "0", "completion": "0"}}],
        }

        artifacts = build([base, free], endpoints, "2026-08-20T00:00:00Z")

        self.assertEqual(artifacts["shortlist"]["gate"]["passed_unique_families"], 1)
        self.assertEqual(len(artifacts["snapshot"]["models"]), 2)
        self.assertTrue(all(item["variant_count"] == 2 for item in artifacts["snapshot"]["models"]))
        self.assertEqual({item["variant_id"] for item in artifacts["snapshot"]["models"]}, {"vendor/model", "vendor/model:free"})


if __name__ == "__main__":
    unittest.main()
