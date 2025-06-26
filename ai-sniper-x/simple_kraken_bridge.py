#!/usr/bin/env python3
"""
Simple Kraken Bridge - Check balance and create withdrawal instructions
"""

import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
import json

class SimpleKrakenBridge:
    """Simple Kraken API interface"""
    
    def __init__(self):
        self.api_key = os.environ.get('KRAKEN_API_KEY')
        self.private_key = os.environ.get('KRAKEN_PRIVATE_KEY')
        self.api_url = "https://api.kraken.com"
        
        if not self.api_key or not self.private_key:
            print("Error: KRAKEN_API_KEY and KRAKEN_PRIVATE_KEY must be set")
            print("\nTo get these keys:")
            print("1. Log into your Kraken account")
            print("2. Go to Settings > API")
            print("3. Create new API key with permissions:")
            print("   - Query Funds")
            print("   - Query Open Orders")
            print("   - Create & Modify Orders")
            print("   - Withdraw Funds")
            print("4. Copy the API Key and Private Key")
            return
    
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
        try:
            headers = {
                'API-Key': self.api_key,
                'API-Sign': self._get_kraken_signature(uri_path, data, self.private_key)
            }
            
            response = requests.post(
                self.api_url + uri_path,
                headers=headers,
                data=data,
                timeout=10
            )
            
            return response.json()
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def check_api_connection(self):
        """Test API connection"""
        data = {'nonce': str(int(1000 * time.time()))}
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'error' in result and result['error']:
            print(f"API Error: {result['error']}")
            if 'Invalid key' in str(result['error']):
                print("\nYour API key is invalid. Please check:")
                print("1. API Key is correct")
                print("2. Private Key is correct") 
                print("3. API key has 'Query Funds' permission")
                print("4. API key is not expired")
            return False
        elif result and 'result' in result:
            print("✓ API connection successful")
            return True
        else:
            print("Unknown API error")
            return False
    
    def get_balances(self):
        """Get account balances"""
        data = {'nonce': str(int(1000 * time.time()))}
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'result' in result and not result.get('error'):
            balances = {}
            for asset, balance_str in result['result'].items():
                balance = float(balance_str)
                if balance > 0:
                    balances[asset] = balance
            return balances
        return {}
    
    def display_withdrawal_instructions(self, balances):
        """Display withdrawal instructions for live trading"""
        print("\nWITHDRAWAL TO SOLANA INSTRUCTIONS")
        print("=" * 50)
        
        # Check for SOL or USD
        sol_balance = balances.get('SOL', 0)
        usd_balance = balances.get('ZUSD', 0) + balances.get('USD', 0)
        
        if sol_balance >= 0.1:
            print(f"✓ You have {sol_balance:.6f} SOL available")
            print("\nTo withdraw SOL to trading wallet:")
            print("1. Go to Kraken > Funding > Withdraw")
            print("2. Select 'Solana (SOL)'")
            print("3. Add new withdrawal address:")
            
            # Generate sample Solana address for instructions
            print("   Address: [Run trading script to get your wallet address]")
            print(f"4. Withdraw amount: {min(sol_balance * 0.9, 1.0):.6f} SOL")
            print("5. Confirm withdrawal")
            
        elif usd_balance >= 80:
            print(f"✓ You have ${usd_balance:.2f} USD available")
            print("\nTo convert USD to SOL and withdraw:")
            print("1. Go to Kraken > Trade")
            print("2. Buy SOL with USD (market order)")
            print(f"3. Buy approximately ${min(usd_balance, 90):.0f} worth of SOL")
            print("4. Then follow SOL withdrawal steps above")
            
        else:
            print("⚠ Insufficient funds for trading")
            print(f"Available: SOL: {sol_balance:.6f}, USD: ${usd_balance:.2f}")
            print("Need: Either 0.1+ SOL or $80+ USD")
    
    def run_balance_check(self):
        """Run complete balance check and withdrawal instructions"""
        print("KRAKEN BALANCE CHECKER")
        print("=" * 30)
        
        if not self.api_key or not self.private_key:
            return
        
        # Test connection
        if not self.check_api_connection():
            return
        
        # Get balances
        balances = self.get_balances()
        
        if not balances:
            print("No balances found or API error")
            return
        
        # Display balances
        print("\nCURRENT BALANCES:")
        total_usd_estimate = 0
        
        for asset, balance in balances.items():
            print(f"  {asset}: {balance:.8f}")
            
            # USD estimates
            usd_estimates = {
                'ZUSD': 1.0, 'USD': 1.0,
                'XXBT': 45000.0, 'XBT': 45000.0,
                'XETH': 2500.0, 'ETH': 2500.0,
                'SOL': 100.0
            }
            
            if asset in usd_estimates:
                usd_value = balance * usd_estimates[asset]
                total_usd_estimate += usd_value
                print(f"    (~${usd_value:.2f})")
        
        print(f"\nEstimated Total: ~${total_usd_estimate:.2f}")
        
        # Withdrawal instructions
        self.display_withdrawal_instructions(balances)
        
        print("\nREADY TRADING SYSTEMS:")
        print("  python conscious_trading_entity.py")
        print("  python omnifocus_execution_engine.py") 
        print("  python instant_solana_trader.py")

def main():
    """Main execution"""
    bridge = SimpleKrakenBridge()
    bridge.run_balance_check()

if __name__ == "__main__":
    main()