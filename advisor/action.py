"""Reviewable config action preview; never mutates Hermes config."""
from __future__ import annotations

import json


def _yaml_value(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return json.dumps(str(value), ensure_ascii=False)


def _yaml_block(section: str, values: dict) -> str:
    lines = [f"{section}:"]
    for key in ("model", "provider", "variant"):
        if key in values:
            lines.append(f"  {key}: {_yaml_value(values[key])}")
    return "\n".join(lines)


def build_config_patch(profile: str, before: dict, after: dict, reason: str) -> dict:
    before_block = _yaml_block("before", before)
    after_block = _yaml_block("after", after)
    diff = "--- config.yaml\n+++ proposed config.yaml\n" + "\n".join(
        [f"- {line}" for line in before_block.splitlines()] + [f"+ {line}" for line in after_block.splitlines()]
    )
    return {
        "status": "not_applied",
        "requires_confirmation": True,
        "applied": False,
        "profile": profile,
        "from": before,
        "to": after,
        "yaml_diff": diff,
        "reason": reason,
    }


def patch_for_profile(profile: str, current: dict | None, recommended: dict | None, reason: str) -> dict:
    return build_config_patch(profile, current or {}, recommended or {}, reason)
