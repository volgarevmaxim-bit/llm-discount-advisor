# LLM Discount Advisor — отчёт от 2026-09-01

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **420** строк каталога / **343** семейств; после scope gate прошло **109** строк / **69** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 17; raw Pareto: 5; stable Pareto: 12.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 63.1
- cost option: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1331983537 / score 57.5
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 63.1

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 32; raw Pareto: 4; stable Pareto: 11.
- balanced default: `openai/gpt-5.6-terra-20260709` / OpenAI / $2.7891389899 / score 76.7
- cost option: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1331983537 / score 71.5
- quality option: `openai/gpt-5.6-sol-20260709` / OpenAI / $5.1806024492 / score 78.3

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 22; raw Pareto: 3; stable Pareto: 7.
- balanced default: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1331983537 / score 58.2
- cost option: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1331983537 / score 58.2
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 59.2

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 17; raw Pareto: 5; stable Pareto: 12.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 63.1
- cost option: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1331983537 / score 57.5
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 63.1

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 19; raw Pareto: 7; stable Pareto: 12.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 63.1
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.162029761 / score 51.8
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.6962927054 / score 63.1

### Secondary evidence coverage

Families total: 343; uncovered: 181;
`worthy_candidate`: 0; `likely_low_signal`: 181.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 1.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.1187/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.119/1M; от лидера по качеству отстаёт на 5.6 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, intelligence 56.0, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.40%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $2.0000/1M, intelligence 60.9, скидка 50%. Почему: Скидка 50% активна, но качество 60.9 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через DeepInfra: $1.9000/1M, intelligence 59.5, скидка 10%. Почему: Преимущество не окупает смену: цена $1.900/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0775/1M, coding 69.1, скидка 50%. Почему: coding 69.1 при цене $0.078/1M; от лидера по качеству отстаёт на 8.9 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, coding 76.1, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.40%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.1187/1M, coding 71.5, скидка 67%. Почему: Скидка 67% активна, но качество 71.5 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, coding 71.4. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0775/1M, agentic 48.4, скидка 50%. Почему: agentic 48.4 при цене $0.078/1M; от лидера по качеству отстаёт на 10.8 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, agentic 45.1, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.40%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.1187/1M, agentic 58.2, скидка 67%. Почему: Скидка 67% активна, но качество 58.2 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, agentic 46.9. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.0909/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.091/1M; от лидера по качеству отстаёт на 5.6 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.5114/1M, intelligence 56.0, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.40%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $1.3636/1M, intelligence 60.9, скидка 50%. Почему: Скидка 50% активна, но качество 60.9 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через DeepInfra: $1.4545/1M, intelligence 59.5, скидка 10%. Почему: Преимущество не окупает смену: цена $1.455/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `MiniMax: MiniMax M3 (free)` через GMICloud: $0.0000/1M, intelligence 45.4. Почему: intelligence 45.4 при цене $0.000/1M; от лидера по качеству отстаёт на 17.7 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.4750/1M, intelligence 52.3. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.99%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.1325/1M, intelligence 51.8, скидка 50%. Почему: Скидка 50% активна, но качество 51.8 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `MiniMax: MiniMax M3` через CoreWeave: $0.7775/1M, intelligence 45.4, скидка 50%. Почему: Преимущество не окупает смену: цена $0.777/1M без минимум 30% экономии относительно дефолта. Reasoning: `не указан`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
