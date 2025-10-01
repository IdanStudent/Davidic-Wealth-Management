from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.db import get_db
from ..schemas.finance import TransactionCreate, TransactionOut
from ..models.finance import Transaction, Account, Category
from ..services.deps import get_current_user, enforce_shabbat_readonly

router = APIRouter()

@router.get("/", response_model=List[TransactionOut])
def list_transactions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.date.desc()).all()

@router.post("/", response_model=TransactionOut, dependencies=[Depends(enforce_shabbat_readonly)])
def create_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = db.query(Account).filter(Account.id == tx_in.account_id, Account.user_id == user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if tx_in.category_id:
        category = db.query(Category).filter(Category.id == tx_in.category_id, Category.user_id == user.id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    tx = Transaction(
        user_id=user.id,
        account_id=tx_in.account_id,
        category_id=tx_in.category_id,
        date=tx_in.date,
        amount=tx_in.amount,
        note=tx_in.note or "",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

@router.delete("/{tx_id}", dependencies=[Depends(enforce_shabbat_readonly)])
def delete_transaction(tx_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return {"ok": True}
