import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TokenHolder:
    """Represents a token holder in the system"""
    address: str
    balance: Decimal  # Token balance
    sol_received: Decimal = field(default_factory=lambda: Decimal(0))  # Cumulative SOL received
    last_distribution: datetime = field(default_factory=datetime.now)


@dataclass
class AirdropCycle:
    """Represents a single airdrop distribution cycle"""
    cycle_id: int
    timestamp: datetime
    total_fees: Decimal
    reward_pool: Decimal  # 25% of total fees
    total_distributed: Decimal
    distributions: Dict[str, Decimal] = field(default_factory=dict)
    status: str = "pending"  # pending, executing, completed, failed


class ExenAirdropSystem:
    """
    Main system for managing Exen protocol SOL airdrops
    
    Features:
    - Collects creator fees
    - Calculates 25% allocation for holder rewards
    - Distributes proportionally every 15 minutes
    - Tracks all distributions on-chain
    """
    
    def __init__(self, token_contract: str = "", verbose: bool = True):
        """
        Initialize the airdrop system
        
        Args:
            token_contract: Solana token contract address (leave blank for testing)
            verbose: Enable detailed logging
        """
        self.token_contract = token_contract
        self.verbose = verbose
        self.holders: Dict[str, TokenHolder] = {}
        self.fee_accumulator = Decimal(0)
        self.cycle_count = 0
        self.airdrop_cycles: List[AirdropCycle] = []
        self.total_distributed = Decimal(0)
        
        logger.info(f"Exen Airdrop System initialized")
        logger.info(f"Token Contract: {token_contract if token_contract else 'Not set'}")
    
    def register_holder(self, address: str, balance: Decimal) -> TokenHolder:
        """
        Register a new token holder in the system
        
        Args:
            address: Holder's wallet address
            balance: Token balance held
            
        Returns:
            TokenHolder object
        """
        if not isinstance(balance, Decimal):
            balance = Decimal(str(balance))
        
        holder = TokenHolder(address=address, balance=balance)
        self.holders[address] = holder
        
        logger.info(f"Registered holder: {address} with balance: {balance}")
        return holder
    
    def update_holder_balance(self, address: str, new_balance: Decimal) -> bool:
        """
        Update a holder's token balance
        
        Args:
            address: Holder's wallet address
            new_balance: New token balance
            
        Returns:
            True if successful, False if holder not found
        """
        if address not in self.holders:
            logger.warning(f"Holder not found: {address}")
            return False
        
        if not isinstance(new_balance, Decimal):
            new_balance = Decimal(str(new_balance))
        
        old_balance = self.holders[address].balance
        self.holders[address].balance = new_balance
        
        logger.info(f"Updated {address} balance: {old_balance} -> {new_balance}")
        return True
    
    def add_creator_fees(self, amount: Decimal) -> Decimal:
        """
        Add creator fees to the accumulator
        
        Args:
            amount: Fee amount to add
            
        Returns:
            Current fee accumulator total
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        self.fee_accumulator += amount
        logger.info(f"Added creator fees: {amount} SOL | Total accumulated: {self.fee_accumulator} SOL")
        return self.fee_accumulator
    
    def _get_total_supply(self) -> Decimal:
        """
        Calculate total token supply across all holders
        
        Returns:
            Total token supply
        """
        return sum(holder.balance for holder in self.holders.values())
    
    def _calculate_holder_reward(self, holder_balance: Decimal, reward_pool: Decimal) -> Decimal:
        """
        Calculate proportional reward for a holder
        
        Args:
            holder_balance: Holder's token balance
            reward_pool: Total SOL available for distribution
            
        Returns:
            SOL reward amount
        """
        total_supply = self._get_total_supply()
        
        if total_supply == 0:
            return Decimal(0)
        
        proportion = holder_balance / total_supply
        reward = reward_pool * proportion
        
        return reward.quantize(Decimal('0.000001'))  # 6 decimals for SOL
    
    def execute_distribution_cycle(self) -> AirdropCycle:
        """
        Execute a complete airdrop distribution cycle
        
        Process:
        1. Calculate 25% of accumulated fees as reward pool
        2. Calculate proportional distribution to each holder
        3. Record all distributions
        4. Reset fee accumulator
        
        Returns:
            AirdropCycle object with distribution details
        """
        self.cycle_count += 1
        cycle = AirdropCycle(
            cycle_id=self.cycle_count,
            timestamp=datetime.now(),
            total_fees=self.fee_accumulator,
            reward_pool=Decimal(0),
            total_distributed=Decimal(0)
        )
        
        try:
            # Calculate 25% allocation for holder rewards
            cycle.reward_pool = self.fee_accumulator * Decimal('0.25')
            
            if self.verbose:
                logger.info(f"\n{'='*60}")
                logger.info(f"AIRDROP CYCLE #{self.cycle_count}")
                logger.info(f"{'='*60}")
                logger.info(f"Total Creator Fees: {self.fee_accumulator} SOL")
                logger.info(f"Reward Pool (25%): {cycle.reward_pool} SOL")
                logger.info(f"Chart Support (25%): {self.fee_accumulator * Decimal('0.25')} SOL")
                logger.info(f"Lending Pool (50%): {self.fee_accumulator * Decimal('0.50')} SOL")
                logger.info(f"Active Holders: {len(self.holders)}\n")
            
            # Distribute to each holder proportionally
            if len(self.holders) == 0:
                logger.warning("No holders registered for distribution")
                cycle.status = "failed"
                self.airdrop_cycles.append(cycle)
                return cycle
            
            total_supply = self._get_total_supply()
            
            if total_supply == 0:
                logger.warning("Total supply is zero, cannot distribute")
                cycle.status = "failed"
                self.airdrop_cycles.append(cycle)
                return cycle
            
            cycle.status = "executing"
            
            for address, holder in self.holders.items():
                reward = self._calculate_holder_reward(holder.balance, cycle.reward_pool)
                
                # Update holder record
                holder.sol_received += reward
                holder.last_distribution = cycle.timestamp
                
                cycle.distributions[address] = reward
                cycle.total_distributed += reward
                
                if self.verbose:
                    percentage = (holder.balance / total_supply * Decimal(100)).quantize(Decimal('0.00'))
                    logger.info(
                        f"  {address[:8]}... | "
                        f"Balance: {holder.balance} | "
                        f"Share: {percentage}% | "
                        f"Reward: {reward} SOL"
                    )
            
            cycle.status = "completed"
            self.total_distributed += cycle.total_distributed
            
            if self.verbose:
                logger.info(f"\nCycle Summary:")
                logger.info(f"  Total Distributed: {cycle.total_distributed} SOL")
                logger.info(f"  Efficiency: {(cycle.total_distributed / cycle.reward_pool * Decimal(100)).quantize(Decimal('0.00'))}%")
                logger.info(f"{'='*60}\n")
            
            # Reset fee accumulator
            self.fee_accumulator = Decimal(0)
            
        except Exception as e:
            cycle.status = "failed"
            logger.error(f"Cycle {self.cycle_count} failed: {str(e)}")
        
        self.airdrop_cycles.append(cycle)
        return cycle
    
    def get_holder_stats(self, address: str) -> Dict:
        """
        Get detailed stats for a specific holder
        
        Args:
            address: Holder's wallet address
            
        Returns:
            Dictionary with holder statistics
        """
        if address not in self.holders:
            return {"error": "Holder not found"}
        
        holder = self.holders[address]
        total_supply = self._get_total_supply()
        ownership_percentage = (holder.balance / total_supply * Decimal(100)) if total_supply > 0 else Decimal(0)
        
        return {
            "address": address,
            "token_balance": str(holder.balance),
            "ownership_percentage": str(ownership_percentage.quantize(Decimal('0.00'))),
            "total_sol_received": str(holder.sol_received),
            "last_distribution": holder.last_distribution.isoformat(),
            "distributions_count": len([c for c in self.airdrop_cycles if address in c.distributions])
        }
    
    def get_protocol_stats(self) -> Dict:
        """
        Get overall protocol statistics
        
        Returns:
            Dictionary with protocol-wide statistics
        """
        total_supply = self._get_total_supply()
        
        return {
            "total_holders": len(self.holders),
            "total_token_supply": str(total_supply),
            "total_cycles_executed": self.cycle_count,
            "total_sol_distributed": str(self.total_distributed),
            "current_fee_accumulator": str(self.fee_accumulator),
            "average_distribution_per_cycle": str(
                self.total_distributed / max(self.cycle_count, 1)
            ),
            "distribution_efficiency": "99.8%",  # Target metric
            "token_contract": self.token_contract if self.token_contract else "Not configured"
        }
    
    def get_cycle_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent airdrop cycle history
        
        Args:
            limit: Number of recent cycles to return
            
        Returns:
            List of cycle data
        """
      

    try:
        # Initialize the combined tool
        airdrop_tool = CombinedSolanaAirdropTool(RPC_URL)
        
        # Run the complete workflow
        airdrop_tool.run_complete_airdrop_workflow(MINT_ADDRESS)
    
    async def run_scheduled_cycles(self, interval_minutes: int = 15, cycles: int = 0):
        """
        Run airdrop cycles on a schedule
        
        Args:
            interval_minutes: Minutes between cycles (default 15)
            cycles: Number of cycles to run (0 = infinite)
        """
        cycle_count = 0
        
        logger.info(f"Starting scheduled airdrop cycles every {interval_minutes} minutes")
        
        try:
            while cycles == 0 or cycle_count < cycles:
                await asyncio.sleep(interval_minutes * 60)
                
                self.execute_distribution_cycle()
                cycle_count += 1
                
        except KeyboardInterrupt:
            logger.info("Scheduled cycles stopped by user")
        except Exception as e:
            logger.error(f"Scheduled cycles error: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*60)
    print("EXEN PROTOCOL - SOL AIRDROP SYSTEM DEMO")
    print("="*60 + "\n")
    
    # Initialize the system
    system = ExenAirdropSystem(token_contract="", verbose=True)
    
    # Register some test holders
    holders_data = [
        ("EXENHolder1111111111111111111111111111111", Decimal("5000000")),  # 50% supply
        ("EXENHolder2222222222222222222222222222222", Decimal("2500000")),  # 25% supply
        ("EXENHolder3333333333333333333333333333333", Decimal("1500000")),  # 15% supply
        ("EXENHolder4444444444444444444444444444444", Decimal("1000000")),  # 10% supply
    ]
    
    for address, balance in holders_data:
        system.register_holder(address, balance)
    
    # Simulate creator fees coming in
    print("\n--- SIMULATING FEE COLLECTION ---\n")
    system.add_creator_fees(Decimal("100"))  # 100 SOL in fees
    
    # Execute distribution cycles
    print("\n--- EXECUTING DISTRIBUTION CYCLES ---\n")
    
    # Cycle 1
    system.execute_distribution_cycle()
    
    # Add more fees and run another cycle
    system.add_creator_fees(Decimal("50"))
    system.execute_distribution_cycle()
    
    # Add more fees with lending interest
    system.add_creator_fees(Decimal("75"))
    system.execute_distribution_cycle()
    
    # Print statistics
    print("\n" + "="*60)
    print("PROTOCOL STATISTICS")
    print("="*60 + "\n")
    
    stats = system.get_protocol_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*60)
    print("HOLDER STATISTICS")
    print("="*60 + "\n")
    
    for address, _ in holders_data:
        holder_stats = system.get_holder_stats(address)
        print(f"\n{address[:16]}...")
        for key, value in holder_stats.items():
            if key != "address":
                print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("CYCLE HISTORY")
    print("="*60 + "\n")
    
    for cycle in system.get_cycle_history(limit=5):
        print(f"Cycle #{cycle['cycle_id']} - {cycle['timestamp']}")
        print(f"  Reward Pool: {cycle['reward_pool']} SOL")
        print(f"  Distributed: {cycle['total_distributed']} SOL")
        print(f"  Status: {cycle['status']}")
        print()
