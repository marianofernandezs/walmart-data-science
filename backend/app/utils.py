from __future__ import annotations

from datetime import date
from typing import Iterable


CATEGORY_BASE_DEMAND = {
    "FOODS": 36.0,
    "HOBBIES": 14.0,
    "HOUSEHOLD": 22.0,
}


def clamp_non_negative(value: float) -> float:
    return max(0.0, float(value))


def state_from_store(store_id: str) -> str:
    prefix = store_id.split("_", 1)[0].upper()
    return prefix if prefix in {"CA", "TX", "WI"} else "CA"


def dept_from_sku_category(sku: str, category: str) -> str:
    if "_" in sku:
        bits = sku.split("_")
        if len(bits) >= 2:
            return f"{category}_{bits[1]}"
    return f"{category}_1"


def category_baseline(category: str) -> float:
    return CATEGORY_BASE_DEMAND.get(category.upper(), 18.0)


def seeded_noise(seed_text: str, day_offset: int) -> float:
    raw = sum(ord(char) for char in f"{seed_text}:{day_offset}")
    return ((raw % 11) - 5) / 25.0


def safe_round_list(values: Iterable[float], digits: int = 2) -> list[float]:
    return [round(float(value), digits) for value in values]


def seasonality_multiplier(target_date: date) -> float:
    weekday = target_date.weekday()
    if weekday >= 5:
        return 1.12
    if weekday == 4:
        return 1.06
    return 0.98 if weekday == 1 else 1.0
