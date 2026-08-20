"""Secondary OpenRouter evidence with explicit scopes and coverage counts."""
from __future__ import annotations

import re

from .rankings import family_join_key


def _family(value: str | None) -> str | None:
    return family_join_key(value)


def _benchmark_item(row: dict) -> dict:
    return {
        "benchmark_type": row.get("benchmark_type"),
        "model_permaslug": row.get("model_permaslug"),
        "canonical_family": _family(row.get("model_permaslug")),
        "avg_cost_per_task_usd": row.get("avg_cost_per_task"),
        "quality_metric": "accuracy",
        "quality": row.get("accuracy"),
        "total_tasks": row.get("total_tasks"),
        "last_run_at": row.get("last_run_timestamp"),
        "source": row.get("source", "openrouter"),
        "evidence_tier": "A",
        "scope": "named_benchmark_run",
    }


def _session_item(row: dict) -> dict:
    return {
        "app_slug": row.get("app_slug"),
        "app_name": row.get("app_name"),
        "turn_range": row.get("turn_range"),
        "model_permaslug": row.get("model_permaslug"),
        "canonical_family": _family(row.get("model_permaslug")),
        "median_session_cost_usd": row.get("median_session_cost_usd"),
        "window_days": row.get("window_days"),
        "as_of": row.get("as_of"),
        "source": "openrouter",
        "evidence_tier": "B",
        "scope": "named_application_workload",
    }


def build_task_cost_evidence(benchmarks: list[dict], sessions: list[dict], generated_at: str | None = None, benchmark_meta: list[dict] | None = None, session_meta: dict | None = None) -> dict:
    benchmark_meta = benchmark_meta or []
    session_meta = session_meta or {}
    evidence = {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "sources": {
            "benchmarks": {"urls": ["https://openrouter.ai/api/v1/benchmarks?source=openrouter"], "meta": benchmark_meta},
            "session_cost": {"url": "https://openrouter.ai/api/v1/datasets/session-cost", "meta": session_meta},
        },
        "benchmarks": [_benchmark_item(row) for row in benchmarks],
        "session_cost": [_session_item({**row, "window_days": session_meta.get("window_days"), "as_of": session_meta.get("as_of")}) for row in sessions],
        "attribution": "Source: OpenRouter evals (openrouter.ai) via OpenRouter (openrouter.ai/rankings).",
    }
    return evidence


def classify_coverage(catalog_families: list[str], rankings_families: list[str], benchmark_families: list[str], session_families: list[str], signals: dict[str, dict] | None = None, current_picks: set[str] | None = None) -> dict:
    signals = signals or {}
    current_picks = current_picks or set()
    catalog = sorted({_family(value) for value in catalog_families if _family(value)})
    rankings = {_family(value) for value in rankings_families if _family(value)}
    benchmark = {_family(value) for value in benchmark_families if _family(value)}
    session = {_family(value) for value in session_families if _family(value)}
    secondary = benchmark | session
    families = []
    for family in catalog:
        covered_by = []
        if family in rankings:
            covered_by.append("rankings_surface")
        if family in benchmark:
            covered_by.append("benchmark_cost")
        if family in session:
            covered_by.append("session_cost")
        if covered_by:
            classification = "covered"
        else:
            score_map = (signals.get(family) or {}).get("quality_scores") or {}
            strong_quality = any(value is not None and float(value) >= 45 for value in score_map.values())
            classification = "worthy_candidate" if family in current_picks or strong_quality else "likely_low_signal"
        families.append({"canonical_family": family, "covered_by": covered_by, "classification": classification})
    uncovered = [row for row in families if not row["covered_by"]]
    return {
        "schema_version": "1.0",
        "counts": {
            "families_total": len(catalog),
            "rankings_surface_families": len(rankings),
            "benchmark_cost_families": len(benchmark),
            "session_cost_families": len(session),
            "union_secondary_covered": len(secondary),
            "uncovered": len(uncovered),
            "worthy_uncovered": sum(row["classification"] == "worthy_candidate" for row in uncovered),
            "likely_low_signal_uncovered": sum(row["classification"] == "likely_low_signal" for row in uncovered),
        },
        "families": families,
    }


def coverage_for_artifacts(catalog_rows: list[dict], ranking_rows: list[dict], evidence: dict, signals: dict | None = None, current_picks: set[str] | None = None, catalog_families: list[str] | None = None) -> dict:
    catalog_families = catalog_families if catalog_families is not None else [row.get("canonical_slug") for row in catalog_rows]
    ranking_families = [row.get("permaslug") or row.get("ranking_key") for row in ranking_rows]
    benchmark_families = [row.get("canonical_family") or row.get("model_permaslug") for row in evidence.get("benchmarks", [])]
    session_families = [row.get("canonical_family") or row.get("model_permaslug") for row in evidence.get("session_cost", [])]
    return classify_coverage(catalog_families, ranking_families, benchmark_families, session_families, signals, current_picks)


def extract_evidence_payload(payload: dict) -> tuple[list[dict], dict]:
    rows = payload.get("data") if isinstance(payload, dict) else []
    meta = payload.get("meta") if isinstance(payload, dict) else {}
    return (rows if isinstance(rows, list) else []), (meta if isinstance(meta, dict) else {})
