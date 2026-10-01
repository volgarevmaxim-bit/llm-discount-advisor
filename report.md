# LLM Discount Advisor — отчёт от 2026-10-01

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **462** строк каталога / **378** семейств; после scope gate прошло **119** строк / **80** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $4.5367206413 / score 56.0
- cost option: `anthropic/claude-sonnet-5.5-20260928` / Google / $4.5367206413 / score 56.0
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.9557450283 / score 57.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 33; raw Pareto: 7; stable Pareto: 14.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $27.6891917953 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / StreamLake / $0.0992242529 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $27.6891917953 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 12; raw Pareto: 5; stable Pareto: 6.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.5185488717 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / OpenInference / $0.245245959 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $27.6891917953 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $4.5367206413 / score 56.0
- cost option: `anthropic/claude-sonnet-5.5-20260928` / Google / $4.5367206413 / score 56.0
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.9557450283 / score 57.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 4; raw Pareto: 4; stable Pareto: 4.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $16.4368281103 / score 50.8
- cost option: `xiaomi/mimo-v2.6-pro-20260921` / GMICloud / $0.3947604229 / score 46.3
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $16.4368281103 / score 50.8

### Secondary evidence coverage

Families total: 378; uncovered: 210;
`worthy_candidate`: 0; `likely_low_signal`: 210.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $4.0000/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $4.000/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $8.0000/1M, intelligence 57.6. Почему: Преимущество не окупает смену: цена $8.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, coding 68.1. Почему: coding 68.1 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через Baidu: $0.2515/1M, coding 68.8, скидка 90%. Почему: У этой же модели есть провайдер дешевле в 7.7 раза при uptime 99.98%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через StreamLake: $0.0660/1M, coding 69.1, скидка 90%. Почему: Скидка 90% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через OpenInference: $0.0900/1M, coding 71.5, скидка 50%. Почему: Преимущество не окупает смену: цена $0.090/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, agentic 45.8. Почему: agentic 45.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.1 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.3 Flash` через OpenInference: $0.0900/1M, agentic 50.9, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.6 раза при uptime 99.86%. Reasoning: `max`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3` через Baidu: $0.2387/1M, agentic 53.1, скидка 89%. Почему: Скидка 89% активна, но качество 53.1 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Phala: $0.5813/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.581/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $2.7273/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $2.727/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $5.4545/1M, intelligence 57.6. Почему: Преимущество не окупает смену: цена $5.455/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Xiaomi: MiMo-V2.6-Pro` через GMICloud: $0.7232/1M, intelligence 46.3, скидка 5%. Почему: intelligence 46.3 при цене $0.723/1M; от лидера по качеству отстаёт на 4.5 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Sol` через OpenAI: $4.0000/1M, intelligence 47.5. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.97%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 47.0, скидка 50%. Почему: Скидка 50% активна, но качество 47.0 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5` через Claude Platform on AWS: $20.0000/1M, intelligence 50.8. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
