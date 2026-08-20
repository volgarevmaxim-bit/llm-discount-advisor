import unittest

from advisor.evidence import build_task_cost_evidence, classify_coverage


class EvidenceTests(unittest.TestCase):
    def test_benchmark_and_session_units_remain_separate(self):
        evidence = build_task_cost_evidence(
            benchmarks=[{
                "source": "openrouter",
                "model_permaslug": "vendor/model-20260820",
                "benchmark_type": "gpqa_diamond",
                "accuracy": 0.8,
                "avg_cost_per_task": 0.07,
                "total_tasks": 100,
                "last_run_timestamp": "2026-08-19T00:00:00Z",
            }],
            sessions=[{
                "app_slug": "claude-code",
                "turn_range": "10-49-turns",
                "model_permaslug": "vendor/model-20260820",
                "median_session_cost_usd": 0.03,
            }],
            generated_at="2026-08-20T00:00:00Z",
        )
        self.assertEqual(evidence["benchmarks"][0]["scope"], "named_benchmark_run")
        self.assertEqual(evidence["benchmarks"][0]["avg_cost_per_task_usd"], 0.07)
        self.assertEqual(evidence["session_cost"][0]["scope"], "named_application_workload")
        self.assertNotIn("avg_cost_per_task_usd", evidence["session_cost"][0])

    def test_coverage_classifies_uncovered_worthy_family(self):
        coverage = classify_coverage(
            catalog_families=["vendor/model", "vendor/strong"],
            rankings_families=["vendor/model"],
            benchmark_families=[],
            session_families=[],
            signals={"vendor/strong": {"quality_scores": {"agentic": 60.0}}},
        )
        self.assertEqual(coverage["counts"]["uncovered"], 1)
        self.assertEqual(coverage["families"][1]["classification"], "worthy_candidate")


if __name__ == "__main__":
    unittest.main()
