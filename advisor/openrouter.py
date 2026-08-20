"""Small stdlib OpenRouter client with bounded retries and concurrency=8."""
from __future__ import annotations
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

LOG = logging.getLogger("advisor.openrouter")
BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterError(RuntimeError):
    pass


def get_json(path: str, api_key: str | None = None, attempts: int = 4, timeout: int = 30):
    url = BASE_URL + path
    last = None
    for attempt in range(attempts):
        headers = {"Accept": "application/json", "User-Agent": "llm-discount-advisor-poc/1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        try:
            with urlopen(Request(url, headers=headers), timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last = exc
            if exc.code == 429:
                LOG.warning("429 rate limit: %s (attempt %d/%d)", path, attempt + 1, attempts)
            if exc.code not in {408, 425, 429, 500, 502, 503, 504} or attempt == attempts - 1:
                break
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
            if attempt == attempts - 1:
                break
        time.sleep(0.5 * (2**attempt))
    raise OpenRouterError(f"GET {url} failed after {attempts} attempts: {last}")


def fetch_models(api_key: str | None = None) -> list[dict]:
    payload = get_json("/models", api_key)
    models = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(models, list):
        raise OpenRouterError("/models response has no data list")
    return models


def endpoint_slug(model: dict) -> str:
    """Return the unique catalog id used by the endpoints route.

    OpenRouter currently exposes a family-level ``canonical_slug`` together
    with distinct ``id`` variants such as ``:free`` and ``:batch``.  The
    family remains the benchmark/gate key; the variant id is the price source
    key.  Falling back to canonical_slug keeps old fixtures compatible.
    """
    return model.get("id") or model.get("canonical_slug") or ""


def fetch_endpoints(slug: str, api_key: str | None = None) -> list[dict]:
    encoded = quote(slug, safe="/:")
    payload = get_json(f"/models/{encoded}/endpoints", api_key)
    endpoints = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(endpoints, dict):
        endpoints = endpoints.get("endpoints")
    if not isinstance(endpoints, list):
        raise OpenRouterError(f"/endpoints response for {slug} has no list")
    return endpoints


def fetch_endpoint_batch(models: list[dict], api_key: str | None = None, workers: int = 8) -> dict[str, list[dict]]:
    results: dict[str, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="or-endpoint") as pool:
        futures = {pool.submit(fetch_endpoints, endpoint_slug(model), api_key): endpoint_slug(model) for model in models}
        for future in as_completed(futures):
            slug = futures[future]
            results[slug] = future.result()
    return results
