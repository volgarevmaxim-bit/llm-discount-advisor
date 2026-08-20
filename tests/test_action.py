import unittest

from advisor.action import build_config_patch


class ActionTests(unittest.TestCase):
    def test_yaml_patch_is_preview_only_and_requires_confirmation(self):
        result = build_config_patch(
            profile="code",
            before={"model": "vendor/old", "provider": "Old"},
            after={"model": "vendor/new", "provider": "New", "variant": "vendor/new:batch"},
            reason="stable frontier default changed",
        )
        self.assertEqual(result["status"], "not_applied")
        self.assertTrue(result["requires_confirmation"])
        self.assertIn("vendor/new:batch", result["yaml_diff"])
        self.assertFalse(result["applied"])


if __name__ == "__main__":
    unittest.main()
