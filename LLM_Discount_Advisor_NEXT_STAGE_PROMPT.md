# LLM Discount Advisor — Prompt for Revised MVP-1 Start

Скопируй этот файл целиком в новую сессию Hermes.

---

## Роль и цель

Продолжи проект `LLM Discount Advisor` после завершённого PoC. Работай по revised spec:

```text
C:\Users\volga\llm-discount-advisor\LLM_Discount_Advisor_MVP1_REVISED_SPEC.md
```

Главная задача revised MVP-1 — не старый change detection поверх token-price ranking. Сначала воспроизведи decision surface, которой автор уже пользуется вручную на OpenRouter Rankings:

```text
task profile
→ relevant quality index
→ Avg Price Per 100 Requests
→ raw Pareto
→ stable Pareto with margins
→ current provider / variant / discount overlay
→ recommendation
→ YAML patch preview
→ decision-level change detection
```

Не начинай с нуля и не пересобирай PoC gate без необходимости.

## Обязательный контекст: прочитать до любых изменений

Прочитай целиком:

1. `C:\Users\volga\llm-discount-advisor\LLM_Discount_Advisor_MVP1_REVISED_SPEC.md`
2. `C:\Users\volga\llm-discount-advisor\LLM_Discount_Advisor_Design_Spec.md`
3. `C:\Users\volga\llm-discount-advisor\LLM_Discount_PoC_Session_Summary.md`
4. `C:\Users\volga\llm-discount-advisor\README.md`
5. `C:\Users\volga\llm-discount-advisor\advisor\pipeline.py`
6. `C:\Users\volga\llm-discount-advisor\advisor\normalize.py`
7. `C:\Users\volga\llm-discount-advisor\advisor\recommend.py`
8. `C:\Users\volga\llm-discount-advisor\advisor\gate.py`
9. `C:\Users\volga\llm-discount-advisor\advisor\config.py`
10. `C:\Users\volga\llm-discount-advisor\advisor\report.py`
11. `C:\Users\volga\llm-discount-advisor\index.html`
12. `C:\Users\volga\llm-discount-advisor\data\latest.json`
13. все JSON-файлы в `C:\Users\volga\llm-discount-advisor\data\snapshots\`
14. `C:\Users\volga\llm-discount-advisor\.github\workflows\update.yml`
15. все тесты в `C:\Users\volga\llm-discount-advisor\tests\`

Также проверь живые источники:

```text
https://openrouter.ai/rankings?benchmark=agentic#benchmarks
https://openrouter.ai/api/frontend/v1/rankings/benchmarks
https://openrouter.ai/api/v1/models
https://openrouter.ai/api/v1/models/{id}/endpoints
https://openrouter.ai/api/v1/benchmarks?source=openrouter&benchmark_type=gpqa_diamond
https://openrouter.ai/api/v1/benchmarks?source=openrouter&benchmark_type=tau_bench_verified_airline
https://openrouter.ai/api/v1/datasets/session-cost
```

## Проверенный baseline

- Локальный путь: `C:\Users\volga\llm-discount-advisor`.
- GitHub: `https://github.com/volgarevmaxim-bit/llm-discount-advisor`.
- Pages: `https://volgarevmaxim-bit.github.io/llm-discount-advisor/`.
- PoC acceptance: full-vs-gated top-10 `code` = **10/10**, target = 9.
- Последний проверенный snapshot: 414 catalog rows, 343 families, 387 prefiltered rows, 316 prefiltered families, 108 gated variant rows, 76 gated families, 107 normalized rows.
- Existing tests: **16 tests, OK**.
- Нельзя откатывать variant-aware поведение `:free` / `:batch`.
- `canonical_slug` — family key; `id` / `variant_id` — selectable variant key.
- `avg_cost_per_task` и session-cost уже подтверждены живыми запросами, но не являются primary decision surface.
- Frontend Rankings endpoint живой и возвращает `aaData`, `costPerRequest`, `weightedInputPrices`, `daData`; его schema нужно валидировать, потому что это frontend surface, а не стабильный API reference contract.

## Что должно быть построено

### Primary decision surface

Для каждого profile:

- выбрать relevant quality metric:
  - `chat` → `intelligence`;
  - `code` → `coding`;
  - `agentic` → `agentic`;
  - `longdoc` → `intelligence`;
  - `bulk` → `intelligence` с текущим reasoning filter;
- использовать `costPerRequest` как `usd_per_100_requests`;
- построить raw Pareto, воспроизводимый по OpenRouter surface;
- построить stable Pareto с `price_margin=10%` и `quality_margin=2 points`;
- выдать `cost_option`, `quality_option`, `balanced_default`;
- присоединить family/variant/provider/discount/uptime data.

### Discount

Не делать автоматически:

```text
costPerRequest * (1 - discount)
```

Сначала проведи discount reflection audit минимум на 20 matched families:

- `costPerRequest`;
- `weightedInputPrices`;
- endpoint prompt/completion prices;
- current discount;
- provider and uptime.

Результат должен быть одним из:

```text
validated | inconsistent | unknown
```

До `validated` discount остаётся overlay/action signal, а не числовой корректор observed ranking cost.

### Secondary evidence

Подключить отдельно:

- `/api/v1/benchmarks?source=openrouter&benchmark_type=...`;
- `/api/v1/datasets/session-cost`.

Сделать:

```text
data/task_cost_evidence.json
data/task_cost_coverage.json
```

Coverage не является предварительным блокером. Сначала построить primary ranking, затем классифицировать uncovered families:

```text
worthy_candidate | needs_review | likely_low_signal
```

### Action

Создать только preview:

```text
data/config_patch.json
```

Условия:

```json
{
  "status": "not_applied",
  "requires_confirmation": true
}
```

Никакого автоматического изменения `config.yaml`.

### Change detection

Только после decision surface:

- сравнивать `decision_surface.json`, а не только сырые prices;
- показывать `decision_changed` и `discount_action_changed`;
- raw field events оставить supporting details;
- legacy snapshot schema migration не считать market change;
- default change подтверждать hysteresis правилом из spec.

## Порядок работы

### Сначала analysis-only checkpoint

До изменения project files покажи:

1. что уже есть и что не трогается;
2. живую schema frontend endpoint;
3. как ты воспроизведёшь raw Pareto;
4. identity join plan (`permaslug` / `canonical_slug` / variants);
5. discount reflection audit plan;
6. profile contracts и floors;
7. список файлов и артефактов;
8. TDD slices;
9. риски и stop conditions.

**Дождись явного `go` пользователя перед реализацией.**

Не изменяй файлы только потому, что spec уже написана.

### После `go`: strict vertical TDD

1. Напиши один failing test для frontend normalization.
2. Запусти его и покажи RED.
3. Реализуй минимум и покажи GREEN.
4. Запусти полный suite.
5. Перейди к raw Pareto.
6. Затем join с catalog/variants.
7. Затем endpoint discount overlay и calibration.
8. Затем task-cost evidence и coverage.
9. Затем stable Pareto и recommendation roles.
10. Затем YAML patch preview.
11. Затем UI/report.
12. Последним — decision-level change detection.

Production code нельзя писать до соответствующего failing test.

## Обязательные тесты

- frontend response normalization;
- invalid/missing frontend schema fails loudly;
- profile → quality metric mapping;
- exact raw Pareto deterministic;
- zero-price candidate handling;
- stable Pareto suppresses insignificant flicker;
- family/variant join;
- unmatched ranking candidate is not recommended;
- endpoint discount does not overwrite observed `costPerRequest`;
- discount calibration states `validated/inconsistent/unknown`;
- benchmark and session-cost units remain separate;
- all current families appear in coverage artifact;
- current PoC picks and worthy uncovered candidates are visible;
- deterministic `cost_option`, `quality_option`, `balanced_default`;
- YAML patch is `not_applied` and requires confirmation;
- baseline/no-previous decision snapshot;
- same-day rerun deterministic;
- hysteresis for decision change;
- all existing PoC tests remain green.

## Secrets

Ключи не просить в чате и не печатать.

Локально использовать существующий profile dotenv:

```bash
set -a && . "$HOME/.hermes/.env" && set +a
```

Показывать только наличие/длину ключа, не значение. В GitHub Actions секрет добавлять только если это входит в отдельное подтверждённое deployment step. `--no-key` должен оставаться рабочим для публичного degraded mode, но не должен молча выдавать normal Rankings decision surface.

## Live verification after implementation

Проверить:

1. live frontend endpoint и `data/rankings_surface.json`;
2. `data/decision_surface.json` для всех profiles;
3. raw/stable Pareto counts;
4. discount calibration result;
5. `data/task_cost_evidence.json` и coverage;
6. `data/config_patch.json`;
7. `shortlist.json`, `report.md`, `index.html`;
8. schema migration handling;
9. отсутствие секретов в logs/artifacts/git diff;
10. `python -m unittest discover -s tests -v`;
11. `git diff --check`.

После локальной проверки — live run, затем только по отдельному подтверждённому deployment scope commit/push/Pages verification.

Не заявляй, что H1 подтверждена, пока пользователь лично не записал действие в `NOTES.md`.

## Финальный отчёт сессии

Верни:

- изменённые файлы;
- source schema и live counts;
- пример `decision_surface.json`;
- raw vs stable Pareto results;
- discount calibration result;
- task-cost/session-cost coverage;
- кто остался uncovered и кто из них worthy;
- результаты RED/GREEN и полного suite;
- YAML patch preview и подтверждение, что он не применён;
- live verification output;
- commit/ref и Pages URL, только если реально сделаны и проверены;
- что осталось измерить на пользователе;
- честные блокеры.

Главное правило: сначала воспроизвести decision surface OpenRouter, затем добавить объяснимый discount/provider action. Не возвращаться к token-price-first ranking под новым названием.
