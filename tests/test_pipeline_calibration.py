import unittest

from advisor.pipeline import build


class PipelineCalibrationTests(unittest.TestCase):
    def test_authenticated_build_runs_discount_calibration_without_changing_ranking_cost(self):
        model = {
            "id": "vendor/model",
            "canonical_slug": "vendor/model-20260820",
            "name": "Vendor Model",
            "pricing": {"prompt": "0.000001", "completion": "0.000002"},
            "context_length": 300000,
            "supported_parameters": ["tools"],
            "architecture": {"input_modalities": ["text"], "output_modalities": ["text"]},
            "benchmarks": {
                "artificial_analysis": {
                    "intelligence_index": 70,
                    "coding_index": 75,
                    "agentic_index": 65,
                },
                "design_arena": [],
            },
            "reasoning": {"mandatory": False},
        }
        rankings = {
            "data": {
                "aaData": {
                    "intelligence": [],
                    "coding": [{"uid": "vendor/model-20260820", "permaslug": "vendor/model-20260820", "score": 75}],
                    "agentic": [],
                },
                "costPerRequest": {"vendor/model-20260820": 1.0},
                "weightedInputPrices": {"vendor/model-20260820": 0.5},
                "daData": {},
            }
        }
        endpoints = {
            "vendor/model": [{
                "provider_name": "Provider",
                "uptime_last_1d": 99.0,
                "pricing": {
                    "prompt": "0.000001",
                    "completion": "0.000002",
                    "discount": 0.25,
                },
            }]
        }

        artifacts = build(
            [model],
            endpoints,
            generated_at="2026-08-20T00:00:00Z",
            rankings_payload=rankings,
            calibrate_discount=True,
        )

        calibration = artifacts["mvp1"]["decision_surface"]["discount_calibration"]
        self.assertEqual(calibration["sample_size"], 20)
        self.assertEqual(len(calibration["observations"]), 1)
        self.assertEqual(calibration["observations"][0]["ranking_key"], "vendor/model-20260820")
        self.assertEqual(calibration["observations"][0]["frontend_cost_per_request"], 1.0)
        code_profile = next(
            profile for profile in artifacts["mvp1"]["decision_surface"]["profiles"]
            if profile["profile"] == "code"
        )
        self.assertEqual(code_profile["candidates"][0]["price"], 1.0)


if __name__ == "__main__":
    unittest.main()
