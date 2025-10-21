import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DecisionStatus(Enum):
    """Lending decision outcomes"""
    APPROVED = "approved"
    CONDITIONAL_APPROVAL = "conditional_approval"
    DENIED = "denied"
    PENDING_REVIEW = "pending_review"


class RiskLevel(Enum):
    """Risk classification for loan"""
    MINIMAL = "minimal"         # 0-5% risk
    LOW = "low"                 # 5-15% risk
    MODERATE = "moderate"       # 15-30% risk
    HIGH = "high"               # 30-50% risk
    VERY_HIGH = "very_high"     # 50%+ risk


@dataclass
class LoanRequest:
    """Loan application request"""
    request_id: str
    wallet_address: str
    collateral_amount: Decimal  # Exen tokens
    borrow_amount_usd: Decimal
    collateral_token_price: Decimal
    credit_score: Decimal
    credit_rating: str
    total_inflow: Decimal
    total_outflow: Decimal
    net_flow: Decimal
    current_balance: Decimal
    transaction_success_rate: Decimal
    transaction_count: int
    average_inflow: Decimal
    requested_at: datetime


@dataclass
class RiskAssessment:
    """Detailed risk analysis"""
    collateral_risk: Decimal  # 0-100
    credit_risk: Decimal  # 0-100
    liquidity_risk: Decimal  # 0-100
    behavioral_risk: Decimal  # 0-100
    overall_risk_score: Decimal  # 0-100
    risk_level: RiskLevel
    key_risk_factors: List[str] = field(default_factory=list)


@dataclass
class LoanTerms:
    """Proposed loan terms"""
    loan_amount: Decimal  # USD
    interest_rate: Decimal  # % APY
    ltv_ratio: Decimal  # Loan-to-Value %
    collateral_required: Decimal  # Tokens required
    liquidation_threshold: Decimal  # Health factor
    repayment_period_days: int
    monthly_payment: Decimal
    total_interest: Decimal


@dataclass
class LoanDecision:
    """Final lending decision"""
    decision_id: str
    request_id: str
    wallet_address: str
    status: DecisionStatus
    decision_timestamp: datetime
    risk_assessment: RiskAssessment
    proposed_terms: Optional[LoanTerms]
    approval_reason: str
    denial_reason: Optional[str]
    conditions: List[str] = field(default_factory=list)
    collateral_required: Decimal = Decimal(0)
    max_ltv: Decimal = Decimal(0)
    confidence_score: Decimal = Decimal(0)  # 0-100
    manual_review_required: bool = False
    manual_review_reason: Optional[str] = None


class AutoDecisionEngine:
    """
    Automated lending decision system
    Makes approval/denial decisions based on credit analysis and risk metrics
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the decision engine
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.decisions: List[LoanDecision] = []
        self.decision_counter = 0
        
        # Configuration thresholds
        self.base_ltv = Decimal('60')  # 60% base LTV
        self.min_credit_score = Decimal(400)
        self.min_transactions = 3
        self.min_success_rate = Decimal('80')
        self.max_loan_amount_usd = Decimal(500000)
        self.min_loan_amount_usd = Decimal(100)
        
        logger.info("Auto Decisioning Engine initialized")
    
    def assess_collateral_risk(self, loan_request: LoanRequest) -> Decimal:
        """
        Assess risk from collateral volatility and adequacy
        
        Scale: 0-100 (lower is better)
        
        Args:
            loan_request: Loan request to analyze
            
        Returns:
            Collateral risk score
        """
        collateral_value = loan_request.collateral_amount * loan_request.collateral_token_price
        
        if collateral_value <= 0:
            return Decimal(100)
        
        ltv = (loan_request.borrow_amount_usd / collateral_value * Decimal(100))
        
        # Risk increases with LTV
        if ltv <= Decimal(30):
            return Decimal(5)  # Very safe
        elif ltv <= Decimal(50):
            return Decimal(15)
        elif ltv <= Decimal(60):
            return Decimal(25)
        elif ltv <= Decimal(75):
            return Decimal(50)
        else:
            return Decimal(80)  # Risky
    
    def assess_credit_risk(self, loan_request: LoanRequest) -> Decimal:
        """
        Assess risk based on credit score and payment history
        
        Scale: 0-100 (lower is better)
        
        Args:
            loan_request: Loan request to analyze
            
        Returns:
            Credit risk score
        """
        score = loan_request.credit_score
        
        # Direct mapping of credit score to risk
        if score >= Decimal(750):
            return Decimal(5)
        elif score >= Decimal(650):
            return Decimal(15)
        elif score >= Decimal(550):
            return Decimal(30)
        elif score >= Decimal(450):
            return Decimal(60)
        else:
            return Decimal(85)
    
    def assess_liquidity_risk(self, loan_request: LoanRequest) -> Decimal:
        """
        Assess risk based on wallet liquidity and cash flow
        
        Scale: 0-100 (lower is better)
        
        Args:
            loan_request: Loan request to analyze
            
        Returns:
            Liquidity risk score
        """
        # Calculate cash flow ratio
        if loan_request.total_outflow == 0:
            cash_flow_ratio = Decimal(100)
        else:
            cash_flow_ratio = (loan_request.current_balance / loan_request.total_outflow)
        
        # Monthly outflow approximation
        estimated_monthly_outflow = loan_request.average_inflow * Decimal('0.8')
        
        if estimated_monthly_outflow == 0:
            outflow_coverage = Decimal(100)
        else:
            outflow_coverage = loan_request.current_balance / estimated_monthly_outflow
        
        # Risk based on coverage
        if outflow_coverage >= Decimal(6):
            return Decimal(10)  # Excellent coverage
        elif outflow_coverage >= Decimal(3):
            return Decimal(20)
        elif outflow_coverage >= Decimal(1):
            return Decimal(40)
        elif outflow_coverage >= Decimal(0.5):
            return Decimal(65)
        else:
            return Decimal(90)  # Poor coverage
    
    def assess_behavioral_risk(self, loan_request: LoanRequest) -> Decimal:
        """
        Assess risk based on on-chain behavior patterns
        
        Scale: 0-100 (lower is better)
        
        Args:
            loan_request: Loan request to analyze
            
        Returns:
            Behavioral risk score
        """
        risk = Decimal(0)
        
        # Transaction frequency risk
        if loan_request.transaction_count < 5:
            risk += Decimal(20)
        elif loan_request.transaction_count < 20:
            risk += Decimal(10)
        elif loan_request.transaction_count < 50:
            risk += Decimal(5)
        
        # Success rate risk
        if loan_request.transaction_success_rate < Decimal(80):
            risk += Decimal(25)
        elif loan_request.transaction_success_rate < Decimal(95):
            risk += Decimal(10)
        
        # Cash flow stability
        if loan_request.net_flow <= 0:
            risk += Decimal(30)
        elif loan_request.net_flow < loan_request.average_inflow * Decimal('0.5'):
            risk += Decimal(15)
        
        return min(risk, Decimal(100))
    
    def perform_risk_assessment(self, loan_request: LoanRequest) -> RiskAssessment:
        """
        Perform complete risk assessment
        
        Args:
            loan_request: Loan request to analyze
            
        Returns:
            Comprehensive risk assessment
        """
        collateral_risk = self.assess_collateral_risk(loan_request)
        credit_risk = self.assess_credit_risk(loan_request)
        liquidity_risk = self.assess_liquidity_risk(loan_request)
        behavioral_risk = self.assess_behavioral_risk(loan_request)
        
        # Weighted average for overall risk
        overall_risk = (
            collateral_risk * Decimal('0.30') +
            credit_risk * Decimal('0.35') +
            liquidity_risk * Decimal('0.20') +
            behavioral_risk * Decimal('0.15')
        )
        
        overall_risk = overall_risk.quantize(Decimal('0.00'))
        
        # Determine risk level
        if overall_risk <= Decimal(15):
            risk_level = RiskLevel.MINIMAL
        elif overall_risk <= Decimal(30):
            risk_level = RiskLevel.LOW
        elif overall_risk <= Decimal(50):
            risk_level = RiskLevel.MODERATE
        elif overall_risk <= Decimal(75):
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        # Identify key risk factors
        key_factors = []
        if collateral_risk > Decimal(50):
            key_factors.append("High collateral risk")
        if credit_risk > Decimal(50):
            key_factors.append("Poor credit history")
        if liquidity_risk > Decimal(50):
            key_factors.append("Low cash flow coverage")
        if behavioral_risk > Decimal(50):
            key_factors.append("Concerning transaction patterns")
        
        return RiskAssessment(
            collateral_risk=collateral_risk,
            credit_risk=credit_risk,
            liquidity_risk=liquidity_risk,
            behavioral_risk=behavioral_risk,
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            key_risk_factors=key_factors
        )
    
    def calculate_loan_terms(self, loan_request: LoanRequest, risk_assessment: RiskAssessment) -> LoanTerms:
        """
        Calculate loan terms based on risk assessment
        
        Args:
            loan_request: Loan request
            risk_assessment: Risk assessment results
            
        Returns:
            Proposed loan terms
        """
        collateral_value = loan_request.collateral_amount * loan_request.collateral_token_price
        
        # Adjust LTV based on risk
        if risk_assessment.risk_level == RiskLevel.MINIMAL:
            ltv = self.base_ltv
            interest_rate = Decimal('8.0')
        elif risk_assessment.risk_level == RiskLevel.LOW:
            ltv = self.base_ltv
            interest_rate = Decimal('10.0')
        elif risk_assessment.risk_level == RiskLevel.MODERATE:
            ltv = self.base_ltv * Decimal('0.9')
            interest_rate = Decimal('12.0')
        elif risk_assessment.risk_level == RiskLevel.HIGH:
            ltv = self.base_ltv * Decimal('0.7')
            interest_rate = Decimal('15.0')
        else:
            ltv = self.base_ltv * Decimal('0.5')
            interest_rate = Decimal('18.0')
        
        # Adjust for credit score
        credit_score_factor = (loan_request.credit_score - Decimal(300)) / Decimal(550)
        interest_rate *= (Decimal(1) - credit_score_factor * Decimal('0.4'))
        
        interest_rate = max(interest_rate, Decimal('5.0'))
        interest_rate = min(interest_rate, Decimal('18.0'))
        
        # Calculate maximum loan
        max_loan = collateral_value * ltv / Decimal(100)
        loan_amount = min(loan_request.borrow_amount_usd, max_loan)
        
        # Calculate repayment terms
        repayment_days = 180  # 6 months
        annual_interest = loan_amount * interest_rate / Decimal(100)
        total_interest = annual_interest * Decimal(repayment_days) / Decimal(365)
        monthly_payment = (loan_amount + total_interest) / Decimal(6)
        
        return LoanTerms(
            loan_amount=loan_amount.quantize(Decimal('0.01')),
            interest_rate=interest_rate.quantize(Decimal('0.01')),
            ltv_ratio=ltv.quantize(Decimal('0.00')),
            collateral_required=loan_request.collateral_amount,
            liquidation_threshold=Decimal('1.0'),  # Health factor
            repayment_period_days=repayment_days,
            monthly_payment=monthly_payment.quantize(Decimal('0.01')),
            total_interest=total_interest.quantize(Decimal('0.01'))
        )
    
    def make_decision(self, loan_request: LoanRequest) -> LoanDecision:
        """
        Make automated lending decision
        
        Args:
            loan_request: Loan request to evaluate
            
        Returns:
            Complete lending decision
        """
        self.decision_counter += 1
        decision_id = f"DECISION_{self.decision_counter}"
        
        # Preliminary checks
        if loan_request.credit_score < self.min_credit_score:
            return LoanDecision(
                decision_id=decision_id,
                request_id=loan_request.request_id,
                wallet_address=loan_request.wallet_address,
                status=DecisionStatus.DENIED,
                decision_timestamp=datetime.now(),
                risk_assessment=RiskAssessment(
                    collateral_risk=Decimal(0),
                    credit_risk=Decimal(100),
                    liquidity_risk=Decimal(0),
                    behavioral_risk=Decimal(0),
                    overall_risk_score=Decimal(100),
                    risk_level=RiskLevel.VERY_HIGH
                ),
                proposed_terms=None,
                approval_reason="",
                denial_reason=f"Credit score {loan_request.credit_score} below minimum {self.min_credit_score}",
                confidence_score=Decimal(99)
            )
        
        if loan_request.transaction_count < self.min_transactions:
            return LoanDecision(
                decision_id=decision_id,
                request_id=loan_request.request_id,
                wallet_address=loan_request.wallet_address,
                status=DecisionStatus.PENDING_REVIEW,
                decision_timestamp=datetime.now(),
                risk_assessment=RiskAssessment(
                    collateral_risk=Decimal(0),
                    credit_risk=Decimal(0),
                    liquidity_risk=Decimal(0),
                    behavioral_risk=Decimal(80),
                    overall_risk_score=Decimal(80),
                    risk_level=RiskLevel.HIGH,
                    key_risk_factors=["Insufficient transaction history"]
                ),
                proposed_terms=None,
                approval_reason="",
                denial_reason=None,
                manual_review_reason="Insufficient on-chain history for auto approval",
                confidence_score=Decimal(40),
                manual_review_required=True
            )
        
        if loan_request.borrow_amount_usd > self.max_loan_amount_usd:
            return LoanDecision(
                decision_id=decision_id,
                request_id=loan_request.request_id,
                wallet_address=loan_request.wallet_address,
                status=DecisionStatus.DENIED,
                decision_timestamp=datetime.now(),
                risk_assessment=RiskAssessment(
                    collateral_risk=Decimal(0),
                    credit_risk=Decimal(0),
                    liquidity_risk=Decimal(0),
                    behavioral_risk=Decimal(0),
                    overall_risk_score=Decimal(0),
                    risk_level=RiskLevel.MINIMAL
                ),
                proposed_terms=None,
                approval_reason="",
                denial_reason=f"Loan amount exceeds maximum {self.max_loan_amount_usd}",
                confidence_score=Decimal(99)
            )
        
        if loan_request.borrow_amount_usd < self.min_loan_amount_usd:
            return LoanDecision(
                decision_id=decision_id,
                request_id=loan_request.request_id,
                wallet_address=loan_request.wallet_address,
                status=DecisionStatus.DENIED,
                decision_timestamp=datetime.now(),
                risk_assessment=RiskAssessment(
                    collateral_risk=Decimal(0),
                    credit_risk=Decimal(0),
                    liquidity_risk=Decimal(0),
                    behavioral_risk=Decimal(0),
                    overall_risk_score=Decimal(0),
                    risk_level=RiskLevel.MINIMAL
                ),
                proposed_terms=None,
                approval_reason="",
                denial_reason=f"Loan amount below minimum {self.min_loan_amount_usd}",
                confidence_score=Decimal(99)
            )
        
        # Perform risk assessment
        risk_assessment = self.perform_risk_assessment(loan_request)
        
        # Calculate loan terms
        loan_terms = self.calculate_loan_terms(loan_request, risk_assessment)
        
        # Determine decision
        conditions = []
        
        if risk_assessment.overall_risk_score <= Decimal(15):
            status = DecisionStatus.APPROVED
            approval_reason = "Minimal risk profile. Excellent credit history and collateral coverage."
            confidence = Decimal(95)
        
        elif risk_assessment.overall_risk_score <= Decimal(30):
            status = DecisionStatus.APPROVED
            approval_reason = "Low risk profile. Good credit score and adequate collateral."
            confidence = Decimal(90)
        
        elif risk_assessment.overall_risk_score <= Decimal(50):
            status = DecisionStatus.CONDITIONAL_APPROVAL
            approval_reason = "Moderate risk accepted with conditions."
            conditions.append("Higher interest rate applied")
            conditions.append("Reduced LTV ratio")
            conditions.append("Monthly collateral health check required")
            confidence = Decimal(75)
        
        elif risk_assessment.overall_risk_score <= Decimal(75):
            status = DecisionStatus.PENDING_REVIEW
            approval_reason = ""
            manual_review_required = True
            confidence = Decimal(45)
        
        else:
            status = DecisionStatus.DENIED
            approval_reason = ""
            denial_reason = f"Overall risk score {risk_assessment.overall_risk_score} exceeds approval threshold. Risk factors: {', '.join(risk_assessment.key_risk_factors)}"
            confidence = Decimal(90)
        
        decision = LoanDecision(
            decision_id=decision_id,
            request_id=loan_request.request_id,
            wallet_address=loan_request.wallet_address,
            status=status,
            decision_timestamp=datetime.now(),
            risk_assessment=risk_assessment,
            proposed_terms=loan_terms if status != DecisionStatus.DENIED else None,
            approval_reason=approval_reason,
            denial_reason=approval_reason if status != DecisionStatus.DENIED else denial_reason,
            conditions=conditions,
            collateral_required=loan_request.collateral_amount,
            max_ltv=loan_terms.ltv_ratio,
            confidence_score=confidence,
            manual_review_required=status == DecisionStatus.PENDING_REVIEW
        )
        
        self.decisions.append(decision)
        
        if self.verbose:
            self._print_decision(decision)
        
        return decision
    
    def _print_decision(self, decision: LoanDecision) -> None:
        """Print formatted decision"""
        logger.info("\n" + "="*70)
        logger.info("AUTOMATED LENDING DECISION")
        logger.info("="*70)
        logger.info(f"\nDecision ID: {decision.decision_id}")
        logger.info(f"Request ID: {decision.request_id}")
        logger.info(f"Wallet: {decision.wallet_address}")
        logger.info(f"Status: {decision.status.value.upper()}")
        logger.info(f"Decision Time: {decision.decision_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Confidence: {decision.confidence_score}%")
        
        logger.info(f"\n{'RISK ASSESSMENT':-^70}")
        logger.info(f"Overall Risk: {decision.risk_assessment.overall_risk_score}/100 ({decision.risk_assessment.risk_level.value.upper()})")
        logger.info(f"  Collateral Risk: {decision.risk_assessment.collateral_risk}/100")
        logger.info(f"  Credit Risk: {decision.risk_assessment.credit_risk}/100")
        logger.info(f"  Liquidity Risk: {decision.risk_assessment.liquidity_risk}/100")
        logger.info(f"  Behavioral Risk: {decision.risk_assessment.behavioral_risk}/100")
        
        if decision.risk_assessment.key_risk_factors:
            logger.info(f"  Key Risk Factors: {', '.join(decision.risk_assessment.key_risk_factors)}")
        
        if decision.proposed_terms:
            logger.info(f"\n{'PROPOSED TERMS':-^70}")
            logger.info(f"Loan Amount: ${decision.proposed_terms.loan_amount}")
            logger.info(f"Interest Rate: {decision.proposed_terms.interest_rate}% APY")
            logger.info(f"LTV Ratio: {decision.proposed_terms.ltv_ratio}%")
            logger.info(f"Repayment Period: {decision.proposed_terms.repayment_period_days} days")
            logger.info(f"Monthly Payment: ${decision.proposed_terms.monthly_payment}")
            logger.info(f"Total Interest: ${decision.proposed_terms.total_interest}")
        
        if decision.conditions:
            logger.info(f"\n{'CONDITIONS':-^70}")
            for condition in decision.conditions:
                logger.info(f"  - {condition}")
        
        logger.info(f"\n{'DECISION':-^70}")
        if decision.approval_reason:
            logger.info(f"Approval: {decision.approval_reason}")
        if decision.denial_reason:
            logger.info(f"Reason: {decision.denial_reason}")
        if decision.manual_review_required:
            logger.info(f"Manual Review Required: {decision.manual_review_reason}")
        
        logger.info("="*70 + "\n")
    
    def get_decision_stats(self) -> Dict:
        """Get decision engine statistics"""
        approved = len([d for d in self.decisions if d.status == DecisionStatus.APPROVED])
        conditional = len([d for d in self.decisions if d.status == DecisionStatus.CONDITIONAL_APPROVAL])
        denied = len([d for d in self.decisions if d.status == DecisionStatus.DENIED])
        pending = len([d for d in self.decisions if d.status == DecisionStatus.PENDING_REVIEW])
        total = len(self.decisions)
        
        return {
            "total_decisions": total,
            "approved": approved,
            "conditional_approval": conditional,
            "denied": denied,
            "pending_review": pending,
            "approval_rate": f"{(approved / total * 100):.1f}%" if total > 0 else "0%",
            "auto_decision_rate": f"{((approved + conditional + denied) / total * 100):.1f}%" if total > 0 else "0%",
            "avg_confidence": str(sum(d.confidence_score for d in self.decisions) / total) if total > 0 else "0"
        }


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("EXEN PROTOCOL - AUTO DECISIONING ENGINE DEMO")
    print("="*70 + "\n")
    
    engine = AutoDecisionEngine(verbose=True)
    
    # Create test loan requests
    requests = [
        LoanRequest(
            request_id="REQ_001",
            wallet_address="ExcellentWallet1111111111111111111111111",
            collateral_amount=Decimal("100000"),
            borrow_amount_usd=Decimal("5000"),
            collateral_token_price=Decimal("0.10"),
            credit_score=Decimal(780),
            credit_rating="excellent",
            total_inflow=Decimal("50000"),
            total_outflow=Decimal("20000"),
            net_flow=Decimal("30000"),
            current_balance=Decimal("100"),
            transaction_success_rate=Decimal(99.5),
            transaction_count=150,
            average_inflow=Decimal("500"),
            requested_at=datetime.now()
        ),
        LoanRequest(
            request_id="REQ_002",
            wallet_address="FairWallet222222222222222222222222222",
            collateral_amount=Decimal("50000"),
            borrow_amount_usd=Decimal("2000"),
            collateral_token_price=Decimal("0.10"),
            credit_score=Decimal(550),
            credit_rating="good",
            total_inflow=Decimal("10000"),
            total_outflow=Decimal("9000"),
            net_flow=Decimal("1000"),
            current_balance=Decimal("20"),
            transaction_success_rate=Decimal(92),
            transaction_count=25,
            average_inflow=Decimal("200"),
            requested_at=datetime.now()
        ),
        LoanRequest(
            request_id="REQ_003",
            wallet_address="PoorWallet3333333333333333333333333333",
            collateral_amount=Decimal("20000"),
            borrow_amount_usd=Decimal("5000"),
            collateral_token_price=Decimal("0.10"),
            credit_score=Decimal(420),
            credit_rating="poor",
            total_inflow=Decimal("5000"),
            total_outflow=Decimal("6000"),
            net_flow=Decimal("-1000"),
            current_balance=Decimal("5"),
            transaction_success_rate=Decimal(75),
            transaction_count=8,
            average_inflow=Decimal("100"),
            requested_at=datetime.now()
        )
    ]
    
    # Process requests
    print("\n--- PROCESSING LOAN REQUESTS ---\n")
    for request in requests:
        engine.make_decision(request)
    
    # Print statistics
    print("\n" + "="*70)
    print("DECISION ENGINE STATISTICS")
    print("="*70 + "\n")
    
    stats = engine.get_decision_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
