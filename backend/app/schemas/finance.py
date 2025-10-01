from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class AccountBase(BaseModel):
    name: str
    type: str
    opening_balance: float = 0.0
    is_liability: bool = False

class AccountCreate(AccountBase):
    pass

class AccountOut(AccountBase):
    id: int

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

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int

    class Config:
        from_attributes = True

class BudgetItemIn(BaseModel):
    category_id: int
    limit: float

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
