"""
Accounting Lite Schemas
Pydantic models for financial management API
"""

from pydantic import BaseModel, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


# Enums
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    CHEQUE = "cheque"
    OTHER = "other"


class FeeStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    WAIVED = "waived"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


# Base schemas
class AccountBase(BaseModel):
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: AccountType
    description: Optional[str] = None
    is_active: bool = True
    parent_account_id: Optional[int] = None


class AccountCreate(AccountBase):
    school_id: int
    created_by: int


class AccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    parent_account_id: Optional[int] = None


class AccountResponse(AccountBase):
    account_id: int
    school_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Transaction schemas
class TransactionBase(BaseModel):
    account_id: int
    transaction_type: TransactionType
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=1000)
    reference_number: Optional[str] = Field(None, max_length=100)
    payment_method: Optional[PaymentMethod] = None
    student_id: Optional[int] = None
    transaction_date: date = Field(default_factory=date.today)
    due_date: Optional[date] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TransactionCreate(TransactionBase):
    school_id: int
    created_by: int


class TransactionUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    reference_number: Optional[str] = Field(None, max_length=100)
    status: Optional[TransactionStatus] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TransactionResponse(TransactionBase):
    transaction_id: int
    school_id: int
    transaction_number: str
    status: TransactionStatus
    invoice_id: Optional[int] = None
    fee_payment_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Fee Structure schemas
class FeeStructureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    class_level: str = Field(..., min_length=1, max_length=100)
    base_amount: float = Field(..., gt=0)
    currency: str = Field(default="NGN", max_length=3)
    is_installment_allowed: bool = True
    installment_count: int = Field(default=1, ge=1)
    due_date: Optional[date] = None
    late_fee_amount: float = Field(default=0, ge=0)
    late_fee_percentage: float = Field(default=0, ge=0, le=100)
    is_active: bool = True
    is_mandatory: bool = True


class FeeStructureCreate(FeeStructureBase):
    school_id: int
    term_id: Optional[int] = None
    created_by: int


class FeeStructureUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    base_amount: Optional[float] = Field(None, gt=0)
    is_installment_allowed: Optional[bool] = None
    installment_count: Optional[int] = Field(None, ge=1)
    due_date: Optional[date] = None
    late_fee_amount: Optional[float] = Field(None, ge=0)
    late_fee_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    is_mandatory: Optional[bool] = None


class FeeStructureResponse(FeeStructureBase):
    structure_id: int
    school_id: int
    term_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Fee Assignment schemas
class FeeAssignmentBase(BaseModel):
    student_id: int
    structure_id: int
    assigned_amount: float = Field(..., gt=0)
    discount_amount: float = Field(default=0, ge=0)
    discount_percentage: float = Field(default=0, ge=0, le=100)
    due_date: date
    
    @validator('final_amount', always=True)
    def calculate_final_amount(cls, v, values):
        assigned = values.get('assigned_amount', 0)
        discount_amt = values.get('discount_amount', 0)
        discount_pct = values.get('discount_percentage', 0)
        
        discount_total = discount_amt + (assigned * discount_pct / 100)
        return max(0, assigned - discount_total)


class FeeAssignmentCreate(FeeAssignmentBase):
    school_id: int
    assigned_by: int


class FeeAssignmentUpdate(BaseModel):
    assigned_amount: Optional[float] = Field(None, gt=0)
    discount_amount: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    due_date: Optional[date] = None
    status: Optional[FeeStatus] = None


class FeeAssignmentResponse(FeeAssignmentBase):
    assignment_id: int
    school_id: int
    final_amount: float
    status: FeeStatus
    paid_amount: float
    balance_amount: float
    last_payment_date: Optional[date] = None
    assigned_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Fee Payment schemas
class FeePaymentBase(BaseModel):
    student_id: int
    assignment_id: int
    amount_paid: float = Field(..., gt=0)
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(None, max_length=100)
    payment_date: date = Field(default_factory=date.today)
    notes: Optional[str] = None


class FeePaymentCreate(FeePaymentBase):
    school_id: int
    received_by: int


class FeePaymentUpdate(BaseModel):
    reference_number: Optional[str] = Field(None, max_length=100)
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None


class FeePaymentResponse(FeePaymentBase):
    payment_id: int
    school_id: int
    payment_number: str
    status: TransactionStatus
    receipt_url: Optional[str] = None
    received_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Invoice schemas
class InvoiceItemBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., gt=0)
    notes: Optional[str] = None
    
    @validator('total_price', always=True)
    def calculate_total_price(cls, v, values):
        quantity = values.get('quantity', 0)
        unit_price = values.get('unit_price', 0)
        return quantity * unit_price


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    item_id: int
    invoice_id: int
    total_price: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    client_type: str = Field(..., regex=r'^(student|parent|vendor)$')
    client_id: int
    client_name: str = Field(..., min_length=1, max_length=200)
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    subtotal: float = Field(..., ge=0)
    tax_amount: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    currency: str = Field(default="NGN", max_length=3)
    invoice_date: date = Field(default_factory=date.today)
    due_date: date
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None
    
    @validator('total_amount', always=True)
    def calculate_total_amount(cls, v, values):
        subtotal = values.get('subtotal', 0)
        tax = values.get('tax_amount', 0)
        discount = values.get('discount_amount', 0)
        return max(0, subtotal + tax - discount)
    
    @validator('due_date')
    def validate_due_date(cls, v, values):
        invoice_date = values.get('invoice_date')
        if invoice_date and v < invoice_date:
            raise ValueError('Due date cannot be before invoice date')
        return v


class InvoiceCreate(InvoiceBase):
    school_id: int
    created_by: int
    items: List[InvoiceItemCreate] = []


class InvoiceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[InvoiceStatus] = None
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    invoice_id: int
    school_id: int
    invoice_number: str
    total_amount: float
    paid_amount: float
    balance_amount: float
    status: InvoiceStatus
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[InvoiceItemResponse] = []
    
    class Config:
        from_attributes = True


# Financial Report schemas
class FinancialReportBase(BaseModel):
    report_type: str = Field(..., regex=r'^(income_statement|balance_sheet|cash_flow|fee_summary)$')
    report_name: str = Field(..., min_length=1, max_length=200)
    report_period: str = Field(..., regex=r'^(monthly|quarterly|yearly|custom)$')
    start_date: date
    end_date: date
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        start_date = values.get('start_date')
        if start_date and v < start_date:
            raise ValueError('End date cannot be before start date')
        return v


class FinancialReportCreate(FinancialReportBase):
    school_id: int
    generated_by: int


class FinancialReportResponse(FinancialReportBase):
    report_id: int
    school_id: int
    report_data: Dict[str, Any]
    summary_data: Optional[Dict[str, Any]] = None
    file_url: Optional[str] = None
    file_format: Optional[str] = None
    is_finalized: bool
    generated_by: int
    generated_at: datetime
    
    class Config:
        from_attributes = True


# Budget schemas
class BudgetItemBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    planned_amount: float = Field(..., gt=0)
    month: Optional[int] = Field(None, ge=1, le=12)
    quarter: Optional[int] = Field(None, ge=1, le=4)
    account_id: Optional[int] = None


class BudgetItemCreate(BudgetItemBase):
    pass


class BudgetItemResponse(BudgetItemBase):
    item_id: int
    budget_id: int
    actual_amount: float
    variance_amount: float
    variance_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    budget_year: int = Field(..., ge=2020, le=2050)
    total_budget: float = Field(..., gt=0)
    is_active: bool = True


class BudgetCreate(BudgetBase):
    school_id: int
    created_by: int
    items: List[BudgetItemCreate] = []


class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    total_budget: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None


class BudgetResponse(BudgetBase):
    budget_id: int
    school_id: int
    allocated_amount: float
    spent_amount: float
    remaining_amount: float
    is_approved: bool
    created_by: int
    approved_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    items: List[BudgetItemResponse] = []
    
    class Config:
        from_attributes = True


# Dashboard and summary schemas
class FinancialSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_income: float
    outstanding_fees: float
    collected_fees: float
    pending_invoices: float
    cash_balance: float


class FeeSummary(BaseModel):
    total_assigned: float
    total_collected: float
    total_outstanding: float
    collection_rate: float
    overdue_amount: float
    students_with_outstanding: int


class TransactionSummary(BaseModel):
    total_transactions: int
    income_transactions: int
    expense_transactions: int
    pending_transactions: int
    todays_transactions: int
    this_month_total: float


class DashboardData(BaseModel):
    financial_summary: FinancialSummary
    fee_summary: FeeSummary
    transaction_summary: TransactionSummary
    recent_transactions: List[TransactionResponse]
    pending_payments: List[FeePaymentResponse]
    overdue_invoices: List[InvoiceResponse]


# Bulk operation schemas
class BulkFeeAssignmentCreate(BaseModel):
    structure_id: int
    student_ids: List[int]
    discount_percentage: float = Field(default=0, ge=0, le=100)
    discount_amount: float = Field(default=0, ge=0)
    due_date: date


class BulkTransactionCreate(BaseModel):
    transactions: List[TransactionCreate]


class BulkOperationResponse(BaseModel):
    successful: int
    failed: int
    errors: List[str] = []
    created_ids: List[int] = []


# Search and filter schemas
class TransactionFilter(BaseModel):
    account_id: Optional[int] = None
    transaction_type: Optional[TransactionType] = None
    status: Optional[TransactionStatus] = None
    student_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class FeePaymentFilter(BaseModel):
    student_id: Optional[int] = None
    assignment_id: Optional[int] = None
    status: Optional[TransactionStatus] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class InvoiceFilter(BaseModel):
    client_type: Optional[str] = None
    client_id: Optional[int] = None
    status: Optional[InvoiceStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    overdue_only: bool = False
