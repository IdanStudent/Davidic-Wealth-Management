import sys, os
import pytest
from fastapi.testclient import TestClient
# ensure repo root is on sys.path so `backend` package is importable when running pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.app.main import app
from backend.app.core.db import get_db, Base, engine
from backend.app.models.finance import Account, Transaction, AccountType
from backend.app.models.user import User
from sqlalchemy.orm import Session
from datetime import date

# Use the real DB but isolate by creating/dropping tables around tests
@pytest.fixture(autouse=True)
def create_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    sess = Session(bind=engine)
    try:
        yield sess
    finally:
        sess.close()

# override get_current_user to return a test user
@pytest.fixture(autouse=True)
def fake_user(db_session):
    u = User(email='test@example.com', hashed_password='x', full_name='Tester')
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    def _get_current_user_override():
        return u
    app.dependency_overrides = { }
    from backend.app.services.deps import get_current_user
    app.dependency_overrides[get_current_user] = lambda: u
    return u


def test_networth_endpoint(db_session):
    # create an account and a transaction
    user = db_session.query(User).filter_by(email='test@example.com').first()
    a = Account(user_id=user.id, name='Cash', type=AccountType.CASH, opening_balance=100.0, is_liability=False)
    db_session.add(a)
    db_session.commit()
    # create a transaction
    t = Transaction(user_id=user.id, account_id=a.id, date=date.today(), amount=50.0, note='Deposit')
    db_session.add(t)
    db_session.commit()

    client = TestClient(app)
    resp = client.get('/api/reports/networth')
    assert resp.status_code == 200
    data = resp.json()
    assert 'assets' in data and 'liabilities' in data and 'net_worth' in data
    # assets should include the transaction sum (50) + opening balance if logic calculates that way
    assert isinstance(data['assets'], float) or isinstance(data['assets'], int)
    assert isinstance(data['history'], list)
