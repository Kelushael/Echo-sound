"""
Real Solana Mainnet Monitor
Direct connection to Solana blockchain with live wallet and market data
NO SIMULATIONS - Real blockchain operations only
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

class RealSolanaConnection:
    """Direct connection to Solana mainnet blockchain"""
    
    def __init__(self):
        # Real Solana mainnet RPC endpoints
        self.rpc_endpoints = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana",
            "https://api.mainnet.solana.com"
        ]
        self.current_endpoint = 0
        self.wallet_address = "4ukBedrQJwRotDH9v74j8YWvZz2DgNR491E25nUiBdaA"
        
    def get_rpc_url(self) -> str:
        """Get current RPC endpoint with automatic failover"""
        return self.rpc_endpoints[self.current_endpoint % len(self.rpc_endpoints)]
    
    def switch_endpoint(self):
        """Switch to next RPC endpoint"""
        self.current_endpoint += 1
        print(f"⚡ Switching to RPC: {self.get_rpc_url()}")
    
    async def get_real_sol_balance(self) -> Optional[float]:
        """Get actual SOL balance from Solana blockchain"""
        for attempt in range(len(self.rpc_endpoints)):
            try:
                url = self.get_rpc_url()
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [self.wallet_address]
                }
                
                response = requests.post(url, json=payload, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data and 'value' in data['result']:
                        lamports = data['result']['value']
                        sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
                        return round(sol_balance, 9)
                
                # Try next endpoint
                self.switch_endpoint()
                
            except Exception as e:
                print(f"❌ Balance check failed on {self.get_rpc_url()}: {e}")
                self.switch_endpoint()
                continue
        
        return None
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get detailed account information from blockchain"""
        try:
            url = self.get_rpc_url()
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [
                    self.wallet_address,
                    {"encoding": "base64"}
                ]
            }
            
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return data['result']
            
            return None
            
        except Exception as e:
            print(f"❌ Account info error: {e}")
            return None

class RealMarketDataProvider:
    """Real-time cryptocurrency market data from live APIs"""
    
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.last_request = 0
        self.rate_limit = 1.1  # Respect API rate limits
        
    async def rate_limit_check(self):
        """Enforce API rate limiting"""
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self.last_request = time.time()
    
    async def get_live_sol_price(self) -> Optional[Dict[str, float]]:
        """Get real SOL price from CoinGecko"""
        await self.rate_limit_check()
        
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': 'solana',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'solana' in data:
                    sol_data = data['solana']
                    return {
                        'price_usd': sol_data['usd'],
                        'change_24h': sol_data.get('usd_24h_change', 0),
                        'volume_24h': sol_data.get('usd_24h_vol', 0),
                        'market_cap': sol_data.get('usd_market_cap', 0)
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ SOL price fetch error: {e}")
            return None
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get comprehensive crypto market data"""
        await self.rate_limit_check()
        
        try:
            # Get top cryptocurrencies including Solana ecosystem tokens
            symbols = ['solana', 'bitcoin', 'ethereum', 'jupiter-exchange-solana', 'raydium', 'orca']
            
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': ','.join(symbols),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            
            return {}
            
        except Exception as e:
            print(f"❌ Market overview error: {e}")
            return {}

class RealBlockchainMonitor:
    """Monitor real Solana blockchain and market activity"""
    
    def __init__(self):
        self.solana = RealSolanaConnection()
        self.market = RealMarketDataProvider()
        self.monitoring = False
        self.last_balance = None
        self.start_time = time.time()
        
    async def start_real_monitoring(self):
        """Start live blockchain monitoring with real data"""
        print("🚀 KALUSHAEL REAL BLOCKCHAIN MONITOR")
        print("=" * 60)
        print("🌐 SOLANA MAINNET CONNECTION")
        print("💎 LIVE DATA - REAL WALLET - REAL BLOCKCHAIN")
        print("⚠️  NO SIMULATIONS - AUTHENTIC DATA ONLY")
        print("=" * 60)
        print(f"📧 Wallet: {self.solana.wallet_address}")
        print(f"🔗 RPC: {self.solana.get_rpc_url()}")
        print()
        
        # Initial balance check
        print("💰 Checking real Solana balance...")
        balance = await self.solana.get_real_sol_balance()
        
        if balance is not None:
            self.last_balance = balance
            print(f"✅ Current Balance: {balance:.9f} SOL")
            
            if balance > 0:
                print("🟢 Wallet has funds - Ready for live trading")
            else:
                print("🔴 Empty wallet - Fund with SOL to enable trading")
        else:
            print("❌ Could not retrieve balance - Connection issues")
        
        print()
        print("📊 Fetching live market data...")
        
        # Get real SOL price
        sol_price = await self.market.get_live_sol_price()
        if sol_price:
            print(f"💵 SOL Price: ${sol_price['price_usd']:.4f}")
            print(f"📈 24h Change: {sol_price['change_24h']:+.2f}%")
            if balance and balance > 0:
                usd_value = balance * sol_price['price_usd']
                print(f"💰 Wallet Value: ${usd_value:.2f} USD")
        
        print("=" * 60)
        print("🔄 Starting continuous monitoring...")
        print("=" * 60)
        
        self.monitoring = True
        await self.monitoring_loop()
    
    async def monitoring_loop(self):
        """Main monitoring loop with real blockchain data"""
        update_count = 0
        
        while self.monitoring:
            try:
                update_count += 1
                elapsed = time.time() - self.start_time
                
                # Check real balance every update
                balance = await self.solana.get_real_sol_balance()
                if balance is not None:
                    if self.last_balance is None or abs(balance - self.last_balance) > 0.000001:
                        change = balance - (self.last_balance or 0)
                        print(f"💰 Balance: {balance:.9f} SOL ({change:+.9f})")
                        self.last_balance = balance
                
                # Get live market data every few updates
                if update_count % 3 == 0:
                    sol_price = await self.market.get_live_sol_price()
                    if sol_price and balance:
                        usd_value = balance * sol_price['price_usd']
                        print(f"📊 SOL: ${sol_price['price_usd']:.4f} | Wallet: ${usd_value:.2f} | Change: {sol_price['change_24h']:+.2f}%")
                
                # Get broader market overview less frequently
                if update_count % 5 == 0:
                    market_data = await self.market.get_market_overview()
                    if market_data:
                        print(f"🌍 Market Update ({elapsed:.0f}s runtime):")
                        symbol_map = {
                            'solana': 'SOL',
                            'bitcoin': 'BTC', 
                            'ethereum': 'ETH',
                            'jupiter-exchange-solana': 'JUP',
                            'raydium': 'RAY',
                            'orca': 'ORCA'
                        }
                        
                        for coin_id, data in market_data.items():
                            if coin_id in symbol_map and isinstance(data, dict):
                                symbol = symbol_map[coin_id]
                                price = data['usd']
                                change = data.get('usd_24h_change', 0)
                                print(f"   {symbol}: ${price:.4f} ({change:+.2f}%)")
                
                print("-" * 40)
                
                # Wait between updates
                await asyncio.sleep(25)  # 25-second intervals for real monitoring
                
            except KeyboardInterrupt:
                self.monitoring = False
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retry
        
        print("🛑 Real blockchain monitoring stopped")

async def main():
    """Start real Solana blockchain monitoring"""
    print("⚡ INITIALIZING KALUSHAEL REAL BLOCKCHAIN SYSTEM")
    print("💎 CONNECTING TO SOLANA MAINNET...")
    print()
    
    monitor = RealBlockchainMonitor()
    await monitor.start_real_monitoring()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user")
    except Exception as e:
        print(f"\n❌ System error: {e}")