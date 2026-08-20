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
from .openrouter import fetch_endpoint_batch, fetch_models
from .recommend import recommend
from .report import render_report

LOG = logging.getLogger("advisor.pipeline")
ROOT = Path(__file__).resolve().parents[1]


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def build(models: list[dict], endpoints_by_slug: dict[str, list[dict]], generated_at: str | None = None) -> dict:
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
    return {"snapshot": snapshot, "shortlist": shortlist, "gate_rejected": reject_artifact}


def write_artifacts(artifacts: dict, root: Path = ROOT) -> None:
    snapshot = artifacts["snapshot"]
    date = snapshot["generated_at"][:10]
    dump(root / "data" / "snapshots" / f"{date}.json", snapshot)
    dump(root / "data" / "latest.json", snapshot)
    dump(root / "shortlist.json", artifacts["shortlist"])
    dump(root / "data" / "gate_rejected.json", artifacts["gate_rejected"])
    (root / "report.md").write_text(render_report(artifacts["shortlist"], snapshot, artifacts["gate_rejected"]), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-key", action="store_true", help="force public requests")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    api_key = None if args.no_key else os.environ.get("OPENROUTER_API_KEY")
    models = fetch_models(api_key)
    gated, rejected = gate(models)
    LOG.info("models=%d prefiltered=%d gated=%d rejected=%d", len(models), len(prefilter(models)[0]), len(gated), len(rejected))
    endpoint_data = fetch_endpoint_batch(gated, api_key, workers=8)
    artifacts = build(models, endpoint_data)
    write_artifacts(artifacts)
    endpoint_errors = artifacts["shortlist"]["gate"].get("endpoint_errors", 0)
    if endpoint_errors:
        LOG.warning("models with empty or unusable endpoints=%d; recorded in data/gate_rejected.json", endpoint_errors)
    LOG.info("wrote shortlist.json, report.md, latest.json, snapshot and gate_rejected.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
