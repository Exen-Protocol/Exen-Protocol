
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import logging
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CreditRating(Enum):
    """Credit rating classification"""
    EXCELLENT = "excellent"    # 750+
    VERY_GOOD = "very_good"    # 650-749
    GOOD = "good"              # 550-649
    FAIR = "fair"              # 450-549
    POOR = "poor"              # <450


class TransactionType(Enum):
    """Types of transactions"""
    INFLOW = "inflow"          # Money coming in
    OUTFLOW = "outflow"        # Money going out
    INTERNAL = "internal"      # Transfers between own wallets


@dataclass
class Transaction:
    """Represents a single transaction"""
    tx_hash: str
    timestamp: datetime
    amount: Decimal
    transaction_type: TransactionType
    counterparty: str  # Address transaction is with
    description: str
    is_successful: bool


@dataclass
class WalletMetrics:
    """Key metrics for wallet analysis"""
    total_inflow: Decimal = Decimal(0)
    total_outflow: Decimal = Decimal(0)
    net_flow: Decimal = Decimal(0)
    inflow_count: int = 0
    outflow_count: int = 0
    avg_inflow: Decimal = Decimal(0)
    avg_outflow: Decimal = Decimal(0)
    transaction_count: int = 0
    success_rate: Decimal = Decimal(100)
    current_balance: Decimal = Decimal(0)


@dataclass
class CredibilityFactors:
    """Factors that contribute to credit score"""
    transaction_volume_score: Decimal  # 0-20
    payment_consistency_score: Decimal  # 0-20
    inflow_reliability_score: Decimal  # 0-20
    balance_stability_score: Decimal  # 0-20
    transaction_success_rate_score: Decimal  # 0-20
    account_age_score: Decimal  # 0-20 (reserve)


@dataclass
class CreditScoreReport:
    """Complete credit score report for a wallet"""
    wallet_address: str
    credit_score: Decimal  # 300-850
    credit_rating: CreditRating
    borrow_limit_usd: Decimal  # Recommended lending limit
    interest_rate_adjustment: Decimal  # % adjustment from base rate
    metrics: WalletMetrics
    credibility_factors: CredibilityFactors
    analysis_timestamp: datetime
    recommendation: str


class SolanaWalletAnalyzer:
    """
    Analyzes Solana wallet transaction history
    Generates credit scores based on on-chain behavior
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the wallet analyzer
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.wallets: Dict[str, Dict] = {}
        self.base_interest_rate = Decimal('8.0')  # 8% base APY
        self.max_interest_rate = Decimal('18.0')  # 18% max APY
        
        logger.info("Solana Wallet Analyzer initialized")
    
    def add_wallet(self, wallet_address: str, current_balance: Decimal) -> None:
        """
        Register a wallet for analysis
        
        Args:
            wallet_address: Solana wallet public key
            current_balance: Current SOL balance
        """
        if not isinstance(current_balance, Decimal):
            current_balance = Decimal(str(current_balance))
        
        self.wallets[wallet_address] = {
            "address": wallet_address,
            "current_balance": current_balance,
            "transactions": [],
            "created_at": datetime.now()
        }
        
        logger.info(f"Registered wallet: {wallet_address}")
    
    def add_transaction(
        self,
        wallet_address: str,
        tx_hash: str,
        timestamp: datetime,
        amount: Decimal,
        transaction_type: str,
        counterparty: str,
        description: str = "",
        is_successful: bool = True
    ) -> bool:
        """
        Add a transaction to wallet history
        
        Args:
            wallet_address: Wallet being analyzed
            tx_hash: Transaction hash
            timestamp: When transaction occurred
            amount: Amount in SOL or USD
            transaction_type: "inflow", "outflow", or "internal"
            counterparty: Address transaction is with
            description: Transaction description
            is_successful: Whether transaction succeeded
            
        Returns:
            True if successful, False otherwise
        """
        if wallet_address not in self.wallets:
            logger.warning(f"Wallet not found: {wallet_address}")
            return False
        
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        try:
            tx_type = TransactionType(transaction_type)
        except ValueError:
            logger.warning(f"Invalid transaction type: {transaction_type}")
            return False
        
        transaction = Transaction(
            tx_hash=tx_hash,
            timestamp=timestamp,
            amount=amount,
            transaction_type=tx_type,
            counterparty=counterparty,
            description=description,
            is_successful=is_successful
        )
        
        self.wallets[wallet_address]["transactions"].append(transaction)
        
        if self.verbose:
            logger.debug(f"Added transaction: {tx_hash[:8]}... | {amount} {transaction_type}")
        
        return True
    
    def _calculate_wallet_metrics(self, wallet_address: str) -> WalletMetrics:
        """
        Calculate key metrics for a wallet
        
        Args:
            wallet_address: Wallet to analyze
            
        Returns:
            WalletMetrics object
        """
        if wallet_address not in self.wallets:
            return WalletMetrics()
        
        wallet_data = self.wallets[wallet_address]
        transactions = wallet_data["transactions"]
        
        metrics = WalletMetrics()
        metrics.current_balance = wallet_data["current_balance"]
        
        if not transactions:
            return metrics
        
        # Calculate flows
        inflows = [tx for tx in transactions if tx.transaction_type == TransactionType.INFLOW]
        outflows = [tx for tx in transactions if tx.transaction_type == TransactionType.OUTFLOW]
        
        metrics.total_inflow = sum(tx.amount for tx in inflows)
        metrics.total_outflow = sum(tx.amount for tx in outflows)
        metrics.net_flow = metrics.total_inflow - metrics.total_outflow
        
        metrics.inflow_count = len(inflows)
        metrics.outflow_count = len(outflows)
        metrics.transaction_count = len(transactions)
        
        # Calculate averages
        metrics.avg_inflow = metrics.total_inflow / max(metrics.inflow_count, 1)
        metrics.avg_outflow = metrics.total_outflow / max(metrics.outflow_count, 1)
        
        # Calculate success rate
        successful = len([tx for tx in transactions if tx.is_successful])
        metrics.success_rate = Decimal(successful) / Decimal(len(transactions)) * Decimal(100)
        
        return metrics
    
    def _calculate_transaction_volume_score(self, metrics: WalletMetrics) -> Decimal:
        """
        Score based on transaction volume
        Higher volume = better credit (indicates active trading/usage)
        Scale: 0-20
        """
        total_volume = metrics.total_inflow + metrics.total_outflow
        
        if total_volume < Decimal('100'):
            return Decimal(2)
        elif total_volume < Decimal('500'):
            return Decimal(5)
        elif total_volume < Decimal('1000'):
            return Decimal(10)
        elif total_volume < Decimal('5000'):
            return Decimal(15)
        else:
            return Decimal(20)
    
    def _calculate_payment_consistency_score(self, metrics: WalletMetrics) -> Decimal:
        """
        Score based on payment patterns
        Regular, consistent payments = better credit
        Scale: 0-20
        """
        if metrics.transaction_count < 3:
            return Decimal(2)
        
        if metrics.outflow_count == 0:
            return Decimal(5)  # No outflows is suspicious
        
        # Calculate consistency: regular intervals = higher score
        consistency_ratio = Decimal(metrics.inflow_count) / Decimal(metrics.outflow_count)
        
        if consistency_ratio >= Decimal('1.5'):  # More inflows than outflows
            return Decimal(18)
        elif consistency_ratio >= Decimal('1.0'):
            return Decimal(15)
        elif consistency_ratio >= Decimal('0.7'):
            return Decimal(12)
        elif consistency_ratio >= Decimal('0.5'):
            return Decimal(8)
        else:
            return Decimal(4)
    
    def _calculate_inflow_reliability_score(self, metrics: WalletMetrics) -> Decimal:
        """
        Score based on inflow reliability
        Consistent, regular inflows = better credit
        Scale: 0-20
        """
        if metrics.total_inflow == 0:
            return Decimal(2)
        
        if metrics.inflow_count < 2:
            return Decimal(5)
        
        # Calculate inflow stability (lower variance = more reliable)
        inflow_values = [
            tx.amount for tx in self.wallets[self._current_wallet]["transactions"]
            if tx.transaction_type == TransactionType.INFLOW
        ]
        
        if len(inflow_values) < 2:
            return Decimal(10)
        
        mean_inflow = metrics.avg_inflow
        variance = sum((x - mean_inflow) ** 2 for x in inflow_values) / len(inflow_values)
        
        # Coefficient of variation
        if mean_inflow == 0:
            return Decimal(5)
        
        cv = (variance.sqrt() / mean_inflow) if variance > 0 else Decimal(0)
        
        if cv < Decimal('0.2'):  # Very consistent
            return Decimal(18)
        elif cv < Decimal('0.5'):
            return Decimal(15)
        elif cv < Decimal('1.0'):
            return Decimal(12)
        else:
            return Decimal(8)
    
    def _calculate_balance_stability_score(self, metrics: WalletMetrics) -> Decimal:
        """
        Score based on balance stability
        Positive net flow and healthy balance = better credit
        Scale: 0-20
        """
        if metrics.net_flow <= 0:
            return Decimal(5)  # Negative or zero net flow is risky
        
        if metrics.current_balance <= 0:
            return Decimal(2)  # No balance
        
        # Ratio of balance to average outflow
        if metrics.avg_outflow == 0:
            balance_ratio = Decimal(100)
        else:
            balance_ratio = metrics.current_balance / metrics.avg_outflow
        
        if balance_ratio >= Decimal(10):
            return Decimal(20)  # Very healthy
        elif balance_ratio >= Decimal(5):
            return Decimal(16)
        elif balance_ratio >= Decimal(2):
            return Decimal(12)
        elif balance_ratio >= Decimal(1):
            return Decimal(8)
        else:
            return Decimal(4)
    
    def _calculate_transaction_success_rate_score(self, metrics: WalletMetrics) -> Decimal:
        """
        Score based on transaction success rate
        Higher success rate = lower risk
        Scale: 0-20
        """
        success_rate = metrics.success_rate
        
        if success_rate >= Decimal('98'):
            return Decimal(20)
        elif success_rate >= Decimal('95'):
            return Decimal(16)
        elif success_rate >= Decimal('90'):
            return Decimal(12)
        elif success_rate >= Decimal('80'):
            return Decimal(8)
        else:
            return Decimal(2)
    
    def _calculate_account_age_score(self, wallet_address: str) -> Decimal:
        """
        Score based on account age
        Older accounts = more trustworthy
        Scale: 0-20 (reserved for future use)
        """
        wallet_data = self.wallets[wallet_address]
        created_at = wallet_data["created_at"]
        age_days = (datetime.now() - created_at).days
        
        if age_days >= 365:
            return Decimal(20)
        elif age_days >= 180:
            return Decimal(15)
        elif age_days >= 90:
            return Decimal(10)
        elif age_days >= 30:
            return Decimal(5)
        else:
            return Decimal(2)
    
    def generate_credit_score(self, wallet_address: str) -> Optional[CreditScoreReport]:
        """
        Generate a complete credit score for a wallet
        
        Args:
            wallet_address: Wallet to analyze
            
        Returns:
            CreditScoreReport or None if wallet not found
        """
        if wallet_address not in self.wallets:
            logger.warning(f"Wallet not found: {wallet_address}")
            return None
        
        self._current_wallet = wallet_address
        
        # Calculate metrics
        metrics = self._calculate_wallet_metrics(wallet_address)
        
        # Calculate credibility factors (each 0-20)
        credibility_factors = CredibilityFactors(
            transaction_volume_score=self._calculate_transaction_volume_score(metrics),
            payment_consistency_score=self._calculate_payment_consistency_score(metrics),
            inflow_reliability_score=self._calculate_inflow_reliability_score(metrics),
            balance_stability_score=self._calculate_balance_stability_score(metrics),
            transaction_success_rate_score=self._calculate_transaction_success_rate_score(metrics),
            account_age_score=self._calculate_account_age_score(wallet_address)
        )
        
        # Calculate total credit score (0-100, scaled to 300-850)
        total_score = (
            credibility_factors.transaction_volume_score +
            credibility_factors.payment_consistency_score +
            credibility_factors.inflow_reliability_score +
            credibility_factors.balance_stability_score +
            credibility_factors.transaction_success_rate_score
        ) / Decimal(5)  # Average of 5 factors
        
        # Scale from 0-20 to 300-850
        credit_score = Decimal(300) + (total_score / Decimal(20)) * Decimal(550)
        credit_score = credit_score.quantize(Decimal('0'))
        
        # Determine rating
        if credit_score >= Decimal(750):
            rating = CreditRating.EXCELLENT
        elif credit_score >= Decimal(650):
            rating = CreditRating.VERY_GOOD
        elif credit_score >= Decimal(550):
            rating = CreditRating.GOOD
        elif credit_score >= Decimal(450):
            rating = CreditRating.FAIR
        else:
            rating = CreditRating.POOR
        
        # Calculate borrow limit (USD)
        base_borrow_limit = Decimal(1000)
        borrow_limit = base_borrow_limit * (credit_score / Decimal(850))
        borrow_limit = borrow_limit.quantize(Decimal('1'))
        
        # Calculate interest rate adjustment
        if rating == CreditRating.EXCELLENT:
            rate_adjustment = Decimal('-1.5')
        elif rating == CreditRating.VERY_GOOD:
            rate_adjustment = Decimal('-0.5')
        elif rating == CreditRating.GOOD:
            rate_adjustment = Decimal('0.0')
        elif rating == CreditRating.FAIR:
            rate_adjustment = Decimal('2.0')
        else:
            rate_adjustment = Decimal('5.0')
        
        # Calculate actual interest rate
        actual_rate = self.base_interest_rate + rate_adjustment
        actual_rate = min(actual_rate, self.max_interest_rate)
        actual_rate = max(actual_rate, Decimal('5.0'))  # Minimum 5%
        
        # Generate recommendation
        if rating == CreditRating.EXCELLENT:
            recommendation = "Excellent on-chain history. Eligible for maximum borrowing at favorable rates."
        elif rating == CreditRating.VERY_GOOD:
            recommendation = "Very good on-chain behavior. Eligible for substantial borrowing with competitive rates."
        elif rating == CreditRating.GOOD:
            recommendation = "Good transaction history. Standard borrowing rates apply."
        elif rating == CreditRating.FAIR:
            recommendation = "Fair on-chain activity. Limited borrowing available at higher rates."
        else:
            recommendation = "Poor transaction history. Not recommended for lending at this time. Build more on-chain activity."
        
        report = CreditScoreReport(
            wallet_address=wallet_address,
            credit_score=credit_score,
            credit_rating=rating,
            borrow_limit_usd=borrow_limit,
            interest_rate_adjustment=rate_adjustment,
            metrics=metrics,
            credibility_factors=credibility_factors,
            analysis_timestamp=datetime.now(),
            recommendation=recommendation
        )
        
        if self.verbose:
            self._print_credit_report(report, actual_rate)
        
        return report
    
    def _print_credit_report(self, report: CreditScoreReport, actual_rate: Decimal) -> None:
        """Print a formatted credit report"""
        logger.info("\n" + "="*70)
        logger.info("ON-CHAIN CREDIT SCORE REPORT")
        logger.info("="*70)
        logger.info(f"\nWallet: {report.wallet_address}")
        logger.info(f"Analysis Date: {report.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        logger.info(f"\n{'CREDIT SCORE':-^70}")
        logger.info(f"Score: {report.credit_score} | Rating: {report.credit_rating.value.upper()}")
        logger.info(f"Borrow Limit: ${report.borrow_limit_usd}")
        logger.info(f"Interest Rate: {actual_rate}% APY (Base: {self.base_interest_rate}%, Adjustment: {report.interest_rate_adjustment:+.1f}%)")
        
        logger.info(f"\n{'TRANSACTION METRICS':-^70}")
        logger.info(f"Total Inflow: ${report.metrics.total_inflow} ({report.metrics.inflow_count} transactions)")
        logger.info(f"Total Outflow: ${report.metrics.total_outflow} ({report.metrics.outflow_count} transactions)")
        logger.info(f"Net Flow: ${report.metrics.net_flow}")
        logger.info(f"Current Balance: ${report.metrics.current_balance}")
        logger.info(f"Total Transactions: {report.metrics.transaction_count}")
        logger.info(f"Success Rate: {report.metrics.success_rate:.1f}%")
        logger.info(f"Average Inflow: ${report.metrics.avg_inflow}")
        logger.info(f"Average Outflow: ${report.metrics.avg_outflow}")
        
        logger.info(f"\n{'CREDIBILITY FACTORS (0-20 each)':-^70}")
        logger.info(f"Transaction Volume: {report.credibility_factors.transaction_volume_score}/20")
        logger.info(f"Payment Consistency: {report.credibility_factors.payment_consistency_score}/20")
        logger.info(f"Inflow Reliability: {report.credibility_factors.inflow_reliability_score}/20")
        logger.info(f"Balance Stability: {report.credibility_factors.balance_stability_score}/20")
        logger.info(f"Transaction Success: {report.credibility_factors.transaction_success_rate_score}/20")
        
        logger.info(f"\n{'RECOMMENDATION':-^70}")
        logger.info(report.recommendation)
        logger.info("="*70 + "\n")


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("EXEN PROTOCOL - ON-CHAIN CREDIT SCORE SYSTEM DEMO")
    print("="*70 + "\n")
    
    # Initialize analyzer
    analyzer = SolanaWalletAnalyzer(verbose=True)
    
    # Register test wallets
    wallet1 = "DemoWallet1111111111111111111111111111111"
    wallet2 = "DemoWallet2222222222222222222222222222222"
    
    analyzer.add_wallet(wallet1, Decimal("50"))
    analyzer.add_wallet(wallet2, Decimal("10"))
    
    # Simulate excellent wallet (consistent inflows, good balance)
    print("\n--- SIMULATING WALLET 1: EXCELLENT HISTORY ---\n")
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(10):
        # Regular inflows
        analyzer.add_transaction(
            wallet1,
            f"inflow_{i}",
            base_time + timedelta(days=i*3),
            Decimal("5"),
            "inflow",
            "PaymentProcessor1",
            "Regular income",
            True
        )
        
        # Some outflows
        if i % 2 == 0:
            analyzer.add_transaction(
                wallet1,
                f"outflow_{i}",
                base_time + timedelta(days=i*3+1),
                Decimal("2"),
                "outflow",
                "Vendor1",
                "Purchase",
                True
            )
    
    # Simulate fair wallet (inconsistent, small balance)
    print("\n--- SIMULATING WALLET 2: FAIR HISTORY ---\n")
    
    analyzer.add_transaction(wallet2, "tx1", base_time, Decimal("20"), "inflow", "Source1", "Large deposit", True)
    analyzer.add_transaction(wallet2, "tx2", base_time + timedelta(days=5), Decimal("15"), "outflow", "Buyer1", "Large withdrawal", True)
    analyzer.add_transaction(wallet2, "tx3", base_time + timedelta(days=10), Decimal("5"), "outflow", "Fee", "Gas fee", True)
    analyzer.add_transaction(wallet2, "tx4", base_time + timedelta(days=12), Decimal("3"), "inflow", "Refund", "Partial refund", False)  # Failed
    
    # Generate credit scores
    print("\n--- GENERATING CREDIT SCORES ---\n")
    report1 = analyzer.generate_credit_score(wallet1)
    report2 = analyzer.generate_credit_score(wallet2)
    
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    
    print(f"\nWallet 1: {report1.credit_score} ({report1.credit_rating.value.upper()})")
    print(f"  Borrow Limit: ${report1.borrow_limit_usd}")
    print(f"  Inflow: ${report1.metrics.total_inflow} | Outflow: ${report1.metrics.total_outflow}")
    print(f"  Net: ${report1.metrics.net_flow}")
    
    print(f"\nWallet 2: {report2.credit_score} ({report2.credit_rating.value.upper()})")
    print(f"  Borrow Limit: ${report2.borrow_limit_usd}")
    print(f"  Inflow: ${report2.metrics.total_inflow} | Outflow: ${report2.metrics.total_outflow}")
    print(f"  Net: ${report2.metrics.net_flow}")
