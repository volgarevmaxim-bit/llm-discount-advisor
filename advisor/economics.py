"""Observed ranking economics plus non-destructive provider discount overlays."""
from __future__ import annotations


def _million(value) -> float:
    return float(value or 0) * 1_000_000


def build_discount_overlay(ranking_cost: float, endpoint: dict) -> dict:
    pricing = endpoint.get("pricing") or {}
    prompt = _million(pricing.get("prompt"))
    completion = _million(pricing.get("completion"))
    discount = float(pricing.get("discount") or 0)
    discount = max(0.0, min(1.0, discount))
    base_in = prompt / (1 - discount) if discount < 1 else prompt
    base_out = completion / (1 - discount) if discount < 1 else completion
    return {
        "ranking_cost_usd_per_100_requests": ranking_cost,
        "ranking_cost_source": "openrouter_frontend_rankings",
        "discount_overlay": {
            "discount_max": discount,
            "discount_provider": endpoint.get("provider_name"),
            "current_best_provider": endpoint.get("provider_name"),
            "current_effective_price_in": prompt,
            "current_effective_price_out": completion,
            "base_price_in": base_in,
            "base_price_out": base_out,
            "uptime_1d": endpoint.get("uptime_last_1d"),
            "status": "active" if discount > 0 else "none",
            "ranking_effect": "not_established",
        },
        "current_effective_price_in": prompt,
        "current_effective_price_out": completion,
        "base_price_in": base_in,
        "base_price_out": base_out,
        "ranking_effect": "not_established",
        "discount_scenario": {
            "status": "scenario_only",
            "estimated_cost": None,
            "reason": "Не доказано, что frontend costPerRequest можно пропорционально пересчитать по endpoint discount.",
        },
    }


def calibrate_discount_reflection(observations: list[dict], sample_size: int = 20) -> dict:
    """Classify reflection only when at least 16/20 observations are within 20%."""
    if not observations:
        return {"status": "unknown", "sample_size": 0, "within_tolerance": 0, "tolerance_pct": 20}
    sample = observations[:sample_size]
    within = sum(abs(float(item.get("relative_error", 1.0))) <= 0.20 for item in sample)
    status = "validated" if len(sample) >= sample_size and within >= 16 else "inconsistent" if len(sample) >= sample_size else "unknown"
    return {"status": status, "sample_size": len(sample), "within_tolerance": within, "tolerance_pct": 20}


def build_discount_calibration_observations(rankings: dict, catalog_rows: list[dict], provider_endpoints: dict[str, list[dict]], sample_size: int = 20) -> list[dict]:
    """Create audit observations without altering the primary ranking price."""
    observations = []
    ranking_cost = rankings.get("cost_per_request", {})
    for key in sorted(ranking_cost):
        if len(observations) >= sample_size:
            break
        catalog_matches = [
            row for row in catalog_rows
            if row.get("canonical_slug") == key
            or row.get("id") == key
            or row.get("canonical_slug") == key.split(":", 1)[0]
            or row.get("id") == key.split(":", 1)[0]
        ]
        endpoint_keys = [key, key.split(":", 1)[0]]
        endpoint_keys.extend(row.get("variant_id") or row.get("id") for row in catalog_matches)
        endpoints = []
        seen_endpoint_keys = set()
        for endpoint_key in endpoint_keys:
            if not endpoint_key or endpoint_key in seen_endpoint_keys:
                continue
            seen_endpoint_keys.add(endpoint_key)
            endpoints.extend(provider_endpoints.get(endpoint_key) or [])
        if not endpoints:
            continue
        endpoint = sorted(endpoints, key=lambda item: (item.get("provider_name") or "", item.get("name") or ""))[0]
        prompt = _million((endpoint.get("pricing") or {}).get("prompt"))
        completion = _million((endpoint.get("pricing") or {}).get("completion"))
        discount = float((endpoint.get("pricing") or {}).get("discount") or 0)
        effective = (3 * prompt + completion) / 4
        base = effective / (1 - discount) if discount < 1 else effective
        observed = float(ranking_cost[key])
        relationship = base if base > 0 else effective
        relative_error = abs(observed - relationship) / max(abs(relationship), 1e-9)
        observations.append({
            "ranking_key": key,
            "frontend_cost_per_request": observed,
            "weighted_input_price": rankings.get("weighted_input_prices", {}).get(key),
            "endpoint_prompt_price": prompt,
            "endpoint_completion_price": completion,
            "discount": discount,
            "provider": endpoint.get("provider_name"),
            "uptime_1d": endpoint.get("uptime_last_1d"),
            "relative_error": relative_error,
        })
    return observations


def calibration_for_rankings(rankings: dict, catalog_rows: list[dict], provider_endpoints: dict[str, list[dict]], sample_size: int = 20) -> dict:
    observations = build_discount_calibration_observations(rankings, catalog_rows, provider_endpoints, sample_size)
    result = calibrate_discount_reflection(observations, sample_size)
    result["requested_sample_size"] = sample_size
    result["matched_observations"] = len(observations)
    result["sample_size"] = sample_size
    result["observations"] = observations
    return result
