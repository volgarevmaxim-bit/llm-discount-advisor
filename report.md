# LLM Discount Advisor — отчёт от 2026-09-20

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
Candidates: 34; raw Pareto: 7; stable Pareto: 16.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.855399164 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / Relace / $0.074589737 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.855399164 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 12; raw Pareto: 4; stable Pareto: 6.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.3521405608 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / GMICloud / $0.1592635872 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.855399164 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 0; raw Pareto: 0; stable Pareto: 0.
- balanced default: нет сравнимого кандидата
- cost option: нет сравнимого кандидата
- quality option: нет сравнимого кандидата

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $15.5527838602 / score 50.8
- cost option: `openai/gpt-5.6-sol-20260709` / OpenAI / $5.6191987267 / score 47.0
- quality option: `anthropic/claude-opus-5-20260723` / Azure / $15.5527838602 / score 50.8

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
- **Та же модель, но дешевле провайдер** — `MoonshotAI: Kimi K2.6` через Baidu: $0.6747/1M, coding 61.8, скидка 61%. Почему: У этой же модели есть провайдер дешевле в 2.5 раза при uptime 99.97%. Reasoning: `не указан`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через Relace: $0.0500/1M, coding 69.1, скидка 90%. Почему: Скидка 90% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, coding 71.5, скидка 50%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, agentic 45.8. Почему: agentic 45.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.1 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Qwen: Qwen3.8 27B` через Darkbloom: $0.5250/1M, agentic 45.8, скидка 25%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.08%. Reasoning: `xhigh`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, agentic 50.9, скидка 50%. Почему: Скидка 50% активна, но качество 50.9 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через Baidu: $1.2965/1M, agentic 53.1, скидка 40%. Почему: Преимущество не окупает смену: цена $1.296/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Длинные документы (`longdoc`)

- Недостаточно кандидатов с объяснимыми данными.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 47.0, скидка 50%. Почему: intelligence 47.0 при цене $4.000/1M; от лидера по качеству отстаёт на 3.8 п. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5` через Azure: $20.0000/1M, intelligence 50.8. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
