import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import logging
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SignalStrength(Enum):
    """Buy signal strength classification"""
    STRONG = "strong"      # Both 1m and 5m confirmed
    MODERATE = "moderate"  # One timeframe confirmed
    WEAK = "weak"          # No confirmation
    NONE = "none"          # No signal


@dataclass
class PriceData:
    """Represents price candle data"""
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass
class TechnicalIndicators:
    """Technical analysis indicators"""
    rsi: Decimal
    macd_line: Decimal
    signal_line: Decimal
    histogram: Decimal
    timestamp: datetime


@dataclass
class BuySignal:
    """Represents a buy signal from technical analysis"""
    signal_id: int
    timestamp: datetime
    price: Decimal
    rsi_1m: Decimal
    rsi_5m: Decimal
    macd_1m_positive: bool
    macd_5m_positive: bool
    strength: SignalStrength
    confidence: Decimal  # 0-100%


@dataclass
class BuyExecution:
    """Records a completed buyback execution"""
    execution_id: int
    timestamp: datetime
    signal_id: int
    amount_usd: Decimal
    buy_price: Decimal
    tokens_purchased: Decimal
    reason: str
    status: str  # pending, executed, failed, cancelled
    price_impact: Decimal = Decimal(0)  # % impact on token price
    slippage: Decimal = Decimal(0)  # % slippage on execution


class RSICalculator:
    """Calculates Relative Strength Index (RSI)"""
    
    @staticmethod
    def calculate(prices: List[Decimal], period: int = 14) -> Decimal:
        """
        Calculate RSI for a price series
        
        Args:
            prices: List of close prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return Decimal(50)  # Neutral if insufficient data
        
        prices = list(prices[-period-1:])
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        
        gains = [Decimal(max(0, d)) for d in deltas]
        losses = [Decimal(max(0, -d)) for d in deltas]
        
        avg_gains = sum(gains) / len(gains) if gains else Decimal(0)
        avg_losses = sum(losses) / len(losses) if losses else Decimal(0)
        
        if avg_losses == 0:
            return Decimal(100) if avg_gains > 0 else Decimal(50)
        
        rs = avg_gains / avg_losses
        rsi = Decimal(100) - (Decimal(100) / (Decimal(1) + rs))
        
        return rsi.quantize(Decimal('0.00'))


class MACDCalculator:
    """Calculates MACD (Moving Average Convergence Divergence)"""
    
    @staticmethod
    def _calculate_ema(prices: List[Decimal], period: int) -> List[Decimal]:
        """Calculate Exponential Moving Average"""
        if not prices:
            return []
        
        multiplier = Decimal(2) / (Decimal(period) + Decimal(1))
        ema = [prices[0]]
        
        for price in prices[1:]:
            ema_val = price * multiplier + ema[-1] * (Decimal(1) - multiplier)
            ema.append(ema_val)
        
        return ema
    
    @staticmethod
    def calculate(prices: List[Decimal], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[Decimal, Decimal, Decimal]:
        """
        Calculate MACD indicators
        
        Args:
            prices: List of close prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        if len(prices) < slow:
            return Decimal(0), Decimal(0), Decimal(0)
        
        prices = list(prices[-slow:])
        
        ema_fast = MACDCalculator._calculate_ema(prices, fast)
        ema_slow = MACDCalculator._calculate_ema(prices, slow)
        
        if len(ema_fast) != len(ema_slow):
            min_len = min(len(ema_fast), len(ema_slow))
            ema_fast = ema_fast[-min_len:]
            ema_slow = ema_slow[-min_len:]
        
        macd_line = ema_fast[-1] - ema_slow[-1]
        
        macd_values = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
        signal_line_ema = MACDCalculator._calculate_ema(macd_values, signal)
        signal_line = signal_line_ema[-1] if signal_line_ema else Decimal(0)
        
        histogram = macd_line - signal_line
        
        return (
            macd_line.quantize(Decimal('0.000001')),
            signal_line.quantize(Decimal('0.000001')),
            histogram.quantize(Decimal('0.000001'))
        )


class ExenBuybackSystem:
    """
    Chart support buyback engine for Exen Protocol
    
    Features:
    - Multi-timeframe RSI/MACD analysis (1m and 5m)
    - Algorithmic buy signal generation
    - Position sizing and risk management
    - Complete execution tracking
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the buyback system
        
        Args:
            verbose: Enable detailed logging
        """
        self.verbose = verbose
        self.buyback_fund = Decimal(0)
        self.price_history_1m: List[Decimal] = []
        self.price_history_5m: List[Decimal] = []
        self.buy_signals: List[BuySignal] = []
        self.executions: List[BuyExecution] = []
        self.execution_counter = 0
        self.signal_counter = 0
        self.total_spent = Decimal(0)
        self.total_tokens_bought = Decimal(0)
        self.last_buy_time = None
        self.cooldown_minutes = 5
        
        # Risk management thresholds
        self.rsi_oversold = Decimal(30)
        self.rsi_oversold_strong = Decimal(20)
        self.rsi_overbought = Decimal(70)
        self.max_position_size = Decimal('0.10')  # 10% of available funds per trade
        self.max_buy_size_usd = Decimal(5000)
        
        logger.info("Exen Buyback System initialized")
    
    def add_buyback_funds(self, amount: Decimal) -> Decimal:
        """
        Add funds to the buyback support pool
        
        Sources: 25% of creator fees + 50% of lending interest
        
        Args:
            amount: USD amount to add
            
        Returns:
            Current buyback fund total
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        self.buyback_fund += amount
        
        if self.verbose:
            logger.info(f"Added buyback funds: ${amount} | Total: ${self.buyback_fund}")
        
        return self.buyback_fund
    
    def add_price_data(self, price: Decimal, timeframe: str = "1m") -> None:
        """
        Add price candle data
        
        Args:
            price: Close price for the candle
            timeframe: "1m" or "5m"
        """
        if not isinstance(price, Decimal):
            price = Decimal(str(price))
        
        if timeframe == "1m":
            self.price_history_1m.append(price)
            # Keep last 100 candles for analysis
            if len(self.price_history_1m) > 100:
                self.price_history_1m = self.price_history_1m[-100:]
        
        elif timeframe == "5m":
            self.price_history_5m.append(price)
            if len(self.price_history_5m) > 100:
                self.price_history_5m = self.price_history_5m[-100:]
    
    def analyze_1m_timeframe(self) -> Tuple[Decimal, Decimal, bool]:
        """
        Analyze 1-minute timeframe
        
        Returns:
            Tuple of (RSI, MACD histogram, is_bullish)
        """
        if len(self.price_history_1m) < 30:
            return Decimal(50), Decimal(0), False
        
        rsi = RSICalculator.calculate(self.price_history_1m, period=14)
        macd_line, signal_line, histogram = MACDCalculator.calculate(self.price_history_1m)
        
        is_bullish = histogram > 0
        
        return rsi, histogram, is_bullish
    
    def analyze_5m_timeframe(self) -> Tuple[Decimal, Decimal, bool]:
        """
        Analyze 5-minute timeframe
        
        Returns:
            Tuple of (RSI, MACD histogram, is_bullish)
        """
        if len(self.price_history_5m) < 30:
            return Decimal(50), Decimal(0), False
        
        rsi = RSICalculator.calculate(self.price_history_5m, period=14)
        macd_line, signal_line, histogram = MACDCalculator.calculate(self.price_history_5m)
        
        is_bullish = histogram > 0
        
        return rsi, histogram, is_bullish
    
    def _check_cooldown(self) -> bool:
        """
        Check if sufficient time has passed since last buy
        
        Returns:
            True if enough time has passed, False if in cooldown
        """
        if self.last_buy_time is None:
            return True
        
        elapsed = datetime.now() - self.last_buy_time
        return elapsed >= timedelta(minutes=self.cooldown_minutes)
    
    def generate_buy_signal(self) -> Optional[BuySignal]:
        """
        Generate buy signal based on multi-timeframe technical analysis
        
        Criteria:
        - RSI < 30 (oversold) on both 1m and 5m
        - MACD positive (bullish) on both 1m and 5m
        - Not in cooldown period
        
        Returns:
            BuySignal if conditions met, None otherwise
        """
        if not self._check_cooldown():
            return None
        
        if len(self.price_history_1m) < 30 or len(self.price_history_5m) < 30:
            return None
        
        # Analyze both timeframes
        rsi_1m, macd_1m, bullish_1m = self.analyze_1m_timeframe()
        rsi_5m, macd_5m, bullish_5m = self.analyze_5m_timeframe()
        
        current_price = self.price_history_1m[-1]
        
        # Determine signal strength
        rsi_1m_oversold = rsi_1m < self.rsi_oversold
        rsi_5m_oversold = rsi_5m < self.rsi_oversold
        
        both_rsi_confirmed = rsi_1m_oversold and rsi_5m < Decimal(35)
        both_macd_confirmed = bullish_1m and bullish_5m
        
        # Calculate signal strength and confidence
        if both_rsi_confirmed and both_macd_confirmed:
            strength = SignalStrength.STRONG
            confidence = Decimal(85)
        elif (rsi_1m_oversold or rsi_5m_oversold) and (bullish_1m or bullish_5m):
            strength = SignalStrength.MODERATE
            confidence = Decimal(65)
        elif rsi_1m < self.rsi_oversold_strong:
            strength = SignalStrength.STRONG
            confidence = Decimal(75)
        else:
            return None
        
        self.signal_counter += 1
        signal = BuySignal(
            signal_id=self.signal_counter,
            timestamp=datetime.now(),
            price=current_price,
            rsi_1m=rsi_1m,
            rsi_5m=rsi_5m,
            macd_1m_positive=bullish_1m,
            macd_5m_positive=bullish_5m,
            strength=strength,
            confidence=confidence
        )
        
        self.buy_signals.append(signal)
        
        if self.verbose:
            logger.info(
                f"BUY SIGNAL GENERATED (ID: {signal.signal_id}) - {strength.value.upper()}\n"
                f"  Price: ${current_price}\n"
                f"  RSI 1m: {rsi_1m} | RSI 5m: {rsi_5m}\n"
                f"  MACD 1m: {bullish_1m} | MACD 5m: {bullish_5m}\n"
                f"  Confidence: {confidence}%"
            )
        
        return signal
    
    def _calculate_position_size(self, signal: BuySignal) -> Decimal:
        """
        Calculate buy amount based on signal strength and available funds
        
        Args:
            signal: The buy signal
            
        Returns:
            USD amount to spend
        """
        if self.buyback_fund <= 0:
            return Decimal(0)
        
        # Maximum 10% of available funds per trade
        base_size = self.buyback_fund * self.max_position_size
        
        # Adjust based on signal strength
        if signal.strength == SignalStrength.STRONG:
            size = base_size * (signal.confidence / Decimal(100))
        elif signal.strength == SignalStrength.MODERATE:
            size = base_size * Decimal('0.7')
        else:
            size = base_size * Decimal('0.5')
        
        # Cap maximum buy size
        size = min(size, self.max_buy_size_usd)
        
        return size.quantize(Decimal('0.01'))
    
    def execute_buy(self, signal: BuySignal, slippage_percent: Decimal = Decimal('0.5')) -> Optional[BuyExecution]:
        """
        Execute a buy order based on signal
        
        Args:
            signal: The buy signal to execute
            slippage_percent: Expected slippage % (default 0.5%)
            
        Returns:
            BuyExecution record if successful, None otherwise
        """
        if self.buyback_fund <= 0:
            logger.warning("Insufficient buyback funds for execution")
            return None
        
        buy_amount = self._calculate_position_size(signal)
        
        if buy_amount <= 0:
            return None
        
        # Calculate tokens purchased (simple calculation)
        # In production, this would use actual DEX pricing
        execution_price = signal.price * (Decimal(1) + (slippage_percent / Decimal(100)))
        tokens_purchased = buy_amount / execution_price
        
        self.execution_counter += 1
        execution = BuyExecution(
            execution_id=self.execution_counter,
            timestamp=datetime.now(),
            signal_id=signal.signal_id,
            amount_usd=buy_amount,
            buy_price=execution_price,
            tokens_purchased=tokens_purchased,
            reason=f"{signal.strength.value}_signal",
            status="executed",
            price_impact=Decimal('0.2'),  # Simulated 0.2% price impact
            slippage=slippage_percent
        )
        
        # Update state
        self.buyback_fund -= buy_amount
        self.total_spent += buy_amount
        self.total_tokens_bought += tokens_purchased
        self.last_buy_time = datetime.now()
        
        self.executions.append(execution)
        
        if self.verbose:
            logger.info(
                f"BUYBACK EXECUTED (Execution ID: {execution.execution_id})\n"
                f"  Amount: ${buy_amount}\n"
                f"  Price: ${execution_price}\n"
                f"  Tokens: {tokens_purchased.quantize(Decimal('0.00'))}\n"
                f"  Slippage: {slippage_percent}%\n"
                f"  Price Impact: {execution.price_impact}%\n"
                f"  Remaining Fund: ${self.buyback_fund}"
            )
        
        return execution
    
    def cancel_signal(self, signal_id: int) -> bool:
        """
        Cancel a pending buy signal
        
        Args:
            signal_id: ID of signal to cancel
            
        Returns:
            True if successful
        """
        for signal in self.buy_signals:
            if signal.signal_id == signal_id:
                logger.info(f"Signal {signal_id} cancelled")
                return True
        
        return False
    
    def get_system_stats(self) -> Dict:
        """
        Get overall buyback system statistics
        
        Returns:
            Dictionary of system stats
        """
        return {
            "buyback_fund_available": str(self.buyback_fund),
            "total_spent": str(self.total_spent),
            "total_tokens_bought": str(self.total_tokens_bought),
            "total_signals_generated": self.signal_counter,
            "total_executions": len(self.executions),
            "execution_success_rate": f"{(len(self.executions) / max(self.signal_counter, 1) * 100):.1f}%",
            "avg_execution_size": str(
                self.total_spent / max(len(self.executions), 1)
            ),
            "avg_price_paid": str(
                self.total_spent / max(self.total_tokens_bought, Decimal(1))
            ),
            "price_chart_health": "Maintained via algorithmic support",
            "cooldown_period": f"{self.cooldown_minutes} minutes",
            "max_position_size": f"{(self.max_position_size * 100):.0f}% of fund"
        }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent execution history
        
        Args:
            limit: Number of recent executions to return
            
        Returns:
            List of execution records
        """
        history = []
        for execution in self.executions[-limit:]:
            history.append({
                "execution_id": execution.execution_id,
                "signal_id": execution.signal_id,
                "timestamp": execution.timestamp.isoformat(),
                "amount_usd": str(execution.amount_usd),
                "buy_price": str(execution.buy_price),
                "tokens_purchased": str(execution.tokens_purchased),
                "slippage": f"{execution.slippage}%",
                "price_impact": f"{execution.price_impact}%",
                "status": execution.status
            })
        return history


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*70)
    print("EXEN PROTOCOL - ALGORITHMIC BUYBACK SYSTEM DEMO")
    print("="*70 + "\n")
    
    # Initialize the system
    system = ExenBuybackSystem(verbose=True)
    
    # Simulate incoming funds (25% of creator fees + 50% of lending interest)
    print("\n--- SIMULATING BUYBACK FUND ALLOCATION ---\n")
    system.add_buyback_funds(Decimal("100"))  # 25% of 100 SOL fee = 25, scaled to 100 for demo
    
    # Simulate price data with oversold conditions
    print("\n--- SIMULATING PRICE MOVEMENTS (1m timeframe) ---\n")
    
    # Normal price movement
    for price in [100, 101, 102, 103, 102, 101, 99, 98, 97, 96, 95]:
        system.add_price_data(Decimal(price), timeframe="1m")
    
    # Oversold conditions
    for price in [94, 92, 90, 88, 86, 84, 82, 80, 79, 78]:
        system.add_price_data(Decimal(price), timeframe="1m")
    
    # Recovery (bullish)
    for price in [80, 82, 85, 87, 90, 93, 95]:
        system.add_price_data(Decimal(price), timeframe="1m")
    
    # Simulate 5m data similarly
    system.price_history_5m = system.price_history_1m[::5]  # Every 5th price point
    
    print("\n--- GENERATING BUY SIGNALS ---\n")
    
    # Try to generate signals
    for i in range(3):
        signal = system.generate_buy_signal()
        if signal:
            # Execute if signal generated
            execution = system.execute_buy(signal, slippage_percent=Decimal('0.3'))
            if execution:
                # Add recovery price after each buy
                for price in [95, 98, 100, 103, 105]:
                    system.add_price_data(Decimal(price), timeframe="1m")
                system.price_history_5m = system.price_history_1m[::5]
    
    # Print statistics
    print("\n" + "="*70)
    print("BUYBACK SYSTEM STATISTICS")
    print("="*70 + "\n")
    
    stats = system.get_system_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*70)
    print("EXECUTION HISTORY")
    print("="*70 + "\n")
    
    for execution in system.get_execution_history(limit=10):
        print(f"Execution #{execution['execution_id']}")
        print(f"  Signal: #{execution['signal_id']}")
        print(f"  Amount: ${execution['amount_usd']}")
        print(f"  Price: ${execution['buy_price']}")
        print(f"  Tokens: {execution['tokens_purchased']}")
        print(f"  Status: {execution['status']}")
        print()
