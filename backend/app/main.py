from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import auth, accounts, transactions, budgets, reports, goals, utils, categories, investments, connections
from .core.db import Base, engine, init_db
# ensure models are imported before create_all
from .models import user as _user_models  # noqa: F401
from .models import finance as _finance_models  # noqa: F401
from .models import security as _security_models  # noqa: F401
from .models import connections as _connections_models  # noqa: F401

app = FastAPI(title="Malka Money API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
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

@app.get("/")
async def root():
    return {"message": "Shalom! Malka Money API is running."}
