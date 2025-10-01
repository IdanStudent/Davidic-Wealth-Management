from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.db import get_db
from ..schemas.finance import TransactionCreate, TransactionOut
from ..models.finance import Transaction, Account, Category, AccountType, CategoryType
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
    # detect income category and perform Maaser split
    created_tx = None
    if tx_in.category_id:
        cat = db.query(Category).filter(Category.id == tx_in.category_id, Category.user_id == user.id).first()
        if cat and cat.type == CategoryType.INCOME:
            # maaser percentage from user settings (default 0.10)
            maaser_pct = getattr(user, 'maaser_pct', 0.10) or 0.10
            maaser_amount = round(float(tx_in.amount) * maaser_pct, 2)
            main_amount = round(float(tx_in.amount) - maaser_amount, 2)

            # create main income transaction (reduced amount)
            tx_main = Transaction(user_id=user.id, account_id=tx_in.account_id, category_id=tx_in.category_id, date=tx_in.date, amount=main_amount, note=(tx_in.note or '') + ' (after maaser)')
            db.add(tx_main)
            db.commit()
            db.refresh(tx_main)

            # find or create Maaser account
            maaser_acc = db.query(Account).filter(Account.user_id == user.id, Account.name == 'Maaser').first()
            if not maaser_acc:
                maaser_acc = Account(user_id=user.id, name='Maaser', type=AccountType.SAVINGS, opening_balance=0.0)
                db.add(maaser_acc)
                db.commit()
                db.refresh(maaser_acc)

            # create transfer transaction to maaser account (negative amount on main? we'll represent as positive on maaser account)
            tx_transfer = Transaction(user_id=user.id, account_id=maaser_acc.id, category_id=None, date=tx_in.date, amount=maaser_amount, note='Auto Maaser (10%)', is_transfer=True, counterparty_account_id=tx_main.account_id)
            db.add(tx_transfer)
            db.commit()
            db.refresh(tx_transfer)

            # link counterparty on main (optional)
            tx_main.is_transfer = False
            db.commit()
            created_tx = tx_main
        else:
            # normal transaction
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
            created_tx = tx
    else:
        tx = Transaction(
            user_id=user.id,
            account_id=tx_in.account_id,
            category_id=None,
            date=tx_in.date,
            amount=tx_in.amount,
            note=tx_in.note or "",
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        created_tx = tx

    return created_tx

@router.delete("/{tx_id}", dependencies=[Depends(enforce_shabbat_readonly)])
def delete_transaction(tx_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return {"ok": True}
