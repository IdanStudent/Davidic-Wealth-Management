from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Dict, Any
from ..core.db import get_db
from ..models.finance import Transaction, Account, Category, Budget, BudgetItem, CategoryType
from ..services.deps import get_current_user
from ..services.export import export_month_csv, export_month_pdf

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
