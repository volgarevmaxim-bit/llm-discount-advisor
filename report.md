# LLM Discount Advisor — отчёт от 2026-11-01

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **416** строк каталога / **368** семейств; после scope gate прошло **116** строк / **83** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 1; stable Pareto: 2.
- balanced default: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.5954585746 / score 58.4
- cost option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.5954585746 / score 58.4
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.5954585746 / score 58.4

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 34; raw Pareto: 6; stable Pareto: 15.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0042187655 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / Baidu / $0.0503324971 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0042187655 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 14; raw Pareto: 5; stable Pareto: 7.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $4.0202075927 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / Relace / $0.0984036637 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $21.0042187655 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 1; stable Pareto: 2.
- balanced default: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.5954585746 / score 58.4
- cost option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.5954585746 / score 58.4
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $11.5954585746 / score 58.4

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 1; stable Pareto: 1.
- balanced default: `openai/gpt-6.1-terra-20261026` / OpenAI / $0.859134003 / score 51.0
- cost option: `openai/gpt-6.1-terra-20261026` / OpenAI / $0.859134003 / score 51.0
- quality option: `openai/gpt-6.1-terra-20261026` / OpenAI / $0.859134003 / score 51.0

### Secondary evidence coverage

Families total: 368; uncovered: 209;
`worthy_candidate`: 0; `likely_low_signal`: 209.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $8.0000/1M, intelligence 58.4. Почему: intelligence 58.4 при цене $8.000/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $10.0000/1M, intelligence 56.9. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.87%. Reasoning: `medium`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0445/1M, coding 71.5, скидка 50%. Почему: coding 71.5 при цене $0.044/1M; от лидера по качеству отстаёт на 9.2 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через Baidu: $0.2903/1M, coding 68.8, скидка 86%. Почему: У этой же модели есть провайдер дешевле в 5.9 раза при uptime 100.00%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через Baidu: $0.0667/1M, coding 69.1, скидка 90%. Почему: Скидка 90% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через PrimeIntellect: $0.1655/1M, coding 68.1, скидка 25%. Почему: Преимущество не окупает смену: цена $0.166/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через Relace: $0.0445/1M, agentic 50.9, скидка 50%. Почему: agentic 50.9 при цене $0.044/1M; от лидера по качеству отстаёт на 6.3 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Qwen: Qwen3.8 27B` через PrimeIntellect: $0.1655/1M, agentic 45.8, скидка 25%. Почему: У этой же модели есть провайдер дешевле в 3.5 раза при uptime 99.27%. Reasoning: `xhigh`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash Vision Exp` через DeepInfra: $0.3234/1M, agentic 47.5, скидка 51%. Почему: Скидка 51% активна, но качество 47.5 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Z.ai: GLM 5.3` через Wafer: $0.4024/1M, agentic 53.1, скидка 80%. Почему: Преимущество не окупает смену: цена $0.402/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, обязателен.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $5.4545/1M, intelligence 58.4. Почему: intelligence 58.4 при цене $5.455/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `high`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Astra` через OpenAI: $6.8182/1M, intelligence 56.9. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.87%. Reasoning: `medium`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `OpenAI: GPT-6.1 Terra` через OpenAI: $2.0000/1M, intelligence 51.0. Почему: intelligence 51.0 при цене $2.000/1M; от лидера по качеству отстаёт на 0.0 п. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `MoonshotAI: Kimi K3.1 Pro` через Moonshot AI: $8.0000/1M, intelligence 46.0. Почему: Преимущество не окупает смену: цена $8.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `max`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
