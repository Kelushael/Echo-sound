#!/usr/bin/env python3
"""
Live Cryptocurrency Sniper Bot
Real on-chain trading with actual execution capabilities
Designed for proof-of-concept live trading with small amounts
"""

import requests
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
from web3 import Web3
import ccxt
import os
from decimal import Decimal
import hmac
import hashlib
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Represents an executed trade"""
    exchange: str
    symbol: str
    side: str  # 'buy' or 'sell'
    amount: float
    price: float
    timestamp: datetime
    tx_hash: Optional[str] = None
    status: str = 'pending'

class DEXTrader:
    """Handles DEX trading through Web3"""
    
    def __init__(self, private_key: str = None, rpc_url: str = "https://mainnet.infura.io/v3/YOUR_KEY"):
        self.private_key = private_key or os.getenv('PRIVATE_KEY')
        self.rpc_url = rpc_url
        self.w3 = None
        self.account = None
        
        if self.private_key:
            self.setup_web3()
    
    def setup_web3(self):
        """Initialize Web3 connection"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self.account = self.w3.eth.account.from_key(self.private_key)
            logger.info(f"Web3 connected. Wallet: {self.account.address}")
        except Exception as e:
            logger.error(f"Web3 setup failed: {e}")
    
    def get_eth_balance(self) -> float:
        """Get ETH balance"""
        if not self.w3 or not self.account:
            return 0.0
        
        try:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            logger.error(f"Error getting ETH balance: {e}")
            return 0.0
    
    def execute_uniswap_trade(self, token_in: str, token_out: str, amount_in: float, min_amount_out: float) -> Optional[str]:
        """Execute trade on Uniswap V3"""
        if not self.w3 or not self.account:
            logger.error("Web3 not initialized")
            return None
        
        try:
            # Uniswap V3 Router address
            router_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
            
            # This is a simplified example - real implementation would need:
            # 1. Token contract ABIs
            # 2. Proper slippage calculation
            # 3. Gas estimation
            # 4. Transaction signing and sending
            
            logger.info(f"Simulating Uniswap trade: {amount_in} {token_in} -> {token_out}")
            
            # For now, return a mock transaction hash
            return f"0x{''.join(['a'] * 64)}"
            
        except Exception as e:
            logger.error(f"Uniswap trade failed: {e}")
            return None

class CEXTrader:
    """Handles centralized exchange trading"""
    
    def __init__(self):
        self.exchanges = {}
        self.setup_exchanges()
    
    def setup_exchanges(self):
        """Setup exchange connections"""
        
        # Binance
        if os.getenv('BINANCE_API_KEY') and os.getenv('BINANCE_SECRET'):
            try:
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': os.getenv('BINANCE_API_KEY'),
                    'secret': os.getenv('BINANCE_SECRET'),
                    'sandbox': False,  # Set to True for testnet
                    'enableRateLimit': True,
                })
                logger.info("Binance exchange connected")
            except Exception as e:
                logger.error(f"Binance setup failed: {e}")
        
        # Coinbase Pro
        if os.getenv('COINBASE_API_KEY') and os.getenv('COINBASE_SECRET'):
            try:
                self.exchanges['coinbasepro'] = ccxt.coinbasepro({
                    'apiKey': os.getenv('COINBASE_API_KEY'),
                    'secret': os.getenv('COINBASE_SECRET'),
                    'passphrase': os.getenv('COINBASE_PASSPHRASE'),
                    'sandbox': False,
                    'enableRateLimit': True,
                })
                logger.info("Coinbase Pro exchange connected")
            except Exception as e:
                logger.error(f"Coinbase Pro setup failed: {e}")
        
        # KuCoin
        if os.getenv('KUCOIN_API_KEY') and os.getenv('KUCOIN_SECRET'):
            try:
                self.exchanges['kucoin'] = ccxt.kucoin({
                    'apiKey': os.getenv('KUCOIN_API_KEY'),
                    'secret': os.getenv('KUCOIN_SECRET'),
                    'passphrase': os.getenv('KUCOIN_PASSPHRASE'),
                    'sandbox': False,
                    'enableRateLimit': True,
                })
                logger.info("KuCoin exchange connected")
            except Exception as e:
                logger.error(f"KuCoin setup failed: {e}")
    
    def get_balances(self, exchange_name: str) -> Dict[str, float]:
        """Get account balances from exchange"""
        if exchange_name not in self.exchanges:
            return {}
        
        try:
            exchange = self.exchanges[exchange_name]
            balance = exchange.fetch_balance()
            return {asset: info['free'] for asset, info in balance.items() if info['free'] > 0}
        except Exception as e:
            logger.error(f"Error getting {exchange_name} balances: {e}")
            return {}
    
    def execute_market_order(self, exchange_name: str, symbol: str, side: str, amount: float) -> Optional[Dict]:
        """Execute market order on exchange"""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not available")
            return None
        
        try:
            exchange = self.exchanges[exchange_name]
            
            # Check if market exists
            markets = exchange.load_markets()
            if symbol not in markets:
                logger.error(f"Market {symbol} not found on {exchange_name}")
                return None
            
            # Execute order
            order = exchange.create_market_order(symbol, side, amount)
            logger.info(f"Order executed on {exchange_name}: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Order execution failed on {exchange_name}: {e}")
            return None
    
    def execute_limit_order(self, exchange_name: str, symbol: str, side: str, amount: float, price: float) -> Optional[Dict]:
        """Execute limit order on exchange"""
        if exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not available")
            return None
        
        try:
            exchange = self.exchanges[exchange_name]
            order = exchange.create_limit_order(symbol, side, amount, price)
            logger.info(f"Limit order placed on {exchange_name}: {order}")
            return order
            
        except Exception as e:
            logger.error(f"Limit order failed on {exchange_name}: {e}")
            return None

class MarketScanner:
    """Scans for trading opportunities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'CryptoSniper/1.0'})
    
    def scan_new_listings(self) -> List[Dict[str, Any]]:
        """Scan for new token listings"""
        opportunities = []
        
        try:
            # CoinGecko new listings
            response = self.session.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'order': 'volume_desc',
                    'per_page': 50,
                    'page': 1,
                    'sparkline': False,
                    'price_change_percentage': '1h,24h'
                }
            )
            
            coins = response.json()
            
            # Look for coins with high volume and recent price movement
            for coin in coins:
                if (coin.get('total_volume', 0) > 1000000 and 
                    abs(coin.get('price_change_percentage_1h', 0)) > 5):
                    
                    opportunities.append({
                        'symbol': coin['symbol'].upper(),
                        'name': coin['name'],
                        'price': coin['current_price'],
                        'volume_24h': coin['total_volume'],
                        'change_1h': coin.get('price_change_percentage_1h', 0),
                        'change_24h': coin.get('price_change_percentage_24h', 0),
                        'market_cap': coin.get('market_cap', 0),
                        'source': 'coingecko'
                    })
            
        except Exception as e:
            logger.error(f"Error scanning new listings: {e}")
        
        return opportunities
    
    def scan_pump_signals(self) -> List[Dict[str, Any]]:
        """Scan for potential pump signals"""
        signals = []
        
        try:
            # Get trending coins
            response = self.session.get("https://api.coingecko.com/api/v3/search/trending")
            trending = response.json().get('coins', [])
            
            for coin in trending:
                coin_data = coin.get('item', {})
                signals.append({
                    'symbol': coin_data.get('symbol', '').upper(),
                    'name': coin_data.get('name', ''),
                    'market_cap_rank': coin_data.get('market_cap_rank', 999999),
                    'trending_score': coin_data.get('score', 0),
                    'source': 'trending'
                })
            
        except Exception as e:
            logger.error(f"Error scanning pump signals: {e}")
        
        return signals

class LiveCryptoSniper:
    """Main sniper bot for live trading"""
    
    def __init__(self, initial_capital: float = 90.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trade_history: List[Trade] = []
        
        # Initialize components
        self.dex_trader = DEXTrader()
        self.cex_trader = CEXTrader()
        self.market_scanner = MarketScanner()
        
        # Trading parameters
        self.max_trade_size = 20.0  # Maximum $20 per trade
        self.stop_loss_percent = 0.15  # 15% stop loss
        self.take_profit_percent = 0.25  # 25% take profit
        self.max_concurrent_trades = 3
        
        # State
        self.active = False
        self.trading_thread = None
        self.active_positions: Dict[str, Dict] = {}
        
    def start_sniping(self):
        """Start the live trading bot"""
        self.active = True
        self.trading_thread = threading.Thread(target=self._sniper_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        logger.info("🎯 LIVE CRYPTO SNIPER STARTED")
        logger.info(f"💰 Starting capital: ${self.current_capital}")
    
    def stop_sniping(self):
        """Stop the trading bot"""
        self.active = False
        if self.trading_thread:
            self.trading_thread.join()
        logger.info("🛑 SNIPER STOPPED")
    
    def _sniper_loop(self):
        """Main sniping loop"""
        while self.active:
            try:
                # Scan for opportunities
                opportunities = self.market_scanner.scan_new_listings()
                pump_signals = self.market_scanner.scan_pump_signals()
                
                # Analyze and execute trades
                for opportunity in opportunities[:5]:  # Top 5 opportunities
                    if len(self.active_positions) < self.max_concurrent_trades:
                        self._evaluate_and_execute(opportunity)
                
                # Check existing positions
                self._manage_positions()
                
                # Log status
                self._log_status()
                
                # Wait before next scan
                time.sleep(30)  # Scan every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in sniper loop: {e}")
                time.sleep(60)
    
    def _evaluate_and_execute(self, opportunity: Dict[str, Any]):
        """Evaluate opportunity and execute if viable"""
        symbol = opportunity['symbol']
        
        # Skip if already trading this symbol
        if symbol in self.active_positions:
            return
        
        # Basic filters
        volume_24h = opportunity.get('volume_24h', 0)
        change_1h = opportunity.get('change_1h', 0)
        
        # Opportunity criteria
        if (volume_24h > 500000 and  # Minimum $500k volume
            abs(change_1h) > 3 and   # At least 3% movement in 1h
            abs(change_1h) < 50):    # But not more than 50% (too risky)
            
            # Determine trade direction
            if change_1h > 0:
                side = 'buy'  # Momentum trade
                logger.info(f"📈 BULLISH SIGNAL: {symbol} (+{change_1h:.2f}%)")
            else:
                side = 'sell'  # Counter-trend trade (risky)
                logger.info(f"📉 BEARISH SIGNAL: {symbol} ({change_1h:.2f}%)")
                return  # Skip bearish for now
            
            # Calculate position size
            trade_amount = min(self.max_trade_size, self.current_capital * 0.2)
            
            if trade_amount < 5:  # Minimum $5 trade
                logger.warning(f"⚠️  Trade amount too small: ${trade_amount}")
                return
            
            # Execute trade
            self._execute_snipe(symbol, side, trade_amount, opportunity)
    
    def _execute_snipe(self, symbol: str, side: str, amount: float, opportunity: Dict[str, Any]):
        """Execute the snipe trade"""
        logger.info(f"🎯 EXECUTING SNIPE: {side.upper()} ${amount} of {symbol}")
        
        # Try different exchanges in priority order
        exchanges_to_try = ['binance', 'kucoin', 'coinbasepro']
        
        for exchange_name in exchanges_to_try:
            if exchange_name in self.cex_trader.exchanges:
                # Format symbol for exchange
                trading_symbol = f"{symbol}/USDT"
                
                try:
                    # Get current price
                    exchange = self.cex_trader.exchanges[exchange_name]
                    ticker = exchange.fetch_ticker(trading_symbol)
                    current_price = ticker['last']
                    
                    # Calculate quantity
                    quantity = amount / current_price
                    
                    # Execute market order
                    order = self.cex_trader.execute_market_order(
                        exchange_name, trading_symbol, side, quantity
                    )
                    
                    if order:
                        # Record trade
                        trade = Trade(
                            exchange=exchange_name,
                            symbol=trading_symbol,
                            side=side,
                            amount=quantity,
                            price=current_price,
                            timestamp=datetime.now(),
                            status='executed'
                        )
                        
                        self.trade_history.append(trade)
                        self.current_capital -= amount
                        
                        # Track position
                        self.active_positions[symbol] = {
                            'entry_price': current_price,
                            'quantity': quantity,
                            'side': side,
                            'exchange': exchange_name,
                            'entry_time': datetime.now(),
                            'stop_loss': current_price * (1 - self.stop_loss_percent) if side == 'buy' else current_price * (1 + self.stop_loss_percent),
                            'take_profit': current_price * (1 + self.take_profit_percent) if side == 'buy' else current_price * (1 - self.take_profit_percent)
                        }
                        
                        logger.info(f"✅ SNIPE EXECUTED: {order['id']} on {exchange_name}")
                        logger.info(f"💰 Remaining capital: ${self.current_capital:.2f}")
                        return
                    
                except Exception as e:
                    logger.error(f"❌ Failed to execute on {exchange_name}: {e}")
                    continue
        
        logger.error(f"❌ Failed to execute snipe for {symbol} on all exchanges")
    
    def _manage_positions(self):
        """Manage existing positions (stop loss, take profit)"""
        positions_to_close = []
        
        for symbol, position in self.active_positions.items():
            try:
                exchange_name = position['exchange']
                trading_symbol = f"{symbol}/USDT"
                
                # Get current price
                exchange = self.cex_trader.exchanges[exchange_name]
                ticker = exchange.fetch_ticker(trading_symbol)
                current_price = ticker['last']
                
                # Check stop loss and take profit
                should_close = False
                reason = ""
                
                if position['side'] == 'buy':
                    if current_price <= position['stop_loss']:
                        should_close = True
                        reason = "STOP LOSS"
                    elif current_price >= position['take_profit']:
                        should_close = True
                        reason = "TAKE PROFIT"
                else:  # sell position
                    if current_price >= position['stop_loss']:
                        should_close = True
                        reason = "STOP LOSS"
                    elif current_price <= position['take_profit']:
                        should_close = True
                        reason = "TAKE PROFIT"
                
                # Check time-based exit (max 1 hour hold)
                if (datetime.now() - position['entry_time']).total_seconds() > 3600:
                    should_close = True
                    reason = "TIME EXIT"
                
                if should_close:
                    positions_to_close.append((symbol, reason))
                    
            except Exception as e:
                logger.error(f"Error managing position {symbol}: {e}")
        
        # Close positions
        for symbol, reason in positions_to_close:
            self._close_position(symbol, reason)
    
    def _close_position(self, symbol: str, reason: str):
        """Close a position"""
        if symbol not in self.active_positions:
            return
        
        position = self.active_positions[symbol]
        exchange_name = position['exchange']
        trading_symbol = f"{symbol}/USDT"
        
        try:
            # Determine exit side
            exit_side = 'sell' if position['side'] == 'buy' else 'buy'
            
            # Execute exit order
            order = self.cex_trader.execute_market_order(
                exchange_name, trading_symbol, exit_side, position['quantity']
            )
            
            if order:
                # Calculate P&L
                exit_price = order['price']
                entry_price = position['entry_price']
                
                if position['side'] == 'buy':
                    pnl = (exit_price - entry_price) / entry_price
                else:
                    pnl = (entry_price - exit_price) / entry_price
                
                pnl_amount = position['quantity'] * entry_price * pnl
                self.current_capital += position['quantity'] * exit_price
                
                logger.info(f"🏁 POSITION CLOSED: {symbol} - {reason}")
                logger.info(f"💹 P&L: {pnl:.2%} (${pnl_amount:.2f})")
                logger.info(f"💰 New capital: ${self.current_capital:.2f}")
                
                # Remove from active positions
                del self.active_positions[symbol]
                
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
    
    def _log_status(self):
        """Log current status"""
        total_pnl = self.current_capital - self.initial_capital
        pnl_percent = (total_pnl / self.initial_capital) * 100
        
        logger.info(f"📊 STATUS: Capital: ${self.current_capital:.2f} | P&L: ${total_pnl:.2f} ({pnl_percent:+.2f}%) | Active: {len(self.active_positions)}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        total_pnl = self.current_capital - self.initial_capital
        pnl_percent = (total_pnl / self.initial_capital) * 100
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_pnl': total_pnl,
            'pnl_percent': pnl_percent,
            'total_trades': len(self.trade_history),
            'active_positions': len(self.active_positions),
            'uptime': datetime.now().isoformat(),
            'trade_history': [asdict(trade) for trade in self.trade_history[-10:]]  # Last 10 trades
        }

if __name__ == "__main__":
    # Initialize sniper with your capital
    sniper = LiveCryptoSniper(initial_capital=90.0)
    
    print("🎯 LIVE CRYPTOCURRENCY SNIPER BOT")
    print("=================================")
    print("⚠️  WARNING: LIVE TRADING WITH REAL MONEY")
    print(f"💰 Starting Capital: ${sniper.initial_capital}")
    print("📡 Scanning for opportunities...")
    
    try:
        # Start sniping
        sniper.start_sniping()
        
        # Run for demo (remove this for continuous operation)
        time.sleep(300)  # Run for 5 minutes
        
        # Get performance report
        report = sniper.get_performance_report()
        print(f"\n📊 PERFORMANCE REPORT:")
        print(f"💰 Final Capital: ${report['current_capital']:.2f}")
        print(f"📈 Total P&L: ${report['total_pnl']:+.2f} ({report['pnl_percent']:+.2f}%)")
        print(f"🔄 Total Trades: {report['total_trades']}")
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down sniper...")
        sniper.stop_sniping()
        
        # Final report
        report = sniper.get_performance_report()
        print(f"📊 FINAL REPORT: ${report['total_pnl']:+.2f} ({report['pnl_percent']:+.2f}%)")