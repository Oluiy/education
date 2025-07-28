"""
Accounting Lite Service
Business logic for basic financial management
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
import logging
import uuid

from models.accounting_models import (
    Account, Transaction, FeeStructure, FeeAssignment, FeePayment,
    Invoice, InvoiceItem, FinancialReport, Budget, BudgetItem
)
from schemas.accounting_schemas import (
    AccountCreate, TransactionCreate, FeeStructureCreate, FeeAssignmentCreate,
    FeePaymentCreate, InvoiceCreate, BudgetCreate, FinancialSummary,
    FeeSummary, TransactionSummary, DashboardData, TransactionStatus,
    FeeStatus, InvoiceStatus, PaymentMethod, AccountType
)

logger = logging.getLogger(__name__)


class AccountingService:
    """Service for accounting and financial management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # === ACCOUNT MANAGEMENT ===
    
    def create_default_accounts(self, school_id: int, created_by: int) -> List[Account]:
        """
        Create default chart of accounts for a school
        """
        try:
            default_accounts = [
                # Assets
                {"code": "1000", "name": "Cash", "type": AccountType.ASSET},
                {"code": "1100", "name": "Bank Account", "type": AccountType.ASSET},
                {"code": "1200", "name": "Accounts Receivable", "type": AccountType.ASSET},
                {"code": "1300", "name": "Equipment", "type": AccountType.ASSET},
                
                # Liabilities
                {"code": "2000", "name": "Accounts Payable", "type": AccountType.LIABILITY},
                {"code": "2100", "name": "Accrued Expenses", "type": AccountType.LIABILITY},
                
                # Equity
                {"code": "3000", "name": "Owner's Equity", "type": AccountType.EQUITY},
                {"code": "3100", "name": "Retained Earnings", "type": AccountType.EQUITY},
                
                # Revenue
                {"code": "4000", "name": "Tuition Revenue", "type": AccountType.REVENUE},
                {"code": "4100", "name": "Other Fees", "type": AccountType.REVENUE},
                {"code": "4200", "name": "Other Income", "type": AccountType.REVENUE},
                
                # Expenses
                {"code": "5000", "name": "Salaries & Wages", "type": AccountType.EXPENSE},
                {"code": "5100", "name": "Utilities", "type": AccountType.EXPENSE},
                {"code": "5200", "name": "Supplies", "type": AccountType.EXPENSE},
                {"code": "5300", "name": "Maintenance", "type": AccountType.EXPENSE},
                {"code": "5400", "name": "Other Expenses", "type": AccountType.EXPENSE},
            ]
            
            created_accounts = []
            
            for acc_data in default_accounts:
                # Check if account already exists
                existing = self.db.query(Account).filter(
                    and_(
                        Account.school_id == school_id,
                        Account.account_code == acc_data["code"]
                    )
                ).first()
                
                if not existing:
                    account = Account(
                        school_id=school_id,
                        account_code=acc_data["code"],
                        account_name=acc_data["name"],
                        account_type=acc_data["type"],
                        created_by=created_by
                    )
                    
                    self.db.add(account)
                    created_accounts.append(account)
            
            self.db.commit()
            
            for account in created_accounts:
                self.db.refresh(account)
            
            logger.info(f"Created {len(created_accounts)} default accounts for school {school_id}")
            return created_accounts
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating default accounts: {e}")
            raise
    
    def get_account_balance(self, account_id: int, as_of_date: Optional[date] = None) -> float:
        """
        Calculate account balance as of specified date
        """
        try:
            query = self.db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.account_id == account_id,
                    Transaction.status == TransactionStatus.COMPLETED
                )
            )
            
            if as_of_date:
                query = query.filter(Transaction.transaction_date <= as_of_date)
            
            balance = query.scalar() or 0.0
            return balance
            
        except Exception as e:
            logger.error(f"Error calculating account balance: {e}")
            return 0.0
    
    # === TRANSACTION MANAGEMENT ===
    
    def create_transaction(
        self,
        transaction_data: TransactionCreate
    ) -> Transaction:
        """
        Create a new financial transaction
        """
        try:
            # Generate transaction number
            transaction_number = self._generate_transaction_number()
            
            transaction = Transaction(
                **transaction_data.dict(),
                transaction_number=transaction_number
            )
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            logger.info(f"Created transaction {transaction.transaction_number}")
            return transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise
    
    def process_fee_payment(
        self,
        payment_data: FeePaymentCreate
    ) -> Tuple[FeePayment, Transaction]:
        """
        Process a fee payment and create corresponding transaction
        """
        try:
            # Get fee assignment
            assignment = self.db.query(FeeAssignment).filter(
                FeeAssignment.assignment_id == payment_data.assignment_id
            ).first()
            
            if not assignment:
                raise ValueError("Fee assignment not found")
            
            if assignment.status == FeeStatus.PAID:
                raise ValueError("Fee already paid in full")
            
            # Check payment amount
            if payment_data.amount_paid > assignment.balance_amount:
                raise ValueError("Payment amount exceeds balance")
            
            # Generate payment number
            payment_number = self._generate_payment_number()
            
            # Create fee payment
            fee_payment = FeePayment(
                **payment_data.dict(),
                payment_number=payment_number
            )
            
            self.db.add(fee_payment)
            self.db.flush()  # Get payment ID
            
            # Create corresponding transaction
            revenue_account = self._get_revenue_account(payment_data.school_id)
            
            transaction_data = TransactionCreate(
                school_id=payment_data.school_id,
                account_id=revenue_account.account_id,
                transaction_type="income",
                amount=payment_data.amount_paid,
                description=f"Fee payment from student {payment_data.student_id}",
                reference_number=payment_data.reference_number,
                payment_method=payment_data.payment_method,
                student_id=payment_data.student_id,
                transaction_date=payment_data.payment_date,
                fee_payment_id=fee_payment.payment_id,
                created_by=payment_data.received_by
            )
            
            transaction = self.create_transaction(transaction_data)
            
            # Update fee assignment
            assignment.paid_amount += payment_data.amount_paid
            assignment.balance_amount -= payment_data.amount_paid
            assignment.last_payment_date = payment_data.payment_date
            
            # Update status
            if assignment.balance_amount <= 0:
                assignment.status = FeeStatus.PAID
            elif assignment.paid_amount > 0:
                assignment.status = FeeStatus.PARTIAL
            
            assignment.updated_at = datetime.utcnow()
            
            # Mark transaction as completed
            transaction.status = TransactionStatus.COMPLETED
            fee_payment.status = TransactionStatus.COMPLETED
            
            self.db.commit()
            
            self.db.refresh(fee_payment)
            self.db.refresh(transaction)
            
            logger.info(f"Processed fee payment {fee_payment.payment_number}")
            return fee_payment, transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing fee payment: {e}")
            raise
    
    # === FEE MANAGEMENT ===
    
    def bulk_assign_fees(
        self,
        structure_id: int,
        student_ids: List[int],
        school_id: int,
        assigned_by: int,
        discount_percentage: float = 0,
        discount_amount: float = 0,
        due_date: Optional[date] = None
    ) -> List[FeeAssignment]:
        """
        Assign fees to multiple students
        """
        try:
            # Get fee structure
            structure = self.db.query(FeeStructure).filter(
                FeeStructure.structure_id == structure_id
            ).first()
            
            if not structure:
                raise ValueError("Fee structure not found")
            
            # Use structure due date if not provided
            if not due_date:
                due_date = structure.due_date or date.today() + timedelta(days=30)
            
            assignments = []
            
            for student_id in student_ids:
                # Check if assignment already exists
                existing = self.db.query(FeeAssignment).filter(
                    and_(
                        FeeAssignment.student_id == student_id,
                        FeeAssignment.structure_id == structure_id
                    )
                ).first()
                
                if existing:
                    continue  # Skip if already assigned
                
                # Calculate amounts
                assigned_amount = structure.base_amount
                total_discount = discount_amount + (assigned_amount * discount_percentage / 100)
                final_amount = max(0, assigned_amount - total_discount)
                
                assignment = FeeAssignment(
                    school_id=school_id,
                    student_id=student_id,
                    structure_id=structure_id,
                    assigned_amount=assigned_amount,
                    discount_amount=discount_amount,
                    discount_percentage=discount_percentage,
                    final_amount=final_amount,
                    balance_amount=final_amount,
                    due_date=due_date,
                    assigned_by=assigned_by
                )
                
                self.db.add(assignment)
                assignments.append(assignment)
            
            self.db.commit()
            
            for assignment in assignments:
                self.db.refresh(assignment)
            
            logger.info(f"Bulk assigned fees to {len(assignments)} students")
            return assignments
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error bulk assigning fees: {e}")
            raise
    
    def calculate_overdue_fees(self, school_id: int) -> Dict[str, Any]:
        """
        Calculate overdue fees and late charges
        """
        try:
            today = date.today()
            
            # Get overdue assignments
            overdue_assignments = self.db.query(FeeAssignment).filter(
                and_(
                    FeeAssignment.school_id == school_id,
                    FeeAssignment.due_date < today,
                    FeeAssignment.balance_amount > 0,
                    FeeAssignment.status.in_([FeeStatus.PENDING, FeeStatus.PARTIAL])
                )
            ).all()
            
            # Update status to overdue
            for assignment in overdue_assignments:
                assignment.status = FeeStatus.OVERDUE
                assignment.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # Calculate summary
            total_overdue = sum(a.balance_amount for a in overdue_assignments)
            students_affected = len(set(a.student_id for a in overdue_assignments))
            
            return {
                "total_overdue_amount": total_overdue,
                "overdue_assignments_count": len(overdue_assignments),
                "students_affected": students_affected,
                "assignments": [
                    {
                        "assignment_id": a.assignment_id,
                        "student_id": a.student_id,
                        "amount": a.balance_amount,
                        "days_overdue": (today - a.due_date).days
                    }
                    for a in overdue_assignments
                ]
            }
            
        except Exception as e:
            logger.error(f"Error calculating overdue fees: {e}")
            raise
    
    # === INVOICE MANAGEMENT ===
    
    def create_invoice_with_items(
        self,
        invoice_data: InvoiceCreate
    ) -> Invoice:
        """
        Create invoice with items
        """
        try:
            # Generate invoice number
            invoice_number = self._generate_invoice_number()
            
            # Calculate totals from items
            subtotal = sum(item.quantity * item.unit_price for item in invoice_data.items)
            total_amount = subtotal + invoice_data.tax_amount - invoice_data.discount_amount
            balance_amount = total_amount
            
            # Create invoice
            invoice_dict = invoice_data.dict()
            items_data = invoice_dict.pop('items', [])
            
            invoice = Invoice(
                **invoice_dict,
                invoice_number=invoice_number,
                subtotal=subtotal,
                total_amount=total_amount,
                balance_amount=balance_amount
            )
            
            self.db.add(invoice)
            self.db.flush()  # Get invoice ID
            
            # Create invoice items
            for item_data in items_data:
                item = InvoiceItem(
                    invoice_id=invoice.invoice_id,
                    **item_data,
                    total_price=item_data['quantity'] * item_data['unit_price']
                )
                self.db.add(item)
            
            self.db.commit()
            self.db.refresh(invoice)
            
            logger.info(f"Created invoice {invoice.invoice_number}")
            return invoice
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating invoice: {e}")
            raise
    
    def process_invoice_payment(
        self,
        invoice_id: int,
        amount_paid: float,
        payment_method: PaymentMethod,
        reference_number: Optional[str] = None,
        created_by: int = None
    ) -> Tuple[Invoice, Transaction]:
        """
        Process payment for an invoice
        """
        try:
            invoice = self.db.query(Invoice).filter(
                Invoice.invoice_id == invoice_id
            ).first()
            
            if not invoice:
                raise ValueError("Invoice not found")
            
            if invoice.status == InvoiceStatus.PAID:
                raise ValueError("Invoice already paid")
            
            if amount_paid > invoice.balance_amount:
                raise ValueError("Payment amount exceeds balance")
            
            # Update invoice
            invoice.paid_amount += amount_paid
            invoice.balance_amount -= amount_paid
            
            # Update status
            if invoice.balance_amount <= 0:
                invoice.status = InvoiceStatus.PAID
            
            invoice.updated_at = datetime.utcnow()
            
            # Create transaction
            revenue_account = self._get_revenue_account(invoice.school_id)
            
            transaction_data = TransactionCreate(
                school_id=invoice.school_id,
                account_id=revenue_account.account_id,
                transaction_type="income",
                amount=amount_paid,
                description=f"Payment for invoice {invoice.invoice_number}",
                reference_number=reference_number,
                payment_method=payment_method,
                invoice_id=invoice_id,
                created_by=created_by or 1
            )
            
            transaction = self.create_transaction(transaction_data)
            transaction.status = TransactionStatus.COMPLETED
            
            self.db.commit()
            
            self.db.refresh(invoice)
            self.db.refresh(transaction)
            
            logger.info(f"Processed payment for invoice {invoice.invoice_number}")
            return invoice, transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing invoice payment: {e}")
            raise
    
    # === REPORTING ===
    
    def generate_financial_summary(
        self,
        school_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> FinancialSummary:
        """
        Generate financial summary for dashboard
        """
        try:
            if not start_date:
                start_date = date.today().replace(day=1)  # Start of month
            if not end_date:
                end_date = date.today()
            
            # Income and expenses
            income_query = self.db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.school_id == school_id,
                    Transaction.transaction_type == "income",
                    Transaction.status == TransactionStatus.COMPLETED,
                    Transaction.transaction_date.between(start_date, end_date)
                )
            )
            
            expense_query = self.db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.school_id == school_id,
                    Transaction.transaction_type == "expense",
                    Transaction.status == TransactionStatus.COMPLETED,
                    Transaction.transaction_date.between(start_date, end_date)
                )
            )
            
            total_income = income_query.scalar() or 0.0
            total_expenses = expense_query.scalar() or 0.0
            net_income = total_income - total_expenses
            
            # Fee collections
            fee_collected_query = self.db.query(func.sum(FeePayment.amount_paid)).filter(
                and_(
                    FeePayment.school_id == school_id,
                    FeePayment.status == TransactionStatus.COMPLETED,
                    FeePayment.payment_date.between(start_date, end_date)
                )
            )
            
            collected_fees = fee_collected_query.scalar() or 0.0
            
            # Outstanding fees
            outstanding_query = self.db.query(func.sum(FeeAssignment.balance_amount)).filter(
                and_(
                    FeeAssignment.school_id == school_id,
                    FeeAssignment.balance_amount > 0
                )
            )
            
            outstanding_fees = outstanding_query.scalar() or 0.0
            
            # Pending invoices
            pending_invoices_query = self.db.query(func.sum(Invoice.balance_amount)).filter(
                and_(
                    Invoice.school_id == school_id,
                    Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE])
                )
            )
            
            pending_invoices = pending_invoices_query.scalar() or 0.0
            
            # Cash balance (simplified - from cash accounts)
            cash_account = self.db.query(Account).filter(
                and_(
                    Account.school_id == school_id,
                    Account.account_code == "1000"
                )
            ).first()
            
            cash_balance = 0.0
            if cash_account:
                cash_balance = self.get_account_balance(cash_account.account_id)
            
            return FinancialSummary(
                total_income=total_income,
                total_expenses=total_expenses,
                net_income=net_income,
                outstanding_fees=outstanding_fees,
                collected_fees=collected_fees,
                pending_invoices=pending_invoices,
                cash_balance=cash_balance
            )
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {e}")
            raise
    
    def generate_fee_summary(self, school_id: int) -> FeeSummary:
        """
        Generate fee collection summary
        """
        try:
            # Total assigned fees
            assigned_query = self.db.query(func.sum(FeeAssignment.final_amount)).filter(
                FeeAssignment.school_id == school_id
            )
            
            total_assigned = assigned_query.scalar() or 0.0
            
            # Total collected fees
            collected_query = self.db.query(func.sum(FeeAssignment.paid_amount)).filter(
                FeeAssignment.school_id == school_id
            )
            
            total_collected = collected_query.scalar() or 0.0
            
            # Outstanding fees
            outstanding_query = self.db.query(func.sum(FeeAssignment.balance_amount)).filter(
                and_(
                    FeeAssignment.school_id == school_id,
                    FeeAssignment.balance_amount > 0
                )
            )
            
            total_outstanding = outstanding_query.scalar() or 0.0
            
            # Overdue amount
            overdue_query = self.db.query(func.sum(FeeAssignment.balance_amount)).filter(
                and_(
                    FeeAssignment.school_id == school_id,
                    FeeAssignment.status == FeeStatus.OVERDUE
                )
            )
            
            overdue_amount = overdue_query.scalar() or 0.0
            
            # Students with outstanding balances
            students_query = self.db.query(func.count(func.distinct(FeeAssignment.student_id))).filter(
                and_(
                    FeeAssignment.school_id == school_id,
                    FeeAssignment.balance_amount > 0
                )
            )
            
            students_with_outstanding = students_query.scalar() or 0
            
            # Collection rate
            collection_rate = (total_collected / total_assigned * 100) if total_assigned > 0 else 0
            
            return FeeSummary(
                total_assigned=total_assigned,
                total_collected=total_collected,
                total_outstanding=total_outstanding,
                collection_rate=collection_rate,
                overdue_amount=overdue_amount,
                students_with_outstanding=students_with_outstanding
            )
            
        except Exception as e:
            logger.error(f"Error generating fee summary: {e}")
            raise
    
    # === HELPER METHODS ===
    
    def _generate_transaction_number(self) -> str:
        """Generate unique transaction number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"TXN{timestamp}{random_suffix}"
    
    def _generate_payment_number(self) -> str:
        """Generate unique payment number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"PAY{timestamp}{random_suffix}"
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:8].upper()
        return f"INV{timestamp}{random_suffix}"
    
    def _get_revenue_account(self, school_id: int) -> Account:
        """Get or create default revenue account"""
        account = self.db.query(Account).filter(
            and_(
                Account.school_id == school_id,
                Account.account_code == "4000"
            )
        ).first()
        
        if not account:
            # Create default revenue account
            account = Account(
                school_id=school_id,
                account_code="4000",
                account_name="Tuition Revenue",
                account_type=AccountType.REVENUE,
                created_by=1
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
        
        return account
