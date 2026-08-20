import json
import tempfile
import unittest
from pathlib import Path

from advisor.pipeline import load_previous_decision, write_artifacts


class PipelineLineageTests(unittest.TestCase):
    def test_loads_latest_prior_decision_snapshot_not_same_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "data" / "decision_snapshots"
            directory.mkdir(parents=True)
            (directory / "2026-08-18.json").write_text(json.dumps({"day": 18}), encoding="utf-8")
            (directory / "2026-08-19.json").write_text(json.dumps({"day": 19}), encoding="utf-8")
            (directory / "2026-08-20.json").write_text(json.dumps({"day": 20}), encoding="utf-8")

            result = load_previous_decision(root, "2026-08-20T16:00:00Z")

            self.assertEqual(result["day"], 19)

    def test_writer_persists_decision_snapshot_by_date(self):
        artifacts = {
            "snapshot": {"generated_at": "2026-08-20T00:00:00Z", "models": []},
            "shortlist": {},
            "gate_rejected": {},
            "mvp1": {
                "rankings_surface": {},
                "decision_surface": {"schema_version": "1.0", "generated_at": "2026-08-20T00:00:00Z", "profiles": []},
                "task_cost_evidence": {},
                "task_cost_coverage": {},
                "config_patch": {},
                "changes": {},
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_artifacts(artifacts, root)
            snapshot = root / "data" / "decision_snapshots" / "2026-08-20.json"
            self.assertTrue(snapshot.exists())
            self.assertEqual(json.loads(snapshot.read_text(encoding="utf-8"))["generated_at"], "2026-08-20T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
