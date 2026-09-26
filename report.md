# LLM Discount Advisor — отчёт от 2026-09-26

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **458** строк каталога / **374** семейств; после scope gate прошло **120** строк / **81** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 1; raw Pareto: 1; stable Pareto: 1.
- balanced default: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.7901245856 / score 57.6
- cost option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.7901245856 / score 57.6
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.7901245856 / score 57.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 33; raw Pareto: 6; stable Pareto: 16.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $17.4959443717 / score 81.6
- cost option: `z-ai/glm-5.3-flash-20260826` / InferenceNet / $0.1001396534 / score 71.5
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $17.4959443717 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 12; raw Pareto: 5; stable Pareto: 6.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.971295 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / InferenceNet / $0.1001396534 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $17.4959443717 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 1; raw Pareto: 1; stable Pareto: 1.
- balanced default: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.7901245856 / score 57.6
- cost option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.7901245856 / score 57.6
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $10.7901245856 / score 57.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 4; raw Pareto: 3; stable Pareto: 4.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $9.7674733391 / score 50.8
- cost option: `xiaomi/mimo-v2.6-pro-20260921` / GMICloud / $0.537384284 / score 46.3
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $9.7674733391 / score 50.8

### Secondary evidence coverage

Families total: 374; uncovered: 210;
`worthy_candidate`: 0; `likely_low_signal`: 210.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $8.0000/1M, intelligence 57.6. Почему: intelligence 57.6 при цене $8.000/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, coding 68.1. Почему: coding 68.1 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.3 Flash` через InferenceNet: $0.0688/1M, coding 71.5, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.3 раза при uptime 99.26%. Reasoning: `max`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через StreamLake: $0.0660/1M, coding 69.1, скидка 90%. Почему: Скидка 90% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, coding 71.4. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Qwen: Qwen3.8 27B (free)` через ModelRun: $0.0000/1M, agentic 45.8. Почему: agentic 45.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.1 п. Reasoning: `xhigh`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.3 Flash` через InferenceNet: $0.0688/1M, agentic 50.9, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.3 раза при uptime 99.26%. Reasoning: `max`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3` через Baidu: $0.5827/1M, agentic 53.1, скидка 73%. Почему: Скидка 73% активна, но качество 53.1 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Darkbloom: $0.5250/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.525/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $5.4545/1M, intelligence 57.6. Почему: intelligence 57.6 при цене $5.455/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Xiaomi: MiMo-V2.6-Pro` через GMICloud: $0.7612/1M, intelligence 46.3. Почему: intelligence 46.3 при цене $0.761/1M; от лидера по качеству отстаёт на 4.5 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Sol` через OpenAI: $4.0000/1M, intelligence 47.5. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 47.0, скидка 50%. Почему: Скидка 50% активна, но качество 47.0 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5` через Claude Platform on AWS: $20.0000/1M, intelligence 50.8. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
