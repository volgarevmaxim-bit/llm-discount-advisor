"""Explainable, threshold-and-zone recommendations for the four PoC profiles."""
from __future__ import annotations
from .config import MIN_UPTIME, Profile, profile_blended

STATUS_LABELS = {
    "default": "Это твой рабочий вариант",
    "good_enough_cheaper": "Не хуже по сути, но дешевле",
    "big_discount_not_safe": "Большая скидка, но не для основной работы",
    "cheaper_provider": "Та же модель, но дешевле провайдер",
    "not_worth_switching": "Скорее всего, менять не стоит",
}


def _quality(model: dict, profile: Profile):
    return model.get(profile.quality_metric)


def _eligible(models: list[dict], profile: Profile) -> list[dict]:
    result = []
    for model in models:
        quality = _quality(model, profile)
        if quality is None or quality < profile.q_min or model.get("context", 0) < profile.min_context:
            continue
        if profile.needs_tools and not model.get("has_tools"):
            continue
        if model.get("uptime_1d", 0) < MIN_UPTIME:
            continue
        if profile.key == "bulk" and model.get("reasoning_mandatory"):
            continue
        result.append(model)
    return result


def _decorate(model: dict, profile: Profile, status: str, reason: str, blended: float) -> dict:
    return {
        "slug": model["slug"], "name": model["name"], "provider": model.get("best_provider"), "status": status, "label": STATUS_LABELS[status], "reason": reason,
        "blended_price": round(blended, 4), "base_price": model.get("base_price"), "quality": _quality(model, profile), "quality_metric": profile.quality_metric,
        "intelligence": model.get("intelligence"), "coding": model.get("coding"), "agentic": model.get("agentic"), "context": model.get("context"), "uptime_1d": model.get("uptime_1d"),
        "discount": model.get("discount_max", 0), "has_tiered_pricing": model.get("has_tiered_pricing", False), "reasoning_default_effort": model.get("reasoning_default_effort"),
        "reasoning_mandatory": model.get("reasoning_mandatory", False), "provider_count": model.get("provider_count"), "overpay_ratio": model.get("overpay_ratio"), "signals": [],
    }


def recommend(models: list[dict], profile: Profile) -> dict:
    candidates = []
    for original in models:
        model = dict(original)
        model["blended_price"] = profile_blended(model, profile)
        model["value_ratio"] = (_quality(model, profile) or 0) / max(model["blended_price"], 1e-9)
        candidates.append(model)
    eligible = _eligible(candidates, profile)
    if not eligible:
        return {"profile": profile.key, "title": profile.title, "q_min": profile.q_min, "picks": [], "rejected": [], "ratio": profile.ratio_label}
    by_price = sorted(eligible, key=lambda m: m["blended_price"])
    default = max(eligible, key=lambda m: (m["value_ratio"], _quality(m, profile) or 0))
    default_price = default["blended_price"]
    default_quality = _quality(default, profile) or 0
    best_quality = max(_quality(other, profile) or 0 for other in eligible)
    default_reason = f"{profile.quality_metric} {default_quality:.1f} при цене ${default_price:.3f}/1M; от лидера по качеству отстаёт на {max(0, best_quality - default_quality):.1f} п."
    picks = [_decorate(default, profile, "default", default_reason, default_price)]
    provider_candidates = [m for m in eligible if m.get("overpay_ratio", 1) >= 1.5 and m.get("uptime_1d", 0) >= 99 and m["slug"] != default["slug"]]
    if provider_candidates:
        candidate = max(provider_candidates, key=lambda m: m.get("overpay_ratio", 1))
        picks.append(_decorate(candidate, profile, "cheaper_provider", f"У этой же модели есть провайдер дешевле в {candidate['overpay_ratio']:.1f} раза при uptime {candidate['uptime_1d']:.2f}%.", candidate["blended_price"]))
    cheaper = [m for m in by_price if m["slug"] != default["slug"] and m["blended_price"] <= default_price * 0.7 and (_quality(m, profile) or 0) >= default_quality - 5]
    if cheaper:
        candidate = cheaper[0]
        savings = 100 * (1 - candidate["blended_price"] / default_price)
        picks.append(_decorate(candidate, profile, "good_enough_cheaper", f"Качество {(_quality(candidate, profile) or 0):.1f} не более чем на 5 п. ниже дефолта, цена на {savings:.0f}% ниже.", candidate["blended_price"]))
    discounts = [m for m in by_price if m.get("discount_max", 0) >= 0.3 and m["slug"] not in {p["slug"] for p in picks}]
    if discounts:
        candidate = discounts[0]
        picks.append(_decorate(candidate, profile, "big_discount_not_safe", f"Скидка {candidate['discount_max']:.0%} активна, но качество {(_quality(candidate, profile) or 0):.1f} требует осторожной проверки.", candidate["blended_price"]))
    remaining = [m for m in sorted(eligible, key=lambda m: m["value_ratio"], reverse=True) if m["slug"] not in {p["slug"] for p in picks}]
    if remaining and len(picks) < profile.max_cards:
        candidate = remaining[0]
        picks.append(_decorate(candidate, profile, "not_worth_switching", f"Преимущество не окупает смену: цена ${candidate['blended_price']:.3f}/1M без минимум 30% экономии относительно дефолта.", candidate["blended_price"]))
    return {"profile": profile.key, "title": profile.title, "q_min": profile.q_min, "ratio": profile.ratio_label, "picks": picks[:profile.max_cards], "rejected": [], "eligible_count": len(eligible)}
