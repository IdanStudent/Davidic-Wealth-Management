from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.db import get_db
from ..schemas.finance import AccountCreate, AccountOut
from ..models.finance import Account, AccountType
from ..services.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Account).filter(Account.user_id == user.id).all()

@router.post("/", response_model=AccountOut)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if account_in.type not in [t.value for t in AccountType]:
        raise HTTPException(status_code=400, detail="Invalid account type")
    account = Account(
        user_id=user.id,
        name=account_in.name,
        type=AccountType(account_in.type),
        opening_balance=account_in.opening_balance,
        is_liability=account_in.is_liability,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"ok": True}
