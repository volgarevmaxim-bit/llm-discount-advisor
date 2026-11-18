# LLM Discount Advisor — отчёт от 2026-11-18

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **443** строк каталога / **375** семейств; после scope gate прошло **146** строк / **98** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 6; raw Pareto: 4; stable Pareto: 5.
- balanced default: `anthropic/claude-fable-5.2-20261109` / Google / $21.2156407667 / score 64.6
- cost option: `openai/gpt-6.2-sol-20261117` / OpenAI / $1.7436108262 / score 57.3
- quality option: `anthropic/claude-fable-5.2-20261109` / Google / $21.2156407667 / score 64.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 35; raw Pareto: 8; stable Pareto: 19.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $27.0487386887 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / Relace / $0.0707695355 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $27.0487386887 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 15; raw Pareto: 5; stable Pareto: 5.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.1830802049 / score 56.0
- cost option: `qwen/qwen3.8-flash-20260826` / Alibaba / $0.1695823902 / score 53.6
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $27.0487386887 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 6; raw Pareto: 4; stable Pareto: 5.
- balanced default: `anthropic/claude-fable-5.2-20261109` / Google / $21.2156407667 / score 64.6
- cost option: `openai/gpt-6.2-sol-20261117` / OpenAI / $1.7436108262 / score 57.3
- quality option: `anthropic/claude-fable-5.2-20261109` / Google / $21.2156407667 / score 64.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 1; stable Pareto: 1.
- balanced default: `openai/gpt-6.1-terra-20261026` / OpenAI / $0.9701028203 / score 51.3
- cost option: `openai/gpt-6.1-terra-20261026` / OpenAI / $0.9701028203 / score 51.3
- quality option: `openai/gpt-6.1-terra-20261026` / OpenAI / $0.9701028203 / score 51.3

### Secondary evidence coverage

Families total: 375; uncovered: 209;
`worthy_candidate`: 0; `likely_low_signal`: 209.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Google: Gemini 4 Carbon` через Google AI Studio: $2.0000/1M, intelligence 60.0, скидка 50%. Почему: intelligence 60.0 при цене $2.000/1M; от лидера по качеству отстаёт на 4.6 п. Reasoning: `medium`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, intelligence 56.9. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-6.2 Sol` через OpenAI: $4.0000/1M, intelligence 57.3. Почему: Преимущество не окупает смену: цена $4.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0495/1M, coding 71.5, скидка 50%. Почему: coding 71.5 при цене $0.050/1M; от лидера по качеству отстаёт на 9.2 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через DeepInfra: $0.6975/1M, coding 68.8, скидка 56%. Почему: У этой же модели есть провайдер дешевле в 2.4 раза при uptime 100.00%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через Relace: $0.0875/1M, coding 69.1, скидка 70%. Почему: Скидка 70% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 Flash` через Alibaba: $0.2300/1M, coding 73.1. Почему: Преимущество не окупает смену: цена $0.230/1M без минимум 30% экономии относительно дефолта. Reasoning: `не указан`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0495/1M, agentic 50.9, скидка 50%. Почему: agentic 50.9 при цене $0.050/1M; от лидера по качеству отстаёт на 6.3 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, agentic 51.0. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash Vision Exp` через DeepInfra: $0.3234/1M, agentic 47.5, скидка 51%. Почему: Скидка 51% активна, но качество 47.5 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 Flash` через Alibaba: $0.2300/1M, agentic 53.6. Почему: Преимущество не окупает смену: цена $0.230/1M без минимум 30% экономии относительно дефолта. Reasoning: `не указан`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Google: Gemini 4 Carbon` через Google AI Studio: $1.3636/1M, intelligence 60.0, скидка 50%. Почему: intelligence 60.0 при цене $1.364/1M; от лидера по качеству отстаёт на 4.6 п. Reasoning: `medium`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $6.8182/1M, intelligence 56.9. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, обязателен.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-6.2 Sol` через OpenAI: $2.7273/1M, intelligence 57.3. Почему: Преимущество не окупает смену: цена $2.727/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `OpenAI: GPT-6.1 Terra` через OpenAI: $2.0000/1M, intelligence 51.3. Почему: intelligence 51.3 при цене $2.000/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `MoonshotAI: Kimi K3.1 Pro` через Relace: $6.3618/1M, intelligence 46.5, скидка 40%. Почему: Скидка 40% активна, но качество 46.5 требует осторожной проверки. Reasoning: `max`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
