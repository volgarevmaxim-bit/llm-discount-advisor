# LLM Discount Advisor — отчёт от 2026-10-11

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **458** строк каталога / **372** семейств; после scope gate прошло **121** строк / **81** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $5.8775501924 / score 56.0
- cost option: `anthropic/claude-sonnet-5.5-20260928` / Google / $5.8775501924 / score 56.0
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $13.3446793374 / score 57.6

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 35; raw Pareto: 9; stable Pareto: 16.
- balanced default: `anthropic/claude-fable-5.1-20260831` / Azure / $27.4331942309 / score 81.6
- cost option: `deepseek/deepseek-v4-flash-20260731` / OpenInference / $0.0771922119 / score 69.1
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $27.4331942309 / score 81.6

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 14; raw Pareto: 6; stable Pareto: 7.
- balanced default: `qwen/qwen3.8-max-20260902` / Alibaba / $3.7319398891 / score 56.0
- cost option: `z-ai/glm-5.3-flash-20260826` / InferenceNet / $0.2152511785 / score 50.9
- quality option: `anthropic/claude-fable-5.1-20260831` / Azure / $27.4331942309 / score 57.9

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 2; raw Pareto: 2; stable Pareto: 2.
- balanced default: `anthropic/claude-sonnet-5.5-20260928` / Google / $5.8775501924 / score 56.0
- cost option: `anthropic/claude-sonnet-5.5-20260928` / Google / $5.8775501924 / score 56.0
- quality option: `anthropic/claude-opus-5.5-20260921` / Amazon Bedrock / $13.3446793374 / score 57.6

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 4; raw Pareto: 3; stable Pareto: 4.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $15.0885610839 / score 50.8
- cost option: `xiaomi/mimo-v2.6-pro-20260921` / DeepInfra / $0.4421377303 / score 46.3
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $15.0885610839 / score 50.8

### Secondary evidence coverage

Families total: 372; uncovered: 144;
`worthy_candidate`: 0; `likely_low_signal`: 144.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 1.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $4.0000/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $4.000/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $8.0000/1M, intelligence 57.6. Почему: Преимущество не окупает смену: цена $8.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через InferenceNet: $0.0650/1M, coding 71.5, скидка 54%. Почему: coding 71.5 при цене $0.065/1M; от лидера по качеству отстаёт на 10.1 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через InferenceNet: $0.2625/1M, coding 68.8, скидка 60%. Почему: У этой же модели есть провайдер дешевле в 6.8 раза при uptime 100.00%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через OpenInference: $0.0824/1M, coding 69.1, скидка 80%. Почему: Скидка 80% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, coding 71.4. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.3 Flash` через InferenceNet: $0.0650/1M, agentic 50.9, скидка 54%. Почему: agentic 50.9 при цене $0.065/1M; от лидера по качеству отстаёт на 7.0 п. Reasoning: `max`, обязателен.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.3` через Baidu: $0.5375/1M, agentic 53.1, скидка 75%. Почему: У этой же модели есть провайдер дешевле в 2.3 раза при uptime 100.00%. Reasoning: `max`, обязателен.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash Vision Exp` через DeepInfra: $0.3234/1M, agentic 47.5, скидка 51%. Почему: Скидка 51% активна, но качество 47.5 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Qwen: Qwen3.8 27B` через Tenstorrent: $0.3675/1M, agentic 45.8, скидка 25%. Почему: Преимущество не окупает смену: цена $0.368/1M без минимум 30% экономии относительно дефолта. Reasoning: `xhigh`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Anthropic: Claude Sonnet 5.5` через Google: $2.7273/1M, intelligence 56.0. Почему: intelligence 56.0 при цене $2.727/1M; от лидера по качеству отстаёт на 1.6 п. Reasoning: `high`, обязателен.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5.5` через Amazon Bedrock: $5.4545/1M, intelligence 57.6. Почему: Преимущество не окупает смену: цена $5.455/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Xiaomi: MiMo-V2.6-Pro` через DeepInfra: $0.7600/1M, intelligence 46.3. Почему: intelligence 46.3 при цене $0.760/1M; от лидера по качеству отстаёт на 4.5 п. Reasoning: `не указан`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-6 Sol` через OpenAI: $4.0000/1M, intelligence 47.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 100.00%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $4.0000/1M, intelligence 47.0, скидка 50%. Почему: Скидка 50% активна, но качество 47.0 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Anthropic: Claude Opus 5` через Claude Platform on AWS: $20.0000/1M, intelligence 50.8. Почему: Преимущество не окупает смену: цена $20.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `high`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
