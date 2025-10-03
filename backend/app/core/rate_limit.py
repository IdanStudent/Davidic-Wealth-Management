from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

# Global limiter instance used across the app
limiter = Limiter(key_func=get_remote_address, default_limits=[])

def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too Many Requests", "error": str(exc)}
    )
