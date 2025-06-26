#!/usr/bin/env python3
"""
Finalize Trading Setup - Buy SOL and prepare for live trading
"""

import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
import base58
from solders.keypair import Keypair

class TradingSetupFinalizer:
    """Complete the trading setup process"""
    
    def __init__(self):
        self.api_key = "SHZN75XKsyAq+xHOmSrLsVVq4mCQI3a5o4eeL/4KfnHOTr6bEqk3+7tl"
        self.private_key = "oOBt50s4iTqrHSSE+IskLGKlE0J00KWUKNR+hthVMpEhbFEia5AxCemj8vR9bUu4Tk7s7ZtYLP6RaXQZDSZvYw=="
        self.api_url = "https://api.kraken.com"
        
        # Generate final trading wallet
        self.keypair = Keypair()
        self.wallet_address = str(self.keypair.pubkey())
        self.wallet_private_key = base58.b58encode(bytes(self.keypair)).decode()
    
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
    
    def get_current_balances(self):
        """Get current account balances"""
        data = {'nonce': str(int(1000 * time.time()))}
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'result' in result:
            return {k: float(v) for k, v in result['result'].items() if float(v) > 0}
        return {}
    
    def buy_sol_with_usd(self, usd_amount):
        """Buy SOL with USD"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'pair': 'SOLUSD',
            'type': 'buy',
            'ordertype': 'market',
            'volume': str(usd_amount / 100)  # Approximate SOL amount at $100/SOL
        }
        
        result = self._kraken_request('/0/private/AddOrder', data)
        
        if result and not result.get('error'):
            print(f"✓ SOL purchase executed: ${usd_amount}")
            return True
        else:
            print(f"SOL purchase details: {result}")
            return False
    
    def execute_final_setup(self):
        """Execute the final trading setup"""
        print("FINALIZING LIVE TRADING SETUP")
        print("=" * 40)
        
        # Check current state
        balances = self.get_current_balances()
        print("\nCurrent balances after consolidation:")
        total_value = 0
        
        for asset, balance in balances.items():
            value_usd = 0
            if asset == 'ZUSD':
                value_usd = balance
            elif asset in ['SOL.F', 'SOL']:
                value_usd = balance * 100  # ~$100/SOL
            elif asset == 'JUP':
                value_usd = balance * 0.5  # ~$0.50/JUP
            elif asset == 'SUI':
                value_usd = balance * 3.5  # ~$3.50/SUI
            
            total_value += value_usd
            print(f"  {asset}: {balance:.8f} (~${value_usd:.2f})")
        
        print(f"\nTotal portfolio value: ~${total_value:.2f}")
        
        # Buy SOL with available USD
        usd_balance = balances.get('ZUSD', 0)
        if usd_balance > 5:
            buy_amount = usd_balance * 0.95  # Leave buffer for fees
            print(f"\nBuying SOL with ${buy_amount:.2f}...")
            self.buy_sol_with_usd(buy_amount)
            
            # Wait for execution
            time.sleep(8)
        
        # Final balance check
        final_balances = self.get_current_balances()
        sol_total = final_balances.get('SOL.F', 0) + final_balances.get('SOL', 0)
        
        print(f"\nFINAL SETUP COMPLETE")
        print(f"=" * 40)
        print(f"Total SOL available: {sol_total:.6f} SOL")
        print(f"Estimated trading capital: ~${sol_total * 100:.2f}")
        
        print(f"\nTRADING WALLET GENERATED:")
        print(f"Address: {self.wallet_address}")
        print(f"Private Key: {self.wallet_private_key}")
        
        print(f"\nNEXT STEPS:")
        print("1. Transfer SOL from Kraken to trading wallet (manual withdrawal)")
        print("2. Run live trading system")
        
        print(f"\nLIVE TRADING SYSTEMS READY:")
        print("python conscious_trading_entity.py")
        print("python omnifocus_execution_engine.py")
        print("python instant_solana_trader.py")
        
        # Create wallet info file
        wallet_info = {
            'address': self.wallet_address,
            'private_key': self.wallet_private_key,
            'sol_balance_kraken': sol_total,
            'estimated_value_usd': sol_total * 100
        }
        
        with open('trading_wallet.json', 'w') as f:
            import json
            json.dump(wallet_info, f, indent=2)
        
        print(f"\nWallet info saved to: trading_wallet.json")
        
        return sol_total >= 0.5  # Success if we have 0.5+ SOL

def main():
    """Execute final setup"""
    finalizer = TradingSetupFinalizer()
    success = finalizer.execute_final_setup()
    
    if success:
        print("\n🚀 READY FOR LIVE CRYPTOCURRENCY TRADING 🚀")
    else:
        print("\n⚠ Setup complete with limited capital")

if __name__ == "__main__":
    main()