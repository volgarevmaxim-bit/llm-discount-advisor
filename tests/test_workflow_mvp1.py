import unittest
from pathlib import Path


class WorkflowMvp1Tests(unittest.TestCase):
    def test_workflow_supports_public_degraded_and_authenticated_modes(self):
        workflow = Path(__file__).resolve().parents[1].joinpath(".github", "workflows", "update.yml").read_text(encoding="utf-8")
        self.assertIn("OPENROUTER_API_KEY", workflow)
        self.assertIn("--no-key", workflow)
        self.assertIn("rankings_surface.json", workflow)
        self.assertIn("decision_surface.json", workflow)
        self.assertIn("task_cost_evidence.json", workflow)
        self.assertIn("config_patch.json", workflow)
        self.assertIn("changes.json", workflow)


if __name__ == "__main__":
    unittest.main()
