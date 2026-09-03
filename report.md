# LLM Discount Advisor — отчёт от 2026-09-03

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **424** строк каталога / **346** семейств; после scope gate прошло **110** строк / **70** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 19; raw Pareto: 6; stable Pareto: 11.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 65.7
- cost option: `z-ai/glm-5.3-flash-20260826` / GMICloud / $0.1712315639 / score 57.5
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 65.7

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 33; raw Pareto: 6; stable Pareto: 13.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 81.6
- cost option: `z-ai/glm-5.3-flash-20260826` / GMICloud / $0.1712315639 / score 71.5
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 24; raw Pareto: 4; stable Pareto: 7.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 61.3
- cost option: `z-ai/glm-5.3-flash-20260826` / GMICloud / $0.1712315639 / score 58.2
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 61.3

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 19; raw Pareto: 6; stable Pareto: 11.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 65.7
- cost option: `z-ai/glm-5.3-flash-20260826` / GMICloud / $0.1712315639 / score 57.5
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0880959422 / score 65.7

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 18; raw Pareto: 6; stable Pareto: 11.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $11.1447328836 / score 63.1
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.2063913529 / score 51.8
- quality option: `anthropic/claude-opus-5-20260723` / Azure / $11.1447328836 / score 63.1

### Secondary evidence coverage

Families total: 346; uncovered: 183;
`worthy_candidate`: 0; `likely_low_signal`: 183.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 5.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.119/1M; от лидера по качеству отстаёт на 8.2 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.8 Flash` через Google AI Studio: $0.7500/1M, intelligence 58.7, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.67%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.7500/1M, intelligence 56.0, скидка 50%. Почему: Скидка 50% активна, но качество 56.0 требует осторожной проверки. Reasoning: `medium`, обязателен.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через Decart: $1.6985/1M, intelligence 59.5, скидка 21%. Почему: Преимущество не окупает смену: цена $1.699/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, coding 68.8. Почему: coding 68.8 при цене $0.000/1M; от лидера по качеству отстаёт на 12.8 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.8 Flash` через Google AI Studio: $0.7500/1M, coding 76.3, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.67%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0775/1M, coding 69.1, скидка 70%. Почему: Скидка 70% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, coding 71.5, скидка 67%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, agentic 45.7. Почему: agentic 45.7 при цене $0.000/1M; от лидера по качеству отстаёт на 15.6 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.8 Flash` через Google AI Studio: $0.7500/1M, agentic 50.0, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.67%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0775/1M, agentic 48.4, скидка 70%. Почему: Скидка 70% активна, но качество 48.4 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.1187/1M, agentic 58.2, скидка 67%. Почему: Преимущество не окупает смену: цена $0.119/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через GMICloud: $0.0909/1M, intelligence 57.5, скидка 67%. Почему: intelligence 57.5 при цене $0.091/1M; от лидера по качеству отстаёт на 8.2 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Google: Gemini 3.8 Flash` через Google AI Studio: $0.5114/1M, intelligence 58.7, скидка 50%. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.67%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Google: Gemini 3.7 Flash` через Google AI Studio: $0.5114/1M, intelligence 56.0, скидка 50%. Почему: Скидка 50% активна, но качество 56.0 требует осторожной проверки. Reasoning: `medium`, обязателен.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через Decart: $1.3215/1M, intelligence 59.5, скидка 21%. Почему: Преимущество не окупает смену: цена $1.321/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, intelligence 52.6. Почему: intelligence 52.6 при цене $0.000/1M; от лидера по качеству отстаёт на 10.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.4750/1M, intelligence 52.3. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.82%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.1325/1M, intelligence 51.8, скидка 70%. Почему: Скидка 70% активна, но качество 51.8 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `MiniMax: MiniMax M3 (free)` через GMICloud: $0.0000/1M, intelligence 45.4. Почему: Преимущество не окупает смену: цена $0.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `не указан`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
