# LLM Discount Advisor — Revised MVP-1 Session Summary

**Дата закрытия этапа:** 20 августа 2026
**Локальный путь:** `C:\Users\volga\llm-discount-advisor`
**GitHub:** https://github.com/volgarevmaxim-bit/llm-discount-advisor
**GitHub Pages:** https://volgarevmaxim-bit.github.io/llm-discount-advisor/

Этот документ — handoff по revised MVP-1. Исторический PoC handoff сохранён отдельно в `LLM_Discount_PoC_Session_Summary.md`.

## 1. Цель этапа

Перестроить продукт вокруг decision surface, которой автор пользуется вручную на OpenRouter Rankings:

```text
task profile
→ relevant quality index
→ Avg Price Per 100 Requests
→ raw Pareto
→ stable Pareto
→ provider / variant / discount overlay
→ recommendation
→ YAML patch preview
→ decision-level change detection
```

`avg_cost_per_task` и session-cost не смешиваются с primary ranking. Они публикуются как отдельный validation/evidence layer.

## 2. Что реализовано

### Primary Rankings surface

Добавлены:

- `advisor/rankings.py`;
- schema guard для `https://openrouter.ai/api/frontend/v1/rankings/benchmarks`;
- нормализация `aaData.intelligence`, `aaData.coding`, `aaData.agentic`;
- сохранение `permaslug` как `ranking_key`;
- `costPerRequest` как observed `usd_per_100_requests`;
- `weightedInputPrices` как отдельное diagnostic field;
- explicit raw Pareto;
- stable Pareto с margins:
  - price margin: 10%;
  - quality margin: 2 points.

### Profile contracts

В `advisor/config.py` теперь пять явных профилей:

| Profile | Quality metric | Floor |
|---|---|---:|
| `chat` | `intelligence` | 55 |
| `code` | `coding` | 60 |
| `agentic` | `agentic` | 45 |
| `longdoc` | `intelligence` | 55 |
| `bulk` | `intelligence` | 45 |

Для `code` и `agentic` сохраняется требование tool support. Для `bulk` сохраняется исключение моделей с mandatory reasoning.

### Recommendations

`advisor/decision.py` публикует три детерминированные роли:

- `cost_option`;
- `quality_option`;
- `balanced_default`.

Unmatched и unpriced candidates не попадают в comparable recommendation set.

### Identity joins

Сохранены разные роли ключей:

```text
canonical_slug — family identity
id / variant_id — selectable endpoint variant
permaslug — Rankings identity
```

`permaslug` не подменяется heuristic slug без фиксации причины. Суффиксы `:free` и `:batch` сохраняются в variant identity.

### Discount/provider overlay

`advisor/economics.py`:

- сохраняет observed ranking cost отдельно;
- сохраняет endpoint effective/base prices;
- сохраняет provider, uptime и discount;
- не делает `costPerRequest * (1 - discount)`;
- публикует scenario-only block до прохождения audit gate.

Последний live audit:

```text
matched observations: 20
within tolerance:      1
acceptance threshold: 16 / 20
status:                inconsistent
```

Следствие: discount остаётся overlay/action signal и не меняет primary ranking cost.

### Secondary evidence

`advisor/evidence.py` и `advisor/openrouter.py` подключают:

- `/api/v1/benchmarks?source=openrouter&benchmark_type=gpqa_diamond`;
- `/api/v1/benchmarks?source=openrouter&benchmark_type=tau_bench_verified_airline`;
- `/api/v1/datasets/session-cost`.

Последний authenticated artifact содержит:

```text
benchmark rows: 200
session-cost rows: 100
```

В evidence сохраняются source metadata, `as_of`, `window_days`, scope и attribution.

### Full-catalog coverage

Coverage строится по всем catalog families из `/models`, а не только по моделям, для которых был endpoint response.

Последний artifact:

```text
families_total:              345
rankings_surface_families:   140
benchmark_cost_families:     106
session_cost_families:        34
union_secondary_covered:     113
uncovered:                   183
worthy_uncovered:              0
likely_low_signal_uncovered: 183
```

Это coverage artifact, а не причина добавить uncovered candidates в comparable Pareto без Rankings price/quality evidence.

### Action preview

`advisor/action.py` и `data/config_patch.json`:

```json
{
  "status": "not_applied",
  "requires_confirmation": true,
  "applied": false
}
```

Hermes config автоматически не изменялся.

### Change detection and lineage

`advisor/changes.py` и pipeline поддерживают:

- `baseline`;
- `compared`;
- `comparison_skipped` при несовместимой schema;
- `decision_changed`;
- `discount_action_changed`;
- same-day idempotence;
- snapshot lineage в `data/decision_snapshots/YYYY-MM-DD.json`;
- hysteresis на двух совместимых snapshots.

Текущий `changes.json`:

```text
status: baseline
events: 0
```

Это ожидаемо: текущий день — первый совместимый decision baseline. Same-day rerun не считается новым market snapshot.

## 3. Последний live primary result

Источник: authenticated OpenRouter run, 20 августа 2026.

```text
/models rows:       416
prefiltered rows:   389
gated rows:         108
gated families:      76
endpoint errors:      1
```

Frontend Rankings:

```text
aaData.intelligence: 114 rows
aaData.coding:      140 rows
aaData.agentic:     115 rows
costPerRequest:     179 keys
```

Profile results:

| Profile | Candidates | Raw Pareto | Stable Pareto | Balanced default |
|---|---:|---:|---:|---|
| `chat` | 16 | 7 | 12 | `anthropic/claude-opus-5-20260723` |
| `code` | 31 | 4 | 9 | `openai/gpt-5.6-terra-20260709` |
| `agentic` | 21 | 6 | 11 | `z-ai/glm-5.3-20260816` |
| `longdoc` | 16 | 7 | 12 | `anthropic/claude-opus-5-20260723` |
| `bulk` | 19 | 6 | 11 | `anthropic/claude-opus-5-20260723` |

Числа зависят от живого OpenRouter snapshot и не являются постоянным контрактом.

## 4. Артефакты

### Primary artifacts

- `data/rankings_surface.json` — normalized frontend Rankings surface;
- `data/decision_surface.json` — profiles, candidates, Pareto, roles и discount calibration;
- `data/task_cost_evidence.json` — benchmark/session evidence без смешения units;
- `data/task_cost_coverage.json` — полный coverage по catalog families;
- `data/config_patch.json` — reviewable YAML patch preview;
- `changes.json` — decision-level changes;
- `data/decision_snapshots/2026-08-20.json` — baseline lineage snapshot.

### Legacy-compatible artifacts

- `data/latest.json`;
- `data/snapshots/2026-08-20.json`;
- `data/gate_rejected.json`;
- `shortlist.json`;
- `report.md`;
- `index.html`.

`index.html` теперь ставит revised decision surface выше legacy shortlist.

## 5. Tests and quality gates

Последняя локальная проверка:

```text
Ran 44 tests
OK
```

Покрыты:

- Rankings normalization и schema failure;
- raw/stable Pareto;
- profile contracts;
- family/variant joins;
- unmatched/unpriced exclusion;
- discount overlay/calibration states;
- benchmark/session unit separation;
- full-catalog coverage;
- YAML patch preview;
- baseline, schema migration, same-day idempotence и hysteresis;
- artifact writer;
- report/UI contract;
- workflow contract;
- legacy PoC tests.

Дополнительно:

```text
git diff --check: clean
secret value scan: clean
```

В репозиторий не включён локальный `.hermes/`.

## 6. Git and deployment

Основная история:

```text
e1e4e22 chore: daily OpenRouter MVP-1 snapshot
3c9353d chore: daily OpenRouter MVP-1 snapshot
46342ab merge: preserve revised MVP-1 after daily artifact commit
2356f2c feat: implement revised MVP-1 Rankings decision surface
82289af chore: daily OpenRouter snapshot
2356f2c feat: implement revised MVP-1 Rankings decision surface
21354af feat: build LLM Discount Advisor PoC
```

Текущие refs:

```text
HEAD:        e1e4e22
origin/main: e1e4e22
```

Remote URL очищен от token credentials.

### GitHub Actions

Repository secret `OPENROUTER_API_KEY` добавлен через GitHub Actions Secrets API из локального dotenv. Значение не публиковалось в чате, логах, artifacts или git diff.

Успешный authenticated workflow:

```text
Run:        32379166143
Status:     completed
Conclusion: success
```

Проверенные steps:

```text
Run daily pipeline:       success
Validate generated artifacts: success
Commit daily artifacts:   success
```

### GitHub Pages

Pages source:

```text
branch: main
path:   /
status: built
```

Последний Pages build для authenticated artifact commit:

```text
Pages build: 1163682931
Commit:      e1e4e22
Status:      built
```

Live URL:

```text
https://volgarevmaxim-bit.github.io/llm-discount-advisor/
```

Фактически проверены через HTTPS с cache-busting:

- `index.html` — HTTP 200, revised UI markers присутствуют;
- `data/decision_surface.json` — HTTP 200, пять профилей, `rankings_cost_per_request`, calibration `inconsistent`;
- `data/rankings_surface.json` — HTTP 200;
- `data/task_cost_evidence.json` — HTTP 200, `200/100` rows;
- `data/task_cost_coverage.json` — HTTP 200, `345` families;
- `data/config_patch.json` — HTTP 200, preview-only;
- `changes.json` — HTTP 200, baseline;
- `report.md` — HTTP 200.

## 7. Что осталось измерить

### На пользователе

Главный незакрытый вопрос — H1:

> За 14 дней автор хотя бы один раз изменил Hermes config по рекомендации и не откатил изменение.

Факт нужно записать вручную в `NOTES.md`. Нельзя объявлять H1 подтверждённой по одному live deployment.

Нужно также измерить:

- был ли `balanced_default` понятнее cost/quality alternatives;
- вызвал ли `decision_changed` реальное действие;
- оказался ли `discount_action_changed` полезнее смены model family;
- достаточно ли сайта или нужен push-канал;
- не создаёт ли stable Pareto слишком много альтернатив.

### На данных

- дождаться второго совместимого дневного snapshot;
- проверить реальный `changes.json` с decision event;
- наблюдать устойчивость provider/variant join;
- пересмотреть классификацию 183 uncovered families после нескольких snapshots;
- отдельно оценить, нужен ли `data-extraction` profile.

## 8. Честные ограничения

- Frontend Rankings endpoint — observed frontend surface, а не гарантированный public API contract; schema guard обязателен.
- Discount calibration не прошёл gate `16/20`; числовая discount correction запрещена.
- `costPerRequest` — operational proxy за 100 requests, не universal arbitrary-task cost.
- Benchmark `avg_cost_per_task` и session-cost имеют named scopes и разные units.
- Reasoning effort может менять фактический расход, но MVP-1 не измеряет multiplier при разных effort levels.
- Current `changes.json` — baseline, не доказательство отсутствия market changes.
- `config.yaml` не меняется автоматически.
- Один gated variant имеет unusable endpoints и остаётся в reject artifact.
- Никаких claims о подтверждённой пользовательской ценности без записи в `NOTES.md`.

## 9. Команды продолжения

```bash
cd /c/Users/volga/llm-discount-advisor

# Tests
python -m unittest discover -s tests -v

# Public degraded mode
python -m advisor.pipeline --no-key

# Authenticated local mode; value is loaded, never printed
set -a && . "$HOME/.hermes/.env" && set +a
python -m advisor.pipeline

# Repository status
git status --short --branch
git ls-remote origin refs/heads/main

# Local static preview
python -m http.server 8000
```

## 10. Recommended next session

Не начинать новую реализацию. Сначала:

1. прочитать этот summary;
2. прочитать `LLM_Discount_Advisor_MVP1_REVISED_SPEC.md` только при изменении scope;
3. проверить `NOTES.md` и записать пользовательское действие, если оно было;
4. после второго compatible snapshot проверить `changes.json` и hysteresis;
5. не добавлять Telegram, backend или automatic config apply до подтверждённого пользовательского сигнала.

Текущий статус: **revised MVP-1 implemented, authenticated, tested, deployed and live-verified; H1 user validation pending.**
