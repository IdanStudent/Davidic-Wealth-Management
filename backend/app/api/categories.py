from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from ..core.db import get_db
from ..schemas.finance import CategoryCreate, CategoryOut, CategoryUpdate
from ..models.finance import Category, CategoryType, Transaction, Budget, BudgetItem
from ..services.deps import get_current_user
from ..services.bootstrap import ensure_default_categories

router = APIRouter()

@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    ensure_default_categories(db, user.id)
    return db.query(Category).filter(Category.user_id == user.id).all()

@router.post("/", response_model=CategoryOut)
def create_category(cat_in: CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    typ = CategoryType(cat_in.type)
    c = Category(user_id=user.id, name=cat_in.name, type=typ, icon=cat_in.icon or "")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, cat_in: CategoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    # For built-in categories, restrict type changes
    if cat.is_builtin and cat_in.type is not None and cat_in.type != cat.type.value:
        raise HTTPException(status_code=400, detail="Cannot change type of built-in category")
    if cat_in.name is not None:
        cat.name = cat_in.name
    if cat_in.icon is not None:
        cat.icon = cat_in.icon
    if cat_in.type is not None:
        cat.type = CategoryType(cat_in.type)
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.is_builtin:
        raise HTTPException(status_code=400, detail="Cannot delete built-in category")
    # Prevent deletion if referenced
    tx_count = (
        db.query(func.count()).select_from(Transaction)
        .filter(Transaction.user_id == user.id, Transaction.category_id == category_id)
        .scalar()
    )
    bi_count = (
        db.query(func.count()).select_from(BudgetItem)
        .join(Budget, BudgetItem.budget_id == Budget.id)
        .filter(Budget.user_id == user.id, BudgetItem.category_id == category_id)
        .scalar()
    )
    if (tx_count or 0) > 0 or (bi_count or 0) > 0:
        raise HTTPException(status_code=400, detail="Category is in use and cannot be deleted")
    db.delete(cat)
    db.commit()
    return {"ok": True}
