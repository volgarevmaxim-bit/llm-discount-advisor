"""Russian Markdown report renderer."""
from datetime import datetime


def render_report(shortlist: dict, snapshot: dict, rejected: dict) -> str:
    lines = [
        f"# LLM Discount Advisor — отчёт от {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "Короткий PoC-shortlist для ручного решения, какую модель поставить в Hermes config.yaml.",
        "",
        f"Рассмотрено **{snapshot.get('model_count', 0)}** строк каталога (**{snapshot.get('model_family_count', 0)}** семейств); после scope gate прошло **{snapshot.get('gated_count', 0)}** строк / **{snapshot.get('gated_unique_families', 0)}** семейств, нормализовано **{len(snapshot.get('models', []))}**. Отсеяно и не обработано: **{len(rejected.get('rejected', []))}**.",
        "",
        "## Рекомендации",
        "",
    ]
    for profile in shortlist.get("profiles", []):
        lines += [f"### {profile['title']} (`{profile['profile']}`)", ""]
        for pick in profile.get("picks", []):
            discount = f", скидка {pick['discount']:.0%}" if pick.get("discount") else ""
            effort = pick.get("reasoning_default_effort") or "не указан"
            mandatory = "обязателен" if pick.get("reasoning_mandatory") else "можно отключить/не указан"
            lines.append(f"- **{pick['label']}** — `{pick['name']}` через {pick.get('provider') or 'провайдера не указано'}: ${pick['blended_price']:.4f}/1M, {pick['quality_metric']} {pick.get('quality') or 'нет'}{discount}. Почему: {pick['reason']} Reasoning: `{effort}`, {mandatory}.")
        if not profile.get("picks"):
            lines.append("- Недостаточно кандидатов с объяснимыми данными.")
        lines.append("")
    lines += [
        "## Допущения и честные ограничения",
        "",
        "- Цена берётся только из `/api/v1/models/{id}/endpoints`; `canonical_slug` — ключ семейства, а `id` сохраняет варианты `:free` и `:batch`. Цена `/models` используется только как цена дефолтного провайдера для overpay-сравнения.",
        "- `discount` уже применён к цене. База восстановлена как `price / (1 - discount)`.",
        "- Blended price — прокси, а не стоимость задачи: для профилей используется фиксированное соотношение input:output, указанное рядом с профилем. Универсальный cost per task не вычисляется.",
        "- Latency и throughput эндпоинтов не используются: в аудите эти поля пусты у 100% проверенных endpoint-строк. Uptime — только фильтр надёжности.",
        "- Цена соответствует дефолтному reasoning effort модели. При `high` фактический расход может быть выше: reasoning-токены тарифицируются как output.",
        "- `pricing.overrides` не игнорируется: наличие ступенчатой цены отмечено флагом `has_tiered_pricing`; детальный калькулятор длинного контекста отложен.",
        "- Data API, G5 по объёму, история изменений, дельты, алерты, поиск, фильтры, графики и персонализация не входят в PoC.",
        "- Источник: OpenRouter public API. Бенчмарки показываются как поля, полученные через OpenRouter, а не как собственное измерение.",
        "",
        "## Что смотреть вручную",
        "",
        "`data/gate_rejected.json` — обязательный ежедневный просмотр в первую неделю: ошибка gate невидима, пока нужная модель не окажется среди rejects.",
        "",
    ]
    return "\n".join(lines)
