from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.db import get_db
from ..schemas.finance import TransactionCreate, TransactionOut
from ..models.finance import Transaction, Account, Category, AccountType, CategoryType, CategoryRule
from ..services.deps import get_current_user, enforce_shabbat_readonly
from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional, Any


class TransferIn(BaseModel):
    from_account_id: int
    to_account_id: int
    date: date
    amount: float
    note: str | None = None

    @classmethod
    def __get_validators__(cls):
        yield cls._validate_date

    @classmethod
    def _validate_date(cls, values):
        # pydantic V1 style validator compatibility: ensure date field is a python date
        d = values.get('date')
        if d is None:
            return values
        if isinstance(d, date):
            return values
        try:
            values['date'] = date.fromisoformat(str(d))
            return values
        except Exception:
            raise ValueError('Invalid date format')

router = APIRouter()


class TransactionUpdate(BaseModel):
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    date: Optional[Any] = None
    amount: Optional[float] = None
    note: Optional[str] = None


class ImportRow(BaseModel):
    account_id: int
    date: Any
    amount: float
    note: Optional[str] = None
    category_id: Optional[int] = None

    @field_validator('date', mode='before')
    def _coerce_date(cls, v):
        if v is None:
            return v
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(str(v))
        except Exception:
            raise ValueError('Invalid date format')


class ImportPayload(BaseModel):
    rows: list[ImportRow]

@router.get("/", response_model=List[TransactionOut])
def list_transactions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.date.desc()).all()


@router.get('/recent', response_model=List[TransactionOut])
def recent_transactions(limit: int = 20, account_id: int | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Transaction).filter(Transaction.user_id == user.id)
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    q = q.order_by(Transaction.date.desc(), Transaction.id.desc()).limit(limit)
    return q.all()

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
            # treat incoming amount as magnitude (user supplies positive number)
            incoming = abs(float(tx_in.amount))
            maaser_amount = round(incoming * maaser_pct, 2)
            main_amount = round(incoming - maaser_amount, 2)

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
            # normal transaction: sign amount by category type
            amt = abs(float(tx_in.amount))
            if cat.type == CategoryType.EXPENSE:
                signed = -amt
            else:
                # fallback: treat as income/other positive
                signed = amt
            tx = Transaction(
                user_id=user.id,
                account_id=tx_in.account_id,
                category_id=tx_in.category_id,
                date=tx_in.date,
                amount=signed,
                note=tx_in.note or "",
            )
            db.add(tx)
            db.commit()
            db.refresh(tx)
            created_tx = tx
    else:
        # No category provided: try rules-based categorization (simple substring + amount bounds)
        assigned_category_id = None
        note_text = (tx_in.note or "")
        rules = db.query(CategoryRule).filter(CategoryRule.user_id == user.id).all()
        for r in rules:
            txt = note_text if r.case_sensitive else note_text.lower()
            pat = r.pattern if r.case_sensitive else (r.pattern or '').lower()
            if pat and pat in txt:
                amt = float(tx_in.amount)
                if (r.min_amount is not None and amt < r.min_amount):
                    continue
                if (r.max_amount is not None and amt > r.max_amount):
                    continue
                assigned_category_id = r.category_id
                break
        if assigned_category_id:
            cat = db.query(Category).filter(Category.id == assigned_category_id, Category.user_id == user.id).first()
            if cat:
                magnitude = abs(float(tx_in.amount))
                signed = -magnitude if cat.type == CategoryType.EXPENSE else magnitude
                tx = Transaction(
                    user_id=user.id,
                    account_id=tx_in.account_id,
                    category_id=assigned_category_id,
                    date=tx_in.date,
                    amount=signed,
                    note=tx_in.note or "",
                )
                db.add(tx)
                db.commit()
                db.refresh(tx)
                created_tx = tx
                return created_tx
        # Fallback: preserve sign as supplied by client
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


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.patch("/{tx_id}", response_model=TransactionOut, dependencies=[Depends(enforce_shabbat_readonly)])
def update_transaction(tx_id: int, upd: TransactionUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # update simple fields if present
    if upd.account_id is not None:
        acc = db.query(Account).filter(Account.id == upd.account_id, Account.user_id == user.id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
        tx.account_id = upd.account_id
    if upd.date is not None:
        # accept ISO date string from client; coerce to datetime.date for DB
        if isinstance(upd.date, date):
            tx.date = upd.date
        else:
            try:
                tx.date = date.fromisoformat(str(upd.date))
            except Exception:
                raise HTTPException(status_code=400, detail='Invalid date format')
    if upd.note is not None:
        tx.note = upd.note

    # handle category/amount together to ensure sign correctness
    if upd.category_id is not None:
        if upd.category_id:
            cat = db.query(Category).filter(Category.id == upd.category_id, Category.user_id == user.id).first()
            if not cat:
                raise HTTPException(status_code=404, detail="Category not found")
            tx.category_id = upd.category_id
            # if amount provided, use it, else use existing magnitude
            magnitude = abs(float(upd.amount)) if (upd.amount is not None) else abs(float(tx.amount))
            if cat.type == CategoryType.EXPENSE:
                tx.amount = -magnitude
            else:
                tx.amount = magnitude
        else:
            # clearing category - preserve sign from provided amount if present
            tx.category_id = None
            if upd.amount is not None:
                tx.amount = upd.amount

    elif upd.amount is not None:
        # no category change — just update numeric amount (assume caller sends intended signed or unsigned as needed)
        tx.amount = upd.amount

    db.commit()
    db.refresh(tx)
    return tx


@router.post('/transfer', response_model=TransactionOut, dependencies=[Depends(enforce_shabbat_readonly)])
def transfer(t: TransferIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if t.from_account_id == t.to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")
    from_acc = db.query(Account).filter(Account.id == t.from_account_id, Account.user_id == user.id).first()
    to_acc = db.query(Account).filter(Account.id == t.to_account_id, Account.user_id == user.id).first()
    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # ensure date is a Python date object (SQLite Date column requires date)
    tx_date = t.date if isinstance(t.date, date) else date.fromisoformat(str(t.date))

    # create withdrawal on from_acc (negative amount)
    tx_from = Transaction(user_id=user.id, account_id=from_acc.id, category_id=None, date=tx_date, amount=-abs(float(t.amount)), note=t.note or 'Transfer out', is_transfer=True, counterparty_account_id=to_acc.id)
    db.add(tx_from)
    db.commit()
    db.refresh(tx_from)

    # create deposit on to_acc (positive amount)
    tx_to = Transaction(user_id=user.id, account_id=to_acc.id, category_id=None, date=tx_date, amount=abs(float(t.amount)), note=t.note or 'Transfer in', is_transfer=True, counterparty_account_id=from_acc.id)
    db.add(tx_to)
    db.commit()
    db.refresh(tx_to)

    return tx_from


@router.post('/import')
def import_transactions(payload: ImportPayload, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Bulk import transactions via simple JSON rows. Amounts should be positive; signs are applied by category type when provided,
    or left as-is (positive) when no category is given (rules may assign)."""
    imported = 0
    errors: list[dict] = []
    for idx, row in enumerate(payload.rows):
        try:
            acc = db.query(Account).filter(Account.id == row.account_id, Account.user_id == user.id).first()
            if not acc:
                raise HTTPException(status_code=400, detail=f"Row {idx}: Account not found")
            assigned_category_id = None
            cat = None
            if row.category_id:
                cat = db.query(Category).filter(Category.id == row.category_id, Category.user_id == user.id).first()
                if not cat:
                    raise HTTPException(status_code=400, detail=f"Row {idx}: Category not found")
                assigned_category_id = row.category_id
            else:
                # try rules
                note_text = row.note or ""
                rules = db.query(CategoryRule).filter(CategoryRule.user_id == user.id).all()
                for r in rules:
                    txt = note_text if r.case_sensitive else note_text.lower()
                    pat = r.pattern if r.case_sensitive else (r.pattern or '').lower()
                    if pat and pat in txt:
                        amt = float(row.amount)
                        if (r.min_amount is not None and amt < r.min_amount):
                            continue
                        if (r.max_amount is not None and amt > r.max_amount):
                            continue
                        assigned_category_id = r.category_id
                        cat = db.query(Category).filter(Category.id == assigned_category_id, Category.user_id == user.id).first()
                        break
            # compute signed amount
            magnitude = abs(float(row.amount))
            if cat:
                signed = -magnitude if cat.type == CategoryType.EXPENSE else magnitude
            else:
                # leave positive magnitude for uncategorized
                signed = magnitude
            tx = Transaction(
                user_id=user.id,
                account_id=row.account_id,
                category_id=assigned_category_id,
                date=row.date if isinstance(row.date, date) else date.fromisoformat(str(row.date)),
                amount=signed,
                note=row.note or "",
            )
            db.add(tx)
            imported += 1
        except HTTPException as he:
            errors.append({"index": idx, "detail": he.detail})
        except Exception as e:
            errors.append({"index": idx, "detail": str(e)})
    db.commit()
    return {"imported": imported, "errors": errors}
