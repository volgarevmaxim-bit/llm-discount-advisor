Ты помогаешь спроектировать **proof of concept and staged MVP** для продукта в духе:

**LLM Discount Dashboard / Model Choice Advisor**

Но это **не** generic pricing dashboard и **не** полный enterprise product.
Твоя задача — подготовить **детальный spec-driven design document** для поэтапной реализации полезного прототипа, который можно быстро показать небольшой аудитории и собрать реальный feedback.

***

# 1. Product framing

## Core thesis

Продукт нужен не для того, чтобы “показывать каталог моделей”, а чтобы **сужать большое пространство выбора до короткого списка реально полезных действий** для конкретного пользователя или маленькой команды.

Основная аудитория первой версии:

- закрытое комьюнити индивидуальных предпринимателей (~500 человек),
- активно используют AI,
- чувствительны к расходам,
- не хотят вручную сравнивать десятки моделей,
- ценят простоту и actionable output.

Продукт должен отвечать на вопросы вида:

- Что мне разумно использовать как default?
- Что стало дешевле и при этом всё ещё достаточно хорошо?
- Что выглядит заманчиво по скидке, но не является safe default?
- Что изменилось со вчерашнего дня?
- Надо ли вообще заходить на сайт, или лучше присылать это в Telegram/Markdown digest?

***

# 2. Main task

Подготовь **structured design spec** с поэтапным планом:

- **PoC**
- **MVP-1**
- **MVP-2**

Не проектируй “сразу весь продукт”.
Оптимизируй под **learning velocity**, а не под completeness.

***

# 3. Critical constraints

## 3.1 Do not assume cost-per-task must be computed

Не предполагай, что `cost per task` надо вычислять самостоятельно.

Сначала проведи аудит данных и раздели все метрики на категории:

- **directly available**
- **available but paid-gated**
- **derivable**
- **proxy only**
- **not realistically available**

Если `cost per task` где-то уже доступен как готовый сигнал, это нужно использовать как вариант.
Если доступность зависит от платного плана, API tier, licensing, redistribution limits, quotas or sales access — это надо **явно и честно указать**.

## 3.2 Static-first assumption

Предпочтительная стартовая форма:

- **статический сайт**
- развёртывание на **GitHub Pages**
- локальные JSON/Markdown artifacts в репозитории
- scheduled refresh через **GitHub Actions**

Не добавляй backend, database, auth, queues или complex infra, если они не являются строго необходимыми.

## 3.3 Delivery channel is part of the product

Канал доставки — часть продукта, а не второстепенная деталь.

Обязательно оцени как минимум:

- static website,
- Markdown memo / digest,
- Telegram delivery,
- Telegram alerts.

Пользователи могут предпочесть push-канал вместо сайта.

## 3.4 Expect disruptive feedback

Сразу закладывай, что аудитория может захотеть не то, что кажется логичным сейчас.
Например:

- “нам важнее alerts, чем ranking”;
- “нам не нужен Hermes”;
- “мы вообще не используем OpenRouter как основной способ работы”;
- “мы не хотим сайт, шли это в Telegram”;
- “самый полезный сигнал — скидка пропала, а не появилась”;
- “нам нужен safe default, а не Pareto explanation”.

***

# 4. Deliverable format

Итоговый результат должен быть **structured design spec** со следующими разделами:

1. Executive summary
2. Product goal
3. User segments and jobs-to-be-done
4. Product hypotheses
5. Data source audit
6. Metrics inventory
7. Recommendation logic options
8. Staged roadmap: PoC / MVP-1 / MVP-2
9. UX / delivery options
10. Technical architecture
11. Output artifacts
12. Risks and disruptive feedback scenarios
13. Open questions
14. Final recommendation: what to build first

***

# 5. Data source audit requirements

Проведи отдельный аудит источников данных.

## 5.1 OpenRouter as primary operational source

Проверь, что реально доступно из OpenRouter и пригодно для PoC / MVP:

- model ids
- pricing
- discounts
- free models / collections
- context window
- benchmarks or ranking indices
- latency / uptime / throughput if present
- compare/models/benchmarks pages or API endpoints
- change frequency and freshness
- whether data is sufficient for ranking, alerting, and shortlist generation

Сделай вывод:

- что достаточно для PoC,
- что достаточно для MVP-1,
- каких данных не хватает,
- где есть risk of instability or weak semantics.


## 5.2 Artificial Analysis as secondary validation/enrichment source

Отдельно оцени **Artificial Analysis** как независимый или enrich-слой:

- benchmark scores
- intelligence index
- pricing
- blended price
- cost per task if directly available
- latency / throughput / availability
- API availability
- free limits
- paid limits
- whether usage in MVP is feasible
- whether it should be optional, validation-only, or integrated in later stages

Обязательно отдели:

- what is publicly/free accessible,
- what is API-accessible but rate-limited,
- what is paid/commercial,
- what may create operational dependency for a small MVP.


## 5.3 Optional third source

Если нужен третий источник, упомяни его кратко и только если он реально снижает product risk.
Не раздувай scope.

***

# 6. Recommendation logic requirements

Продукт должен уметь выдавать **explainable recommendations**, но не обязан начинать со сложной математики.

Нужно проанализировать и сравнить несколько подходов.

## 6.1 Heuristic shortlist logic

Опиши простую rule-based логику, пригодную для PoC:

- cheapest acceptable
- default picks
- big discounts worth watching
- probably not worth switching

Это должна быть explainable логика, которую можно запустить даже если данных мало.

## 6.2 Pareto / frontier logic

Отдельно проанализируй идею:

- Pareto frontier on cost vs intelligence
- knee point / elbow
- efficient frontier zones

Но не предполагай, что красивый перегиб обязательно будет.

## 6.3 Fallback if no clear knee exists

Если фронтир:

- почти линейный,
- noisy,
- sparse,
- unstable,
- visually ambiguous,

предложи альтернативы:

- parallel shift of Pareto line/frontier,
- tolerance bands around efficient frontier,
- dominance with margins,
- value-per-cost thresholds,
- zone-based heuristics,
- piecewise business rules.

Нужно не просто перечислить, а дать recommendation:

- что годится для PoC,
- что для MVP-1,
- что можно отложить на MVP-2.


## 6.4 Labels and taxonomy

Spec должен определить, как присваиваются human-readable статусы, например:

- **This is your default**
- **Good enough and cheaper**
- **Probably not worth switching**
- **Big discount, but not my safe default**

Опиши, какие сигналы стоят за каждым статусом.

***

# 7. Staged product plan

Нужно спроектировать 3 стадии.

## 7.1 PoC

Цель: проверить, есть ли вообще ценность в shortlist/recommendation artifact.

Ожидаемый формат:

- статический сайт на GitHub Pages,
- JSON snapshot,
- Markdown report,
- без backend.

Нужно явно определить:

- hypothesis,
- minimal data needed,
- minimal UI,
- what feedback to collect.


## 7.2 MVP-1

Цель: проверить delivery fit и change-awareness.

Рассмотри как минимум:

- static site remains,
- Telegram digest,
- top changes since last snapshot,
- whether website is enough,
- whether audience prefers push delivery.


## 7.3 MVP-2

Цель: добавить только то, что реально подтверждено спросом.

Может включать:

- alerts,
- discount disappeared,
- watchlists,
- richer recommendation logic,
- task-driven premium rules,
- optional downstream integration like Hermes config advisor.

Но не предполагай, что это обязательно нужно.

***

# 8. UX / UI expectations

Интерфейс должен быть **decision-support**, а не BI dashboard.

Для каждой стадии опиши:

- основную сущность интерфейса,
- минимальный пользовательский сценарий,
- нужен ли график вообще,
- когда chart adds value and when it is just decoration.

Обязательно рассмотри вариант, что **в PoC график может быть не нужен**, если основная ценность — short memo + shortlist cards.

Возможные primary artifacts:

- website cards,
- Markdown report,
- Telegram digest,
- alert message.

***

# 9. Technical architecture expectations

Архитектура должна быть маленькой, объяснимой и deployable quickly.

Предпочтительный старт:

- static HTML/JS site,
- generated JSON files in repo,
- scheduled GitHub Actions refresh,
- optional Telegram send step from workflow.

Оцени feasibility такой схемы:

- fetch source data,
- normalize,
- compute shortlist,
- generate artifacts,
- publish static site,
- optionally send Telegram summary.

Если Telegram feasible через GitHub Actions + bot token + secrets — зафиксируй это как lightweight option.
Если есть ограничения или fragility — тоже укажи явно. GitHub Actions can schedule data refreshes and commit updated JSON that GitHub Pages then serves as a static site, and Telegram notifications can be sent from Actions using bot token and chat ID secrets. [^1][^2][^3][^4]

***

# 10. Output artifacts

Spec должен определить, какие артефакты генерирует каждая стадия.

Минимум опиши:

- `shortlist.json`
- `report.md`
- static site page
- optional `telegram_message.md` or equivalent message payload structure
- optional change log artifact for alerts

***

# 11. Explicit non-goals

Явно укажи, что **не входит** в ранние стадии:

- enterprise multi-tenant platform
- real-time streaming backend
- auth
- complex personalized accounts
- heavy analytics dashboard
- assuming Hermes is the main target workflow
- assuming all users want a website
- assuming all users care about Pareto charts

***

# 12. Quality bar

Spec должен быть:

- practical,
- opinionated,
- explicit about trade-offs,
- honest about data limitations,
- suitable as direct input for implementation,
- optimized for one-week prototype velocity.

***

# 13. Final section requirements

В конце обязательно дай:

1. **Recommended PoC build**
2. **Recommended MVP-1 build**
3. **What to postpone**
4. **What to validate with real users first**
5. **What could invalidate the whole current product direction**
6. **Best default delivery format**
7. **Best fallback if data quality is weaker than expected**

***

# 14. Style

Пиши как product/technical architect в spec-driven approach:

- ясно,
- без маркетинговой воды,
- с конкретными choices,
- с объяснением “why this, not that”.

Do not write code.
Do not jump to implementation before clarifying staged product strategy.