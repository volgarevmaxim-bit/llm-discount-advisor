"""Russian Markdown reports for legacy PoC and revised MVP-1."""
from datetime import datetime


def _fmt_role(role: dict | None) -> str:
    if not role:
        return "нет сравнимого кандидата"
    return (
        f"`{role.get('ranking_key') or '—'}`"
        f" / {role.get('provider') or 'провайдер не указан'}"
        f" / ${role.get('price') if role.get('price') is not None else '—'}"
        f" / score {role.get('score') if role.get('score') is not None else '—'}"
    )


def _render_mvp1(mvp1: dict) -> list[str]:
    decision = mvp1.get("decision_surface") or {}
    coverage = mvp1.get("task_cost_coverage") or {}
    counts = coverage.get("counts") or {}
    patch = mvp1.get("config_patch") or {}
    changes = mvp1.get("changes") or {}
    calibration = decision.get("discount_calibration") or {}
    lines = [
        "## Decision surface",
        "",
        f"Режим: `{decision.get('ranking_mode', 'unknown')}`.",
        "Primary price: **Avg Price Per 100 Requests** (`costPerRequest`), unit: `usd_per_100_requests`.",
        "Это operational metric OpenRouter Rankings, не `avg_cost_per_task`.",
        "",
        f"Discount calibration: `{calibration.get('status', 'unknown')}`; sample size: {calibration.get('sample_size', 20)}.",
        "Discount не умножается на observed `costPerRequest`; до подтверждения это только overlay/action signal.",
        "",
    ]
    for profile in decision.get("profiles", []):
        roles = profile.get("roles") or {}
        balanced = roles.get("balanced_default")
        lines.extend([
            f"### Профиль `{profile.get('profile')}`",
            "",
            f"Quality: `{profile.get('quality_metric')}`; floor: {profile.get('quality_floor', '—')}.",
            f"Candidates: {profile.get('candidate_count', 0)}; raw Pareto: {profile.get('raw_pareto_count', 0)}; stable Pareto: {profile.get('stable_pareto_count', 0)}.",
            f"- balanced default: {_fmt_role(balanced)}",
            f"- cost option: {_fmt_role(roles.get('cost_option'))}",
            f"- quality option: {_fmt_role(roles.get('quality_option'))}",
            "",
        ])
    lines.extend([
        "### Secondary evidence coverage",
        "",
        f"Families total: {counts.get('families_total', 0)}; uncovered: {counts.get('uncovered', 0)};",
        f"`worthy_candidate`: {counts.get('worthy_uncovered', 0)}; `likely_low_signal`: {counts.get('likely_low_signal_uncovered', 0)}.",
        "Benchmark `avg_cost_per_task` и session-cost остаются разными units и не входят в primary Pareto.",
        "",
        "### YAML patch preview",
        "",
        f"Status: `{patch.get('status', 'unknown')}`; requires confirmation: `{patch.get('requires_confirmation', True)}`.",
        "Конфигурация автоматически не изменялась.",
        "",
        "### Что изменилось",
        "",
        f"Status: `{changes.get('status', 'unknown')}`; events: {len(changes.get('events', []))}.",
        "",
    ])
    return lines


def render_report(shortlist: dict, snapshot: dict, rejected: dict, mvp1: dict | None = None) -> str:
    lines = [
        f"# LLM Discount Advisor — отчёт от {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "Decision-support для выбора модели и provider/variant в Hermes.",
        "",
        f"Legacy snapshot: **{snapshot.get('model_count', 0)}** строк каталога / **{snapshot.get('model_family_count', 0)}** семейств; после scope gate прошло **{snapshot.get('gated_count', 0)}** строк / **{snapshot.get('gated_unique_families', 0)}** семейств.",
        "",
    ]
    if mvp1:
        lines.extend(_render_mvp1(mvp1))
    lines.extend([
        "## Legacy shortlist",
        "",
    ])
    for profile in shortlist.get("profiles", []):
        lines += [f"### {profile['title']} (`{profile['profile']}`)", ""]
        for pick in profile.get("picks", []):
            discount = f", скидка {pick['discount']:.0%}" if pick.get("discount") else ""
            effort = pick.get("reasoning_default_effort") or "не указан"
            mandatory = "обязателен" if pick.get("reasoning_mandatory") else "можно отключить/не указан"
            lines.append(
                f"- **{pick['label']}** — `{pick['name']}` через {pick.get('provider') or 'провайдера не указано'}: "
                f"${pick['blended_price']:.4f}/1M, {pick['quality_metric']} {pick.get('quality') or 'нет'}{discount}. "
                f"Почему: {pick['reason']} Reasoning: `{effort}`, {mandatory}."
            )
        if not profile.get("picks"):
            lines.append("- Недостаточно кандидатов с объяснимыми данными.")
        lines.append("")
    lines += [
        "## Ограничения",
        "",
        "- `costPerRequest` — operational metric OpenRouter Rankings за 100 requests; это не универсальная стоимость пользовательской задачи.",
        "- `avg_cost_per_task` benchmark evidence и session-cost не смешиваются с primary ranking.",
        "- Discount не применяется вторично к `costPerRequest` до прохождения calibration gate.",
        "- Цена token view зависит от reasoning effort; эта MVP-1 версия показывает labels, но не измеряет расход при разных effort.",
        "- Если frontend Rankings schema ломается, normal decision surface не публикуется.",
        "",
        "Источник: OpenRouter public API и публичная frontend Rankings surface.",
        "",
    ]
    return "\n".join(lines)
