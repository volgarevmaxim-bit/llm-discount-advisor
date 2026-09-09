# LLM Discount Advisor — отчёт от 2026-09-09

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **431** строк каталога / **348** семейств; после scope gate прошло **125** строк / **80** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 0; raw Pareto: 0; stable Pareto: 0.
- balanced default: нет сравнимого кандидата
- cost option: нет сравнимого кандидата
- quality option: нет сравнимого кандидата

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 34; raw Pareto: 7; stable Pareto: 15.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $24.8273504305 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.1163881415 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $24.8273504305 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 12; raw Pareto: 4; stable Pareto: 8.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $14.8293403214 / score 56.2
- cost option: `z-ai/glm-5.3-flash-20260826` / DeepInfra / $0.1479138263 / score 51.2
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $24.8273504305 / score 58.0

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 0; raw Pareto: 0; stable Pareto: 0.
- balanced default: нет сравнимого кандидата
- cost option: нет сравнимого кандидата
- quality option: нет сравнимого кандидата

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-opus-5-20260723` / Azure / $14.8293403214 / score 50.7
- cost option: `openai/gpt-5.6-sol-20260709` / OpenAI / $4.9272821999 / score 47.1
- quality option: `anthropic/claude-opus-5-20260723` / Azure / $14.8293403214 / score 50.7

### Secondary evidence coverage

Families total: 348; uncovered: 185;
`worthy_candidate`: 0; `likely_low_signal`: 185.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- Недостаточно кандидатов с объяснимыми данными.

### Код (`code`)

- **Это твой рабочий вариант** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0775/1M, coding 69.1, скидка 70%. Почему: coding 69.1 при цене $0.078/1M; от лидера по качеству отстаёт на 12.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, coding 76.9. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.96%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `Z.ai: GLM 5.3 Flash` через DeepInfra: $0.1187/1M, coding 71.5, скидка 67%. Почему: Скидка 67% активна, но качество 71.5 требует осторожной проверки. Reasoning: `max`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, coding 71.4. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через DeepInfra: $0.1187/1M, agentic 51.2, скидка 67%. Почему: agentic 51.2 при цене $0.119/1M; от лидера по качеству отстаёт на 6.8 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, agentic 51.5. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.96%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $2.0000/1M, agentic 50.5, скидка 50%. Почему: Скидка 50% активна, но качество 50.5 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Darkbloom: $0.6125/1M, agentic 46.5. Почему: Преимущество не окупает смену: цена $0.613/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- Недостаточно кандидатов с объяснимыми данными.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 47.1, скидка 50%. Почему: intelligence 47.1 при цене $4.000/1M; от лидера по качеству отстаёт на 3.6 п. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Claude Opus 5` через Azure: $20.0000/1M, intelligence 50.7. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
