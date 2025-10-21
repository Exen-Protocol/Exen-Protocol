"""
Exen Protocol - Loan Approval, Funds Transfer & Collateral Management System
Handles USD stablecoin disbursement, Exen token collateral deposits, and escrow management
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import logging
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TransactionStatus(Enum):
    """Status of fund transfers"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COLLATERAL_LOCKED = "collateral_locked"
    FUNDS_DISBURSED = "funds_disbursed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EscrowStatus(Enum):
    """Status of collateral in escrow"""
    EMPTY = "empty"
    LOCKED = "locked"
    LIQUIDATION_IN_PROGRESS = "liquidation_in_progress"
    RELEASED = "released"


@dataclass
class CollateralDeposit:
    """Record of collateral deposited"""
    deposit_id: str
    loan_id: str
    wallet_address: str
    exen_amount: Decimal
    exen_price: Decimal
    collateral_value_usd: Decimal
    deposit_timestamp: datetime
    status: EscrowStatus
    locked_until: datetime
    health_factor: Decimal = Decimal('1.5')  # Liquidation at 1.0


@dataclass
class FundsTransfer:
    """Record of USD stablecoin transfer"""
    transfer_id: str
    loan_id: str
    from_address: str  # Lending pool
    to_address: str     # Borrower
    amount_usd: Decimal
    transfer_timestamp: datetime
    status: TransactionStatus
    block_hash: Optional[str] = None
    tx_hash: Optional[str] = None


@dataclass
class LoanAccount:
    """Borrower loan account"""
    loan_id: str
    wallet_address: str
    loan_amount_usd: Decimal
    interest_rate: Decimal
    collateral_amount_exen: Decimal
    collateral_price_usd: Decimal
    ltv_ratio: Decimal
    repayment_period_days: int
    origination_timestamp: datetime
    repayment_due_date: datetime
    status: TransactionStatus
    collateral_deposit: Optional[CollateralDeposit] = None
    funds_transfer: Optional[FundsTransfer] = None
    borrowed_amount_received: Decimal = Decimal(0)
    repaid_amount: Decimal = Decimal(0)
    accrued_interest: Decimal = Decimal(0)


@dataclass
class EscrowAccount:
    """Escrow/vault for collateral management"""
    vault_id: str
    location: str  # "escrow_vault"
    total_collateral_locked: Decimal = Decimal(0)
    deposits: Dict[str, CollateralDeposit] = field(default_factory=dict)
    status: EscrowStatus = EscrowStatus.EMPTY


class LoanFundsTransferSystem:
    """
    Manages approved loan execution including:
    - USD stablecoin disbursement
    - Exen token collateral deposits
    - Escrow management
    - Fund transfers and tracking
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the funds transfer system
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.loan_accounts: Dict[str, LoanAccount] = {}
        self.escrow_vault = EscrowAccount(vault_id="EXEN_ESCROW_001", location="escrow_vault")
        self.fund_transfers: List[FundsTransfer] = []
        self.collateral_deposits: List[CollateralDeposit] = []
        self.transaction_counter = 0
        self.loan_counter = 0
        
        # Pool configuration
        self.lending_pool_balance = Decimal(100000)  # USD available
        self.lending_pool_address = "EXEN_LENDING_POOL_ADDRESS"
        
        logger.info("Loan Funds Transfer System initialized")
        logger.info(f"Lending Pool Balance: ${self.lending_pool_balance}")
    
    def create_loan_account(
        self,
        wallet_address: str,
        loan_amount_usd: Decimal,
        interest_rate: Decimal,
        collateral_amount_exen: Decimal,
        collateral_price_usd: Decimal,
        ltv_ratio: Decimal,
        repayment_days: int
    ) -> LoanAccount:
        """
        Create a new loan account for an approved borrower
        
        Args:
            wallet_address: Borrower's wallet
            loan_amount_usd: Loan amount in USD
            interest_rate: APY interest rate
            collateral_amount_exen: Exen tokens as collateral
            collateral_price_usd: Current Exen price
            ltv_ratio: Loan-to-value ratio
            repayment_days: Repayment period
            
        Returns:
            LoanAccount object
        """
        self.loan_counter += 1
        loan_id = f"LOAN_{self.loan_counter}"
        
        repayment_due = datetime.now() + timedelta(days=repayment_days)
        
        loan = LoanAccount(
            loan_id=loan_id,
            wallet_address=wallet_address,
            loan_amount_usd=loan_amount_usd,
            interest_rate=interest_rate,
            collateral_amount_exen=collateral_amount_exen,
            collateral_price_usd=collateral_price_usd,
            ltv_ratio=ltv_ratio,
            repayment_period_days=repayment_days,
            origination_timestamp=datetime.now(),
            repayment_due_date=repayment_due,
            status=TransactionStatus.PENDING
        )
        
        self.loan_accounts[loan_id] = loan
        
        if self.verbose:
            logger.info(
                f"Created loan account {loan_id}\n"
                f"  Borrower: {wallet_address}\n"
                f"  Amount: ${loan_amount_usd}\n"
                f"  Rate: {interest_rate}%\n"
                f"  Collateral: {collateral_amount_exen} EXEN @ ${collateral_price_usd}"
            )
        
        return loan
    
    def deposit_collateral(
        self,
        loan_id: str,
        exen_amount: Decimal,
        current_price: Decimal
    ) -> Optional[CollateralDeposit]:
        """
        Process Exen token collateral deposit to escrow
        
        Args:
            loan_id: Loan ID
            exen_amount: Amount of Exen tokens
            current_price: Current Exen price
            
        Returns:
            CollateralDeposit record or None if failed
        """
        if loan_id not in self.loan_accounts:
            logger.warning(f"Loan not found: {loan_id}")
            return None
        
        loan = self.loan_accounts[loan_id]
        
        if exen_amount != loan.collateral_amount_exen:
            logger.warning(
                f"Collateral amount mismatch: {exen_amount} vs required {loan.collateral_amount_exen}"
            )
            return None
        
        collateral_value = exen_amount * current_price
        
        deposit_id = f"DEPOSIT_{self.transaction_counter}"
        self.transaction_counter += 1
        
        locked_until = datetime.now() + timedelta(days=loan.repayment_period_days + 30)
        
        deposit = CollateralDeposit(
            deposit_id=deposit_id,
            loan_id=loan_id,
            wallet_address=loan.wallet_address,
            exen_amount=exen_amount,
            exen_price=current_price,
            collateral_value_usd=collateral_value,
            deposit_timestamp=datetime.now(),
            status=EscrowStatus.LOCKED,
            locked_until=locked_until
        )
        
        # Add to escrow vault
        self.escrow_vault.deposits[deposit_id] = deposit
        self.escrow_vault.total_collateral_locked += collateral_value
        self.escrow_vault.status = EscrowStatus.LOCKED
        
        # Link to loan
        loan.collateral_deposit = deposit
        loan.status = TransactionStatus.COLLATERAL_LOCKED
        
        self.collateral_deposits.append(deposit)
        
        if self.verbose:
            logger.info(
                f"COLLATERAL DEPOSITED TO ESCROW\n"
                f"  Deposit ID: {deposit_id}\n"
                f"  Loan: {loan_id}\n"
                f"  Amount: {exen_amount} EXEN\n"
                f"  Price: ${current_price}\n"
                f"  Value: ${collateral_value}\n"
                f"  Status: LOCKED\n"
                f"  Escrow Vault Total: ${self.escrow_vault.total_collateral_locked}"
            )
        
        return deposit
    
    def verify_collateral_health(self, loan_id: str, current_exen_price: Decimal) -> Tuple[bool, Decimal]:
        """
        Check collateral health factor
        
        Liquidation occurs when health_factor < 1.0
        Health Factor = Collateral Value / Loan Amount
        
        Args:
            loan_id: Loan to check
            current_exen_price: Current Exen price
            
        Returns:
            Tuple of (is_healthy, health_factor)
        """
        if loan_id not in self.loan_accounts:
            return False, Decimal(0)
        
        loan = self.loan_accounts[loan_id]
        
        if not loan.collateral_deposit:
            return False, Decimal(0)
        
        current_collateral_value = loan.collateral_amount_exen * current_exen_price
        health_factor = current_collateral_value / loan.loan_amount_usd
        
        is_healthy = health_factor >= Decimal('1.0')
        
        if self.verbose and not is_healthy:
            logger.warning(
                f"COLLATERAL HEALTH ALERT - Loan {loan_id}\n"
                f"  Health Factor: {health_factor:.2f} (< 1.0)\n"
                f"  Collateral Value: ${current_collateral_value}\n"
                f"  Loan Amount: ${loan.loan_amount_usd}\n"
                f"  Action: LIQUIDATION REQUIRED"
            )
        
        return is_healthy, health_factor
    
    def disburse_funds(self, loan_id: str) -> Optional[FundsTransfer]:
        """
        Disburse approved loan funds to borrower
        
        Prerequisites:
        - Collateral must be locked
        - Lending pool must have sufficient funds
        
        Args:
            loan_id: Loan to disburse
            
        Returns:
            FundsTransfer record or None if failed
        """
        if loan_id not in self.loan_accounts:
            logger.warning(f"Loan not found: {loan_id}")
            return None
        
        loan = self.loan_accounts[loan_id]
        
        # Verify collateral is locked
        if loan.status != TransactionStatus.COLLATERAL_LOCKED:
            logger.warning(f"Cannot disburse - loan status is {loan.status}, must be COLLATERAL_LOCKED")
            return None
        
        # Verify sufficient funds in pool
        if self.lending_pool_balance < loan.loan_amount_usd:
            logger.warning(
                f"Insufficient lending pool balance: ${self.lending_pool_balance} < ${loan.loan_amount_usd}"
            )
            return None
        
        transfer_id = f"TRANSFER_{self.transaction_counter}"
        self.transaction_counter += 1
        
        transfer = FundsTransfer(
            transfer_id=transfer_id,
            loan_id=loan_id,
            from_address=self.lending_pool_address,
            to_address=loan.wallet_address,
            amount_usd=loan.loan_amount_usd,
            transfer_timestamp=datetime.now(),
            status=TransactionStatus.IN_PROGRESS
        )
        
        # Simulate transaction processing
        transfer.tx_hash = self._generate_tx_hash(transfer)
        transfer.status = TransactionStatus.FUNDS_DISBURSED
        
        # Update pool balance
        self.lending_pool_balance -= loan.loan_amount_usd
        
        # Update loan
        loan.borrowed_amount_received = loan.loan_amount_usd
        loan.funds_transfer = transfer
        loan.status = TransactionStatus.FUNDS_DISBURSED
        
        self.fund_transfers.append(transfer)
        
        if self.verbose:
            logger.info(
                f"FUNDS DISBURSED\n"
                f"  Transfer ID: {transfer_id}\n"
                f"  Loan: {loan_id}\n"
                f"  From: {transfer.from_address[:16]}...\n"
                f"  To: {transfer.to_address}\n"
                f"  Amount: ${transfer.amount_usd}\n"
                f"  TX Hash: {transfer.tx_hash[:16]}...\n"
                f"  Remaining Pool Balance: ${self.lending_pool_balance}"
            )
        
        return transfer
    
    def complete_loan_setup(
        self,
        loan_id: str,
        exen_amount: Decimal,
        current_exen_price: Decimal
    ) -> Tuple[bool, str]:
        """
        Execute complete loan approval workflow:
        1. Deposit collateral
        2. Disburse funds
        
        Args:
            loan_id: Loan to setup
            exen_amount: Collateral amount
            current_exen_price: Current price
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"INITIATING LOAN APPROVAL WORKFLOW - {loan_id}")
        logger.info(f"{'='*70}")
        
        # Step 1: Deposit collateral
        logger.info(f"\nStep 1: Depositing collateral...")
        deposit = self.deposit_collateral(loan_id, exen_amount, current_exen_price)
        
        if not deposit:
            error_msg = "Failed to deposit collateral"
            logger.error(error_msg)
            return False, error_msg
        
        # Step 2: Verify collateral
        logger.info(f"\nStep 2: Verifying collateral health...")
        is_healthy, health_factor = self.verify_collateral_health(loan_id, current_exen_price)
        
        if not is_healthy:
            error_msg = f"Collateral health check failed: {health_factor}"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"  Health Factor: {health_factor:.2f} (Healthy)")
        
        # Step 3: Disburse funds
        logger.info(f"\nStep 3: Disbursing USD funds...")
        transfer = self.disburse_funds(loan_id)
        
        if not transfer:
            error_msg = "Failed to disburse funds"
            logger.error(error_msg)
            return False, error_msg
        
        # Mark as completed
        loan = self.loan_accounts[loan_id]
        loan.status = TransactionStatus.COMPLETED
        
        success_msg = f"Loan {loan_id} approved and funded successfully"
        
        logger.info(f"\n{'='*70}")
        logger.info("LOAN APPROVAL WORKFLOW COMPLETED")
        logger.info(f"{'='*70}\n")
        
        return True, success_msg
    
    def process_repayment(
        self,
        loan_id: str,
        repayment_amount_usd: Decimal,
        from_address: str
    ) -> bool:
        """
        Process loan repayment and release collateral
        
        Args:
            loan_id: Loan being repaid
            repayment_amount_usd: Repayment amount
            from_address: Borrower address
            
        Returns:
            True if successful
        """
        if loan_id not in self.loan_accounts:
            logger.warning(f"Loan not found: {loan_id}")
            return False
        
        loan = self.loan_accounts[loan_id]
        
        # Calculate accrued interest
        days_outstanding = (datetime.now() - loan.origination_timestamp).days
        accrued_interest = (
            loan.loan_amount_usd * 
            (loan.interest_rate / Decimal(100)) * 
            (Decimal(days_outstanding) / Decimal(365))
        )
        
        total_owed = loan.loan_amount_usd + accrued_interest
        
        if repayment_amount_usd < total_owed:
            logger.warning(
                f"Insufficient repayment: ${repayment_amount_usd} < ${total_owed} owed"
            )
            return False
        
        # Update loan
        loan.repaid_amount = repayment_amount_usd
        loan.accrued_interest = accrued_interest
        
        # Release collateral
        if loan.collateral_deposit:
            deposit = loan.collateral_deposit
            deposit.status = EscrowStatus.RELEASED
            self.escrow_vault.total_collateral_locked -= deposit.collateral_value_usd
        
        # Add funds back to pool
        self.lending_pool_balance += repayment_amount_usd
        
        if self.verbose:
            logger.info(
                f"LOAN REPAYMENT PROCESSED\n"
                f"  Loan: {loan_id}\n"
                f"  Principal: ${loan.loan_amount_usd}\n"
                f"  Interest: ${accrued_interest:.2f}\n"
                f"  Total Repaid: ${repayment_amount_usd}\n"
                f"  Collateral Released: {loan.collateral_amount_exen} EXEN\n"
                f"  Pool Balance: ${self.lending_pool_balance}"
            )
        
        return True
    
    def _generate_tx_hash(self, transfer: FundsTransfer) -> str:
        """Generate simulated transaction hash"""
        data = f"{transfer.transfer_id}{transfer.timestamp.isoformat()}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def get_loan_details(self, loan_id: str) -> Optional[Dict]:
        """Get complete loan details"""
        if loan_id not in self.loan_accounts:
            return None
        
        loan = self.loan_accounts[loan_id]
        
        return {
            "loan_id": loan.loan_id,
            "status": loan.status.value,
            "borrower": loan.wallet_address,
            "loan_amount": str(loan.loan_amount_usd),
            "interest_rate": str(loan.interest_rate),
            "collateral_amount": str(loan.collateral_amount_exen),
            "collateral_value": str(loan.collateral_amount_exen * loan.collateral_price_usd),
            "ltv_ratio": str(loan.ltv_ratio),
            "originated": loan.origination_timestamp.isoformat(),
            "due_date": loan.repayment_due_date.isoformat(),
            "borrowed_received": str(loan.borrowed_amount_received),
            "repaid": str(loan.repaid_amount),
            "accrued_interest": str(loan.accrued_interest)
        }
    
    def get_escrow_status(self) -> Dict:
        """Get escrow vault status"""
        return {
            "vault_id": self.escrow_vault.vault_id,
            "status": self.escrow_vault.status.value,
            "total_collateral_locked": str(self.escrow_vault.total_collateral_locked),
            "active_deposits": len([d for d in self.escrow_vault.deposits.values() if d.status == EscrowStatus.LOCKED]),
            "deposits": {
                deposit_id: {
                    "loan_id": deposit.loan_id,
                    "exen_amount": str(deposit.exen_amount),
                    "value_usd": str(deposit.collateral_value_usd),
                    "status": deposit.status.value,
                    "locked_until": deposit.locked_until.isoformat()
                }
                for deposit_id, deposit in self.escrow_vault.deposits.items()
            }
        }
    
    def get_pool_status(self) -> Dict:
        """Get lending pool status"""
        total_disbursed = sum(
            transfer.amount_usd for transfer in self.fund_transfers
            if transfer.status == TransactionStatus.FUNDS_DISBURSED
        )
        
        return {
            "lending_pool_balance": str(self.lending_pool_balance),
            "total_disbursed": str(total_disbursed),
            "active_loans": len([l for l in self.loan_accounts.values() if l.status != TransactionStatus.COMPLETED]),
            "completed_loans": len([l for l in self.loan_accounts.values() if l.status == TransactionStatus.COMPLETED]),
            "transfers_processed": len(self.fund_transfers)
        }


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("EXEN PROTOCOL - LOAN APPROVAL & FUNDS TRANSFER SYSTEM DEMO")
    print("="*70 + "\n")
    
    system = LoanFundsTransferSystem(verbose=True)
    
    # Create approved loan accounts
    print("\n--- CREATING APPROVED LOAN ACCOUNTS ---\n")
    
    loan1 = system.create_loan_account(
        wallet_address="BorrowerWallet1111111111111111111111111",
        loan_amount_usd=Decimal("5000"),
        interest_rate=Decimal("10.0"),
        collateral_amount_exen=Decimal("100000"),
        collateral_price_usd=Decimal("0.10"),
        ltv_ratio=Decimal("60"),
        repayment_days=180
    )
    
    loan2 = system.create_loan_account(
        wallet_address="BorrowerWallet2222222222222222222222222",
        loan_amount_usd=Decimal("2000"),
        interest_rate=Decimal("12.0"),
        collateral_amount_exen=Decimal("40000"),
        collateral_price_usd=Decimal("0.10"),
        ltv_ratio=Decimal("50"),
        repayment_days=180
    )
    
    # Execute complete loan workflows
    print("\n--- EXECUTING LOAN APPROVAL WORKFLOWS ---\n")
    
    success1, msg1 = system.complete_loan_setup(
        loan1.loan_id,
        Decimal("100000"),
        Decimal("0.10")
    )
    
    success2, msg2 = system.complete_loan_setup(
        loan2.loan_id,
        Decimal("40000"),
        Decimal("0.10")
    )
    
    # Print system status
    print("\n" + "="*70)
    print("SYSTEM STATUS")
    print("="*70 + "\n")
    
    print("--- LENDING POOL STATUS ---")
    pool_status = system.get_pool_status()
    for key, value in pool_status.items():
        print(f"{key}: {value}")
    
    print("\n--- ESCROW VAULT STATUS ---")
    escrow_status = system.get_escrow_status()
    print(f"Vault: {escrow_status['vault_id']}")
    print(f"Status: {escrow_status['status']}")
    print(f"Total Collateral Locked: ${escrow_status['total_collateral_locked']}")
    print(f"Active Deposits: {escrow_status['active_deposits']}")
    
    print("\n--- LOAN DETAILS ---")
    for loan_id in [loan1.loan_id, loan2.loan_id]:
        details = system.get_loan_details(loan_id)
        print(f"\n{loan_id}:")
        for key, value in details.items():
            print(f"  {key}: {value}")
    
    # Simulate repayment
    print("\n" + "="*70)
    print("PROCESSING LOAN REPAYMENT")
    print("="*70 + "\n")
    
    system.process_repayment(
        loan1.loan_id,
        Decimal("5500"),  # Principal + interest
        "BorrowerWallet1111111111111111111111111"
    )
    
    print("\n--- FINAL POOL STATUS ---")
    final_pool = system.get_pool_status()
    for key, value in final_pool.items():
        print(f"{key}: {value}")
