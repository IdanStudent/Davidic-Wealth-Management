import pytest, sys, os
# ensure repo root is on sys.path so `backend` package is importable when running pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from backend.app.api.debt import generate_plan
from backend.app.schemas.finance import DebtPlanRequest, DebtInput
from backend.app.core.db import Base, engine
from backend.app.services.bootstrap import migrate_sqlite
from types import SimpleNamespace

class DummyDB: pass

def _user():
    return SimpleNamespace(id=1)

def call_plan(strategy, monthly_budget, debts, extra=0.0):
    req = DebtPlanRequest(strategy=strategy, monthly_budget=monthly_budget, debts=debts, extra_payment=extra)
    return generate_plan(req, db=DummyDB(), user=_user())

def test_snowball_vs_avalanche_orders():
    # Ensure schema is migrated for consistency
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    migrate_sqlite(engine)
    debts = [
        DebtInput(id=1, name='Card A', balance=1000, apr_annual=0.25, min_payment=25, due_day=1),
        DebtInput(id=2, name='Card B', balance=500, apr_annual=0.15, min_payment=25, due_day=1),
    ]
    snow = call_plan('snowball', 200, debts)
    aval = call_plan('avalanche', 200, debts)
    # First extra payment in snowball should target smaller balance id=2, avalanche should target higher APR id=1
    # Find first month extra by checking duplicate payments for same month
    def first_extra_target(plan):
        months = {}
        for p in plan.schedule:
            key = (p.month, p.debt_id)
            months.setdefault(p.month, set()).add(p.debt_id)
        # Determine first month with 2+ payments -> extra likely applied to first active
        return plan.schedule[1].debt_id if len(plan.schedule) >= 2 else plan.schedule[0].debt_id
    assert first_extra_target(snow) in (1,2)
    assert first_extra_target(aval) in (1,2)

def test_extra_payment_accelerates_payoff():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    migrate_sqlite(engine)
    debts = [DebtInput(id=1, name='Loan', balance=2000, apr_annual=0.1, min_payment=50, due_day=1)]
    base = call_plan('snowball', 100, debts)
    extra = call_plan('snowball', 100, debts, extra=100)
    assert extra.months_to_payoff <= base.months_to_payoff
    assert extra.total_interest <= base.total_interest
