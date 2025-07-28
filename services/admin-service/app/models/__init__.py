"""
Models package for Admin Service
"""

from .term_models import (
    Term, ClassSchedule, AssessmentConfig, GradingConfig,
    Holiday, WizardSession, TermTemplate, CalendarEvent
)
from .accounting_models import (
    Account, Transaction, FeeStructure, FeeAssignment, FeePayment,
    Invoice, InvoiceItem, FinancialReport, Budget, BudgetItem
)

__all__ = [
    # Term models
    "Term", "ClassSchedule", "AssessmentConfig", "GradingConfig",
    "Holiday", "WizardSession", "TermTemplate", "CalendarEvent",
    
    # Accounting models
    "Account", "Transaction", "FeeStructure", "FeeAssignment", "FeePayment",
    "Invoice", "InvoiceItem", "FinancialReport", "Budget", "BudgetItem"
]
