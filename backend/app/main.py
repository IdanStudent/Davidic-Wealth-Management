from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from slowapi.middleware import SlowAPIMiddleware
from .core.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .core.config import settings
from .api import auth, accounts, transactions, budgets, reports, goals, utils, categories, investments, connections, rules, debt
from .core.db import Base, engine, init_db
# ensure models are imported before create_all
from .models import user as _user_models  # noqa: F401
from .models import finance as _finance_models  # noqa: F401
from .models import security as _security_models  # noqa: F401
from .models import connections as _connections_models  # noqa: F401

app = FastAPI(title="Malka Money API", version="0.1.0")

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

def _split_csv(val: str) -> list[str]:
    return [v.strip() for v in (val or "").split(",") if v.strip()]

# Security-related middlewares
origins = _split_csv(settings.BACKEND_CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or [settings.BACKEND_CORS_ORIGINS] or ["https://davidic-wealth-management-3.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hosts = _split_csv(settings.ALLOWED_HOSTS)
if hosts and hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

if settings.HTTPS_REDIRECT:
    app.add_middleware(HTTPSRedirectMiddleware)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Basic security headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    # HSTS only when HTTPS is enforced
    if settings.HTTPS_REDIRECT:
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
    return response

@app.on_event("startup")
async def on_startup():
    # Refuse to boot with default secret in production
    if settings.ENV.lower() == "prod" and settings.SECRET_KEY == "change-me":
        raise RuntimeError("SECURITY: SECRET_KEY must be set to a strong value in production")
    Base.metadata.create_all(bind=engine)
    await init_db()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) 
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"]) 
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"]) 
app.include_router(budgets.router, prefix="/api/budgets", tags=["budgets"]) 
app.include_router(reports.router, prefix="/api/reports", tags=["reports"]) 
app.include_router(goals.router, prefix="/api/goals", tags=["goals"]) 
app.include_router(utils.router, prefix="/api/utils", tags=["utils"]) 
app.include_router(categories.router, prefix="/api/categories", tags=["categories"]) 
app.include_router(investments.router, prefix="/api/investments", tags=["investments"]) 
app.include_router(connections.router, prefix="/api/connections", tags=["connections"]) 
app.include_router(rules.router, prefix="/api/rules", tags=["rules"]) 
app.include_router(debt.router, prefix="/api/debt", tags=["debt"]) 

@app.get("/")
async def root():
    return {"message": "Shalom! Malka Money API is running."}
