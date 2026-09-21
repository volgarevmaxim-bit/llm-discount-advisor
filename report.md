# LLM Discount Advisor — отчёт от 2026-09-21

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **446** строк каталога / **359** семейств; после scope gate прошло **120** строк / **77** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 0; raw Pareto: 0; stable Pareto: 0.
- balanced default: нет сравнимого кандидата
- cost option: нет сравнимого кандидата
- quality option: нет сравнимого кандидата

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 34; raw Pareto: 8; stable Pareto: 17.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $25.090895492 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / Relace / $0.070683034 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $25.090895492 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 12; raw Pareto: 6; stable Pareto: 7.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $4.2269640781 / score 56.0
- cost option: `qwen/qwen3.8-27b-20260814` / Darkbloom / $0.467275309 / score 45.8
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $25.090895492 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 0; raw Pareto: 0; stable Pareto: 0.
- balanced default: нет сравнимого кандидата
- cost option: нет сравнимого кандидата
- quality option: нет сравнимого кандидата

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $13.5325944761 / score 50.8
- cost option: `openai/gpt-5.6-sol-20260709` / OpenAI / $5.622848367 / score 47.0
- quality option: `anthropic/claude-opus-5-20260723` / Azure / $13.5325944761 / score 50.8

### Secondary evidence coverage

Families total: 359; uncovered: 193;
`worthy_candidate`: 0; `likely_low_signal`: 193.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- Недостаточно кандидатов с объяснимыми данными.

### Код (`code`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, coding 68.1. Почему: coding 68.1 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, coding 76.9. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через Relace: $0.0700/1M, coding 69.1, скидка 88%. Почему: Скидка 88% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, coding 71.5, скидка 50%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, agentic 45.8. Почему: agentic 45.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.1 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, agentic 51.0. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, agentic 50.9, скидка 50%. Почему: Скидка 50% активна, но качество 50.9 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Darkbloom: $0.5250/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.525/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- Недостаточно кандидатов с объяснимыми данными.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `OpenAI: GPT-5.6 Sol` через OpenAI: $8.0000/1M, intelligence 47.0, скидка 50%. Почему: intelligence 47.0 при цене $8.000/1M; от лидера по качеству отстаёт на 3.8 п. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5` через Azure: $20.0000/1M, intelligence 50.8. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
