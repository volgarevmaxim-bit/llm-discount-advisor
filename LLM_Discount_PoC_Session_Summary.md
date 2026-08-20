Локальная версия PoC реализована. После продолжения выполнены live acceptance и исправлена идентичность model family/variant; GitHub-деплой ещё не начинался.

### Что сделано

Сохранён план реализации:

`C:\Users\volga\.hermes\plans\2026-08-20_002900-llm-discount-advisor-poc.md`

Создан локальный репозиторий:

`C:\Users\volga\llm-discount-advisor`

Реализованы:

- Python-пайплайн без сторонних фреймворков;
- scope gate до обхода endpoint-ов;
- ключ сопоставления `canonical_slug`;
- `canonical_slug` используется как family key, а уникальный `id` — как endpoint/price key для вариантов `:free` и `:batch`;
- G1–G4 и G6;
- запросы `/models/{id}/endpoints`;
- конкурентность 8;
- retry/backoff и логирование 429;
- выбор лучшего надёжного провайдера;
- `pricing.discount` и восстановление базовой цены;
- флаг `has_tiered_pricing`;
- reasoning `default_effort` / `mandatory`;
- дисквалификация `mandatory=true` для `bulk`;
- четыре профиля: `chat`, `code`, `longdoc`, `bulk`;
- пять статусов рекомендаций;
- обязательная строка «Почему»;
- русский `index.html`;
- `report.md`;
- `NOTES.md`;
- GitHub Actions с ежедневным cron;
- unit-тесты.

### Проверка тестами

Локально прошло:

```text
Ran 16 tests
OK
```

Проверены:

- gate и причины reject;
- G4 free;
- G6 participation;
- `canonical_slug`;
- discount/base price;
- provider selection;
- tiered pricing;
- bulk reasoning filter;
- наличие объяснимой причины;
- синтетический acceptance-прогон.

Синтетический acceptance-прогон дал:

```text
full top-10: 10
gated top-10: 10
overlap: 10
target: 9
passed: true
```

Это тестовый результат на фикстуре, не результат live-каталога.

### Live-прогон OpenRouter

Предыдущий live-прогон публичного OpenRouter API от 19 августа дал:

```text
models=415
prefiltered=388
gated=97
rejected=318
```

Сгенерированы:

- `data/snapshots/2026-08-19.json`
- `data/latest.json`
- `data/gate_rejected.json`
- `shortlist.json`
- `report.md`

В live-прогоне:

```text
scope gate: 97 моделей
нормализовано: 89
endpoint errors: 8
```

Это был важный промежуточный результат: прежняя реализация на фактических данных давала **97**, а не ожидаемые в спеке 77. Число нельзя было подменять на 77. Ниже зафиксирован разбор расхождения и выполнен live acceptance-прогон full-vs-gated по одному кешу endpoint-данных.

### Продолжение PoC: live acceptance и исправление gate

На текущем каталоге OpenRouter от 20 августа получено:

```text
/models rows:                 414
unique canonical_slug:        343
prefilter rows:               387
prefilter unique families:    316
gated rows:                   108
gated unique families:         76
normalized rows:              107
endpoint errors in gated:       1
```

Причина расхождения `97` vs `77` установлена. `97` — это прежний подсчёт строк `/models`, в котором варианты с одинаковым `canonical_slug` (`:free`/`:batch`) выглядели как отдельные модели; на текущем каталоге это 69 уникальных семейств. `77` — число из исторического аудита на другом snapshot и невалидный target для сегодняшнего каталога. В текущей реализации gate агрегирует benchmark-сигналы на уровне семейства, но сохраняет все variant rows; endpoint-запросы идут по `id`.

Live acceptance выполнен на одном и том же кеше endpoint-данных:

```text
full normalized rows:         382
gated normalized rows:        108
full code eligible:            32
gated code eligible:           32
full/gated top-10 overlap:   10/10
target:                         9
passed:                      true
```

Полные и gated top-10 совпали по всем десяти `canonical_slug`-семействам. Это фактический результат live API, не синтетическая фикстура.

На странице сейчас по 4 карточки для каждого профиля:

- `chat`
- `code`
- `longdoc`
- `bulk`

### Что не завершено

Не выполнены:

1. создание публичного GitHub-репозитория;
2. commit/push в `main`;
3. настройка GitHub Pages;
4. запуск и проверка GitHub Actions;
5. проверка live URL.

Причина блокировки GitHub:

- `gh` CLI отсутствует;
- `GITHUB_TOKEN` в dotenv нет;
- SSH-ключ есть, но первое подключение завершилось `Host key verification failed`.

Поэтому я не заявляю, что репозиторий опубликован или сайт работает live.

Локальная реализация находится здесь:

```text
C:\Users\volga\llm-discount-advisor
```

Открыть локально можно командой:

```bash
cd /c/Users/volga/llm-discount-advisor
python -m http.server 8000
```

Технический вопрос о расхождении `97` vs `77` закрыт: это смешение snapshot-дат и row-count с family-count, усиленное вариантами `:free`/`:batch`. Перед публикацией остаётся только GitHub-аутентификация, push, Pages и проверка live-артефактов.