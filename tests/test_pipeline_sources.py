import unittest
from unittest.mock import patch

from advisor.pipeline import collect_mvp1_sources


class PipelineSourceTests(unittest.TestCase):
    @patch("advisor.pipeline.fetch_secondary_evidence")
    @patch("advisor.pipeline.fetch_rankings_surface")
    def test_collects_public_rankings_and_authenticated_evidence(self, fetch_rankings, fetch_secondary):
        rankings = {"data": {"aaData": {}, "costPerRequest": {}, "weightedInputPrices": {}, "daData": {}}}
        fetch_rankings.return_value = rankings
        fetch_secondary.return_value = ([{"benchmark_type": "gpqa_diamond"}], [{"app_slug": "claude-code"}], {"session_meta": {}})

        result = collect_mvp1_sources("secret-not-printed")

        self.assertIs(result["rankings_payload"], rankings)
        self.assertEqual(result["benchmark_rows"], [{"benchmark_type": "gpqa_diamond"}])
        self.assertEqual(result["session_rows"], [{"app_slug": "claude-code"}])
        fetch_secondary.assert_called_once_with("secret-not-printed")

    @patch("advisor.pipeline.fetch_secondary_evidence")
    @patch("advisor.pipeline.fetch_rankings_surface")
    def test_no_key_keeps_public_rankings_and_skips_authenticated_evidence(self, fetch_rankings, fetch_secondary):
        rankings = {"data": {"aaData": {}, "costPerRequest": {}, "weightedInputPrices": {}, "daData": {}}}
        fetch_rankings.return_value = rankings

        result = collect_mvp1_sources(None)

        self.assertIs(result["rankings_payload"], rankings)
        self.assertEqual(result["benchmark_rows"], [])
        self.assertEqual(result["session_rows"], [])
        fetch_secondary.assert_not_called()


if __name__ == "__main__":
    unittest.main()
