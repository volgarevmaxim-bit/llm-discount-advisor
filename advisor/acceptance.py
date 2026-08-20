"""Acceptance comparison: same normalized rows, full vs gated shortlist."""
from __future__ import annotations
import json
from pathlib import Path
from .config import PROFILE_BY_KEY
from .gate import gate
from .recommend import _eligible


def code_top10(models: list[dict]) -> list[str]:
    profile = PROFILE_BY_KEY["code"]
    rows = []
    for model in models:
        row = dict(model)
        if "price_in" not in row:
            pricing = row.get("pricing") or {}
            row["price_in"] = float(pricing.get("prompt", 0)) * 1_000_000
            row["price_out"] = float(pricing.get("completion", 0)) * 1_000_000
            aa = (row.get("benchmarks") or {}).get("artificial_analysis") or {}
            row["coding"] = aa.get("coding_index")
            row["slug"] = row.get("canonical_slug")
            row["context"] = row.get("context_length", 128_000)
            row["has_tools"] = True
            row["uptime_1d"] = 100
        row["blended_price"] = (3 * row["price_in"] + row["price_out"]) / 4
        row["value_ratio"] = (row.get("coding") or 0) / max(row["blended_price"], 1e-9)
        rows.append(row)
    eligible = _eligible(rows, profile)
    # The gate works on canonical families, while endpoint pricing is fetched
    # per catalog variant (base/:free/:batch).  Pick the best eligible variant
    # for each family before comparing top-10 families.
    families: dict[str, dict] = {}
    for row in eligible:
        family = row.get("canonical_slug") or row["slug"]
        current = families.get(family)
        if current is None or row["value_ratio"] > current["value_ratio"]:
            families[family] = row
    result = []
    for row in sorted(families.values(), key=lambda row: row["value_ratio"], reverse=True):
        family = row.get("canonical_slug") or row["slug"]
        result.append(family)
        if len(result) == 10:
            break
    return result


def compare_normalized(full_models: list[dict], gated_models: list[dict]) -> dict:
    """Compare two runs over the same normalized endpoint-price rows."""
    full_top10 = code_top10(full_models)
    gated_top10 = code_top10(gated_models)
    overlap = len(set(full_top10) & set(gated_top10))
    return {
        "full_rows": len(full_models),
        "gated_rows": len(gated_models),
        "full_unique_families": len({row.get("canonical_slug", row.get("slug")) for row in full_models}),
        "gated_unique_families": len({row.get("canonical_slug", row.get("slug")) for row in gated_models}),
        "full_top10": full_top10,
        "gated_top10": gated_top10,
        "overlap": overlap,
        "target": 9,
        "passed": overlap >= 9,
    }


def compare(models: list[dict]) -> dict:
    gated, _ = gate(models)
    full = code_top10(models)
    reduced = code_top10(gated)
    overlap = len(set(full) & set(reduced))
    return {"full_models": len(models), "gated_models": len(gated), "full_top10": full, "gated_top10": reduced, "overlap": overlap, "target": 9, "passed": overlap >= 9}


def main(path: str = "tests/fixtures/models.json") -> int:
    models = json.loads(Path(path).read_text(encoding="utf-8"))
    print(json.dumps(compare(models), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
