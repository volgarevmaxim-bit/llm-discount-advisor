"""Decision surface built from normalized Rankings data and catalog overlays."""
from __future__ import annotations

from .rankings import join_ranking_to_catalog, raw_pareto, stable_pareto


PRICE_METRIC = "costPerRequest"
PRICE_UNIT = "usd_per_100_requests"
PRICE_LABEL = "Avg Price Per 100 Requests"
QUALITY_LABELS = {
    "intelligence": "Intelligence Index Score",
    "coding": "Coding Index Score",
    "agentic": "Agentic Index Score",
}


def _catalog_overlay(joined: dict) -> dict:
    rows = joined.get("catalog_rows") or []
    if not rows:
        return {}
    current = sorted(rows, key=lambda row: (row.get("id") or "", row.get("canonical_slug") or ""))[0]
    return {
        "canonical_slug": joined.get("canonical_slug"),
        "variant_id": current.get("id"),
        "provider": current.get("best_provider"),
        "discount_max": current.get("discount_max", 0.0),
        "discount_provider": current.get("discount_provider"),
        "current_effective_price_in": current.get("price_in"),
        "current_effective_price_out": current.get("price_out"),
        "base_price": current.get("base_price"),
        "uptime_1d": current.get("uptime_1d"),
        "reasoning_mandatory": current.get("reasoning_mandatory", False),
        "has_tools": current.get("has_tools", False),
    }


def build_profile_decision(ranking_surface: dict, catalog_rows: list[dict], profile) -> dict:
    """Build one profile's comparable candidates, frontiers, and recommendation roles."""
    selected = [row for row in ranking_surface.get("quality_rows", []) if row.get("category") == profile.quality_metric]
    candidates = []
    unmatched = 0
    unpriced = 0
    excluded = []
    cost_map = ranking_surface.get("cost_per_request", {})
    for quality_row in selected:
        joined = join_ranking_to_catalog(quality_row, catalog_rows)
        ranking_key = quality_row["ranking_key"]
        price = cost_map.get(ranking_key)
        if joined.get("join_status") != "matched":
            unmatched += 1
            excluded.append({"ranking_key": ranking_key, "reason": "unmatched_family_join"})
            continue
        if price is None:
            unpriced += 1
            excluded.append({"ranking_key": ranking_key, "reason": "missing_cost_per_request"})
            continue
        if price < 0:
            raise ValueError("negative costPerRequest cannot enter decision surface")
        overlay = _catalog_overlay(joined)
        # The frontend price is observed and never adjusted by discount.
        candidate = {
            "ranking_key": ranking_key,
            "permaslug": quality_row.get("permaslug"),
            "score": quality_row["score"],
            "price": price,
            "price_metric": PRICE_METRIC,
            "price_unit": PRICE_UNIT,
            "quality_metric": profile.quality_metric,
            "quality_label": QUALITY_LABELS[profile.quality_metric],
            "join_status": joined["join_status"],
            **overlay,
        }
        if candidate["score"] < profile.q_min:
            excluded.append({"ranking_key": ranking_key, "reason": "below_quality_floor"})
            continue
        if candidate.get("uptime_1d") is not None and candidate["uptime_1d"] < profile.min_uptime:
            excluded.append({"ranking_key": ranking_key, "reason": "below_uptime_floor"})
            continue
        if profile.needs_tools and candidate.get("has_tools") is False:
            excluded.append({"ranking_key": ranking_key, "reason": "tools_required"})
            continue
        if profile.key == "bulk" and candidate.get("reasoning_mandatory"):
            excluded.append({"ranking_key": ranking_key, "reason": "reasoning_mandatory"})
            continue
        candidates.append(candidate)

    raw = raw_pareto(candidates)
    stable = stable_pareto(candidates)
    eligible_sorted = sorted(candidates, key=lambda row: (row["price"], -row["score"], row["ranking_key"]))
    quality_sorted = sorted(candidates, key=lambda row: (-row["score"], row["price"], row["ranking_key"]))
    roles = {"cost_option": eligible_sorted[0] if eligible_sorted else None, "quality_option": quality_sorted[0] if quality_sorted else None, "balanced_default": None}
    if quality_sorted:
        target_quality = max(profile.q_min, quality_sorted[0]["score"] - 2.0)
        balanced = [row for row in stable if row["score"] >= target_quality]
        roles["balanced_default"] = sorted(balanced, key=lambda row: (row["price"], -row["score"], row["ranking_key"]))[0] if balanced else quality_sorted[0]
    return {
        "profile": profile.key,
        "title": profile.title,
        "quality_metric": profile.quality_metric,
        "quality_label": QUALITY_LABELS[profile.quality_metric],
        "quality_floor": profile.q_min,
        "price_metric": PRICE_METRIC,
        "price_label": PRICE_LABEL,
        "price_unit": PRICE_UNIT,
        "min_uptime": profile.min_uptime,
        "requires_tools": profile.needs_tools,
        "candidate_count": len(candidates),
        "raw_pareto_count": len(raw),
        "stable_pareto_count": len(stable),
        "unmatched_quality_rows": unmatched,
        "unpriced_rows": unpriced,
        "roles": roles,
        "raw_pareto": raw,
        "stable_pareto": stable,
        "candidates": candidates,
        "excluded": excluded,
        "fallback_policy": profile.fallback_policy,
        "margins": {"price_pct": 10, "quality_points": 2.0},
    }
