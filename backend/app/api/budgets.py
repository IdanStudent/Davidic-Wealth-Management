from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.db import get_db
from ..schemas.finance import BudgetCreate, BudgetOut
from ..models.finance import Budget, BudgetItem, Category
from ..services.deps import get_current_user, enforce_shabbat_readonly

router = APIRouter()

@router.get("/", response_model=List[BudgetOut])
def list_budgets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    return budgets

@router.post("/", response_model=BudgetOut, dependencies=[Depends(enforce_shabbat_readonly)])
def create_budget(budget_in: BudgetCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    b = Budget(user_id=user.id, month=budget_in.month)
    db.add(b)
    db.flush()
    for item in budget_in.items:
        # ensure category belongs to user
        cat = db.query(Category).filter(Category.id == item.category_id, Category.user_id == user.id).first()
        if not cat:
            raise HTTPException(status_code=404, detail=f"Category {item.category_id} not found")
        db.add(BudgetItem(
            budget_id=b.id,
            category_id=item.category_id,
            limit=item.limit,
            item_type=(item.item_type or "fixed"),
            tolerance_pct=(item.tolerance_pct if item.tolerance_pct is not None else 0.15),
            window_months=(item.window_months if item.window_months is not None else 3),
        ))
    db.commit()
    db.refresh(b)
    return b
