import unittest

from advisor.pipeline import build


class PipelineMetadataTests(unittest.TestCase):
    def test_build_forwards_secondary_source_metadata(self):
        model = {
            "id": "vendor/model",
            "canonical_slug": "vendor/model-20260820",
            "name": "Vendor Model",
            "pricing": {"prompt": "0.000001", "completion": "0.000002"},
            "context_length": 300000,
            "supported_parameters": ["tools"],
            "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            "benchmarks": {"artificial_analysis": {"intelligence_index": 70, "coding_index": 75, "agentic_index": 65}, "design_arena": []},
            "reasoning": {"mandatory": False},
        }
        rankings = {"data": {"aaData": {"intelligence": [], "coding": [], "agentic": []}, "costPerRequest": {}, "weightedInputPrices": {}, "daData": {}}}
        result = build(
            [model],
            {"vendor/model": []},
            generated_at="2026-08-20T00:00:00Z",
            rankings_payload=rankings,
            evidence_meta={
                "benchmark_meta": [{"as_of": "2026-08-19T00:00:00Z"}],
                "session_meta": {"as_of": "2026-08-17T00:00:00Z", "window_days": 30},
            },
        )
        evidence = result["mvp1"]["task_cost_evidence"]
        self.assertEqual(evidence["sources"]["benchmarks"]["meta"][0]["as_of"], "2026-08-19T00:00:00Z")
        self.assertEqual(evidence["sources"]["session_cost"]["meta"]["window_days"], 30)


if __name__ == "__main__":
    unittest.main()
