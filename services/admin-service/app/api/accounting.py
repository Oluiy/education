"""
Accounting Lite API endpoints
Basic financial management for schools
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging

from database import get_db
from services.accounting_service import AccountingService
from schemas.accounting_schemas import (
    AccountCreate, AccountResponse, AccountUpdate,
    TransactionCreate, TransactionResponse, TransactionUpdate, TransactionFilter,
    FeeStructureCreate, FeeStructureResponse, FeeStructureUpdate,
    FeeAssignmentCreate, FeeAssignmentResponse, FeePaymentCreate, FeePaymentResponse,
    InvoiceCreate, InvoiceResponse, InvoiceUpdate, InvoiceFilter,
    BudgetCreate, BudgetResponse, BudgetUpdate,
    FinancialSummary, FeeSummary, TransactionSummary, DashboardData,
    BulkFeeAssignmentCreate, BulkOperationResponse
)
from auth.dependencies import get_current_user, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/accounting",
    tags=["Accounting Lite"]
)


# === ACCOUNT MANAGEMENT ===

@router.post("/accounts/setup-defaults", response_model=List[AccountResponse])
async def setup_default_accounts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"]))
):
    """
    Set up default chart of accounts for the school
    """
    try:
        service = AccountingService(db)
        
        accounts = service.create_default_accounts(
            school_id=current_user["school_id"],
            created_by=current_user["user_id"]
        )
        
        return [AccountResponse.from_orm(account) for account in accounts]
    
    except Exception as e:
        logger.error(f"Error setting up default accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup default accounts"
        )


@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"]))
):
    """
    Create a new account
    """
    try:
        from models.accounting_models import Account
        
        # Check if account code already exists
        existing = db.query(Account).filter(
            Account.school_id == current_user["school_id"],
            Account.account_code == account.account_code
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account code already exists"
            )
        
        # Set school_id and created_by
        account.school_id = current_user["school_id"]
        account.created_by = current_user["user_id"]
        
        new_account = Account(**account.dict())
        db.add(new_account)
        db.commit()
        db.refresh(new_account)
        
        return AccountResponse.from_orm(new_account)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(
    account_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get all accounts for the school
    """
    try:
        from models.accounting_models import Account
        from sqlalchemy import and_
        
        query = db.query(Account).filter(Account.school_id == current_user["school_id"])
        
        if account_type:
            query = query.filter(Account.account_type == account_type)
        
        if is_active is not None:
            query = query.filter(Account.is_active == is_active)
        
        accounts = query.order_by(Account.account_code).all()
        
        return [AccountResponse.from_orm(account) for account in accounts]
    
    except Exception as e:
        logger.error(f"Error getting accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get accounts"
        )


@router.get("/accounts/{account_id}/balance")
async def get_account_balance(
    account_id: int,
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get account balance
    """
    try:
        service = AccountingService(db)
        
        balance = service.get_account_balance(account_id, as_of_date)
        
        return {
            "account_id": account_id,
            "balance": balance,
            "as_of_date": as_of_date or date.today()
        }
    
    except Exception as e:
        logger.error(f"Error getting account balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get account balance"
        )


# === TRANSACTION MANAGEMENT ===

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Create a new transaction
    """
    try:
        service = AccountingService(db)
        
        # Set school_id and created_by
        transaction.school_id = current_user["school_id"]
        transaction.created_by = current_user["user_id"]
        
        new_transaction = service.create_transaction(transaction)
        
        return TransactionResponse.from_orm(new_transaction)
    
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction"
        )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    student_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get transactions with filters
    """
    try:
        from models.accounting_models import Transaction
        from sqlalchemy import and_, desc
        
        query = db.query(Transaction).filter(
            Transaction.school_id == current_user["school_id"]
        )
        
        # Apply filters
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if status:
            query = query.filter(Transaction.status == status)
        
        if student_id:
            query = query.filter(Transaction.student_id == student_id)
        
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        
        # Order by most recent first
        query = query.order_by(desc(Transaction.created_at))
        
        # Apply pagination
        transactions = query.offset(offset).limit(limit).all()
        
        return [TransactionResponse.from_orm(transaction) for transaction in transactions]
    
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions"
        )


# === FEE MANAGEMENT ===

@router.post("/fee-structures", response_model=FeeStructureResponse)
async def create_fee_structure(
    fee_structure: FeeStructureCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"]))
):
    """
    Create a new fee structure
    """
    try:
        from models.accounting_models import FeeStructure
        
        # Set school_id and created_by
        fee_structure.school_id = current_user["school_id"]
        fee_structure.created_by = current_user["user_id"]
        
        new_structure = FeeStructure(**fee_structure.dict())
        db.add(new_structure)
        db.commit()
        db.refresh(new_structure)
        
        return FeeStructureResponse.from_orm(new_structure)
    
    except Exception as e:
        logger.error(f"Error creating fee structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create fee structure"
        )


@router.post("/fee-assignments/bulk", response_model=BulkOperationResponse)
async def bulk_assign_fees(
    bulk_assignment: BulkFeeAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Assign fees to multiple students
    """
    try:
        service = AccountingService(db)
        
        assignments = service.bulk_assign_fees(
            structure_id=bulk_assignment.structure_id,
            student_ids=bulk_assignment.student_ids,
            school_id=current_user["school_id"],
            assigned_by=current_user["user_id"],
            discount_percentage=bulk_assignment.discount_percentage,
            discount_amount=bulk_assignment.discount_amount,
            due_date=bulk_assignment.due_date
        )
        
        return BulkOperationResponse(
            successful=len(assignments),
            failed=0,
            created_ids=[a.assignment_id for a in assignments]
        )
    
    except Exception as e:
        logger.error(f"Error bulk assigning fees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk assign fees"
        )


@router.post("/fee-payments", response_model=FeePaymentResponse)
async def process_fee_payment(
    payment: FeePaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Process a fee payment
    """
    try:
        service = AccountingService(db)
        
        # Set school_id and received_by
        payment.school_id = current_user["school_id"]
        payment.received_by = current_user["user_id"]
        
        fee_payment, transaction = service.process_fee_payment(payment)
        
        return FeePaymentResponse.from_orm(fee_payment)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing fee payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process fee payment"
        )


@router.get("/fee-assignments/overdue")
async def get_overdue_fees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get overdue fee assignments
    """
    try:
        service = AccountingService(db)
        
        overdue_data = service.calculate_overdue_fees(current_user["school_id"])
        
        return overdue_data
    
    except Exception as e:
        logger.error(f"Error getting overdue fees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get overdue fees"
        )


# === INVOICE MANAGEMENT ===

@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Create a new invoice with items
    """
    try:
        service = AccountingService(db)
        
        # Set school_id and created_by
        invoice.school_id = current_user["school_id"]
        invoice.created_by = current_user["user_id"]
        
        new_invoice = service.create_invoice_with_items(invoice)
        
        return InvoiceResponse.from_orm(new_invoice)
    
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invoice"
        )


@router.post("/invoices/{invoice_id}/payment")
async def process_invoice_payment(
    invoice_id: int,
    amount_paid: float,
    payment_method: str,
    reference_number: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Process payment for an invoice
    """
    try:
        service = AccountingService(db)
        
        invoice, transaction = service.process_invoice_payment(
            invoice_id=invoice_id,
            amount_paid=amount_paid,
            payment_method=payment_method,
            reference_number=reference_number,
            created_by=current_user["user_id"]
        )
        
        return {
            "invoice": InvoiceResponse.from_orm(invoice),
            "transaction": TransactionResponse.from_orm(transaction)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing invoice payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process invoice payment"
        )


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    client_type: Optional[str] = None,
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    overdue_only: bool = False,
    limit: int = Query(default=50, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get invoices with filters
    """
    try:
        from models.accounting_models import Invoice
        from sqlalchemy import and_, desc
        
        query = db.query(Invoice).filter(
            Invoice.school_id == current_user["school_id"]
        )
        
        # Apply filters
        if client_type:
            query = query.filter(Invoice.client_type == client_type)
        
        if client_id:
            query = query.filter(Invoice.client_id == client_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if overdue_only:
            today = date.today()
            query = query.filter(
                and_(
                    Invoice.due_date < today,
                    Invoice.balance_amount > 0
                )
            )
        
        # Order by most recent first
        query = query.order_by(desc(Invoice.created_at))
        
        # Apply pagination
        invoices = query.offset(offset).limit(limit).all()
        
        return [InvoiceResponse.from_orm(invoice) for invoice in invoices]
    
    except Exception as e:
        logger.error(f"Error getting invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get invoices"
        )


# === DASHBOARD AND REPORTING ===

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get dashboard data with financial summaries
    """
    try:
        service = AccountingService(db)
        
        # Set default date range (current month)
        if not start_date:
            start_date = date.today().replace(day=1)
        if not end_date:
            end_date = date.today()
        
        # Generate summaries
        financial_summary = service.generate_financial_summary(
            school_id=current_user["school_id"],
            start_date=start_date,
            end_date=end_date
        )
        
        fee_summary = service.generate_fee_summary(
            school_id=current_user["school_id"]
        )
        
        # Get recent transactions
        from models.accounting_models import Transaction
        from sqlalchemy import desc
        
        recent_transactions_query = db.query(Transaction).filter(
            Transaction.school_id == current_user["school_id"]
        ).order_by(desc(Transaction.created_at)).limit(10)
        
        recent_transactions = recent_transactions_query.all()
        
        # Get pending payments
        from models.accounting_models import FeePayment
        
        pending_payments_query = db.query(FeePayment).filter(
            and_(
                FeePayment.school_id == current_user["school_id"],
                FeePayment.status == "pending"
            )
        ).limit(10)
        
        pending_payments = pending_payments_query.all()
        
        # Get overdue invoices
        from models.accounting_models import Invoice
        
        today = date.today()
        overdue_invoices_query = db.query(Invoice).filter(
            and_(
                Invoice.school_id == current_user["school_id"],
                Invoice.due_date < today,
                Invoice.balance_amount > 0
            )
        ).limit(10)
        
        overdue_invoices = overdue_invoices_query.all()
        
        # Transaction summary
        total_transactions = db.query(Transaction).filter(
            Transaction.school_id == current_user["school_id"]
        ).count()
        
        income_transactions = db.query(Transaction).filter(
            and_(
                Transaction.school_id == current_user["school_id"],
                Transaction.transaction_type == "income"
            )
        ).count()
        
        expense_transactions = db.query(Transaction).filter(
            and_(
                Transaction.school_id == current_user["school_id"],
                Transaction.transaction_type == "expense"
            )
        ).count()
        
        pending_transactions = db.query(Transaction).filter(
            and_(
                Transaction.school_id == current_user["school_id"],
                Transaction.status == "pending"
            )
        ).count()
        
        today_transactions = db.query(Transaction).filter(
            and_(
                Transaction.school_id == current_user["school_id"],
                Transaction.transaction_date == date.today()
            )
        ).count()
        
        from sqlalchemy import func
        this_month_total_query = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.school_id == current_user["school_id"],
                Transaction.status == "completed",
                extract('month', Transaction.transaction_date) == date.today().month,
                extract('year', Transaction.transaction_date) == date.today().year
            )
        )
        
        this_month_total = this_month_total_query.scalar() or 0.0
        
        transaction_summary = TransactionSummary(
            total_transactions=total_transactions,
            income_transactions=income_transactions,
            expense_transactions=expense_transactions,
            pending_transactions=pending_transactions,
            todays_transactions=today_transactions,
            this_month_total=this_month_total
        )
        
        return DashboardData(
            financial_summary=financial_summary,
            fee_summary=fee_summary,
            transaction_summary=transaction_summary,
            recent_transactions=[TransactionResponse.from_orm(t) for t in recent_transactions],
            pending_payments=[FeePaymentResponse.from_orm(p) for p in pending_payments],
            overdue_invoices=[InvoiceResponse.from_orm(i) for i in overdue_invoices]
        )
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard data"
        )


@router.get("/reports/financial-summary", response_model=FinancialSummary)
async def get_financial_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get financial summary report
    """
    try:
        service = AccountingService(db)
        
        summary = service.generate_financial_summary(
            school_id=current_user["school_id"],
            start_date=start_date,
            end_date=end_date
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating financial summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial summary"
        )


@router.get("/reports/fee-summary", response_model=FeeSummary)
async def get_fee_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin", "teacher"]))
):
    """
    Get fee collection summary report
    """
    try:
        service = AccountingService(db)
        
        summary = service.generate_fee_summary(
            school_id=current_user["school_id"]
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"Error generating fee summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate fee summary"
        )


# === UTILITY ENDPOINTS ===

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Accounting Lite",
        "timestamp": datetime.now().isoformat()
    }
