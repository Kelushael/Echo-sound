#!/usr/bin/env python3
"""
Kraken Balance Checker
Check account balance and available funds for trading
"""

import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
from typing import Dict, Any, Optional

class KrakenBalanceChecker:
    """Kraken API balance checker"""
    
    def __init__(self):
        self.api_key = os.environ.get('KRAKEN_API_KEY')
        self.private_key = os.environ.get('KRAKEN_PRIVATE_KEY')
        self.api_url = "https://api.kraken.com"
        
        if not self.api_key or not self.private_key:
            raise ValueError("KRAKEN_API_KEY and KRAKEN_PRIVATE_KEY must be set")
    
    def _get_kraken_signature(self, urlpath: str, data: Dict, secret: str) -> str:
        """Generate Kraken API signature"""
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()
    
    def _kraken_request(self, uri_path: str, data: Dict) -> Optional[Dict[str, Any]]:
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
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def get_account_balance(self) -> Dict[str, float]:
        """Get account balance for all assets"""
        data = {
            'nonce': str(int(1000 * time.time()))
        }
        
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'result' in result:
            balances = {}
            for asset, balance_str in result['result'].items():
                balance = float(balance_str)
                if balance > 0:  # Only show assets with positive balance
                    balances[asset] = balance
            return balances
        else:
            print("Failed to get balance")
            if result and 'error' in result:
                print(f"Kraken API Error: {result['error']}")
            return {}
    
    def get_trading_balance(self) -> Dict[str, float]:
        """Get trading balance (available for trading)"""
        data = {
            'nonce': str(int(1000 * time.time()))
        }
        
        result = self._kraken_request('/0/private/TradeBalance', data)
        
        if result and 'result' in result:
            trade_balance = result['result']
            return {
                'equivalent_balance_usd': float(trade_balance.get('eb', 0)),
                'trade_balance_usd': float(trade_balance.get('tb', 0)),
                'margin_amount': float(trade_balance.get('m', 0)),
                'unrealized_pnl': float(trade_balance.get('n', 0)),
                'cost_basis': float(trade_balance.get('c', 0)),
                'current_valuation': float(trade_balance.get('v', 0)),
                'equity': float(trade_balance.get('e', 0)),
                'free_margin': float(trade_balance.get('mf', 0))
            }
        else:
            print("Failed to get trading balance")
            if result and 'error' in result:
                print(f"Kraken API Error: {result['error']}")
            return {}
    
    def check_withdrawal_capability(self) -> bool:
        """Check if account can make withdrawals"""
        # Get withdrawal methods
        data = {
            'nonce': str(int(1000 * time.time())),
            'asset': 'XBT'  # Bitcoin as test
        }
        
        result = self._kraken_request('/0/private/WithdrawMethods', data)
        
        if result and 'result' in result:
            return len(result['result']) > 0
        else:
            return False
    
    def display_complete_balance_info(self):
        """Display comprehensive balance information"""
        print("KRAKEN ACCOUNT BALANCE CHECK")
        print("=" * 50)
        
        # Account balance
        print("\n1. ACCOUNT BALANCES:")
        balances = self.get_account_balance()
        if balances:
            total_usd_estimate = 0
            for asset, balance in balances.items():
                print(f"   {asset}: {balance:.8f}")
                
                # Rough USD estimates for major assets
                usd_estimates = {
                    'ZUSD': 1.0, 'USD': 1.0,
                    'XXBT': 45000.0, 'XBT': 45000.0,  # Bitcoin ~$45k
                    'XETH': 2500.0, 'ETH': 2500.0,   # Ethereum ~$2.5k
                    'SOL': 100.0                      # Solana ~$100
                }
                
                if asset in usd_estimates:
                    usd_value = balance * usd_estimates[asset]
                    total_usd_estimate += usd_value
                    print(f"        (~${usd_value:.2f} USD)")
            
            print(f"\n   ESTIMATED TOTAL: ~${total_usd_estimate:.2f} USD")
        else:
            print("   No balance data available")
        
        # Trading balance
        print("\n2. TRADING BALANCE:")
        trading_balance = self.get_trading_balance()
        if trading_balance:
            for key, value in trading_balance.items():
                print(f"   {key.replace('_', ' ').title()}: ${value:.2f}")
        else:
            print("   No trading balance data available")
        
        # Withdrawal capability
        print("\n3. WITHDRAWAL CAPABILITY:")
        can_withdraw = self.check_withdrawal_capability()
        print(f"   Can withdraw funds: {'YES' if can_withdraw else 'NO'}")
        
        # Available for crypto trading
        print("\n4. AVAILABLE FOR CRYPTO TRADING:")
        if balances:
            crypto_assets = {k: v for k, v in balances.items() 
                           if k not in ['ZUSD', 'USD'] and v > 0}
            if crypto_assets:
                print("   Available crypto assets:")
                for asset, balance in crypto_assets.items():
                    print(f"   - {asset}: {balance:.8f}")
            else:
                print("   No crypto assets available")
            
            # USD/Stablecoin balance
            usd_balance = balances.get('ZUSD', 0) + balances.get('USD', 0)
            if usd_balance > 0:
                print(f"\n   USD Balance for buying crypto: ${usd_balance:.2f}")
                
                # Calculate how much crypto could be bought
                if usd_balance >= 80:
                    print(f"   ✓ Sufficient funds for $80-90 crypto trading")
                    print(f"   ✓ Could buy ~{usd_balance/100:.3f} SOL at current prices")
                else:
                    print(f"   ⚠ Only ${usd_balance:.2f} available (need $80+ for trading)")
        
        print("\n" + "=" * 50)

def main():
    """Main function to check Kraken balance"""
    try:
        checker = KrakenBalanceChecker()
        checker.display_complete_balance_info()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()