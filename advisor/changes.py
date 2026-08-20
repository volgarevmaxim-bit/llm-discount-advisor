"""Decision-level change detection with schema migration and hysteresis guards."""
from __future__ import annotations

REQUIRED_SURFACE_KEYS = {"schema_version", "generated_at", "profiles"}
CONFIRMATION_SNAPSHOTS = 2


def decision_snapshot_compatible(snapshot: dict) -> bool:
    if not isinstance(snapshot, dict) or not REQUIRED_SURFACE_KEYS.issubset(snapshot):
        return False
    for profile in snapshot.get("profiles", []):
        if not isinstance(profile, dict) or "profile" not in profile or "roles" not in profile:
            return False
    return True


def _profile_defaults(surface: dict) -> dict[str, dict]:
    result = {}
    for profile in surface.get("profiles", []):
        role = (profile.get("roles") or {}).get("balanced_default") or {}
        result[profile.get("profile")] = {
            "ranking_key": role.get("ranking_key"),
            "provider": role.get("provider"),
            "variant_id": role.get("variant_id"),
            "price": role.get("price"),
            "score": role.get("score"),
            "stable": role.get("ranking_key") in {row.get("ranking_key") for row in profile.get("stable_pareto", [])},
        }
    return result


def compare_decisions(previous: dict | None, current: dict) -> dict:
    if not previous:
        return {"schema_version": "1.0", "from": None, "to": current.get("generated_at"), "events": [], "status": "baseline"}
    if not decision_snapshot_compatible(previous) or not decision_snapshot_compatible(current):
        return {"schema_version": "1.0", "from": previous.get("generated_at"), "to": current.get("generated_at"), "events": [], "status": "comparison_skipped", "reason": "schema_migration"}
    before = _profile_defaults(previous)
    after = _profile_defaults(current)
    events = []
    for profile in sorted(set(before) | set(after)):
        old = before.get(profile, {})
        new = after.get(profile, {})
        if old == new:
            continue
        if old.get("ranking_key") != new.get("ranking_key") or old.get("variant_id") != new.get("variant_id"):
            events.append({"type": "decision_changed", "profile": profile, "before": old, "after": new, "reason": "Actionable balanced default changed.", "confirmed": False})
        elif old.get("provider") != new.get("provider"):
            events.append({"type": "discount_action_changed", "profile": profile, "before": old, "after": new, "reason": "Current actionable provider changed."})
    return {"schema_version": "1.0", "from": previous.get("generated_at"), "to": current.get("generated_at"), "events": events, "status": "compared"}


def hysteresis_default_change(before: str | None, after: str | None, recent_defaults: list[str], confirmations: int = CONFIRMATION_SNAPSHOTS) -> bool:
    if not after or before == after or len(recent_defaults) < confirmations:
        return False
    return recent_defaults[-confirmations:] == [after] * confirmations


def apply_hysteresis(changes: dict, recent_defaults: dict[str, list[str]], confirmations: int = CONFIRMATION_SNAPSHOTS) -> dict:
    result = dict(changes)
    filtered = []
    for event in changes.get("events", []):
        if event.get("type") != "decision_changed":
            filtered.append(event)
            continue
        profile = event.get("profile")
        before = (event.get("before") or {}).get("ranking_key")
        after = (event.get("after") or {}).get("ranking_key")
        confirmed = hysteresis_default_change(before, after, recent_defaults.get(profile, []), confirmations)
        event = dict(event)
        event["confirmed"] = confirmed
        if confirmed:
            filtered.append(event)
    result["events"] = filtered
    return result


def changes_from_surfaces(previous: dict | None, current: dict, recent_defaults: dict[str, list[str]] | None = None) -> dict:
    result = compare_decisions(previous, current)
    if recent_defaults:
        result = apply_hysteresis(result, recent_defaults)
    return result
