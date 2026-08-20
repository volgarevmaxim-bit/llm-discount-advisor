"""OpenRouter frontend Rankings surface normalization and Pareto logic."""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone


SOURCE_URL = "https://openrouter.ai/api/frontend/v1/rankings/benchmarks"
CATEGORIES = ("intelligence", "coding", "agentic")
VARIANT_SUFFIX_RE = re.compile(r":(?:free|batch)$")


class RankingsSchemaError(ValueError):
    """Raised when the undocumented frontend Rankings shape is incompatible."""


def _number(value, field: str, *, allow_zero: bool = True) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise RankingsSchemaError(f"{field} must be numeric") from exc
    if not math.isfinite(number) or (not allow_zero and number <= 0) or number < 0:
        raise RankingsSchemaError(f"{field} must be a finite non-negative number")
    return number


def _generated_at(value: str | None) -> str:
    if value:
        return value
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_mapping(value, field: str) -> dict:
    if not isinstance(value, dict):
        raise RankingsSchemaError(f"{field} must be an object")
    return value


def normalize_rankings_payload(payload: dict, generated_at: str | None = None) -> dict:
    """Validate and reduce the live frontend response to reproducible fields."""
    root = _require_mapping(payload, "response")
    data = _require_mapping(root.get("data"), "response.data")
    aa_data = _require_mapping(data.get("aaData"), "response.data.aaData")
    cost_map = _require_mapping(data.get("costPerRequest"), "response.data.costPerRequest")
    weighted_map = _require_mapping(data.get("weightedInputPrices"), "response.data.weightedInputPrices")
    if "daData" not in data:
        raise RankingsSchemaError("response.data.daData is required")

    quality_rows: list[dict] = []
    categories: dict[str, dict] = {}
    for category in CATEGORIES:
        rows = aa_data.get(category)
        if not isinstance(rows, list):
            raise RankingsSchemaError(f"response.data.aaData.{category} must be an array")
        normalized_rows = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise RankingsSchemaError(f"{category}[{index}] must be an object")
            permaslug = row.get("permaslug")
            if not isinstance(permaslug, str) or not permaslug:
                raise RankingsSchemaError(f"{category}[{index}].permaslug is required")
            score = _number(row.get("score"), f"{category}[{index}].score")
            item = {
                "category": category,
                "ranking_key": permaslug,
                "permaslug": permaslug,
                "uid": row.get("uid"),
                "openrouter_slug": row.get("openrouter_slug"),
                "heuristic_openrouter_slug": row.get("heuristic_openrouter_slug"),
                "aa_name": row.get("aa_name"),
                "score": score,
            }
            normalized_rows.append(item)
            quality_rows.append(item.copy())
        categories[category] = {"quality_metric": category, "rows": len(normalized_rows), "items": normalized_rows}

    normalized_cost = {str(key): _number(value, f"costPerRequest[{key}]") for key, value in cost_map.items()}
    normalized_weighted = {str(key): _number(value, f"weightedInputPrices[{key}]") for key, value in weighted_map.items()}
    da_data = data.get("daData")
    if isinstance(da_data, dict):
        da_counts = {str(key): len(value) if isinstance(value, list) else 0 for key, value in da_data.items()}
    elif isinstance(da_data, list):
        da_counts = {"items": len(da_data)}
    else:
        raise RankingsSchemaError("response.data.daData must be an object or array")

    return {
        "schema_version": "1.0",
        "generated_at": _generated_at(generated_at),
        "source_url": SOURCE_URL,
        "categories": categories,
        "quality_rows": quality_rows,
        "cost_per_request": normalized_cost,
        "weighted_input_prices": normalized_weighted,
        "da_data_counts": da_counts,
    }


def family_join_key(value: str | None) -> str | None:
    """Remove only selectable variant suffixes for family joins."""
    if not isinstance(value, str) or not value:
        return None
    return VARIANT_SUFFIX_RE.sub("", value)


def join_ranking_to_catalog(ranking_row: dict, catalog_rows: list[dict]) -> dict:
    """Join one permaslug to catalog identity without mutating ranking identity."""
    ranking_key = ranking_row.get("ranking_key") or ranking_row.get("permaslug")
    if not ranking_key:
        return {"join_status": "unmatched", "ranking_key": ranking_key, "catalog_rows": []}
    exact_canonical = [row for row in catalog_rows if row.get("canonical_slug") == ranking_key]
    if exact_canonical:
        return {"join_status": "matched", "join_method": "canonical_slug", "ranking_key": ranking_key, "canonical_slug": ranking_key, "catalog_rows": exact_canonical}
    exact_id = [row for row in catalog_rows if row.get("id") == ranking_key]
    if exact_id:
        return {"join_status": "matched", "join_method": "variant_id", "ranking_key": ranking_key, "canonical_slug": exact_id[0].get("canonical_slug"), "catalog_rows": exact_id}

    heuristic = ranking_row.get("heuristic_openrouter_slug")
    if heuristic:
        heuristic_rows = [row for row in catalog_rows if row.get("id") == heuristic or row.get("canonical_slug") == heuristic]
        if heuristic_rows:
            return {"join_status": "matched", "join_method": "explicit_heuristic_fallback", "join_reason": "permaslug did not match catalog; frontend heuristic_openrouter_slug matched", "ranking_key": ranking_key, "canonical_slug": heuristic_rows[0].get("canonical_slug"), "catalog_rows": heuristic_rows}

    ranking_family = family_join_key(ranking_key)
    family_rows = [row for row in catalog_rows if family_join_key(row.get("canonical_slug")) == ranking_family or family_join_key(row.get("id")) == ranking_family]
    if family_rows:
        return {"join_status": "matched", "join_method": "family_suffix_fallback", "join_reason": "variant suffix removed for family join", "ranking_key": ranking_key, "canonical_slug": family_rows[0].get("canonical_slug"), "catalog_rows": family_rows}
    return {"join_status": "unmatched", "ranking_key": ranking_key, "catalog_rows": []}


def raw_pareto(points: list[dict]) -> list[dict]:
    """Reproduce the Rankings frontier: new strict maximum score by price."""
    ordered = sorted(points, key=lambda point: (point["price"], -point["score"], point["ranking_key"]))
    frontier: list[dict] = []
    best_score = float("-inf")
    for point in ordered:
        if point["score"] > best_score:
            frontier.append(point)
            best_score = point["score"]
    return frontier


def _stable_dominates(a: dict, b: dict, price_margin: float, quality_margin: float) -> bool:
    return (
        a["price"] <= b["price"] * (1 - price_margin)
        and a["score"] >= b["score"] + quality_margin
    )


def stable_pareto(points: list[dict], price_margin: float = 0.10, quality_margin: float = 2.0) -> list[dict]:
    """Return points not dominated after explicit stability margins."""
    if not 0 <= price_margin < 1:
        raise ValueError("price_margin must be in [0, 1)")
    if quality_margin < 0:
        raise ValueError("quality_margin must be non-negative")
    return [
        point for point in points
        if not any(_stable_dominates(other, point, price_margin, quality_margin) for other in points if other is not point)
    ]
