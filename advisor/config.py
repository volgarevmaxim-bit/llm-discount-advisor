"""Explicit MVP-1 profile contracts."""
from dataclasses import dataclass


MIN_UPTIME = 95.0
RELIABLE_UPTIME = 98.0
DEFAULT_BLEND_IN = 3
DEFAULT_BLEND_OUT = 1


@dataclass(frozen=True)
class Profile:
    key: str
    title: str
    quality_metric: str
    q_min: float
    min_context: int
    needs_tools: bool
    blend_in: int
    blend_out: int
    max_cards: int = 6
    price_metric: str = "costPerRequest"
    price_unit: str = "usd_per_100_requests"
    quality_label: str = ""
    requires_tools: bool = False
    fallback_policy: str = "show_token_price_only"

    def __post_init__(self):
        if not self.quality_label:
            object.__setattr__(self, "quality_label", {
                "intelligence": "Intelligence Index Score",
                "coding": "Coding Index Score",
                "agentic": "Agentic Index Score",
            }[self.quality_metric])
        if not self.requires_tools:
            object.__setattr__(self, "requires_tools", self.needs_tools)

    @property
    def min_uptime(self) -> float:
        return MIN_UPTIME

    @property
    def ratio_label(self) -> str:
        return f"{self.blend_in}:{self.blend_out}"


PROFILES = (
    Profile("chat", "Быстрый ассистент", "intelligence", 55, 32_000, False, 3, 1),
    Profile("code", "Код", "coding", 60, 128_000, True, 3, 1),
    Profile("agentic", "Агентный workflow", "agentic", 45, 128_000, True, 3, 1),
    Profile("longdoc", "Длинные документы", "intelligence", 55, 200_000, False, 10, 1),
    Profile("bulk", "Массовая генерация", "intelligence", 45, 16_000, False, 1, 3),
)

PROFILE_BY_KEY = {p.key: p for p in PROFILES}
GATE_TOP_N = 20
GATE_DA_RANK = 7
GATE_DA_CATEGORIES = 6
GATE_MAX_AGE_DAYS = 180


def profile_blended(model: dict, profile: Profile) -> float:
    return (profile.blend_in * model["price_in"] + profile.blend_out * model["price_out"]) / (profile.blend_in + profile.blend_out)
