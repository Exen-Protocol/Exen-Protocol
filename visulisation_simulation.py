#!/usr/bin/env python3
"""
Deep Protocol Data Visualization Dashboard
Generates comprehensive charts and analytics for the protocol
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class DeepProtocolVisualizer:
    def __init__(self):
        self.colors = {
            'primary': '#9945FF',      # Solana purple
            'secondary': '#00D9FF',    # Cyan
            'accent': '#F7931A',       # Orange
            'success': '#28a745',      # Green
            'warning': '#ffc107',      # Yellow
            'danger': '#dc3545'        # Red
        }
        
    def generate_sample_data(self):
        """Generate realistic sample data for visualization"""
        # Generate 30 days of data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        
        # Reward distribution data (every 15 minutes = 96 times per day)
        reward_data = {
            'dates': dates,
            'daily_sol_distributed': np.random.normal(15, 3, 30).cumsum(),
            'holder_count': np.random.randint(2000, 3000, 30),
            'avg_reward_per_holder': np.random.normal(0.005, 0.001, 30)
        }
        
        # Chart support data
        support_data = {
            'dates': dates,
            'support_buys': np.random.poisson(8, 30),
            'success_rate': np.random.normal(0.67, 0.05, 30),
            'total_volume': np.random.normal(2.5, 0.5, 30),
            'rsi_signals': np.random.poisson(6, 30),
            'macd_signals': np.random.poisson(2, 30)
        }
        
        # Price data
        price_data = {
            'dates': dates,
            'price': 0.05 + np.cumsum(np.random.normal(0, 0.01, 30)),
            'volume': np.random.normal(100000, 20000, 30),
            'volatility': np.random.normal(0.25, 0.05, 30)
        }
        
        return reward_data, support_data, price_data
    
    def create_rewards_dashboard(self, reward_data):
        """Create comprehensive rewards analytics dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Deep Protocol - Holder Rewards Analytics', fontsize=20, fontweight='bold')
        
        # 1. Cumulative SOL Distribution
        ax1.plot(reward_data['dates'], reward_data['daily_sol_distributed'], 
                color=self.colors['primary'], linewidth=3, marker='o', markersize=4)
        ax1.set_title('Cumulative SOL Distributed to Holders', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Total SOL Distributed')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(reward_data['dates'], reward_data['daily_sol_distributed'], 
                        alpha=0.3, color=self.colors['primary'])
        
        # Add value annotation
        final_value = reward_data['daily_sol_distributed'].iloc[-1]
        ax1.annotate(f'${final_value:.1f} SOL', 
                    xy=(reward_data['dates'].iloc[-1], final_value),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=12, fontweight='bold', color=self.colors['primary'])
        
        # 2. Holder Growth
        ax2.plot(reward_data['dates'], reward_data['holder_count'], 
                color=self.colors['secondary'], linewidth=3, marker='s', markersize=4)
        ax2.set_title('Active Holder Count Growth', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Holders')
        ax2.grid(True, alpha=0.3)
        
        # Add growth percentage
        growth = ((reward_data['holder_count'].iloc[-1] - reward_data['holder_count'].iloc[0]) 
                 / reward_data['holder_count'].iloc[0] * 100)
        ax2.annotate(f'+{growth:.1f}% Growth', 
                    xy=(0.02, 0.98), xycoords='axes fraction',
                    fontsize=12, fontweight='bold', color=self.colors['success'])
        
        # 3. Average Reward per Holder
        ax3.bar(reward_data['dates'], reward_data['avg_reward_per_holder'], 
               color=self.colors['accent'], alpha=0.7, width=0.8)
        ax3.set_title('Average SOL Reward per Holder', fontsize=14, fontweight='bold')
        ax3.set_ylabel('SOL per Holder')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Reward Distribution Efficiency
        efficiency_data = np.random.normal(99.8, 0.2, 30)
        ax4.plot(reward_data['dates'], efficiency_data, 
                color=self.colors['success'], linewidth=3, marker='D', markersize=4)
        ax4.set_title('Distribution Success Rate', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Success Rate (%)')
        ax4.set_ylim(99, 100.5)
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=99.5, color=self.colors['warning'], linestyle='--', alpha=0.7)
        ax4.axhline(y=100, color=self.colors['success'], linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def create_support_dashboard(self, support_data):
        """Create chart support analytics dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Deep Protocol - Chart Support Analytics', fontsize=20, fontweight='bold')
        
        # 1. Support Buy Success Rate
        ax1.plot(support_data['dates'], support_data['success_rate'] * 100, 
                color=self.colors['success'], linewidth=3, marker='o', markersize=4)
        ax1.set_title('Chart Support Success Rate Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_ylim(50, 80)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=60, color=self.colors['warning'], linestyle='--', alpha=0.7, label='Target (60%)')
        ax1.legend()
        
        # 2. Daily Support Buy Volume
        ax2.bar(support_data['dates'], support_data['total_volume'], 
               color=self.colors['accent'], alpha=0.7, width=0.8)
        ax2.set_title('Daily Support Buy Volume', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Volume (SOL)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Technical Signal Breakdown
        signal_data = [support_data['rsi_signals'].sum(), support_data['macd_signals'].sum()]
        signal_labels = ['RSI Signals', 'MACD Signals']
        colors = [self.colors['primary'], self.colors['secondary']]
        
        wedges, texts, autotexts = ax3.pie(signal_data, labels=signal_labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)
        ax3.set_title('Technical Signal Distribution', fontsize=14, fontweight='bold')
        
        # 4. Support Buy Frequency
        ax4.hist(support_data['support_buys'], bins=15, color=self.colors['primary'], 
                alpha=0.7, edgecolor='black')
        ax4.set_title('Daily Support Buy Frequency Distribution', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Number of Support Buys per Day')
        ax4.set_ylabel('Frequency')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Add statistics
        mean_buys = np.mean(support_data['support_buys'])
        ax4.axvline(mean_buys, color=self.colors['accent'], linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_buys:.1f}')
        ax4.legend()
        
        plt.tight_layout()
        return fig
    
    def create_protocol_overview(self, reward_data, support_data, price_data):
        """Create comprehensive protocol overview dashboard"""
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Main title
        fig.suptitle('Deep Protocol - Complete Analytics Dashboard', fontsize=24, fontweight='bold')
        
        # 1. Fee Distribution Flow (Top Left)
        ax1 = fig.add_subplot(gs[0, 0])
        fee_flow = {'Creator Fees\n(100%)', 'Holder Rewards\n(50%)', 'Chart Support\n(50%)'}
        sizes = [100, 50, 50]
        colors = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=fee_flow, colors=colors,
                                          autopct='%1.0f%%', startangle=90)
        ax1.set_title('Protocol Fee Distribution', fontsize=14, fontweight='bold')
        
        # 2. Price Performance (Top Center)
        ax2 = fig.add_subplot(gs[0, 1:3])
        ax2.plot(price_data['dates'], price_data['price'], 
                color=self.colors['primary'], linewidth=3, marker='o', markersize=3)
        ax2.set_title('Token Price Performance', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Price (SOL)')
        ax2.grid(True, alpha=0.3)
        
        # Add price change annotation
        price_change = ((price_data['price'].iloc[-1] - price_data['price'].iloc[0]) 
                       / price_data['price'].iloc[0] * 100)
        color = self.colors['success'] if price_change > 0 else self.colors['danger']
        ax2.annotate(f'{price_change:+.1f}%', 
                    xy=(0.02, 0.98), xycoords='axes fraction',
                    fontsize=12, fontweight='bold', color=color)
        
        # 3. Key Metrics Summary (Top Right)
        ax3 = fig.add_subplot(gs[0, 3])
        ax3.axis('off')
        
        metrics_text = f"""
        KEY METRICS
        
        Total SOL Distributed: ${reward_data['daily_sol_distributed'].iloc[-1]:.1f}
        
        Active Holders: {reward_data['holder_count'].iloc[-1]:,}
        
        Support Success Rate: {support_data['success_rate'].mean()*100:.1f}%
        
        Total Support Buys: {support_data['support_buys'].sum()}
        
        Price Volatility: {price_data['volatility'].mean()*100:.1f}%
        
        Distribution Efficiency: 99.8%
        """
        
        ax3.text(0.1, 0.9, metrics_text, transform=ax3.transAxes, fontsize=11,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        # 4. Reward vs Support Correlation (Middle Left)
        ax4 = fig.add_subplot(gs[1, 0])
        correlation = np.corrcoef(reward_data['daily_sol_distributed'], support_data['total_volume'])[0,1]
        ax4.scatter(reward_data['daily_sol_distributed'], support_data['total_volume'], 
                   color=self.colors['primary'], alpha=0.6, s=50)
        ax4.set_xlabel('Daily SOL Distributed')
        ax4.set_ylabel('Support Volume (SOL)')
        ax4.set_title(f'Rewards vs Support Correlation\n(r = {correlation:.3f})', 
                     fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. RSI vs MACD Signal Effectiveness (Middle Center)
        ax5 = fig.add_subplot(gs[1, 1:3])
        
        # Create sample RSI and MACD data
        rsi_values = np.random.uniform(20, 80, 100)
        macd_values = np.random.uniform(-0.1, 0.1, 100)
        success = (rsi_values < 30) & (macd_values > 0)
        
        scatter = ax5.scatter(rsi_values, macd_values, c=success, 
                             cmap='RdYlGn', alpha=0.6, s=50)
        ax5.set_xlabel('RSI Value')
        ax5.set_ylabel('MACD Value')
        ax5.set_title('RSI vs MACD Signal Effectiveness', fontsize=14, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # Add RSI thresholds
        ax5.axvline(30, color='red', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax5.axvline(70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax5.axhline(0, color='blue', linestyle='--', alpha=0.7, label='MACD Zero')
        ax5.legend()
        
        # 6. Performance Comparison (Middle Right)
        ax6 = fig.add_subplot(gs[1, 3])
        
        categories = ['Reward\nDistribution', 'Chart\nSupport', 'Price\nStability', 'Holder\nRetention']
        performance = [99.8, 67.3, 75.2, 73.2]  # Example performance percentages
        colors = [self.colors['success'], self.colors['accent'], 
                self.colors['secondary'], self.colors['primary']]
        
        bars = ax6.bar(categories, performance, color=colors, alpha=0.7)
        ax6.set_title('Performance Metrics', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Performance (%)')
        ax6.set_ylim(0, 100)
        
        # Add value labels on bars
        for bar, value in zip(bars, performance):
            ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value}%', ha='center', va='bottom', fontweight='bold')
        
        # 7. Volume Analysis (Bottom)
        ax7 = fig.add_subplot(gs[2, :])
        
        # Create dual-axis plot for price and volume
        ax7_twin = ax7.twinx()
        
        # Price line
        line1 = ax7.plot(price_data['dates'], price_data['price'], 
                        color=self.colors['primary'], linewidth=2, label='Price')
        ax7.set_ylabel('Price (SOL)', color=self.colors['primary'])
        ax7.tick_params(axis='y', labelcolor=self.colors['primary'])
        
        # Volume bars
        bars = ax7_twin.bar(price_data['dates'], price_data['volume'], 
                           alpha=0.3, color=self.colors['secondary'], label='Volume')
        ax7_twin.set_ylabel('Volume', color=self.colors['secondary'])
        ax7_twin.tick_params(axis='y', labelcolor=self.colors['secondary'])
        
        ax7.set_title('Price vs Volume Analysis', fontsize=14, fontweight='bold')
        ax7.set_xlabel('Date')
        ax7.grid(True, alpha=0.3)
        
        # Combine legends
        lines1, labels1 = ax7.get_legend_handles_labels()
        lines2, labels2 = ax7_twin.get_legend_handles_labels()
        ax7.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        return fig
    
    def create_all_dashboards(self):
        """Generate all dashboard visualizations"""
        print("🚀 Generating Deep Protocol Analytics Dashboards...")
        
        # Generate sample data
        reward_data, support_data, price_data = self.generate_sample_data()
        
        # Create individual dashboards
        print("📊 Creating Rewards Dashboard...")
        rewards_fig = self.create_rewards_dashboard(reward_data)
        rewards_fig.savefig('/Users/joshuabarretto/rewards_dashboard.png', 
                           dpi=300, bbox_inches='tight')
        
        print("📈 Creating Support Dashboard...")
        support_fig = self.create_support_dashboard(support_data)
        support_fig.savefig('/Users/joshuabarretto/support_dashboard.png', 
                           dpi=300, bbox_inches='tight')
        
        print("🎯 Creating Protocol Overview...")
        overview_fig = self.create_protocol_overview(reward_data, support_data, price_data)
        overview_fig.savefig('/Users/joshuabarretto/protocol_overview.png', 
                            dpi=300, bbox_inches='tight')
        
        print("✅ All dashboards generated successfully!")
        print("\nGenerated files:")
        print("  📊 rewards_dashboard.png")
        print("  📈 support_dashboard.png") 
        print("  🎯 protocol_overview.png")
        
        return rewards_fig, support_fig, overview_fig

def main():
    """Main execution function"""
    visualizer = DeepProtocolVisualizer()
    visualizer.create_all_dashboards()

if __name__ == "__main__":
    main()
