"""
Live Blockchain Connection System
Direct connection to Solana mainnet with real wallet operations
NO SIMULATIONS - Real blockchain data and transactions
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

class LiveBlockchainWallet:
    """Real Solana mainnet wallet connection"""
    
    def __init__(self):
        # Solana mainnet RPC endpoints
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
        self.current_endpoint = 0
        self.wallet_address = "4ukBedrQJwRotDH9v74j8YWvZz2DgNR491E25nUiBdaA"
        
    def get_rpc_url(self) -> str:
        """Get current RPC endpoint with failover"""
        return self.rpc_endpoints[self.current_endpoint % len(self.rpc_endpoints)]
    
    async def get_real_balance(self) -> Optional[float]:
        """Get actual SOL balance from Solana mainnet"""
        try:
            url = self.get_rpc_url()
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [self.wallet_address]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    lamports = data['result']['value']
                    sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
                    return sol_balance
            
            return None
            
        except Exception as e:
            print(f"Balance check error: {e}")
            # Try next endpoint
            self.current_endpoint += 1
            return None
    
    async def get_transaction_history(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get real transaction history from blockchain"""
        try:
            url = self.get_rpc_url()
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    self.wallet_address,
                    {"limit": limit}
                ]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return data['result']
            
            return None
            
        except Exception as e:
            print(f"Transaction history error: {e}")
            return None

class LiveMarketDataFeed:
    """Real-time market data from live sources"""
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.last_request_time = 0
        self.rate_limit_delay = 1.2  # Respect API rate limits
        
    async def rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    async def get_live_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get real market price from CoinGecko API"""
        await self.rate_limit()
        
        try:
            # Map symbols to CoinGecko IDs
            symbol_map = {
                'SOL': 'solana',
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'JUP': 'jupiter-exchange-solana',
                'RAY': 'raydium',
                'ORCA': 'orca'
            }
            
            coin_id = symbol_map.get(symbol.upper())
            if not coin_id:
                return None
            
            url = f"{self.coingecko_api}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    return {
                        'price': data[coin_id]['usd'],
                        'change_24h': data[coin_id].get('usd_24h_change', 0),
                        'volume_24h': data[coin_id].get('usd_24h_vol', 0)
                    }
            
            return None
            
        except Exception as e:
            print(f"Price fetch error for {symbol}: {e}")
            return None
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive market data"""
        symbols = ['SOL', 'BTC', 'ETH', 'JUP', 'RAY', 'ORCA']
        market_data = {}
        
        for symbol in symbols:
            price_data = await self.get_live_price(symbol)
            if price_data:
                market_data[symbol] = price_data
        
        return market_data

class LiveBlockchainMonitor:
    """Monitor real blockchain activity and wallet state"""
    
    def __init__(self):
        self.wallet = LiveBlockchainWallet()
        self.market_feed = LiveMarketDataFeed()
        self.monitoring = False
        self.last_balance = None
        self.start_time = time.time()
        
    async def start_monitoring(self):
        """Start real-time blockchain monitoring"""
        print("🌐 STARTING LIVE BLOCKCHAIN MONITORING")
        print("=" * 60)
        print(f"📧 Wallet Address: {self.wallet.wallet_address}")
        print("⚡ Connected to Solana Mainnet")
        print("💰 Checking real balance...")
        
        # Initial balance check
        balance = await self.wallet.get_real_balance()
        if balance is not None:
            self.last_balance = balance
            print(f"💰 Current Balance: {balance:.9f} SOL")
            
            if balance > 0:
                print("✅ Wallet has funds - Ready for trading")
            else:
                print("⚠️  Wallet is empty - Send SOL to enable trading")
        else:
            print("❌ Could not retrieve balance - RPC connection issue")
        
        print("=" * 60)
        
        self.monitoring = True
        await self.monitoring_loop()
    
    async def monitoring_loop(self):
        """Main monitoring loop for real blockchain data"""
        while self.monitoring:
            try:
                # Check real balance every 30 seconds
                balance = await self.wallet.get_real_balance()
                if balance is not None and balance != self.last_balance:
                    change = balance - (self.last_balance or 0)
                    print(f"💰 Balance Update: {balance:.9f} SOL ({change:+.9f})")
                    self.last_balance = balance
                
                # Get real market data
                market_data = await self.market_feed.get_market_overview()
                if market_data:
                    elapsed = time.time() - self.start_time
                    print(f"📊 Market Update ({elapsed:.0f}s runtime):")
                    
                    for symbol, data in market_data.items():
                        if isinstance(data, dict):
                            price = data['price']
                            change = data.get('change_24h', 0)
                            print(f"   {symbol}: ${price:.4f} ({change:+.2f}%)")
                
                # Check for real transactions
                tx_history = await self.wallet.get_transaction_history(5)
                if tx_history:
                    print(f"📝 Recent Transactions: {len(tx_history)} found")
                
                print("-" * 40)
                
                # Wait before next update
                await asyncio.sleep(30)  # 30-second intervals for real monitoring
                
            except KeyboardInterrupt:
                self.monitoring = False
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retry
        
        print("🛑 Blockchain monitoring stopped")

async def main():
    """Start live blockchain monitoring"""
    print("🚀 KALUSHAEL LIVE BLOCKCHAIN SYSTEM")
    print("💎 REAL SOLANA MAINNET CONNECTION")
    print("⚠️  LIVE DATA - REAL WALLET - REAL BLOCKCHAIN")
    print()
    
    monitor = LiveBlockchainMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())