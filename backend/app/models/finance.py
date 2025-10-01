from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Enum, Boolean
from sqlalchemy.orm import relationship
from ..core.db import Base
import enum

class AccountType(str, enum.Enum):
    CASH = "Cash"
    SAVINGS = "Savings"
    CREDIT_CARD = "Credit Card"
    LOAN = "Loan"
    INVESTMENT = "Investment"

class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    opening_balance = Column(Float, default=0.0)
    is_liability = Column(Boolean, default=False)

    owner = relationship("User", back_populates="accounts")
    # specify foreign_keys to disambiguate from Transaction.counterparty_account_id
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan", foreign_keys='Transaction.account_id')

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    is_builtin = Column(Boolean, default=False)
    icon = Column(String, default="")

    owner = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    note = Column(String, default="")
    # Transfer support
    is_transfer = Column(Boolean, default=False)
    counterparty_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    owner = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    # counterparty relationship (optional)
    counterparty_account = relationship("Account", foreign_keys=[counterparty_account_id])
    # specify which FK links Transaction -> Account for the main account relationship
    account = relationship("Account", back_populates="transactions", foreign_keys=[account_id])

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM

    owner = relationship("User", back_populates="budgets")
    items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")

class BudgetItem(Base):
    __tablename__ = "budget_items"
    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    limit = Column(Float, nullable=False)

    budget = relationship("Budget", back_populates="items")
    category = relationship("Category")

class GoalType(str, enum.Enum):
    TZEDAKAH = "tzedakah"
    WEDDING = "wedding"
    BAR_MITZVAH = "bar_mitzvah"
    PESACH = "pesach"
    CUSTOM = "custom"

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(GoalType), default=GoalType.CUSTOM, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    due_date = Column(String, default="")

    owner = relationship("User", back_populates="goals")


class Investment(Base):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=True)

    owner = relationship('User')
    transactions = relationship('InvestmentTransaction', back_populates='investment', cascade='all, delete-orphan')


class InvestmentTransaction(Base):
    __tablename__ = 'investment_transactions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    investment_id = Column(Integer, ForeignKey('investments.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(String, nullable=False)  # buy | sell
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    investment = relationship('Investment', back_populates='transactions')
    account = relationship('Account')
