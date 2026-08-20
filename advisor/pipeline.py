"""Daily PoC pipeline and artifact writer."""
from __future__ import annotations
import argparse
import json
import logging
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from .config import PROFILES
from .gate import gate, prefilter
from .normalize import normalize_all
from .openrouter import (
    fetch_endpoint_batch,
    fetch_models,
    fetch_rankings_surface,
    fetch_secondary_evidence,
)
from .recommend import recommend
from .report import render_report
from .mvp1 import build_mvp1_artifacts
from .mvp1 import build_live_mvp1_artifacts

LOG = logging.getLogger("advisor.pipeline")
ROOT = Path(__file__).resolve().parents[1]


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_previous_decision(root: Path, generated_at: str) -> dict | None:
    """Load the latest compatible decision snapshot strictly before today."""
    current_day = generated_at[:10]
    directory = root / "data" / "decision_snapshots"
    if not directory.exists():
        return None
    candidates = sorted(
        path for path in directory.glob("*.json")
        if path.stem < current_day
    )
    for path in reversed(candidates):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            return value
    return None


def collect_mvp1_sources(api_key: str | None) -> dict:
    """Fetch public Rankings and optionally authenticated secondary evidence."""
    rankings_payload = fetch_rankings_surface()
    if not api_key:
        return {
            "rankings_payload": rankings_payload,
            "benchmark_rows": [],
            "session_rows": [],
            "evidence_meta": {},
            "secondary_status": "skipped_no_key",
        }
    benchmark_rows, session_rows, evidence_meta = fetch_secondary_evidence(api_key)
    return {
        "rankings_payload": rankings_payload,
        "benchmark_rows": benchmark_rows,
        "session_rows": session_rows,
        "evidence_meta": evidence_meta,
        "secondary_status": "fetched",
    }


def build(
    models: list[dict],
    endpoints_by_slug: dict[str, list[dict]],
    generated_at: str | None = None,
    rankings_payload: dict | None = None,
    benchmark_rows: list[dict] | None = None,
    session_rows: list[dict] | None = None,
    previous_decision: dict | None = None,
    evidence_meta: dict | None = None,
    calibrate_discount: bool = False,
) -> dict:
    generated_at = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    gated, rejected = gate(models)
    variant_counts = Counter(meta.get("canonical_slug") for meta in gated)
    normalized = []
    endpoint_errors = []
    for meta in gated:
        try:
            enriched = dict(meta)
            enriched["_variant_count"] = variant_counts[meta.get("canonical_slug")]
            normalized.extend(normalize_all([enriched], endpoints_by_slug, generated_at))
        except (ValueError, KeyError) as exc:
            endpoint_errors.append({"slug": meta.get("id") or meta["canonical_slug"], "canonical_slug": meta["canonical_slug"], "reason": f"endpoint_unusable: {exc}"})
    shortlist = {
        "generated_at": generated_at,
        "assumptions": {
            "blend_ratios": {p.key: p.ratio_label for p in PROFILES},
            "reasoning_effort": "default",
            "reasoning_note": "Цена соответствует дефолтному effort; при high фактический расход выше.",
            "price_source": "/api/v1/models/{id}/endpoints; canonical_slug is the family key",
        },
        "gate": {"considered": len(models), "considered_unique_families": len({m.get("canonical_slug") for m in prefilter(models)[0]}), "eligible_after_prefilter": len(prefilter(models)[0]), "passed": len(gated), "passed_unique_families": len({m.get("canonical_slug") for m in gated}), "normalized": len(normalized), "endpoint_errors": len(endpoint_errors), "rules": "G1-G4,G6"},
        "profiles": [recommend(normalized, profile) for profile in PROFILES],
    }
    snapshot = {"generated_at": generated_at, "source": "openrouter", "model_count": len(models), "model_family_count": len({m.get("canonical_slug") for m in models}), "eligible_after_prefilter": len(prefilter(models)[0]), "eligible_unique_families": len({m.get("canonical_slug") for m in prefilter(models)[0]}), "gated_count": len(gated), "gated_unique_families": len({m.get("canonical_slug") for m in gated}), "models": normalized}
    reject_artifact = {"generated_at": generated_at, "total": len(models), "total_unique_families": len({m.get("canonical_slug") for m in models}), "passed": len(gated), "passed_unique_families": len({m.get("canonical_slug") for m in gated}), "normalized": len(normalized), "eligible_after_prefilter": len(prefilter(models)[0]), "eligible_unique_families": len({m.get("canonical_slug") for m in prefilter(models)[0]}), "rejected": rejected + endpoint_errors}
    artifacts = {"snapshot": snapshot, "shortlist": shortlist, "gate_rejected": reject_artifact}
    if rankings_payload is not None:
        builder = build_live_mvp1_artifacts if calibrate_discount else build_mvp1_artifacts
        artifacts["mvp1"] = builder(
            models,
            endpoints_by_slug,
            rankings_payload,
            generated_at,
            previous_decision=previous_decision,
            benchmark_rows=benchmark_rows,
            session_rows=session_rows,
            evidence_meta=evidence_meta or {},
            )
    return artifacts


def write_artifacts(artifacts: dict, root: Path = ROOT) -> None:
    snapshot = artifacts["snapshot"]
    date = snapshot["generated_at"][:10]
    dump(root / "data" / "snapshots" / f"{date}.json", snapshot)
    dump(root / "data" / "latest.json", snapshot)
    dump(root / "shortlist.json", artifacts["shortlist"])
    dump(root / "data" / "gate_rejected.json", artifacts["gate_rejected"])
    (root / "report.md").write_text(
        render_report(
            artifacts["shortlist"],
            snapshot,
            artifacts["gate_rejected"],
            mvp1=artifacts.get("mvp1"),
        ),
        encoding="utf-8",
    )
    mvp1 = artifacts.get("mvp1")
    if mvp1:
        dump(
            root / "data" / "decision_snapshots" / f"{snapshot['generated_at'][:10]}.json",
            mvp1["decision_surface"],
        )
        dump(root / "data" / "rankings_surface.json", mvp1["rankings_surface"])
        dump(root / "data" / "decision_surface.json", mvp1["decision_surface"])
        dump(root / "data" / "task_cost_evidence.json", mvp1["task_cost_evidence"])
        dump(root / "data" / "task_cost_coverage.json", mvp1["task_cost_coverage"])
        dump(root / "data" / "config_patch.json", mvp1["config_patch"])
        dump(root / "changes.json", mvp1["changes"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-key", action="store_true", help="force public requests")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    api_key = None if args.no_key else os.environ.get("OPENROUTER_API_KEY")
    models = fetch_models(api_key)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    previous_decision = load_previous_decision(ROOT, generated_at)
    gated, rejected = gate(models)
    LOG.info("models=%d prefiltered=%d gated=%d rejected=%d", len(models), len(prefilter(models)[0]), len(gated), len(rejected))
    endpoint_data = fetch_endpoint_batch(gated, api_key, workers=8)
    sources = collect_mvp1_sources(api_key)
    artifacts = build(
        models,
        endpoint_data,
        generated_at=generated_at,
        rankings_payload=sources["rankings_payload"],
        benchmark_rows=sources["benchmark_rows"],
        session_rows=sources["session_rows"],
        previous_decision=previous_decision,
        evidence_meta=sources["evidence_meta"],
        calibrate_discount=bool(api_key),
    )
    write_artifacts(artifacts)
    endpoint_errors = artifacts["shortlist"]["gate"].get("endpoint_errors", 0)
    if endpoint_errors:
        LOG.warning("models with empty or unusable endpoints=%d; recorded in data/gate_rejected.json", endpoint_errors)
    LOG.info(
        "wrote legacy artifacts plus MVP-1 artifacts; secondary evidence=%s",
        sources["secondary_status"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
