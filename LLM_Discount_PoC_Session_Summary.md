# LLM Discount Advisor — PoC Session Summary

**Дата закрытия PoC:** 2026-08-20
**Локальный путь:** `C:\Users\volga\llm-discount-advisor`
**GitHub:** https://github.com/volgarevmaxim-bit/llm-discount-advisor
**GitHub Pages:** https://volgarevmaxim-bit.github.io/llm-discount-advisor/

## 1. Что проверял PoC

PoC отвечает на один практический вопрос нулевого пользователя: какую модель и вариант провайдера поставить в Hermes `config.yaml`, если хочется сохранить достаточное качество и не переплачивать.

Нулевой пользователь — автор проекта. Фальсифицируемый критерий успеха H1: за 14 дней хотя бы один раз изменить модель в Hermes по рекомендации и не откатить изменение. Сам факт пользовательского изменения в этой сессии не заявляется: его нужно фиксировать вручную в `NOTES.md`.

## 2. Что реализовано

- Python-пайплайн только на stdlib, без фреймворков;
- один статический русский `index.html` без сборки, backend и БД;
- публичный OpenRouter `/api/v1/models`;
- prefilter для aliases, non-text и voice-моделей;
- scope gate G1–G4 и G6 до обхода endpoint-ов;
- `canonical_slug` как ключ семейства модели для gate/benchmark-логики;
- уникальный `id` как ключ endpoint/price-запроса, поэтому `:free` и `:batch` остаются отдельными вариантами;
- до 8 конкурентных endpoint-запросов;
- retry/backoff и логирование HTTP 429;
- цены только из `/api/v1/models/{id}/endpoints`;
- выбор лучшего надёжного провайдера с uptime-фильтром;
- discounted price, восстановление base price и overpay-сравнение;
- сохранение `pricing.overrides` и флаг `has_tiered_pricing`;
- reasoning `default_effort`, `mandatory`, supported efforts;
- исключение `mandatory=true` для профиля `bulk`;
- профили `chat`, `code`, `longdoc`, `bulk`;
- пять статусов рекомендаций;
- обязательная русская строка «Почему» в каждой карточке;
- `report.md`, `NOTES.md`, JSON-снапшоты и `data/gate_rejected.json`;
- ежедневный GitHub Actions workflow;
- GitHub Pages из `main` / root;
- unit-тесты и live full-vs-gated acceptance.

## 3. Тесты

Последняя локальная проверка:

```text
Ran 16 tests
OK
```

Дополнительно проверено:

```bash
python -m unittest discover -s tests -v
git diff --check
```

Проверки покрывают gate/reject reasons, G4 free, G6 participation, family/variant identity, discount/base price, provider selection, tiered pricing, reasoning bulk filter, explainable reasons и acceptance-дедупликацию по семействам.

## 4. Live-каталог и исправление расхождения 97 vs 77

Исторический аудит 19 августа был сделан на другом snapshot:

```text
/models rows:     415
prefiltered:      388
old gated rows:    97
normalized:        89
```

Текущий live-каталог 20 августа:

```text
/models rows:                 414
unique canonical_slug:        343
prefilter rows:               387
prefilter unique families:    316
gated variant rows:           108
gated unique families:         76
normalized rows:              107
endpoint errors in gated:       1
```

Число `77` из спеки нельзя использовать как постоянный target: это результат старого snapshot и другой единицы подсчёта. Старые `97` были количеством строк каталога. На текущих данных прежняя строковая логика давала 97 gate-строк, но только 69 уникальных семейств.

Причина — OpenRouter публикует несколько строк с одним `canonical_slug`, например базовый вариант, `:free` и `:batch`. Исправленная логика агрегирует benchmark-сигналы на уровне семейства, но получает цены каждого варианта отдельно по `id`.

Честная текущая контрольная цифра: **76 gated-семейств / 108 variant-строк**.

## 5. Live acceptance

Full и gated прогон использовали один и тот же кеш endpoint-данных. Сравнивались top-10 семейств профиля `code`.

Дата acceptance: `2026-08-20T08:28:32Z`.

```text
full normalized rows:         382
gated normalized rows:        108
full code eligible:             32
gated code eligible:            32
full/gated top-10 overlap:   10/10
target:                          9
passed:                       true
```

Все десять семейств top-10 совпали:

```text
z-ai/glm-5.2-20260616
deepseek/deepseek-v4-flash-20260731
openai/gpt-5.6-luna-20260709
google/gemini-3.7-flash-20260813
xiaomi/mimo-v2.5-pro-20260422
google/gemini-3.6-flash-20260721
qwen/qwen3.8-27b-20260814
moonshotai/kimi-k2.6-20260420
moonshotai/kimi-k2.7-code-20260612
google/gemini-3.5-flash-20260519
```

Это live-результат, не синтетическая фикстура.

## 6. Деплой

Создан публичный репозиторий:

```text
https://github.com/volgarevmaxim-bit/llm-discount-advisor
```

Первый локальный commit:

```text
21354af feat: build LLM Discount Advisor PoC
```

После Actions remote `main` получил artifact commit; последний проверенный remote ref:

```text
82289af1c760bdc22a5f04dce95e6089b6490707 refs/heads/main
```

GitHub Pages настроен из `main` / root:

```text
https://volgarevmaxim-bit.github.io/llm-discount-advisor/
```

Финально проверено:

- Pages API: `built`;
- Pages source: `main /`;
- `index.html`: HTTP 200;
- `shortlist.json`: HTTP 200;
- `data/latest.json`: HTTP 200;
- `report.md`: HTTP 200;
- remote `main` существует;
- локальное рабочее дерево чистое;
- токен удалён из Git remote URL.

## 7. Actions

Ручной запуск ежедневного workflow:

```text
Workflow: Daily OpenRouter snapshot
Run: 32353701879
Status: completed
Conclusion: success
```

Последний Pages deployment:

```text
Run: 32353718458
Status: completed
Conclusion: success
```

После Actions live-артефакты содержали:

```text
generated_at: 2026-08-20T09:24:24Z
normalized models: 107
gated variant rows: 108
gated families: 76
endpoint errors: 1
```

## 8. Главные ограничения, сознательно оставленные в PoC

Не реализованы графики, Telegram, change detection, исторические дельты, alerts, watchlists, personalization, Data API с ключом, поиск, фильтры, аккаунты, backend, БД и автоматическое изменение Hermes-конфига.

`blended_price` остаётся прокси с фиксированными ratio: `3:1` для chat/code, `10:1` для longdoc, `1:3` для bulk. Универсальная стоимость задачи не вычисляется.

Latency и throughput не используются. Reasoning effort явно показывается, но сравнение разных default effort пока не нормализовано экспериментально.

Один gated вариант имеет unusable endpoints и записывается в reject-артефакт; пайплайн не публикует его как рабочую рекомендацию.

## 9. Артефакты

- `README.md` — описание, аудит, acceptance и статус деплоя;
- `LLM_Discount_Advisor_Design_Spec.md` — исходная design spec v1.3;
- `LLM_Discount_PoC_Session_Summary.md` — этот handoff;
- `LLM_Discount_Advisor_NEXT_STAGE_PROMPT.md` — промт старта MVP-1;
- `advisor/` — код пайплайна;
- `tests/` — тесты;
- `data/snapshots/` — append-only snapshots;
- `data/latest.json` — последний нормализованный snapshot;
- `data/gate_rejected.json` — модели/варианты, отвергнутые gate или endpoint-нормализацией;
- `shortlist.json` — данные для HTML;
- `report.md` — русский текстовый отчёт;
- `index.html` — статический UI;
- `.github/workflows/update.yml` — daily workflow;
- `NOTES.md` — ручной журнал пользовательской валидации.

## 10. Команды продолжения

```bash
cd /c/Users/volga/llm-discount-advisor
python -m unittest discover -s tests -v
python -m advisor.pipeline --no-key
python -m http.server 8000
```

Проверка удалённого проекта:

```bash
git remote -v
git status --short --branch
git ls-remote origin refs/heads/main
```

## 11. Следующий этап

PoC закрыт. Следующий этап по разделу 14.2 спеки — **MVP-1 change detection**:

- `changes.json`;
- блок «Что изменилось» выше shortlist;
- сравнение соседних нормализованных snapshots;
- события изменения цены, discount, best provider, появления/исчезновения варианта и model family;
- dominance with margins;
- hysteresis против дрожания рекомендаций;
- `pareto_rank` как аккуратный дополнительный сигнал;
- первые две недели наблюдений H1/H2/H3 на себе.

Стартовать нужно с промта в `LLM_Discount_Advisor_NEXT_STAGE_PROMPT.md`. Код не начинать до чтения спеки и показа плана.
