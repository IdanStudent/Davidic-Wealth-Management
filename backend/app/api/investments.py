from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.db import get_db
from ..schemas.finance import InvestmentCreate, InvestmentOut, InvestmentTransactionCreate, InvestmentTransactionOut
from ..models.finance import Investment, InvestmentTransaction, Account
from ..services.deps import get_current_user, enforce_shabbat_readonly
from sqlalchemy import func
router = APIRouter()


@router.get('/holdings')
def holdings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    invs = db.query(Investment).filter(Investment.user_id == user.id).all()
    out = []
    for inv in invs:
        qsum = db.query(func.sum(InvestmentTransaction.quantity)).filter(InvestmentTransaction.investment_id == inv.id, InvestmentTransaction.user_id == user.id).scalar() or 0.0
        buy_cost = db.query(func.sum(InvestmentTransaction.total_cost)).filter(InvestmentTransaction.investment_id == inv.id, InvestmentTransaction.user_id == user.id, InvestmentTransaction.type == 'buy').scalar() or 0.0
        sell_cost = db.query(func.sum(InvestmentTransaction.total_cost)).filter(InvestmentTransaction.investment_id == inv.id, InvestmentTransaction.user_id == user.id, InvestmentTransaction.type == 'sell').scalar() or 0.0
        quantity = float(qsum)
        cost_basis = float((buy_cost or 0.0) - (sell_cost or 0.0))
        out.append({'investment_id': inv.id, 'symbol': inv.symbol, 'name': inv.name, 'quantity': quantity, 'cost_basis': cost_basis, 'market_value': None})
    return out

router = APIRouter()

@router.post('/', response_model=InvestmentOut)
def create_investment(inv_in: InvestmentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    inv = Investment(user_id=user.id, symbol=inv_in.symbol.upper(), name=inv_in.name or inv_in.symbol)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.post('/txn', response_model=InvestmentTransactionOut, dependencies=[Depends(enforce_shabbat_readonly)])
def investment_tx(tx_in: InvestmentTransactionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    inv = db.query(Investment).filter(Investment.id == tx_in.investment_id, Investment.user_id == user.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail='Investment not found')
    acct = db.query(Account).filter(Account.id == tx_in.account_id, Account.user_id == user.id).first()
    if not acct:
        raise HTTPException(status_code=404, detail='Account not found')
    # For buys, deduct amount from account by creating a transaction and record investment txn
    total = float(tx_in.quantity) * float(tx_in.unit_price)
    inv_tx = InvestmentTransaction(user_id=user.id, investment_id=tx_in.investment_id, account_id=tx_in.account_id, date=tx_in.date, type=tx_in.type, quantity=tx_in.quantity, unit_price=tx_in.unit_price, total_cost=total)
    db.add(inv_tx)
    # create account transaction representing cash out/in
    if tx_in.type == 'buy':
        acct_tx = Account.__table__.metadata.bind
        from ..models.finance import Transaction
        cash_tx = Transaction(user_id=user.id, account_id=tx_in.account_id, category_id=None, date=tx_in.date, amount=-total, note=f'Buy {inv.symbol} x{tx_in.quantity}')
        db.add(cash_tx)
    elif tx_in.type == 'sell':
        from ..models.finance import Transaction
        cash_tx = Transaction(user_id=user.id, account_id=tx_in.account_id, category_id=None, date=tx_in.date, amount=total, note=f'Sell {inv.symbol} x{tx_in.quantity}')
        db.add(cash_tx)
    db.commit()
    db.refresh(inv_tx)
    return inv_tx
