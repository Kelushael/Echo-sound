#!/usr/bin/env python3
"""
Kraken to Solana Bridge
Automated withdrawal from Kraken to Solana wallet for live trading
"""

import os
import requests
import urllib.parse
import hashlib
import hmac
import base64
import time
import json
from typing import Dict, Any, Optional, List
from solders.keypair import Keypair

class KrakenSolanaBridge:
    """Bridge funds from Kraken to Solana for trading"""
    
    def __init__(self):
        self.api_key = os.environ.get('KRAKEN_API_KEY')
        self.private_key = os.environ.get('KRAKEN_PRIVATE_KEY')
        self.api_url = "https://api.kraken.com"
        
        if not self.api_key or not self.private_key:
            raise ValueError("KRAKEN_API_KEY and KRAKEN_PRIVATE_KEY must be set")
        
        # Generate Solana wallet for trading
        self.solana_keypair = Keypair()
        self.solana_address = str(self.solana_keypair.pubkey())
        self.solana_private_key = base58.b58encode(bytes(self.solana_keypair)).decode()
        
        print(f"TRADING WALLET GENERATED:")
        print(f"Address: {self.solana_address}")
        print(f"Private Key: {self.solana_private_key}")
    
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
            
            return response.json()
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def get_account_balance(self) -> Dict[str, float]:
        """Get current account balance"""
        data = {'nonce': str(int(1000 * time.time()))}
        result = self._kraken_request('/0/private/Balance', data)
        
        if result and 'result' in result and not result.get('error'):
            balances = {}
            for asset, balance_str in result['result'].items():
                balance = float(balance_str)
                if balance > 0:
                    balances[asset] = balance
            return balances
        else:
            print(f"Balance check failed: {result.get('error', 'Unknown error')}")
            return {}
    
    def get_withdrawal_methods(self, asset: str) -> List[Dict]:
        """Get available withdrawal methods for asset"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'asset': asset
        }
        
        result = self._kraken_request('/0/private/WithdrawMethods', data)
        
        if result and 'result' in result and not result.get('error'):
            return result['result']
        else:
            print(f"Withdrawal methods failed: {result.get('error', 'Unknown error')}")
            return []
    
    def create_solana_withdrawal_address(self) -> Optional[str]:
        """Add Solana withdrawal address to Kraken account"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'currency': 'SOL',
            'key': f'trading_wallet_{int(time.time())}',
            'address': self.solana_address
        }
        
        result = self._kraken_request('/0/private/WithdrawAddresses/Add', data)
        
        if result and not result.get('error'):
            print(f"Solana address added successfully: {self.solana_address}")
            return data['key']
        else:
            print(f"Failed to add withdrawal address: {result.get('error', 'Unknown error')}")
            return None
    
    def withdraw_sol_to_trading_wallet(self, amount: float, address_key: str) -> bool:
        """Withdraw SOL to trading wallet"""
        data = {
            'nonce': str(int(1000 * time.time())),
            'asset': 'SOL',
            'key': address_key,
            'amount': str(amount)
        }
        
        result = self._kraken_request('/0/private/Withdraw', data)
        
        if result and not result.get('error'):
            print(f"Withdrawal initiated: {amount} SOL to {self.solana_address}")
            return True
        else:
            print(f"Withdrawal failed: {result.get('error', 'Unknown error')}")
            return False
    
    def buy_solana_with_usd(self, usd_amount: float) -> bool:
        """Buy Solana with USD on Kraken"""
        # Calculate SOL amount (approximate)
        sol_price = 100.0  # Approximate SOL price
        sol_amount = usd_amount / sol_price
        
        data = {
            'nonce': str(int(1000 * time.time())),
            'pair': 'SOLUSD',
            'type': 'buy',
            'ordertype': 'market',
            'volume': str(sol_amount)
        }
        
        result = self._kraken_request('/0/private/AddOrder', data)
        
        if result and not result.get('error'):
            print(f"Market buy order placed: {sol_amount:.6f} SOL for ~${usd_amount}")
            return True
        else:
            print(f"Buy order failed: {result.get('error', 'Unknown error')}")
            return False
    
    def execute_complete_bridge(self, target_amount_usd: float = 90.0) -> bool:
        """Execute complete bridge from Kraken USD to Solana trading wallet"""
        print("KRAKEN TO SOLANA BRIDGE EXECUTION")
        print("=" * 50)
        
        # Step 1: Check current balance
        print("\n1. CHECKING BALANCE...")
        balances = self.get_account_balance()
        
        if not balances:
            print("❌ Cannot access account balance")
            return False
        
        print("Current balances:")
        for asset, balance in balances.items():
            print(f"   {asset}: {balance:.8f}")
        
        # Step 2: Ensure we have USD or buy SOL
        usd_balance = balances.get('ZUSD', 0) + balances.get('USD', 0)
        sol_balance = balances.get('SOL', 0)
        
        if usd_balance >= target_amount_usd:
            print(f"\n2. BUYING SOLANA WITH ${target_amount_usd} USD...")
            if not self.buy_solana_with_usd(target_amount_usd):
                return False
            
            # Wait for order execution
            print("Waiting for buy order to execute...")
            time.sleep(10)
            
        elif sol_balance * 100 >= target_amount_usd:  # Assume SOL ~$100
            print(f"\n2. SUFFICIENT SOL BALANCE: {sol_balance:.6f} SOL")
            
        else:
            print(f"❌ Insufficient funds. USD: ${usd_balance:.2f}, SOL: {sol_balance:.6f}")
            return False
        
        # Step 3: Add withdrawal address
        print(f"\n3. ADDING TRADING WALLET ADDRESS...")
        address_key = self.create_solana_withdrawal_address()
        
        if not address_key:
            return False
        
        # Step 4: Get updated balance
        time.sleep(5)
        updated_balances = self.get_account_balance()
        sol_balance = updated_balances.get('SOL', 0)
        
        if sol_balance < 0.1:
            print(f"❌ Insufficient SOL balance after purchase: {sol_balance:.6f}")
            return False
        
        # Step 5: Withdraw to trading wallet
        withdraw_amount = min(sol_balance * 0.9, target_amount_usd / 100)  # Leave some for fees
        
        print(f"\n4. WITHDRAWING {withdraw_amount:.6f} SOL TO TRADING WALLET...")
        if not self.withdraw_sol_to_trading_wallet(withdraw_amount, address_key):
            return False
        
        print(f"\n✅ BRIDGE EXECUTION COMPLETE")
        print(f"Trading wallet: {self.solana_address}")
        print(f"Amount withdrawn: {withdraw_amount:.6f} SOL")
        print(f"Estimated value: ~${withdraw_amount * 100:.2f}")
        
        return True
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status"""
        balances = self.get_account_balance()
        
        return {
            'kraken_balances': balances,
            'trading_wallet': self.solana_address,
            'trading_wallet_private_key': self.solana_private_key,
            'ready_for_trading': len(balances) > 0
        }

def main():
    """Execute Kraken to Solana bridge"""
    try:
        bridge = KrakenSolanaBridge()
        
        # Execute complete bridge
        success = bridge.execute_complete_bridge(90.0)
        
        if success:
            print("\n" + "=" * 50)
            print("READY FOR LIVE TRADING")
            print("Run any of these trading systems:")
            print("  python conscious_trading_entity.py")
            print("  python omnifocus_execution_engine.py")
            print("  python instant_solana_trader.py")
            print("=" * 50)
        else:
            print("\n❌ Bridge execution failed")
            
    except Exception as e:
        print(f"Bridge error: {e}")

if __name__ == "__main__":
    main()