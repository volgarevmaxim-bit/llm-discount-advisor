"""The scope gate runs before any per-model endpoint request."""
from datetime import datetime, timezone
from .config import GATE_DA_CATEGORIES, GATE_DA_RANK, GATE_MAX_AGE_DAYS, GATE_TOP_N


def _quality(model: dict, key: str):
    value = (model.get("benchmarks") or {}).get("artificial_analysis", {}).get(key)
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _price(model: dict) -> float:
    pricing = model.get("pricing") or {}
    try:
        pin = float(pricing.get("prompt", 0)) * 1_000_000
        pout = float(pricing.get("completion", 0)) * 1_000_000
    except (TypeError, ValueError):
        return 0.0
    return (3 * pin + pout) / 4


def _family_quality(rows: list[dict], metric: str):
    values = [value for value in (_quality(model, metric) for model in rows) if value is not None]
    return max(values) if values else None


def _da_rows(model: dict) -> list[dict]:
    value = (model.get("benchmarks") or {}).get("design_arena") or []
    return value if isinstance(value, list) else []


def _age_days(model: dict, now: datetime) -> int | None:
    raw = model.get("created")
    if raw is None:
        return None
    try:
        created = datetime.fromtimestamp(float(raw), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None
    return max(0, (now - created).days)


def prefilter(models: list[dict]) -> tuple[list[dict], list[dict]]:
    """Remove aliases/non-text/voice models without endpoint requests."""
    eligible, rejected = [], []
    for model in models:
        slug = model.get("canonical_slug")
        if not slug:
            rejected.append({"slug": model.get("id", ""), "reason": "missing_canonical_slug"})
            continue
        if model.get("alias_target"):
            rejected.append({"slug": slug, "reason": "alias"})
            continue
        architecture = model.get("architecture") or {}
        outputs = architecture.get("output_modalities") or ["text"]
        if any(item not in {"text"} for item in outputs):
            rejected.append({"slug": slug, "reason": "non_text_output"})
            continue
        if model.get("supported_voices"):
            rejected.append({"slug": slug, "reason": "voice_model"})
            continue
        eligible.append(model)
    return eligible, rejected


def gate(models: list[dict], now: datetime | None = None) -> tuple[list[dict], list[dict]]:
    """Apply OR-of-G1..G4,G6; annotate admitted models with every reason."""
    now = now or datetime.now(timezone.utc)
    eligible, rejected = prefilter(models)
    families: dict[str, list[dict]] = {}
    for model in eligible:
        families.setdefault(model["canonical_slug"], []).append(model)
    ranking_sets: dict[str, set[str]] = {}
    for metric in ("intelligence_index", "coding_index", "agentic_index"):
        quality_ranked = sorted(
            ((slug, _family_quality(rows, metric)) for slug, rows in families.items()),
            key=lambda pair: pair[1] if pair[1] is not None else float("-inf"),
            reverse=True,
        )
        short = metric.removesuffix("_index")
        ranking_sets[f"q:{short}"] = {slug for slug, value in quality_ranked[:GATE_TOP_N] if value is not None}
        value_ranked = []
        for slug, rows in families.items():
            quality = _family_quality(rows, metric)
            price = min((_price(m) for m in rows), default=0.0)
            if quality is not None:
                value_ranked.append((slug, quality / price if price > 0 else float("inf")))
        value_ranked.sort(key=lambda pair: pair[1], reverse=True)
        ranking_sets[f"v:{short}"] = {slug for slug, _ in value_ranked[:GATE_TOP_N]}

    passed, final_rejected = [], list(rejected)
    for slug, family in families.items():
        reasons = [key for key, slugs in ranking_sets.items() if slug in slugs]
        da = [row for model in family for row in _da_rows(model)]
        if any(_safe_rank(row) <= GATE_DA_RANK for row in da):
            reasons.append("G3:design_arena")
        if any(_price(model) == 0 for model in family):
            reasons.append("G4:free")
        recent_participation = any(
            len(_da_rows(model)) >= GATE_DA_CATEGORIES
            and (age := _age_days(model, now)) is not None
            and age < GATE_MAX_AGE_DAYS
            for model in family
        )
        if recent_participation:
            reasons.append("G6:participation")
        if reasons:
            for model in family:
                copy = dict(model)
                copy["gate_reason"] = list(reasons)
                passed.append(copy)
        else:
            final_rejected.extend({"slug": model.get("id") or slug, "reason": "below_all_thresholds"} for model in family)
    return passed, final_rejected


def _safe_rank(row: dict) -> float:
    try:
        return float(row.get("rank", float("inf")))
    except (TypeError, ValueError):
        return float("inf")
