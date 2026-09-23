# LLM Discount Advisor — отчёт от 2026-09-23

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **454** строк каталога / **368** семейств; после scope gate прошло **124** строк / **81** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 1; raw Pareto: 1; stable Pareto: 1.
- balanced default: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.0892657023 / score 57.6
- cost option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.0892657023 / score 57.6
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.0892657023 / score 57.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 34; raw Pareto: 8; stable Pareto: 14.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $17.4788744727 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / StreamLake / $0.1106714901 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $17.4788744727 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 12; raw Pareto: 4; stable Pareto: 6.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $2.5449402503 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / DeepInfra / $0.2166307957 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $17.4788744727 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 1; raw Pareto: 1; stable Pareto: 1.
- balanced default: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.0892657023 / score 57.6
- cost option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.0892657023 / score 57.6
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.0892657023 / score 57.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 4; raw Pareto: 3; stable Pareto: 4.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.5037693351 / score 50.8
- cost option: `xiaomi/mimo-v2.6-pro-20260921` / DeepInfra / $0.4047968588 / score 46.3
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.5037693351 / score 50.8

### Secondary evidence coverage

Families total: 368; uncovered: 200;
`worthy_candidate`: 0; `likely_low_signal`: 200.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 2.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $8.0000/1M, intelligence 57.6. Почему: intelligence 57.6 при цене $8.000/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, coding 68.1. Почему: coding 68.1 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `DeepSeek: DeepSeek V4 Pro 0813` через StreamLake: $0.7480/1M, coding 68.8, скидка 62%. Почему: У этой же модели есть провайдер дешевле в 2.6 раза при uptime 99.83%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через StreamLake: $0.0792/1M, coding 69.1, скидка 88%. Почему: Скидка 88% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через DeepInfra: $0.1187/1M, coding 71.5, скидка 50%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, agentic 45.8. Почему: agentic 45.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.1 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, agentic 51.0. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через DeepInfra: $0.1187/1M, agentic 50.9, скидка 50%. Почему: Скидка 50% активна, но качество 50.9 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Darkbloom: $0.5250/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.525/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $5.4545/1M, intelligence 57.6. Почему: intelligence 57.6 при цене $5.455/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Xiaomi: MiMo-V2.6-Pro` через DeepInfra: $0.7612/1M, intelligence 46.3. Почему: intelligence 46.3 при цене $0.761/1M; от лидера по качеству отстаёт на 4.5 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Sol` через OpenAI: $4.0000/1M, intelligence 47.5. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.95%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 47.0, скидка 50%. Почему: Скидка 50% активна, но качество 47.0 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5` через Claude Platform on AWS: $20.0000/1M, intelligence 50.8. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
