import unittest

from advisor.economics import calibrate_discount_reflection, build_discount_overlay


class EconomicsTests(unittest.TestCase):
    def test_observed_ranking_cost_is_not_discount_adjusted(self):
        overlay = build_discount_overlay(
            ranking_cost=0.635268,
            endpoint={
                "provider_name": "Google",
                "pricing": {"prompt": "0.0000001875", "completion": "0.0000009375", "discount": 0.75},
                "uptime_last_1d": 99.5,
            },
        )
        self.assertEqual(overlay["ranking_cost_usd_per_100_requests"], 0.635268)
        self.assertEqual(overlay["ranking_effect"], "not_established")
        self.assertIsNone(overlay["discount_scenario"]["estimated_cost"])
        self.assertEqual(overlay["current_effective_price_in"], 0.1875)
        self.assertEqual(overlay["base_price_in"], 0.75)

    def test_calibration_states_are_explicit(self):
        matched = [{"relative_error": 0.05} for _ in range(16)] + [{"relative_error": 0.3} for _ in range(4)]
        self.assertEqual(calibrate_discount_reflection(matched)["status"], "validated")
        self.assertEqual(calibrate_discount_reflection([{"relative_error": 0.3}] * 20)["status"], "inconsistent")
        self.assertEqual(calibrate_discount_reflection([])["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
