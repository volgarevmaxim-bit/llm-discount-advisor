import unittest

from advisor.report import render_report


class Mvp1ReportTests(unittest.TestCase):
    def test_report_exposes_revised_decision_surface_and_units(self):
        mvp1 = {
            "decision_surface": {
                "ranking_mode": "rankings_cost_per_request",
                "profiles": [
                    {
                        "profile": "code",
                        "quality_metric": "coding",
                        "price_unit": "usd_per_100_requests",
                        "candidate_count": 1,
                        "raw_pareto_count": 1,
                        "stable_pareto_count": 1,
                        "roles": {
                            "balanced_default": {
                                "ranking_key": "vendor/model",
                                "provider": "Provider",
                                "price": 0.5,
                                "score": 75,
                            },
                            "cost_option": {"ranking_key": "vendor/model"},
                            "quality_option": {"ranking_key": "vendor/model"},
                        },
                        "discount_calibration": {"status": "unknown"},
                    }
                ],
                "discount_calibration": {"status": "unknown", "sample_size": 20},
            },
            "task_cost_coverage": {
                "counts": {
                    "families_total": 1,
                    "uncovered": 1,
                    "worthy_uncovered": 1,
                    "likely_low_signal_uncovered": 0,
                }
            },
            "config_patch": {"status": "not_applied", "requires_confirmation": True},
            "changes": {"status": "baseline", "events": []},
        }

        result = render_report(
            {"profiles": [], "gate": {"passed": 0}},
            {"model_count": 0, "model_family_count": 0, "gated_count": 0, "gated_unique_families": 0, "models": []},
            {"rejected": []},
            mvp1=mvp1,
        )

        self.assertIn("Decision surface", result)
        self.assertIn("Avg Price Per 100 Requests", result)
        self.assertIn("usd_per_100_requests", result)
        self.assertIn("Discount calibration: `unknown`", result)
        self.assertIn("YAML patch preview", result)
        self.assertIn("not_applied", result)
        self.assertIn("worthy_candidate", result)


if __name__ == "__main__":
    unittest.main()
