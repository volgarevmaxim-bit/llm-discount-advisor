# LLM Discount Advisor — MVP-1 Revised Spec

**Версия:** 2.0
**Дата:** 20 августа 2026
**Статус:** план реализации; код по этой spec ещё не начинать без явного `go` пользователя.
**Автор:** Максим Волгарев

> Эта spec заменяет прежний план MVP-1, в котором change detection шёл непосредственно поверх token-price ranking. Исходная Design Spec v1.3 и PoC остаются историческим baseline и источником уже проверенных ограничений.

## Changelog

- **2.0:** decision surface перестроена вокруг публичной Rankings-логики OpenRouter: task-relevant quality index × `Avg Price Per 100 Requests` × Pareto frontier. `avg_cost_per_task` и `session-cost` переведены в отдельный validation/evidence layer. Discount стал overlay для текущей экономики и YAML action, а не бездоказательной поправкой к benchmark cost. Change detection сравнивает decision outcome.

---

## 1. Executive decision

Продукт не должен отвечать на вопрос «у какой модели дешевле миллион токенов». Это слишком низкоуровневый сигнал.

Рабочий вопрос:

> Какую модель и какой текущий вариант/provider выбрать для конкретного типа работы, учитывая релевантное качество, operational cost, активный discount и возможность применить решение в Hermes YAML?

Новая основная цепочка:

```text
task profile
→ relevant quality index
→ Avg Price Per 100 Requests
→ raw Pareto frontier
→ stable Pareto with margins
→ current provider / variant / discount overlay
→ recommendation
→ YAML patch preview
→ change detection on decision outcome
```

Это приближает продукт к тому, как автор уже принимает решение вручную на OpenRouter Rankings: выбирает тип задачи, соответствующий quality index, operational price и смотрит Pareto. Страница OpenRouter прямо описывает Rankings как сравнение моделей по usage, а секция Benchmarks предоставляет выбор ценовой метрики, quality category и `Show Pareto`.[6]

### Что становится главным

- `costPerRequest` из публичной frontend Rankings surface;
- task-relevant Artificial Analysis score;
- raw и stable Pareto;
- current endpoint/provider/variant economics;
- actionable YAML patch preview.

### Что больше не является главным

- `blended_3to1`;
- `quality / blended_price`;
- произвольный universal `cost_per_task`;
- отдельные события мелких колебаний uptime/provider.

`blended_3to1` остаётся техническим fallback и диагностикой.

---

## 2. Источники и их роли

### 2.1 Primary decision surface — OpenRouter Rankings frontend

```text
GET https://openrouter.ai/api/frontend/v1/rankings/benchmarks
```

Это endpoint, который использует публичная Rankings page. Он не является описанным в присланной API reference публичным data contract, поэтому интеграция должна иметь schema guard и loud failure при несовместимом ответе.

Текущая живая структура ответа содержит:

```text
data.aaData.intelligence       — 114 rows
 data.aaData.coding             — 140 rows
data.aaData.agentic             — 115 rows
data.costPerRequest             — 179 model keys
data.weightedInputPrices        — 179 model keys
data.daData                     — Design Arena category arrays
```

Количество строк меняется. Эти числа — audit snapshot, а не постоянный контракт.[7]

#### Нормализуемые поля `aaData[category]`

```json
{
  "uid": "google/gemini-3.7-flash-20260813",
  "permaslug": "google/gemini-3.7-flash-20260813",
  "openrouter_slug": null,
  "heuristic_openrouter_slug": "google/gemini-3.7-flash",
  "aa_name": "Gemini 3.7 Flash (medium)",
  "score": 45.1
}
```

#### Нормализуемые ценовые поля

```json
{
  "costPerRequest": 0.6352683803,
  "weightedInputPrices": 0.163409
}
```

В UI `costPerRequest` отображается как **Avg Price Per 100 Requests**, а `weightedInputPrices` — как **Weighted Avg Input Price**. Нельзя переименовывать первое в `avg_cost_per_task`: это другая operational metric.[6][7]

### 2.2 Catalog and provider truth

```text
GET https://openrouter.ai/api/v1/models
GET https://openrouter.ai/api/v1/models/{id}/endpoints
```

Используется для:

- `canonical_slug` family identity;
- `id` / `variant_id` selectable variant identity;
- provider;
- current prompt/completion price;
- `discount`;
- recovered base price;
- uptime;
- reasoning labels;
- `:free`, `:batch` и другие варианты.

Frontend Rankings отвечает на вопрос «как выглядит operational price/quality surface». Endpoint data отвечает на вопрос «какое конкретное действие можно сделать сейчас».

### 2.3 Secondary validation evidence — authenticated Data API

```text
GET /api/v1/benchmarks?source=openrouter&benchmark_type=...
GET /api/v1/datasets/session-cost
```

`avg_cost_per_task` сохраняется как direct measurement для именованного benchmark run, но не становится главным ranking. `session-cost` сохраняется как direct measurement для именованного приложения и диапазона длины сессии. Эти метрики нельзя смешивать численно с `costPerRequest` или token price.[2][3][4][5]

Покрытие не считается предварительным блокером. Сначала строим основную decision surface, затем публикуем список моделей, которые не получили secondary evidence.

### 2.4 Attribution and source status

Производные артефакты должны сохранять:

- URL источника;
- время получения;
- `meta.as_of`, если источник его отдаёт;
- версию/тип источника;
- attribution, если публикуется производный набор данных.

Сырые ответы Data API не превращаем в публичное зеркало. Публикуем только нормализованные и производные данные.

---

## 3. Identity and joins

Три ключа имеют разные роли:

```text
canonical_slug — family key в проекте
id / variant_id — selectable OpenRouter variant
permaslug      — Rankings/Data API identity
```

### Правила

1. `permaslug` сохраняется без изменений как `ranking_key`.
2. Для family join используется `canonical_slug`.
3. Суффиксы `:free` и `:batch` снимаются только при family join, но не при сохранении variant identity.
4. При невозможности join кандидат получает `join_status: unmatched` и не становится default recommendation.
5. Нельзя подменять `permaslug` полем `heuristic_openrouter_slug` без явного fallback и записи причины.
6. Один и тот же family может иметь несколько selectable variants. Их нельзя сливать до слоя action.

Пример:

```json
{
  "ranking_key": "google/gemini-3.7-flash-20260813",
  "canonical_slug": "google/gemini-3.7-flash-20260813",
  "variant_id": "google/gemini-3.7-flash",
  "join_status": "matched"
}
```

Если frontend surface содержит только family-level `permaslug`, variants из `/models` добавляются как action alternatives, но не получают выдуманный `costPerRequest`.

---

## 4. Task profiles and relevant quality

Один quality metric для всех задач — дефект. Профиль выбирает relevant index.

| Profile | Relevant quality | Начальный floor | Action intent |
|---|---|---:|---|
| `chat` | `intelligence` | 55 | рабочий общий ассистент |
| `code` | `coding` | 60 | код и инженерные задачи |
| `agentic` | `agentic` | 45 | tool-use / coding-agent workflow |
| `longdoc` | `intelligence` | 55 | длинный контекст и документы |
| `bulk` | `intelligence` | 45 | массовая генерация; `reasoning_mandatory=true` исключается |

Floors `chat`, `code`, `longdoc`, `bulk` продолжают текущие PoC-константы. `agentic=45` — новая начальная константа для первой калибровки, а не утверждение о естественном пороге качества.

Каждый profile contract должен содержать:

```json
{
  "profile": "agentic",
  "quality_metric": "agentic",
  "quality_label": "Agentic Index Score",
  "quality_floor": 45,
  "price_metric": "costPerRequest",
  "price_label": "Avg Price Per 100 Requests",
  "min_uptime": 95.0,
  "requires_tools": true,
  "fallback_policy": "show_token_price_only"
}
```

Профиль может быть добавлен или скорректирован только через явную конфигурацию, а не через скрытый `if` в ranking code.

---

## 5. Price surface

### 5.1 Primary price

```text
price_metric = costPerRequest
unit = USD per 100 requests
source = openrouter frontend rankings
```

Это operational price proxy, соответствующий ручному UI OpenRouter. Он не называется universal task cost.

### 5.2 Secondary price views

```text
weightedInputPrices — USD per 1M weighted input
input list price    — USD per 1M input list price
```

Они сохраняются для объяснения, диагностики и discount audit. Они не заменяют `costPerRequest` в primary profile ranking.

### 5.3 Fallback

Если для candidate нет `costPerRequest`:

- candidate не попадает в comparable Pareto set;
- сохраняется в coverage artifact;
- может отображаться как `unpriced_candidate`;
- старый token-price ranking не смешивается с primary price ranking.

При полном отсутствии frontend endpoint разрешён explicit degraded mode:

```text
ranking_mode = token_price_fallback
```

Degraded mode должен быть заметен в report/UI и не может публиковаться как normal MVP-1 decision surface.

---

## 6. Pareto logic

### 6.1 Raw Pareto — воспроизведение OpenRouter

Цели:

- быть объяснимым;
- быть детерминированным;
- совпадать с ручной логикой страницы;
- не превращаться в скрытый weighted score.

Для каждого profile берём только candidates, у которых есть:

```text
relevant quality score
costPerRequest > 0 или равная нулевая цена
successful family join
```

Сортировка:

```python
(price ascending, score descending, ranking_key ascending)
```

Алгоритм:

```python
best_score = -infinity
frontier = []
for point in sorted_points:
    if point.score > best_score:
        frontier.append(point)
        best_score = point.score
```

Это соответствует наблюдаемой frontend-логике: цена — ось cost, quality — ось score; Pareto path оставляет точки, которые дают новый максимум score при росте цены.[6][7]

`raw_pareto` — transparency artifact. Его нельзя автоматически трактовать как единственный safe default.

### 6.2 Stable Pareto — для daily decision

Чтобы одна небольшая флуктуация не меняла action:

```text
PARETO_PRICE_MARGIN = 0.10
PARETO_QUALITY_MARGIN = 2.0
```

A margin-dominates B, если:

```text
A.price <= B.price * (1 - PARETO_PRICE_MARGIN)
AND
A.score >= B.score + PARETO_QUALITY_MARGIN
```

`stable_pareto` — candidates, для которых не существует такого A.

Raw frontier и stable frontier публикуются одновременно:

```json
{
  "raw_pareto": ["..."],
  "stable_pareto": ["..."],
  "margins": {
    "price_pct": 10,
    "quality_points": 2
  }
}
```

### 6.3 Recommendation roles

Не сводить всю decision surface к одной непрозрачной формуле. Для каждого profile публикуются три роли:

1. `cost_option` — самый дешёвый eligible candidate;
2. `quality_option` — самый качественный eligible candidate, при равной quality выбирается более дешёвый;
3. `balanced_default` — самый дешёвый stable-frontier candidate с quality не ниже `max(floor, best_quality - 2 points)`.

Если `balanced_default` отсутствует, default = `quality_option`, а причина явно указывает отсутствие подходящего stable frontier.

В UI default — одна карточка. Две альтернативы остаются рядом как объяснение trade-off.

---

## 7. Discount and provider overlay

### 7.1 Не считать discount второй раз

`costPerRequest` — агрегированная frontend metric. Пока не доказано, как она построена и отражает ли конкретный endpoint discount, нельзя делать:

```text
costPerRequest * (1 - discount)
```

и называть результат измеренной стоимостью.

Первый audit slice обязан сравнить для выборки минимум из 20 matched families:

```text
frontend costPerRequest
frontend weightedInputPrices
current endpoint prompt/completion prices
current discount
best reliable provider
```

Результат:

```text
discount_reflection_status = validated | inconsistent | unknown
```

Начальный acceptance gate для `validated`:

```text
не менее 16 из 20 families объяснимы одной согласованной текущей price relationship
с отклонением не более 20% после явного учёта unit и provider selection.
```

Если gate не пройден, discount остаётся overlay и action signal, а не числовой корректор primary ranking.

### 7.2 Что публикуем всегда

```json
{
  "discount_overlay": {
    "discount_max": 0.75,
    "discount_provider": "Google",
    "current_best_provider": "Google",
    "current_effective_price_in": 0.1875,
    "current_effective_price_out": 0.9375,
    "base_price": 1.5,
    "status": "active",
    "ranking_effect": "not_established"
  }
}
```

`ranking_cost` остаётся отдельным полем:

```json
{
  "ranking_cost_usd_per_100_requests": 0.635268,
  "ranking_cost_source": "openrouter_frontend_rankings"
}
```

### 7.3 Discount scenario

Если audit gate не пройден, допускается только отдельный сценарный блок:

```json
{
  "discount_scenario": {
    "status": "scenario_only",
    "estimated_cost": null,
    "reason": "Не доказано, что frontend costPerRequest можно пропорционально пересчитать по endpoint discount."
  }
}
```

Если relationship будет подтверждена, сценарный rank можно включить отдельным полем:

```text
base_rank
scenario_rank
rank_delta
scenario_method
scenario_confidence
```

Scenario никогда не затирает observed `costPerRequest`.

### 7.4 Action relevance

Discount уже достаточно полезен без фальшивого пересчёта, если он меняет конкретное действие:

- закрепить provider;
- выбрать `:free` / `:batch` variant;
- не менять model family, но поменять routing;
- оставить текущий YAML, потому что discount уже отражён у используемого provider.

---

## 8. Secondary task-cost evidence and coverage experiment

### 8.1 `avg_cost_per_task`

Сохраняем отдельно:

```json
{
  "benchmark_type": "tau_bench_verified_airline",
  "avg_cost_per_task_usd": 0.07709048,
  "quality_metric": "accuracy",
  "quality": 0.805556,
  "total_tasks": 48,
  "last_run_at": "2026-08-15T00:15:15.845Z",
  "source": "openrouter",
  "evidence_tier": "A",
  "scope": "named_benchmark_run"
}
```

Не используем для primary Pareto, потому что это другая единица и другое множество candidates.

### 8.2 `session-cost`

Сохраняем отдельно:

```json
{
  "app_slug": "claude-code",
  "turn_range": "10-49-turns",
  "median_session_cost_usd": 0.03219995,
  "window_days": 30,
  "as_of": "2026-08-17T13:30:26.781Z",
  "source": "openrouter",
  "evidence_tier": "B",
  "scope": "named_application_workload"
}
```

### 8.3 Coverage artifact

```text
data/task_cost_coverage.json
```

Обязательные counts:

```text
families_total
rankings_surface_families
benchmark_cost_families
session_cost_families
union_secondary_covered
uncovered
worthy_uncovered
likely_low_signal_uncovered
```

Каждый uncovered family получает одну из меток:

```text
worthy_candidate
needs_review
likely_low_signal
```

Критерии `worthy_candidate`:

- текущий PoC pick;
- проходит хотя бы один профильный quality floor;
- сильный relevant AA score;
- сильный Design Arena/usage signal;
- явно пригодный variant/provider.

Coverage experiment не скрывает достойные модели и не добавляет их в сравнимый Pareto без primary price/quality evidence.

---

## 9. Output artifacts

### `data/rankings_surface.json`

Нормализованный primary source snapshot:

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-08-20T12:00:00Z",
  "source_url": "https://openrouter.ai/api/frontend/v1/rankings/benchmarks",
  "categories": {
    "agentic": {
      "quality_metric": "agentic",
      "rows": 115
    }
  },
  "cost_per_request": {
    "google/gemini-3.7-flash-20260813": 0.635268
  },
  "weighted_input_prices": {
    "google/gemini-3.7-flash-20260813": 0.163409
  }
}
```

Не сохранять необработанный огромный response без необходимости. Сохранять только нормализованные поля, необходимые для воспроизводимости и audit.

### `data/decision_surface.json`

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-08-20T12:00:00Z",
  "ranking_mode": "rankings_cost_per_request",
  "profiles": [
    {
      "profile": "agentic",
      "quality_metric": "agentic",
      "price_metric": "costPerRequest",
      "price_unit": "usd_per_100_requests",
      "candidate_count": 60,
      "raw_pareto_count": 8,
      "stable_pareto_count": 6,
      "roles": {
        "cost_option": {"ranking_key": "..."},
        "quality_option": {"ranking_key": "..."},
        "balanced_default": {"ranking_key": "..."}
      },
      "candidates": []
    }
  ],
  "discount_calibration": {
    "status": "unknown",
    "sample_size": 20
  }
}
```

### `data/task_cost_evidence.json`

Benchmark and session evidence. Не смешивать units.

### `data/task_cost_coverage.json`

Список покрытых и uncovered candidates.

### `data/config_patch.json`

Только preview:

```json
{
  "status": "not_applied",
  "requires_confirmation": true,
  "profile": "agentic",
  "from": {
    "model": "...",
    "provider": "..."
  },
  "to": {
    "model": "...",
    "provider": "...",
    "variant": "..."
  },
  "yaml_diff": "...",
  "reason": "..."
}
```

Никакого автоматического изменения `config.yaml` в MVP-1.

### `changes.json`

Создаётся после decision surface и сравнивает не сырые fields, а outcome:

```json
{
  "schema_version": "1.0",
  "from": "2026-08-20",
  "to": "2026-08-21",
  "events": [
    {
      "type": "decision_changed",
      "profile": "agentic",
      "before": {"ranking_key": "...", "provider": "..."},
      "after": {"ranking_key": "...", "provider": "..."},
      "reason": "Новый candidate прошёл stable Pareto и изменил actionable default.",
      "confirmed": false
    },
    {
      "type": "discount_action_changed",
      "profile": "code",
      "reason": "Discount provider больше не является current actionable provider."
    }
  ],
  "status": "baseline | compared | comparison_skipped"
}
```

Raw `price_changed`, `provider_changed` и `uptime_crossing` допускаются как supporting details, но не должны вытеснять decision event.

---

## 10. UI and action

Верх страницы:

```text
Что выбрать для профиля
  1. balanced default
  2. cost option
  3. quality option
  4. почему
  5. ranking cost / 100 requests
  6. relevant quality score
  7. raw/stable Pareto status
  8. current provider / variant / discount
  9. YAML patch preview
```

Ниже:

```text
Модели без comparable Rankings evidence
Task-cost validation coverage
Что изменилось
```

График не обязателен для первой вертикали. Данные и frontier должны быть воспроизведены сначала; компактная таблица/cards достаточно подтверждают decision path. Если chart добавляется, он должен иметь те же controls:

- profile/category;
- price view;
- quality index;
- Show Pareto/raw vs stable.

---

## 11. Implementation order

### Slice 1 — reproduce Rankings surface

- HTTP client for frontend endpoint;
- fixture from live response;
- schema guard;
- normalized `rankings_surface.json`;
- task profile mapping;
- exact raw Pareto.

### Slice 2 — join catalog and variants

- `permaslug` to `canonical_slug` join;
- preserve `:free`/`:batch`;
- unmatched coverage list;
- no fabricated price for absent variants.

### Slice 3 — endpoint economics and discount audit

- endpoint/provider join;
- current effective/base price;
- discount/provider/uptime overlay;
- 20-family reflection calibration;
- decide `validated`, `inconsistent` or `unknown`.

### Slice 4 — stable Pareto and roles

- margins;
- floors;
- cost/quality/balanced roles;
- deterministic ordering;
- compare against existing PoC picks.

### Slice 5 — secondary evidence coverage

- `/api/v1/benchmarks` with `source=openrouter`;
- `/api/v1/datasets/session-cost`;
- `task_cost_evidence.json`;
- coverage classification.

### Slice 6 — YAML patch preview

- candidate → provider/variant action;
- diff generation;
- `requires_confirmation=true`;
- `not_applied`.

### Slice 7 — UI/report

- decision surface above legacy shortlist;
- explicit ranking mode and units;
- discount status;
- coverage block;
- fallback warning.

### Slice 8 — decision change detection

- compatible snapshot lineage;
- baseline/compared states;
- outcome-level `changes.json`;
- two-snapshot hysteresis for default change.

---

## 12. TDD and acceptance

Strict vertical TDD. No production code before a failing test.

Minimum tests:

1. frontend response normalization;
2. missing/invalid frontend fields fail loudly;
3. deterministic profile-to-quality mapping;
4. exact raw Pareto reproduction;
5. zero price handling;
6. deterministic stable Pareto with margins;
7. catalog family/variant join;
8. unmatched rankings candidates are not recommendations;
9. endpoint discount overlay does not mutate observed ranking cost;
10. discount calibration states;
11. `avg_cost_per_task` and session-cost remain separate units;
12. coverage artifact classifies all current families;
13. three recommendation roles are deterministic;
14. YAML patch preview is not applied;
15. baseline and same-day idempotence for decision artifacts;
16. decision hysteresis;
17. all existing PoC tests remain green.

Live acceptance:

- `rankings_surface.json` generated from live frontend endpoint;
- all five profiles have explicit metric/price contracts;
- raw Pareto output can be compared with current OpenRouter surface;
- `costPerRequest` is never printed as `avg_cost_per_task`;
- discount status is explicit (`validated`, `inconsistent`, `unknown`);
- current PoC picks and worthy uncovered families are visible in coverage;
- YAML patch is preview only;
- no secret appears in logs, artifacts or git diff;
- `python -m unittest discover -s tests -v` remains green;
- `git diff --check` is clean.

---

## 13. Risks and stop conditions

### Main risks

1. Frontend endpoint is not a stable public API contract.
2. `costPerRequest` semantics may change or be unavailable for some models.
3. Discount may already be reflected in the frontend aggregate; double correction would corrupt ranking.
4. `permaslug` and current catalog variants may not join one-to-one.
5. Quality indices embed reasoning effort labels; comparing defaults remains imperfect.
6. `avg_cost_per_task` and session-cost coverage is incomplete and benchmark/app-specific.
7. Raw Pareto can include cheap but unusable low-quality models; quality floor is mandatory.

### Stop conditions

- Do not publish a primary ranking if frontend schema fails validation.
- Do not treat missing `costPerRequest` as zero.
- Do not re-rank all models on token price while labelling the result Rankings-based.
- Do not multiply discount into `costPerRequest` until the reflection audit passes.
- Do not apply YAML patch automatically.
- Do not classify schema migration as market change.

---

## 14. Non-goals

- automatic config modification;
- Telegram;
- backend, database, accounts and multi-user;
- universal cost model for arbitrary user tasks;
- new benchmark provider;
- raw Data API mirror;
- reasoning token consumption experiment;
- real-time monitoring;
- replacing OpenRouter Rankings with an opaque global score.

---

## 15. Sources

[2] OpenRouter Data API documentation: https://openrouter.ai/docs/cookbook/administration/data-api
[3] OpenRouter GPQA benchmark response: https://openrouter.ai/api/v1/benchmarks?source=openrouter&benchmark_type=gpqa_diamond&max_results=100
[4] OpenRouter tau-bench benchmark response: https://openrouter.ai/api/v1/benchmarks?source=openrouter&benchmark_type=tau_bench_verified_airline&max_results=100
[5] OpenRouter session-cost response: https://openrouter.ai/api/v1/datasets/session-cost
[6] OpenRouter public Rankings page: https://openrouter.ai/rankings?benchmark=agentic#benchmarks
[7] OpenRouter frontend Rankings benchmark response: https://openrouter.ai/api/frontend/v1/rankings/benchmarks
