#!/usr/bin/env python3
"""
Dynamic Cryptocurrency Trading Engine
Intelligent trading system with dynamic coin selection, DEX swapping, 
portfolio diversification, and risk management using live CoinGecko data
"""

import requests
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor
import websocket
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingPair:
    """Represents a trading pair with market data"""
    symbol: str
    base_asset: str
    quote_asset: str
    current_price: float
    volume_24h: float
    price_change_24h: float
    market_cap: float
    liquidity_score: float
    volatility: float
    trend_score: float

@dataclass
class PortfolioPosition:
    """Represents a position in the portfolio"""
    asset: str
    quantity: float
    average_price: float
    current_price: float
    unrealized_pnl: float
    allocation_percentage: float
    last_updated: datetime

@dataclass
class TradingSignal:
    """Represents a trading signal"""
    pair: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    target_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timestamp: datetime

class MarketDataProvider:
    """Provides live market data from CoinGecko and other sources"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoTradingEngine/1.0'
        })
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting for API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def get_top_coins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top coins by market cap"""
        self._rate_limit()
        
        try:
            response = self.session.get(
                f"{self.base_url}/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': limit,
                    'page': 1,
                    'sparkline': True,
                    'price_change_percentage': '1h,24h,7d,30d'
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching top coins: {e}")
            return []
    
    def get_coin_data(self, coin_id: str) -> Dict[str, Any]:
        """Get detailed data for a specific coin"""
        self._rate_limit()
        
        try:
            response = self.session.get(
                f"{self.base_url}/coins/{coin_id}",
                params={
                    'localization': False,
                    'tickers': True,
                    'market_data': True,
                    'community_data': False,
                    'developer_data': False,
                    'sparkline': True
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching coin data for {coin_id}: {e}")
            return {}
    
    def get_trending_coins(self) -> List[Dict[str, Any]]:
        """Get trending coins"""
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.base_url}/search/trending")
            response.raise_for_status()
            return response.json().get('coins', [])
        except Exception as e:
            logger.error(f"Error fetching trending coins: {e}")
            return []
    
    def get_defi_protocols(self) -> List[Dict[str, Any]]:
        """Get DeFi protocols for DEX trading opportunities"""
        self._rate_limit()
        
        try:
            response = self.session.get(f"{self.base_url}/coins/categories")
            response.raise_for_status()
            
            # Filter for DeFi categories
            categories = response.json()
            defi_categories = [cat for cat in categories if 'defi' in cat['name'].lower()]
            return defi_categories
        except Exception as e:
            logger.error(f"Error fetching DeFi protocols: {e}")
            return []

class TechnicalAnalyzer:
    """Performs technical analysis on price data"""
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # neutral
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_moving_averages(self, prices: List[float]) -> Dict[str, float]:
        """Calculate various moving averages"""
        if len(prices) < 50:
            return {'sma_20': prices[-1], 'sma_50': prices[-1], 'ema_12': prices[-1], 'ema_26': prices[-1]}
        
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        # EMA calculation
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_12': ema_12,
            'ema_26': ema_26
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1]
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': prices[-1], 'middle': prices[-1], 'lower': prices[-1]}
        
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def calculate_volatility(self, prices: List[float], period: int = 20) -> float:
        """Calculate price volatility"""
        if len(prices) < period:
            return 0.0
        
        returns = np.diff(prices[-period:]) / prices[-period:-1]
        return np.std(returns) * np.sqrt(365)  # Annualized volatility

class TradingStrategy:
    """Implements various trading strategies"""
    
    def __init__(self, risk_tolerance: float = 0.02):
        self.risk_tolerance = risk_tolerance
        self.analyzer = TechnicalAnalyzer()
        
    def momentum_strategy(self, coin_data: Dict[str, Any], technical_data: Dict[str, Any]) -> TradingSignal:
        """Momentum-based trading strategy"""
        current_price = coin_data.get('market_data', {}).get('current_price', {}).get('usd', 0)
        price_change_24h = coin_data.get('market_data', {}).get('price_change_percentage_24h', 0)
        volume = coin_data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
        
        # Generate signal based on momentum
        if price_change_24h > 5 and volume > 1000000:  # Strong upward momentum
            confidence = min(abs(price_change_24h) / 10, 0.9)
            return TradingSignal(
                pair=coin_data.get('symbol', '').upper() + '/USD',
                action='BUY',
                confidence=confidence,
                target_price=current_price * 1.1,
                stop_loss=current_price * 0.95,
                take_profit=current_price * 1.2,
                reasoning=f"Strong momentum: {price_change_24h:.2f}% gain with high volume",
                timestamp=datetime.now()
            )
        elif price_change_24h < -5:  # Strong downward momentum
            confidence = min(abs(price_change_24h) / 10, 0.9)
            return TradingSignal(
                pair=coin_data.get('symbol', '').upper() + '/USD',
                action='SELL',
                confidence=confidence,
                target_price=current_price * 0.9,
                stop_loss=current_price * 1.05,
                take_profit=current_price * 0.8,
                reasoning=f"Strong downward momentum: {price_change_24h:.2f}% decline",
                timestamp=datetime.now()
            )
        else:
            return TradingSignal(
                pair=coin_data.get('symbol', '').upper() + '/USD',
                action='HOLD',
                confidence=0.5,
                target_price=current_price,
                stop_loss=current_price * 0.95,
                take_profit=current_price * 1.05,
                reasoning="Neutral momentum, holding position",
                timestamp=datetime.now()
            )
    
    def mean_reversion_strategy(self, coin_data: Dict[str, Any], technical_data: Dict[str, Any]) -> TradingSignal:
        """Mean reversion trading strategy"""
        current_price = coin_data.get('market_data', {}).get('current_price', {}).get('usd', 0)
        
        # Use Bollinger Bands for mean reversion
        if 'bollinger' in technical_data:
            bb = technical_data['bollinger']
            
            if current_price <= bb['lower']:  # Oversold
                return TradingSignal(
                    pair=coin_data.get('symbol', '').upper() + '/USD',
                    action='BUY',
                    confidence=0.8,
                    target_price=bb['middle'],
                    stop_loss=current_price * 0.95,
                    take_profit=bb['upper'],
                    reasoning="Price below lower Bollinger Band - oversold condition",
                    timestamp=datetime.now()
                )
            elif current_price >= bb['upper']:  # Overbought
                return TradingSignal(
                    pair=coin_data.get('symbol', '').upper() + '/USD',
                    action='SELL',
                    confidence=0.8,
                    target_price=bb['middle'],
                    stop_loss=current_price * 1.05,
                    take_profit=bb['lower'],
                    reasoning="Price above upper Bollinger Band - overbought condition",
                    timestamp=datetime.now()
                )
        
        return TradingSignal(
            pair=coin_data.get('symbol', '').upper() + '/USD',
            action='HOLD',
            confidence=0.5,
            target_price=current_price,
            stop_loss=current_price * 0.95,
            take_profit=current_price * 1.05,
            reasoning="Price within normal range",
            timestamp=datetime.now()
        )

class PortfolioManager:
    """Manages portfolio allocation and diversification"""
    
    def __init__(self, total_capital: float = 10000.0):
        self.total_capital = total_capital
        self.positions: Dict[str, PortfolioPosition] = {}
        self.target_allocations = {
            'BTC': 0.4,   # 40% Bitcoin
            'ETH': 0.3,   # 30% Ethereum
            'DEFI': 0.15, # 15% DeFi tokens
            'ALT': 0.15   # 15% Alternative coins
        }
        self.max_position_size = 0.1  # Max 10% in any single asset
        
    def calculate_portfolio_value(self, market_data: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        total_value = 0.0
        for asset, position in self.positions.items():
            current_price = market_data.get(asset, position.current_price)
            total_value += position.quantity * current_price
        return total_value
    
    def get_portfolio_allocation(self, market_data: Dict[str, float]) -> Dict[str, float]:
        """Get current portfolio allocation percentages"""
        total_value = self.calculate_portfolio_value(market_data)
        if total_value == 0:
            return {}
        
        allocations = {}
        for asset, position in self.positions.items():
            current_price = market_data.get(asset, position.current_price)
            asset_value = position.quantity * current_price
            allocations[asset] = asset_value / total_value
        
        return allocations
    
    def should_rebalance(self, market_data: Dict[str, float]) -> bool:
        """Determine if portfolio needs rebalancing"""
        current_allocations = self.get_portfolio_allocation(market_data)
        
        for asset, target in self.target_allocations.items():
            current = current_allocations.get(asset, 0)
            if abs(current - target) > 0.05:  # 5% threshold
                return True
        
        return False
    
    def generate_rebalancing_orders(self, market_data: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate orders to rebalance portfolio"""
        orders = []
        current_allocations = self.get_portfolio_allocation(market_data)
        total_value = self.calculate_portfolio_value(market_data)
        
        for asset, target_allocation in self.target_allocations.items():
            current_allocation = current_allocations.get(asset, 0)
            difference = target_allocation - current_allocation
            
            if abs(difference) > 0.01:  # 1% minimum difference
                target_value = total_value * target_allocation
                current_value = total_value * current_allocation
                trade_value = target_value - current_value
                
                if trade_value > 0:
                    action = 'BUY'
                    quantity = trade_value / market_data.get(asset, 1)
                else:
                    action = 'SELL'
                    quantity = abs(trade_value) / market_data.get(asset, 1)
                
                orders.append({
                    'asset': asset,
                    'action': action,
                    'quantity': quantity,
                    'reason': 'rebalancing',
                    'target_allocation': target_allocation,
                    'current_allocation': current_allocation
                })
        
        return orders

class RiskManager:
    """Manages trading risk and implements stop-loss mechanisms"""
    
    def __init__(self, max_daily_loss: float = 0.05, max_position_risk: float = 0.02):
        self.max_daily_loss = max_daily_loss  # 5% max daily loss
        self.max_position_risk = max_position_risk  # 2% risk per position
        self.daily_pnl = 0.0
        self.daily_reset_time = datetime.now().date()
        
    def check_daily_loss_limit(self, current_pnl: float) -> bool:
        """Check if daily loss limit is exceeded"""
        today = datetime.now().date()
        if today != self.daily_reset_time:
            self.daily_pnl = 0.0
            self.daily_reset_time = today
        
        self.daily_pnl += current_pnl
        return self.daily_pnl <= -self.max_daily_loss
    
    def calculate_position_size(self, account_balance: float, entry_price: float, stop_loss: float) -> float:
        """Calculate appropriate position size based on risk"""
        risk_amount = account_balance * self.max_position_risk
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return min(position_size, account_balance * 0.1)  # Max 10% of balance
    
    def should_execute_trade(self, signal: TradingSignal, portfolio_value: float) -> bool:
        """Determine if trade should be executed based on risk parameters"""
        # Check confidence threshold
        if signal.confidence < 0.6:
            return False
        
        # Check daily loss limit
        if self.check_daily_loss_limit(0):
            return False
        
        # Check position risk
        risk_per_trade = abs(signal.target_price - signal.stop_loss) / signal.target_price
        if risk_per_trade > self.max_position_risk * 2:  # 4% max risk per trade
            return False
        
        return True

class DynamicTradingEngine:
    """Main trading engine that coordinates all components"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.market_data = MarketDataProvider()
        self.strategy = TradingStrategy()
        self.portfolio = PortfolioManager(initial_capital)
        self.risk_manager = RiskManager()
        self.technical_analyzer = TechnicalAnalyzer()
        
        self.active = False
        self.trading_thread = None
        self.last_analysis_time = datetime.now()
        self.analysis_interval = 300  # 5 minutes
        
        # Trading preferences
        self.preferred_exchanges = ['binance', 'coinbase', 'uniswap', 'sushiswap']
        self.min_liquidity = 1000000  # $1M minimum liquidity
        self.max_slippage = 0.005  # 0.5% max slippage
        
    def start_trading(self):
        """Start the trading engine"""
        self.active = True
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        logger.info("Trading engine started")
    
    def stop_trading(self):
        """Stop the trading engine"""
        self.active = False
        if self.trading_thread:
            self.trading_thread.join()
        logger.info("Trading engine stopped")
    
    def _trading_loop(self):
        """Main trading loop"""
        while self.active:
            try:
                current_time = datetime.now()
                if (current_time - self.last_analysis_time).total_seconds() >= self.analysis_interval:
                    self._analyze_and_trade()
                    self.last_analysis_time = current_time
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _analyze_and_trade(self):
        """Analyze market and execute trades"""
        logger.info("Starting market analysis...")
        
        # Get market data
        top_coins = self.market_data.get_top_coins(50)
        trending_coins = self.market_data.get_trending_coins()
        
        signals = []
        
        # Analyze top coins
        for coin in top_coins[:20]:  # Analyze top 20 coins
            try:
                coin_data = self.market_data.get_coin_data(coin['id'])
                if not coin_data:
                    continue
                
                # Get price history for technical analysis
                sparkline = coin.get('sparkline_in_7d', {}).get('price', [])
                if len(sparkline) < 10:
                    continue
                
                # Calculate technical indicators
                technical_data = {
                    'ma': self.technical_analyzer.calculate_moving_averages(sparkline),
                    'rsi': self.technical_analyzer.calculate_rsi(sparkline),
                    'bollinger': self.technical_analyzer.calculate_bollinger_bands(sparkline),
                    'volatility': self.technical_analyzer.calculate_volatility(sparkline)
                }
                
                # Generate trading signals
                momentum_signal = self.strategy.momentum_strategy(coin_data, technical_data)
                mean_reversion_signal = self.strategy.mean_reversion_strategy(coin_data, technical_data)
                
                # Combine signals (weighted average)
                combined_confidence = (momentum_signal.confidence * 0.6 + 
                                     mean_reversion_signal.confidence * 0.4)
                
                if momentum_signal.action == mean_reversion_signal.action:
                    # Both strategies agree
                    signal = momentum_signal
                    signal.confidence = combined_confidence * 1.2  # Boost confidence
                    signals.append(signal)
                elif combined_confidence > 0.7:
                    # Use the stronger signal
                    stronger_signal = momentum_signal if momentum_signal.confidence > mean_reversion_signal.confidence else mean_reversion_signal
                    signals.append(stronger_signal)
                
            except Exception as e:
                logger.error(f"Error analyzing coin {coin.get('id', 'unknown')}: {e}")
                continue
        
        # Filter and execute top signals
        signals.sort(key=lambda x: x.confidence, reverse=True)
        
        for signal in signals[:5]:  # Execute top 5 signals
            if self.risk_manager.should_execute_trade(signal, self.portfolio.total_capital):
                self._execute_trade(signal)
        
        # Check for rebalancing
        market_prices = {coin['symbol'].upper(): coin['current_price'] for coin in top_coins}
        if self.portfolio.should_rebalance(market_prices):
            rebalancing_orders = self.portfolio.generate_rebalancing_orders(market_prices)
            for order in rebalancing_orders:
                logger.info(f"Rebalancing order: {order}")
                # Execute rebalancing order here
        
        logger.info(f"Analysis complete. Generated {len(signals)} signals.")
    
    def _execute_trade(self, signal: TradingSignal):
        """Execute a trading signal"""
        logger.info(f"Executing trade: {signal.action} {signal.pair} at {signal.target_price:.6f}")
        logger.info(f"Reasoning: {signal.reasoning}")
        logger.info(f"Confidence: {signal.confidence:.2%}")
        
        # Here you would integrate with actual trading APIs
        # For now, we'll simulate the trade
        
        # Calculate position size based on risk
        position_size = self.risk_manager.calculate_position_size(
            self.portfolio.total_capital,
            signal.target_price,
            signal.stop_loss
        )
        
        logger.info(f"Position size: {position_size:.6f}")
        
        # Simulate trade execution
        trade_result = {
            'pair': signal.pair,
            'action': signal.action,
            'size': position_size,
            'price': signal.target_price,
            'timestamp': datetime.now(),
            'status': 'executed'
        }
        
        logger.info(f"Trade executed: {trade_result}")
        return trade_result
    
    def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading engine status"""
        return {
            'active': self.active,
            'last_analysis': self.last_analysis_time.isoformat(),
            'portfolio_value': self.portfolio.total_capital,
            'daily_pnl': self.risk_manager.daily_pnl,
            'positions': len(self.portfolio.positions),
            'risk_level': 'NORMAL' if not self.risk_manager.check_daily_loss_limit(0) else 'HIGH'
        }

if __name__ == "__main__":
    # Example usage
    engine = DynamicTradingEngine(initial_capital=10000.0)
    
    print("Dynamic Cryptocurrency Trading Engine")
    print("====================================")
    
    # Start trading
    engine.start_trading()
    
    try:
        # Run for demonstration
        time.sleep(10)
        
        # Get status
        status = engine.get_trading_status()
        print(f"\nTrading Status: {json.dumps(status, indent=2)}")
        
    except KeyboardInterrupt:
        print("\nShutting down trading engine...")
        engine.stop_trading()