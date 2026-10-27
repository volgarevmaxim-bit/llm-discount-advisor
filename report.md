# LLM Discount Advisor — отчёт от 2026-10-27

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **463** строк каталога / **381** семейств; после scope gate прошло **131** строк / **87** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 3; raw Pareto: 3; stable Pareto: 3.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $5.2621266958 / score 56.0
- cost option: `moonshotai/kimi-k3.1-pro-20261023` / Moonshot AI / $4.8270946779 / score 55.1
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.1743793007 / score 57.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 34; raw Pareto: 5; stable Pareto: 14.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $25.9868091167 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / Relace / $0.0957023555 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $25.9868091167 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 14; raw Pareto: 6; stable Pareto: 6.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.6632339583 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / Relace / $0.1563812201 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $25.9868091167 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 3; raw Pareto: 3; stable Pareto: 3.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $5.2621266958 / score 56.0
- cost option: `moonshotai/kimi-k3.1-pro-20261023` / Moonshot AI / $4.8270946779 / score 55.1
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.1743793007 / score 57.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 6; raw Pareto: 3; stable Pareto: 5.
- balanced default: `moonshotai/kimi-k3.1-pro-20261023` / Moonshot AI / $4.8270946779 / score 55.1
- cost option: `xiaomi/mimo-v2.6-pro-20260921` / GMICloud / $0.4237763777 / score 46.3
- quality option: `moonshotai/kimi-k3.1-pro-20261023` / Moonshot AI / $4.8270946779 / score 55.1

### Secondary evidence coverage

Families total: 381; uncovered: 148;
`worthy_candidate`: 0; `likely_low_signal`: 148.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $4.0000/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $4.000/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `MoonshotAI: Kimi K3.1 Pro` через Moonshot AI: $4.0000/1M, intelligence 55.1. Почему: Преимущество не окупает смену: цена $4.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, можно отключить/не указан.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0445/1M, coding 71.5, скидка 50%. Почему: coding 71.5 при цене $0.044/1M; от лидера по качеству отстаёт на 10.1 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через DeepInfra: $0.6975/1M, coding 68.8, скидка 56%. Почему: У этой же модели есть провайдер дешевле в 2.5 раза при uptime 100.00%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через Relace: $0.0748/1M, coding 69.1, скидка 70%. Почему: Скидка 70% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Tenstorrent: $0.1700/1M, coding 68.1, скидка 25%. Почему: Преимущество не окупает смену: цена $0.170/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0445/1M, agentic 50.9, скидка 50%. Почему: agentic 50.9 при цене $0.044/1M; от лидера по качеству отстаёт на 7.0 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, agentic 50.2. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.55%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash Vision Exp` через DeepInfra: $0.3234/1M, agentic 47.5, скидка 51%. Почему: Скидка 51% активна, но качество 47.5 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Tenstorrent: $0.1700/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.170/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $2.7273/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $2.727/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `MoonshotAI: Kimi K3.1 Pro` через Moonshot AI: $2.7273/1M, intelligence 55.1. Почему: Преимущество не окупает смену: цена $2.727/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, можно отключить/не указан.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Xiaomi: MiMo-V2.6-Pro` через GMICloud: $0.6471/1M, intelligence 46.3, скидка 15%. Почему: intelligence 46.3 при цене $0.647/1M; от лидера по качеству отстаёт на 8.8 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6.1 Terra` через OpenAI: $2.0000/1M, intelligence 48.1. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-6 Sol` через OpenAI: $4.0000/1M, intelligence 47.6. Почему: Преимущество не окупает смену: цена $4.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
