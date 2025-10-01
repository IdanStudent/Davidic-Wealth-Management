from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Dict, Any
from ..core.db import get_db
from ..models.finance import Transaction, Account, Category, Budget, BudgetItem, CategoryType
from ..models.finance import Investment, InvestmentTransaction
from ..services.deps import get_current_user
from ..services.export import export_month_csv, export_month_pdf
from typing import Optional, List
from sqlalchemy import func

router = APIRouter()

@router.get("/monthly")
def monthly_summary(year: int, month: int, db: Session = Depends(get_db), user=Depends(get_current_user)) -> Dict[str, Any]:
    start = date(year, month, 1)
    end = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)

    # Exclude transfer transactions from income/expense totals
    q = db.query(Transaction).filter(Transaction.user_id == user.id, Transaction.is_transfer == False, Transaction.date >= start, Transaction.date < end)
    income = 0.0
    expenses = 0.0
    for tx in q:
        if tx.category and tx.category.type == CategoryType.INCOME:
            income += tx.amount
        else:
            expenses += tx.amount
    savings = income - expenses

    # budget used per category
    budget_items = (
        db.query(BudgetItem, Category)
        .join(Budget, BudgetItem.budget_id == Budget.id)
        .join(Category, BudgetItem.category_id == Category.id)
        .filter(Budget.user_id == user.id, Budget.month == f"{year:04d}-{month:02d}")
        .all()
    )

    spending_by_category = (
        db.query(Category.name, func.sum(Transaction.amount))
        .join(Category, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == user.id, Transaction.is_transfer == False, Transaction.date >= start, Transaction.date < end)
        .group_by(Category.name)
        .all()
    )
    spending = {name: float(total or 0) for name, total in spending_by_category}

    # Maaser total: sum of transactions credited to the Maaser account in this month
    maaser_acc = db.query(Account).filter(Account.user_id == user.id, Account.name == 'Maaser').first()
    maaser_total = 0.0
    if maaser_acc:
        maaser_total = float(db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user.id, Transaction.account_id == maaser_acc.id, Transaction.date >= start, Transaction.date < end).scalar() or 0.0)

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "spending": spending,
        "maaser": maaser_total,
        "budget": [
            {"category": c.name, "limit": float(bi.limit)} for bi, c in budget_items
        ],
    }

@router.get("/export/csv")
def export_csv(year: int, month: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    content, filename = export_month_csv(db, user.id, year, month)
    return {"filename": filename, "content": content}

@router.get("/export/pdf")
def export_pdf(year: int, month: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    content_b64, filename = export_month_pdf(db, user.id, year, month)
    return {"filename": filename, "content_b64": content_b64}


@router.get('/networth')
def networth(months: Optional[int] = 12, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Return current assets, liabilities, net worth and a monthly history for the past `months` months (default 12)."""
    if months is None or months <= 0:
        months = 12
    today = date.today()

    # load accounts once
    accounts = db.query(Account).filter(Account.user_id == user.id).all()

    # current totals (use same logic as list_accounts)
    assets_total = 0.0
    liabilities_total = 0.0
    accounts_out = []
    for a in accounts:
        tx_count = db.query(func.count(Transaction.id)).filter(Transaction.account_id == a.id, Transaction.user_id == user.id).scalar() or 0
        if tx_count and tx_count > 0:
            tx_sum = db.query(func.sum(Transaction.amount)).filter(Transaction.account_id == a.id, Transaction.user_id == user.id).scalar() or 0.0
            balance = float(tx_sum)
        else:
            balance = float(a.opening_balance or 0.0)
        accounts_out.append({"id": a.id, "name": a.name, "type": a.type.value if hasattr(a.type, 'value') else str(a.type), "is_liability": bool(a.is_liability), "balance": balance})
        if a.is_liability:
            liabilities_total += balance
        else:
            assets_total += balance

    # investments valuation: compute holdings and value using latest unit_price from investment transactions
    investments_out = []
    invs = db.query(Investment).filter(Investment.user_id == user.id).all()
    inv_assets_value = 0.0
    for inv in invs:
        # sum buy quantities as positive, sell quantities as negative
        qty = 0.0
        latest_price = None
        its = db.query(InvestmentTransaction).filter(InvestmentTransaction.investment_id == inv.id, InvestmentTransaction.user_id == user.id).order_by(InvestmentTransaction.date.asc(), InvestmentTransaction.id.asc()).all()
        for it in its:
            if it.type == 'buy':
                qty += it.quantity
            elif it.type == 'sell':
                qty -= it.quantity
            latest_price = it.unit_price if it.unit_price is not None else latest_price
        value = float(qty * (latest_price or 0.0))
        if value:
            inv_assets_value += value
        investments_out.append({"investment_id": inv.id, "symbol": inv.symbol, "name": inv.name, "quantity": qty, "price": latest_price, "value": value})

    # include investment valuations in assets_total
    assets_total += inv_assets_value

    # monthly history: compute month-ends going back `months` months
    history: List[dict] = []
    # helper to get year/month stepping
    def prev_month(year, month):
        if month == 1:
            return year - 1, 12
        return year, month - 1

    # build list of month_end dates from oldest to newest
    year = today.year
    month = today.month
    month_ends = []
    for i in range(months):
        # compute year/month for the current step backwards
        y, m = year, month
        for _ in range(i):
            y, m = prev_month(y, m)
        # compute month end as first of next month minus one day
        if m == 12:
            next_year, next_month = y + 1, 1
        else:
            next_year, next_month = y, m + 1
        next_first = date(next_year, next_month, 1)
        # month_end is next_first - 1 day
        month_end = next_first - (date.resolution)
        # date.resolution is a timedelta of one microsecond, so to get one day subtract a day
        # safer: compute last day by using day=1 of next month and subtract one day
        from datetime import timedelta
        month_end = next_first - timedelta(days=1)
        month_ends.append((y, m, month_end))

    # month_ends is recent-first reversed to oldest-first
    month_ends = list(reversed(month_ends))

    for y, m, month_end in month_ends:
        assets_m = 0.0
        liabilities_m = 0.0
        for a in accounts:
            tx_count = db.query(func.count(Transaction.id)).filter(Transaction.account_id == a.id, Transaction.user_id == user.id, Transaction.date <= month_end).scalar() or 0
            if tx_count and tx_count > 0:
                tx_sum = db.query(func.sum(Transaction.amount)).filter(Transaction.account_id == a.id, Transaction.user_id == user.id, Transaction.date <= month_end).scalar() or 0.0
                balance = float(tx_sum)
            else:
                balance = float(a.opening_balance or 0.0)
            if a.is_liability:
                liabilities_m += balance
            else:
                assets_m += balance
        history.append({"month": f"{y:04d}-{m:02d}", "assets": assets_m, "liabilities": liabilities_m, "net_worth": assets_m - liabilities_m})

    return {
        "assets": assets_total,
        "liabilities": liabilities_total,
        "net_worth": assets_total - liabilities_total,
        "accounts": accounts_out,
        "investments": investments_out,
        "history": history,
    }
