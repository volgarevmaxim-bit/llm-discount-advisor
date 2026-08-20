"""Stdlib OpenRouter client for public and authenticated MVP-1 sources."""
from __future__ import annotations
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

LOG = logging.getLogger("advisor.openrouter")
PUBLIC_BASE_URL = "https://openrouter.ai/api/v1"
FRONTEND_RANKINGS_URL = "https://openrouter.ai/api/frontend/v1/rankings/benchmarks"


class OpenRouterError(RuntimeError):
    pass


def get_url(url: str, api_key: str | None = None, attempts: int = 4, timeout: int = 30):
    last = None
    for attempt in range(attempts):
        headers = {"Accept": "application/json", "User-Agent": "llm-discount-advisor-mvp1/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            with urlopen(Request(url, headers=headers), timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last = exc
            if exc.code == 429:
                LOG.warning("429 rate limit: %s (attempt %d/%d)", url, attempt + 1, attempts)
            if exc.code not in {408, 425, 429, 500, 502, 503, 504} or attempt == attempts - 1:
                break
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            if attempt == attempts - 1:
                break
        time.sleep(0.5 * (2 ** attempt))
    raise OpenRouterError(f"GET {url} failed after {attempts} attempts: {last}")


def get_json(path: str, api_key: str | None = None, attempts: int = 4, timeout: int = 30):
    return get_url(PUBLIC_BASE_URL + path, api_key, attempts, timeout)


def fetch_rankings_surface() -> dict:
    payload = get_url(FRONTEND_RANKINGS_URL)
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
        raise OpenRouterError("frontend rankings response has no data object")
    return payload


def fetch_models(api_key: str | None = None) -> list[dict]:
    payload = get_json("/models", api_key)
    models = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        raise OpenRouterError("/models response has no data list")
    return models


def endpoint_slug(model: dict) -> str:
    return model.get("id") or model.get("canonical_slug") or ""


def fetch_endpoints(slug: str, api_key: str | None = None) -> list[dict]:
    encoded = quote(slug, safe="/:")
    payload = get_json(f"/models/{encoded}/endpoints", api_key)
    data = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(data, dict):
        endpoints = data.get("endpoints")
    else:
        endpoints = data
    if not isinstance(endpoints, list):
        raise OpenRouterError(f"/endpoints response for {slug} has no list")
    return endpoints


def fetch_endpoint_batch(models: list[dict], api_key: str | None = None, workers: int = 8) -> dict[str, list[dict]]:
    results = {}
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="or-endpoint") as pool:
        futures = {pool.submit(fetch_endpoints, endpoint_slug(model), api_key): endpoint_slug(model) for model in models}
        for future in as_completed(futures):
            slug = futures[future]
            results[slug] = future.result()
    return results


def fetch_secondary_evidence(api_key: str) -> tuple[list[dict], list[dict], dict]:
    if not api_key:
        raise OpenRouterError("authenticated evidence requires an API key")
    benchmark_rows = []
    benchmark_meta = []
    for benchmark_type in ("gpqa_diamond", "tau_bench_verified_airline"):
        payload = get_json(f"/benchmarks?source=openrouter&benchmark_type={benchmark_type}&max_results=100", api_key)
        rows = payload.get("data") if isinstance(payload, dict) else []
        benchmark_rows.extend(rows if isinstance(rows, list) else [])
        benchmark_meta.append(payload.get("meta", {}) if isinstance(payload, dict) else {})
    session_payload = get_json("/datasets/session-cost", api_key)
    session_rows = session_payload.get("data") if isinstance(session_payload, dict) else []
    session_meta = session_payload.get("meta", {}) if isinstance(session_payload, dict) else {}
    return benchmark_rows, (session_rows if isinstance(session_rows, list) else []), {"benchmark_meta": benchmark_meta, "session_meta": session_meta}
