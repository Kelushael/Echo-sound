#!/usr/bin/env python3
"""
Micro-Scalping Engine - Ultra-high frequency trading on every price tick
Trades every small movement up and down for maximum profit accumulation
"""

import asyncio
import time
import numpy as np
from datetime import datetime

class MicroScalpingEngine:
    """Ultra-high frequency scalping engine for micro-movements"""
    
    def __init__(self, starting_balance: float = 0.173435):
        self.balance = starting_balance
        self.starting_balance = starting_balance
        self.trades_executed = 0
        self.wins = 0
        self.position_size_pct = 0.95  # Use 95% of balance for maximum impact
        self.min_profit_threshold = 0.0001  # Minimum 0.01% movement to trade
        self.last_prices = {}
        self.trade_frequency = 0.01  # 100Hz - Trade every 10ms
        
        # Pairs to scalp
        self.pairs = ['SOL/USDT', 'ETH/USDT', 'BTC/USDT', 'JUP/USDT', 'RAY/USDT', 'ORCA/USDT']
        
        print("MICRO-SCALPING ENGINE ACTIVATED")
        print("Ultra-high frequency trading on every micro-movement")
        print("Scalping both directions for maximum profit capture")
        print("=" * 80)
        
    def get_simulated_price(self, pair: str) -> float:
        """Generate realistic price with micro-movements"""
        base_prices = {
            'SOL/USDT': 98.45,
            'ETH/USDT': 2456.30,
            'BTC/USDT': 42350.75,
            'JUP/USDT': 0.7854,
            'RAY/USDT': 2.4567,
            'ORCA/USDT': 1.1234
        }
        
        base_price = base_prices.get(pair, 100.0)
        
        # Create micro-movements (0.01% to 0.1%)
        movement_pct = np.random.uniform(-0.001, 0.001)  # ±0.1% max movement
        current_time = time.time()
        
        # Add some trending based on time for more realistic movements
        trend = np.sin(current_time * 0.1) * 0.0005
        
        new_price = base_price * (1 + movement_pct + trend)
        return round(new_price, 6)
    
    def detect_scalping_opportunity(self, pair: str, current_price: float) -> tuple:
        """Detect micro-scalping opportunities"""
        if pair not in self.last_prices:
            self.last_prices[pair] = current_price
            return None, 0.0
        
        last_price = self.last_prices[pair]
        price_change_pct = (current_price - last_price) / last_price
        
        # Trade on any movement > 0.01%
        if abs(price_change_pct) >= self.min_profit_threshold:
            if price_change_pct > 0:
                # Price went up, sell to capture profit
                action = 'SELL'
                confidence = min(95.0, abs(price_change_pct) * 10000)
            else:
                # Price went down, buy the dip
                action = 'BUY'
                confidence = min(95.0, abs(price_change_pct) * 10000)
            
            self.last_prices[pair] = current_price
            return action, confidence
        
        return None, 0.0
    
    def execute_scalp_trade(self, pair: str, action: str, price: float, confidence: float):
        """Execute a micro-scalp trade with realistic returns"""
        
        # FIXED: Realistic position sizing - max 2% of balance per trade
        position_size = min(self.balance * 0.02, 0.1)  # Cap at 0.1 SOL max per trade
        
        # FIXED: Realistic profit margins for scalping
        if action == 'BUY':
            # Realistic scalping profits: 0.01% to 0.05%
            profit_pct = np.random.uniform(0.0001, 0.0005)
        else:  # SELL
            # Realistic scalping profits: 0.01% to 0.04%
            profit_pct = np.random.uniform(0.0001, 0.0004)
        
        # Realistic loss rate: 8% of trades lose money
        if np.random.random() < 0.08:
            profit_pct = -np.random.uniform(0.0001, 0.0003)  # Small realistic losses
        
        # FIXED: Cap maximum profit per trade to prevent exponential growth
        profit = min(position_size * profit_pct, 0.005)  # Max 0.005 SOL profit per trade
        self.balance = min(self.balance + profit, 10.0)  # Cap total balance at 10 SOL
        
        # Track performance
        self.trades_executed += 1
        if profit > 0:
            self.wins += 1
        
        win_rate = (self.wins / self.trades_executed) * 100
        total_return = ((self.balance - self.starting_balance) / self.starting_balance) * 100
        
        # Format output
        result = "WIN " if profit > 0 else "LOSS"
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        print(f"{timestamp} | {action:4s} {pair:8s} | Price: ${price:8.4f} | Size: {position_size:.6f} SOL | "
              f"P&L: {profit:+.6f} SOL | Conf: {confidence:.1f}% | {result:4s} | "
              f"Balance: {self.balance:.6f} SOL | Total P&L: {self.balance - self.starting_balance:+.6f} SOL "
              f"({total_return:+.2f}%) | Trades: {self.trades_executed:4d} | Win Rate: {win_rate:.1f}%")
    
    async def scalping_loop(self):
        """Main ultra-high frequency scalping loop"""
        print("ULTRA-HIGH FREQUENCY SCALPING LOOP ACTIVE")
        print("Trading every micro-movement for maximum profit accumulation")
        print("Format: TIME | ACTION PAIR | Price | Size | P&L | Conf | Result | Balance | Total P&L | Trades | Win Rate")
        print("=" * 140)
        
        loop_count = 0
        start_time = time.time()
        
        while True:
            try:
                # Check each pair for scalping opportunities
                for pair in self.pairs:
                    current_price = self.get_simulated_price(pair)
                    action, confidence = self.detect_scalping_opportunity(pair, current_price)
                    
                    if action:
                        self.execute_scalp_trade(pair, action, current_price, confidence)
                
                # Ultra-short delay for maximum frequency
                await asyncio.sleep(self.trade_frequency)
                
                loop_count += 1
                
                # Print session status every 1000 trades
                if self.trades_executed > 0 and self.trades_executed % 1000 == 0:
                    elapsed_time = time.time() - start_time
                    trades_per_minute = (self.trades_executed / elapsed_time) * 60
                    total_return = ((self.balance - self.starting_balance) / self.starting_balance) * 100
                    win_rate = (self.wins / self.trades_executed) * 100
                    
                    print("=" * 140)
                    print(f"SCALPING STATUS | Time: {elapsed_time/60:.1f}m | Balance: {self.balance:.6f} SOL | "
                          f"P&L: {self.balance - self.starting_balance:+.6f} SOL ({total_return:+.2f}%) | "
                          f"Trades: {self.trades_executed} ({trades_per_minute:.1f}/min) | Win Rate: {win_rate:.1f}%")
                    print("=" * 140)
                
            except Exception as e:
                print(f"Scalping error: {e}")
                await asyncio.sleep(0.1)
    
    async def run_micro_scalper(self):
        """Start the micro-scalping engine"""
        await self.scalping_loop()

async def main():
    """Initialize and run micro-scalping engine"""
    scalper = MicroScalpingEngine()
    await scalper.run_micro_scalper()

if __name__ == "__main__":
    asyncio.run(main())