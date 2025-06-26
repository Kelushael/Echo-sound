#!/usr/bin/env python3
"""
Check available Kraken trading pairs and execute proper consolidation
"""

import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
from solders.keypair import Keypair

class KrakenTradingManager:
    """Manage Kraken trading with proper pair validation"""
    
    def __init__(self):
        self.api_key = os.environ.get('KRAKEN_API_KEY')
        self.private_key = os.environ.get('KRAKEN_PRIVATE_KEY')
        self.api_url = "https://api.kraken.com"
        
        # Generate trading wallet
        self.solana_keypair = Keypair()
        self.solana_address = str(self.solana_keypair.pubkey())
        
        print(f"Generated Trading Wallet: {self.solana_address}")
        
        # Set credentials
        os.environ['KRAKEN_API_KEY'] = "SHZN75XKsyAq+xHOmSrLsVVq4mCQI3a5o4eeL/4KfnHOTr6bEqk3+7tl"
        os.environ['KRAKEN_PRIVATE_KEY'] = "oOBt50s4iTqrHSSE+IskLGKlE0J00KWUKNR+hthVMpEhbFEia5AxCemj8vR9bUu4Tk7s7ZtYLP6RaXQZDSZvYw=="
    
    def _get_kraken_signature(self, urlpath, data, secret):
        """Generate Kraken API signature"""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()
    
    def _kraken_request(self, uri_path, data):
        """Make authenticated request to Kraken API"""
        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._get_kraken_signature(uri_path, data, self.private_key)
        }
        
        response = requests.post(self.api_url + uri_path, headers=headers, data=data, timeout=10)
        return response.json()
    
    def get_trading_pairs(self):
        """Get all available trading pairs"""
        response = requests.get(f"{self.api_url}/0/public/AssetPairs", timeout=10)
        return response.json()
    
    def get_balances(self):
        """Get current balances"""
        data = {'nonce': str(int(1000 * time.time()))}
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'result' in result:
            return {k: float(v) for k, v in result['result'].items() if float(v) > 0}
        return {}
    
    def find_best_trading_pairs(self, balances):
        """Find the best trading pairs for consolidation"""
        pairs_data = self.get_trading_pairs()
        available_pairs = pairs_data.get('result', {})
        
        # Assets we want to convert
        target_assets = ['JUP', 'SUI', 'ETH.F']
        conversion_pairs = {}
        
        print("Finding available trading pairs...")
        
        for asset in target_assets:
            if asset in balances and balances[asset] > 0:
                # Look for USD pairs first, then SOL pairs
                for pair_name, pair_info in available_pairs.items():
                    base = pair_info.get('base', '')
                    quote = pair_info.get('quote', '')
                    
                    # Check if this asset can be sold for USD
                    if (base == asset or base == asset.replace('.F', '')) and quote in ['ZUSD', 'USD']:
                        conversion_pairs[asset] = {
                            'pair': pair_name,
                            'base': base,
                            'quote': quote,
                            'balance': balances[asset]
                        }
                        print(f"Found: {asset} -> {pair_name} (sell for {quote})")
                        break
        
        return conversion_pairs
    
    def execute_sell_order(self, pair, volume):
        """Execute market sell order"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'pair': pair,
            'type': 'sell',
            'ordertype': 'market',
            'volume': str(volume * 0.99)  # Leave buffer for fees
        }
        
        result = self._kraken_request('/0/private/AddOrder', data)
        
        if result and not result.get('error'):
            print(f"✓ Sell order executed: {volume} {pair}")
            return True
        else:
            print(f"✗ Sell failed: {result.get('error', 'Unknown error')}")
            return False
    
    def buy_sol_with_usd(self, usd_amount):
        """Buy SOL with USD"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'pair': 'SOLUSD',
            'type': 'buy',
            'ordertype': 'market',
            'quoteOrderQty': str(usd_amount)  # Spend specific USD amount
        }
        
        result = self._kraken_request('/0/private/AddOrder', data)
        
        if result and not result.get('error'):
            print(f"✓ SOL buy order executed: ${usd_amount}")
            return True
        else:
            print(f"✗ SOL buy failed: {result.get('error', 'Unknown error')}")
            return False
    
    def execute_consolidation_strategy(self):
        """Execute smart consolidation strategy"""
        print("SMART ASSET CONSOLIDATION STRATEGY")
        print("=" * 50)
        
        # Get current balances
        balances = self.get_balances()
        print("\nCurrent balances:")
        for asset, balance in balances.items():
            print(f"  {asset}: {balance:.8f}")
        
        # Find available trading pairs
        conversion_pairs = self.find_best_trading_pairs(balances)
        
        if not conversion_pairs:
            print("No suitable trading pairs found for consolidation")
            return False
        
        total_usd_value = 0
        
        # Convert crypto assets to USD
        for asset, pair_info in conversion_pairs.items():
            balance = pair_info['balance']
            pair = pair_info['pair']
            
            print(f"\nConverting {balance:.6f} {asset} to USD...")
            if self.execute_sell_order(pair, balance):
                # Estimate USD value (rough calculation)
                if asset == 'JUP':
                    total_usd_value += balance * 0.8  # ~$0.80 per JUP
                elif asset == 'SUI':
                    total_usd_value += balance * 1.0  # ~$1.00 per SUI
                elif asset == 'ETH.F':
                    total_usd_value += balance * 2500  # ~$2500 per ETH
            
            time.sleep(2)  # Rate limiting
        
        # Wait for orders to execute
        print("\nWaiting for sell orders to execute...")
        time.sleep(10)
        
        # Buy SOL with accumulated USD
        updated_balances = self.get_balances()
        usd_balance = updated_balances.get('ZUSD', 0)
        
        if usd_balance > 5:  # Minimum for SOL purchase
            print(f"\nBuying SOL with ${usd_balance:.2f} USD...")
            self.buy_sol_with_usd(usd_balance * 0.95)  # Leave buffer
            time.sleep(5)
        
        # Final balance check
        final_balances = self.get_balances()
        sol_balance = final_balances.get('SOL.F', 0) + final_balances.get('SOL', 0)
        
        print(f"\nCONSOLIDATION COMPLETE")
        print(f"Final SOL balance: {sol_balance:.6f} SOL")
        print(f"Estimated value: ~${sol_balance * 100:.2f}")
        
        if sol_balance >= 0.05:
            print(f"\n✓ Ready for live trading")
            print(f"Trading wallet: {self.solana_address}")
            print("\nStart trading with:")
            print("  python conscious_trading_entity.py")
            return True
        else:
            print(f"\n⚠ Low SOL balance for optimal trading")
            print("Consider additional funding or manual trading")
            return False

def main():
    """Execute trading management"""
    manager = KrakenTradingManager()
    manager.execute_consolidation_strategy()

if __name__ == "__main__":
    main()