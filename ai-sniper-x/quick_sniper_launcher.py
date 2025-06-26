#!/usr/bin/env python3
"""
Quick Live Trading Launcher
Simplified setup for immediate live trading with real exchanges
"""

import os
import ccxt
import requests
import time
import json
from datetime import datetime
import threading

class QuickSniper:
    """Simplified live trading sniper for immediate execution"""
    
    def __init__(self, api_key: str, secret: str, exchange: str = 'binance', capital: float = 90.0):
        self.capital = capital
        self.remaining_capital = capital
        self.exchange_name = exchange
        self.trades = []
        
        # Setup exchange
        if exchange == 'binance':
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret,
                'sandbox': False,
                'enableRateLimit': True,
            })
        elif exchange == 'kucoin':
            # For KuCoin, you need passphrase too
            passphrase = os.getenv('KUCOIN_PASSPHRASE', '')
            self.exchange = ccxt.kucoin({
                'apiKey': api_key,
                'secret': secret,
                'passphrase': passphrase,
                'sandbox': False,
                'enableRateLimit': True,
            })
        else:
            raise ValueError(f"Exchange {exchange} not supported in quick launcher")
        
        # Trading parameters
        self.max_trade_amount = 15.0  # $15 max per trade
        self.stop_loss = 0.12  # 12% stop loss
        self.take_profit = 0.20  # 20% take profit
        self.active_positions = {}
        
        print(f"Quick Sniper initialized with ${capital} on {exchange.upper()}")
        
    def get_balance(self) -> dict:
        """Get current balances"""
        try:
            balance = self.exchange.fetch_balance()
            return {
                'USDT': balance.get('USDT', {}).get('free', 0),
                'BTC': balance.get('BTC', {}).get('free', 0),
                'ETH': balance.get('ETH', {}).get('free', 0),
                'total_usd': balance.get('total', {}).get('USDT', 0)
            }
        except Exception as e:
            print(f"Error getting balance: {e}")
            return {}
    
    def scan_opportunities(self) -> list:
        """Scan for trading opportunities"""
        try:
            # Get trending coins from CoinGecko
            response = requests.get('https://api.coingecko.com/api/v3/search/trending')
            trending = response.json().get('coins', [])
            
            opportunities = []
            for coin in trending[:10]:  # Top 10 trending
                symbol = coin['item']['symbol'].upper()
                name = coin['item']['name']
                
                # Check if trading pair exists on exchange
                trading_pair = f"{symbol}/USDT"
                try:
                    ticker = self.exchange.fetch_ticker(trading_pair)
                    
                    # Basic filters
                    if ticker['quoteVolume'] > 100000:  # $100k+ volume
                        opportunities.append({
                            'symbol': trading_pair,
                            'name': name,
                            'price': ticker['last'],
                            'volume': ticker['quoteVolume'],
                            'change': ticker['percentage']
                        })
                except:
                    continue  # Skip if pair doesn't exist
            
            return opportunities
            
        except Exception as e:
            print(f"Error scanning opportunities: {e}")
            return []
    
    def execute_buy(self, symbol: str, amount_usd: float) -> bool:
        """Execute buy order"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            quantity = amount_usd / price
            
            # Execute market buy
            order = self.exchange.create_market_buy_order(symbol, quantity)
            
            if order:
                self.active_positions[symbol] = {
                    'entry_price': price,
                    'quantity': quantity,
                    'entry_time': datetime.now(),
                    'stop_loss_price': price * (1 - self.stop_loss),
                    'take_profit_price': price * (1 + self.take_profit)
                }
                
                self.trades.append({
                    'action': 'BUY',
                    'symbol': symbol,
                    'price': price,
                    'quantity': quantity,
                    'time': datetime.now().isoformat(),
                    'order_id': order['id']
                })
                
                self.remaining_capital -= amount_usd
                print(f"BOUGHT {quantity:.6f} {symbol} at ${price:.4f}")
                return True
                
        except Exception as e:
            print(f"Buy order failed for {symbol}: {e}")
            return False
    
    def execute_sell(self, symbol: str) -> bool:
        """Execute sell order for position"""
        if symbol not in self.active_positions:
            return False
        
        try:
            position = self.active_positions[symbol]
            quantity = position['quantity']
            
            # Execute market sell
            order = self.exchange.create_market_sell_order(symbol, quantity)
            
            if order:
                sell_price = order['price']
                entry_price = position['entry_price']
                pnl = ((sell_price - entry_price) / entry_price) * 100
                
                self.trades.append({
                    'action': 'SELL',
                    'symbol': symbol,
                    'price': sell_price,
                    'quantity': quantity,
                    'time': datetime.now().isoformat(),
                    'pnl_percent': pnl,
                    'order_id': order['id']
                })
                
                self.remaining_capital += quantity * sell_price
                del self.active_positions[symbol]
                
                print(f"SOLD {quantity:.6f} {symbol} at ${sell_price:.4f} | P&L: {pnl:+.2f}%")
                return True
                
        except Exception as e:
            print(f"Sell order failed for {symbol}: {e}")
            return False
    
    def monitor_positions(self):
        """Monitor active positions for stop loss/take profit"""
        positions_to_close = []
        
        for symbol, position in self.active_positions.items():
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Check stop loss
                if current_price <= position['stop_loss_price']:
                    positions_to_close.append((symbol, 'STOP_LOSS'))
                    print(f"STOP LOSS triggered for {symbol}")
                
                # Check take profit
                elif current_price >= position['take_profit_price']:
                    positions_to_close.append((symbol, 'TAKE_PROFIT'))
                    print(f"TAKE PROFIT triggered for {symbol}")
                
                # Check time limit (30 minutes max)
                elif (datetime.now() - position['entry_time']).total_seconds() > 1800:
                    positions_to_close.append((symbol, 'TIME_LIMIT'))
                    print(f"TIME LIMIT reached for {symbol}")
                    
            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")
        
        # Close positions
        for symbol, reason in positions_to_close:
            self.execute_sell(symbol)
    
    def start_live_trading(self, duration_minutes: int = 60):
        """Start live trading for specified duration"""
        print(f"STARTING LIVE TRADING FOR {duration_minutes} MINUTES")
        print("=" * 50)
        
        start_time = datetime.now()
        end_time = start_time.replace(minute=start_time.minute + duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Monitor existing positions
                self.monitor_positions()
                
                # Look for new opportunities if we have capital and open slots
                if (self.remaining_capital > self.max_trade_amount and 
                    len(self.active_positions) < 3):
                    
                    opportunities = self.scan_opportunities()
                    
                    # Execute on best opportunity
                    if opportunities:
                        best_opp = opportunities[0]  # First trending coin
                        symbol = best_opp['symbol']
                        
                        # Don't trade if already have position
                        if symbol not in self.active_positions:
                            print(f"OPPORTUNITY: {symbol} | Vol: ${best_opp['volume']:,.0f}")
                            self.execute_buy(symbol, self.max_trade_amount)
                
                # Status update
                total_pnl = self.remaining_capital - self.capital
                print(f"STATUS | Capital: ${self.remaining_capital:.2f} | P&L: ${total_pnl:+.2f} | Positions: {len(self.active_positions)}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("Manual stop requested")
                break
            except Exception as e:
                print(f"Trading loop error: {e}")
                time.sleep(60)
        
        # Close all remaining positions
        print("CLOSING ALL POSITIONS...")
        for symbol in list(self.active_positions.keys()):
            self.execute_sell(symbol)
        
        # Final report
        final_pnl = self.remaining_capital - self.capital
        final_pnl_percent = (final_pnl / self.capital) * 100
        
        print("\n" + "=" * 50)
        print("LIVE TRADING SESSION COMPLETE")
        print(f"Starting Capital: ${self.capital:.2f}")
        print(f"Ending Capital: ${self.remaining_capital:.2f}")
        print(f"Total P&L: ${final_pnl:+.2f} ({final_pnl_percent:+.2f}%)")
        print(f"Total Trades: {len(self.trades)}")
        print("=" * 50)

def quick_start():
    """Quick start function for immediate trading"""
    print("LIVE CRYPTO SNIPER - QUICK START")
    print("=" * 40)
    
    # Get credentials from environment or user input
    api_key = os.getenv('BINANCE_API_KEY')
    secret = os.getenv('BINANCE_SECRET')
    
    if not api_key or not secret:
        print("ERROR: Missing exchange credentials")
        print("Set BINANCE_API_KEY and BINANCE_SECRET environment variables")
        print("OR edit this script to hardcode your credentials")
        return
    
    # Initialize sniper
    sniper = QuickSniper(
        api_key=api_key,
        secret=secret,
        exchange='binance',
        capital=90.0
    )
    
    # Check balance
    balance = sniper.get_balance()
    print(f"Current USDT Balance: ${balance.get('USDT', 0):.2f}")
    
    if balance.get('USDT', 0) < 20:
        print("WARNING: Low USDT balance for trading")
        print("Consider depositing more USDT to your exchange account")
    
    # Start trading
    sniper.start_live_trading(duration_minutes=30)  # 30 minute session

if __name__ == "__main__":
    quick_start()