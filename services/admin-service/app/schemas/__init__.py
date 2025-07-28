"""
Schemas package for Admin Service
"""

from .term_schemas import (
    TermCreate, TermUpdate, TermResponse, 
    ClassScheduleCreate, ClassScheduleUpdate, ClassScheduleResponse,
    AssessmentConfigCreate, AssessmentConfigUpdate, AssessmentConfigResponse,
    GradingConfigCreate, GradingConfigUpdate, GradingConfigResponse,
    HolidayCreate, HolidayUpdate, HolidayResponse,
    WizardSessionCreate, WizardSessionUpdate, WizardSessionResponse,
    TermTemplateCreate, TermTemplateUpdate, TermTemplateResponse,
    CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse,
    WizardStepRequest, WizardStepResponse, WizardProgressResponse,
    TermSummary, WizardStep, TermStatus
)
from .accounting_schemas import (
    AccountCreate, AccountUpdate, AccountResponse,
    TransactionCreate, TransactionUpdate, TransactionResponse,
    FeeStructureCreate, FeeStructureUpdate, FeeStructureResponse,
    FeeAssignmentCreate, FeeAssignmentUpdate, FeeAssignmentResponse,
    FeePaymentCreate, FeePaymentUpdate, FeePaymentResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    InvoiceItemCreate, InvoiceItemResponse,
    BudgetCreate, BudgetUpdate, BudgetResponse,
    BudgetItemCreate, BudgetItemResponse,
    FinancialSummary, FeeSummary, TransactionSummary, DashboardData,
    BulkFeeAssignmentCreate, BulkOperationResponse
)

__all__ = [
    # Term schemas
    "TermCreate", "TermUpdate", "TermResponse",
    "ClassScheduleCreate", "ClassScheduleUpdate", "ClassScheduleResponse",
    "AssessmentConfigCreate", "AssessmentConfigUpdate", "AssessmentConfigResponse",
    "GradingConfigCreate", "GradingConfigUpdate", "GradingConfigResponse",
    "HolidayCreate", "HolidayUpdate", "HolidayResponse",
    "WizardSessionCreate", "WizardSessionUpdate", "WizardSessionResponse",
    "TermTemplateCreate", "TermTemplateUpdate", "TermTemplateResponse",
    "CalendarEventCreate", "CalendarEventUpdate", "CalendarEventResponse",
    "WizardStepRequest", "WizardStepResponse", "WizardProgressResponse",
    "TermSummary", "WizardStep", "TermStatus",
    
    # Accounting schemas
    "AccountCreate", "AccountUpdate", "AccountResponse",
    "TransactionCreate", "TransactionUpdate", "TransactionResponse",
    "FeeStructureCreate", "FeeStructureUpdate", "FeeStructureResponse",
    "FeeAssignmentCreate", "FeeAssignmentUpdate", "FeeAssignmentResponse",
    "FeePaymentCreate", "FeePaymentUpdate", "FeePaymentResponse",
    "InvoiceCreate", "InvoiceUpdate", "InvoiceResponse",
    "InvoiceItemCreate", "InvoiceItemResponse",
    "BudgetCreate", "BudgetUpdate", "BudgetResponse",
    "BudgetItemCreate", "BudgetItemResponse",
    "FinancialSummary", "FeeSummary", "TransactionSummary", "DashboardData",
    "BulkFeeAssignmentCreate", "BulkOperationResponse"
]
