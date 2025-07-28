"""
Accounting Lite Models
Basic financial tracking for educational institutions
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
import uuid

Base = declarative_base()


# Enums
class TransactionType(PyEnum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentMethod(PyEnum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    CHEQUE = "cheque"
    OTHER = "other"


class FeeStatus(PyEnum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    WAIVED = "waived"


class InvoiceStatus(PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class AccountType(PyEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


# Models
class Account(Base):
    """Chart of accounts for basic bookkeeping"""
    __tablename__ = "accounts"
    
    account_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    account_code = Column(String(20), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    parent_account_id = Column(Integer, ForeignKey("accounts.account_id"))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    parent_account = relationship("Account", remote_side=[account_id])
    child_accounts = relationship("Account", back_populates="parent_account")
    transactions = relationship("Transaction", back_populates="account")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class Transaction(Base):
    """Financial transactions"""
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False)
    transaction_number = Column(String(50), unique=True, nullable=False, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    reference_number = Column(String(100))
    payment_method = Column(SQLEnum(PaymentMethod))
    
    # Related entities
    student_id = Column(Integer, index=True)  # For fee payments
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"))
    fee_payment_id = Column(Integer, ForeignKey("fee_payments.payment_id"))
    
    # Status and dates
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    transaction_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date)
    
    # Additional metadata
    notes = Column(Text)
    tags = Column(JSON)  # For categorization
    attachments = Column(JSON)  # File references
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    invoice = relationship("Invoice", back_populates="transactions")
    fee_payment = relationship("FeePayment", back_populates="transaction")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class FeeStructure(Base):
    """School fee structure definition"""
    __tablename__ = "fee_structures"
    
    structure_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    term_id = Column(Integer, index=True)
    class_level = Column(String(100), nullable=False)
    
    # Fee details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    base_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="NGN")
    
    # Payment schedule
    is_installment_allowed = Column(Boolean, default=True)
    installment_count = Column(Integer, default=1)
    due_date = Column(Date)
    late_fee_amount = Column(Float, default=0)
    late_fee_percentage = Column(Float, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_mandatory = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    fee_assignments = relationship("FeeAssignment", back_populates="fee_structure")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class FeeAssignment(Base):
    """Individual student fee assignments"""
    __tablename__ = "fee_assignments"
    
    assignment_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    structure_id = Column(Integer, ForeignKey("fee_structures.structure_id"), nullable=False)
    
    # Assignment details
    assigned_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0)
    discount_percentage = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    
    # Payment status
    status = Column(SQLEnum(FeeStatus), default=FeeStatus.PENDING)
    paid_amount = Column(Float, default=0)
    balance_amount = Column(Float, nullable=False)
    
    # Dates
    due_date = Column(Date, nullable=False)
    last_payment_date = Column(Date)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    assigned_by = Column(Integer, nullable=False)
    
    # Relationships
    fee_structure = relationship("FeeStructure", back_populates="fee_assignments")
    fee_payments = relationship("FeePayment", back_populates="fee_assignment")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class FeePayment(Base):
    """Student fee payments"""
    __tablename__ = "fee_payments"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    assignment_id = Column(Integer, ForeignKey("fee_assignments.assignment_id"), nullable=False)
    
    # Payment details
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    amount_paid = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    reference_number = Column(String(100))
    
    # Status and dates
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    payment_date = Column(Date, nullable=False, default=date.today)
    
    # Additional details
    notes = Column(Text)
    receipt_url = Column(String(500))
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    received_by = Column(Integer, nullable=False)
    
    # Relationships
    fee_assignment = relationship("FeeAssignment", back_populates="fee_payments")
    transaction = relationship("Transaction", back_populates="fee_payment")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class Invoice(Base):
    """Invoices for various charges"""
    __tablename__ = "invoices"
    
    invoice_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Invoice details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Client information
    client_type = Column(String(20), nullable=False)  # 'student', 'parent', 'vendor'
    client_id = Column(Integer, nullable=False)
    client_name = Column(String(200), nullable=False)
    client_email = Column(String(200))
    client_phone = Column(String(20))
    
    # Financial details
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="NGN")
    
    # Payment details
    paid_amount = Column(Float, default=0)
    balance_amount = Column(Float, nullable=False)
    
    # Dates
    invoice_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    
    # Status
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Additional details
    notes = Column(Text)
    terms_conditions = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    
    # Relationships
    invoice_items = relationship("InvoiceItem", back_populates="invoice")
    transactions = relationship("Transaction", back_populates="invoice")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class InvoiceItem(Base):
    """Individual items in an invoice"""
    __tablename__ = "invoice_items"
    
    item_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"), nullable=False)
    
    # Item details
    description = Column(String(500), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Additional details
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class FinancialReport(Base):
    """Pre-generated financial reports for quick access"""
    __tablename__ = "financial_reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Report details
    report_type = Column(String(50), nullable=False)  # 'income_statement', 'balance_sheet', 'cash_flow'
    report_name = Column(String(200), nullable=False)
    report_period = Column(String(20), nullable=False)  # 'monthly', 'quarterly', 'yearly'
    
    # Period details
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Report data
    report_data = Column(JSON, nullable=False)
    summary_data = Column(JSON)
    
    # File storage
    file_url = Column(String(500))
    file_format = Column(String(10))  # 'pdf', 'excel'
    
    # Status
    is_finalized = Column(Boolean, default=False)
    
    # Audit fields
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, nullable=False)
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class Budget(Base):
    """Budget planning and tracking"""
    __tablename__ = "budgets"
    
    budget_id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, nullable=False, index=True)
    
    # Budget details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    budget_year = Column(Integer, nullable=False)
    
    # Financial data
    total_budget = Column(Float, nullable=False)
    allocated_amount = Column(Float, default=0)
    spent_amount = Column(Float, default=0)
    remaining_amount = Column(Float, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    approved_by = Column(Integer)
    approved_at = Column(DateTime)
    
    # Relationships
    budget_items = relationship("BudgetItem", back_populates="budget")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )


class BudgetItem(Base):
    """Individual budget line items"""
    __tablename__ = "budget_items"
    
    item_id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.budget_id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.account_id"))
    
    # Item details
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    
    # Budget amounts
    planned_amount = Column(Float, nullable=False)
    actual_amount = Column(Float, default=0)
    variance_amount = Column(Float, default=0)
    variance_percentage = Column(Float, default=0)
    
    # Period
    month = Column(Integer)  # 1-12
    quarter = Column(Integer)  # 1-4
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    budget = relationship("Budget", back_populates="budget_items")
    
    # Constraints
    __table_args__ = (
        {"mysql_engine": "InnoDB"}
    )
