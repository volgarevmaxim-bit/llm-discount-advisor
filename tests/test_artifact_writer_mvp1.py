import json
import tempfile
import unittest
from pathlib import Path

from advisor.pipeline import write_artifacts


class Mvp1ArtifactWriterTests(unittest.TestCase):
    def test_writes_revised_mvp1_artifacts_when_present(self):
        artifacts = {
            "snapshot": {"generated_at": "2026-08-20T00:00:00Z", "models": []},
            "shortlist": {},
            "gate_rejected": {},
            "mvp1": {
                "rankings_surface": {"schema_version": "1.0"},
                "decision_surface": {"ranking_mode": "rankings_cost_per_request"},
                "task_cost_evidence": {"schema_version": "1.0"},
                "task_cost_coverage": {"schema_version": "1.0"},
                "config_patch": {"status": "not_applied"},
                "changes": {"status": "baseline"},
            },
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_artifacts(artifacts, root)

            expected = {
                root / "data" / "rankings_surface.json": {"schema_version": "1.0"},
                root / "data" / "decision_surface.json": {"ranking_mode": "rankings_cost_per_request"},
                root / "data" / "task_cost_evidence.json": {"schema_version": "1.0"},
                root / "data" / "task_cost_coverage.json": {"schema_version": "1.0"},
                root / "data" / "config_patch.json": {"status": "not_applied"},
                root / "changes.json": {"status": "baseline"},
            }
            for path, expected_value in expected.items():
                self.assertTrue(path.exists(), path)
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), expected_value)


if __name__ == "__main__":
    unittest.main()
