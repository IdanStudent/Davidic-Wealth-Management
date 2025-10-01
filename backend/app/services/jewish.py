from typing import Dict, Any
from datetime import date


def maaser_from_income(amount: float) -> float:
    # 10% tithe
    return round(amount * 0.10, 2)


def get_holidays(year: int) -> Dict[str, Any]:
    # Minimal stub data; integrate Hebcal later
    # Return a few key holidays with Gregorian placeholders
    return {
        "year": year,
        "holidays": [
            {"name": "Rosh Hashanah", "approx": f"{year}-10-03"},
            {"name": "Yom Kippur", "approx": f"{year}-10-12"},
            {"name": "Sukkot", "approx": f"{year}-10-17"},
            {"name": "Chanukah", "approx": f"{year}-12-15"},
            {"name": "Purim", "approx": f"{year}-03-17"},
            {"name": "Pesach", "approx": f"{year}-04-13"},
            {"name": "Shavuot", "approx": f"{year}-06-02"},
        ]
    }
