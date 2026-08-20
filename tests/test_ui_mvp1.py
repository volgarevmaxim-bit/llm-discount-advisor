import unittest
from pathlib import Path


class Mvp1UiContractTests(unittest.TestCase):
    def test_static_ui_anchors_revised_decision_surface(self):
        html = Path(__file__).resolve().parents[1].joinpath("index.html").read_text(encoding="utf-8")
        for required in (
            "decision_surface.json",
            "task_cost_coverage.json",
            "config_patch.json",
            "changes.json",
            "Avg Price Per 100 Requests",
            "balanced_default",
            "Что изменилось",
            "YAML patch preview",
        ):
            self.assertIn(required, html)


if __name__ == "__main__":
    unittest.main()
