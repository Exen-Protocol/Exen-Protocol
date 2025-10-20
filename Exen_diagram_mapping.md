# 📊 Exen Protocol - System Diagrams

This document contains comprehensive system architecture and data flow diagrams for the Exen Protocol, rendered using Mermaid diagrams for optimal GitHub compatibility.

## 🏗️ System Architecture Overview

```mermaid
graph TB
    subgraph "Exen Protocol Ecosystem"
        CF[Creator Fees<br/>💰 100%]
        FS[Fee Splitter<br/>⚖️ 25/25/50 Split]
        
        subgraph "Reward Engine"
            RE[Reward Calculator<br/>📊]
            RD[Reward Distributor<br/>📤]
        end
        
        subgraph "Chart Buyback Engine"
            TA[Technical Analyzer<br/>📈]
            BE[Buy Executor<br/>🛒]
        end
        
        subgraph "Lending Pool Infrastructure"
            LP[Lending Pool<br/>🏦 $50k Min]
            IR[Interest Revenue<br/>💸]
            LIQ[Liquidation Engine<br/>⚡]
        end
        
        subgraph "Data Sources"
            PF[Price Feeds<br/>💹]
            RSI[RSI Data<br/>📊]
            MACD[MACD Data<br/>📈]
            OR[Oracles<br/>🔮]
        end
        
        subgraph "Outputs"
            H[Token Holders<br/>👥]
            M[Market<br/>🏪]
            B[Borrowers<br/>💼]
            A[Analytics<br/>📊]
        end
    end
    
    %% Main flow
    CF --> FS
    FS -->|25%| RE
    FS -->|25%| TA
    FS -->|50%| LP
    
    %% Data flow
    PF --> TA
    RSI --> TA
    MACD --> TA
    OR --> LP
    
    %% Processing
    RE --> RD
    TA --> BE
    LP --> IR
    LP --> LIQ
    
    %% Revenue redistribution from lending
    IR -->|50%| RE
    IR -->|50%| TA
    LIQ -->|50%| RE
    LIQ -->|50%| TA
    
    %% Outputs
    RD --> H
    BE --> M
    LP --> B
    RD --> A
    BE --> A
    LP --> A
    
    %% Styling
    classDef primary fill:#9945FF,stroke:#000,stroke-width:2px,color:#fff
    classDef secondary fill:#00D9FF,stroke:#000,stroke-width:2px,color:#000
    classDef accent fill:#F7931A,stroke:#000,stroke-width:2px,color:#fff
    classDef success fill:#28a745,stroke:#000,stroke-width:2px,color:#fff
    classDef lending fill:#e91e63,stroke:#000,stroke-width:2px,color:#fff
    
    class CF,FS primary
    class RE,RD,PF,RSI,MACD,OR secondary
    class TA,BE accent
    class LP,IR,LIQ lending
    class H,M,B,A success
```

## 🔄 Data Flow Architecture

```mermaid
flowchart TD
    subgraph "Input Layer"
        A1[Creator Fees<br/>💰]
        A2[Price Data<br/>💹]
        A3[RSI Indicators<br/>📊]
        A4[MACD Signals<br/>📈]
        A5[Holder Data<br/>👥]
        A6[Collateral Value<br/>🏦]
        A7[Interest Payments<br/>💸]
    end
    
    subgraph "Processing Layer"
        B1[Fee Splitter<br/>⚖️ 25/25/50]
        B2[Reward Calculator<br/>🧮]
        B3[Technical Analyzer<br/>🔍]
        B4[Buy Executor<br/>⚡]
        B5[Lending Pool<br/>🏦]
        B6[Interest Engine<br/>💰]
    end
    
    subgraph "Output Layer"
        C1[SOL Distribution<br/>💸 25%]
        C2[Holder Rewards<br/>🎁]
        C3[Support Buys<br/>🛒 25%]
        C4[Price Impact<br/>📈]
        C5[USD Loans<br/>💵 50%]
        C6[Interest Revenue<br/>💰]
        C7[Analytics Data<br/>📊]
    end
    
    %% Input to Processing
    A1 --> B1
    A2 --> B3
    A3 --> B3
    A4 --> B3
    A5 --> B2
    A6 --> B5
    A7 --> B6
    
    %% Processing to Output
    B1 -->|25%| C1
    B1 -->|25%| C3
    B1 -->|50%| C5
    B2 --> C2
    B3 --> C3
    B3 --> C4
    B4 --> C3
    B5 --> C5
    B5 --> C6
    B6 --> C7
    
    %% Revenue redistribution
    C6 -.->|50%| B2
    C6 -.->|50%| B4
    
    %% Cross connections
    B1 -.-> B2
    B3 -.-> B4
    B5 -.-> B6
    
    %% Styling
    classDef input fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef output fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef lending fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class A1,A2,A3,A4,A5,A6,A7 input
    class B1,B2,B3,B4,B5,B6 process
    class C1,C2,C3,C4,C5,C6,C7 output
```

## 🧠 Technical Analysis Decision Flow

```mermaid
flowchart TD
    Start([Price Data Input<br/>📊]) --> RSI[Calculate RSI<br/>1m & 5m<br/>📈]
    Start --> MACD[Calculate MACD<br/>1m & 5m<br/>📊]
    
    RSI --> RSI_Check{RSI < 30?<br/>Oversold?<br/>Both Timeframes?}
    MACD --> MACD_Check{MACD > 0?<br/>Bullish Cross?<br/>Both Timeframes?}
    
    RSI_Check -->|Yes| RSI_True[RSI Signal<br/>✅]
    RSI_Check -->|No| RSI_False[Wait<br/>⏳]
    
    MACD_Check -->|Yes| MACD_True[MACD Signal<br/>✅]
    MACD_Check -->|No| MACD_False[Wait<br/>⏳]
    
    RSI_True --> Both_Check{Both Signals<br/>Confirmed?}
    MACD_True --> Both_Check
    
    Both_Check -->|Yes| Volatility{Check<br/>Volatility}
    Both_Check -->|No| Wait[Wait for Next<br/>Cycle ⏰]
    
    Volatility -->|High| Reduce[Reduce Position<br/>50% 📉]
    Volatility -->|Normal| Normal[Standard Position<br/>10% 📊]
    
    Reduce --> Execute[Execute Buy<br/>🛒]
    Normal --> Execute
    
    RSI_False --> Wait
    MACD_False --> Wait
    
    Execute --> Cooldown[5-Minute<br/>Cooldown ⏱️]
    Cooldown --> Log[Log Transaction<br/>📝]
    Log --> Update[Update Analytics<br/>📊]
    Update --> Wait
    
    Wait --> Start
    
    %% Styling
    classDef start fill:#4caf50,stroke:#000,stroke-width:3px,color:#fff
    classDef process fill:#2196f3,stroke:#000,stroke-width:2px,color:#fff
    classDef decision fill:#ff9800,stroke:#000,stroke-width:2px,color:#fff
    classDef success fill:#4caf50,stroke:#000,stroke-width:2px,color:#fff
    classDef wait fill:#f44336,stroke:#000,stroke-width:2px,color:#fff
    
    class Start start
    class RSI,MACD,RSI_True,MACD_True,Execute,Log,Update,Reduce,Normal process
    class RSI_Check,MACD_Check,Both_Check,Volatility decision
    class Execute success
    class RSI_False,MACD_False,Wait,Cooldown wait
```

## 🏦 Lending Pool Flow

```mermaid
flowchart TD
    subgraph "Pool Funding"
        Fees[Creator Fees<br/>50% Allocation<br/>💰]
        Threshold{Pool Balance<br/>≥ $50,000?}
        Inactive[Pool Inactive<br/>⏳]
        Active[Pool Active<br/>✅]
    end
    
    subgraph "Borrowing Process"
        Deposit[User Deposits<br/>Exen Collateral<br/>🔒]
        CalcLimit[Calculate Limit<br/>60% LTV<br/>📊]
        Borrow[Issue USD Loan<br/>💵]
        Monitor[Monitor Health<br/>📈]
    end
    
    subgraph "Revenue Generation"
        Interest[Interest Accrues<br/>8-18% APY<br/>💰]
        Revenue[Interest Revenue<br/>100%<br/>💸]
        Split{50/50 Split}
        ToHolders[50% → Holder Rewards<br/>🎁]
        ToBuyback[50% → Chart Buyback<br/>📈]
    end
    
    subgraph "Liquidation"
        Health{Health Factor<br/>< 1.0?}
        Liquidate[Sell Collateral<br/>⚡]
        RepayLoan[Repay Loan<br/>✅]
        Surplus[Surplus Funds<br/>💰]
    end
    
    %% Pool funding flow
    Fees --> Threshold
    Threshold -->|No| Inactive
    Threshold -->|Yes| Active
    Inactive --> Fees
    
    %% Borrowing flow
    Active --> Deposit
    Deposit --> CalcLimit
    CalcLimit --> Borrow
    Borrow --> Monitor
    
    %% Revenue flow
    Borrow --> Interest
    Interest --> Revenue
    Revenue --> Split
    Split --> ToHolders
    Split --> ToBuyback
    
    %% Liquidation flow
    Monitor --> Health
    Health -->|Yes| Liquidate
    Health -->|No| Monitor
    Liquidate --> RepayLoan
    RepayLoan --> Surplus
    Surplus --> Split
    
    %% Styling
    classDef funding fill:#9945FF,stroke:#000,stroke-width:2px,color:#fff
    classDef borrowing fill:#00D9FF,stroke:#000,stroke-width:2px,color:#000
    classDef revenue fill:#4caf50,stroke:#000,stroke-width:2px,color:#fff
    classDef liquidation fill:#f44336,stroke:#000,stroke-width:2px,color:#fff
    
    class Fees,Threshold,Inactive,Active funding
    class Deposit,CalcLimit,Borrow,Monitor borrowing
    class Interest,Revenue,Split,ToHolders,ToBuyback revenue
    class Health,Liquidate,RepayLoan,Surplus liquidation
```

## 💰 Fee Distribution Flow

```mermaid
graph TD
    A[Creator Fees<br/>100%<br/>💰] --> B[Fee Splitter<br/>⚖️]
    
    B -->|25%| C[Holder Rewards<br/>SOL Airdrops<br/>Every 15min<br/>🎁]
    B -->|25%| D[Chart Buyback<br/>RSI/MACD Triggered<br/>Algorithmic<br/>📈]
    B -->|50%| E[Lending Pool<br/>USD Loans<br/>60% LTV<br/>🏦]
    
    E --> F[Interest Revenue<br/>8-18% APY<br/>💰]
    
    F -->|50%| G[Additional Holder Rewards<br/>SOL Distribution<br/>🎁]
    F -->|50%| H[Additional Buyback Support<br/>Enhanced Power<br/>📊]
    
    E --> I[Liquidation Surplus<br/>💸]
    I -->|50%| G
    I -->|50%| H
    
    C --> J[All Token Holders<br/>Proportional Distribution<br/>👥]
    D --> K[Market Buys<br/>Price Support<br/>🛒]
    G --> J
    H --> K
    
    %% Styling
    classDef primary fill:#9945FF,stroke:#000,stroke-width:3px,color:#fff
    classDef rewards fill:#4caf50,stroke:#000,stroke-width:2px,color:#fff
    classDef buyback fill:#ff9800,stroke:#000,stroke-width:2px,color:#fff
    classDef lending fill:#e91e63,stroke:#000,stroke-width:2px,color:#fff
    classDef output fill:#00bcd4,stroke:#000,stroke-width:2px,color:#fff
    
    class A,B primary
    class C,G,J rewards
    class D,H,K buyback
    class E,F,I lending
```

## 📊 Complete Revenue Flow Diagram

```mermaid
flowchart TB
    subgraph "Primary Revenue"
        A[Creator Fees<br/>💰]
    end
    
    subgraph "Primary Distribution (25/25/50)"
        B[25% Holder Rewards<br/>👥]
        C[25% Chart Buyback<br/>📈]
        D[50% Lending Pool<br/>🏦]
    end
    
    subgraph "Lending Revenue Generation"
        E[Interest Revenue<br/>8-18% APY<br/>💰]
        F[Liquidation Surplus<br/>💸]
    end
    
    subgraph "Secondary Distribution (50/50)"
        G[50% → Holders<br/>🎁]
        H[50% → Buyback<br/>📊]
    end
    
    subgraph "Value Creation"
        I[Passive Income<br/>💸]
        J[Price Stability<br/>📊]
        K[Access to Capital<br/>🏦]
        L[Community Growth<br/>🌱]
    end
    
    subgraph "Ecosystem Benefits"
        M[Increased Holdings<br/>📈]
        N[Reduced Volatility<br/>⚖️]
        O[Lending Adoption<br/>💼]
        P[Network Effects<br/>🕸️]
    end
    
    A --> B
    A --> C
    A --> D
    
    D --> E
    D --> F
    
    E --> G
    E --> H
    F --> G
    F --> H
    
    B --> I
    C --> J
    D --> K
    G --> I
    H --> J
    
    I --> L
    J --> L
    K --> L
    
    L --> M
    L --> N
    L --> O
    L --> P
    
    %% Styling
    classDef revenue fill:#4caf50,stroke:#000,stroke-width:2px,color:#fff
    classDef distribution fill:#2196f3,stroke:#000,stroke-width:2px,color:#fff
    classDef lending fill:#e91e63,stroke:#000,stroke-width:2px,color:#fff
    classDef value fill:#ff9800,stroke:#000,stroke-width:2px,color:#fff
    classDef benefit fill:#9c27b0,stroke:#000,stroke-width:2px,color:#fff
    
    class A revenue
    class B,C,D distribution
    class E,F,G,H lending
    class I,J,K,L value
    class M,N,O,P benefit
```

## 🎯 Protocol Performance Metrics

```mermaid
graph LR
    subgraph "Key Performance Indicators"
        A[Distribution Success<br/>Target: 99.8%]
        B[Buyback Accuracy<br/>Target: 67.3%]
        C[Holder Retention<br/>Target: 73.2%]
        D[Price Stability<br/>Target: +24.7%]
        E[Fee Efficiency<br/>Target: 97.1%]
        F[Lending Utilization<br/>Target: 60%]
        G[Loan Health<br/>Target: >1.2]
        H[Interest Revenue<br/>Target: 12-18%]
    end
    
    subgraph "Target Benchmarks"
        I[Distribution: >99%]
        J[Accuracy: >60%]
        K[Retention: >70%]
        L[Stability: >20%]
        M[Efficiency: >95%]
        N[Utilization: 40-70%]
        O[Health Factor: >1.0]
        P[APY: 12-18%]
    end
    
    A --> I
    B --> J
    C --> K
    D --> L
    E --> M
    F --> N
    G --> O
    H --> P
    
    %% Styling
    classDef metric fill:#e8f5e8,stroke:#4caf50,stroke-width:2px
    classDef target fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef lending fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    
    class A,B,C,D,E metric
    class F,G,H lending
    class I,J,K,L,M,N,O,P target
```

## 🌐 Ecosystem Stakeholder Map

```mermaid
graph TB
    subgraph "Exen Protocol Ecosystem"
        Protocol[Exen Protocol<br/>🏛️<br/>Core Engine]
        
        subgraph "Primary Stakeholders"
            Holders[Token Holders<br/>👥<br/>Passive Income]
            Borrowers[Borrowers<br/>💼<br/>Access to Capital]
            Creators[Content Creators<br/>🎨<br/>Fee Payers]
        end
        
        subgraph "Secondary Stakeholders"
            Traders[Active Traders<br/>📈<br/>Market Participants]
            Analysts[Data Analysts<br/>📊<br/>Insight Seekers]
            Developers[Protocol Developers<br/>👨‍💻<br/>Builders]
            Liquidators[Liquidators<br/>⚡<br/>Risk Managers]
        end
        
        subgraph "External Systems"
            Market[Solana Market<br/>🏪<br/>Trading Venue]
            Oracles[Price Oracles<br/>🔮<br/>Pyth Network]
            Analytics[Analytics Platforms<br/>📈<br/>Data Consumers]
            Stablecoin[USD Stablecoin<br/>💵<br/>Loan Currency]
        end
    end
    
    %% Primary relationships
    Creators -->|Pay Fees| Protocol
    Protocol -->|SOL Rewards| Holders
    Protocol -->|USD Loans| Borrowers
    Protocol -->|Support Buys| Market
    Protocol -->|Data Feed| Analytics
    
    %% Secondary relationships
    Traders -->|Trade Tokens| Market
    Analysts -->|Consume Data| Analytics
    Developers -->|Maintain| Protocol
    Liquidators -->|Monitor Health| Protocol
    Borrowers -->|Deposit Collateral| Protocol
    Borrowers -->|Pay Interest| Protocol
    
    %% External relationships
    Protocol -->|Fetch Prices| Oracles
    Protocol -->|Issue Loans| Stablecoin
    Market -->|Price Data| Protocol
    
    %% Styling
    classDef protocol fill:#9945FF,stroke:#000,stroke-width:3px,color:#fff
    classDef primary fill:#00D9FF,stroke:#000,stroke-width:2px,color:#000
    classDef secondary fill:#F7931A,stroke:#000,stroke-width:2px,color:#fff
    classDef external fill:#28a745,stroke:#000,stroke-width:2px,color:#fff
    
    class Protocol protocol
    class Holders,Borrowers,Creators primary
    class Traders,Analysts,Developers,Liquidators secondary
    class Market,Oracles,Analytics,Stablecoin external
```

## ⚡ Real-Time Processing Timeline

```mermaid
gantt
    title Exen Protocol Processing Timeline
    dateFormat X
    axisFormat %M:%S
    
    section Reward Cycle
    Collect Fees          :active, fees, 0, 30s
    Calculate Rewards    :calc, after fees, 15s
    Distribute SOL       :dist, after calc, 45s
    
    section Buyback Cycle
    Analyze Market       :analyze, 0, 45s
    RSI/MACD Signals     :signals, after analyze, 15s
    Execute Buys         :execute, after signals, 30s
    Cooldown Period      :cooldown, after execute, 300s
    
    section Lending Operations
    Process Collateral   :collateral, 0, 60s
    Issue Loans          :loans, after collateral, 30s
    Accrue Interest      :interest, 0, 900s
    Monitor Health       :health, 0, 900s
    
    section Data Processing
    Update Analytics     :analytics, 0, 90s
    Log Transactions     :logging, 0, 90s
    Monitor Performance  :monitor, 0, 90s
```

## 🔧 Smart Contract Architecture

```mermaid
graph TB
    subgraph "Smart Contract Layer"
        Main[Main Protocol Contract<br/>📜]
        
        subgraph "Core Modules"
            FeeSplitter[Fee Splitter<br/>⚖️ 25/25/50]
            RewardEngine[Reward Engine<br/>💸 25%]
            BuybackEngine[Buyback Engine<br/>🛒 25%]
            LendingPool[Lending Pool<br/>🏦 50%]
        end
        
        subgraph "Lending Submodules"
            Collateral[Collateral Manager<br/>🔒]
            LoanIssuer[Loan Issuer<br/>💵]
            InterestCalc[Interest Calculator<br/>💰]
            Liquidator[Liquidation Engine<br/>⚡]
        end
        
        subgraph "Utility Contracts"
            Oracle[Price Oracle<br/>🔮]
            Analytics[Analytics Contract<br/>📊]
            Treasury[Treasury Contract<br/>🏦]
        end
        
        subgraph "External Integrations"
            Jupiter[Jupiter API<br/>🪐]
            Pyth[Pyth Network<br/>📡]
            Solana[Solana RPC<br/>⛓️]
            USDC[USDC Contract<br/>💵]
        end
    end
    
    %% Main contract connections
    Main --> FeeSplitter
    FeeSplitter --> RewardEngine
    FeeSplitter --> BuybackEngine
    FeeSplitter --> LendingPool
    
    %% Lending connections
    LendingPool --> Collateral
    LendingPool --> LoanIssuer
    LendingPool --> InterestCalc
    LendingPool --> Liquidator
    
    %% Revenue redistribution
    InterestCalc -.->|50%| RewardEngine
    InterestCalc -.->|50%| BuybackEngine
    Liquidator -.->|Surplus 50%| RewardEngine
    Liquidator -.->|Surplus 50%| BuybackEngine
    
    %% Module connections
    RewardEngine --> Treasury
    BuybackEngine --> Treasury
    LendingPool --> Treasury
    
    %% External connections
    Oracle --> Pyth
    BuybackEngine --> Jupiter
    Analytics --> Main
    Treasury --> Solana
    LendingPool --> USDC
    Collateral --> Oracle
    Liquidator --> Oracle
    
    %% Styling
    classDef main fill:#9945FF,stroke:#000,stroke-width:3px,color:#fff
    classDef core fill:#00D9FF,stroke:#000,stroke-width:2px,color:#000
    classDef lending fill:#e91e63,stroke:#000,stroke-width:2px,color:#fff
    classDef utility fill:#F7931A,stroke:#000,stroke-width:2px,color:#fff
    classDef external fill:#28a745,stroke:#000,stroke-width:2px,color:#fff
    
    class Main main
    class FeeSplitter,RewardEngine,BuybackEngine,LendingPool core
    class Collateral,LoanIssuer,InterestCalc,Liquidator lending
    class Oracle,Analytics,Treasury utility
    class Jupiter,Pyth,Solana,USDC external
```

## 📈 Lending Pool Mechanics

```mermaid
graph TB
    subgraph "User Actions"
        A[User Deposits<br/>Exen Tokens<br/>🔒]
        B[Collateral Locked<br/>Smart Contract<br/>⛓️]
        C[Calculate Borrow Limit<br/>60% LTV<br/>📊]
        D[Issue USD Loan<br/>💵]
    end
    
    subgraph "Interest & Monitoring"
        E[Interest Accrues<br/>8-18% APY<br/>Based on Utilization<br/>💰]
        F[Health Factor<br/>Monitored 24/7<br/>📈]
        G[User Repays<br/>+ Interest<br/>✅]
    end
    
    subgraph "Risk Management"
        H{Health Factor<br/>< 1.0?}
        I[Liquidation Triggered<br/>⚡]
        J[Sell Collateral<br/>Market Order<br/>🛒]
        K[Repay Loan<br/>✓]
        L{Surplus?}
        M[50% to Holders<br/>50% to Buyback<br/>💸]
    end
    
    subgraph "Revenue Distribution"
        N[Interest Revenue<br/>Collected<br/>💰]
        O[50% Split]
        P[50% Holder Rewards<br/>SOL Distribution<br/>🎁]
        Q[50% Buyback Support<br/>Enhanced Power<br/>📈]
    end
    
    %% Flow
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> H
    H -->|Yes| I
    H -->|No| E
    I --> J
    J --> K
    K --> L
    L -->|Yes| M
    L -->|No| K
    
    E --> G
    G --> N
    N --> O
    O --> P
    O --> Q
    
    M -.-> O
    
    %% Styling
    classDef user fill:#2196f3,stroke:#000,stroke-width:2px,color:#fff
    classDef interest fill:#4caf50,stroke:#000,stroke-width:2px,color:#fff
    classDef risk fill:#f44336,stroke:#000,stroke-width:2px,color:#fff
    classDef revenue fill:#9c27b0,stroke:#000,stroke-width:2px,color:#fff
    
    class A,B,C,D user
    class E,F,G interest
    class H,I,J,K,L,M risk
    class N,O,P,Q revenue
```

## 🎯 Success Metrics Dashboard

```mermaid
quadrantChart
    title Exen Protocol Success Metrics
    x-axis Low Impact --> High Impact
    y-axis Low Effort --> High Effort
    
    quadrant-1 High Impact, High Effort
    quadrant-2 Low Impact, High Effort
    quadrant-3 Low Impact, Low Effort
    quadrant-4 High Impact, Low Effort
    
    "Distribution Success": [0.9, 0.3]
    "Buyback Accuracy": [0.7, 0.6]
    "Holder Retention": [0.8, 0.7]
    "Price Stability": [0.9, 0.5]
    "Fee Efficiency": [0.6, 0.4]
    "Lending Adoption": [0.85, 0.85]
    "Interest Revenue": [0.8, 0.6]
    "Liquidation Health": [0.7, 0.8]
    "Community Growth": [0.8, 0.9]
    "Technical Innovation": [0.9, 0.9]
```

## 💵 Lending Pool Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Accumulation: Protocol Launch
    
    Accumulation --> Accumulation: Fees < $50k
    Accumulation: 50% of fees deposited
    Accumulation: Display progress
    Accumulation: No lending available
    
    Accumulation --> Activation: Pool ≥ $50k
    
    Activation --> Active: Lending Enabled
    Activation: Collateral deposits open
    Activation: Loan issuance begins
    
    Active --> Active: Normal Operations
    Active: Users deposit collateral
    Active: Users borrow USD
    Active: Interest accrues
    Active: Revenue distributes
    
    Active --> HighUtilization: Utilization > 80%
    HighUtilization: Increase interest rates
    HighUtilization: Incentivize repayments
    HighUtilization --> Active: Utilization normalizes
    
    Active --> LowUtilization: Utilization < 20%
    LowUtilization: Reduce interest rates
    LowUtilization: Encourage borrowing
    LowUtilization --> Active: Utilization normalizes
    
    Active --> Liquidation: Health Factor < 1.0
    Liquidation: Sell collateral
    Liquidation: Repay loan
    Liquidation: Distribute surplus
    Liquidation --> Active: Complete
    
    Active --> Growth: Continuous fees
    Growth: Pool size increases
    Growth: More lending capacity
    Growth: Higher revenue generation
    Growth --> Active: Ongoing
```

## 🔄 Interest Revenue Cycle

```mermaid
sequenceDiagram
    participant Borrower
    participant LendingPool
    participant InterestEngine
    participant HolderRewards
    participant BuybackEngine
    
    Borrower->>LendingPool: Borrow $10,000 USD
    Note over LendingPool: 14% APY applied
    
    loop Daily Interest Accrual
        LendingPool->>InterestEngine: Calculate Daily Interest
        Note over InterestEngine: $10,000 × 14% / 365<br/>= $3.84 per day
    end
    
    alt Monthly Distribution
        InterestEngine->>InterestEngine: Accumulate Revenue
        Note over InterestEngine: Monthly Total:<br/>$3.84 × 30 = $115.20
        
        InterestEngine->>HolderRewards: 50% = $57.60
        Note over HolderRewards: Convert to SOL<br/>Distribute to holders
        
        InterestEngine->>BuybackEngine: 50% = $57.60
        Note over BuybackEngine: Add to buyback funds<br/>Deploy on RSI/MACD signals
    end
    
    alt User Repayment
        Borrower->>LendingPool: Repay Loan + Interest
        LendingPool->>InterestEngine: Process Interest Payment
        InterestEngine->>HolderRewards: 50% to Rewards
        InterestEngine->>BuybackEngine: 50% to Buyback
    end
```

## 📊 Comprehensive Value Flow

```mermaid
sankey-beta

Creator Fees,Holder Rewards (25%),25
Creator Fees,Chart Buyback (25%),25
Creator Fees,Lending Pool (50%),50

Lending Pool (50%),Interest Revenue,15
Lending Pool (50%),Liquidation Surplus,5

Interest Revenue,Additional Holder Rewards,7.5
Interest Revenue,Additional Buyback Support,7.5

Liquidation Surplus,Additional Holder Rewards,2.5
Liquidation Surplus,Additional Buyback Support,2.5

Holder Rewards (25%),SOL Distribution,25
Additional Holder Rewards,SOL Distribution,10

Chart Buyback (25%),Market Buys,25
Additional Buyback Support,Market Buys,10

SOL Distribution,Token Holders,35
Market Buys,Price Stability,35
```

---

## 📋 Diagram Usage

These diagrams are designed to be:

- **GitHub Compatible**: All diagrams use Mermaid syntax for perfect GitHub rendering
- **Interactive**: Click and explore relationships in supported viewers
- **Comprehensive**: Cover all aspects of the 25/25/50 split and lending infrastructure
- **Maintainable**: Easy to update as the protocol evolves
- **Professional**: Clean, consistent styling throughout

## 🔄 Updating Diagrams

To update these diagrams:

1. Modify the Mermaid code in this document
2. Test rendering in GitHub or Mermaid Live Editor
3. Update corresponding documentation as needed
4. Version control all changes

## 📖 Diagram Legend

### Color Coding
- **Purple (#9945FF)**: Main protocol components
- **Cyan (#00D9FF)**: Reward engine and data sources
- **Orange (#F7931A)**: Chart buyback and technical analysis
- **Pink (#e91e63)**: Lending pool infrastructure
- **Green (#28a745)**: Outputs and success metrics
- **Blue (#2196f3)**: Processing and user actions
- **Red (#f44336)**: Risk management and liquidations

### Icons Used
- 💰 Money/Fees
- ⚖️ Balance/Splitting
- 📊 Analysis/Metrics
- 📈 Charts/Growth
- 🏦 Banking/Lending
- 💸 Rewards/Distribution
- 🛒 Buying/Trading
- 👥 Users/Holders
- 🔒 Locked/Collateral
- ⚡ Liquidation/Action
- 💵 USD/Stablecoin
- 🔮 Oracles/Data
- ✅ Success/Confirmation

---

*Last updated: January 2025 - Exen Protocol v1.0*
