from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from ..core.db import get_db
from ..services.deps import get_current_user
from ..schemas.finance import DebtPlanRequest, DebtPlan, DebtPayment

router = APIRouter()

def _month_add(ym: str, n: int) -> str:
    y, m = map(int, ym.split('-'))
    m += n
    y += (m - 1) // 12
    m = ((m - 1) % 12) + 1
    return f"{y:04d}-{m:02d}"

def _current_month() -> str:
    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"

@router.post('/plan', response_model=DebtPlan)
def generate_plan(req: DebtPlanRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Validate strategy
    strategy = req.strategy.lower()
    if strategy not in ("snowball", "avalanche"):
        raise HTTPException(status_code=400, detail="strategy must be snowball|avalanche")
    # Copy debts state
    debts = [
        {
            'id': d.id,
            'name': d.name,
            'balance': float(d.balance),
            'apr': float(d.apr_annual) / 100.0 if d.apr_annual > 1 else float(d.apr_annual),
            'min': float(d.min_payment),
            'due_day': d.due_day or 1,
        }
        for d in req.debts if d.balance > 0 and d.min_payment > 0 and d.apr_annual is not None
    ]
    if not debts:
        return DebtPlan(schedule=[], months_to_payoff=0, total_interest=0.0, strategy=strategy)

    # Order according to strategy
    if strategy == 'snowball':
        debts.sort(key=lambda x: x['balance'])
    else:  # avalanche
        debts.sort(key=lambda x: x['apr'], reverse=True)

    month_budget = max(0.0, float(req.monthly_budget)) + float(req.extra_payment or 0.0)
    schedule: list[DebtPayment] = []
    total_interest = 0.0
    month = _current_month()
    months_to_payoff = 0

    # Index rate changes by (debt_id, month_index)
    rate_changes = {}
    if req.rate_changes:
        for rc in req.rate_changes:
            try:
                rate_changes[(int(rc['debt_id']), int(rc['month_offset']))] = float(rc['apr_annual'])
            except Exception:
                continue
    # Safety cap to avoid infinite loops
    for month_index in range(0, 600):  # up to 50 years
        active = [d for d in debts if d['balance'] > 0.005]
        if not active:
            break
        months_to_payoff += 1
        # min payments first
        budget = month_budget
        # accrue and pay
        leftovers = 0.0
        for d in active:
            # apply rate change at this month if configured
            key = (d['id'], month_index)
            if key in rate_changes:
                new_apr = rate_changes[key]
                d['apr'] = float(new_apr) / 100.0 if new_apr > 1 else float(new_apr)
            # monthly interest
            monthly_rate = d['apr'] / 12.0
            interest = d['balance'] * monthly_rate
            total_interest += interest
            d['balance'] += interest
        # pay mins
        for d in active:
            pay = min(d['min'], d['balance'])
            d['balance'] -= pay
            budget -= pay
            principal = max(0.0, pay - (d['apr']/12.0)*d['balance'])  # approximate principal portion reporting
            schedule.append(DebtPayment(month=month, debt_id=d['id'], payment=pay, principal=principal, interest=pay-principal, balance_after=max(0.0, d['balance'])))
        # snowball payment to the first active per ordering
        if budget > 0 and active:
            target = active[0]
            extra = min(budget, target['balance'])
            if extra > 0:
                target['balance'] -= extra
                schedule.append(DebtPayment(month=month, debt_id=target['id'], payment=extra, principal=extra, interest=0.0, balance_after=max(0.0, target['balance'])))
    month = _month_add(month, 1)

    return DebtPlan(schedule=schedule, months_to_payoff=months_to_payoff, total_interest=round(total_interest, 2), strategy=strategy)
