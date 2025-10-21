# 📊 Exen Protocol - Complete End-to-End System Mapping

## 🌍 Full Protocol Flow Architecture

```
CREATOR FEES (100%)
    ↓
PROTOCOL RECEIVES FEES
    ↓
FEE SPLITTER (25/25/50)
    ├─────────────────────────────────────────────────────────────┐
    │                                                               │
    ├─ 25% HOLDER REWARDS ENGINE          │  25% CHART BUYBACK     │  50% LENDING POOL
    │                                      │  ENGINE               │
    │  ✓ Fee Accumulation                 │                       │  ✓ Fee Accumulation
    │  ✓ Calculate 25% of fees            │  ✓ Fee Accumulation  │  ✓ Activate at $50k
    │  ✓ Proportional distribution        │  ✓ Technical analysis │  ✓ USD stablecoin pool
    │  ✓ 15-minute cycles                 │  ✓ RSI calculation   │  ✓ Interest accrual
    │  ✓ All holders included             │  ✓ MACD calculation  │  ✓ Risk management
    │                                      │  ✓ Multi-timeframe   │
    │  DISTRIBUTION                        │    confirmation      │  COLLATERAL MANAGEMENT
    │  ├─ Calculate holder percentages     │  ✓ Position sizing  │  ├─ Wallet analysis
    │  ├─ SOL conversion                  │  ✓ Risk management  │  ├─ Credit scoring
    │  ├─ Send to all holders             │  ✓ Execution        │  ├─ Auto-decisioning
    │  └─ Record on-chain                 │                       │  ├─ Collateral deposit
    │                                      │  BUY EXECUTION       │  ├─ Health monitoring
    │  MONTHLY: $X,XXX to holders         │  ├─ Oversold detect │  ├─ Liquidation
    │                                      │  ├─ Signal confirm   │  └─ Surplus redistribution
    │                                      │  ├─ Market order     │
    │                                      │  ├─ Price impact     │  LENDING FLOW
    │                                      │  └─ Log transaction  │  ├─ User initiates
    │                                      │                       │  ├─ Wallet auto-scored
    │                                      │  MONTHLY: $X,XXX     │  ├─ Decision: Yes/No/Maybe
    │                                      │  to chart support    │  ├─ Deposit collateral
    │                                      │                       │  ├─ Escrow lock
    │                                      │                       │  ├─ USD issued
    │                                      │                       │  ├─ Interest accrues
    │                                      │                       │  ├─ Health monitored
    │                                      │                       │  ├─ User repays
    │                                      │                       │  └─ Collateral released
    │
    ├─────────────────────────────────────────────────────────────┘

LENDING POOL INTEREST REVENUE (100%)
    ↓
    ├─ 50% → HOLDER REWARDS (SOL Distribution)
    │   └─ Added to 25% allocation
    │       └─ Increased rewards every 15 minutes
    │
    └─ 50% → CHART BUYBACK SUPPORT (Enhanced Buying Power)
        └─ Added to 25% allocation
            └─ Enhanced algorithmic buybacks

LIQUIDATION SURPLUS (100%)
    ↓
    ├─ 50% → HOLDER REWARDS
    └─ 50% → CHART BUYBACK
```

---

## 1️⃣ HOLDER REWARDS ENGINE (25% of Fees)

### Input
- Creator fees flow in
- 25% allocation calculated

### Processing
```
Reward Pool = Total Fees × 25%

For each holder:
  Holder Reward = (Holder Balance / Total Supply) × Reward Pool
```

### Output
- SOL airdrops every 15 minutes
- Proportional to token holdings
- No minimum balance required
- 100% of holders included

### Example
```
Total Fees: 100 SOL
Reward Pool: 25 SOL
Holders: 4

Holder 1: 50% of supply = 12.5 SOL
Holder 2: 25% of supply = 6.25 SOL
Holder 3: 15% of supply = 3.75 SOL
Holder 4: 10% of supply = 2.5 SOL
```

### Plus: Interest Revenue Boost
- When lending pool generates interest
- 50% of that interest distributed as SOL
- Increases reward pool size
- Same 15-minute distribution cycle

---

## 2️⃣ CHART BUYBACK ENGINE (25% of Fees)

### Input
- Creator fees flow in
- 25% allocation accumulated
- Price data feeds (1m and 5m candles)

### Processing
```
Step 1: Technical Analysis
├─ Calculate RSI (14 period)
│  ├─ 1-minute timeframe
│  └─ 5-minute timeframe
│
├─ Calculate MACD
│  ├─ 1-minute timeframe
│  └─ 5-minute timeframe
│
└─ Generate Signal
   ├─ RSI < 30 on both? (Oversold)
   ├─ MACD > 0 on both? (Bullish)
   └─ Both confirmed = BUY SIGNAL

Step 2: Risk Management
├─ Check 5-minute cooldown
├─ Calculate position size (max 10% of funds)
├─ Adjust for volatility
└─ Adjust for liquidity

Step 3: Execution
├─ Market order placed
├─ Log transaction
├─ Record price impact
└─ Reset cooldown timer
```

### Output
- Algorithmic buybacks at oversold levels
- Chart price support maintained
- Reduced volatility
- Real-time execution tracking

### Example
```
Buyback Fund: $1,000
Available: $1,000

Signal Generated:
- RSI 1m: 28 ✓
- RSI 5m: 32 ✓
- MACD 1m: Positive ✓
- MACD 5m: Positive ✓

Position Size: 10% = $100
Token Price: $0.10
Tokens Purchased: 1,000 EXEN

Remaining Fund: $900
```

### Plus: Interest Revenue Boost
- When lending pool generates interest
- 50% of that interest added to buyback fund
- More firepower for supporting chart
- Same RSI/MACD triggered execution

---

## 3️⃣ LENDING POOL INFRASTRUCTURE (50% of Fees)

### Phase 1: Pool Accumulation (Pre-Activation)

```
Minimum Threshold: $50,000 USD
├─ 50% of all creator fees accumulated
├─ Progress tracked publicly
├─ Pool inactive until threshold reached
└─ No lending available yet

Timeline Example:
Day 1:  $5,000 accumulated (10%)
Day 2:  $12,000 accumulated (24%)
Day 3:  $18,000 accumulated (36%)
...
Day X:  $50,000+ accumulated → ACTIVATED
```

### Phase 2: Pool Activation & Operations

#### 2.1 Borrower Wallet Analysis (NEW USER)

```
When user initiates lending:

Step 1: Automatic Wallet Scan
├─ Connect Solana wallet
├─ Fetch on-chain transaction history
├─ Analyze last 30-90 days

Step 2: Credit Score Calculation
Analyze 5 Credibility Factors (0-20 each):

├─ Transaction Volume Score
│  └─ Total inflow + outflow activity
│
├─ Payment Consistency Score
│  └─ Regular patterns and frequency
│
├─ Inflow Reliability Score
│  └─ Consistency of incoming funds
│
├─ Balance Stability Score
│  └─ Health of current balance
│
└─ Transaction Success Rate Score
   └─ Percentage of successful TXs

Aggregate to 300-850 Credit Score:
├─ 750+: EXCELLENT
├─ 650-749: VERY GOOD
├─ 550-649: GOOD
├─ 450-549: FAIR
└─ <450: POOR
```

#### 2.2 Auto-Decisioning

```
Risk Assessment (4 Factors):

├─ Collateral Risk (30% weight)
│  ├─ LTV ratio calculation
│  ├─ Token volatility
│  └─ Liquidation probability
│
├─ Credit Risk (35% weight)
│  ├─ Credit score mapping
│  ├─ Payment history
│  └─ Default probability
│
├─ Liquidity Risk (20% weight)
│  ├─ Cash flow analysis
│  ├─ Balance adequacy
│  └─ Repayment capacity
│
└─ Behavioral Risk (15% weight)
   ├─ Transaction patterns
   ├─ Account age
   └─ Activity consistency

Overall Risk Score (0-100):
├─ 0-15: MINIMAL RISK → APPROVED
├─ 15-30: LOW RISK → APPROVED
├─ 30-50: MODERATE RISK → CONDITIONAL
├─ 50-75: HIGH RISK → PENDING REVIEW
└─ 75+: VERY HIGH RISK → DENIED
```

#### 2.3 Loan Terms Generation

```
Based on Risk Assessment:

MINIMAL RISK (Score 750+)
├─ Interest Rate: 8% APY
├─ LTV Ratio: 60%
├─ Max Borrow: Collateral × 60%
└─ Health Factor Threshold: 1.0

VERY GOOD (Score 650-749)
├─ Interest Rate: 10% APY
├─ LTV Ratio: 60%
└─ Health Factor Threshold: 1.0

GOOD (Score 550-649)
├─ Interest Rate: 12% APY
├─ LTV Ratio: 54%
└─ Health Factor Threshold: 1.1

FAIR (Score 450-549)
├─ Interest Rate: 15% APY
├─ LTV Ratio: 42%
└─ Health Factor Threshold: 1.2

POOR (Score <450)
├─ Interest Rate: 18% APY
├─ LTV Ratio: 30%
└─ Decision: DENIED or CONDITIONAL
```

#### 2.4 Collateral Deposit

```
User Actions:
1. Send Exen tokens to smart contract
2. Collateral locked in escrow vault
3. Collateral value calculated: Tokens × Current Price

Protocol Actions:
1. Lock tokens until repayment
2. Calculate borrow limit: Collateral Value × LTV%
3. Set liquidation threshold
4. Begin health monitoring

Escrow Management:
├─ Vault Address: EXEN_ESCROW_001
├─ Status: LOCKED
├─ Release Condition: Full loan repayment
└─ Liquidation Trigger: Health Factor < 1.0
```

#### 2.5 Loan Issuance

```
Prerequisites Met:
✓ Wallet approved
✓ Collateral deposited
✓ Health factor healthy

Execution:
1. USD stablecoin issued to borrower
2. TX hash recorded on-chain
3. Interest rate activated
4. Repayment clock starts

Borrower Receives:
├─ USD Amount: Approved loan amount
├─ Account Created: Shows balance + terms
├─ Interest Rate: Based on credit score
├─ Repayment Date: 180 days default
└─ Health Factor: Monitored 24/7
```

#### 2.6 Interest Accrual & Monitoring

```
Daily Operations:

Interest Calculation:
Daily Interest = Loan Amount × (APY / 365)

Example (14% APY on $5,000):
Daily = $5,000 × (14% / 365) = $1.92/day
Monthly = $1.92 × 30 = $57.60

Health Factor Monitoring:
HF = Collateral Value / Loan Amount

If Exen drops:
├─ $10,000 collateral → $8,000 value
├─ $5,000 loan
├─ HF = 8,000 / 5,000 = 1.6 (HEALTHY)

If drops more:
├─ $5,500 collateral value
├─ $5,000 loan
├─ HF = 1.1 (WARNING)

If drops further:
├─ $4,500 collateral value
├─ $5,000 loan
├─ HF = 0.9 (LIQUIDATION TRIGGERED)
```

#### 2.7 Interest Revenue Distribution

```
Monthly Interest Collected: $57.60

Split 50/50:

50% to Holder Rewards ($28.80)
├─ Convert USD to SOL
├─ Add to reward pool
├─ Distribute in next 15-min cycle
└─ Goes to all token holders

50% to Chart Buyback ($28.80)
├─ Add to buyback fund
├─ Available for RSI/MACD triggers
├─ Deploy on oversold signals
└─ Supports chart health
```

#### 2.8 Liquidation Mechanics

```
Trigger: Health Factor < 1.0

Liquidation Process:
1. Identify underwater position
2. Sell collateral on market
3. Repay loan from proceeds
4. Calculate surplus/deficit

If Surplus (Collateral > Loan):
├─ Surplus Amount: Collateral - Loan
├─ 50% → Holder Rewards
├─ 50% → Chart Buyback
└─ Example: $8,333 - $5,000 = $3,333 surplus

If Deficit (Collateral < Loan):
├─ Protocol covers loss
├─ Taken from lending reserves
├─ Triggers risk management protocols
└─ Rare with 60% LTV constraint
```

#### 2.9 Repayment & Collateral Release

```
User Action:
1. User repays USD + accrued interest
2. Transaction processed on-chain

Protocol Action:
1. Verify full repayment
2. Release collateral from escrow
3. Update borrower record
4. Return funds to pool

Collateral Released:
├─ User receives: Original Exen tokens + price appreciation
├─ Example: Deposited 100,000 EXEN
│   Price: $0.10 → $0.15
│   Still receive: 100,000 EXEN
│   But worth: $15,000 (instead of $10,000)
└─ User keeps all price upside
```

---

## 4️⃣ COMPLETE DAILY FLOW EXAMPLE

```
Day 1 Operations:

08:00 AM - CREATOR FEES ARRIVE
├─ $1,000 in fees collected
└─ Fee splitter processes

08:01 AM - FEE ALLOCATION
├─ $250 → Reward Engine (25%)
├─ $250 → Buyback Engine (25%)
└─ $500 → Lending Pool (50%)

08:15 AM - FIRST REWARD CYCLE
├─ Calculate proportions
├─ Holder 1 (50%): 125 SOL
├─ Holder 2 (25%): 62.5 SOL
├─ Holder 3 (15%): 37.5 SOL
└─ Holder 4 (10%): 25 SOL
    Total Distributed: 250 SOL

08:20 AM - BUYBACK ANALYSIS
├─ RSI 1m: 28 (Oversold)
├─ RSI 5m: 32 (Oversold)
├─ MACD 1m: Positive (Bullish)
├─ MACD 5m: Positive (Bullish)
└─ SIGNAL GENERATED

08:21 AM - BUYBACK EXECUTION
├─ Position Size: $25 (10% of $250)
├─ Market Buy: 250 EXEN @ $0.10
└─ Fund Remaining: $225

11:30 AM - NEW BORROWER INITIATES LENDING
├─ Wallet scanned automatically
├─ Credit score generated: 680 (VERY GOOD)
├─ Auto-decision: APPROVED
├─ Interest rate set: 10% APY
├─ LTV ratio set: 60%
└─ Borrower can proceed

11:45 AM - BORROWER DEPOSITS COLLATERAL
├─ Deposits: 50,000 EXEN
├─ Collateral value: $5,000 (@ $0.10)
├─ Max borrow: $3,000 (60% LTV)
├─ Borrow amount requested: $2,000
└─ Collateral locked in escrow

11:46 AM - FUNDS DISBURSED
├─ $2,000 USD sent to borrower
├─ Interest rate activated: 10% APY
├─ Repayment due: 180 days
└─ Health monitoring begins

12:00 PM - LENDING POOL INTEREST ACCRUED
├─ Daily interest: $0.55 ($2,000 × 10% / 365)
├─ Distributed (50/50):
│   ├─ $0.275 → Next reward cycle
│   └─ $0.275 → Buyback fund
└─ Cycle continues...

15:00 PM - SECOND REWARD CYCLE (15-min)
├─ Reward pool: $250 + $0.275 (interest)
├─ Total: $250.275
├─ Distributed proportionally to all holders
└─ Cycle 2 complete

DAILY SUMMARY:
├─ Total fees processed: $1,000
├─ Total rewards distributed: $250+
├─ Total buybacks executed: 250 EXEN
├─ Loan issued: $2,000
├─ Interest generated: $0.55
├─ Lending pool balance: $499.50 (+ $0.50 accrued)
└─ Status: Normal operations
```

---

## 5️⃣ REVENUE FLOW ECOSYSTEM

```
CREATOR FEES
    ↓
    ├─ 25% Holder Rewards ($250)
    │       ├─ 15-min distribution
    │       ├─ All holders included
    │       └─ Proportional allocation
    │
    ├─ 25% Chart Buyback ($250)
    │       ├─ Technical analysis
    │       ├─ Risk-managed execution
    │       └─ Price support
    │
    └─ 50% Lending Pool ($500)
            ├─ Pool growth
            ├─ Interest generation: $X/month
            │   ├─ 50% → Rewards ($X/2)
            │   └─ 50% → Buyback ($X/2)
            │
            └─ Liquidation surplus: $Y
                ├─ 50% → Rewards ($Y/2)
                └─ 50% → Buyback ($Y/2)

TOTAL MONTHLY ALLOCATION:
├─ Base Holder Rewards: $250 × 30 = $7,500
├─ + Interest allocation: ~$500 + lending interest
├─ Base Buyback Support: $250 × 30 = $7,500
├─ + Interest allocation: ~$500 + lending interest
└─ Lending Pool: $500 × 30 = $15,000
    ├─ Growing pool
    ├─ Generating interest
    └─ Creating surplus from liquidations
```

---

## 6️⃣ STATE TRANSITIONS & DECISION TREES

### Holder Flow
```
User acquires tokens
    ↓
Automatic eligibility in reward program
    ↓
15-minute cycles (no action needed)
    ↓
Receive SOL proportional to holdings
    ↓
Compound effect: Use rewards to buy more tokens
    ↓
Higher holdings = Higher future rewards
```

### Borrower Flow
```
User wants to borrow USD
    ↓
Connect wallet (auto-analysis triggered)
    ↓
Credit score generated
    ↓
Decision tree:
├─ APPROVED → Proceed to deposit
├─ CONDITIONAL → Meet conditions, proceed
├─ PENDING → Wait for manual review
└─ DENIED → Cannot proceed
    ↓
Deposit collateral
    ↓
Health verified (HF > 1.0)
    ↓
USD disbursed
    ↓
Interest accrues daily
    ↓
Repay anytime (full or partial)
    ↓
Release collateral + keep upside
```

### Liquidation Flow
```
Borrower has active loan
    ↓
Token price declines
    ↓
Health factor decreases
    ↓
HF < 1.0 threshold?
├─ NO → Continue monitoring
└─ YES → LIQUIDATION TRIGGERED
        ↓
        Sell collateral
        ↓
        Repay loan from proceeds
        ↓
        Surplus calculation:
        ├─ Sale Proceeds > Loan = SURPLUS
        │   ├─ 50% → Holder Rewards
        │   └─ 50% → Chart Buyback
        │
        └─ Sale Proceeds < Loan = DEFICIT
            └─ Protocol covers loss
```

---

## 7️⃣ DATA FLOW & CALCULATIONS

### Every 15 Minutes (Reward Distribution)

```
Input:
├─ Creator fees accumulated
├─ Interest collected from lending
└─ Liquidation surplus

Calculation:
├─ Total reward pool = Fees + (Interest × 0.5) + (Liquidation × 0.5)
├─ For each holder:
│   └─ Reward = (Holder Balance / Total Supply) × Reward Pool
└─ Round to 6 decimals (SOL standard)

Output:
├─ SOL transfer to each holder
├─ Event logged on-chain
└─ Analytics updated
```

### When Buy Signal Detected (Chart Support)

```
Input:
├─ Price data (1m and 5m)
├─ RSI calculations
├─ MACD calculations
└─ Buyback fund balance

Decision:
├─ RSI < 30 on both? YES
├─ MACD > 0 on both? YES
├─ In cooldown? NO
└─ Volatility high? NO → Execute standard size

Calculation:
├─ Position size = Fund × 10% × Signal strength
├─ Adjusted for volatility
└─ Capped at max trade limit

Execution:
├─ Market order placed
├─ Slippage tracked
├─ Price impact calculated
└─ Transaction logged

Output:
├─ Tokens purchased
├─ Fund reduced
└─ Cooldown timer set (5 minutes)
```

### When Loan is Issued

```
Input:
├─ Borrower wallet analysis
├─ Credit score (300-850)
├─ Collateral amount
├─ Requested borrow amount
└─ Current token price

Calculation:
├─ Credit rating determined
├─ Interest rate set (based on score)
├─ LTV ratio set (based on risk)
├─ Max borrow = Collateral × Price × LTV%
└─ Actual loan = min(Requested, Max borrow, Pool available)

Conditions:
├─ Health factor = Collateral Value / Loan Amount
├─ Must be ≥ 1.0
└─ Liquidation threshold varies by rating

Output:
├─ Loan approved/denied
├─ Terms generated
├─ Collateral locked
└─ USD issued
```

### When Interest Accrues (Daily)

```
Input:
├─ Loan amount
├─ Interest rate (APY)
├─ Days outstanding

Calculation:
├─ Daily interest = Loan × (Rate / 365)
├─ Accumulated interest = Daily × Days
├─ 50% allocation = Total / 2

Output:
├─ Holder reward portion
├─ Buyback support portion
├─ Health factor recalculated (daily)
└─ Liquidation check performed (daily)
```

---

## 8️⃣ SECURITY & MONITORING

### Continuous Monitoring (24/7)

```
Reward Engine:
├─ Verify fee collection
├─ Confirm distributions sent
└─ Check holder eligibility

Buyback Engine:
├─ Monitor signal accuracy
├─ Track execution quality
├─ Verify price impact
└─ Ensure no flash crashes

Lending Pool:
├─ Monitor all health factors
├─ Track collateral values (price feeds)
├─ Prepare liquidations
├─ Monitor interest accrual
├─ Verify reserve adequacy
└─ Track utilization rates
```

### Risk Management Thresholds

```
Reward Distribution:
├─ Minimum: All eligible holders paid
├─ Maximum: No single holder gets >50%
└─ Frequency: Exactly every 15 minutes

Buyback Execution:
├─ Max position: 10% of available funds
├─ Minimum cooldown: 5 minutes
├─ Stop loss: RSI > 70
└─ Volatility reduction: 50% size cut if high vol

Lending Pool:
├─ Minimum pool: $50k to activate
├─ Maximum LTV: 60% (adjusted down by risk)
├─ Minimum health: 1.0 (liquidation at <1.0)
├─ Maximum interest: 18% APY
├─ Minimum interest: 5% APY
└─ Per-user cap: $500k USD max loan
```

---

## ✅ COMPLETE SYSTEM SUMMARY

| Component | Input | Process | Output | Frequency |
|-----------|-------|---------|--------|-----------|
| **Reward Engine** | Creator fees (25%) | Calculate proportions | SOL to holders | Every 15 min |
| **Buyback Engine** | Creator fees (25%) | RSI/MACD analysis | Buy orders | On signal |
| **Lending Pool** | Creator fees (50%) | Collateral mgmt | USD loans | On approval |
| **Interest Revenue** | Loan interest | 50/50 split | Rewards + Buyback | Daily accrual |
| **Liquidation** | Underwater positions | Collateral sale | Surplus distribution | On trigger |
| **Credit Scoring** | Wallet analysis | 5-factor assessment | Credit score | On application |
| **Auto-Decisioning** | Credit score + risk | 4-factor risk model | Approve/Deny | On application |

---

## 🎯 Key Metrics to Track

```
Real-Time Dashboards:
├─ Reward Distribution
│   ├─ SOL per holder (15-min)
│   ├─ Total distributed (lifetime)
│   └─ Efficiency rate (%)
│
├─ Chart Support
│   ├─ Buys executed
│   ├─ Average buy price
│   ├─ Total tokens accumulated
│   └─ Price support effectiveness
│
├─ Lending Pool
│   ├─ Pool balance
│   ├─ Total borrowed
│   ├─ Active loans
│   ├─ Interest revenue (daily/monthly)
│   ├─ Utilization rate (%)
│   ├─ Average interest rate
│   └─ Liquidation rate (%)
│
└─ Overall Protocol
    ├─ Total fees processed
    ├─ Total value distributed
    ├─ Community growth
    ├─ Loan default rate
    └─ System uptime (%)
```

---

This is the complete end-to-end mapping of how Exen Protocol flows from fee collection through all three engines, with wallet analysis and credit scoring integrated into the lending pipeline.
