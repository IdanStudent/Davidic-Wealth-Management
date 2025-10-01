from datetime import datetime, timedelta
import math

# Simple astronomical approximation for sunset; for MVP use a rough heuristic.
# In production, integrate with a proper zmanim or Hebcal API.

def approximate_sunset(lat: float, lon: float, dt: datetime) -> datetime:
    # Very rough: assume sunset at 18:30 local; this is placeholder logic
    local = dt
    return local.replace(hour=18, minute=30, second=0, microsecond=0)


def is_shabbat_now(user) -> bool:
    now = datetime.now()
    # Friday sunset to Saturday nightfall (sunset + ~40m)
    sunset_fri = approximate_sunset(user.lat or 31.778, user.lon or 35.235, now)
    start = sunset_fri.replace(hour=18, minute=30)  # approximate
    end = start + timedelta(hours=25)  # ends around 19:30 Sat
    # If today is Friday after 16:00 treat as near-sunset start; if Saturday until ~20:00
    weekday = now.weekday()  # Mon=0 ... Sun=6
    if weekday == 4 and now >= start:
        return True
    if weekday == 5 and now <= end:
        return True
    return False
