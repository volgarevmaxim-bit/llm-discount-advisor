# LLM Discount Advisor — отчёт от 2026-09-05

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **431** строк каталога / **348** семейств; после scope gate прошло **119** строк / **74** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 1; raw Pareto: 1; stable Pareto: 1.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 56.8
- cost option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 56.8
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 56.8

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 33; raw Pareto: 7; stable Pareto: 13.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / Baidu / $0.0957187179 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 11; raw Pareto: 4; stable Pareto: 5.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $9.3918747905 / score 56.4
- cost option: `z-ai/glm-5.3-flash-20260826` / GMICloud / $0.1744391929 / score 51.5
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 58.2

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 1; raw Pareto: 1; stable Pareto: 1.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 56.8
- cost option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 56.8
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.3737585582 / score 56.8

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 5; raw Pareto: 3; stable Pareto: 5.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $9.3918747905 / score 54.1
- cost option: `openai/gpt-5.6-terra-20260709` / OpenAI / $2.2534309614 / score 46.8
- quality option: `anthropic/claude-opus-5-20260723` / Azure / $9.3918747905 / score 54.1

### Secondary evidence coverage

Families total: 348; uncovered: 186;
`worthy_candidate`: 0; `likely_low_signal`: 186.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 1.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Fable 5.1` через Azure: $20.0000/1M, intelligence 56.8. Почему: intelligence 56.8 при цене $20.000/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, coding 68.8. Почему: coding 68.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.8 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через StreamLake: $0.5268/1M, coding 68.8, скидка 76%. Почему: У этой же модели есть провайдер дешевле в 2.8 раза при uptime 99.86%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через Baidu: $0.0625/1M, coding 69.1, скидка 80%. Почему: Скидка 80% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, coding 71.5, скидка 67%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, agentic 51.5, скидка 67%. Почему: agentic 51.5 при цене $0.119/1M; от лидера по качеству отстаёт на 6.7 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, agentic 51.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.98%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $2.0000/1M, agentic 50.7, скидка 50%. Почему: Скидка 50% активна, но качество 50.7 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Parasail: $0.7300/1M, agentic 46.8, скидка 10%. Почему: Преимущество не окупает смену: цена $0.730/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Fable 5.1` через Azure: $13.6364/1M, intelligence 56.8. Почему: intelligence 56.8 при цене $13.636/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 51.3, скидка 50%. Почему: intelligence 51.3 при цене $4.000/1M; от лидера по качеству отстаёт на 2.8 п. Reasoning: `medium`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Terra` через OpenAI: $4.7500/1M, intelligence 46.8. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Sonnet 5` через Claude Platform on AWS: $8.0000/1M, intelligence 45.1. Почему: Преимущество не окупает смену: цена $8.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
