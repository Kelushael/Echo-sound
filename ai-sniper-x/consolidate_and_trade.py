#!/usr/bin/env python3
"""
Consolidate Kraken Assets and Start Live Trading
Convert JUP and SUI to SOL, then start automated trading
"""

import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
import asyncio
from solders.keypair import Keypair

class KrakenConsolidator:
    """Consolidate crypto assets and prepare for Solana trading"""
    
    def __init__(self):
        self.api_key = os.environ.get('KRAKEN_API_KEY')
        self.private_key = os.environ.get('KRAKEN_PRIVATE_KEY')
        self.api_url = "https://api.kraken.com"
        
        # Generate Solana trading wallet
        self.solana_keypair = Keypair()
        self.solana_address = str(self.solana_keypair.pubkey())
        
        print(f"TRADING WALLET: {self.solana_address}")
    
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
    
    def get_balances(self):
        """Get current balances"""
        data = {'nonce': str(int(1000 * time.time()))}
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'result' in result:
            return {k: float(v) for k, v in result['result'].items() if float(v) > 0}
        return {}
    
    def place_market_sell_order(self, pair, volume):
        """Place market sell order"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'pair': pair,
            'type': 'sell',
            'ordertype': 'market',
            'volume': str(volume)
        }
        
        result = self._kraken_request('/0/private/AddOrder', data)
        
        if result and not result.get('error'):
            print(f"✓ Sell order placed: {volume} {pair}")
            return True
        else:
            print(f"✗ Sell order failed: {result.get('error', 'Unknown error')}")
            return False
    
    def consolidate_to_sol(self):
        """Convert JUP and SUI to SOL"""
        print("CONSOLIDATING ASSETS TO SOL")
        print("=" * 40)
        
        balances = self.get_balances()
        
        # Sell JUP for SOL
        jup_balance = balances.get('JUP', 0)
        if jup_balance > 1:  # Minimum trade size
            print(f"Converting {jup_balance:.2f} JUP to SOL...")
            self.place_market_sell_order('JUPSOL', jup_balance * 0.99)  # Leave buffer for fees
            time.sleep(3)
        
        # Sell SUI for SOL  
        sui_balance = balances.get('SUI', 0)
        if sui_balance > 1:
            print(f"Converting {sui_balance:.2f} SUI to SOL...")
            self.place_market_sell_order('SUISOL', sui_balance * 0.99)  # Leave buffer for fees
            time.sleep(3)
        
        # Wait for orders to execute
        print("Waiting for orders to execute...")
        time.sleep(10)
        
        # Check new SOL balance
        updated_balances = self.get_balances()
        sol_balance = updated_balances.get('SOL.F', 0) + updated_balances.get('SOL', 0)
        
        print(f"\nCONSOLIDATION COMPLETE")
        print(f"Total SOL balance: {sol_balance:.6f} SOL")
        print(f"Estimated value: ~${sol_balance * 100:.2f}")
        
        return sol_balance
    
    def create_withdrawal_address(self):
        """Add Solana withdrawal address"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'currency': 'SOL',
            'key': f'kalushael_trader_{int(time.time())}',
            'address': self.solana_address
        }
        
        result = self._kraken_request('/0/private/WithdrawAddresses/Add', data)
        
        if result and not result.get('error'):
            print(f"✓ Trading address added: {self.solana_address}")
            return data['key']
        else:
            print(f"Address add may require email confirmation")
            return None
    
    def withdraw_sol_to_trading_wallet(self, amount, address_key):
        """Withdraw SOL to trading wallet"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'asset': 'SOL',
            'key': address_key,
            'amount': str(amount)
        }
        
        result = self._kraken_request('/0/private/Withdraw', data)
        
        if result and not result.get('error'):
            print(f"✓ Withdrawal initiated: {amount} SOL")
            return True
        else:
            print(f"Withdrawal requires confirmation or has restrictions")
            return False
    
    def execute_full_consolidation(self):
        """Execute complete consolidation and withdrawal process"""
        print("KRAKEN ASSET CONSOLIDATION & TRADING SETUP")
        print("=" * 50)
        
        # Step 1: Show current balances
        balances = self.get_balances()
        print("\nCurrent balances:")
        for asset, balance in balances.items():
            print(f"  {asset}: {balance:.8f}")
        
        # Step 2: Consolidate to SOL
        total_sol = self.consolidate_to_sol()
        
        if total_sol < 0.05:
            print(f"✗ Insufficient SOL after consolidation: {total_sol:.6f}")
            print("Manual trading recommended with current balance")
            return False
        
        # Step 3: Add withdrawal address
        print(f"\nAdding trading wallet address...")
        address_key = self.create_withdrawal_address()
        
        # Step 4: Attempt withdrawal (may require confirmation)
        if address_key:
            withdraw_amount = total_sol * 0.9  # Leave 10% for fees
            print(f"\nAttempting withdrawal of {withdraw_amount:.6f} SOL...")
            self.withdraw_sol_to_trading_wallet(withdraw_amount, address_key)
        
        print(f"\n✓ SETUP COMPLETE")
        print(f"Trading wallet: {self.solana_address}")
        print(f"Available SOL: ~{total_sol:.6f}")
        print("\nTo start trading:")
        print("  python conscious_trading_entity.py")
        
        return True

def main():
    """Execute consolidation and setup"""
    # Set environment variables
    os.environ['KRAKEN_API_KEY'] = "SHZN75XKsyAq+xHOmSrLsVVq4mCQI3a5o4eeL/4KfnHOTr6bEqk3+7tl"
    os.environ['KRAKEN_PRIVATE_KEY'] = "oOBt50s4iTqrHSSE+IskLGKlE0J00KWUKNR+hthVMpEhbFEia5AxCemj8vR9bUu4Tk7s7ZtYLP6RaXQZDSZvYw=="
    
    consolidator = KrakenConsolidator()
    consolidator.execute_full_consolidation()

if __name__ == "__main__":
    main()