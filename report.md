# LLM Discount Advisor — отчёт от 2026-08-22

Decision-support для выбора модели и provider/variant в Hermes.

Legacy snapshot: **421** строк каталога / **349** семейств; после scope gate прошло **110** строк / **77** семейств.

## Decision surface

Режим: `rankings_cost_per_request`.
Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.
Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.

Discount calibration: `inconsistent`; sample size: 20.
Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.

### Профиль `chat`

Quality: `intelligence`; floor: —.
Candidates: 16; raw Pareto: 5; stable Pareto: 13.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 63.1
- cost option: `google/gemini-3.7-flash-20260813` / Google / $0.7597188834 / score 56.0
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 63.1

### Профиль `code`

Quality: `coding`; floor: —.
Candidates: 31; raw Pareto: 6; stable Pareto: 11.
- balanced default: `openai/gpt-5.6-terra-20260709` / OpenAI / $2.6053959965 / score 76.7
- cost option: `deepseek/deepseek-v4-flash-20260731` / StreamLake / $0.0960365529 / score 69.1
- quality option: `openai/gpt-5.6-sol-20260709` / OpenAI / $5.7207058493 / score 78.3

### Профиль `agentic`

Quality: `agentic`; floor: —.
Candidates: 21; raw Pareto: 5; stable Pareto: 12.
- balanced default: `z-ai/glm-5.3-20260816` / Z.AI / $3.1033225622 / score 59.1
- cost option: `deepseek/deepseek-v4-flash-20260731` / StreamLake / $0.0960365529 / score 48.4
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 59.2

### Профиль `longdoc`

Quality: `intelligence`; floor: —.
Candidates: 16; raw Pareto: 5; stable Pareto: 13.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 63.1
- cost option: `google/gemini-3.7-flash-20260813` / Google / $0.7597188834 / score 56.0
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 63.1

### Профиль `bulk`

Quality: `intelligence`; floor: —.
Candidates: 19; raw Pareto: 7; stable Pareto: 12.
- balanced default: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 63.1
- cost option: `deepseek/deepseek-v4-flash-20260731` / StreamLake / $0.0960365529 / score 51.8
- quality option: `anthropic/claude-opus-5-20260723` / Claude Platform on AWS / $11.8983017761 / score 63.1

### Secondary evidence coverage

Families total: 349; uncovered: 187;
`worthy_candidate`: 0; `likely_low_signal`: 187.
Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.

### YAML patch preview

Status: `not_applied`; requires confirmation: `True`.
Конфигурация автоматически не изменялась.

### Что изменилось

Status: `compared`; events: 0.

## Legacy shortlist

### Быстрый ассистент (`chat`)

- **Это твой рабочий вариант** — `Google: Gemini 3.7 Flash` через Google: $0.3750/1M, intelligence 56.0, скидка 75%. Почему: intelligence 56.0 при цене $0.375/1M; от лидера по качеству отстаёт на 7.1 п. Reasoning: `medium`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Terra` через OpenAI: $2.2500/1M, intelligence 56.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.91%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $2.0000/1M, intelligence 60.9, скидка 50%. Почему: Скидка 50% активна, но качество 60.9 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Meta: Muse Spark 1.2` через Meta: $2.0000/1M, intelligence 56.8. Почему: Преимущество не окупает смену: цена $2.000/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, обязателен.

### Код (`code`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, coding 68.8. Почему: coding 68.8 при цене $0.000/1M; от лидера по качеству отстаёт на 9.2 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через StreamLake: $0.5160/1M, coding 68.8, скидка 76%. Почему: У этой же модели есть провайдер дешевле в 2.9 раза при uptime 99.12%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через StreamLake: $0.0856/1M, coding 69.1, скидка 51%. Почему: Скидка 51% активна, но качество 69.1 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, coding 71.4. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Агентный workflow (`agentic`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, agentic 45.7. Почему: agentic 45.7 при цене $0.000/1M; от лидера по качеству отстаёт на 13.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через StreamLake: $0.5160/1M, agentic 45.7, скидка 76%. Почему: У этой же модели есть провайдер дешевле в 2.9 раза при uptime 99.12%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через StreamLake: $0.0856/1M, agentic 48.4, скидка 51%. Почему: Скидка 51% активна, но качество 48.4 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.2250/1M, agentic 46.9. Почему: Преимущество не окупает смену: цена $0.225/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

### Длинные документы (`longdoc`)

- **Это твой рабочий вариант** — `Google: Gemini 3.7 Flash` через Google: $0.2557/1M, intelligence 56.0, скидка 75%. Почему: intelligence 56.0 при цене $0.256/1M; от лидера по качеству отстаёт на 7.1 п. Reasoning: `medium`, обязателен.
- **Та же модель, но дешевле провайдер** — `OpenAI: GPT-5.6 Terra` через OpenAI: $1.4545/1M, intelligence 56.6. Почему: У этой же модели есть провайдер дешевле в 2.0 раза при uptime 99.91%. Reasoning: `medium`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `OpenAI: GPT-5.6 Sol` через OpenAI: $1.3636/1M, intelligence 60.9, скидка 50%. Почему: Скидка 50% активна, но качество 60.9 требует осторожной проверки. Reasoning: `medium`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `Meta: Muse Spark 1.2` через Meta: $1.5227/1M, intelligence 56.8. Почему: Преимущество не окупает смену: цена $1.523/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, обязателен.

### Массовая генерация (`bulk`)

- **Это твой рабочий вариант** — `Z.ai: GLM 5.2 (free)` через Decart: $0.0000/1M, intelligence 52.6. Почему: intelligence 52.6 при цене $0.000/1M; от лидера по качеству отстаёт на 10.5 п. Reasoning: `high`, можно отключить/не указан.
- **Та же модель, но дешевле провайдер** — `Z.ai: GLM 5.2` через StreamLake: $0.8760/1M, intelligence 52.6, скидка 76%. Почему: У этой же модели есть провайдер дешевле в 2.9 раза при uptime 99.12%. Reasoning: `high`, можно отключить/не указан.
- **Большая скидка, но не для основной работы** — `DeepSeek: DeepSeek V4 Flash 0731` через StreamLake: $0.1198/1M, intelligence 51.8, скидка 51%. Почему: Скидка 51% активна, но качество 51.8 требует осторожной проверки. Reasoning: `high`, можно отключить/не указан.
- **Скорее всего, менять не стоит** — `OpenAI: GPT-5.6 Luna` через OpenAI: $0.4750/1M, intelligence 52.3. Почему: Преимущество не окупает смену: цена $0.475/1M без минимум 30% экономии относительно дефолта. Reasoning: `medium`, можно отключить/не указан.

## Ограничения

- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.
- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.
- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.
- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.
- Если frontend Rankings schema ломается, normal decision surface не публикуется.

Источник: OpenRouter public API и публичная frontend Rankings surface.
