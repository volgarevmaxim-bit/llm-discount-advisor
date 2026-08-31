# LLM Discount Advisor — отчёт от 2026-08-31

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **396** строк каталога / **343** семейств; после scope gate прошло **106** строк / **71** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 17; raw Pareto: 5; stable Pareto: 12.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 63.1
- cost option: `z-ai/glm-5.3-flash-20260826` / Relace / $0.0695505756 / score 57.5
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 63.1

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 32; raw Pareto: 4; stable Pareto: 12.
- balanced default: `openai/gpt-5.6-terra-20260709` / OpenAI / $2.2987607645 / score 76.7
- cost option: `z-ai/glm-5.3-flash-20260826` / Relace / $0.0695505756 / score 71.5
- quality option: `openai/gpt-5.6-sol-20260709` / OpenAI / $6.3948809818 / score 78.3

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 22; raw Pareto: 3; stable Pareto: 6.
- balanced default: `z-ai/glm-5.3-flash-20260826` / Relace / $0.0695505756 / score 58.2
- cost option: `z-ai/glm-5.3-flash-20260826` / Relace / $0.0695505756 / score 58.2
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 59.2

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 17; raw Pareto: 5; stable Pareto: 12.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 63.1
- cost option: `z-ai/glm-5.3-flash-20260826` / Relace / $0.0695505756 / score 57.5
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 63.1

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 19; raw Pareto: 8; stable Pareto: 13.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 63.1
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.1322690527 / score 51.8
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.786087773 / score 63.1

### Secondary evidence coverage

Families total: 343; uncovered: 182;
`worthy_candidate`: 0; `likely_low_signal`: 182.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.1128/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.113/1M; от лидера по качеству отстаёт на 5.6 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, intelligence 56.0, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.78%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $2.0000/1M, intelligence 60.9, скидка 50%. Почему: Скидка 50% активна, но качество 60.9 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через DeepInfra: $1.9000/1M, intelligence 59.5, скидка 10%. Почему: Преимущество не окупает смену: цена $1.900/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, coding 68.8. Почему: coding 68.8 при цене $0.000/1M; от лидера по качеству отстаёт на 9.2 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, coding 76.1, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.78%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0625/1M, coding 69.1, скидка 50%. Почему: Скидка 50% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через Relace: $0.1128/1M, coding 71.5, скидка 67%. Почему: Преимущество не окупает смену: цена $0.113/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, agentic 45.7. Почему: agentic 45.7 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, agentic 45.1, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.78%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0625/1M, agentic 48.4, скидка 50%. Почему: Скидка 50% активна, но качество 48.4 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через Relace: $0.1128/1M, agentic 58.2, скидка 67%. Почему: Преимущество не окупает смену: цена $0.113/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0864/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.086/1M; от лидера по качеству отстаёт на 5.6 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.5114/1M, intelligence 56.0, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.78%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $1.3636/1M, intelligence 60.9, скидка 50%. Почему: Скидка 50% активна, но качество 60.9 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через DeepInfra: $1.4545/1M, intelligence 59.5, скидка 10%. Почему: Преимущество не окупает смену: цена $1.455/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, intelligence 52.6. Почему: intelligence 52.6 при цене $0.000/1M; от лидера по качеству отстаёт на 10.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.4750/1M, intelligence 52.3. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.1275/1M, intelligence 51.8, скидка 50%. Почему: Скидка 50% активна, но качество 51.8 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `MiniMax: MiniMax M3 (free)` через GMICloud: $0.0000/1M, intelligence 45.4. Почему: Преимущество не окупает смену: цена $0.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `не указан`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
