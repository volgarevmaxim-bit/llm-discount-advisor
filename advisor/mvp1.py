"""Small composition layer for the revised MVP-1 artifacts."""
from __future__ import annotations

from .action import build_config_patch
from .changes import compare_decisions
from .config import PROFILES
from .decision import build_profile_decision
from .economics import calibration_for_rankings
from .evidence import build_task_cost_evidence, coverage_for_artifacts
from .rankings import normalize_rankings_payload


def _catalog_view(models: list[dict], endpoints_by_id: dict[str, list[dict]]) -> list[dict]:
    from .normalize import normalize_all

    normalized = []
    for model in models:
        key = model.get("id") or model.get("canonical_slug")
        endpoints = endpoints_by_id.get(key, [])
        try:
            normalized.extend(normalize_all([model], endpoints_by_id, model.get("generated_at")))
        except (ValueError, KeyError):
            continue
    return normalized


def _profile_points(decisions: list[dict]) -> list[dict]:
    return [
        {
            "profile": decision["profile"],
            "quality_metric": decision["quality_metric"],
            "price_metric": decision["price_metric"],
            "price_unit": decision["price_unit"],
            "candidate_count": decision["candidate_count"],
            "raw_pareto_count": decision["raw_pareto_count"],
            "stable_pareto_count": decision["stable_pareto_count"],
            "unmatched_quality_rows": decision["unmatched_quality_rows"],
            "unpriced_rows": decision["unpriced_rows"],
            "roles": decision["roles"],
            "raw_pareto": decision["raw_pareto"],
            "stable_pareto": decision["stable_pareto"],
            "candidates": decision["candidates"],
            "excluded": decision["excluded"],
            "margins": decision["margins"],
        }
        for decision in decisions
    ]


def _catalog_quality_signals(models: list[dict]) -> dict[str, dict]:
    signals = {}
    for model in models:
        family = model.get("canonical_slug")
        if not family:
            continue
        aa = (model.get("benchmarks") or {}).get("artificial_analysis") or {}
        signals[family] = {
            "quality_scores": {
                "intelligence": aa.get("intelligence_index"),
                "coding": aa.get("coding_index"),
                "agentic": aa.get("agentic_index"),
            }
        }
    return signals


def build_mvp1_artifacts(models: list[dict], endpoints_by_id: dict[str, list[dict]], rankings_payload: dict, generated_at: str, previous_decision: dict | None = None, benchmark_rows: list[dict] | None = None, session_rows: list[dict] | None = None, evidence_meta: dict | None = None) -> dict:
    ranking_surface = normalize_rankings_payload(rankings_payload, generated_at)
    catalog_rows = _catalog_view(models, endpoints_by_id)
    decisions = [build_profile_decision(ranking_surface, catalog_rows, profile) for profile in PROFILES]
    decision_surface = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "ranking_mode": "rankings_cost_per_request",
        "source_url": ranking_surface["source_url"],
        "profiles": _profile_points(decisions),
        "discount_calibration": {"status": "unknown", "sample_size": 20},
        "attribution": "Source: OpenRouter (openrouter.ai/rankings).",
    }
    evidence_meta = evidence_meta or {}
    evidence = build_task_cost_evidence(
        benchmark_rows or [],
        session_rows or [],
        generated_at,
        benchmark_meta=evidence_meta.get("benchmark_meta"),
        session_meta=evidence_meta.get("session_meta"),
    )
    current_picks = {
        (profile.get("roles") or {}).get("balanced_default", {}).get("canonical_slug")
        for profile in decisions
        if (profile.get("roles") or {}).get("balanced_default")
    }
    coverage = coverage_for_artifacts(
        catalog_rows,
        ranking_surface["quality_rows"],
        evidence,
        signals=_catalog_quality_signals(models),
        current_picks={value for value in current_picks if value},
        catalog_families=[model.get("canonical_slug") for model in models],
    )
    changes = compare_decisions(previous_decision, decision_surface)
    default = next((item["roles"]["balanced_default"] for item in decisions if item["profile"] == "code"), None)
    patch = build_config_patch("code", {}, {"model": (default or {}).get("variant_id"), "provider": (default or {}).get("provider"), "variant": (default or {}).get("variant_id")}, "MVP-1 recommendation preview; no automatic config changes.")
    return {
        "rankings_surface": ranking_surface,
        "decision_surface": decision_surface,
        "task_cost_evidence": evidence,
        "task_cost_coverage": coverage,
        "config_patch": patch,
        "changes": changes,
        "catalog_rows": catalog_rows,
    }


def build_live_mvp1_artifacts(models, endpoints_by_id, rankings_payload, generated_at, benchmark_rows=None, session_rows=None, previous_decision=None, evidence_meta=None):
    result = build_mvp1_artifacts(models, endpoints_by_id, rankings_payload, generated_at, previous_decision, benchmark_rows, session_rows, evidence_meta=evidence_meta)
    ranking_surface = result["rankings_surface"]
    result["decision_surface"]["discount_calibration"] = calibration_for_rankings(ranking_surface, result["catalog_rows"], endpoints_by_id, 20)
    return result
