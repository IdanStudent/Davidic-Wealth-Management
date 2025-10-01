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

    q = db.query(Transaction).filter(Transaction.user_id == user.id, Transaction.date >= start, Transaction.date < end)
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
        .filter(Transaction.user_id == user.id, Transaction.date >= start, Transaction.date < end)
        .group_by(Category.name)
        .all()
    )
    spending = {name: float(total or 0) for name, total in spending_by_category}

    return {
        "income": income,
        "expenses": expenses,
        "savings": savings,
        "spending": spending,
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
