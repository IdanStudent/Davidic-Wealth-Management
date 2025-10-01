from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..core.db import get_db
from ..schemas.finance import AccountCreate, AccountOut
from ..models.finance import Account, AccountType, Transaction, Category
from datetime import date
from ..models.finance import Transaction, Category
from ..services.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AccountOut])
def list_accounts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    # compute balance per account: opening_balance + sum(transactions.amount) (include transfers as they are stored on accounts)
    out = []
    for a in accounts:
        tx_sum = db.query(func.sum(Transaction.amount)).filter(Transaction.account_id == a.id, Transaction.user_id == user.id).scalar() or 0.0
        balance = float((a.opening_balance or 0.0) + (tx_sum or 0.0))
        ao = AccountOut.from_orm(a)
        ao.balance = balance
        out.append(ao)
    return out

@router.post("/", response_model=AccountOut)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if account_in.type not in [t.value for t in AccountType]:
        raise HTTPException(status_code=400, detail="Invalid account type")
    a = Account(
        user_id=user.id,
        name=account_in.name,
        type=AccountType(account_in.type),
        opening_balance=account_in.opening_balance,
        is_liability=account_in.is_liability,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    # Create opening transaction if opening_balance != 0
    if account_in.opening_balance and float(account_in.opening_balance) != 0.0:
        opening_tx = Transaction(user_id=user.id, account_id=a.id, date=date.today(), amount=float(account_in.opening_balance), note='Opening balance')
        db.add(opening_tx)
        db.commit()
    # ensure Maaser account exists for user
    maaser = db.query(Account).filter(Account.user_id == user.id, Account.name == 'Maaser').first()
    if not maaser:
        ma = Account(user_id=user.id, name='Maaser', type=AccountType.SAVINGS, opening_balance=0.0, is_liability=False)
        db.add(ma)
        db.commit()
    return a

@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"ok": True}
