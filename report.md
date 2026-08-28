# LLM Discount Advisor — отчёт от 2026-08-28

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **388** строк каталога / **345** семейств; после scope gate прошло **98** строк / **72** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 17; raw Pareto: 4; stable Pareto: 13.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 63.1
- cost option: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1376371084 / score 57.5
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 63.1

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 32; raw Pareto: 5; stable Pareto: 12.
- balanced default: `openai/gpt-5.6-terra-20260709` / OpenAI / $2.9159865292 / score 76.7
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.1254540918 / score 69.1
- quality option: `openai/gpt-5.6-sol-20260709` / OpenAI / $4.9726651389 / score 78.3

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 22; raw Pareto: 4; stable Pareto: 7.
- balanced default: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1376371084 / score 58.2
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.1254540918 / score 48.4
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 59.2

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 17; raw Pareto: 4; stable Pareto: 13.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 63.1
- cost option: `z-ai/glm-5.3-flash-20260826` / Z.AI / $0.1376371084 / score 57.5
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 63.1

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 19; raw Pareto: 7; stable Pareto: 11.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 63.1
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.1254540918 / score 51.8
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $12.9008771875 / score 63.1

### Secondary evidence coverage

Families total: 345; uncovered: 184;
`worthy_candidate`: 0; `likely_low_signal`: 184.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.1187/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.119/1M; от лидера по качеству отстаёт на 5.6 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Terra` через OpenAI: $2.2500/1M, intelligence 56.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.89%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `Google: Gemini 3.7 Flash` через Google: $0.3750/1M, intelligence 56.0, скидка 75%. Почему: Скидка 75% активна, но качество 56.0 требует осторожной проверки. Reasoning: `medium`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Sol` через OpenAI: $2.0000/1M, intelligence 60.9, скидка 50%. Почему: Преимущество не окупает смену: цена $2.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, coding 68.8. Почему: coding 68.8 при цене $0.000/1M; от лидера по качеству отстаёт на 9.2 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через Baidu: $0.6429/1M, coding 68.8, скидка 70%. Почему: У этой же модели есть провайдер дешевле в 2.8 раза при uptime 99.98%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0475/1M, coding 69.1, скидка 80%. Почему: Скидка 80% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.1187/1M, coding 71.5, скидка 67%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, agentic 45.7. Почему: agentic 45.7 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через Baidu: $0.6429/1M, agentic 45.7, скидка 70%. Почему: У этой же модели есть провайдер дешевле в 2.8 раза при uptime 99.98%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0475/1M, agentic 48.4, скидка 80%. Почему: Скидка 80% активна, но качество 48.4 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.1187/1M, agentic 58.2, скидка 67%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Z.AI: $0.0909/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.091/1M; от лидера по качеству отстаёт на 5.6 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Terra` через OpenAI: $1.4545/1M, intelligence 56.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.89%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `Google: Gemini 3.7 Flash` через Google: $0.2557/1M, intelligence 56.0, скидка 75%. Почему: Скидка 75% активна, но качество 56.0 требует осторожной проверки. Reasoning: `medium`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Sol` через OpenAI: $1.3636/1M, intelligence 60.9, скидка 50%. Почему: Преимущество не окупает смену: цена $1.364/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, intelligence 52.6. Почему: intelligence 52.6 при цене $0.000/1M; от лидера по качеству отстаёт на 10.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через Baidu: $1.0914/1M, intelligence 52.6, скидка 70%. Почему: У этой же модели есть провайдер дешевле в 2.8 раза при uptime 99.98%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0825/1M, intelligence 51.8, скидка 80%. Почему: Скидка 80% активна, но качество 51.8 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `MiniMax: MiniMax M3 (free)` через GMICloud: $0.0000/1M, intelligence 45.4. Почему: Преимущество не окупает смену: цена $0.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `не указан`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
