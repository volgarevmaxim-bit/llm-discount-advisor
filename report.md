# LLM Discount Advisor — отчёт от 2026-10-20

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **470** строк каталога / **381** семейств; после scope gate прошло **130** строк / **87** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $3.6290915259 / score 56.0
- cost option: `anthropic/claude-sonnet-5.5-20260928` / Google / $3.6290915259 / score 56.0
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.1945096043 / score 57.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 34; raw Pareto: 7; stable Pareto: 15.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $24.141409028 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.0815451841 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $24.141409028 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 14; raw Pareto: 6; stable Pareto: 7.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.2687100266 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / OpenInference / $0.0875201536 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $24.141409028 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $3.6290915259 / score 56.0
- cost option: `anthropic/claude-sonnet-5.5-20260928` / Google / $3.6290915259 / score 56.0
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.1945096043 / score 57.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 4; raw Pareto: 4; stable Pareto: 4.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $14.5678518978 / score 50.8
- cost option: `xiaomi/mimo-v2.6-pro-20260921` / DeepInfra / $0.3174774692 / score 46.3
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $14.5678518978 / score 50.8

### Secondary evidence coverage

Families total: 381; uncovered: 149;
`worthy_candidate`: 0; `likely_low_signal`: 149.
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

- **Это твой рабочий вариант** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0391/1M, coding 69.1, скидка 70%. Почему: coding 69.1 при цене $0.039/1M; от лидера по качеству отстаёт на 12.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.8 Flash` через Google AI Studio: $0.7500/1M, coding 76.3, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.2 раза при uptime 99.93%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через OpenInference: $0.0753/1M, coding 71.5, скидка 61%. Почему: Скидка 61% активна, но качество 71.5 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, coding 71.4. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через OpenInference: $0.0753/1M, agentic 50.9, скидка 61%. Почему: agentic 50.9 при цене $0.075/1M; от лидера по качеству отстаёт на 7.0 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, agentic 51.0. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.81%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash Vision Exp` через DeepInfra: $0.3234/1M, agentic 47.5, скидка 51%. Почему: Скидка 51% активна, но качество 47.5 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Chutes: $0.3417/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.342/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $2.7273/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $2.727/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $5.4545/1M, intelligence 57.6. Почему: Преимущество не окупает смену: цена $5.455/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Xiaomi: MiMo-V2.6-Pro` через DeepInfra: $0.6840/1M, intelligence 46.3, скидка 10%. Почему: intelligence 46.3 при цене $0.684/1M; от лидера по качеству отстаёт на 4.5 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Sol` через OpenAI: $4.0000/1M, intelligence 47.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Sol` через OpenAI: $8.0000/1M, intelligence 47.0. Почему: Преимущество не окупает смену: цена $8.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
