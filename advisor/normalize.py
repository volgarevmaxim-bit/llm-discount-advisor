"""Normalize model metadata and provider endpoints into a compact snapshot."""
from __future__ import annotations
from datetime import datetime, timezone
from .config import MIN_UPTIME


def _num(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _million(value) -> float:
    return (_num(value, 0.0) or 0.0) * 1_000_000


def _discounted_base(price: float, discount: float) -> float:
    return price / (1 - discount) if discount < 1 else price


def _tiered(pricing: dict) -> tuple[bool, list[dict]]:
    overrides = pricing.get("overrides") or []
    if isinstance(overrides, dict):
        overrides = [overrides]
    if not isinstance(overrides, list):
        return False, []
    return bool(overrides), overrides


def _uptime(endpoint: dict) -> float:
    return _num(endpoint.get("uptime_last_1d"), 0.0) or 0.0


def normalize_model(meta: dict, endpoints: list[dict], generated_at: str | None = None) -> dict:
    if not meta.get("canonical_slug"):
        raise ValueError("canonical_slug is required")
    usable = []
    for endpoint in endpoints:
        pricing = endpoint.get("pricing") or {}
        pin, pout = _million(pricing.get("prompt")), _million(pricing.get("completion"))
        if pin < 0 or pout < 0:
            continue
        usable.append((endpoint, pricing, pin, pout))
    if not usable:
        raise ValueError(f"no usable endpoints for {meta['canonical_slug']}")
    reliable = [row for row in usable if _uptime(row[0]) >= MIN_UPTIME]
    candidates = reliable or usable
    def blended(row):
        return (3 * row[2] + row[3]) / 4
    best = min(candidates, key=blended)
    default_pricing = meta.get("pricing") or {}
    default_in, default_out = _million(default_pricing.get("prompt")), _million(default_pricing.get("completion"))
    endpoint, pricing, price_in, price_out = best
    discount = _num(pricing.get("discount"), 0.0) or 0.0
    has_tiered, overrides = _tiered(pricing)
    benchmarks = meta.get("benchmarks") or {}
    aa = benchmarks.get("artificial_analysis") or {}
    da = benchmarks.get("design_arena") or []
    if not isinstance(da, list):
        da = []
    da_ranks = [_num(row.get("rank")) for row in da if _num(row.get("rank")) is not None]
    da_elos = [_num(row.get("elo")) for row in da if _num(row.get("elo")) is not None]
    reasoning = meta.get("reasoning") or {}
    created = _num(meta.get("created"))
    age = None
    if created is not None:
        age = max(0, (datetime.now(timezone.utc) - datetime.fromtimestamp(created, timezone.utc)).days)
    provider_blends = [blended(row) for row in candidates]
    max_discount_row = max(usable, key=lambda row: _num(row[1].get("discount"), 0.0) or 0.0)
    variant_id = meta.get("id") or meta["canonical_slug"]
    return {
        "slug": variant_id, "variant_id": variant_id, "canonical_slug": meta["canonical_slug"], "id": meta.get("id"), "name": meta.get("name") or meta["canonical_slug"],
        "price_in": round(price_in, 6), "price_out": round(price_out, 6), "blended_3to1": round(blended(best), 6),
        "default_price_in": round(default_in, 6), "default_price_out": round(default_out, 6), "default_blended_3to1": round((3 * default_in + default_out) / 4, 6),
        "best_provider": endpoint.get("provider_name") or endpoint.get("name") or "не указан", "provider_count": len(endpoints),
        "provider_spread": round(max(provider_blends) / min((value for value in provider_blends if value > 0), default=1), 3),
        "overpay_ratio": round(((3 * default_in + default_out) / 4) / max(blended(best), 1e-9), 3) if default_in or default_out else 1.0,
        "discount_max": round(max((_num(row[1].get("discount"), 0.0) or 0.0) for row in usable), 4),
        "discount_provider": max_discount_row[0].get("provider_name"), "base_price": round(_discounted_base(blended(best), discount), 6),
        "uptime_1d": round(_uptime(endpoint), 3), "context": int(_num(meta.get("context_length"), 0) or 0),
        "intelligence": _num(aa.get("intelligence_index")), "coding": _num(aa.get("coding_index")), "agentic": _num(aa.get("agentic_index")),
        "has_tools": "tools" in (meta.get("supported_parameters") or []) or "tools" in (endpoint.get("supported_parameters") or []),
        "modality": " -> ".join(meta.get("architecture", {}).get("input_modalities", ["text"])) + " -> " + ", ".join(meta.get("architecture", {}).get("output_modalities", ["text"])),
        "is_free": price_in == 0, "has_tiered_pricing": has_tiered, "pricing_overrides": overrides,
        "da_categories": len(da), "da_best_rank": min(da_ranks) if da_ranks else None, "da_best_elo": max(da_elos) if da_elos else None, "age_days": age,
        "reasoning_default_effort": reasoning.get("default_effort"), "reasoning_mandatory": bool(reasoning.get("mandatory", False)), "reasoning_efforts": reasoning.get("supported_efforts") or [],
        "gate_reason": meta.get("gate_reason", []), "variant_count": int(meta.get("_variant_count", 1) or 1), "generated_at": generated_at,
    }


def normalize_all(models: list[dict], endpoints_by_slug: dict[str, list[dict]], generated_at: str) -> list[dict]:
    rows = []
    for meta in models:
        key = meta.get("id") or meta["canonical_slug"]
        endpoints = endpoints_by_slug.get(key)
        if endpoints is None and key != meta["canonical_slug"]:
            endpoints = endpoints_by_slug.get(meta["canonical_slug"], [])
        rows.append(normalize_model(meta, endpoints or [], generated_at))
    return rows
