from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date

class AccountBase(BaseModel):
    name: str
    type: str
    opening_balance: float = 0.0
    is_liability: bool = False
    apr_annual: float | None = None
    min_payment: float | None = None
    due_day: int | None = None

class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    opening_balance: Optional[float] = None
    is_liability: Optional[bool] = None
    apr_annual: Optional[float] = None
    min_payment: Optional[float] = None
    due_day: Optional[int] = None

class AccountOut(AccountBase):
    id: int
    balance: float = 0.0

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    type: str  # income | expense
    icon: Optional[str] = ""

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    is_builtin: bool

    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None

class TransactionBase(BaseModel):
    account_id: int
    category_id: Optional[int] = None
    date: date
    amount: float
    note: Optional[str] = ""
    is_transfer: bool = False
    counterparty_account_id: Optional[int] = None

    @field_validator('date', mode='before')
    def _coerce_date(cls, v):
        # Accept both date objects and ISO date strings (including years with leading zeros)
        if v is None:
            return v
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(str(v))
        except Exception:
            raise ValueError('Invalid date format')

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int

    class Config:
        from_attributes = True


class InvestmentCreate(BaseModel):
    symbol: str
    name: Optional[str] = None

class InvestmentOut(BaseModel):
    id: int
    symbol: str
    name: Optional[str]

    class Config:
        from_attributes = True

class InvestmentTransactionCreate(BaseModel):
    investment_id: int
    account_id: int
    date: date
    type: str  # buy|sell
    quantity: float
    unit_price: float

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

class InvestmentTransactionOut(InvestmentTransactionCreate):
    id: int

    class Config:
        from_attributes = True

class BudgetItemIn(BaseModel):
    category_id: int
    limit: float
    item_type: str | None = "fixed"  # fixed | flex
    tolerance_pct: float | None = 0.15
    window_months: int | None = 3

class BudgetCreate(BaseModel):
    month: str  # YYYY-MM
    items: List[BudgetItemIn] = []

class BudgetItemOut(BudgetItemIn):
    id: int

    class Config:
        from_attributes = True

class BudgetOut(BaseModel):
    id: int
    month: str
    items: List[BudgetItemOut] = []

    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    name: str
    type: str
    target_amount: float
    current_amount: float = 0.0
    due_date: str = ""

class GoalCreate(GoalBase):
    pass

class GoalOut(GoalBase):
    id: int

    class Config:
        from_attributes = True


class CategoryRuleIn(BaseModel):
    pattern: str
    category_id: int
    min_amount: float | None = None
    max_amount: float | None = None
    case_sensitive: bool = False

class CategoryRuleOut(CategoryRuleIn):
    id: int

    class Config:
        from_attributes = True

# Debt planner
class DebtInput(BaseModel):
    id: int
    name: str
    balance: float
    apr_annual: float
    min_payment: float
    due_day: int | None = None

class DebtPlanRequest(BaseModel):
    strategy: str  # snowball | avalanche
    monthly_budget: float
    debts: list[DebtInput]
    extra_payment: float | None = 0.0
    # Optional APR changes during the plan
    # each item: { debt_id, month_offset: int (0-based), apr_annual: float }
    rate_changes: list[dict] | None = None

class DebtPayment(BaseModel):
    month: str  # YYYY-MM
    debt_id: int
    payment: float
    principal: float
    interest: float
    balance_after: float

class DebtPlan(BaseModel):
    schedule: list[DebtPayment]
    months_to_payoff: int
    total_interest: float
    strategy: str
