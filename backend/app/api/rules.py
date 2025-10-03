from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..services.deps import get_current_user
from ..models.finance import CategoryRule, Category
from ..schemas.finance import CategoryRuleIn, CategoryRuleOut
from typing import List

router = APIRouter()

@router.get('/', response_model=List[CategoryRuleOut])
def list_rules(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(CategoryRule).filter(CategoryRule.user_id == user.id).all()

@router.post('/', response_model=CategoryRuleOut)
def create_rule(rule_in: CategoryRuleIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == rule_in.category_id, Category.user_id == user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail='Category not found')
    r = CategoryRule(
        user_id=user.id,
        pattern=rule_in.pattern,
        category_id=rule_in.category_id,
        min_amount=rule_in.min_amount,
        max_amount=rule_in.max_amount,
        case_sensitive=bool(rule_in.case_sensitive),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.delete('/{rule_id}')
def delete_rule(rule_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = db.query(CategoryRule).filter(CategoryRule.id == rule_id, CategoryRule.user_id == user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail='Rule not found')
    db.delete(r)
    db.commit()
    return {"ok": True}
