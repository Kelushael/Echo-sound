#!/usr/bin/env python3
"""
Local LLM-Powered Cryptocurrency Trading Engine
Uses offline language models (Llama, Mistral, etc.) for decision-making
with live market data integration for autonomous trading
"""

import requests
import time
import json
import logging
import subprocess
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import os
import sqlite3
from pathlib import Path
import websocket
import ssl
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalLLMManager:
    """Manages local language models for trading decisions"""
    
    def __init__(self):
        self.available_models = {
            'llama2': {
                'command': 'ollama run llama2',
                'strengths': ['general_reasoning', 'market_analysis'],
                'specialization': 'balanced_trading_decisions'
            },
            'mistral': {
                'command': 'ollama run mistral',
                'strengths': ['technical_analysis', 'risk_assessment'],
                'specialization': 'technical_trading'
            },
            'codellama': {
                'command': 'ollama run codellama',
                'strengths': ['strategy_development', 'backtesting'],
                'specialization': 'algorithmic_trading'
            },
            'neural-chat': {
                'command': 'ollama run neural-chat',
                'strengths': ['sentiment_analysis', 'news_interpretation'],
                'specialization': 'fundamental_analysis'
            },
            'dolphin-mixtral': {
                'command': 'ollama run dolphin-mixtral',
                'strengths': ['complex_reasoning', 'multi_factor_analysis'],
                'specialization': 'comprehensive_trading'
            }
        }
        self.active_models = {}
        self.model_cache = {}
        self.setup_ollama()
    
    def setup_ollama(self):
        """Setup Ollama for local model management"""
        try:
            # Check if Ollama is installed
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Ollama not found. Installing...")
                self.install_ollama()
            
            # Pull required models
            for model_name in ['llama2', 'mistral', 'codellama', 'neural-chat']:
                self.ensure_model_available(model_name)
                
        except Exception as e:
            logger.error(f"Error setting up Ollama: {e}")
    
    def install_ollama(self):
        """Install Ollama if not present"""
        try:
            install_script = """
            curl -fsSL https://ollama.ai/install.sh | sh
            """
            subprocess.run(install_script, shell=True, check=True)
            logger.info("Ollama installed successfully")
        except Exception as e:
            logger.error(f"Failed to install Ollama: {e}")
    
    def ensure_model_available(self, model_name: str):
        """Ensure a specific model is downloaded and available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if model_name not in result.stdout:
                logger.info(f"Downloading {model_name}...")
                subprocess.run(['ollama', 'pull', model_name], check=True)
                logger.info(f"{model_name} downloaded successfully")
        except Exception as e:
            logger.error(f"Error ensuring {model_name} availability: {e}")
    
    def query_model(self, model_name: str, prompt: str, max_tokens: int = 1000) -> str:
        """Query a local language model"""
        try:
            # Prepare the query
            full_command = f'ollama run {model_name} "{prompt}"'
            
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Error querying {model_name}: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout querying {model_name}")
            return ""
        except Exception as e:
            logger.error(f"Error querying {model_name}: {e}")
            return ""
    
    def get_trading_analysis(self, market_data: Dict[str, Any], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Get trading analysis from multiple local models"""
        
        # Prepare market data summary
        market_summary = self.prepare_market_summary(market_data)
        
        analyses = {}
        
        if analysis_type == "comprehensive":
            # Use multiple models for different aspects
            models_to_use = ['mistral', 'llama2', 'neural-chat']
        elif analysis_type == "technical":
            models_to_use = ['mistral', 'codellama']
        elif analysis_type == "fundamental":
            models_to_use = ['neural-chat', 'llama2']
        else:
            models_to_use = ['llama2']
        
        for model in models_to_use:
            if model in self.available_models:
                prompt = self.create_analysis_prompt(market_summary, model)
                response = self.query_model(model, prompt)
                if response:
                    analyses[model] = self.parse_model_response(response, model)
        
        # Synthesize multiple model outputs
        return self.synthesize_analyses(analyses)
    
    def prepare_market_summary(self, market_data: Dict[str, Any]) -> str:
        """Prepare a concise market data summary for LLM analysis"""
        summary = "CRYPTOCURRENCY MARKET DATA:\n\n"
        
        if 'top_coins' in market_data:
            summary += "TOP PERFORMING COINS:\n"
            for coin in market_data['top_coins'][:10]:
                symbol = coin.get('symbol', 'UNKNOWN').upper()
                price = coin.get('current_price', 0)
                change_24h = coin.get('price_change_percentage_24h', 0)
                volume = coin.get('total_volume', 0)
                market_cap = coin.get('market_cap', 0)
                
                summary += f"{symbol}: ${price:.4f} ({change_24h:+.2f}%) Vol: ${volume:,.0f} MCap: ${market_cap:,.0f}\n"
        
        if 'trending' in market_data:
            summary += "\nTRENDING COINS:\n"
            for coin in market_data['trending'][:5]:
                name = coin.get('item', {}).get('name', 'Unknown')
                symbol = coin.get('item', {}).get('symbol', 'UNKNOWN')
                summary += f"{name} ({symbol})\n"
        
        if 'defi' in market_data:
            summary += "\nDEFI SECTOR PERFORMANCE:\n"
            summary += f"Total DeFi TVL trends and major protocol updates\n"
        
        return summary
    
    def create_analysis_prompt(self, market_summary: str, model_name: str) -> str:
        """Create specialized prompts for different models"""
        
        base_context = f"""You are an expert cryptocurrency trading analyst. 
Analyze the following market data and provide actionable trading insights.

{market_summary}

"""
        
        if model_name == 'mistral':
            prompt = base_context + """
Focus on TECHNICAL ANALYSIS:
1. Identify technical patterns and indicators
2. Suggest entry/exit points with specific price levels
3. Recommend stop-loss and take-profit levels
4. Assess market momentum and trend strength
5. Rate confidence level (1-10) for each recommendation

Provide concise, actionable technical trading signals.
"""
        
        elif model_name == 'neural-chat':
            prompt = base_context + """
Focus on FUNDAMENTAL & SENTIMENT ANALYSIS:
1. Analyze market sentiment and news impact
2. Evaluate project fundamentals and adoption
3. Assess macroeconomic factors affecting crypto
4. Identify narrative-driven opportunities
5. Rate market fear/greed levels

Provide strategic insights for medium-term positioning.
"""
        
        elif model_name == 'codellama':
            prompt = base_context + """
Focus on ALGORITHMIC STRATEGY:
1. Identify quantitative trading opportunities
2. Suggest optimal position sizing formulas
3. Recommend risk management parameters
4. Design portfolio allocation strategies
5. Calculate expected returns and risk metrics

Provide mathematical approach to trading decisions.
"""
        
        else:  # llama2 or default
            prompt = base_context + """
Provide COMPREHENSIVE TRADING ANALYSIS:
1. Overall market assessment (bullish/bearish/neutral)
2. Top 3 trading opportunities with reasoning
3. Risk factors to monitor
4. Portfolio allocation suggestions
5. Time horizon recommendations (short/medium/long term)

Balance technical, fundamental, and risk considerations.
"""
        
        return prompt
    
    def parse_model_response(self, response: str, model_name: str) -> Dict[str, Any]:
        """Parse and structure model responses"""
        parsed = {
            'model': model_name,
            'raw_response': response,
            'timestamp': datetime.now(),
            'signals': [],
            'confidence': 0.5,
            'risk_level': 'medium'
        }
        
        # Extract trading signals using keyword matching
        lines = response.lower().split('\n')
        
        for line in lines:
            if any(word in line for word in ['buy', 'long', 'bullish']):
                if any(coin in line for coin in ['btc', 'eth', 'bitcoin', 'ethereum']):
                    parsed['signals'].append({
                        'action': 'BUY',
                        'asset': self.extract_asset_from_line(line),
                        'reasoning': line.strip()
                    })
            
            elif any(word in line for word in ['sell', 'short', 'bearish']):
                if any(coin in line for coin in ['btc', 'eth', 'bitcoin', 'ethereum']):
                    parsed['signals'].append({
                        'action': 'SELL',
                        'asset': self.extract_asset_from_line(line),
                        'reasoning': line.strip()
                    })
            
            # Extract confidence indicators
            if any(word in line for word in ['high confidence', 'strong', 'very likely']):
                parsed['confidence'] = min(parsed['confidence'] + 0.2, 1.0)
            elif any(word in line for word in ['low confidence', 'uncertain', 'risky']):
                parsed['confidence'] = max(parsed['confidence'] - 0.2, 0.1)
        
        return parsed
    
    def extract_asset_from_line(self, line: str) -> str:
        """Extract cryptocurrency asset from text line"""
        common_assets = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'LINK', 'UNI', 'AAVE']
        line_upper = line.upper()
        
        for asset in common_assets:
            if asset in line_upper or asset.lower() in line:
                return asset
        
        return 'UNKNOWN'
    
    def synthesize_analyses(self, analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize multiple model analyses into unified trading decision"""
        if not analyses:
            return {'decision': 'HOLD', 'confidence': 0.5, 'reasoning': 'No analysis available'}
        
        # Aggregate signals
        buy_signals = []
        sell_signals = []
        hold_signals = []
        
        total_confidence = 0
        model_count = 0
        
        for model_name, analysis in analyses.items():
            model_count += 1
            total_confidence += analysis.get('confidence', 0.5)
            
            for signal in analysis.get('signals', []):
                if signal['action'] == 'BUY':
                    buy_signals.append(signal)
                elif signal['action'] == 'SELL':
                    sell_signals.append(signal)
                else:
                    hold_signals.append(signal)
        
        # Determine overall decision
        if len(buy_signals) > len(sell_signals):
            decision = 'BUY'
            primary_signals = buy_signals
        elif len(sell_signals) > len(buy_signals):
            decision = 'SELL'
            primary_signals = sell_signals
        else:
            decision = 'HOLD'
            primary_signals = hold_signals
        
        avg_confidence = total_confidence / model_count if model_count > 0 else 0.5
        
        return {
            'decision': decision,
            'confidence': avg_confidence,
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'hold_signals': len(hold_signals),
            'primary_reasoning': primary_signals,
            'model_consensus': f"{len(analyses)} models analyzed",
            'timestamp': datetime.now(),
            'detailed_analyses': analyses
        }

class OfflineTradingStrategy:
    """Trading strategy that uses local LLMs for decision making"""
    
    def __init__(self):
        self.llm_manager = LocalLLMManager()
        self.strategy_cache = {}
        self.last_analysis_cache = {}
        
    def analyze_market_with_llm(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use local LLMs to analyze market and generate trading strategy"""
        
        # Get comprehensive analysis from multiple models
        analysis = self.llm_manager.get_trading_analysis(market_data, "comprehensive")
        
        # Cache the analysis
        self.last_analysis_cache = analysis
        
        return analysis
    
    def generate_trading_signals(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals using LLM analysis"""
        
        analysis = self.analyze_market_with_llm(market_data)
        signals = []
        
        if analysis['decision'] == 'BUY' and analysis['confidence'] > 0.6:
            for reasoning in analysis.get('primary_reasoning', []):
                asset = reasoning.get('asset', 'BTC')
                signals.append({
                    'pair': f"{asset}/USD",
                    'action': 'BUY',
                    'confidence': analysis['confidence'],
                    'reasoning': reasoning.get('reasoning', 'LLM analysis suggests bullish outlook'),
                    'source': 'local_llm_analysis',
                    'timestamp': datetime.now()
                })
        
        elif analysis['decision'] == 'SELL' and analysis['confidence'] > 0.6:
            for reasoning in analysis.get('primary_reasoning', []):
                asset = reasoning.get('asset', 'BTC')
                signals.append({
                    'pair': f"{asset}/USD",
                    'action': 'SELL',
                    'confidence': analysis['confidence'],
                    'reasoning': reasoning.get('reasoning', 'LLM analysis suggests bearish outlook'),
                    'source': 'local_llm_analysis',
                    'timestamp': datetime.now()
                })
        
        return signals
    
    def get_portfolio_recommendations(self, current_portfolio: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get portfolio recommendations from LLM analysis"""
        
        # Create portfolio context for LLM
        portfolio_prompt = f"""
Current Portfolio: {json.dumps(current_portfolio, indent=2)}
Market Data: Available
        
Provide portfolio optimization recommendations:
1. Asset allocation adjustments
2. Rebalancing suggestions
3. Risk management improvements
4. Diversification opportunities
5. Exit strategies for underperforming assets
        """
        
        recommendations = {}
        for model in ['mistral', 'llama2']:
            response = self.llm_manager.query_model(model, portfolio_prompt)
            if response:
                recommendations[model] = response
        
        return recommendations

class LocalLLMTradingEngine:
    """Complete trading engine powered by local language models"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.strategy = OfflineTradingStrategy()
        self.initial_capital = initial_capital
        self.current_portfolio = {'USD': initial_capital}
        
        # Market data integration (online)
        self.market_data_url = "https://api.coingecko.com/api/v3"
        self.last_market_update = datetime.now()
        
        # Trading state
        self.active = False
        self.trading_thread = None
        self.analysis_interval = 900  # 15 minutes
        
        # Performance tracking
        self.trade_history = []
        self.performance_metrics = {}
        
        # Local database for storing analysis and performance
        self.setup_local_database()
    
    def setup_local_database(self):
        """Setup local SQLite database for storing trading data"""
        self.db_path = "trading_engine.db"
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                pair TEXT,
                action TEXT,
                quantity REAL,
                price REAL,
                confidence REAL,
                reasoning TEXT,
                source TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_analyses (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                models_used TEXT,
                decision TEXT,
                confidence REAL,
                market_data TEXT,
                full_analysis TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_live_market_data(self) -> Dict[str, Any]:
        """Fetch live market data from CoinGecko"""
        try:
            # Get top coins
            response = requests.get(
                f"{self.market_data_url}/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 50,
                    'page': 1,
                    'sparkline': True,
                    'price_change_percentage': '1h,24h,7d'
                }
            )
            top_coins = response.json()
            
            # Get trending coins
            trending_response = requests.get(f"{self.market_data_url}/search/trending")
            trending = trending_response.json().get('coins', [])
            
            return {
                'top_coins': top_coins,
                'trending': trending,
                'timestamp': datetime.now(),
                'data_source': 'coingecko_live'
            }
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {}
    
    def start_trading(self):
        """Start the local LLM trading engine"""
        self.active = True
        self.trading_thread = threading.Thread(target=self._trading_loop)
        self.trading_thread.daemon = True
        self.trading_thread.start()
        logger.info("Local LLM Trading Engine started")
    
    def stop_trading(self):
        """Stop the trading engine"""
        self.active = False
        if self.trading_thread:
            self.trading_thread.join()
        logger.info("Trading engine stopped")
    
    def _trading_loop(self):
        """Main trading loop using local LLMs"""
        while self.active:
            try:
                current_time = datetime.now()
                if (current_time - self.last_market_update).total_seconds() >= self.analysis_interval:
                    self._analyze_and_trade_with_llm()
                    self.last_market_update = current_time
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _analyze_and_trade_with_llm(self):
        """Analyze market using local LLMs and execute trades"""
        logger.info("Starting LLM-powered market analysis...")
        
        # Get live market data
        market_data = self.get_live_market_data()
        if not market_data:
            logger.warning("No market data available, skipping analysis")
            return
        
        # Use local LLMs for analysis
        signals = self.strategy.generate_trading_signals(market_data)
        
        # Store analysis in local database
        self._store_llm_analysis(self.strategy.last_analysis_cache, market_data)
        
        # Execute high-confidence signals
        for signal in signals:
            if signal['confidence'] > 0.7:
                self._execute_llm_trade(signal)
        
        # Get portfolio recommendations
        portfolio_recs = self.strategy.get_portfolio_recommendations(self.current_portfolio, market_data)
        logger.info(f"Portfolio recommendations from LLM: {len(portfolio_recs)} models consulted")
        
        logger.info(f"LLM analysis complete. Generated {len(signals)} signals.")
    
    def _store_llm_analysis(self, analysis: Dict[str, Any], market_data: Dict[str, Any]):
        """Store LLM analysis in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO llm_analyses 
            (timestamp, models_used, decision, confidence, market_data, full_analysis)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            analysis.get('model_consensus', 'unknown'),
            analysis.get('decision', 'HOLD'),
            analysis.get('confidence', 0.5),
            json.dumps(market_data, default=str),
            json.dumps(analysis, default=str)
        ))
        
        conn.commit()
        conn.close()
    
    def _execute_llm_trade(self, signal: Dict[str, Any]):
        """Execute trade based on LLM signal"""
        logger.info(f"Executing LLM-powered trade: {signal['action']} {signal['pair']}")
        logger.info(f"LLM Reasoning: {signal['reasoning']}")
        logger.info(f"Confidence: {signal['confidence']:.2%}")
        
        # Simulate trade execution (replace with real exchange API)
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'pair': signal['pair'],
            'action': signal['action'],
            'confidence': signal['confidence'],
            'reasoning': signal['reasoning'],
            'source': 'local_llm',
            'status': 'executed'
        }
        
        self.trade_history.append(trade_record)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades 
            (timestamp, pair, action, quantity, price, confidence, reasoning, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_record['timestamp'],
            trade_record['pair'],
            trade_record['action'],
            0,  # quantity - would calculate based on position sizing
            0,  # price - would get from market
            trade_record['confidence'],
            trade_record['reasoning'],
            trade_record['source']
        ))
        conn.commit()
        conn.close()
        
        logger.info(f"Trade recorded: {trade_record}")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        return {
            'active': self.active,
            'local_models_available': list(self.strategy.llm_manager.available_models.keys()),
            'last_analysis': self.last_market_update.isoformat(),
            'total_trades': len(self.trade_history),
            'portfolio_value': sum(self.current_portfolio.values()),
            'analysis_source': 'local_llm_offline',
            'market_data_source': 'coingecko_online'
        }
    
    def get_recent_llm_insights(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent LLM trading insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM llm_analyses 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in results:
            insights.append({
                'timestamp': row[1],
                'models_used': row[2],
                'decision': row[3],
                'confidence': row[4],
                'analysis': json.loads(row[6]) if row[6] else {}
            })
        
        return insights

if __name__ == "__main__":
    # Example usage
    engine = LocalLLMTradingEngine(initial_capital=10000.0)
    
    print("Local LLM-Powered Cryptocurrency Trading Engine")
    print("===============================================")
    print("Uses offline language models for decision-making")
    print("with live market data for autonomous trading")
    
    # Start trading
    engine.start_trading()
    
    try:
        # Run for demonstration
        time.sleep(30)
        
        # Get status
        status = engine.get_engine_status()
        print(f"\nEngine Status: {json.dumps(status, indent=2)}")
        
        # Get recent insights
        insights = engine.get_recent_llm_insights(3)
        print(f"\nRecent LLM Insights: {len(insights)} analyses")
        
    except KeyboardInterrupt:
        print("\nShutting down trading engine...")
        engine.stop_trading()