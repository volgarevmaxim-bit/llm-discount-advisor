"""Explicit PoC configuration: no hidden ranking magic."""
from dataclasses import dataclass


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

    @property
    def ratio_label(self) -> str:
        return f"{self.blend_in}:{self.blend_out}"


PROFILES = (
    Profile("chat", "Быстрый ассистент", "intelligence", 55, 32_000, False, 3, 1),
    Profile("code", "Код", "coding", 60, 128_000, True, 3, 1),
    Profile("longdoc", "Длинные документы", "intelligence", 55, 200_000, False, 10, 1),
    Profile("bulk", "Массовая генерация", "intelligence", 45, 16_000, False, 1, 3),
)

PROFILE_BY_KEY = {p.key: p for p in PROFILES}
GATE_TOP_N = 20
GATE_DA_RANK = 7
GATE_DA_CATEGORIES = 6
GATE_MAX_AGE_DAYS = 180
MIN_UPTIME = 95.0
RELIABLE_UPTIME = 98.0
DEFAULT_BLEND_IN = 3
DEFAULT_BLEND_OUT = 1


def profile_blended(model: dict, profile: Profile) -> float:
    return (profile.blend_in * model["price_in"] + profile.blend_out * model["price_out"]) / (profile.blend_in + profile.blend_out)
